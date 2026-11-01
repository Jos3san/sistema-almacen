# ADR-0002: Ciclo de vida iterativo con ciclo DevOps por capa

- **Estado:** Aceptado
- **Fecha:** 2026-10-27

## Contexto
Los requerimientos dependen de una entrevista pendiente, y el desarrollador quiere aprender DevOps y microservicios practicando.

## Decisión
Modelo iterativo e incremental: cada capa del roadmap recorre Plan → Code → Build → Test → Release → Deploy → Operate → Monitor y termina desplegada. Flujo trunk-based con ramas cortas, PR obligatorio con CI en verde, Conventional Commits y SemVer por servicio. Detalle en `docs/00-ciclo-de-vida.md`.

## Alternativas consideradas
- Cascada: requiere requerimientos cerrados que no tenemos; el ciclo DevOps se practicaría una sola vez al final.
- GitFlow: demasiadas ramas largas para un equipo de una persona; dificulta la integración continua.

## Consecuencias
- Positivas: siempre hay algo funcionando; el pipeline se perfecciona en cada capa.
- Negativas: hay que invertir en CI/CD desde la capa 1, antes de tener funcionalidad de negocio.
