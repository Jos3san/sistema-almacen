# ADR-0005: MVP para diciembre con gateway + auth + core

- **Estado:** Aceptado
- **Fecha:** 2026-10-27

## Contexto
La entrevista fija producción en enero 2027 (campaña escolar, su pico de pedidos del año), con el sistema listo en diciembre y carga de datos la última semana de diciembre. Hay ~8 semanas y un solo desarrollador que aprende programación y DevOps. Lo crítico para el negocio es tomar pedidos y consultar stock; el despacho puede hacerse a mano en una contingencia.

## Decisión
- El MVP despliega solo `gateway`, `auth` y `core`. Los reportes del MVP son un módulo de lectura dentro de `core`.
- `notifications`, `reports` (como servicio), `integrations`, el broker y el outbox se implementan después de salir a producción.
- El frontend se construye en cada capa, no al final.
- Sin modo offline: se requiere conexión.
- RPO y RTO de 1 hora: archivado continuo de WAL desde el MVP.
- Ante atrasos se recorta alcance en este orden: reportes, transferencias, detalle de pagos.

## Alternativas consideradas
- Todos los microservicios desde el inicio: no entra en el plazo y multiplica el trabajo operativo antes de tener valor de negocio.
- Monolito: cumple el plazo, pero pierde el objetivo de aprendizaje y la separación de auth.
- Salir después de la campaña (abril): menos riesgo, pero el negocio pide enero.

## Consecuencias
- Positivas: plazo alcanzable; cada servicio nuevo llega con el pipeline ya maduro.
- Negativas: ADR-0004 (eventos) se pospone; el sistema arranca en temporada alta, lo que exige pruebas con el dueño desde la semana 4 y un plan de contingencia en papel.
