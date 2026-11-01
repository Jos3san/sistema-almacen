# Backlog del MVP (D3)

Parte D3 del diseño (docs/06). Cada historia será un **Issue** en GitHub y una tarjeta en GitHub Projects (semana 1, B5).

- **HU-xx**: historia de usuario. Formato: *Como [perfil], quiero [acción], para [beneficio]*.
- **T-xx**: historia técnica (lo que necesita el equipo para construir y operar).
- **Tamaño**: S (≤ medio día), M (1–2 días), L (3+ días, conviene partirla).
- Una historia empieza si cumple la *Definition of Ready* y termina con la *Definition of Done* (docs/00).
- Detalle completo solo hasta la semana 3; de la 4 en adelante se detalla al inicio de cada semana (ADR-0002).

## Resumen por semana
| Semana | Capa | Historias |
| --- | --- | --- |
| 1 | 0. Preparación | T-01 a T-04 |
| 2 | 1. Base técnica | T-05 a T-10 |
| 3 | 2. Auth | HU-01 a HU-06, T-11 a T-13 |
| 4 | 3. Catálogo | HU-07 a HU-13 |
| 5 | 4. Stock | HU-14 a HU-20, T-14 |
| 6 | 5. Pedidos | HU-21 a HU-27 |
| 7 | 6. Despachos | HU-28 a HU-32 |
| 8 | 7. Producción | HU-33 a HU-36, T-15 a T-19 |

---

## Semana 1 · Capa 0: Preparación
(El seguimiento paso a paso está en `docs/semanas/semana-01.md`.)

### T-01 Repositorio Git local · S
- `git init` con rama `main`, `.gitattributes` con `eol=lf` y `.gitignore` que excluye `.env`, claves, `.venv`, `node_modules` y la entrevista respondida (`*.xlsx` de la raíz).
- Antes del primer commit, docs/ revisado: **sin datos reales del negocio** (repo público).

### T-02 Repositorio en GitHub · S
- Repo público creado con `gh`, primer push.
- `main` protegida: no se permite push directo; todo entra por PR, **sin exigir aprobaciones** (con una sola persona, GitHub no deja aprobar tu propio PR y quedarías bloqueado).

### T-03 API "hola mundo" de core · S
- `services/core` creado con `uv init`, FastAPI y `GET /health` → `{"status": "ok"}`.
- Un test con pytest que comprueba ese endpoint.
- Ruff sin errores.

### T-04 Primer Pull Request · S
- T-03 entra a `main` por un PR con mensaje en Conventional Commits.
- Tablero de GitHub Projects creado con las historias de la semana 2.

## Semana 2 · Capa 1: Base técnica

### T-05 Imagen Docker de core · M
- Dockerfile multi-stage, imagen base con versión fija, usuario no root.
- Se construye con contexto en la raíz del repo (para poder incluir `libs/` en la semana 3) y un `.dockerignore` (docs/06 D1.5).
- `docker run` de la imagen responde `GET /health`.

### T-06 Docker Compose con PostgreSQL · M
- `infra/compose.yaml` levanta core y PostgreSQL 18 con volumen persistente.
- PostgreSQL con `healthcheck`; core arranca solo cuando la base está *healthy*.
- core expone `GET /health/ready`, que responde 200 solo si puede consultar su base.
- Credenciales tomadas de `.env`; `.env.example` en el repo sin valores reales.

### T-07 Gateway con Caddy · M
- `/api/core/*` llega a core sin el prefijo (`root_path` configurado: `/api/core/docs` muestra la documentación).
- Caddy agrega `X-Request-ID` y limita el tamaño de las peticiones.
- En local funciona con `http://localhost` (el navegador lo trata como seguro). HTTPS real llega con staging en la semana 5 (T-14).

### T-08 Integración continua (CI) · M
- GitHub Actions en cada PR: Ruff (lint y formato) y pytest.
- Los tests de integración usan PostgreSQL real (Testcontainers o servicio de Actions).
- La protección de `main` exige la CI en verde para fusionar.

### T-09 Logs estructurados · S
- core escribe logs en JSON a la salida estándar, con el `X-Request-ID` de cada petición.
- Un test comprueba que los logs no contienen el token ni el cuerpo de la petición (docs/06 D1.7).

### T-10 Primera migración con Alembic · S
- Alembic configurado en core; una migración inicial vacía se aplica con un contenedor de un solo uso antes de levantar core (docs/06 D1.5).
- Dos usuarios de base: el dueño del esquema (`MIGRATION_DATABASE_URL`, solo para migraciones) y el de la aplicación con permisos mínimos (`DATABASE_URL`), con `ALTER DEFAULT PRIVILEGES` para las tablas futuras (docs/06 D1.6).

## Semana 3 · Capa 2: Auth

### HU-01 Iniciar sesión · M · UC-01 · RF-22
*Como usuario del sistema, quiero entrar con mi correo y contraseña, para usar las funciones de mi perfil.*
- Con credenciales correctas y usuario activo: recibo un access token (15 min) y la cookie de refresh.
- Con credenciales incorrectas: error 401 con un mensaje genérico que no revela si el correo existe.
- Tras 5 intentos fallidos seguidos, el usuario queda bloqueado 15 minutos.
- Un usuario desactivado no puede entrar.

### HU-02 Mantener la sesión abierta · M · UC-01 · RNF-02
*Como vendedor, quiero no tener que volver a escribir mi contraseña a cada rato, para atender rápido desde el celular.*
- El frontend renueva el access token antes de que venza; al recargar la página la sesión sigue.
- Cada renovación rota el refresh token.
- Si se usa un refresh token ya rotado, se cierran todas las sesiones de ese usuario.
- Después de 7 días sin uso, hay que volver a iniciar sesión.

### HU-03 Cerrar sesión · S · UC-01
*Como usuario, quiero cerrar sesión, para que nadie use mi cuenta en un equipo compartido.*
- Cerrar sesión revoca el refresh token y borra la cookie.

### HU-04 Gestionar usuarios y permisos · L · UC-02 · RF-22, RF-23
*Como dueño, quiero crear usuarios y asignarles perfiles o permisos, para que cada persona haga solo lo que le corresponde.*
- Crear, editar y desactivar usuarios; asignar uno o varios perfiles y permisos sueltos (docs/06 D2).
- Desactivar un usuario revoca sus sesiones.
- No se puede quitar `user.manage` al último administrador activo.
- Se puede desbloquear a un usuario bloqueado por intentos fallidos.
- Cada cambio queda en la auditoría de auth (quién, qué, cuándo, antes y después).
- Los 4 perfiles por defecto existen desde la primera migración.

### HU-05 Primer usuario administrador · S · UC-02
*Como desarrollador, quiero crear el primer usuario dueño con un comando, para poder entrar al sistema recién instalado.*
- Un comando crea el usuario con el perfil Dueño usando datos de variables de entorno (nunca en el código).
- Si ya existe un administrador, el comando no hace nada.

### HU-06 Pantalla de inicio de sesión · M · UC-01
*Como vendedor, quiero una pantalla de login que funcione bien en el celular, para entrar desde la calle.*
- Formulario usable en 360 px de ancho; muestra los errores de HU-01 en español.
- Tras entrar, muestra el nombre del usuario y un botón de cerrar sesión.

### T-11 Validación de JWT compartida · M · ADR-0007
- `libs/security` valida firma RS256, `iss`, `aud` y `exp` con la clave pública leída de archivo, y verifica permisos.
- core protege un endpoint de prueba: sin token → 401; token vencido, mal firmado o de otro `aud` → 401; sin permiso → 403; con permiso → 200. Un test por cada caso.

### T-12 auth en Compose y gateway · S
- auth con su propia base (`auth_db`) y su usuario de base; `/api/auth/*` enrutado por el gateway.
- Claves JWT generadas por un script, montadas como archivos y excluidas de git.

### T-13 Base del frontend · M
- `frontend/` creado con Vite + React + TypeScript + Tailwind; ESLint y Prettier.
- La CI también corre lint y build del frontend.
- Caddy sirve el build del frontend en `/`, en el mismo dominio que la API (docs/06 D1.2).
- En desarrollo, el servidor de Vite reenvía `/api` al gateway, así no hace falta CORS.

## Semana 4 · Capa 3: Catálogo
| Historia | Perfil | UC | Tamaño |
| --- | --- | --- | --- |
| HU-07 Gestionar productos, categorías, marcas, presentaciones con factor y stock mínimo por ubicación | Dueño | UC-04 | L |
| HU-08 Definir escalas de precio por presentación | Dueño | UC-04 | M |
| HU-09 Ver y editar el costo solo con `cost.view` | Dueño | UC-04 | S |
| HU-10 Importar productos desde Excel/CSV con reporte de errores por fila; la **plantilla se entrega al negocio esta semana** para que empiece a llenarla (N-04) | Dueño | UC-05 | M |
| HU-11 Gestionar ubicaciones (tienda o almacén) | Dueño | UC-06 | S |
| HU-12 Gestionar clientes (RUC/DNI, dirección, contacto) | Vendedor, Dueño | UC-07 | S |
| HU-13 Gestionar proveedores | Dueño | UC-08 | S |

## Semana 5 · Capa 4: Stock
| Historia | Perfil | UC | Tamaño |
| --- | --- | --- | --- |
| HU-14 Cargar el inventario inicial de una ubicación desde Excel (una sola vez) | Dueño | UC-09 | M |
| HU-15 Consultar stock disponible por ubicación con equivalencias y stock bajo | Vendedor, todos | UC-10 | M |
| HU-16 Registrar ingreso de mercadería | Dueño, Almacén | UC-11 | M |
| HU-17 Transferir entre ubicaciones | Almacén | UC-12 | M |
| HU-18 Proponer ajuste con motivo | Almacén | UC-13 | S |
| HU-19 Aprobar o rechazar ajustes | Dueño | UC-14 | S |
| HU-20 Consultar el kardex por producto y ubicación | Dueño, Almacén | UC-15 | S |
| T-14 Primer despliegue a staging en la nube (proveedor elegido) con CI/CD y HTTPS (sin HTTPS no funcionan las cookies de sesión) | — | — | L |

## Semana 6 · Capa 5: Pedidos
| Historia | Perfil | UC | Tamaño |
| --- | --- | --- | --- |
| HU-21 Crear pedido: reserva lo disponible, el resto queda por conseguir, idempotente | Vendedor | UC-16 | L |
| HU-22 Asignar faltantes automáticamente al entrar stock (FIFO por pedido) en ingresos, transferencias y ajustes; las devoluciones se conectan en HU-32 (semana 7) | Sistema | UC-11, UC-12, UC-14 | M |
| HU-23 Modificar pedido y cerrar faltantes | Vendedor, Dueño | UC-17 | M |
| HU-24 Anular pedido | Vendedor, Dueño | UC-18 | S |
| HU-25 Generar y compartir la nota de venta en PDF (A4) | Vendedor | UC-19 | M |
| HU-26 Registrar pagos y ver el estado de pago | Vendedor, Repartidor, Dueño | UC-20 | S |
| HU-27 Ver productos por conseguir | Dueño | UC-30 | S |

## Semana 7 · Capa 6: Despachos
| Historia | Perfil | UC | Tamaño |
| --- | --- | --- | --- |
| HU-28 Bandeja de pedidos pendientes y marcar en preparación | Almacén | UC-21 | S |
| HU-29 Despachar total o parcial con nº de comprobante, repartidor (lista desde auth) y cierre opcional del resto | Almacén | UC-22 | L |
| HU-30 Registrar pedidos y despachos hechos en papel durante una caída, en orden y antes de reanudar la operación normal | Almacén, Dueño | UC-23 | M |
| HU-31 Marcar despacho en camino | Repartidor | UC-24 | S |
| HU-32 Registrar entrega con rechazo total o parcial y cobro; lo rechazado vuelve al stock y asigna faltantes | Repartidor | UC-25 | M |

## Semana 8 · Capa 7: Producción
| Historia | Perfil | UC | Tamaño |
| --- | --- | --- | --- |
| HU-33 Ver stock actual y stock bajo por ubicación | Dueño | UC-26 | S |
| HU-34 Ver pedidos por estado | Dueño, Vendedor | UC-27 | S |
| HU-35 Ver histórico de ventas por día y producto (según lo entregado) | Dueño | UC-28 | M |
| HU-36 Exportar reportes a Excel y PDF; consultar la auditoría | Dueño | UC-29, UC-03 | M |
| T-15 Entorno de producción con HTTPS y dominio propio o subdominio | — | — | S |
| T-16 Backup continuo (WAL) y diario fuera del servidor | — | — | M |
| T-17 Prueba de restauración y runbook para levantar un servidor nuevo en menos de 1 h | — | — | M |
| T-18 Monitor externo con alertas al celular | — | — | S |
| T-19 Capacitación por perfil y plan de arranque (fecha, orden de carga, soporte presencial los primeros días) | — | — | M |

## Tareas del negocio (N)
Lo que depende del dueño y su equipo. Si una se atrasa, bloquea el calendario: se revisan en cada reunión semanal.

| Tarea | Responsable | Fecha límite | Bloquea |
| --- | --- | --- | --- |
| N-01 Validar y firmar el alcance del MVP (docs/01) | Dueño | 08/11 (semana 2) | Todo lo que sigue |
| N-02 Responder los pendientes de `docs/entrevista/resultados.md` | Dueño | 15/11 (semana 3) | Catálogo (semana 4) |
| N-03 Aprobar el costo mensual de servidor y dominio, y elegir el nombre del dominio | Dueño | 20/11 (semana 4) | Staging con HTTPS (T-14) |
| N-04 Llenar la plantilla de productos (presentaciones, precios por cantidad, mínimos por ubicación) | Dueño y vendedores | Empieza 23/11; completa al 15/12 | Carga real (21–31/12) |
| N-05 Probar el sistema en staging y dar comentarios cada semana (UAT) | Dueño | Desde la semana 5, cada semana | Ajustes antes de producción |
| N-06 Resolver el internet del almacén externo (datos móviles o router 4G) | Dueño | 15/12 | Uso del sistema en ese almacén |
| N-07 Conteo físico del inventario inicial, con cada ubicación cerrada (regla 16) | Dueño y equipo | Última semana de diciembre | Arranque en enero |
| N-08 Definir el día de arranque y estar disponible para la capacitación | Dueño | 19/12 | Arranque en enero |

Si una semana se atrasa, se recorta en este orden (ADR-0005): HU-33 a HU-36 (reportes), HU-17 (transferencias) y HU-26 (detalle de pagos).
