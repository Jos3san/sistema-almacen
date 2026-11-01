# Arquitectura, stack y roadmap

## Stack (backend: Python + FastAPI, ADR-0006)
| Aspecto | A. Java (descartada) | B. Python (elegida) |
| --- | --- | --- |
| Backend | Java 21 + Spring Boot | FastAPI + SQLAlchemy + Pydantic |
| Migraciones | Flyway | Alembic |
| Tests | JUnit + Testcontainers | pytest + Testcontainers |
| PDF | OpenPDF / JasperReports | WeasyPrint |
| RAM por servicio | 250–500 MB | 50–100 MB |
| Curva para principiante | Alta | Baja |
| Encaje Cloud/MLOps | Medio | Alto |

Frontend: React + TypeScript (Vite), Tailwind, TanStack Query, React Hook Form + Zod. Celular para vendedores y repartidores, escritorio para dueño y almacén. **Se construye junto con cada capa**, no al final.

## Microservicios
Objetivo: si un servicio falla, tomar pedidos y consultar stock sigue funcionando (RNF-10).

| Servicio | Responsabilidad | Si falla | Cuándo |
| --- | --- | --- | --- |
| gateway | Entrada única (Caddy): HTTPS, enruta y sirve el frontend; el JWT lo valida cada servicio (ADR-0007) | Crítico | MVP |
| auth | Usuarios, perfiles, permisos, emisión de JWT | Los tokens vigentes siguen funcionando | MVP |
| core (inventario + pedidos + despachos) | Catálogo, stock, kardex, pedidos, despachos, notas en PDF, auditoría | Crítico; un solo servicio para mantener la transacción de stock | MVP |
| reports | Consolidados y exportación | La operación no se afecta | MVP como módulo de lectura en core; servicio aparte después |
| notifications | WhatsApp/correo por eventos | Eventos esperan en la cola | Después del MVP |
| integrations | Puente con el sistema de facturación | Eventos esperan en la cola | Después del MVP |

- Cada servicio con su propia base de datos (o esquema).
- Eventos (RabbitMQ o Redis Streams) vía **outbox**: después del MVP, cuando llegue `notifications`.
- Health checks, timeouts, reintentos con backoff.
- Dentro de `core`, módulos con límites estrictos para dividirlo después si crece.

## Calendario MVP (28/10 → 19/12/2026)
Cada semana termina con algo desplegado en staging y una revisión con el dueño (desde la semana 4).

| Semana | Fechas | Capa | Entregable |
| --- | --- | --- | --- |
| 1 | 28/10 – 02/11 | 0. Preparación | Herramientas, Git/GitHub, decisión de lenguaje, API "hola mundo" |
| 2 | 03/11 – 09/11 | 1. Base técnica | Docker, Compose (API + PostgreSQL), gateway, CI con lint + tests |
| 3 | 10/11 – 16/11 | 2. Auth | Login JWT, perfiles y permisos, pantalla de login, auditoría base |
| 4 | 17/11 – 23/11 | 3. Catálogo | Productos, presentaciones, escalas de precio, ubicaciones, clientes, importación Excel |
| 5 | 24/11 – 30/11 | 4. Stock | Kardex, ingresos, ajustes, transferencias, inventario inicial; deploy a staging en la nube con HTTPS |
| 6 | 01/12 – 07/12 | 5. Pedidos | Crear/modificar/anular, reserva, faltantes por conseguir y su asignación automática al entrar stock (RF-41, RF-42), pagos, nota de venta PDF |
| 7 | 08/12 – 14/12 | 6. Despachos | Bandeja, despacho parcial, en camino, entrega con rechazo, registro tardío |
| 8 | 15/12 – 19/12 | 7. Producción | Reportes MVP, HTTPS, backups PITR, monitoreo, prueba de restauración, capacitación |
| — | 21/12 – 31/12 | Carga | El negocio carga productos e inventario inicial; soporte y correcciones |
| — | Enero 2027 | Operación | Uso real en campaña escolar |

Si una semana se atrasa, se recorta alcance (no calidad): primero reportes, luego transferencias, luego pagos detallados.

## Después del MVP
| Capa | Entregable |
| --- | --- |
| 8. Eventos | Broker + outbox, servicio `notifications` (alertas de stock mínimo) |
| 9. Reportes | Servicio `reports` separado, más vendidos, sugerencia de compra |
| 10. Observabilidad | Prometheus + Grafana + Loki, alertas |
| 11. Integraciones | Puente con el sistema de facturación |
| 12. Cloud | Terraform (AWS/Azure), registro de contenedores, secretos gestionados |

## Infraestructura
- Nube: VPS en un proveedor cloud (o instancia pequeña AWS/Azure), Ubuntu LTS, Docker Compose, Caddy + Let's Encrypt.
- Dominio: no tienen; usar uno barato o un subdominio gratuito para tener HTTPS. Se necesita desde la semana 5 (staging).
- GitHub Actions: lint + tests en PR; build y deploy a staging al fusionar en `main`; producción manual por tag.
- Backups: archivado continuo de WAL (pgBackRest o WAL-G) para RPO ≤ 1 h + `pg_dump` diario cifrado fuera del servidor, retención 30 días, prueba de restauración mensual.
- Monitoreo MVP: Uptime Kuma **fuera del servidor** (u otro monitor externo) con alertas al celular del desarrollador.
- UFW (22, 80, 443), SSH con llave, fail2ban.
- Conectividad: el almacén externo necesita datos móviles o router 4G.

## Estructura de repo sugerida
```
sistema-almacen/
├── services/
│   ├── auth/
│   ├── core/
│   ├── notifications/   (después del MVP)
│   ├── reports/         (después del MVP)
│   └── integrations/    (después del MVP)
├── frontend/
├── infra/ (docker-compose, caddy, backup, terraform)
├── docs/ (adr/, este material)
├── .github/workflows/
└── CLAUDE.md
```

## Preguntas abiertas
- ~~Lenguaje del backend~~: Python + FastAPI (ADR-0006).
- ~~Productos y precios (#56)~~: resuelto, este sistema es la fuente de verdad del catálogo.
- Conectividad del almacén externo.
- Información del sistema de facturación.
