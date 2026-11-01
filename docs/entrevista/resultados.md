# Resultados de la entrevista (27/10/2026)

**Versión pública anonimizada.** Las cifras y respuestas reales están en la entrevista respondida (`Guia_Entrevista_Sistema_Almacen.xlsx`), que es privada y no está en el repositorio. Los números de pregunta (#xx) se refieren a ese archivo.

Fuente: entrevista de 93 preguntas + aclaraciones posteriores. Documentos recibidos: 0 de 11.

## Datos del negocio (generalizados)
| Tema | Dato |
| --- | --- |
| Rubro | Librería y bazar; clientes variados (público, colegios, empresas) |
| Ubicaciones de stock | Varias: tiendas físicas (cada una con su almacén) y almacenes externos |
| Personas | Equipo pequeño: dueño, vendedores y repartidores. No hay almacenero dedicado: las personas cumplen varios roles |
| Usuarios del sistema | Pocos al inicio, con crecimiento previsto |
| Productos | Unos cientos; la mayoría con código de barras del fabricante |
| Pedidos por día | Decenas en temporada normal y unas 4 veces más en campaña escolar (ene–mar); picos en día del logro, día de la madre, primavera y navidad |
| Control actual | Ninguno: sin inventario, sin Excel, todo a mano o de memoria |
| Problema principal | No tener control de stock; con frecuencia venden lo que no hay o no encuentran lo que sí hay |
| Horario | Horario comercial; mantenimiento de madrugada |
| Soporte | El desarrollador |

## Decisiones que salen de la entrevista
- **Sin aprobación de pedidos**: el pedido reserva lo disponible al confirmarse.
- **Pedido con faltante (H-1)**: lo que no hay queda "por conseguir" y se reserva automáticamente cuando entra mercadería, del pedido más antiguo al más nuevo.
- **Lo por conseguir es variable (H-8)**: si el cliente no quiere esperar, se lleva solo lo que hay y el resto se cierra. Al final solo se registra como venta lo entregado.
- **Sin plazo de reserva (H-3)** para pedidos pagados.
- **El repartidor (H-4, H-6)** marca en camino y entregado, y registra el pago al entregar. A menudo el repartidor también es vendedor.
- **Estados visibles**: pendiente, en preparación, en camino, entregado (+ anulado).
- **Despacho parcial** según acuerdo con el cliente.
- **Rechazo parcial en la entrega**: lo no aceptado vuelve al stock.
- **Presentaciones** (unidad, caja, docena, paquete) y **precios por cantidad**. Precio incluye IGV y no se desglosa.
- **Permisos configurables** por usuario; los vendedores pueden ver pedidos de otros.
- Precio: solo el dueño. Anular pedido: vendedor o dueño, hasta antes de la entrega. Almacén no anula. Costo confidencial (solo dueño). Ajustes los aprueba el dueño.
- **Auditoría desde el inicio.**
- Pedidos separados con **pago adelantado**; cobro al pedir o al entregar; efectivo, Yape, transferencia.
- Nota de venta A4/PDF por WhatsApp, numeración lineal, con logo, RUC, cliente y productos. Guardar el **nº de boleta/factura** emitido en el sistema externo (se emite al despachar).
- Mermas y dañados: se rematan (ajuste con motivo).
- **Catálogo y precios solo en este sistema** (fuente de verdad); en facturación se digitan a mano.
- **Hoy no existe registro de stock**: ese es el motivo principal del sistema. Tras la carga inicial por ubicación, el stock solo cambia por movimientos (pedidos, despachos, ingresos, transferencias, ajustes, devoluciones).
- Lotes, variantes formales, costo/stock valorizado, comisiones, crédito, constancia de entrega: **fuera de v1**.
- Nube; sin dominio por ahora.

## Disponibilidad y continuidad
- Lo más crítico es **tomar pedidos y consultar stock**. El despacho puede hacerse manual y registrarse después.
- Stock confirmado al instante; se asume **conexión permanente** (sin modo offline en v1).
- Tiempo máximo caído: **1 hora** (RTO). Pérdida máxima de datos: **1 hora** (RPO).
- Plan de contingencia del negocio: papel.

## Calendario
- Sistema listo para producción: **diciembre 2026**.
- Carga de datos real (la hacen ellos) e inventario inicial: **última semana de diciembre**.
- Uso en producción: **enero 2027** (campaña escolar).
- Pruebas semanales: el dueño. Desarrollo y pruebas con un subconjunto de productos de prueba.

## Riesgos
1. Plazo corto (~8 semanas) con un desarrollador que aprende programación y DevOps a la vez → MVP estricto.
2. Salida en producción en la temporada más fuerte.
3. Carga de datos e inventario inicial dependen del negocio y se hacen en una semana.
4. El almacén externo no tiene internet: hay que resolver la conectividad (datos móviles / router 4G) antes de enero.
5. El despacho manual en contingencia debe registrarse después, o el stock se descuadra.

## Pendiente de aclarar
- ~~#56~~ Resuelto: productos y precios se mantienen **solo en este sistema** (fuente de verdad). En el sistema de facturación se ingresan a mano al emitir el comprobante.
- H-9: si al cerrar faltantes la cantidad final baja de la escala de precio, ¿se mantiene el precio pactado? (propuesta: sí). Confirmar.
- Supuesto H-3: un pedido separado **sin pago** tampoco vence solo; lo anula el dueño. Confirmar.
- Supuesto: cada tienda guarda su propio stock (cada tienda es una ubicación con stock). Confirmar.
- Conectividad del almacén externo.
- Información del sistema de facturación (nombre, si exporta Excel/CSV).
