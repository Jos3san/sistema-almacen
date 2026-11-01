# ADR-0004: Comunicación asíncrona por eventos con patrón outbox

- **Estado:** Propuesto (broker por elegir: RabbitMQ o Redis Streams)
- **Fecha:** 2026-10-27

## Contexto
Notificaciones, reportes e integraciones deben reaccionar a lo que pasa en `core` sin que su caída bloquee la operación. Publicar al broker directamente después del commit puede perder eventos si el proceso cae entre ambos pasos.

## Decisión
`core` escribe el evento en la tabla `outbox_event` dentro de la misma transacción del cambio de negocio. Un proceso publicador lee los pendientes y los envía al broker. Los consumidores deben ser idempotentes. Eventos versionados (`OrderConfirmed.v1`, `DispatchConfirmed.v1`, `StockBelowMinimum.v1`).

## Alternativas consideradas
- Llamadas HTTP síncronas a cada servicio: acoplan la disponibilidad de `core` a la de los demás.
- Publicar directo al broker sin outbox: riesgo de perder o duplicar eventos inconsistentemente.

## Consecuencias
- Positivas: ningún evento se pierde; los consumidores se ponen al día al recuperarse.
- Negativas: consistencia eventual en reportes; hay que operar un broker y el publicador.
