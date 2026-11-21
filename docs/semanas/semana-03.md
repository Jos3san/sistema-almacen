# Semana 3 (16/11 – 22/11) · Capa 2: Auth

Objetivo: seguridad automatizada en la CI, tablero del proyecto y el segundo microservicio (auth).
Calendario replanificado el 14/11 (docs/04): esta semana empezó el 14/11 con T-20.
Marca `[x]` cada punto al terminarlo y anota en "Notas" lo que te costó o aprendiste.
Leyenda: 🧑‍🏫 = te muestro cómo · 🛠️ = lo haces tú siguiendo el patrón.

Detalle y criterios de aceptación de cada tarea: `docs/07-backlog.md`.

## T-20 · Seguridad automatizada en CI (DevSecOps) 🧑‍🏫
- [x] Secret scanning con push protection y alertas de Dependabot (activados en la semana 2)
- [x] `.github/dependabot.yml`: uv, Dockerfile, Compose y GitHub Actions, cada lunes
- [x] Ruff con reglas `S` (seguridad) y `C90` (complejidad máxima 10)
- [x] pip-audit en la CI: sin vulnerabilidades conocidas en `uv.lock`
- [x] Trivy en la CI; la imagen se endureció (parches del sistema y sin `pip`) hasta quedar limpia
- [x] Los tests leen la imagen de PostgreSQL de `compose.yaml` (una sola versión que mantener)
- [x] CodeQL activado en GitHub (configuración por defecto): analiza Python y GitHub Actions, 0 alertas
- [x] PR fusionado (PR #10)

## Tablero (B5 / T-04) 🛠️
- [ ] Permiso `project` para `gh` y tablero de GitHub Projects con las historias de la semana

## Plantilla Excel de productos (HU-10) 🧑‍🏫
- [x] Plantilla `docs/plantillas/Plantilla_Productos.xlsx` (generada por `build_plantilla_productos.py`): ubicaciones, productos, presentaciones, precios por escala y stock mínimo, con validaciones y ejemplos ficticios
- [ ] Revisada por ti y enviada al dueño el 23/11 (N-04)

## Auth (HU-01 a HU-06, T-11 a T-13)
- [ ] Se detalla al empezar la capa

## Notas
Tu retrospectiva (también va resumida en docs/00, sección 7). Unas líneas por pregunta:
1. ¿Qué funcionó bien y conviene repetir?
2. ¿Qué costó más de lo esperado y por qué?
3. ¿Qué cambio concreto hago en la próxima capa?
