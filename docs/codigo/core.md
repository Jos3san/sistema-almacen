# Guía del código: servicio `core`

Explicación en español de cada archivo y función de `services/core`. Se actualiza **en el mismo Pull Request** que cambia el código (convención en CLAUDE.md). En el código, los comentarios y *docstrings* van en inglés.

Última actualización: 07/11/2026 · Semana 2 (T-07).

## Qué es `core`
El servicio principal del sistema: catálogo, stock, pedidos y despachos (docs/06 D1.2, ADR-0003). Por ahora responde si está vivo y si puede hablar con su base de datos; el negocio se agrega desde la semana 4.

## Estructura
```
services/core/
├── pyproject.toml      ficha del proyecto: nombre, versión de Python, dependencias
├── uv.lock             versiones exactas de todas las librerías (build reproducible)
├── .python-version     fija Python 3.13 para esta carpeta
├── README.md           descripción corta y enlace a esta guía
├── Dockerfile          receta de la imagen Docker (se construye desde la raíz del repo)
├── src/
│   └── core/           el paquete de Python "core" (el código de la aplicación)
│       ├── __init__.py marca la carpeta como paquete
│       ├── config.py   lee la configuración de las variables de entorno
│       ├── db.py       conexión a PostgreSQL (pool de conexiones)
│       └── main.py     crea la aplicación FastAPI y sus rutas
└── tests/
    ├── test_health.py        pruebas de /health
    └── test_health_ready.py  pruebas de /health/ready contra un PostgreSQL real
```
Carpetas que se generan solas y **no** se suben a Git: `.venv/` (librerías instaladas), `__pycache__/` (caché de Python), `.pytest_cache/` (caché de pytest).

¿Por qué `src/core/` y no un `main.py` suelto? Con la carpeta `src/`, los tests importan el código **instalado** como paquete (`from core.main import app`), igual que en producción. Evita que un test funcione "por casualidad" solo porque el archivo estaba en la misma carpeta.

## `pyproject.toml`
| Sección | Qué dice |
| --- | --- |
| `[project]` | Nombre `core`, versión `0.1.0`, requiere Python ≥ 3.13 |
| `dependencies` | Lo que necesita **en producción**: `fastapi`, el servidor `uvicorn[standard]`, `sqlalchemy` (hablar con la base desde Python), `psycopg[binary]` (el *driver* que conecta con PostgreSQL) y `pydantic-settings` (leer la configuración) |
| `[dependency-groups] dev` | Lo que solo se usa **al desarrollar**: `fastapi[standard]` (comando `fastapi dev` y cliente de tests), `pytest`, `ruff` y `testcontainers[postgres]` (PostgreSQL desechable para los tests). La imagen de producción no los instala |
| `[build-system]` | Cómo uv empaqueta el código como paquete instalable (`uv_build`) |
| `[tool.ruff]` | Ruff revisa pensando en Python 3.13, con líneas de hasta 100 caracteres |
| `[tool.ruff.lint] select` | Familias de reglas activas: **E** estilo, **F** errores reales (imports sin usar, variables no definidas), **I** orden de imports, **B** errores típicos, **UP** sintaxis moderna |

## `src/core/main.py`
| Elemento | Qué es | Para qué |
| --- | --- | --- |
| `app = FastAPI(title="core")` | La aplicación | Objeto central al que se le agregan todas las rutas. El título aparece en `/docs` |
| `health()` | Endpoint `GET /health` | Responde `{"status": "ok"}` con código 200 si el proceso está vivo. **No** revisa la base de datos |
| `health_ready()` | Endpoint `GET /health/ready` | Hace `SELECT 1` en la base. 200 `{"status": "ok"}` si responde; si no, **503** `{"status": "unavailable"}` sin detalles internos (OWASP A10, docs/06 D1.10), y la causa va al log. Lo usan el healthcheck de Compose y el monitor externo |
| `engine: Annotated[Engine, Depends(get_engine)]` | Inyección de dependencias | FastAPI llama a `get_engine()` y le pasa el resultado al endpoint. En los tests se reemplaza por otra base (`app.dependency_overrides`) sin tocar el código |

¿Por qué dos *health*? `/health` dice "el proceso vive"; `/health/ready` dice "puedo trabajar". Si la base se cae, core sigue vivo pero no listo: así el monitor distingue "reiniciar core" de "revisar la base".

La *docstring* de cada endpoint (el texto entre `"""` debajo del `def`) aparece como descripción en la documentación automática `/docs`.

## `src/core/config.py` y `src/core/db.py`
| Elemento | Qué es | Para qué |
| --- | --- | --- |
| `Settings` | Clase de `pydantic-settings` | Cada campo se lee de la variable de entorno con el mismo nombre en mayúsculas: `database_url` ← `DATABASE_URL`. Si falta, falla con un error que la nombra. Así no hay contraseñas en el código (docs/06 D1.6) |
| `get_settings()` | Función con `@lru_cache` | Lee la configuración una sola vez y la reutiliza |
| `get_engine()` | Función con `@lru_cache` | Crea **una vez** el *pool* de conexiones de SQLAlchemy. Abrir una conexión cuesta, el pool las reutiliza |
| `pool_pre_ping=True` | Opción del pool | Antes de usar una conexión, comprueba que sigue viva. Por eso core se recupera solo cuando la base vuelve |
| `connect_timeout=3` | Opción del driver | Si la base no responde en 3 s, se rinde en vez de dejar la petición colgada |

La URL de conexión tiene la forma `postgresql+psycopg://usuario:clave@host:5432/base`: `+psycopg` indica a SQLAlchemy qué driver usar. Dentro de Compose, el host es `db`, el nombre del servicio.

## `tests/test_health.py`
| Elemento | Qué es | Para qué |
| --- | --- | --- |
| `client = TestClient(app)` | "Navegador falso" | Hace peticiones a la app sin encender el servidor |
| `test_health_returns_ok()` | Test | Comprueba que `GET /health` responde 200 y `{"status": "ok"}`. Si alguien rompe `/health`, falla |

Convenciones de pytest: la carpeta se llama `tests/`, los archivos empiezan con `test_` y las funciones también.

## `tests/test_health_ready.py`
| Elemento | Qué es | Para qué |
| --- | --- | --- |
| `postgres_url` | *Fixture* de pytest (`scope="module"`) | Levanta un PostgreSQL **real y desechable** con Testcontainers, de la misma versión que `infra/compose.yaml`, y lo borra al terminar. Se crea una vez para todos los tests del archivo |
| `client_for` | *Fixture* | Devuelve una función que crea un cliente de prueba conectado a la base que le digas. Al terminar el test limpia el reemplazo (`dependency_overrides.clear()`) |
| `test_ready_ok_when_database_reachable` | Test | Base real → 200 `{"status": "ok"}` |
| `test_ready_503_when_database_down` | Test | Base inexistente (puerto 1) → 503 y el cuerpo **no** revela detalles |

Una *fixture* es una preparación que pytest le entrega al test con solo nombrarla como parámetro. Estos tests necesitan **Docker Desktop encendido**.

## Comandos (desde `services/core`)
| Comando | Qué hace |
| --- | --- |
| `uv sync` | Instala exactamente lo que dice `uv.lock` (útil al clonar el repo en otra PC) |
| `uv add <librería>` | Agrega una dependencia de producción |
| `uv add --dev <librería>` | Agrega una dependencia solo de desarrollo |
| `uv run fastapi dev src/core/main.py` | Levanta la API en `http://127.0.0.1:8000`, con reinicio automático al guardar |
| `uv run pytest` | Corre todos los tests |
| `uv run ruff format .` | Formatea el código (espacios, comillas, sangrías) |
| `uv run ruff check .` | Revisa errores y estilo; con `--fix` arregla lo que puede solo |

**Rutina antes de cada commit:** `ruff format .` → `ruff check .` → `pytest`. Los tres deben quedar en verde; la CI (semana 2) correrá lo mismo en cada Pull Request.

## Imagen Docker (`Dockerfile` y `/.dockerignore`)
La imagen empaqueta `core` con Python y sus dependencias para que corra igual en tu PC, en la CI y en el servidor (docs/06 D1.5).

**Contexto = raíz del repo.** Se construye desde `D:\proyectoLibreria` con `-f services/core/Dockerfile`, para poder copiar `libs/` desde la semana 3. Por eso el `.dockerignore` está en la raíz: Docker solo lo busca en la raíz del contexto.

**`.dockerignore`** evita que lleguen al build secretos (`.env`, `*.pem`, `*.key`), entornos locales (`.venv`), cachés, `docs/` y `tests/`. Ojo: a diferencia de `.gitignore`, un patrón sin `**/` solo aplica a la raíz; por eso se escribe `**/.env`.

**Dockerfile, en dos etapas (*multi-stage*):**

| Etapa | Paso | Por qué |
| --- | --- | --- |
| `builder` | `FROM python:3.13.15-slim-trixie` | Versión fija: el build de mañana da lo mismo que el de hoy |
| `builder` | Copia `uv` 0.13.6 desde su imagen oficial | Misma herramienta y versión que en local |
| `builder` | Copia `pyproject.toml` + `uv.lock` y corre `uv sync --locked --no-dev --no-install-project` | Instala solo dependencias. Esa capa queda en caché mientras `uv.lock` no cambie, así cambiar código no reinstala nada |
| `builder` | Copia `src/` y corre `uv sync --locked --no-dev --no-editable` | Instala el paquete `core` dentro de `.venv`, sin herramientas de desarrollo |
| `runtime` | Nuevo `FROM` limpio | uv y los archivos temporales no viajan: imagen más pequeña (~233 MB) |
| `runtime` | Usuario `app` (uid 10001) y `USER app` | El proceso no es *root* |
| `runtime` | Copia `.venv` **sin** cambiar el dueño | El código queda de *root*: `app` puede leerlo y ejecutarlo, pero no modificarlo |
| `runtime` | `CMD ["uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "8000"]` | Arranca la API. `0.0.0.0` acepta conexiones desde fuera del contenedor |

El *healthcheck* y la configuración detrás de Caddy no están en la imagen sino en Compose (ver "Cómo se levanta"): la misma imagen sirve para cualquier entorno.

**Comandos (desde la raíz del repo):**

| Comando | Qué hace |
| --- | --- |
| `docker build -f services/core/Dockerfile -t core:dev .` | Construye la imagen. El `.` final es el contexto |
| `docker image ls core` | Lista las imágenes de core y su tamaño |
| `docker run --rm -d -p 8000:8000 --name core-test core:dev` | Arranca un contenedor en segundo plano en el puerto 8000; `--rm` lo borra al detenerlo |
| `docker logs core-test` | Muestra lo que escribió el contenedor |
| `docker stop core-test` | Lo detiene |

Docker Desktop debe estar abierto (*Engine running*); si no, `docker` responde `failed to connect to the docker API`.

## Rutas disponibles
| Método y ruta | Respuesta | Permiso | Desde |
| --- | --- | --- | --- |
| `GET /health` | `200 {"status": "ok"}` | Ninguno | Semana 1 |
| `GET /docs` | Documentación interactiva (OpenAPI) | Ninguno | Semana 1 |
| `GET /health/ready` | `200 {"status": "ok"}` o `503 {"status": "unavailable"}` | Ninguno | Semana 2 |

## Cómo se levanta
core corre dentro del entorno de Docker Compose, detrás del gateway Caddy: se usa en `http://localhost/api/core/...` (por ejemplo `http://localhost/api/core/docs`). Comandos y explicación en [infra.md](infra.md).

Dos variables de entorno que pone Compose y afectan a core:
- `UVICORN_ROOT_PATH=/api/core`: Caddy quita ese prefijo antes de reenviar; con esto FastAPI sabe que vive bajo `/api/core` y `/docs` arma bien sus enlaces. Sin Compose (con `uv run fastapi dev`) no se usa y la API queda en `http://127.0.0.1:8000`.
- `FORWARDED_ALLOW_IPS=*`: core confía en la cabecera `X-Forwarded-For` del gateway para conocer la IP real del cliente. Es seguro solo porque core no publica puertos.
