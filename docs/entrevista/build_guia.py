from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule

S = "★ Imprescindible"
N = "Normal"

Q = [
 # 1
 ("1. Negocio y operación", "¿Qué venden exactamente? ¿Útiles, libros, oficina, arte, otros? ¿Venden al por menor, al por mayor o ambos?", S, "Dueño", "General"),
 ("1. Negocio y operación", "¿Cuántos locales y almacenes tienen? ¿Dónde están?", S, "Dueño", "Inventario"),
 ("1. Negocio y operación", "¿Cuántas personas trabajan y en qué rol (dueños, vendedores, almacén, reparto)?", S, "Dueño", "Usuarios / Auth"),
 ("1. Negocio y operación", "Hoy, ¿cómo controlan el stock y los pedidos? ¿Cuaderno, Excel, otro sistema?", S, "Todos", "General"),
 ("1. Negocio y operación", "¿Cuáles son los tres problemas que más les cuestan hoy (tiempo, dinero, errores)?", S, "Todos", "General"),
 ("1. Negocio y operación", "¿Cuántos pedidos atienden en un día normal? ¿Y en temporada escolar (enero a marzo)?", N, "Dueño", "Infraestructura"),
 ("1. Negocio y operación", "¿Qué tan seguido les pasa vender algo que no había en stock, o no encontrar algo que sí había?", N, "Vendedor", "Inventario"),
 ("1. Negocio y operación", "¿Tienen temporadas o campañas con mucho más movimiento? ¿Qué cambia en esas fechas?", N, "Dueño", "Infraestructura"),
 ("1. Negocio y operación", "¿Quién toma las decisiones sobre el sistema y quién lo va a usar más?", N, "Dueño", "General"),
 # 2
 ("2. Productos y stock", "¿Cuántos productos distintos manejan, aproximadamente?", S, "Dueño", "Catálogo"),
 ("2. Productos y stock", "¿Los productos tienen código de barras? ¿Usan código propio o del fabricante?", S, "Almacén", "Catálogo"),
 ("2. Productos y stock", "¿Venden por unidad, caja, docena o paquete? ¿Un mismo producto se vende de varias formas? (lapicero suelto y caja de 12)", S, "Vendedor", "Catálogo"),
 ("2. Productos y stock", "¿Hay productos con variantes (color, tamaño, modelo)? ¿Cómo los diferencian hoy?", N, "Almacén", "Catálogo"),
 ("2. Productos y stock", "¿Manejan productos con fecha de vencimiento o por lote (pegamentos, tintas)?", N, "Almacén", "Inventario"),
 ("2. Productos y stock", "¿Cómo organizan el almacén? ¿Por estantes, pasillos, ubicaciones?", S, "Almacén", "Inventario"),
 ("2. Productos y stock", "¿Mueven mercadería entre almacenes o entre almacén y tienda? ¿Cómo lo registran?", N, "Almacén", "Inventario"),
 ("2. Productos y stock", "¿Cada cuánto hacen inventario físico? ¿Cuánto tarda y cuántas diferencias encuentran?", S, "Almacén", "Inventario"),
 ("2. Productos y stock", "¿Qué hacen cuando hay mermas, roturas, robos o productos dañados?", N, "Almacén", "Inventario"),
 ("2. Productos y stock", "¿Quieren alertas de stock mínimo? ¿Quién debe recibirlas?", N, "Dueño", "Notificaciones"),
 ("2. Productos y stock", "¿Necesitan saber el costo del stock (stock valorizado)? ¿Con último costo o costo promedio?", N, "Dueño", "Reportes"),
 # 3
 ("3. Compras e ingresos", "¿Cómo llega la mercadería? ¿Con factura, guía de remisión, ambas?", S, "Almacén", "Inventario"),
 ("3. Compras e ingresos", "¿Quién recibe y cuenta la mercadería? ¿Qué pasa si llega menos o diferente a lo pedido?", S, "Almacén", "Inventario"),
 ("3. Compras e ingresos", "¿Cuántos proveedores tienen? ¿Les hacen órdenes de compra formales?", N, "Dueño", "Inventario"),
 ("3. Compras e ingresos", "¿Quieren que el sistema sugiera qué comprar según el stock mínimo o las ventas?", N, "Dueño", "Reportes"),
 ("3. Compras e ingresos", "¿Registran el costo de cada compra? ¿Cambia seguido?", N, "Dueño", "Catálogo"),
 ("3. Compras e ingresos", "¿Reciben devoluciones de clientes o hacen devoluciones a proveedores? ¿Cómo las manejan?", N, "Almacén", "Inventario"),
 # 4
 ("4. Vendedores y pedidos", "¿Cuántos vendedores hay? ¿Venden en tienda, en la calle, por WhatsApp o por teléfono?", S, "Dueño", "Pedidos"),
 ("4. Vendedores y pedidos", "Cuéntame paso a paso el último pedido que tomaste, desde que hablaste con el cliente hasta que recibió todo.", S, "Vendedor", "Pedidos"),
 ("4. Vendedores y pedidos", "¿Necesitas ver el stock antes de prometer un producto? ¿Desde el celular?", S, "Vendedor", "Inventario"),
 ("4. Vendedores y pedidos", "¿Alguien revisa o aprueba los pedidos antes de que pasen al almacén? ¿Quién y por qué?", S, "Dueño", "Pedidos"),
 ("4. Vendedores y pedidos", "¿Los vendedores necesitan tomar pedidos sin conexión a internet (zonas sin señal)?", N, "Vendedor", "Pedidos"),
 ("4. Vendedores y pedidos", "¿Un vendedor debe ver los pedidos o clientes de otro vendedor?", N, "Dueño", "Usuarios / Auth"),
 ("4. Vendedores y pedidos", "¿Se pueden modificar o anular pedidos? ¿Hasta qué momento y quién lo autoriza?", N, "Dueño", "Pedidos"),
 ("4. Vendedores y pedidos", "¿Hay pedidos que se separan o reservan para un cliente y se recogen después?", N, "Vendedor", "Pedidos"),
 ("4. Vendedores y pedidos", "¿Les interesa medir ventas por vendedor? ¿Pagan comisiones?", N, "Dueño", "Reportes"),
 # 5
 ("5. Clientes y precios", "¿Qué tipos de clientes tienen (público, colegios, empresas, otras librerías)?", S, "Dueño", "Clientes"),
 ("5. Clientes y precios", "¿Qué datos del cliente necesitan (RUC/DNI, dirección de entrega, contacto)?", N, "Vendedor", "Clientes"),
 ("5. Clientes y precios", "¿Venden al crédito? ¿Necesitan controlar lo que cada cliente debe?", N, "Dueño", "Clientes"),
 ("5. Clientes y precios", "¿Tienen un solo precio por producto o varios (minorista, mayorista, colegio, cliente especial)?", S, "Dueño", "Catálogo"),
 ("5. Clientes y precios", "¿Quién puede dar descuentos y hasta cuánto?", S, "Dueño", "Pedidos"),
 ("5. Clientes y precios", "¿Hay precios por cantidad (por ejemplo, más de 12 unidades, otro precio)?", N, "Vendedor", "Catálogo"),
 ("5. Clientes y precios", "¿Los precios incluyen IGV? ¿Cómo se muestra en la nota de venta?", N, "Dueño", "Pedidos"),
 ("5. Clientes y precios", "¿Hacen listas escolares o paquetes armados? ¿Cómo los venden?", N, "Vendedor", "Catálogo"),
 # 6
 ("6. Despachos y entregas", "¿Cómo se entera el almacén de que hay un pedido por preparar? (papel, WhatsApp, llamada)", S, "Almacén", "Despachos"),
 ("6. Despachos y entregas", "¿Quién prepara el pedido y quién revisa que esté completo antes de que salga?", S, "Almacén", "Despachos"),
 ("6. Despachos y entregas", "Si falta stock, ¿despachan lo que hay y el resto después, esperan a tener todo, o reemplazan el producto?", S, "Almacén", "Despachos"),
 ("6. Despachos y entregas", "¿El cliente recoge en tienda, lo llevan ustedes o usan un courier/agencia?", S, "Dueño", "Despachos"),
 ("6. Despachos y entregas", "¿Tienen repartidores o movilidad propia? ¿Necesitan asignar pedidos a un repartidor o ruta?", N, "Dueño", "Despachos"),
 ("6. Despachos y entregas", "¿Qué documento acompaña el despacho? ¿Guía de remisión, nota de despacho, la misma nota de venta?", N, "Almacén", "Despachos"),
 ("6. Despachos y entregas", "¿Necesitan constancia de entrega (firma, foto, nombre de quien recibió)?", N, "Dueño", "Despachos"),
 ("6. Despachos y entregas", "¿Cuál es el tiempo esperado entre que se toma el pedido y se entrega?", N, "Dueño", "Despachos"),
 ("6. Despachos y entregas", "¿Qué hacen cuando el cliente rechaza o devuelve parte del pedido al recibirlo?", N, "Almacén", "Inventario"),
 ("6. Despachos y entregas", "¿Necesitan ver el estado de cada pedido (pendiente, en preparación, en camino, entregado)?", N, "Todos", "Pedidos"),
 # 7
 ("7. Nota de venta y facturación", "¿Qué sistema usan para facturar? ¿Es web o instalado? ¿Tiene API o permite importar/exportar Excel o CSV?", S, "Dueño", "Integraciones"),
 ("7. Nota de venta y facturación", "¿En qué momento emiten la boleta o factura: al tomar el pedido, al despachar o al entregar?", S, "Dueño", "Integraciones"),
 ("7. Nota de venta y facturación", "¿Los productos y precios deben estar en un solo sistema o pueden duplicarse? ¿Quién mantendría cada uno?", S, "Dueño", "Integraciones"),
 ("7. Nota de venta y facturación", "¿Necesitan relacionar cada nota de venta con su boleta o factura (guardar el número)?", N, "Dueño", "Pedidos"),
 ("7. Nota de venta y facturación", "¿Qué datos debe llevar la nota de venta? (logo, RUC, cliente, vendedor, condiciones de pago)", N, "Dueño", "Pedidos"),
 ("7. Nota de venta y facturación", "¿Se imprime en ticketera, en A4, o se envía en PDF por WhatsApp o correo?", N, "Vendedor", "Pedidos"),
 ("7. Nota de venta y facturación", "¿La numeración de notas de venta debe seguir una serie específica?", N, "Dueño", "Pedidos"),
 ("7. Nota de venta y facturación", "¿Cobran al tomar el pedido, al entregar o al crédito? ¿Qué medios de pago aceptan (efectivo, Yape, Plin, transferencia, tarjeta)?", N, "Dueño", "Pedidos"),
 # 8
 ("8. Usuarios y reportes", "¿Cuántas personas usarán el sistema y cuántas al mismo tiempo?", S, "Dueño", "Infraestructura"),
 ("8. Usuarios y reportes", "¿Qué no debería poder hacer cada rol? (que el vendedor no cambie precios, que el almacenero no anule pedidos)", S, "Dueño", "Usuarios / Auth"),
 ("8. Usuarios y reportes", "¿Necesitan saber quién hizo cada cambio y cuándo (auditoría)?", N, "Dueño", "Usuarios / Auth"),
 ("8. Usuarios y reportes", "¿Quién debe aprobar ajustes de inventario?", N, "Dueño", "Inventario"),
 ("8. Usuarios y reportes", "¿Qué información quisieran mirar todos los días? ¿Y a fin de mes?", S, "Dueño", "Reportes"),
 ("8. Usuarios y reportes", "¿Qué reportes usan hoy en Excel que el sistema debería reemplazar?", N, "Dueño", "Reportes"),
 ("8. Usuarios y reportes", "¿Necesitan exportar reportes a Excel o PDF?", N, "Dueño", "Reportes"),
 ("8. Usuarios y reportes", "¿Algún dato es confidencial (costos, márgenes) y solo deben verlo los dueños?", N, "Dueño", "Usuarios / Auth"),
 # 9
 ("9. Tecnología y migración", "¿Qué equipos usan: PC, laptop, celulares Android o iPhone, tablets?", S, "Todos", "Infraestructura"),
 ("9. Tecnología y migración", "¿Qué tal es el internet en la tienda, el almacén y en la calle? ¿Se cae seguido?", S, "Todos", "Infraestructura"),
 ("9. Tecnología y migración", "¿Tienen lectoras de código de barras o impresoras de tickets? ¿Qué modelos?", N, "Almacén", "Infraestructura"),
 ("9. Tecnología y migración", "¿Dónde está hoy la lista de productos, precios, clientes y stock? ¿Nos la pueden pasar en Excel?", S, "Dueño", "Catálogo"),
 ("9. Tecnología y migración", "¿Qué tan confiable es el stock actual? ¿Conviene hacer un inventario inicial antes de arrancar?", N, "Almacén", "Inventario"),
 ("9. Tecnología y migración", "¿Tienen dominio web o correo corporativo?", N, "Dueño", "Infraestructura"),
 ("9. Tecnología y migración", "¿Les preocupa dónde se guardan los datos? ¿Prefieren servidor propio o en la nube?", N, "Dueño", "Infraestructura"),
 ("9. Tecnología y migración", "¿Quién dará soporte cuando algo falle? ¿En qué horario necesitan que funcione?", N, "Dueño", "Infraestructura"),
 # 10 new
 ("10. Disponibilidad y continuidad", "Si el sistema falla una hora, ¿qué procesos deben seguir funcionando sí o sí? (tomar pedidos, consultar stock, despachar)", S, "Dueño", "Infraestructura"),
 ("10. Disponibilidad y continuidad", "¿Qué es más grave para el negocio: no poder tomar pedidos o no poder despachar?", S, "Dueño", "General"),
 ("10. Disponibilidad y continuidad", "¿Aceptarían registrar un pedido aunque el stock se confirme unos minutos después, en vez de al instante?", S, "Dueño", "Pedidos"),
 ("10. Disponibilidad y continuidad", "¿Cuánto tiempo máximo pueden estar sin sistema antes de que afecte las ventas?", S, "Dueño", "Infraestructura"),
 ("10. Disponibilidad y continuidad", "Si hay una falla grave, ¿cuánta información podrían perder como máximo? (la última hora, el último día)", S, "Dueño", "Infraestructura"),
 ("10. Disponibilidad y continuidad", "¿En qué horario operan? ¿Hay horarios en que se pueda hacer mantenimiento sin afectar a nadie?", N, "Dueño", "Infraestructura"),
 ("10. Disponibilidad y continuidad", "Si el sistema no está disponible, ¿cómo seguirían trabajando mientras tanto? (papel, Excel)", N, "Todos", "General"),
 ("10. Disponibilidad y continuidad", "¿Necesitan avisos automáticos (WhatsApp, correo) cuando un pedido cambia de estado o el stock baja?", N, "Dueño", "Notificaciones"),
 # 11
 ("11. Crecimiento y prioridades", "Si el sistema solo pudiera hacer tres cosas el primer mes, ¿cuáles serían?", S, "Dueño", "General"),
 ("11. Crecimiento y prioridades", "¿Para cuándo lo necesitan funcionando? ¿Hay una fecha clave (por ejemplo, la campaña escolar)?", S, "Dueño", "General"),
 ("11. Crecimiento y prioridades", "¿Cuánto pueden pagar al mes por el servidor y el dominio?", S, "Dueño", "Infraestructura"),
 ("11. Crecimiento y prioridades", "En 1 o 2 años, ¿planean abrir más locales, sumar vendedores o vender por internet?", S, "Dueño", "General"),
 ("11. Crecimiento y prioridades", "¿Qué otros sistemas les gustaría conectar a futuro (facturación, tienda online, app, contabilidad)?", N, "Dueño", "Integraciones"),
 ("11. Crecimiento y prioridades", "¿Cómo sabremos que el sistema funcionó? (cero pedidos sin stock, inventario cuadrado, despachos en menos de 24 h)", N, "Dueño", "General"),
 ("11. Crecimiento y prioridades", "¿Quién estará disponible para probar el sistema y dar comentarios cada semana?", N, "Dueño", "General"),
 ("11. Crecimiento y prioridades", "¿Están de acuerdo en que el proyecto se muestre en un portafolio con datos ficticios y sin el nombre del negocio?", N, "Dueño", "General"),
]

DOCS = [
 "Lista de productos con códigos, precios y categorías",
 "Lista de clientes frecuentes",
 "Lista de proveedores",
 "Una nota de venta actual (foto o PDF)",
 "Una boleta o factura del sistema de facturación",
 "Una guía de remisión o documento de despacho, si usan",
 "Una factura de compra a proveedor",
 "Excel o cuadernos de control de stock que usen hoy",
 "Fotos del almacén y de cómo está organizado",
 "Logo y datos del negocio para los documentos impresos",
 "Nombre, versión y contacto de soporte del sistema de facturación",
]

FONT = "Arial"
navy = "1F3864"
hdr_fill = PatternFill("solid", fgColor=navy)
hdr_font = Font(name=FONT, bold=True, color="FFFFFF", size=10)
body = Font(name=FONT, size=10)
bold = Font(name=FONT, size=10, bold=True)
input_fill = PatternFill("solid", fgColor="FFF2CC")
thin = Side(style="thin", color="BFBFBF")
border = Border(left=thin, right=thin, top=thin, bottom=thin)
wrap = Alignment(wrap_text=True, vertical="top")
center = Alignment(horizontal="center", vertical="top", wrap_text=True)

wb = Workbook()

# ---------- Instrucciones ----------
ins = wb.active
ins.title = "Instrucciones"
ins.sheet_view.showGridLines = False
ins["A1"] = "Guía de entrevista: Sistema de Almacén y Despachos"
ins["A1"].font = Font(name=FONT, size=16, bold=True, color=navy)
ins["A2"] = "Preparada el 22/10/2026. Objetivo: entender cómo trabaja hoy la librería antes de diseñar el sistema por capas y microservicios."
ins["A2"].font = Font(name=FONT, size=10, italic=True, color="595959")
lines = [
 ("Cómo usarla", None),
 ("1.", "Si se puede, haz la entrevista en el local o el almacén mientras trabajan. Ver un pedido real de principio a fin vale más que diez respuestas."),
 ("2.", "Pide siempre un ejemplo concreto: \"¿cómo fue el último pedido que despacharon?\" en vez de \"¿cómo despachan?\"."),
 ("3.", "Entrevista por separado a un dueño, un vendedor y un almacenero. Filtra la hoja Preguntas por la columna \"Dirigida a\"."),
 ("4.", "Empieza por las preguntas \"★ Imprescindible\"; si el tiempo es corto, deja las \"Normal\" para otra sesión."),
 ("5.", "La columna \"Servicio impactado\" indica qué microservicio se diseña con esa respuesta."),
 ("Qué celdas llenar", None),
 ("", "Solo las celdas con fondo amarillo: Respuesta, Notas / decisiones y Estado (en Preguntas); Recibido y Notas (en Documentos)."),
 ("", "La hoja Resumen se calcula sola con fórmulas: no la edites."),
]
r = 4
for a, b in lines:
    if b is None:
        ins.cell(row=r, column=1, value=a).font = Font(name=FONT, size=12, bold=True, color=navy)
    else:
        ins.cell(row=r, column=1, value=a).font = body
        c = ins.cell(row=r, column=2, value=b); c.font = body; c.alignment = wrap
    r += 1
r += 1
ins.cell(row=r, column=1, value="Ejemplo de una fila respondida").font = Font(name=FONT, size=12, bold=True, color=navy)
r += 1
ex_h = ["Pregunta", "Respuesta", "Notas / decisiones", "Estado"]
ex_v = ["¿Cómo se entera el almacén de que hay un pedido por preparar?",
        "El vendedor manda foto del pedido por WhatsApp al encargado de almacén.",
        "Se pierden pedidos en el chat. Necesitamos bandeja de pendientes en el servicio de Despachos y aviso automático.",
        "Respondida"]
for i, h in enumerate(ex_h):
    c = ins.cell(row=r, column=2 + i, value=h); c.font = hdr_font; c.fill = hdr_fill; c.alignment = center; c.border = border
for i, v in enumerate(ex_v):
    c = ins.cell(row=r + 1, column=2 + i, value=v); c.font = body; c.alignment = wrap; c.border = border
    if i > 0: c.fill = input_fill
ins.row_dimensions[r + 1].height = 60
ins.column_dimensions["A"].width = 5
ins.column_dimensions["B"].width = 55
ins.column_dimensions["C"].width = 40
ins.column_dimensions["D"].width = 45
ins.column_dimensions["E"].width = 14
for rr in range(5, 13):
    ins.merge_cells(start_row=rr, start_column=2, end_row=rr, end_column=5)

# ---------- Preguntas ----------
ws = wb.create_sheet("Preguntas")
heads = ["N°", "Sección", "Pregunta", "Prioridad", "Dirigida a", "Servicio impactado", "Respuesta", "Notas / decisiones", "Estado"]
widths = [6, 26, 60, 16, 12, 18, 45, 40, 13]
for i, (h, w) in enumerate(zip(heads, widths), start=1):
    c = ws.cell(row=1, column=i, value=h); c.font = hdr_font; c.fill = hdr_fill; c.alignment = center; c.border = border
    ws.column_dimensions[c.column_letter].width = w
ws.row_dimensions[1].height = 28
for n, (sec, q, pr, who, svc) in enumerate(Q, start=1):
    row = n + 1
    vals = [n, sec, q, pr, who, svc, None, None, "Pendiente"]
    for i, v in enumerate(vals, start=1):
        c = ws.cell(row=row, column=i, value=v); c.font = body; c.border = border
        c.alignment = center if i in (1, 4, 5, 9) else wrap
        if i in (7, 8, 9): c.fill = input_fill
    if pr == S:
        ws.cell(row=row, column=4).font = Font(name=FONT, size=10, bold=True, color="C00000")
    ws.row_dimensions[row].height = 45
last = len(Q) + 1
ws.freeze_panes = "D2"
ws.auto_filter.ref = f"A1:I{last}"
dv = DataValidation(type="list", formula1='"Pendiente,Respondida,No aplica"', allow_blank=False)
ws.add_data_validation(dv); dv.add(f"I2:I{last}")
green = PatternFill("solid", fgColor="E2EFDA")
ws.conditional_formatting.add(f"I2:I{last}", FormulaRule(formula=['$I2="Respondida"'], fill=green))

# ---------- Documentos ----------
dsh = wb.create_sheet("Documentos")
dh = ["N°", "Documento a pedir", "Recibido", "Notas"]
dw = [6, 60, 12, 45]
for i, (h, w) in enumerate(zip(dh, dw), start=1):
    c = dsh.cell(row=1, column=i, value=h); c.font = hdr_font; c.fill = hdr_fill; c.alignment = center; c.border = border
    dsh.column_dimensions[c.column_letter].width = w
for n, d in enumerate(DOCS, start=1):
    vals = [n, d, "No", None]
    for i, v in enumerate(vals, start=1):
        c = dsh.cell(row=n + 1, column=i, value=v); c.font = body; c.border = border
        c.alignment = center if i in (1, 3) else wrap
        if i in (3, 4): c.fill = input_fill
dlast = len(DOCS) + 1
dv2 = DataValidation(type="list", formula1='"Sí,No"', allow_blank=False)
dsh.add_data_validation(dv2); dv2.add(f"C2:C{dlast}")
dsh.conditional_formatting.add(f"C2:C{dlast}", FormulaRule(formula=['$C2="Sí"'], fill=green))
dsh.freeze_panes = "A2"

# ---------- Resumen ----------
rs = wb.create_sheet("Resumen")
rs.sheet_view.showGridLines = False
rs["A1"] = "Avance de la entrevista"
rs["A1"].font = Font(name=FONT, size=14, bold=True, color=navy)
rh = ["Sección", "Total preguntas", "Imprescindibles", "Respondidas", "% avance"]
rw = [32, 16, 16, 14, 12]
for i, (h, w) in enumerate(zip(rh, rw), start=1):
    c = rs.cell(row=3, column=i, value=h); c.font = hdr_font; c.fill = hdr_fill; c.alignment = center; c.border = border
    rs.column_dimensions[c.column_letter].width = w
sections = []
for s, *_ in Q:
    if s not in sections: sections.append(s)
rng = f"$B$2:$B${last}"
for k, s in enumerate(sections):
    row = 4 + k
    rs.cell(row=row, column=1, value=s)
    rs.cell(row=row, column=2, value=f"=COUNTIF(Preguntas!{rng},A{row})")
    rs.cell(row=row, column=3, value=f'=COUNTIFS(Preguntas!{rng},A{row},Preguntas!$D$2:$D${last},"{S}")')
    rs.cell(row=row, column=4, value=f'=COUNTIFS(Preguntas!{rng},A{row},Preguntas!$I$2:$I${last},"Respondida")+COUNTIFS(Preguntas!{rng},A{row},Preguntas!$I$2:$I${last},"No aplica")')
    rs.cell(row=row, column=5, value=f"=IF(B{row}=0,0,D{row}/B{row})")
tot = 4 + len(sections)
rs.cell(row=tot, column=1, value="Total")
for col in "BCD":
    rs[f"{col}{tot}"] = f"=SUM({col}4:{col}{tot-1})"
rs[f"E{tot}"] = f"=IF(B{tot}=0,0,D{tot}/B{tot})"
for row in range(4, tot + 1):
    for col in range(1, 6):
        c = rs.cell(row=row, column=col); c.border = border
        c.font = bold if row == tot else body
        if col > 1: c.alignment = Alignment(horizontal="center")
    rs.cell(row=row, column=5).number_format = "0%"
for col in range(1, 6):
    rs.cell(row=tot, column=col).fill = PatternFill("solid", fgColor="D9E1F2")
rs.cell(row=tot + 2, column=1, value="Documentos recibidos").font = bold
rs.cell(row=tot + 2, column=2, value=f'=COUNTIF(Documentos!$C$2:$C${dlast},"Sí")&" de "&COUNTA(Documentos!$B$2:$B${dlast})').font = body
rs.cell(row=tot + 3, column=1, value="\"Respondidas\" incluye las marcadas como \"No aplica\".").font = Font(name=FONT, size=9, italic=True, color="595959")

wb.save("Guia_Entrevista_Sistema_Almacen.xlsx")
print(len(Q), "preguntas,", len(sections), "secciones")
