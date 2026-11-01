# Requerimientos

Actualizados con la entrevista del 27/10/2026. Prioridad: **MVP** (diciembre 2026) o **Luego**.

## Funcionales

### Catálogo
| Código | Requerimiento | Prioridad |
| --- | --- | --- |
| RF-01 | Productos: SKU, código de barras (opcional), nombre, categoría, marca, unidad base, costo (solo dueño), activo; stock mínimo por ubicación. | MVP |
| RF-02 | Categorías y marcas. | MVP |
| RF-03 | Clientes (RUC/DNI, dirección, contacto) y proveedores. | MVP |
| RF-04 | Importación masiva de productos desde Excel/CSV. | MVP |
| RF-29 | Presentaciones por producto (unidad, caja, docena, paquete) con factor de conversión a la unidad base. | MVP |
| RF-30 | Precios por presentación y por escala de cantidad. Precio incluye IGV. | MVP |
| RF-31 | Paquetes / listas escolares armadas. | Luego |

### Stock
| Código | Requerimiento | Prioridad |
| --- | --- | --- |
| RF-05 | Varias ubicaciones de stock (tipo tienda o almacén). | MVP |
| RF-06 | Ingreso de mercadería con nº de factura/guía del proveedor. | MVP |
| RF-07 | Transferencias entre ubicaciones. | MVP |
| RF-08 | Ajustes con motivo (merma, rotura, conteo); los aprueba el dueño. | MVP |
| RF-09 | Kardex por producto y ubicación. | MVP |
| RF-10 | Stock físico, reservado y disponible. | MVP |
| RF-11 | Indicador de stock bajo en pantalla, según el mínimo de cada producto en cada ubicación. | MVP |
| RF-32 | Carga inicial de stock por ubicación desde Excel (conteo físico), una sola vez por ubicación; queda como movimiento de inventario inicial. | MVP |
| RF-33 | Alertas de stock mínimo al dueño (WhatsApp/correo). | Luego |

### Pedidos y nota de venta
| Código | Requerimiento | Prioridad |
| --- | --- | --- |
| RF-12 | El vendedor crea pedido: cliente, ubicación, productos, presentación, cantidad; precio calculado según escala. | MVP |
| RF-13 | Al crear el pedido se muestra al instante el stock disponible y cuánto quedará por conseguir en cada línea. | MVP |
| RF-14 | Al confirmar el pedido se reserva lo disponible (sin aprobación); el resto queda por conseguir. | MVP |
| RF-15 | Nota de venta correlativa en PDF A4 (logo, RUC, cliente, productos), para imprimir o enviar por WhatsApp. | MVP |
| RF-16 | Modificar o anular pedido (vendedor o dueño) hasta antes de la entrega; libera la reserva. | MVP |
| RF-34 | Estado de pago (pendiente, adelanto, pagado) y medio (efectivo, Yape, transferencia). | MVP |
| RF-35 | Pedidos separados con pago adelantado para recoger después. | MVP |
| RF-43 | Cerrar lo por conseguir (todo o por línea) cuando el cliente no quiere esperar, también al momento de despachar. | MVP |

### Despachos y entregas
| Código | Requerimiento | Prioridad |
| --- | --- | --- |
| RF-17 | Bandeja de pedidos pendientes por preparar. | MVP |
| RF-18 | Despacho total o parcial. | MVP |
| RF-20 | Al despachar se descuenta físico y reserva. | MVP |
| RF-36 | Registrar nº de boleta/factura del sistema externo en el despacho. | MVP |
| RF-37 | Modalidad: recojo en tienda, reparto propio o agencia. | MVP |
| RF-21 | Marcar en camino y entregado. | MVP |
| RF-38 | Rechazo total o parcial en la entrega; lo rechazado vuelve al stock. | MVP |
| RF-39 | Registro posterior de pedidos y despachos hechos en papel durante una caída, marcados como registrados tarde con su fecha real. | MVP |
| RF-41 | Lista de productos por conseguir (faltantes de pedidos) por ubicación, para decidir compras. | MVP |
| RF-42 | Al entrar stock, reservar automáticamente para los faltantes del pedido más antiguo al más nuevo. | MVP |
| RF-19 | Nota de despacho en PDF separada. | Luego |

### Usuarios y seguridad
| Código | Requerimiento | Prioridad |
| --- | --- | --- |
| RF-22 | Login, perfiles y permisos configurables por usuario. | MVP |
| RF-23 | Auditoría de acciones (quién, qué, cuándo, antes/después). | MVP |

### Reportes
| Código | Requerimiento | Prioridad |
| --- | --- | --- |
| RF-24 | Stock actual por ubicación y stock bajo según el mínimo de cada ubicación. | MVP |
| RF-25 | Pedidos por estado. | MVP |
| RF-26 | Histórico de ventas por día y producto, calculado con lo entregado (no con lo pedido). | MVP |
| RF-28 | Exportar a Excel y PDF. | MVP |
| RF-27 | Más vendidos, estimado de faltantes, sugerencia de compra. | Luego |
| RF-40 | Stock valorizado y ventas por vendedor. | Luego |

## No funcionales
| Código | Requerimiento |
| --- | --- |
| RNF-01 | Web responsive: PC, laptop, Android, iPhone. |
| RNF-02 | HTTPS; hash bcrypt/argon2; JWT corto + refresh token. |
| RNF-03 | Ninguna operación deja stock negativo, incluso con concurrencia. |
| RNF-04 | **RPO ≤ 1 h**: backup continuo de PostgreSQL (WAL/PITR) + respaldo diario fuera del servidor; prueba de restauración mensual. |
| RNF-05 | Movimientos de stock inmutables. |
| RNF-06 | Respuesta < 1 s al crear pedido y consultar stock, con el volumen de campaña (unas 4 veces el normal). |
| RNF-07 | Todo levanta con Docker Compose. |
| RNF-08 | API documentada (OpenAPI) y tests de reglas de negocio. |
| RNF-09 | Interfaz en español, PEN, America/Lima. |
| RNF-10 | Prioridad de disponibilidad: 1) tomar pedidos y consultar stock, 2) despachar. La caída de servicios periféricos no afecta pedidos. |
| RNF-11 | **RTO ≤ 1 h** en el horario comercial del negocio. Mantenimientos de madrugada. |
| RNF-12 | Requiere conexión a internet (sin modo offline en v1). |
| RNF-13 | Despliegue en la nube; costo mensual mínimo. |
| RNF-14 | Costos visibles solo con permiso del dueño. |
