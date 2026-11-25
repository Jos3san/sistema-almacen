# Deuda técnica y mejoras diferidas (con disparadores)

Mejoras que **sabemos** que harán falta, pero que **todavía no** se justifican. Hacerlas antes de tiempo suma complejidad que hay que entender y mantener sin necesitarla (YAGNI, docs/06 D1.11); olvidarlas la hace más cara después.

Por eso cada una tiene un **disparador**: la señal concreta de que llegó su momento. En cada retrospectiva (docs/00, sección 7) se revisa esta tabla: si un disparador se encendió, la mejora entra al backlog de esa semana.

Origen: auditoría del 25/11/2026.

## Mejoras con disparador
| # | Mejora | Por qué hará falta | Disparador | Estado |
| --- | --- | --- | --- | --- |
| DT-1 | Límites entre módulos de core verificados en la CI (*import-linter*) | ADR-0003 promete poder separar catálogo, stock, pedidos y despachos en servicios; sin una regla automática, un módulo puede terminar usando las tablas de otro | Nace el **segundo módulo de negocio** de core (stock, semana 5) | Pendiente |
| DT-2 | Tabla `outbox_event` (ADR-0004) | Notificaciones, reportes e integraciones escucharán eventos ("stock bajo", "pedido entregado") sin tocar la lógica de negocio | Se diseña en el D4 de **stock**; el publicador y el broker, cuando exista el **primer servicio que escuche** (notifications, después del MVP) | Pendiente |
| DT-3 | Librería de observabilidad (logs JSON y middleware) | Hoy hay 2 copias (core y auth); mantener más copias a mano termina en diferencias | **Regla de tres**: aparece un **tercer servicio** | Pendiente |
| DT-4 | Un solo PostgreSQL por sesión de tests | Cada archivo de tests de core levanta su contenedor; con más módulos la CI se alarga | La CI pasa de **~5 minutos** | Pendiente |
| DT-5 | Imágenes publicadas en GHCR con versión (`core:0.4.0`) | Desplegar exactamente lo probado y volver a la versión anterior en segundos | **Primer despliegue a staging** (T-14, semana 5) | Pendiente |
| DT-6 | Límite de intentos de login por IP en el gateway | Hoy se bloquea por usuario; un atacante puede probar una contraseña en muchos usuarios | **Antes de exponer** el sistema a internet (staging) | Pendiente |
| DT-7 | Cliente TypeScript generado desde OpenAPI | Si cambia un campo de la API, el frontend no compila en vez de fallar en el celular | **Primera pantalla** del frontend (T-13) | Pendiente |
| DT-8 | Versiones escritas dentro de comandos de la CI (`aquasec/trivy:0.76.2`, `pip-audit@2.10.1`) | Dependabot no las ve | **Cada retrospectiva**: revisarlas a mano | Recurrente |

## Riesgos que no son técnicos (auditoría del 25/11)
| # | Riesgo | Acción |
| --- | --- | --- |
| R-1 | Alcance sin firmar (N-01 venció el 08/11) | Jossan pide la confirmación del dueño, aunque sea por escrito informal |
| R-2 | Jossan debe poder mantener el sistema, no solo usarlo | Desde el 25/11, las piezas que siguen un patrón ya existente las escribe él, guiado paso a paso (acuerdo en CLAUDE.md) |
| R-3 | El calendario supone más horas de las disponibles | Revisar en cada retrospectiva; recortar alcance antes que calidad (docs/04) |

## Cómo se usa
- Al cerrar cada semana: revisar los disparadores y mover a "En curso" lo que corresponda.
- Una mejora hecha pasa a "Hecha (PR #N)" y, si cambió una decisión, tiene su ADR.
- Cualquier atajo que tomemos a propósito (por ejemplo, copiar código para no adelantar una abstracción) se anota aquí con su disparador.
