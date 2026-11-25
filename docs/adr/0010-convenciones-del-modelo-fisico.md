# ADR-0010: Convenciones del modelo físico de core

- **Estado:** Aceptado
- **Fecha:** 2026-11-25

## Contexto
El catálogo es el primer módulo de negocio de core, y sus convenciones se van a copiar en stock, pedidos y despachos. Conviene fijarlas una vez y no discutirlas en cada módulo. Detalle de las tablas en docs/09.

## Decisión
- Claves primarias `bigint` generadas por PostgreSQL en core (auth usa UUID porque sus ids viajan en los tokens).
- Nada se borra: se desactiva (`active = false`), para que los registros viejos sigan siendo válidos.
- Las reglas que la base puede garantizar van como `CHECK` o `UNIQUE`, además de validarse en el código (por ejemplo, `factor >= 1`, `price > 0`, SKU único sin importar mayúsculas).
- Cada módulo es dueño de sus tablas: un módulo usa a otro solo por su servicio público (ADR-0003). Por eso el stock mínimo vive en el catálogo (`minimum_stock`) y no como columna de `stock`.
- Los datos repetibles con variantes de escritura van en tablas propias (marcas, categorías) para no duplicar "Faber" y "faber".
- Los cuerpos de petición rechazan campos desconocidos (422) en vez de ignorarlos.

## Alternativas consideradas
- UUID en todo core: ids largos e incómodos para el negocio, sin ventaja mientras core sea una sola base.
- Borrado físico: rompería pedidos e historia que apuntan a productos dados de baja.
- Validar solo en el código: un error dejaría datos imposibles en la base.

## Consecuencias
- Positivas: datos consistentes aunque falle el código; cada módulo se puede separar en un servicio más adelante.
- Negativas: las tablas acumulan registros inactivos; los listados filtran por `active` por defecto.
- Revisar si: un módulo se separa en su propio servicio (sus tablas pasan a su propia base, como auth).
