# Sistema de Almacén, Pedidos y Despachos (Librería)

## Contexto
- Sistema web a medida para una librería real (cliente; sus datos reales no se publican): almacén, stock, pedidos de vendedores y despachos, **hasta la nota de venta**.
- **No incluye facturación electrónica** (boletas/facturas SUNAT): el negocio ya tiene un sistema aparte para eso.
- Es también un **proyecto de portafolio** del desarrollador (Jossan, perfil Infra TI → Cloud → Platform/MLOps). Debe mostrar buena arquitectura, DevOps, tests y documentación.
- Debe ser accesible desde cualquier lugar (web, responsive; vendedores usan el celular).
- Se construye **por capas** (ver `docs/04-arquitectura-y-roadmap.md`).

## Estado actual (07/11/2026)
- Entrevista respondida, consolidada y evaluada: `docs/entrevista/resultados.md`. Docs 01–05 actualizados con sus resultados. No inventar datos del negocio que no estén ahí: preguntar.
- Negocio: varias ubicaciones de stock (tiendas y almacenes), unos cientos de productos, un equipo pequeño (dueño, vendedores, repartidores), decenas de pedidos al día y unas 4 veces más en campaña. **Cifras reales solo en `D:/proyectoLibreria-privado`** (fuera del repo); los docs del repo usan valores genéricos o ficticios.
- **Plazo: MVP listo ≈ 19/12/2026**; el negocio carga datos la última semana de diciembre; producción en enero 2027. Calendario semanal en docs/04. Ante atrasos se recorta alcance, no calidad.
- Desarrollo con productos de prueba (los datos reales los carga el negocio).
- Semana 1 cerrada el 05/11 (B5, tablero, movido a la semana 3): `services/core` con `GET /health`, test y Ruff, fusionado por el PR #1. Flujo de trabajo: rama → PR → merge con rebase (`main` protegida). Semana 2: T-05 (imagen Docker de core) fusionada por el PR #2 el 07/11. Seguridad (OWASP + DevSecOps, T-20) y principios de código en docs/06 D1.10–D1.11. T-06 (Compose + PostgreSQL 18 + `/health/ready`) fusionada por el PR #4. T-07 (gateway Caddy en `http://localhost/api/core/`) fusionada por el PR #5. T-08 (CI con GitHub Actions) en curso; luego T-09 y T-10. T-20 (DevSecOps) movida al inicio de la semana 3 con el tablero.
- Repo público (portafolio): el dueño aceptó publicar el trabajo **sin ninguna información relevante del negocio** (nombre, dominio, direcciones, clientes, proveedores, precios, cifras reales): solo datos ficticios. Lo real va en `.env` o fuera del repo. La entrevista respondida no se sube.

## Decisiones tomadas
- Backend: **Python 3.13 + FastAPI** (ADR-0006): SQLAlchemy 2, Pydantic, Alembic, pytest + Testcontainers, Ruff, uv.
- Frontend: libre; propuesta React + TypeScript (Vite) + Tailwind.
- Base de datos: PostgreSQL.
- Arquitectura: el usuario quiere **microservicios** para que la falla de uno no detenga la operación y el sistema pueda crecer. Propuesta acordada como base (ver docs/04):
  - Un **servicio núcleo** Inventario + Pedidos + Despachos (comparten la transacción de stock), con módulos de límites estrictos.
  - Servicios separados para lo que puede fallar sin parar la operación: Auth, Notificaciones, Reportes, Integraciones.
  - Comunicación asíncrona por eventos (RabbitMQ o Redis Streams) con **patrón outbox**.
  - MVP solo con gateway + auth + core (ADR-0005); el resto después de salir a producción.
- Infra: Docker Compose, Caddy (HTTPS automático) como gateway, GitHub Actions, VPS al inicio; luego cloud (AWS/Azure) con Terraform. Una instancia PostgreSQL con una base por servicio.
- Seguridad: JWT RS256 firmado por auth y validado en cada servicio con la clave pública como archivo; access 15 min, refresh rotado 7 días (ADR-0007, docs/06).

## Reglas de negocio no negociables
1. El stock **nunca se edita**: todo cambio es un movimiento (kardex, solo inserciones).
2. Stock físico, reservado y disponible (= físico − reservado).
3. Confirmar pedido → reserva lo disponible (no hay aprobación); el resto queda por conseguir y se reserva al entrar stock (FIFO por pedido). Despachar → descuenta físico y reserva. Rechazo en la entrega → DEVOLUCION al stock.
4. Despachos parciales permitidos. Stock siempre en unidad base (presentaciones con factor).
5. Concurrencia: `SELECT ... FOR UPDATE` en orden por producto_id; CHECK en BD contra negativos.
6. Precios congelados en el pedido; numeración correlativa sin saltos (tabla contador en la misma transacción, no secuencias). Cantidades enteras en unidad base. Orden único de bloqueo: stock primero, luego líneas de pedido.
Detalle en `docs/03-modelo-datos-y-reglas.md`.

## Convenciones
- Código, nombres de API y commits en inglés; interfaz de usuario en español; moneda PEN; zona horaria America/Lima.
- Montos `NUMERIC(12,2)`, nunca float.
- Cada regla de negocio con su test automático.
- **Documentar el código**: cada módulo, función y test con *docstring* en inglés (qué hace y para qué; los endpoints la muestran en `/docs`). La explicación en español para aprender va en `docs/codigo/<servicio>.md` y se actualiza **en el mismo PR** que cambia el código.
- Decisiones de arquitectura en `docs/adr/`.
- Código por capas en cada módulo: `api` → `service` → `repository` (docs/06 D1.11); KISS y YAGNI antes que abstracciones.
- Seguridad: cada cambio respeta la tabla OWASP de docs/06 D1.10; cada endpoint protegido con tests 401/403.
- Secretos solo en `.env` (nunca en el repo).

## Cómo trabajar con el usuario
- Responder en español.
- Objetivo de aprendizaje: **DevOps y microservicios**. El proyecto sigue un ciclo de vida explícito (`docs/00-ciclo-de-vida.md`); explicar el "por qué" de cada práctica DevOps al aplicarla.
- Nivel: conoce el ciclo de vida del software en teoría, pero es **principiante en programación y DevOps**. Guiarlo paso a paso: explicar el concepto, que él ejecute el paso, verificar juntos el resultado. No generar grandes bloques de código sin explicarlos.
- Aprende haciendo: avanzar en pasos concretos y funcionales, una capa a la vez.
- Ser honesto con los trade-offs (p. ej. costo operativo de microservicios).

## Documentos
- `docs/00-ciclo-de-vida.md` — ciclo de vida (SDLC), flujo de trabajo y plan de aprendizaje DevOps
- `docs/01-resumen-y-alcance.md` — objetivos, alcance, roles
- `docs/02-requerimientos.md` — RF y RNF
- `docs/03-modelo-datos-y-reglas.md` — entidades y reglas
- `docs/04-arquitectura-y-roadmap.md` — stack, microservicios, calendario MVP, infra
- `docs/05-casos-de-uso.md` — actores, catálogo de casos de uso, hallazgos y detalle de los críticos
- `docs/06-diseno-tecnico.md` — ruta del diseño (D1–D7), arquitectura C4, seguridad, flujos, estructura del repo, seguridad OWASP y DevSecOps (D1.10), principios de código (D1.11), catálogo de permisos (D2)
- `docs/07-backlog.md` — backlog del MVP (D3): historias HU y técnicas T por semana; detalle completo hasta la semana 3
- `docs/08-glosario.md` — términos del negocio y siglas (agregar aquí toda sigla nueva)
- `docs/codigo/` — guía en español del código de cada servicio (estructura, archivos, funciones, comandos); `core.md` desde el 05/11, `infra.md` (Compose y Caddy) desde el 07/11
- `docs/entrevista/resultados.md` — resumen de la entrevista, decisiones, riesgos y pendientes
- `D:/proyectoLibreria-privado/Guia_Entrevista_Sistema_Almacen.xlsx` (**privado, fuera del repo**) — **entrevista respondida**: col. G = respuesta original; col. J–N = respuesta consolidada, decisión, RF/RNF, UC y alcance (fuente para generar documentos)
- `D:/proyectoLibreria-privado/docs-reales/` y `CLAUDE-real.md` — copia de los docs con las cifras reales del negocio (31/10/2026). Si un doc público cambia una decisión, actualizar también la copia privada si afecta a cifras reales.
- `docs/entrevista/Guia_Entrevista_Sistema_Almacen.xlsx` — plantilla en blanco generada por `build_guia.py`
- `docs/adr/` — decisiones de arquitectura (0001–0007)
- `docs/semanas/` — checklist de seguimiento por semana (qué está hecho, qué hace el usuario y qué se le muestra)
