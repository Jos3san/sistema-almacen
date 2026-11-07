# Guía del código: infraestructura local (`infra/`)

Explicación en español de cómo se levanta el sistema con Docker Compose y del gateway Caddy. Se actualiza **en el mismo Pull Request** que cambia `infra/`.

Última actualización: 07/11/2026 · Semana 2 (T-06 y T-07).

## Estructura
```
infra/
├── compose.yaml      el plano del sistema local: gateway, core y db
├── .env.example      plantilla de variables sin valores reales (sí se sube)
├── .env              tus valores reales (NO se sube: lo bloquea .gitignore)
└── caddy/
    └── Caddyfile     configuración del gateway
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
| `db` | `postgres:18.6-trixie` | Ninguno | Datos en el volumen `pgdata` montado en `/var/lib/postgresql` (desde PostgreSQL 18 es esa carpeta, ya no `.../data`). *Healthcheck* con `pg_isready` |
| `core` | `core:dev` (se construye desde `services/core/Dockerfile`) | Ninguno | Arranca cuando `db` está *healthy*. *Healthcheck* contra `/health/ready`. Variables: `DATABASE_URL`, `UVICORN_ROOT_PATH`, `FORWARDED_ALLOW_IPS` (ver docs/codigo/core.md) |
| `gateway` | `caddy:2.11.9-alpine` | `127.0.0.1:80` → `8080` | Arranca cuando `core` está *healthy*. Usuario sin privilegios (65534), disco de solo lectura y carpetas temporales (`tmpfs`) para `/data` y `/config`. El Caddyfile se monta como solo lectura |

`127.0.0.1` delante del puerto significa que solo se puede entrar desde tu propia PC, no desde otra máquina de tu red.

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
| `cp infra/.env.example infra/.env` | Crea tu archivo de variables (una sola vez). Cambia la contraseña; `.env` **nunca** se sube |
| `docker compose -f infra/compose.yaml up -d --build` | Construye core y levanta todo en segundo plano (`--build` solo hace falta si cambió el código de core) |
| `docker compose -f infra/compose.yaml ps` | Estado de cada servicio; esperar `(healthy)` |
| `docker compose -f infra/compose.yaml logs core` | Logs de un servicio (`core`, `db` o `gateway`) |
| `docker compose -f infra/compose.yaml stop db` / `start db` | Apaga o enciende un servicio (prueba de caída) |
| `docker compose -f infra/compose.yaml down` | Apaga y borra los contenedores; **los datos quedan** en el volumen |
| `docker compose -f infra/compose.yaml down -v` | Además **borra el volumen con los datos**. Solo en local, nunca en producción |
| `docker run --rm -v "<ruta>/infra/caddy/Caddyfile:/etc/caddy/Caddyfile:ro" caddy:2.11.9-alpine caddy validate --config /etc/caddy/Caddyfile` | Valida la sintaxis del Caddyfile sin levantar nada |

Direcciones locales:
- `http://localhost/api/core/health/ready` → estado de core y su base.
- `http://localhost/api/core/docs` → documentación interactiva de core.

## Trampas aprendidas
- `POSTGRES_PASSWORD` solo se aplica **la primera vez** que se crea el volumen. Para cambiarla en local: editar `.env` y `down -v` + `up -d`. En producción se **rota** sin borrar nada: `ALTER USER … PASSWORD` dentro de PostgreSQL y después el `.env`.
- La contraseña va dentro de una URL (`DATABASE_URL`): solo letras y números, porque `@ : / #` la romperían.
- Temporal hasta T-10: core se conecta con el superusuario que crea la imagen de PostgreSQL. T-10 lo separa en dueño del esquema y usuario de la aplicación con permisos mínimos.
