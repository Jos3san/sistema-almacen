# Guía del código: librería compartida `libs/security`

Explicación en español de la librería que valida los tokens de acceso (T-11, ADR-0007, docs/06 D1.3). Se actualiza **en el mismo Pull Request** que cambia `libs/security`.

Última actualización: 21/11/2026 · Semana 3 (T-11).

## Qué es y por qué existe
auth **firma** los tokens de acceso con su clave privada (RS256). Cada servicio (hoy core) los **valida** con la clave pública, que recibe como archivo montado, **sin llamar a auth**: si auth se cae, los tokens vigentes siguen funcionando hasta 15 minutos (RNF-10).

Validar un token tiene varios detalles de seguridad. Si cada servicio lo programara por su cuenta, tarde o temprano uno se equivocaría. Por eso la validación vive **una sola vez** aquí (DRY, docs/06 D1.11). Es el **único código compartido** entre servicios: nada de lógica de negocio va en `libs/` (docs/06 D1.5).

## Estructura
```
libs/security/
├── pyproject.toml          paquete "almacen-security": PyJWT y FastAPI
├── src/almacen_security/
│   ├── __init__.py         lo que se puede importar: TokenValidator, TokenGuard, TokenClaims, InvalidTokenError
│   ├── tokens.py           validación del token
│   └── dependencies.py     protección de endpoints de FastAPI (401/403)
└── tests/                  15 tests: cada forma de romper o atacar un token
```
core la instala como dependencia de ruta (`[tool.uv.sources] almacen-security = { path = "../../libs/security" }`).

## `tokens.py`
| Elemento | Qué es | Para qué |
| --- | --- | --- |
| `ALGORITHM = "RS256"` | Constante | El algoritmo está **fijo**: nunca se lee del token. Si se leyera, un atacante podría mandar `alg: none` (sin firma) o `HS256` firmado con la clave pública, que es pública (OWASP A08) |
| `REQUIRED_CLAIMS` | Lista | `sub`, `name`, `perms`, `iss`, `aud`, `iat`, `exp`: si falta alguno, el token se rechaza |
| `TokenClaims` | Datos del usuario | `user_id`, `name` y `permissions`. `has("order.create")` dice si tiene un permiso |
| `TokenValidator` | Validador | Lee la clave pública **una vez** del archivo y, en `validate()`, revisa firma, emisor (`iss`), destinatario (`aud`) y vencimiento (`exp`). Cualquier error → `InvalidTokenError` |

## `dependencies.py`
| Elemento | Qué es | Para qué |
| --- | --- | --- |
| `TokenGuard(get_validator)` | Fábrica de dependencias de FastAPI | Cada servicio crea uno al arrancar |
| `guard.current_user()` | Dependencia | Exige un token válido: si falta o es inválido → **401** con `WWW-Authenticate: Bearer`. El mensaje es siempre el mismo ("Invalid token"), para no darle pistas a un atacante |
| `guard.require("perm.code")` | Dependencia | Además exige el permiso: sin él → **403** |

Uso en un endpoint:
```python
@app.post("/v1/orders")
def create_order(user: Annotated[TokenClaims, Depends(guard.require("order.create"))]):
    ...
```
**401 o 403:** 401 = "no sé quién eres" (sin token o token inválido). 403 = "sé quién eres, pero no puedes hacer esto".

## Tests
| Archivo | Prueba |
| --- | --- |
| `conftest.py` | Genera un par de claves RSA **de prueba** y una función `make_token()` que firma tokens como lo haría auth |
| `test_tokens.py` | Token válido; vencido; firmado con otra clave; de otro `aud`; de otro `iss`; **sin firma (`alg: none`)**; **HS256 firmado con la clave pública**; sin `perms`; `perms` con tipo incorrecto |
| `test_dependencies.py` | En una app de prueba: sin token → 401; token inválido → 401 con mensaje genérico; válido → 200; con permiso → 200; sin permiso → 403 |

Los dos ataques (`alg: none` y HS256 con la clave pública) se arman **a mano** en el test (`build_unverified_token`), porque PyJWT se niega a crear esos tokens. Así se prueba el ataque real, no una imitación.

## Comandos (desde `libs/security`)
| Comando | Qué hace |
| --- | --- |
| `uv sync` | Instala la librería y sus herramientas |
| `uv run pytest` | Corre los 15 tests |
| `uv run ruff format .` / `uv run ruff check .` | Formato y revisión, con las mismas reglas que los servicios (incluidas `S` y `C90`) |

La CI corre lo mismo en el job `core / lint and tests`, porque core depende de esta librería.
