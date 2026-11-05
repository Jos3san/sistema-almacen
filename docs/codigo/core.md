# Guía del código: servicio `core`

Explicación en español de cada archivo y función de `services/core`. Se actualiza **en el mismo Pull Request** que cambia el código (convención en CLAUDE.md). En el código, los comentarios y *docstrings* van en inglés.

Última actualización: 05/11/2026 · Semana 1 (T-03).

## Qué es `core`
El servicio principal del sistema: catálogo, stock, pedidos y despachos (docs/06 D1.2, ADR-0003). Por ahora solo responde que está vivo; el negocio se agrega desde la semana 4.

## Estructura
```
services/core/
├── pyproject.toml      ficha del proyecto: nombre, versión de Python, dependencias
├── uv.lock             versiones exactas de todas las librerías (build reproducible)
├── .python-version     fija Python 3.13 para esta carpeta
├── README.md           descripción corta y enlace a esta guía
├── src/
│   └── core/           el paquete de Python "core" (el código de la aplicación)
│       ├── __init__.py marca la carpeta como paquete
│       └── main.py     crea la aplicación FastAPI y sus rutas
└── tests/
    └── test_health.py  pruebas automáticas de /health
```
Carpetas que se generan solas y **no** se suben a Git: `.venv/` (librerías instaladas), `__pycache__/` (caché de Python), `.pytest_cache/` (caché de pytest).

¿Por qué `src/core/` y no un `main.py` suelto? Con la carpeta `src/`, los tests importan el código **instalado** como paquete (`from core.main import app`), igual que en producción. Evita que un test funcione "por casualidad" solo porque el archivo estaba en la misma carpeta.

## `pyproject.toml`
| Sección | Qué dice |
| --- | --- |
| `[project]` | Nombre `core`, versión `0.1.0`, requiere Python ≥ 3.13 |
| `dependencies` | Lo que necesita **en producción**: `fastapi[standard]` (FastAPI + el servidor Uvicorn) |
| `[dependency-groups] dev` | Lo que solo se usa **al desarrollar**: `pytest` y `ruff`. La imagen de producción no los instala |
| `[build-system]` | Cómo uv empaqueta el código como paquete instalable (`uv_build`) |
| `[tool.ruff]` | Ruff revisa pensando en Python 3.13, con líneas de hasta 100 caracteres |
| `[tool.ruff.lint] select` | Familias de reglas activas: **E** estilo, **F** errores reales (imports sin usar, variables no definidas), **I** orden de imports, **B** errores típicos, **UP** sintaxis moderna |

## `src/core/main.py`
| Elemento | Qué es | Para qué |
| --- | --- | --- |
| `app = FastAPI(title="core")` | La aplicación | Objeto central al que se le agregan todas las rutas. El título aparece en `/docs` |
| `health()` | Endpoint `GET /health` | Responde `{"status": "ok"}` con código 200 si el proceso está vivo. Lo usarán Docker, el gateway y el monitor externo. **No** revisa la base de datos: eso será `GET /health/ready` (T-06) |

La *docstring* de cada endpoint (el texto entre `"""` debajo del `def`) aparece como descripción en la documentación automática `/docs`.

## `tests/test_health.py`
| Elemento | Qué es | Para qué |
| --- | --- | --- |
| `client = TestClient(app)` | "Navegador falso" | Hace peticiones a la app sin encender el servidor |
| `test_health_returns_ok()` | Test | Comprueba que `GET /health` responde 200 y `{"status": "ok"}`. Si alguien rompe `/health`, falla |

Convenciones de pytest: la carpeta se llama `tests/`, los archivos empiezan con `test_` y las funciones también.

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

## Rutas disponibles
| Método y ruta | Respuesta | Permiso | Desde |
| --- | --- | --- | --- |
| `GET /health` | `200 {"status": "ok"}` | Ninguno | Semana 1 |
| `GET /docs` | Documentación interactiva (OpenAPI) | Ninguno | Semana 1 |
