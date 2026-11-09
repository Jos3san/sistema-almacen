# Semana 1 (28/10 – 02/11, cerrada el 05/11) · Capa 0: Preparación

Objetivo: entorno reproducible + control de versiones + API "hola mundo".
Marca `[x]` cada punto al terminarlo y anota en "Notas" lo que te costó o aprendiste.
Leyenda: 🧑‍🏫 = te muestro cómo · 🛠️ = lo haces tú siguiendo el patrón.

## A. Herramientas

Estado revisado el 28/10/2026:

| # | Herramienta | Para qué | Estado | Quién |
| --- | --- | --- | --- | --- |
| A1 | Git | Control de versiones | Instalado (2.54) | — |
| A2 | Identidad de Git | Que los commits digan quién los hizo | Configurada (correo noreply) | 🛠️ |
| A3 | VS Code | Editor | Instalado | — |
| A4 | Python 3.13 | Lenguaje del backend (ADR-0006) | Instalado (3.13.15) | 🧑‍🏫 |
| A5 | uv | Gestiona Python, dependencias y entornos virtuales | Instalado (0.13.6) | 🛠️ |
| A6 | Node.js LTS | Frontend (Vite + React) | Instalado (24.22.1) | 🛠️ |
| A7 | GitHub CLI (`gh`) | PRs, issues y Actions desde la terminal | Instalado (2.103.3), sesión iniciada (Jos3san) | 🛠️ |
| A8 | Docker Desktop | Contenedores (se usa fuerte en la semana 2) | Funcionando (motor 29.9.2), hello-world OK | 🛠️ |
| A9 | Extensiones de VS Code | Python, Ruff, GitLens, Even Better TOML, Container Tools, YAML | Instaladas | 🛠️ |

- [x] A2 · Identidad de Git configurada
- [x] A4 · Python 3.13 (`python --version` → 3.13.x)
- [x] A5 · uv (`uv --version`)
- [x] A6 · Node.js LTS (`node --version`, `npm --version`)
- [x] A7 · GitHub CLI (`gh --version`) y sesión iniciada (`gh auth status`)
- [x] A8 · Docker funcionando (`docker run hello-world`)
- [x] A9 · Extensiones de VS Code

Extensiones que se agregan al llegar su capa (no antes):

| Semana | Extensión | Id |
| --- | --- | --- |
| 2 (CI) | GitHub Actions | `github.vscode-github-actions` |
| 3–4 (frontend) | ESLint | `dbaeumer.vscode-eslint` |
| 3–4 (frontend) | Prettier | `esbenp.prettier-vscode` |
| 3–4 (frontend) | Tailwind CSS IntelliSense | `bradlc.vscode-tailwindcss` |

### Revisión general (28/10)
Herramientas verificadas. Ajustes encontrados antes de la sección B:

- [x] R1 · PowerShell bloquea scripts (política `Restricted`), así que `npm` va a fallar → el usuario la cambia a `RemoteSigned` solo para su cuenta 🛠️
- [x] R2 · Git crea la rama `master` por defecto; el proyecto usa `main` → `init.defaultBranch main` 🛠️
- [x] R3 · Finales de línea: Windows usa CRLF y Linux/Docker LF → `.gitattributes` con `eol=lf` 🧑‍🏫 (creado 31/10)
- [x] R4 · Archivos sobrantes de la planificación: `PRIMER_PROMPT.md` y `sistema-almacen.zip` → borrados (31/10)
- [x] R5 · El repo será público: el dueño aceptó portafolio **con datos ficticios y sin el nombre del negocio** → la entrevista respondida y la copia real de los docs se movieron a `D:/proyectoLibreria-privado` (31/10); los docs del repo quedaron anonimizados y `.gitignore` excluye `/*.xlsx`

## B. Git y GitHub
- [x] B1 · `git init` en el proyecto (`.gitignore` y `.gitattributes` creados el 31/10) 🛠️
- [x] B2 · Primer commit con la documentación (`2bc43fa docs: add project planning, analysis and design documentation`, 31/10)
- [x] B3 · Repo público `Jos3san/sistema-almacen` y primer push (31/10); GitHub dibuja los diagramas Mermaid
- [x] B4 · Ruleset `proteger-main` activo (sin bypass): PR obligatorio con 0 aprobaciones, sin borrar ni force push; Actions exige aprobación a todo contribuyente externo (31/10)
- [ ] B5 · Tablero GitHub Projects → **movido al inicio de la semana 3** (07/11), con las historias de auth (docs/07, T-04)

## C. API "hola mundo"
- [x] C1 · Crear `services/core` con `uv init` en la rama `feat/core-health` (05/11); uv generó la estructura de paquete `src/core/`, que se adoptó en docs/06
- [x] C2 · Endpoint `GET /health` con FastAPI 0.162 (05/11): responde 200 `{"status": "ok"}`; `/docs` funciona
- [x] C3 · Primer test con pytest 9.2 (05/11): `tests/test_health.py`, 1 passed; se vio fallar a propósito. Código documentado (docstrings) y guía `docs/codigo/core.md`
- [x] C4 · Ruff 0.17 sin errores (05/11): reglas E, F, I, B, UP; lint y formato en verde; se vio fallar a propósito (F401 por un import sin usar y un error de formato)
- [x] C5 · Primer Pull Request #1 fusionado con rebase (05/11): commits `3137540 feat(core)` y `4b9e529 docs`; rama borrada

## Notas
Tu retrospectiva (también va resumida en docs/00, sección 7). Unas líneas por pregunta:
1. ¿Qué funcionó bien y conviene repetir?
2. ¿Qué costó más de lo esperado y por qué?
3. ¿Qué cambio concreto hago en la próxima capa?
