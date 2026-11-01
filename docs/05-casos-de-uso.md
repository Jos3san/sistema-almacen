# Casos de uso (MVP)

Fuente: `docs/01` (alcance y perfiles), `docs/02` (RF/RNF), `docs/03` (modelo y reglas), `docs/entrevista/resultados.md`.
Estado: **Paso 2**: catálogo validado y casos críticos detallados. Los demás casos se detallan al llegar a su semana del calendario.

## Actores
| Actor | Quién (entrevista) | Nota |
| --- | --- | --- |
| Dueño | El dueño | Perfil admin: todos los permisos |
| Vendedor | Vendedores | Tienda, calle, WhatsApp, teléfono (#27) |
| Almacén / despacho | Quien tenga el permiso | No hay almacenero dedicado (#3, #45) |
| Repartidor | Repartidores | Movilidad propia (#48); a menudo también es vendedor |

Los actores son **perfiles por defecto**: una persona puede tener varios y los permisos se configuran por usuario (#33). En cada caso de uso se indica el actor habitual; el sistema valida el permiso, no el nombre del perfil.

## Catálogo
| UC | Nombre | Actor principal | RF | Servicio |
| --- | --- | --- | --- | --- |
| **Acceso y administración** |||||
| UC-01 | Iniciar y cerrar sesión | Todos | RF-22 | auth |
| UC-02 | Gestionar usuarios, perfiles y permisos | Dueño | RF-22 | auth |
| UC-03 | Consultar auditoría | Dueño | RF-23 | core |
| **Catálogo** |||||
| UC-04 | Gestionar productos, categorías, marcas, presentaciones y escalas de precio | Dueño | RF-01, RF-02, RF-29, RF-30 | core |
| UC-05 | Importar productos desde Excel/CSV | Dueño | RF-04 | core |
| UC-06 | Gestionar ubicaciones | Dueño | RF-05 | core |
| UC-07 | Gestionar clientes | Vendedor, Dueño | RF-03 | core |
| UC-08 | Gestionar proveedores | Dueño | RF-03 | core |
| **Stock** |||||
| UC-09 | Cargar inventario inicial de una ubicación | Dueño | RF-32 | core |
| UC-10 | Consultar stock disponible | Vendedor, todos | RF-10, RF-11, RF-13 | core |
| UC-11 | Registrar ingreso de mercadería | Dueño, Almacén | RF-06, RF-42 | core |
| UC-12 | Transferir mercadería entre ubicaciones | Almacén | RF-07, RF-42 | core |
| UC-13 | Proponer ajuste de stock | Almacén | RF-08 | core |
| UC-14 | Aprobar o rechazar ajuste | Dueño | RF-08, RF-42 | core |
| UC-15 | Consultar kardex | Dueño, Almacén | RF-09 | core |
| **Pedidos** |||||
| UC-16 | Crear pedido (reserva lo disponible) | Vendedor | RF-12, RF-13, RF-14, RF-35, RF-37 | core |
| UC-17 | Modificar pedido o cerrar faltantes | Vendedor, Dueño | RF-16, RF-43 | core |
| UC-18 | Anular pedido | Vendedor, Dueño | RF-16 | core |
| UC-19 | Generar y enviar nota de venta (PDF) | Vendedor | RF-15 | core |
| UC-20 | Registrar pago | Vendedor, Repartidor, Dueño | RF-34, RF-35 | core |
| **Despachos y entregas** |||||
| UC-21 | Ver bandeja de pendientes y preparar pedido | Almacén | RF-17 | core |
| UC-22 | Despachar total o parcial | Almacén | RF-18, RF-20, RF-36, RF-37, RF-43 | core |
| UC-23 | Registrar pedidos y despachos hechos en papel (contingencia) | Almacén, Dueño | RF-39 | core |
| UC-24 | Marcar despacho en camino | Repartidor | RF-21 | core |
| UC-25 | Registrar entrega con rechazo total o parcial | Repartidor | RF-21, RF-38, RF-42 | core |
| **Reportes** |||||
| UC-26 | Ver stock actual por ubicación y stock bajo | Dueño | RF-24, RF-11 | core (módulo reportes) |
| UC-27 | Ver pedidos por estado | Dueño, Vendedor | RF-25 | core (módulo reportes) |
| UC-28 | Ver histórico de ventas por día y producto | Dueño | RF-26 | core (módulo reportes) |
| UC-29 | Exportar reportes a Excel o PDF | Dueño | RF-28 | core (módulo reportes) |
| UC-30 | Ver productos por conseguir | Dueño | RF-41 | core (módulo reportes) |

**Críticos** (RNF-10, #78, #86): UC-10 y UC-16 primero, luego UC-22 y UC-25. UC-09 es requisito para salir a producción. UC-11 entra aquí por la asignación de faltantes.

## Fuera del MVP
RF-19 nota de despacho separada · RF-27 más vendidos y sugerencia de compra · RF-31 paquetes/listas escolares · RF-33 alertas por WhatsApp/correo · RF-40 stock valorizado y ventas por vendedor.

## Hallazgos de la validación
| # | Hallazgo | Resolución |
| --- | --- | --- |
| H-1 | Pedido con faltante: #28 vs #80 | **Opción B (dueño)**: lo que falta queda por conseguir y se reserva al entrar stock, FIFO por pedido (docs/03 reglas 3–4, RF-41, RF-42, UC-30) |
| H-2 | EN_CAMINO con despachos parciales | Corregido: en camino / entregado son estados del **despacho**; el estado del pedido se deriva (docs/03) |
| H-3 | Plazo de pedidos separados | **Sin plazo si está pagado (dueño)**. Supuesto: un pedido sin pago tampoco vence solo; el dueño lo anula si quiere (docs/03 regla 10). Confirmar |
| H-4 | Quién marca en camino | **El repartidor (dueño)** |
| H-5 | Quién recibe mercadería | Por permisos: dueño y almacén |
| H-6 | Cobro contra entrega | **El repartidor registra el pago (dueño)**; a menudo también es vendedor |
| H-7 | El rechazo sumaba dos veces en la línea del pedido | Corregido: el rechazo **pasa** cantidad de despachada a anulada (docs/03 regla 8) |
| H-8 | Lo por conseguir varía: si el cliente no quiere esperar, se lleva solo lo que hay (aclaración 27/10) | Cerrar faltantes en UC-17 y al despachar en UC-22; ventas e importe según lo entregado (docs/03 reglas 17–19, RF-43) |
| H-9 | Si se cierran faltantes y la cantidad final baja de la escala de precio (ej. pidió 24 a precio de docena y se lleva 10), ¿se mantiene el precio pactado o se recalcula? | Propuesta: se mantiene el precio congelado (regla 6). **Confirmar con el dueño** |
| H-10 | Quien despacha podía cerrar faltantes, pero la regla 17 se lo daba al vendedor o al dueño | Permiso `order.close_shortage` (docs/06 D2) |
| H-11 | La contingencia solo preveía registrar despachos; los pedidos en papel y el orden de registro no estaban definidos | Al volver el sistema se registran primero pedidos y despachos en papel, en orden, antes de reanudar (docs/03 regla 14, RF-39) |
| H-12 | El stock mínimo era por producto, pero el stock bajo se mira por ubicación | Stock mínimo por producto **y ubicación** (tabla `stock`, RF-01, RF-11, RF-24) |
| H-13 | Las transferencias tenían un estado sin definir | Inmediatas en el MVP (salida y entrada en la misma transacción); "en tránsito" después (docs/03) |

---

## Detalle de casos críticos

Formato: **Actor · Precondición · Flujo principal · Alternos y errores · Reglas · Resultado**. "Reglas" remite a docs/03.

### UC-09 Cargar inventario inicial de una ubicación
- **Actor:** Dueño. **Precondición:** productos cargados (UC-05); la ubicación no tiene un inventario inicial aprobado.
- **Flujo principal**
  1. El dueño elige la ubicación y sube el Excel del conteo (SKU o código de barras, cantidad en unidad base).
  2. El sistema valida cada fila y muestra un resumen: filas válidas, errores y total de unidades.
  3. El dueño confirma.
  4. El sistema crea un ajuste INVENTARIO_INICIAL aprobado y, en una sola transacción, registra un movimiento AJUSTE por producto y actualiza `stock`.
- **Alternos y errores**
  - 2a. SKU inexistente, cantidad negativa o no numérica, producto repetido: la fila se marca con error y el resto se puede confirmar o corregir.
  - 3a. La ubicación ya tiene un inventario inicial: se rechaza; las diferencias posteriores se corrigen con ajustes (UC-13).
- **Reglas:** 1, 13, 16. **Resultado:** la ubicación tiene stock y kardex desde cero.

### UC-10 Consultar stock disponible
- **Actor:** Vendedor (cualquier usuario con sesión). **Precondición:** sesión iniciada.
- **Flujo principal**
  1. El usuario busca por nombre, SKU o código de barras (escáner con la cámara del celular: después del MVP).
  2. El sistema muestra, por ubicación: físico, reservado, disponible, presentaciones con su equivalencia (ej. 3 cajas + 5 unidades) y precios por escala.
  3. Si el disponible está bajo el stock mínimo, lo marca.
- **Alternos y errores:** 1a. Sin resultados: mensaje claro. El costo solo aparece con `cost.view`.
- **Reglas:** 2, 15. RNF-06: respuesta < 1 s. **Resultado:** solo lectura.

### UC-11 Registrar ingreso de mercadería
- **Actor:** Dueño o Almacén. **Precondición:** proveedor y productos existen.
- **Flujo principal**
  1. Elige ubicación y proveedor, e ingresa el nº de factura o guía.
  2. Agrega líneas: producto, presentación y cantidad.
  3. Confirma. En una transacción el sistema registra INGRESO por línea (cantidad × factor), suma al físico y **asigna faltantes**: reserva para las líneas por conseguir de esa ubicación, del pedido más antiguo al más nuevo.
  4. Muestra cuántas unidades quedaron reservadas para qué pedidos.
- **Alternos y errores:** 3a. Llegó menos o distinto de lo pedido al proveedor: se registra lo que llegó; el reclamo al proveedor queda fuera del sistema (#22).
- **Reglas:** 1, 4, 5, 11. **Resultado:** stock aumentado y pedidos con faltante avanzan.

### UC-16 Crear pedido
- **Actor:** Vendedor. **Precondición:** sesión iniciada; el cliente existe o se crea en el momento (UC-07).
- **Flujo principal**
  1. Elige cliente, ubicación de despacho y modalidad (recojo, reparto, agencia).
  2. Agrega líneas: producto, presentación y cantidad. Por cada línea el sistema muestra el precio según la escala, el disponible y cuánto quedaría por conseguir.
  3. Revisa el total y confirma.
  4. En una transacción (bloqueo `FOR UPDATE` por producto, en orden), el sistema reserva lo disponible por línea, deja el resto por conseguir, congela precio y factor, asigna el número correlativo y registra la auditoría.
  5. Muestra el pedido PENDIENTE con su número y lo que falta conseguir; ofrece la nota de venta (UC-19) y registrar un adelanto (UC-20).
- **Alternos y errores**
  - 2a. Producto inactivo o sin precio: no se puede agregar.
  - 2b. El cliente no quiere esperar lo que falta: el vendedor baja la cantidad a lo disponible, y la línea queda sin faltante.
  - 4a. Entre el paso 2 y el 4 otro pedido tomó el stock: la reserva usa el disponible real del momento del paso 4 y el resultado lo muestra (no falla).
  - 4b. Error de conexión o de servidor: no se crea nada (transacción completa o nada); el vendedor reintenta. Si el pedido sí se guardó y solo se perdió la respuesta, el reintento devuelve el mismo pedido gracias a la `Idempotency-Key` (docs/06): nunca se duplica.
- **Reglas:** 2, 3, 5, 6, 11, 12. **Resultado:** pedido creado; stock reservado; faltantes registrados para UC-30.

### UC-22 Despachar total o parcial
- **Actor:** Almacén. **Precondición:** pedido PENDIENTE, EN_PREPARACION o DESPACHADO_PARCIAL con cantidad reservada > 0.
- **Flujo principal**
  1. Desde la bandeja (UC-21) abre el pedido; ve por línea lo reservado y lo por conseguir.
  2. Indica las cantidades a despachar (por defecto, todo lo reservado), el repartidor si es reparto, y el tipo y nº de boleta/factura emitido en el sistema externo.
  3. Confirma. En una transacción: crea el despacho con número correlativo, registra SALIDA por línea, baja físico y reservado, y suma a `cantidad_despachada`.
  4. El despacho queda DESPACHADO; el pedido recalcula su estado.
- **Alternos y errores**
  - 2a. Cantidad mayor a lo reservado: no se permite.
  - 2b. El comprobante aún no se emitió: se puede guardar vacío y completar después (#49: "no siempre").
  - 2c. El cliente se lleva solo lo que hay: se marca "cerrar el resto" y lo por conseguir de esas líneas pasa a anulado en la misma transacción (regla 17). Requiere el permiso `order.close_shortage` (docs/06, H-10).
  - 4a. Modalidad recojo: el cliente se lleva todo en el momento y el despacho pasa directo a ENTREGADO.
- **Reglas:** 7, 11, 12, 17, 18. **Resultado:** stock físico descontado; despacho listo para salir.

### UC-25 Registrar entrega con rechazo
- **Actor:** Repartidor. **Precondición:** despacho EN_CAMINO (UC-24).
- **Flujo principal**
  1. Abre el despacho desde el celular y marca "entregado".
  2. Si el cliente rechaza algo, indica la cantidad rechazada por línea (por defecto 0: acepta todo, #52).
  3. Si se cobra al entregar, registra el pago (UC-20).
  4. Confirma. En una transacción: el despacho pasa a ENTREGADO; por cada rechazo se registra DEVOLUCION a la ubicación de origen, la cantidad pasa de despachada a anulada en la línea, y se asignan faltantes con esa mercadería (regla 4).
  5. El pedido recalcula su estado, su total y su estado de pago.
- **Alternos y errores:** 2a. Rechazo mayor a lo despachado en ese despacho: no se permite.
- **Reglas:** 4, 6, 8, 10, 18. **Resultado:** entrega registrada; lo rechazado vuelve al stock y no se cobra; la venta queda registrada por lo entregado.
