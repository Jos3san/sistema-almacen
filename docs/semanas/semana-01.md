# Semana 1 (28/10 – 02/11) · Capa 0: Preparación

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
- [ ] R2 · Git crea la rama `master` por defecto; el proyecto usa `main` → `init.defaultBranch main` 🛠️
- [x] R3 · Finales de línea: Windows usa CRLF y Linux/Docker LF → `.gitattributes` con `eol=lf` 🧑‍🏫 (creado 31/10)
- [x] R4 · Archivos sobrantes de la planificación: `PRIMER_PROMPT.md` y `sistema-almacen.zip` → borrados (31/10)
- [x] R5 · El repo será público: el dueño aceptó portafolio **con datos ficticios y sin el nombre del negocio** → la entrevista respondida y la copia real de los docs se movieron a `D:/proyectoLibreria-privado` (31/10); los docs del repo quedaron anonimizados y `.gitignore` excluye `/*.xlsx`

## B. Git y GitHub
- [ ] B1 · `git init` en el proyecto (`.gitignore` y `.gitattributes` ya creados el 31/10) 🛠️
- [ ] B2 · Primer commit con la documentación (Conventional Commits: `docs: ...`)
- [ ] B3 · Repo en GitHub y primer push
- [ ] B4 · Proteger `main`: solo entra por PR, sin exigir aprobaciones (trabajas solo; T-02 en docs/07)
- [ ] B5 · Tablero GitHub Projects con las historias de la semana 2

## C. API "hola mundo"
- [ ] C1 · Crear `services/core` con `uv init`
- [ ] C2 · Endpoint `GET /health` con FastAPI
- [ ] C3 · Primer test con pytest
- [ ] C4 · Ruff sin errores
- [ ] C5 · Todo entra a `main` por un PR

## Notas
_(qué aprendiste, qué falló y cómo lo resolviste)_
