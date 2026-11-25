# ADR-0012: Política de actualización de dependencias

- **Estado:** Aceptado
- **Fecha:** 2026-11-21

## Contexto
Dependabot abre PRs con versiones nuevas cada semana. En la primera tanda abrió 6, y uno subía Python de 3.13 a 3.15 (la imagen ni compilaba). Además, varios PRs tocaban los mismos archivos (`pyproject.toml`, `uv.lock`) y entraban en conflicto entre sí.

## Decisión
- Un solo PR semanal por proyecto de Python, con todas sus actualizaciones menores y parches agrupadas.
- Se ignoran automáticamente los cambios de versión de Python (solo parches 3.13.x) y las versiones mayores de PostgreSQL: son decisiones de arquitectura que se planifican a mano, con su ADR.
- Ningún PR de dependencias se fusiona sin CI en verde y sin revisar qué cambia (guía en docs/codigo/infra.md). Los que tocan `uv.lock` se rehacen sobre `main` (`@dependabot rebase`) antes de fusionar.

## Alternativas consideradas
- Aceptar todo lo que esté en verde: un salto de versión mayor puede pasar los tests y fallar en producción.
- Actualizar a mano cada cierto tiempo: las vulnerabilidades quedan abiertas hasta que alguien se acuerde.

## Consecuencias
- Positivas: parches de seguridad semanales con poco ruido.
- Negativas: alguien debe revisar los PRs cada semana (unos minutos).
- Revisar si: el volumen de PRs se vuelve inmanejable, o se decide cambiar de versión de Python.
