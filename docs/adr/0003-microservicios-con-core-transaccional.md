# ADR-0003: Microservicios con un servicio núcleo transaccional

- **Estado:** Aceptado
- **Fecha:** 2026-10-27

## Contexto
Se quiere que la falla de un componente no detenga la operación y que el sistema pueda crecer. Pero inventario, pedidos y despachos modifican el stock en la misma transacción (reservar, descontar), y separarlos exigiría transacciones distribuidas (sagas) desde el día uno.

## Decisión
- Servicio `core` = Inventario + Pedidos + Despachos, con módulos de límites estrictos para poder dividirlo después.
- Servicios separados: `auth`, `notifications`, `reports`, `integrations`, detrás de un `gateway`.
- Cada servicio con su propia base de datos o esquema; ningún servicio lee la BD de otro.

## Alternativas consideradas
- Monolito único: más simple, pero no cumple el objetivo de aislamiento de fallas ni de aprendizaje.
- Un microservicio por entidad (inventario, pedidos, despachos separados): obliga a sagas y consistencia eventual en la regla más crítica (stock nunca negativo).

## Consecuencias
- Positivas: la regla de stock se protege con una transacción ACID local; los servicios periféricos pueden caer sin afectar pedidos ni despachos (RNF-10).
- Negativas: costo operativo de varios servicios (pipelines, despliegues, monitoreo) para un equipo de una persona.
- Revisar si `core` crece mucho o si un módulo necesita escalar por separado.
