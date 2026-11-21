# Guía del código: infraestructura local (`infra/`)

Explicación en español de cómo se levanta el sistema con Docker Compose, del gateway Caddy y de la integración continua. Se actualiza **en el mismo Pull Request** que cambia `infra/` o `.github/`.

Última actualización: 21/11/2026 · Semanas 2 y 3 (T-06 a T-11, T-20).

## Estructura
```
infra/
├── compose.yaml      el plano del sistema local: gateway, core, migrate y db
├── .env.example      plantilla de variables sin valores reales (sí se sube)
├── .env              tus valores reales (NO se sube: lo bloquea .gitignore)
├── caddy/
│   └── Caddyfile     configuración del gateway
├── scripts/
│   └── generate_jwt_keys.py  genera el par de claves JWT (una vez por entorno)
├── secrets/          claves JWT generadas (NO se suben: lo bloquea .gitignore)
└── postgres/
    └── init/
        └── 10-core.sh  crea core_db y sus dos usuarios (solo con el volumen vacío)
```

## Cómo viaja una petición
```
navegador ──► http://localhost/api/core/health/ready
                │  (puerto 80 de tu PC → 8080 del contenedor)
           [ gateway: Caddy ]  límite de 10 MB, cabeceras de seguridad, X-Request-ID,
                │              quita "/api/core" de la ruta
                ▼
           [ core ]  recibe /health/ready  ──►  [ db: PostgreSQL ]
```
Solo el gateway publica un puerto. core y db viven en la red interna de Docker y se encuentran **por nombre** (`core`, `db`): Docker tiene un DNS interno, y si un servicio se apaga su nombre deja de existir (por eso el log decía `failed to resolve host 'db'` en la prueba de caída).

## Servicios de `compose.yaml`
| Servicio | Imagen | Puertos | Detalles |
| --- | --- | --- | --- |
| `db` | `postgres:18.6-trixie` | Ninguno | Datos en el volumen `pgdata` montado en `/var/lib/postgresql` (desde PostgreSQL 18 es esa carpeta, ya no `.../data`). Monta `postgres/init` en `/docker-entrypoint-initdb.d`. *Healthcheck* con `pg_isready` |
| `migrate` | `core:dev` | Ninguno | **Contenedor de un solo uso**: corre `alembic upgrade head` como `core_owner` y termina. En `ps -a` aparece `Exited (0)`, que significa que terminó bien. Arranca cuando `db` está *healthy* |
| `core` | `core:dev` (se construye desde `services/core/Dockerfile`) | Ninguno | Arranca cuando `db` está *healthy* y `migrate` terminó bien (`service_completed_successfully`): si una migración falla, core no arranca. Se conecta como `core_app`. *Healthcheck* contra `/health/ready`. Variables: `DATABASE_URL`, `UVICORN_ROOT_PATH`, `FORWARDED_ALLOW_IPS` (ver docs/codigo/core.md) |
| `gateway` | `caddy:2.11.9-alpine` | `127.0.0.1:80` → `8080` | Arranca cuando `core` está *healthy*. Usuario sin privilegios (65534), disco de solo lectura y carpetas temporales (`tmpfs`) para `/data` y `/config`. El Caddyfile se monta como solo lectura |

`127.0.0.1` delante del puerto significa que solo se puede entrar desde tu propia PC, no desde otra máquina de tu red.

Orden de arranque: `db` (*healthy*) → `migrate` (termina) → `core` (*healthy*) → `gateway`.

## Usuarios de la base (`postgres/init/10-core.sh`, docs/06 D1.6)
| Usuario | Lo usa | Puede | Variable de `.env` |
| --- | --- | --- | --- |
| `postgres` (administrador) | Solo el primer arranque, para crear bases y usuarios; emergencias | Todo | `POSTGRES_USER`, `POSTGRES_PASSWORD` |
| `core_owner` | El contenedor `migrate` (`MIGRATION_DATABASE_URL`) | Es dueño de `core_db`: crea y cambia tablas | `CORE_OWNER_PASSWORD` |
| `core_app` | El servicio core (`DATABASE_URL`) | Leer y escribir filas. **No** puede crear, alterar ni borrar tablas | `CORE_APP_PASSWORD` |

- `REVOKE ALL ON DATABASE core_db FROM PUBLIC`: solo estos usuarios pueden conectarse a `core_db`; el futuro usuario de auth no podrá.
- `ALTER DEFAULT PRIVILEGES`: cada tabla que `core_owner` cree en una migración queda **automáticamente** disponible para `core_app` (leer, insertar, actualizar, borrar filas). Las tablas que deben ser solo de inserción (kardex, auditoría) le quitarán UPDATE y DELETE a `core_app` en su propia migración (RNF-05).
- El script usa variables de `psql` (`:'owner_password'`) para no escribir las claves en el código.
- Lo prueban 3 tests de `services/core/tests/test_migrations.py`, que levantan PostgreSQL con **este mismo script**.

## `caddy/Caddyfile`
| Bloque | Qué hace | Por qué |
| --- | --- | --- |
| `{ auto_https off; admin off; persist_config off }` | Opciones globales | En local no hay dominio ni certificado (HTTPS llega con staging, T-14). Sin panel de administración: menos superficie de ataque. No guarda copias de su configuración (disco de solo lectura) |
| `:8080 { … }` | El sitio: escucha en el puerto 8080 del contenedor | Puerto mayor a 1024, para no necesitar ser *root* |
| `request_body { max_size 10MB }` | Rechaza peticiones más grandes con **413** | Que nadie sature el servidor con archivos enormes; alcanza para importar el Excel de productos |
| `header { … }` | Cabeceras de seguridad de docs/06 D1.10 y `X-Request-ID` | `nosniff`, `DENY` (anti *clickjacking*), `Referrer-Policy`, `Permissions-Policy`. `-Server` y `-Via` quitan cabeceras que anuncian el software. `X-Request-ID` devuelve un identificador único por petición |
| `handle_path /api/core/* { reverse_proxy core:8000 … }` | Envía a core lo que empieza con `/api/core/`, **quitando el prefijo** | `header_up` le pasa a core el mismo `X-Request-ID` (se usará en sus logs, T-09) |
| `handle { respond "Not found" 404 }` | Todo lo demás | Nada se expone por accidente |

Las llaves `{ }` anidan bloques, como cajas dentro de cajas: todo lo del sitio va dentro de `:8080 { … }`, con un Tab más de sangría por nivel. `{http.request.uuid}` es un *placeholder* (valor que Caddy rellena), no un bloque.

Pendiente: HSTS se activa con HTTPS real (T-14) y CSP con el frontend (T-13), con excepción para `/docs`.

## Comandos (desde la raíz del repo)
| Comando | Qué hace |
| --- | --- |
| `cp infra/.env.example infra/.env` | Crea tu archivo de variables (una sola vez). Cambia las 3 claves; `.env` **nunca** se sube |
| `uv run --no-project --with cryptography python infra/scripts/generate_jwt_keys.py` | Genera `infra/secrets/jwt_private.pem` y `jwt_public.pem` (una sola vez; nunca sobrescribe). La privada será solo de auth; la pública se monta en core |
| `docker compose -f infra/compose.yaml up -d --build` | Construye core y levanta todo en segundo plano (`--build` solo hace falta si cambió el código de core) |
| `docker compose -f infra/compose.yaml ps -a` | Estado de cada servicio, incluidos los que ya terminaron (`migrate`); esperar `(healthy)` |
| `docker compose -f infra/compose.yaml logs core` | Logs de un servicio (`core`, `migrate`, `db` o `gateway`); los de core y migrate van en JSON |
| `docker compose -f infra/compose.yaml stop db` / `start db` | Apaga o enciende un servicio (prueba de caída) |
| `docker compose -f infra/compose.yaml down` | Apaga y borra los contenedores; **los datos quedan** en el volumen |
| `docker compose -f infra/compose.yaml down -v` | Además **borra el volumen con los datos**. Solo en local, nunca en producción |
| `docker run --rm -v "<ruta>/infra/caddy/Caddyfile:/etc/caddy/Caddyfile:ro" caddy:2.11.9-alpine caddy validate --config /etc/caddy/Caddyfile` | Valida la sintaxis del Caddyfile sin levantar nada |

Direcciones locales:
- `http://localhost/api/core/health/ready` → estado de core y su base.
- `http://localhost/api/core/docs` → documentación interactiva de core.

## Integración continua (`.github/workflows/ci.yml`)
GitHub Actions corre esto en una máquina limpia en cada PR y en cada push a `main`.

| Job | Pasos | Qué protege |
| --- | --- | --- |
| `core / lint and tests` | Descarga el código, instala uv 0.13.6, `uv sync --locked`, Ruff (formato y lint, con reglas de seguridad `S` y complejidad `C90`), pytest, **pip-audit** | Estilo, errores y comportamiento, con un PostgreSQL real levantado por Testcontainers. `--locked` falla si `uv.lock` no coincide con `pyproject.toml`. pip-audit falla si una dependencia tiene una vulnerabilidad conocida (CVE) |
| `core / Docker image` | `docker build` con contexto en la raíz, igual que en local (no publica nada), y **Trivy** | Que el Dockerfile siga funcionando y que la imagen no tenga vulnerabilidades altas o críticas que ya tengan arreglo |

| Decisión | Por qué |
| --- | --- |
| `permissions: contents: read` | Mínimo privilegio: el workflow solo puede leer el repositorio |
| Acciones fijadas por SHA (`actions/checkout@3d3c42e…`, con la versión en un comentario) | Una etiqueta se puede mover; un SHA no (OWASP A03, docs/06 D1.10) |
| `persist-credentials: false` | El token no queda guardado para los pasos siguientes |
| `cancel-in-progress` solo en PRs | Un push nuevo cancela la corrida vieja del PR, pero en `main` todo commit debe quedar verificado |
| `timeout-minutes: 15` | Una corrida colgada se corta sola |

El ruleset `proteger-main` exige los dos jobs en verde y solo permite fusionar con rebase, sin excepciones. Se comprobó con un PR roto a propósito (#7): quedó `BLOCKED` y `main` no cambió. Los nombres de los jobs están registrados en el ruleset: si se renombran en `ci.yml`, hay que actualizarlos allí o ningún PR podrá fusionarse.

### Seguridad automatizada (T-20, docs/06 D1.10)
| Control | Dónde | Qué hace |
| --- | --- | --- |
| Secret scanning + push protection | GitHub (configuración del repo) | Rechaza un `git push` que contenga una clave o token |
| Dependabot alertas | GitHub | Avisa si una dependencia tiene una vulnerabilidad |
| Dependabot actualizaciones | `.github/dependabot.yml` | Cada lunes abre PRs con versiones nuevas de: dependencias de uv (**todas en un solo PR**, porque todas tocan `pyproject.toml` y `uv.lock`), imágenes del Dockerfile, imágenes de `compose.yaml` y acciones de GitHub. **Ignora** los cambios de versión de Python (solo parches 3.13.x) y las versiones mayores de PostgreSQL: esos se deciden a mano. Cada PR pasa por la CI como cualquier otro |

**Cómo revisar un PR de Dependabot** (CI en verde no basta):
1. ¿Qué cambia de verdad? Mirar *Files changed*: ¿es un parche (3.3.8 → 3.3.9), una versión menor o una mayor?
2. ¿Es una decisión de arquitectura? Cambiar de Python o de versión mayor de PostgreSQL no se acepta por un PR automático: se cierra y se planifica (ADR).
3. ¿Choca con otro PR abierto que toca los mismos archivos? Fusionar uno y pedir a Dependabot `@dependabot rebase` en los otros.
4. Para versiones mayores de una librería: leer sus notas de versión (*release notes*) antes de fusionar.

Primera tanda (21/11): de 6 PRs, el de Python 3.15 lo rechazó la propia CI (la imagen no compilaba) y se cerró; los demás se fusionan uno por uno con `@dependabot rebase`, y la configuración se ajustó para agrupar desde la siguiente semana.
| Ruff `S` y `C90` | CI, job de tests | Código inseguro (claves escritas en el código, SQL armado con texto) y funciones demasiado complejas |
| pip-audit | CI, job de tests | Vulnerabilidades conocidas en las versiones exactas de `uv.lock` |
| Trivy | CI, job de imagen | Vulnerabilidades en los paquetes del sistema y de Python dentro de la imagen |
| CodeQL | GitHub (configuración por defecto) | Análisis profundo del código en cada PR |

Lección de T-20: pip-audit no encontró nada, pero Trivy sí. Las vulnerabilidades no estaban en nuestras dependencias, sino en la imagen base: paquetes de Debian sin parchear y librerías que vienen **dentro de `pip`**. Por eso el Dockerfile instala los parches del sistema y quita `pip` de la imagen final. Revisar **solo el código** no basta: hay que revisar también el contenedor.

Dependabot no actualiza las versiones escritas dentro de comandos (`aquasec/trivy:0.76.2` y `pip-audit@2.10.1` en `ci.yml`): esas se revisan a mano al cerrar cada capa.

**Cómo leer un fallo:** en el PR, **Details** → el paso en rojo. Busca qué falló (`FAILED tests/...`), por qué (`AssertionError: ...`) y dónde (`archivo:línea`).

## Trampas aprendidas
- Las claves de la base y los scripts de `postgres/init` solo se aplican **la primera vez** que se crea el volumen. Para cambiarlas en local: editar `.env` y `down -v` + `up -d`. En producción se **rotan** sin borrar nada: `ALTER USER … PASSWORD` dentro de PostgreSQL y después el `.env`.
- Las claves van dentro de URLs (`DATABASE_URL`, `MIGRATION_DATABASE_URL`): solo letras y números, porque `@ : / #` las romperían.
- Si falta una variable en `infra/.env`, Compose se detiene **antes de hacer nada** con `required variable ... is missing a value` (sintaxis `${VAR:?mensaje}` de `compose.yaml`). Pasó al agregar las claves de T-10: el `.env` local tenía las variables antiguas.
