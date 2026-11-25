# Semana 4 (23/11 – 29/11) · Capa 3: Catálogo

Objetivo: el catálogo completo en core (productos, presentaciones, precios, ubicaciones, clientes, proveedores) e importación desde Excel.
Marca `[x]` cada punto al terminarlo y anota en "Notas" lo que te costó o aprendiste.
Leyenda: 🧑‍🏫 = te muestro cómo · 🛠️ = lo haces tú siguiendo el patrón.

Diseño: `docs/09-modelo-fisico.md` (D4). Historias: `docs/07-backlog.md`.

## D4 · Modelo físico del catálogo 🧑‍🏫
- [x] 10 tablas con sus restricciones, reglas, API y permisos (25/11)
- [x] Decisiones aprobadas: marcas en tabla, stock mínimo en tabla propia, documento del cliente opcional (lo confirmó Jossan el 25/11)
- [ ] Pregunta al dueño: ¿el costo incluye IGV?

## Catálogo, parte 1 (HU-07, HU-08, HU-09, HU-11) 🧑‍🏫
- [x] Módulo `catalog` en core con capas `api` → `service` → `repository`
- [x] Migración: categorías, marcas, ubicaciones, productos, presentaciones, escalas de precio, stock mínimo y `audit_log`
- [x] Presentación base automática; factor inmutable; códigos de barras únicos entre productos y presentaciones
- [x] Costo visible y editable solo con `cost.view`
- [x] Auditoría en la misma transacción; `core_app` no puede modificar ni borrar `audit_log` (RNF-05)
- [x] Los cuerpos de petición rechazan campos desconocidos (asignación masiva)
- [x] 18 tests (401/403 incluidos); en total 72 tests en verde
- [ ] PR fusionado

## Catálogo, parte 2 (HU-12, HU-13)
- [ ] Clientes (documento opcional) y proveedores

## Importación (HU-10)
- [ ] Importar la plantilla con reporte de errores por fila (`dry_run`)
- [ ] Script de datos ficticios (~300 productos) para desarrollo y demo

## Pendientes de la semana 3 (pasan a la semana 5)
- [ ] HU-04 Gestionar usuarios y permisos (#23)
- [ ] HU-06 Pantalla de login y T-13 Base del frontend (#25, #28)

## Notas
Tu retrospectiva (también va resumida en docs/00, sección 7). Unas líneas por pregunta:
1. ¿Qué funcionó bien y conviene repetir?
2. ¿Qué costó más de lo esperado y por qué?
3. ¿Qué cambio concreto hago en la próxima capa?
