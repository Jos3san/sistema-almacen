# Modelo de datos y reglas de negocio

El centro del modelo es `movimiento_stock`: el stock se calcula a partir de los movimientos. La tabla `stock` es un saldo cacheado que se actualiza en la misma transacción. Todo el stock y todas las cantidades de control se guardan en la **unidad base** del producto.

## Entidades
| Entidad | Campos principales | Notas |
| --- | --- | --- |
| usuario | id, nombre, email, password_hash, activo | Servicio Auth |
| perfil / permiso / usuario_perfil | código de permiso (p. ej. `order.cancel`, `price.edit`, `cost.view`) | Permisos configurables; un usuario puede tener varios perfiles |
| categoria | id, nombre | |
| producto | id, sku, codigo_barras (nullable), nombre, categoria_id, marca, unidad_base, costo, activo | `costo` solo visible con `cost.view` |
| presentacion | id, producto_id, nombre (UNIDAD, CAJA, DOCENA…), factor (cantidad en unidad base), codigo_barras | Ej.: caja de 12 → factor 12 |
| precio_escala | presentacion_id, cantidad_desde, precio | Precio con IGV; se toma la escala mayor que aplica |
| ubicacion | id, nombre, tipo (TIENDA, ALMACEN), direccion, activo | Tiendas y almacenes |
| stock | producto_id, ubicacion_id, fisico, reservado, stock_minimo | PK compuesta; disponible = físico − reservado; `stock_minimo` por ubicación (vacío = sin alerta) |
| movimiento_stock | id, fecha, tipo, producto_id, ubicacion_id, cantidad (+/−), saldo_resultante, documento_tipo, documento_id, usuario_id | Kardex; solo inserciones |
| proveedor | id, ruc, razon_social, contacto | |
| ingreso / ingreso_detalle | proveedor_id, ubicacion_id, fecha, nro_documento · producto_id, presentacion_id, cantidad | Genera INGRESO |
| transferencia / transferencia_detalle | origen_id, destino_id, fecha, usuario_id · producto_id, cantidad | **Inmediata** en el MVP: TRANSFERENCIA_SALIDA y TRANSFERENCIA_ENTRADA en la misma transacción; solo se transfiere lo disponible del origen. "En tránsito" queda para después |
| ajuste / ajuste_detalle | ubicacion_id, motivo (MERMA, ROTURA, CONTEO, INVENTARIO_INICIAL), estado, solicitado_por, aprobado_por | Genera AJUSTE |
| cliente | id, tipo_doc, nro_doc, nombre, direccion, telefono | |
| pedido | id, numero, idempotency_key (UNIQUE), cliente_id, vendedor_id, vendedor_nombre, ubicacion_id, estado, modalidad_entrega (RECOJO, REPARTO, AGENCIA), estado_pago, total, fecha, observaciones | `estado` y `estado_pago` se recalculan en cada operación; `vendedor_*` se copia del token (docs/06) |
| pedido_detalle | pedido_id, producto_id, presentacion_id, cantidad, factor, precio_unitario, cantidad_base, cantidad_reservada, cantidad_despachada, cantidad_anulada | Precio y factor congelados; cantidades de control en unidad base |
| pago | pedido_id, fecha, monto, medio (EFECTIVO, YAPE, TRANSFERENCIA), registrado_por | |
| despacho / despacho_detalle | pedido_id, numero, fecha, estado, preparado_por, repartidor_id, repartidor_nombre, comprobante_tipo, comprobante_numero, registrado_tarde · pedido_detalle_id, cantidad, cantidad_rechazada | Genera SALIDA; el rechazo genera DEVOLUCION |
| outbox_event | id, tipo, payload, creado_en, publicado_en | Patrón outbox (después del MVP) |
| auditoria | usuario_id, accion, entidad, entidad_id, datos_antes, datos_despues, fecha | Desde el MVP |

Montos en `NUMERIC(12,2)`. Tipos de movimiento: INGRESO, SALIDA, TRANSFERENCIA_SALIDA, TRANSFERENCIA_ENTRADA, AJUSTE, DEVOLUCION.

### Cantidades enteras
Todas las cantidades son **enteras** en la unidad base. Un producto que se vende por longitud o peso (ej. cinta por metro) usa una unidad base pequeña (centímetro, gramo) y presentaciones con factor (metro = 100). Así se evitan decimales y errores de redondeo en el stock.

### Cantidades de una línea de pedido (unidad base)
```
cantidad_base = cantidad × factor
por_conseguir = cantidad_base − cantidad_reservada − cantidad_despachada − cantidad_anulada
```
Invariante: `cantidad_reservada + cantidad_despachada + cantidad_anulada ≤ cantidad_base`, todas ≥ 0 (CHECK en BD).

## Estados del despacho
```
DESPACHADO ──► EN_CAMINO ──► ENTREGADO        (REPARTO, AGENCIA)
DESPACHADO ──────────────► ENTREGADO          (RECOJO en tienda)
```
- El repartidor marca EN_CAMINO y ENTREGADO.

## Estados del pedido (derivados de líneas y despachos)
```
PENDIENTE ──► EN_PREPARACION ──► DESPACHADO_PARCIAL ──► DESPACHADO ──► EN_CAMINO ──► ENTREGADO
    │               │
    └───────────────┴──► ANULADO (solo si no se despachó nada)
```
| Estado | Condición |
| --- | --- |
| PENDIENTE | Confirmado; nada despachado. Puede tener líneas con faltante (por conseguir) |
| EN_PREPARACION | Alguien inició la preparación (UC-21); nada despachado |
| DESPACHADO_PARCIAL | Algo despachado y queda saldo (reservado o por conseguir) |
| DESPACHADO | Existe al menos un despacho y ninguna línea tiene reservado ni por conseguir; algún despacho aún no sale |
| EN_CAMINO | Igual que DESPACHADO y al menos un despacho EN_CAMINO |
| ENTREGADO | Igual que DESPACHADO y todos los despachos ENTREGADO |
| ANULADO | Sin ningún despacho y todo el pedido anulado o con sus faltantes cerrados |

En la lista de pedidos, un DESPACHADO_PARCIAL con un despacho en camino muestra también la etiqueta "en camino".

## Reglas
1. El stock no se edita; los errores se corrigen con otro movimiento.
2. Físico, reservado y disponible; se vende contra el disponible.
3. **Pedido con faltante:** al confirmar, cada línea reserva lo disponible en la ubicación del pedido y el resto queda **por conseguir** (sin reserva). El pedido se crea igual y el sistema muestra qué falta y cuánto.
4. **Asignación de faltantes:** cuando entra stock a una ubicación (INGRESO, TRANSFERENCIA_ENTRADA, AJUSTE positivo, DEVOLUCION), en la misma transacción se reserva para las líneas por conseguir de esa ubicación, **del pedido más antiguo al más nuevo**.
5. Cantidad en unidad base = cantidad × factor de la presentación.
6. Precio: se elige la escala con mayor `cantidad_desde` ≤ cantidad pedida; queda congelado en el pedido. Importe de línea = precio_unitario × (cantidad_base − cantidad_anulada) / factor, redondeado a 2 decimales.
7. Solo se despacha lo reservado. Despachar baja físico y reservado y registra SALIDA por línea.
8. Rechazo en la entrega: se registra en el despacho; genera DEVOLUCION a la ubicación de origen y en la línea **pasa** la cantidad de `cantidad_despachada` a `cantidad_anulada` (resta de una y suma a la otra, para mantener la invariante). Lo rechazado no se vuelve a despachar ni se cobra.
9. Anulación (vendedor o dueño, antes de ENTREGADO): anula el saldo no despachado de cada línea (libera la reserva y cancela lo por conseguir). Lo ya despachado solo vuelve por rechazo.
10. Pagos: `estado_pago` = PENDIENTE (sin pagos), ADELANTO (pagado < total) o PAGADO (pagado ≥ total). Si un rechazo o anulación baja el total por debajo de lo pagado, el pedido muestra el saldo a favor del cliente. Un pedido no tiene plazo de reserva. Si queda sin pago, el dueño decide anularlo (supuesto: sin vencimiento automático en el MVP).
11. Concurrencia: transacción con `SELECT ... FOR UPDATE` y CHECK (fisico >= 0 AND reservado >= 0 AND reservado <= fisico). **Orden único de bloqueo** en todas las operaciones, para evitar bloqueos mutuos (*deadlocks*): primero las filas de `stock` (por producto_id y luego ubicacion_id), después las líneas de pedido (del pedido más antiguo al más nuevo). Si aun así PostgreSQL detecta un deadlock, la operación se reintenta una vez de forma automática.
12. **Numeración sin saltos** (#60: "debería ser lineal"): pedidos, notas y despachos toman su número de una tabla contador por tipo de documento, bloqueada y actualizada **dentro de la misma transacción**. Si la operación falla, el número no se consume. No se usan secuencias de PostgreSQL para esto porque saltan números cuando una transacción se deshace. Un número anulado no se reutiliza.
13. Ajustes: cualquiera con permiso propone, el dueño aprueba.
14. **Contingencia (caída del sistema):** al volver el sistema, primero se registran los pedidos y despachos hechos en papel, en el orden en que ocurrieron, y recién después se reanuda la operación normal; así lo que ya salió físicamente no compite con pedidos nuevos por el mismo stock. Quedan marcados con `registrado_tarde` y la fecha real. Si al registrar un despacho tardío el stock no alcanza (por un error en papel), se registra igual y la diferencia se corrige con un ajuste aprobado por el dueño.
15. Costos solo visibles con el permiso `cost.view`.
16. Carga inicial: cada ubicación arranca con un ajuste INVENTARIO_INICIAL (importado del conteo físico) aprobado por el dueño. El conteo se hace **con la ubicación cerrada** (después del cierre o antes de abrir) y se carga antes de volver a vender; si hubo ventas entre el conteo y la carga, se registran después como en la contingencia (regla 14). Desde ahí el stock solo cambia por movimientos; nunca se vuelve a "cargar" encima.
17. **Cerrar faltantes (el cliente no espera):** quien tenga el permiso `order.close_shortage` (por defecto vendedor y dueño) puede cerrar lo por conseguir de una o todas las líneas en cualquier momento antes de ENTREGADO; esa cantidad pasa a `cantidad_anulada`. También se puede hacer al despachar ("despachar lo que hay y cerrar el resto"). Lo por conseguir es variable: se puede aumentar, reducir o cerrar modificando el pedido.
18. **Lo que cuenta es lo entregado:** el importe del pedido, los pagos esperados, las ventas (RF-26) y lo que se registra como vendido se calculan con lo despachado y no rechazado (`cantidad_despachada`), no con lo pedido. Mientras el pedido está abierto, el total mostrado es el estimado (pedido − anulado, regla 6); al cerrarse ambos coinciden, porque ya no queda reservado ni por conseguir.
19. **Nota de venta:** conserva su número; al reimprimirla muestra las cantidades vigentes (las cerradas o rechazadas ya no se cobran).
