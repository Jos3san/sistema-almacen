# ADR-0007: JWT firmado por auth y validado en cada servicio

- **Estado:** Aceptado
- **Fecha:** 2026-10-31

## Contexto
docs/04 decía que el gateway valida el JWT. Caddy y Nginx no validan JWT sin plugins o scripts, y la alternativa común (que el gateway pregunte a auth en cada petición) hace que una caída de auth detenga pedidos y stock, lo que va contra RNF-10.

## Decisión
- auth firma los access tokens con **RS256** (clave privada solo en auth).
- La clave pública se entrega a cada servicio (hoy solo core) como **archivo montado** (`JWT_PUBLIC_KEY_PATH`), no se descarga de auth: así core puede arrancar y validar aunque auth esté caído. Rotar la clave es un paso manual documentado.
- Cada servicio valida firma, vencimiento y permisos localmente.
- El gateway solo termina HTTPS, enruta y sirve el frontend.
- Access token de 15 minutos con los permisos del usuario; refresh token rotado de 7 días guardado hasheado.

## Alternativas consideradas
- Validar en el gateway con plugin o `forward_auth` hacia auth: suma una dependencia de auth en cada petición.
- Clave simétrica (HS256) compartida: cualquier servicio que la tenga podría emitir tokens.
- Sesiones en base de datos: cada petición consultaría a auth.

## Consecuencias
- Positivas: si auth cae, los tokens vigentes siguen funcionando hasta 15 minutos y los pedidos no se detienen; se aprende firma asimétrica, uno de los patrones estándar en microservicios.
- Negativas: un permiso quitado puede valer hasta 15 minutos; cada servicio debe implementar la validación (se comparte como un pequeño módulo).
- Revisar si se necesita revocación inmediata.
