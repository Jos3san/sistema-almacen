# Resumen y alcance

Aplicación web a medida para que una librería y bazar gestione su stock en varias ubicaciones (tiendas y almacenes), los pedidos de sus vendedores y los despachos, hasta la emisión de la nota de venta.

Validado con la entrevista del 27/10/2026 (`docs/entrevista/resultados.md`).

## Objetivos
- Saber en todo momento cuánto stock hay, en qué ubicación y por qué cambió (hoy no hay ningún control).
- Que los vendedores registren pedidos viendo el stock real, sin prometer como disponible lo que no hay: lo que falta queda visible como "por conseguir".
- Que el dueño vea pedidos pendientes, despachos, stock bajo, lo que falta conseguir e histórico de ventas.

## Criterios de éxito
- Cero pedidos con stock prometido que no existe (todo faltante queda registrado como "por conseguir").
- Inventario cuadrado contra el conteo físico.
- Despachos en menos de 24 h.

## Calendario
| Hito | Fecha |
| --- | --- |
| MVP listo para producción | Diciembre 2026 (≈ 19/12) |
| Carga de datos e inventario inicial (la hace el negocio) | Última semana de diciembre |
| Uso en producción | Enero 2027 (campaña escolar) |

Las tareas que dependen del negocio, con sus fechas límite, están en docs/07 (N-01 a N-08).

## Incluye (MVP)
- Productos con presentaciones (unidad, caja, docena…) y precios por cantidad; categorías; ubicaciones; clientes; proveedores.
- Importación de productos desde Excel/CSV.
- Ingresos de mercadería, ajustes (aprobados por el dueño), transferencias entre ubicaciones y kardex.
- Pedidos con nota de venta en PDF (A4), reserva de lo disponible al confirmar, faltantes "por conseguir" que se reservan al llegar mercadería, y estado de pago.
- Despachos totales y parciales, entrega con rechazo parcial (vuelve al stock).
- Usuarios con permisos configurables y auditoría.
- Reporte de stock actual, stock bajo, productos por conseguir e histórico de ventas, exportable a Excel/PDF.

## Después del MVP
- Notificaciones (WhatsApp/correo, alertas de stock mínimo), bot.
- Sugerencia de compras, stock valorizado y costos.
- Integración con el sistema de facturación.
- Tienda online, más locales, contabilidad.

## No incluye
- Facturación electrónica (boletas y facturas SUNAT): la maneja un sistema externo. Solo se guarda el número del comprobante emitido. La nota de venta es un documento interno.
- Crédito y cobranzas, comisiones, control por lotes, modo sin conexión.

## Flujo principal
Vendedor crea pedido → al confirmarlo se reserva lo disponible y el resto queda por conseguir (se reserva solo cuando llega mercadería) → se prepara → despacho total o parcial (descuenta stock; se registra nº de boleta/factura) → en camino → entregado (lo rechazado vuelve al stock).

## Perfiles iniciales
Los permisos son configurables por usuario; estos son los perfiles por defecto. Una misma persona puede tener varios. El detalle exacto de permisos por perfil está en docs/06 (D2).

| Perfil | Quién | Puede | No puede |
| --- | --- | --- | --- |
| Dueño (admin) | Dueño | Todo: usuarios y permisos, precios, costos, aprobar ajustes, anular, reportes | — |
| Vendedor | Vendedores | Crear clientes y pedidos, ver stock, ver todos los pedidos, modificar y anular antes de la entrega, registrar pagos, imprimir/enviar nota de venta | Cambiar precios, ver costos, aprobar ajustes |
| Almacén / despacho | Quien tenga el permiso | Ver stock y pedidos, registrar ingresos, preparar y despachar, transferir, proponer ajustes, ver kardex | Anular pedidos, cambiar precios |
| Repartidor | Repartidores (a menudo también vendedores) | Ver stock y sus despachos, marcar en camino y entregado, registrar rechazos y pagos al entregar | Lo demás |
