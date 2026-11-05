# Ciclo de vida del software (SDLC) y plan de aprendizaje DevOps

Este documento define **cómo** se construye el sistema, no **qué** se construye (eso está en docs/01 a 04). El objetivo doble es entregar un sistema útil a la librería y aprender DevOps y microservicios en la práctica.

## 1. Modelo elegido: iterativo e incremental con ciclo DevOps

No usamos cascada (todo el análisis primero, todo el código después) porque los requerimientos todavía dependen de la entrevista y porque DevOps se aprende repitiendo el ciclo muchas veces.

- **Fases macro (una sola vez, se revisan si cambia algo):** Descubrimiento → Análisis → Diseño de arquitectura.
- **Iteraciones (una por capa del roadmap):** cada capa recorre el ciclo DevOps completo y termina en algo desplegado y funcionando.

```
         ┌──────────── DEV ────────────┐   ┌──────────── OPS ────────────┐
 PLAN → CODE → BUILD → TEST → RELEASE → DEPLOY → OPERATE → MONITOR ─┐
   ▲                                                                 │
   └──────────────────── feedback (bugs, métricas, usuarios) ────────┘
```

## 2. Fases macro

| Fase | Pregunta que responde | Entregables | Estado |
| --- | --- | --- | --- |
| Descubrimiento | ¿Qué problema tiene el negocio? | Guía de entrevista consolidada, resultados (docs/entrevista) | Hecho (27/10) |
| Análisis | ¿Qué debe hacer el sistema? | RF/RNF, perfiles, casos de uso (docs/01, 02, 05) | Hecho; falta validación formal del dueño |
| Diseño | ¿Cómo se organiza? | Modelo y reglas, arquitectura, ADRs (docs/03, 04, adr) | Hecho para el MVP; diagramas pendientes |

Salida de estas fases: requerimientos validados con el negocio y ADRs aprobados. Los casos de uso no críticos se detallan al llegar a su semana.

## 3. Ciclo de cada iteración

| Etapa | Qué se hace | Herramienta / práctica | Lo que aprendes |
| --- | --- | --- | --- |
| Plan | Historias de usuario con criterios de aceptación, priorizadas en un tablero | GitHub Issues + Projects (Kanban) | Gestión ágil, Definition of Ready |
| Code | Rama corta por historia, commits pequeños | Git, trunk-based, Conventional Commits | Control de versiones en equipo |
| Build | Imagen Docker por servicio, reproducible | Dockerfile multi-stage, Docker Compose | Contenedores, inmutabilidad |
| Test | Unitarios, integración con BD real, contrato entre servicios | pytest, Testcontainers, Ruff | Pirámide de pruebas, shift-left |
| Release | Versión semántica, changelog, imagen etiquetada | SemVer, tags, GitHub Releases, GHCR | Artefactos versionados |
| Deploy | Despliegue automático a staging y luego a producción | GitHub Actions, Compose en VPS → Terraform en cloud | CI/CD, entornos, IaC |
| Operate | Backups, secretos, seguridad del servidor | pg_dump cifrado, `.env`, UFW, fail2ban | Operación y hardening |
| Monitor | Salud, logs, métricas, alertas | Health checks, Uptime Kuma → Prometheus + Grafana + Loki | Observabilidad, SLOs |

## 4. Flujo de trabajo (reglas del día a día)

### Ramas
- `main` siempre desplegable y protegida (no se hace push directo).
- Ramas cortas: `feat/<issue>-descripcion`, `fix/...`, `chore/...`, `docs/...`.
- Todo entra por **Pull Request** con CI en verde. Aunque trabajes solo, el PR es la revisión y el registro.

### Commits (Conventional Commits, en inglés)
`feat(core): reserve available stock on order confirmation` · `fix(auth): ...` · `chore(ci): ...` · `docs(adr): ...`
Esto permite generar el changelog y decidir la versión automáticamente.

### Definition of Ready (una historia se puede empezar si…)
- Tiene criterios de aceptación verificables.
- Se sabe a qué servicio pertenece.
- No depende de una respuesta pendiente de la entrevista.

### Definition of Done (una historia está terminada si…)
- Código revisado en PR y fusionado a `main`.
- Tests automáticos de cada regla de negocio involucrada, en verde en CI.
- Migración de BD incluida si cambió el esquema.
- API documentada en OpenAPI; docstrings en el código y guía `docs/codigo/<servicio>.md` actualizada.
- Desplegada en staging y verificada (staging existe desde la semana 5; antes, verificada con Docker Compose en local).
- Documentación/ADR actualizada si cambió una decisión.

### Entornos
| Entorno | Para qué | Cómo se despliega |
| --- | --- | --- |
| local | Desarrollo | `docker compose up` |
| ci | Pruebas automáticas en cada PR | GitHub Actions (servicios efímeros) |
| staging | Probar antes de producción, con datos de prueba | Automático al fusionar en `main` |
| production | Uso real de la librería | Manual (aprobación) a partir de un tag `vX.Y.Z` |

### Versionado
- En el MVP hay **una sola versión para todo el sistema** (tag `vX.Y.Z` del monorepo), porque auth, core y el frontend se despliegan juntos. Mientras sea `0.x` se permiten cambios incompatibles. Versiones por servicio (`auth v0.3.0`, `core v0.5.1`) cuando se desplieguen por separado.
- Cambios de API entre servicios: versionar la ruta (`/api/v1/...`) y los eventos (`OrderConfirmed.v1`).

## 5. Plan de aprendizaje por capa

Cada capa del roadmap se usa para practicar un concepto concreto de DevOps o microservicios. La numeración y las fechas son las del calendario de docs/04 (ADR-0005). El frontend se construye dentro de cada capa.

| Capa | Entregable funcional | Concepto DevOps / microservicios que practicas |
| --- | --- | --- |
| 0. Preparación | Herramientas, Git/GitHub, API "hola mundo" | Entorno reproducible, control de versiones |
| 1. Base técnica | Monorepo, Compose, gateway, CI | Contenedores, red de Docker, API gateway, primer pipeline CI |
| 2. Auth | Login JWT, perfiles y permisos | Servicio independiente con su BD, autenticación distribuida (JWT validado en gateway) |
| 3. Catálogo | Productos, presentaciones, precios, importación Excel | Migraciones versionadas, tests de integración con Testcontainers; build y deploy del frontend |
| 4. Stock | Kardex, ingresos, ajustes, transferencias, inventario inicial | Transacciones y concurrencia, tests de reglas críticas; primer deploy a staging en la nube |
| 5. Pedidos | Reserva, faltantes, pagos, nota de venta | Máquina de estados, contratos de API |
| 6. Despachos | Total/parcial, entrega con rechazo | Despliegue continuo a staging, smoke tests post-deploy |
| 7. Producción | HTTPS, backups PITR, monitoreo | Prueba de restauración, alertas, chaos test simple (apagar un servicio) |
| 8. Eventos (post-MVP) | Broker + outbox, notificaciones | Comunicación asíncrona, outbox, idempotencia, reintentos, dead letter queue |
| 9. Reportes (post-MVP) | Servicio de reportes | CQRS / proyecciones por eventos, tolerancia a fallos (RNF-10) |
| 10. Observabilidad (post-MVP) | Prometheus, Grafana, Loki | Métricas, logs, trazas, SLOs |
| 11. Integraciones (post-MVP) | Puente con facturación | Anti-corruption layer, reintentos |
| 12. Cloud (post-MVP) | Migración con Terraform | IaC, registro de contenedores, secretos gestionados, opcional Kubernetes |

**Regla de oro:** no se agrega un microservicio nuevo hasta que el anterior tenga pipeline, tests, health check y despliegue funcionando. Así cada servicio nuevo cuesta menos y el aprendizaje se acumula.

## 6. Mantenimiento y evolución
- Bugs y pedidos del negocio entran como Issues etiquetados (`bug`, `feature`, `negocio`).
- Dependencias actualizadas con Dependabot; escaneo de imágenes con Trivy en CI.
- Retrospectiva corta al cerrar cada capa: qué funcionó, qué mejorar, qué ADR cambia. Se anota al final de este documento.

## 7. Retrospectivas
_(se completa al cerrar cada capa)_
