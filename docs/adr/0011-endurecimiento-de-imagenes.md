# ADR-0011: Endurecimiento de las imágenes y contenedores

- **Estado:** Aceptado
- **Fecha:** 2026-11-14

## Contexto
Un contenedor trae un sistema operativo completo. En T-20, pip-audit no encontró vulnerabilidades en nuestras dependencias, pero Trivy encontró 14 altas o críticas en la imagen base: paquetes de Debian sin parchear y librerías incluidas dentro de `pip`, que el servicio ni siquiera usa.

## Decisión
- Imágenes multi-stage con versión fija (nunca `latest`).
- La etapa final aplica los parches de seguridad del sistema (`apt-get upgrade`) y **elimina `pip`**.
- El proceso corre con un usuario sin privilegios y su código pertenece a root (no puede modificarse a sí mismo).
- El gateway corre como usuario sin privilegios y con disco de solo lectura.
- Trivy revisa cada imagen en la CI y falla con vulnerabilidades altas o críticas que tengan arreglo.

## Alternativas consideradas
- Imagen *distroless*: aún más pequeña, pero sin shell para diagnosticar; demasiado para el nivel actual del proyecto.
- No parchear y esperar a que la imagen base se actualice: deja vulnerabilidades conocidas en producción por semanas.

## Consecuencias
- Positivas: imágenes sin vulnerabilidades conocidas con arreglo; menos superficie de ataque.
- Negativas: la imagen pasó de ~233 MB a ~339 MB, y el build es menos reproducible (los parches cambian con el tiempo).
- Revisar si: el tamaño o el tiempo de despliegue se vuelven un problema, o la imagen base pasa a traer los parches a tiempo.
