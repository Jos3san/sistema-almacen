# Semana 2 (03/11 – 09/11) · Capa 1: Base técnica

Objetivo: que `core` corra en contenedores, detrás del gateway, con CI que bloquee lo que esté roto.
Marca `[x]` cada punto al terminarlo y anota en "Notas" lo que te costó o aprendiste.
Leyenda: 🧑‍🏫 = te muestro cómo · 🛠️ = lo haces tú siguiendo el patrón.

Detalle y criterios de aceptación de cada tarea: `docs/07-backlog.md`.

## T-05 · Imagen Docker de core 🧑‍🏫
- [x] Rama `chore/week-2-docker` creada (incluye los cambios pendientes de la semana 1)
- [x] `.dockerignore` en la raíz del repo
- [x] `services/core/Dockerfile` multi-stage, base con versión fija, usuario no root
- [x] `docker build` desde la raíz del repo termina sin errores
- [x] `docker run` + `GET /health` responde `{"status": "ok"}`
- [x] `docs/codigo/core.md` explica el Dockerfile y los comandos
- [x] PR fusionado (PR #2, 07/11)

## Seguridad y principios (docs/06 D1.10 y D1.11) 🧑‍🏫
- [ ] PR de documentación fusionado
- [ ] Secret scanning con push protection activo en GitHub
- [ ] Alertas de Dependabot activas en GitHub

## T-06 · Docker Compose con PostgreSQL 🧑‍🏫
- [ ] `infra/compose.yaml` con core + PostgreSQL 18 y volumen
- [ ] `.env.example` sin valores reales; `.env` local fuera del repo
- [ ] `GET /health/ready` comprueba la base

## T-07 · Gateway con Caddy 🛠️
- [ ] `/api/core/health` responde a través de Caddy
- [ ] `/api/core/docs` muestra la documentación
- [ ] Cabeceras de seguridad presentes y sin cabecera `Server`

## T-08 · Integración continua 🧑‍🏫
- [ ] Workflow de GitHub Actions con Ruff y pytest
- [ ] Laboratorio: un PR que falla a propósito y GitHub no deja fusionar
- [ ] El ruleset de `main` exige la CI en verde

## T-09 · Logs estructurados 🛠️
- [ ] Logs JSON con `X-Request-ID`, sin tokens ni cuerpos

## T-10 · Migraciones con Alembic 🧑‍🏫
- [ ] Alembic configurado con dos usuarios de BD (migraciones y aplicación)

## T-20 · Seguridad automatizada en CI (DevSecOps) 🧑‍🏫
- [ ] `.github/dependabot.yml` (uv, Docker, GitHub Actions)
- [ ] Ruff `S` y `C90`, pip-audit y Trivy en la CI
- [ ] CodeQL activo

## Notas
_(lo que te costó, lo que aprendiste)_
