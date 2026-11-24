# Guía del código: servicio `auth`

Explicación en español del servicio de usuarios y sesiones (HU-01 a HU-03, HU-05, T-12; docs/06 D1.3, D2). Se actualiza **en el mismo Pull Request** que cambia `services/auth`.

Última actualización: 22/11/2026 · Semana 3.

## Qué es `auth`
El segundo microservicio. Guarda usuarios, perfiles y permisos en **su propia base** (`auth_db`), comprueba contraseñas y **firma** los tokens de acceso con su clave privada. Los demás servicios validan esos tokens con la clave pública **sin llamarlo** (ADR-0007): si auth se cae, nadie puede iniciar sesión, pero los tokens vigentes siguen funcionando hasta 15 minutos.

Sigue el mismo patrón que core (Dockerfile, Alembic, dos usuarios de base, logs JSON, CI): un servicio nuevo cuesta menos porque repite lo aprendido (docs/00, "regla de oro").

## Estructura (capas de docs/06 D1.11)
```
services/auth/
├── Dockerfile, pyproject.toml, alembic.ini, migrations/   igual que core
├── src/auth/
│   ├── main.py            app, middleware de logs, /health y /health/ready
│   ├── config.py          configuración (DATABASE_URL, JWT_PRIVATE_KEY_PATH, tiempos)
│   ├── db.py              conexión, Base (fechas siempre timestamptz) y sesión por petición
│   ├── logging_config.py  logs JSON (copia del de core; ver "Pendientes")
│   ├── bootstrap.py       comando para crear el primer dueño (HU-05)
│   ├── users/
│   │   ├── models.py      tablas: users, permissions, profiles y sus relaciones
│   │   ├── repository.py  consultas: buscar con bloqueo, permisos del usuario, ¿hay dueño?
│   │   └── passwords.py   hash argon2
│   └── sessions/
│       ├── models.py      tabla refresh_tokens (solo el hash)
│       ├── repository.py  consultas de refresh tokens
│       ├── tokens.py      firma del access token; refresh token aleatorio y su hash
│       ├── service.py     REGLAS: login, bloqueo, rotación, robo de token, logout
│       ├── schemas.py     cuerpos de petición y respuesta
│       └── api.py         endpoints HTTP y la cookie
└── tests/                 22 tests contra PostgreSQL real
```

## Base de datos (`migrations/versions/20261122_…_users_profiles_and_sessions.py`)
| Tabla | Para qué |
| --- | --- |
| `users` | Email (único, en minúsculas: lo garantiza un CHECK), nombre, hash de contraseña, activo, intentos fallidos y bloqueo |
| `permissions` | Los 28 códigos de docs/06 D2 (`order.create`, `price.edit`…) |
| `profiles` + `profile_permissions` | Los 4 perfiles por defecto con sus permisos: `owner` (Dueño, todos), `seller` (Vendedor), `warehouse` (Almacén), `courier` (Repartidor) |
| `user_profiles` | Perfiles de cada usuario (puede tener varios) |
| `user_permissions` | Permisos sueltos extra de un usuario |
| `refresh_tokens` | Un registro por refresh token: **solo su hash SHA-256**, vencimiento, revocado y por cuál se reemplazó |

La migración crea las tablas **y carga** el catálogo de permisos y los perfiles: una base nueva queda lista para usar.

## Reglas (`sessions/service.py`)
| Regla | Cómo |
| --- | --- |
| Error genérico (HU-01) | Email inexistente, contraseña incorrecta, usuario inactivo o bloqueado: **la misma respuesta** 401 "Invalid email or password" |
| Mismo tiempo de respuesta | Cuando el email no existe se verifica igual una contraseña falsa: medir cuánto tarda la respuesta no revela qué emails existen |
| Bloqueo | 5 contraseñas incorrectas **seguidas** bloquean 15 minutos; un login correcto reinicia el contador. La fila del usuario se bloquea (`FOR UPDATE`) para que dos intentos simultáneos no se salten la cuenta |
| Access token | JWT RS256 de 15 minutos con `sub`, `name`, `perms`, `iss`, `aud`, `iat`, `exp`. Los permisos se calculan al momento: perfiles + permisos sueltos |
| Refresh token | 256 bits aleatorios; en la base va solo su hash. Viaja en una cookie `HttpOnly` (JavaScript no la lee), `Secure` (solo HTTPS), `SameSite=Strict` (otros sitios no la envían) y `Path=/api/auth/v1` |
| Rotación (HU-02) | Cada `/refresh` revoca el token usado y entrega uno nuevo |
| Robo de token | Si llega un refresh token **ya rotado**, alguien lo copió: se revocan **todas** las sesiones del usuario y queda un aviso en el log |
| Cambio de permisos | Se aplica en el siguiente refresh (máximo 15 minutos) |
| Logout (HU-03) | Revoca el refresh token y borra la cookie. Repetirlo no falla |
| Rehash | Si argon2 cambia sus parámetros recomendados, el hash se recalcula en el siguiente login correcto |

`service.py` no conoce HTTP: lanza `InvalidCredentialsError` o `InvalidRefreshTokenError` y `api.py` los convierte en 401 (docs/06 D1.11).

## Endpoints
| Método y ruta (desde el gateway) | Respuesta | Permiso |
| --- | --- | --- |
| `POST /api/auth/v1/login` `{email, password}` | `200 {access_token, token_type, expires_in}` + cookie; `401`; `422` si los datos son absurdos (contraseña > 128 caracteres) | Ninguno |
| `POST /api/auth/v1/refresh` (cookie) | `200` con token nuevo + cookie rotada; `401` y borra la cookie | Cookie válida |
| `POST /api/auth/v1/logout` (cookie) | `204` y borra la cookie | Ninguno |
| `GET /api/auth/health`, `/health/ready` | Estado del servicio y de `auth_db` | Ninguno |
| `GET /api/auth/docs` | Documentación interactiva | Ninguno |

## Primer usuario dueño (HU-05)
```bash
docker compose -f infra/compose.yaml --profile setup run --rm auth-bootstrap
```
Lee `BOOTSTRAP_ADMIN_EMAIL`, `BOOTSTRAP_ADMIN_NAME` y `BOOTSTRAP_ADMIN_PASSWORD` (mínimo 12 caracteres) de `infra/.env`. Si ya existe un dueño activo, no hace nada. El servicio `auth-bootstrap` tiene `profiles: ["setup"]`: `up` no lo arranca, solo corre cuando se pide.

## Tests (22, contra PostgreSQL real)
| Archivo | Prueba |
| --- | --- |
| `conftest.py` | Levanta PostgreSQL con **los scripts de `infra/postgres/init`**, migra como `auth_owner`, prueba la API como `auth_app`, genera una clave de prueba y vacía las tablas entre tests |
| `test_login.py` | Token con los permisos del perfil; cookie segura; email sin importar mayúsculas; misma respuesta para contraseña incorrecta y email inexistente; inactivo; bloqueo a los 5 intentos; un login correcto reinicia el contador; contraseña gigante → 422 |
| `test_refresh_and_logout.py` | Rotación; **robo de token** (reuso revoca todo); sin cookie; token inventado; vencido; permisos nuevos en el refresh; logout; logout sin sesión |
| `test_bootstrap_and_health.py` | Crea el dueño y puede entrar; no crea un segundo dueño; rechaza contraseñas cortas; health; `auth_app` no puede crear tablas; **`auth_app` no puede conectarse a `core_db`** |

## Comandos (desde `services/auth`)
Los mismos que core: `uv sync`, `uv run pytest` (con Docker Desktop encendido), `uv run ruff format .`, `uv run ruff check .`, `uv run alembic revision -m "..."`.

## Pendientes
- HU-04 (gestionar usuarios y permisos desde la API, con auditoría) y HU-06 (pantalla de login).
- `logging_config.py` y el middleware de logs están copiados de core. Si un tercer servicio los necesita, pasan a una librería compartida (DRY, docs/06 D1.11); con dos copias, todavía es más simple así.
