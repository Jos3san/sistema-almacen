# Glosario

Términos y siglas usados en la documentación del proyecto. Ordenados por tema.

## Términos del negocio
| Término | Significado en este sistema |
| --- | --- |
| Ubicación | Lugar que guarda stock: tienda o almacén (docs/03) |
| Unidad base | Unidad mínima en la que se guarda el stock de un producto (ej. un lapicero) |
| Presentación | Forma de venta de un producto (unidad, caja, docena, paquete) con su **factor** de conversión a la unidad base (caja de 12 → factor 12) |
| Escala de precio | Precio de una presentación según la cantidad comprada (ej. desde 12 unidades, otro precio) |
| Stock físico | Lo que hay realmente en la ubicación |
| Stock reservado | Parte del físico apartada para pedidos confirmados |
| Stock disponible | Físico − reservado: lo que se puede vender |
| Por conseguir | Cantidad pedida que no había al confirmar el pedido; se reserva sola cuando entra mercadería (FIFO) o se cierra si el cliente no espera |
| Kardex | Historial de todos los movimientos de stock de un producto en una ubicación; solo se agregan registros, nunca se modifican |
| Movimiento de stock | Cada entrada o salida: ingreso, salida, transferencia, ajuste o devolución |
| Ingreso | Entrada de mercadería comprada a un proveedor |
| Ajuste | Corrección de stock con motivo (merma, rotura, conteo, inventario inicial); lo aprueba el dueño |
| Inventario inicial | Conteo físico con el que cada ubicación arranca en el sistema, una sola vez |
| Transferencia | Paso de mercadería de una ubicación a otra |
| Pedido | Solicitud de un cliente registrada por un vendedor; reserva stock al confirmarse |
| Nota de venta | Documento interno numerado del pedido (no es comprobante de pago SUNAT) |
| Despacho | Salida física de mercadería de un pedido; puede ser total o parcial |
| Modalidad de entrega | Recojo en tienda, reparto propio o agencia |
| Rechazo | Parte de un despacho que el cliente no acepta al recibir; vuelve al stock y no se cobra |
| Comprobante | Boleta o factura emitida en el sistema de facturación externo; aquí solo se guarda su número |
| Merma | Pérdida de mercadería por daño, rotura o vencimiento |
| Yape | Aplicación de pagos móviles usada en Perú |

## Proceso y gestión
| Sigla / término | Significado |
| --- | --- |
| SDLC | *Software Development Life Cycle*: ciclo de vida del desarrollo de software (docs/00) |
| MVP | *Minimum Viable Product*: producto mínimo viable, lo que sale a producción en enero |
| ADR | *Architecture Decision Record*: registro de una decisión de arquitectura (docs/adr) |
| RF | Requerimiento funcional: lo que el sistema hace (docs/02) |
| RNF | Requerimiento no funcional: cómo debe comportarse (seguridad, rapidez, disponibilidad) |
| UC | *Use Case*: caso de uso (docs/05) |
| HU | Historia de usuario: "Como [perfil], quiero [acción], para [beneficio]" (docs/07) |
| T | Historia técnica del backlog (docs/07) |
| H | Hallazgo de una revisión (docs/05, docs/06) |
| D1–D7 | Partes del diseño técnico (docs/06) |
| A, B, C, R | Códigos del checklist semanal (docs/semanas) |
| N | Tarea que depende del negocio (dueño y su equipo), con fecha límite (docs/07) |
| DoR / DoD | *Definition of Ready / Definition of Done*: cuándo una historia puede empezar y cuándo está terminada |
| UAT | *User Acceptance Testing*: pruebas de aceptación con el usuario (el dueño, cada semana) |
| Backlog | Lista ordenada de todo el trabajo pendiente |
| Staging | Entorno de pruebas igual a producción, con datos ficticios |
| Trunk-based | Forma de trabajo con ramas cortas que se integran pronto a `main` |
| Conventional Commits | Formato de mensajes de commit (`feat:`, `fix:`, `docs:`…) |
| Runbook | Procedimiento escrito para operar o recuperar el sistema |

## Arquitectura y desarrollo
| Sigla / término | Significado |
| --- | --- |
| API | *Application Programming Interface*: la puerta por la que el frontend habla con el backend |
| SPA | *Single Page Application*: web que se carga una vez y se actualiza sin recargar (React) |
| C4 | Modelo de diagramas de arquitectura en 4 niveles: contexto, contenedores, componentes y código |
| ERD | *Entity-Relationship Diagram*: diagrama de tablas y sus relaciones |
| BD / DB | Base de datos (*database*) |
| ORM | *Object-Relational Mapping*: trabajar con tablas como objetos de Python (SQLAlchemy) |
| CRUD | *Create, Read, Update, Delete*: crear, leer, modificar y borrar |
| CQRS | *Command Query Responsibility Segregation*: separar escrituras y lecturas (después del MVP) |
| FIFO | *First In, First Out*: el primero en llegar es el primero en ser atendido |
| Microservicio | Aplicación pequeña e independiente con su propia base de datos (auth, core) |
| Monorepo | Un solo repositorio con todos los servicios y el frontend |
| Gateway | Puerta de entrada única del sistema (Caddy) |
| Outbox | Patrón para publicar eventos sin perderlos (ADR-0004, después del MVP) |
| Idempotencia | Repetir una operación da el mismo resultado; evita pedidos duplicados (`Idempotency-Key`) |
| Health check | Ruta (`/health`) que indica si un servicio está vivo y listo |
| OpenAPI | Formato estándar para documentar una API; FastAPI lo genera solo en `/docs` |
| SKU | *Stock Keeping Unit*: código interno único de un producto |
| JSON | *JavaScript Object Notation*: formato de texto para intercambiar datos |
| YAML / TOML | Formatos de archivos de configuración (Compose y GitHub Actions / proyectos Python) |
| CSV | *Comma-Separated Values*: archivo de texto con datos en columnas |
| PDF | *Portable Document Format*: formato de la nota de venta |
| A4 | Tamaño de hoja (21 × 29,7 cm) de la nota de venta |
| HTTP / GET / POST | Protocolo de la web y sus acciones para leer (GET) o enviar (POST) datos |
| CSS | *Cascading Style Sheets*: estilos visuales de la web (Tailwind) |
| VS Code | Visual Studio Code, el editor de código |

## Base de datos
| Sigla / término | Significado |
| --- | --- |
| SQL | Lenguaje para consultar y modificar bases de datos |
| ACID | Atomicidad, Consistencia, Aislamiento y Durabilidad: garantías de una transacción |
| Transacción | Grupo de operaciones que se guardan todas o ninguna (`BEGIN` … `COMMIT`, o `ROLLBACK` si algo falla) |
| `SELECT … FOR UPDATE` | Bloquea filas mientras dura la transacción para que dos pedidos no tomen el mismo stock |
| PK | *Primary Key*: clave primaria, identifica cada fila |
| `CHECK` / `UNIQUE` | Restricciones de la base: una condición que siempre debe cumplirse / un valor que no se puede repetir |
| `NUMERIC(12,2)` | Tipo exacto para montos (12 dígitos, 2 decimales); nunca `float` |
| `timestamptz` | Fecha y hora con zona horaria; se guarda en UTC |
| Migración | Script versionado que cambia la estructura de la base (Alembic) |
| Secuencia | Contador de PostgreSQL; **no** se usa para la numeración de documentos porque salta números si una transacción falla (docs/03 regla 12) |
| Deadlock | Bloqueo mutuo: dos operaciones esperan cada una a la otra; se evita bloqueando siempre en el mismo orden |

## Seguridad
| Sigla / término | Significado |
| --- | --- |
| JWT | *JSON Web Token*: pase firmado que prueba quién eres y qué permisos tienes |
| RS256 | Firma con clave privada (auth) y verificación con clave pública (cada servicio) |
| HS256 | Firma con una sola clave compartida; descartada (ADR-0007) |
| Access / refresh token | Pase corto (15 min) / pase para renovarlo (7 días, rotado) |
| HTTPS | HTTP cifrado (el candado del navegador); necesita un dominio |
| CORS | *Cross-Origin Resource Sharing*: regla del navegador sobre qué sitios pueden llamar a la API |
| RBAC | *Role-Based Access Control*: permisos agrupados en perfiles (docs/06 D2) |
| argon2 | Algoritmo para guardar contraseñas de forma segura (no es sigla) |
| SSH | *Secure Shell*: acceso remoto cifrado al servidor |
| UFW | *Uncomplicated Firewall*: cortafuegos de Ubuntu |

## DevOps e infraestructura
| Sigla / término | Significado |
| --- | --- |
| DevOps | Unir desarrollo (*Dev*) y operación (*Ops*) con automatización |
| CI / CD | Integración continua (tests automáticos en cada cambio) / despliegue continuo (publicación automática) |
| PR | *Pull Request*: propuesta de cambio que se revisa antes de entrar a `main` |
| Docker / Compose | Contenedores / herramienta para levantar varios contenedores juntos |
| VPS | *Virtual Private Server*: servidor virtual en la nube |
| AWS / Azure | Proveedores de nube de Amazon y Microsoft |
| vCPU / RAM / MB / GB | Procesador virtual / memoria / megabytes / gigabytes |
| IaC | *Infrastructure as Code*: infraestructura descrita en archivos (Terraform) |
| CLI | *Command Line Interface*: programa que se usa desde la terminal (ej. `gh`) |
| LTS | *Long Term Support*: versión con soporte extendido |
| WSL | *Windows Subsystem for Linux*: Linux dentro de Windows (lo usa Docker) |
| GHCR | *GitHub Container Registry*: donde se guardan las imágenes Docker |
| SemVer | Versionado semántico `MAYOR.MENOR.PARCHE` (ej. v1.2.3) |
| CRLF / LF | Fin de línea de Windows / de Linux; el repo usa LF |
| RPO | *Recovery Point Objective*: datos que se pueden perder como máximo (1 h) |
| RTO | *Recovery Time Objective*: tiempo máximo sin sistema (1 h) |
| WAL | *Write-Ahead Log*: registro de cada cambio de PostgreSQL; permite backups continuos |
| PITR | *Point-In-Time Recovery*: restaurar la base a un momento exacto |
| SLO | *Service Level Objective*: meta de disponibilidad o rapidez |
| UTC | Tiempo universal coordinado; se muestra convertido a hora de Lima |
| TI | Tecnologías de la información |
| PC | Computadora personal (de escritorio o laptop) |

## Perú
| Sigla | Significado |
| --- | --- |
| SUNAT | Superintendencia Nacional de Aduanas y de Administración Tributaria |
| RUC | Registro Único de Contribuyentes |
| DNI | Documento Nacional de Identidad |
| IGV | Impuesto General a las Ventas (18 %) |
| PEN | Código de la moneda: sol peruano |
