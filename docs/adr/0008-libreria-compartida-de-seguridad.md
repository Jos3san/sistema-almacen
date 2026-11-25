# ADR-0008: Librería compartida solo para la validación de tokens

- **Estado:** Aceptado
- **Fecha:** 2026-11-21

## Contexto
ADR-0007 decidió que cada servicio valide el JWT por su cuenta. Validar bien un token tiene detalles de seguridad (algoritmo fijo, `iss`, `aud`, `exp`, claims obligatorios) que, programados por separado en cada servicio, terminarían divergiendo. A la vez, el código compartido entre microservicios los acopla: si `libs/` crece, los servicios dejan de ser independientes.

## Decisión
Un único paquete Python, `libs/security` (`almacen-security`), con la validación del token (`TokenValidator`) y la protección de endpoints (`TokenGuard`, 401/403). Cada servicio lo instala como dependencia de ruta. **Nada de lógica de negocio va en `libs/`.** Otro código compartido (por ejemplo, los logs) solo pasa a una librería con la regla de tres: cuando haya tres copias (docs/10).

## Alternativas consideradas
- Copiar la validación en cada servicio: más independencia, pero un error de seguridad corregido en un lugar quedaría vivo en otro.
- Validar en el gateway: Caddy no valida JWT sin plugins, y hacer que el gateway le pregunte a auth acopla la operación a auth (ADR-0007).
- Una librería "común" con todo lo compartido: tiende a crecer sin control y a acoplar los servicios.

## Consecuencias
- Positivas: una sola implementación, probada con 15 tests (incluidos los ataques `alg: none` y HS256 con la clave pública).
- Negativas: cambiar la librería afecta a todos los servicios a la vez; las imágenes se construyen con contexto en la raíz del repo para poder copiarla.
- Revisar si: los servicios pasan a repositorios separados (entonces la librería se publicaría como paquete versionado).
