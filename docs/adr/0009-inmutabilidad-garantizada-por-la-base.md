# ADR-0009: Lo inmutable lo garantiza la base de datos, no solo el código

- **Estado:** Aceptado
- **Fecha:** 2026-11-25

## Contexto
El kardex (regla 1 de docs/03) y la auditoría (RF-23) solo admiten inserciones (RNF-05). Si esa regla vive únicamente en el código, un error, un script manual o un atacante con acceso a la aplicación podría modificar la historia sin dejar rastro.

## Decisión
Cada servicio usa dos usuarios de base: el **dueño del esquema**, solo para migraciones, y el **usuario de la aplicación**, con permisos mínimos (T-10). En las tablas que deben ser inmutables, la migración le quita al usuario de la aplicación `UPDATE`, `DELETE` y `TRUNCATE`. Ya se aplica a `audit_log` (catálogo, 25/11) y se aplicará al kardex (semana 5). Un test comprueba en cada caso que la base rechaza esos cambios.

## Alternativas consideradas
- Confiar solo en el código (no exponer endpoints de edición): no protege de errores ni de accesos directos a la base.
- Triggers que bloqueen UPDATE/DELETE: funcionan, pero son más difíciles de ver y probar que un permiso, y el dueño del esquema podría desactivarlos sin querer.

## Consecuencias
- Positivas: aunque el código tenga un error, la historia no se puede alterar.
- Negativas: corregir un error se hace con un movimiento o un registro nuevo, nunca editando (es justamente lo que pide el negocio). Las pruebas que limpian tablas deben usar el usuario dueño.
- Revisar si: se necesita archivar o anonimizar datos personales viejos (Ley 29733); se haría con un procedimiento del dueño del esquema, documentado.
