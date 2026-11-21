"""Build the product template (Excel) that the business fills in for the import (HU-10, N-04).

Run from the repo root:
    uv run --with openpyxl python docs/plantillas/build_plantilla_productos.py

Sheets follow the data model in docs/03 (producto, presentacion, precio_escala,
ubicacion, stock.stock_minimo). Example rows are fictitious and shaded grey.
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

OUTPUT = Path(__file__).with_name("Plantilla_Productos.xlsx")
MAX_ROWS = 2000

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(bold=True, color="FFFFFF")
REQUIRED_FILL = PatternFill("solid", fgColor="C00000")
EXAMPLE_FILL = PatternFill("solid", fgColor="E7E6E6")
EXAMPLE_FONT = Font(italic=True, color="595959")

INSTRUCTIONS = [
    ("Plantilla de productos", True),
    ("Llenen esta plantilla para cargar los productos al sistema. No cambien los nombres de las hojas ni de las columnas.", False),
    ("", False),
    ("Orden recomendado", True),
    ("1. Ubicaciones: las tiendas y almacenes (una fila por lugar).", False),
    ("2. Productos: una fila por producto, con su SKU (código interno único).", False),
    ("3. Presentaciones: cómo se vende cada producto (unidad, caja, docena…) y cuántas unidades base trae.", False),
    ("4. Precios: el precio de cada presentación según la cantidad que se compre.", False),
    ("5. Stock mínimo: desde qué cantidad avisar que queda poco, por producto y ubicación (opcional).", False),
    ("", False),
    ("Reglas importantes", True),
    ("• Las columnas con encabezado ROJO son obligatorias; las azules, opcionales.", False),
    ("• Las filas grises son EJEMPLOS ficticios: bórrenlas antes de enviar el archivo.", False),
    ("• El SKU une todas las hojas: escríbanlo exactamente igual en cada hoja.", False),
    ("• Unidad base = la unidad más pequeña en que se cuenta el stock (ej. un lapicero, una hoja, un metro). El stock siempre se guarda en esa unidad.", False),
    ("• Factor = cuántas unidades base trae la presentación (caja de 12 → 12). La presentación de la unidad base lleva factor 1.", False),
    ("• Cantidades y factores son números enteros (sin decimales).", False),
    ("• Los precios incluyen IGV, en soles, con máximo 2 decimales.", False),
    ("• Cada presentación necesita al menos un precio 'desde 1'. Si hay precio por mayor, agreguen otra fila (ej. desde 12).", False),
    ("• El costo es opcional y confidencial: solo lo verá el dueño en el sistema.", False),
    ("• Variantes (color, tamaño): por ahora, cada variante es un producto con su propio SKU.", False),
    ("", False),
    ("El inventario inicial (cuántas unidades hay) NO va aquí: se carga en diciembre con el conteo físico de cada ubicación.", True),
]

# (title, required, width, comment)
SHEETS = {
    "Ubicaciones": [
        ("Nombre", True, 28, "Nombre corto y único, ej. Tienda Centro"),
        ("Tipo", True, 14, "TIENDA o ALMACEN"),
        ("Dirección", False, 40, None),
    ],
    "Productos": [
        ("SKU", True, 16, "Código interno único del producto"),
        ("Código de barras", False, 18, "El del fabricante, si tiene"),
        ("Nombre", True, 40, None),
        ("Categoría", True, 20, "Ej. Escritura, Papelería, Arte"),
        ("Marca", False, 18, None),
        ("Unidad base", True, 14, "UNIDAD, HOJA, METRO… La unidad más pequeña en que se cuenta"),
        ("Costo por unidad base (S/)", False, 22, "Opcional y confidencial"),
        ("Activo", True, 10, "SI o NO"),
    ],
    "Presentaciones": [
        ("SKU", True, 16, "El mismo SKU de la hoja Productos"),
        ("Presentación", True, 18, "UNIDAD, CAJA, DOCENA, PAQUETE…"),
        ("Factor", True, 10, "Unidades base que trae (caja de 12 → 12)"),
        ("Código de barras", False, 18, "Si la presentación tiene su propio código"),
    ],
    "Precios": [
        ("SKU", True, 16, None),
        ("Presentación", True, 18, "Igual que en la hoja Presentaciones"),
        ("Desde cantidad", True, 16, "Desde cuántas presentaciones aplica este precio"),
        ("Precio con IGV (S/)", True, 18, "Precio de UNA presentación"),
    ],
    "Stock mínimo": [
        ("SKU", True, 16, None),
        ("Ubicación", True, 28, "Igual que en la hoja Ubicaciones"),
        ("Stock mínimo (unidades base)", True, 26, "Avisar cuando el disponible baje de esta cantidad"),
    ],
}

EXAMPLES = {
    "Ubicaciones": [("Tienda Ejemplo", "TIENDA", "Av. Ficticia 123"), ("Almacén Ejemplo", "ALMACEN", "")],
    "Productos": [
        ("EJ-0001", "7750000000017", "Lapicero azul punta fina", "Escritura", "Marca Ejemplo", "UNIDAD", 0.45, "SI"),
        ("EJ-0002", "", "Cuaderno cuadriculado A4 100 hojas", "Papelería", "Marca Ejemplo", "UNIDAD", 3.10, "SI"),
    ],
    "Presentaciones": [
        ("EJ-0001", "UNIDAD", 1, ""),
        ("EJ-0001", "CAJA", 12, "7750000000024"),
        ("EJ-0002", "UNIDAD", 1, ""),
        ("EJ-0002", "PAQUETE", 5, ""),
    ],
    "Precios": [
        ("EJ-0001", "UNIDAD", 1, 1.00),
        ("EJ-0001", "UNIDAD", 12, 0.90),
        ("EJ-0001", "CAJA", 1, 10.00),
        ("EJ-0002", "UNIDAD", 1, 5.50),
        ("EJ-0002", "PAQUETE", 1, 26.00),
    ],
    "Stock mínimo": [("EJ-0001", "Tienda Ejemplo", 24), ("EJ-0002", "Almacén Ejemplo", 50)],
}


def add_list(ws, column: str, values: str, prompt: str) -> None:
    """Dropdown on a column; other values are rejected."""
    rule = DataValidation(type="list", formula1=f'"{values}"', allow_blank=True)
    rule.error, rule.errorTitle, rule.prompt = f"Use: {values}", "Valor no válido", prompt
    ws.add_data_validation(rule)
    rule.add(f"{column}2:{column}{MAX_ROWS}")


def add_number(ws, column: str, kind: str, minimum: float, message: str) -> None:
    """Accept only whole or decimal numbers above a minimum on a column."""
    rule = DataValidation(type=kind, operator="greaterThanOrEqual", formula1=str(minimum))
    rule.allow_blank = True
    rule.error, rule.errorTitle = message, "Número no válido"
    ws.add_data_validation(rule)
    rule.add(f"{column}2:{column}{MAX_ROWS}")


def build() -> None:
    """Write the workbook with instructions, one sheet per entity, examples and validations."""
    wb = Workbook()
    intro = wb.active
    intro.title = "Instrucciones"
    intro.column_dimensions["A"].width = 120
    for row, (text, bold) in enumerate(INSTRUCTIONS, start=1):
        cell = intro.cell(row=row, column=1, value=text)
        cell.font = Font(bold=bold, size=14 if row == 1 else 11)
        cell.alignment = Alignment(wrap_text=True, vertical="top")

    for name, columns in SHEETS.items():
        ws = wb.create_sheet(name)
        ws.freeze_panes = "A2"
        for col, (title, required, width, comment) in enumerate(columns, start=1):
            cell = ws.cell(row=1, column=col, value=title)
            cell.fill = REQUIRED_FILL if required else HEADER_FILL
            cell.font = HEADER_FONT
            cell.alignment = Alignment(wrap_text=True, vertical="center")
            if comment:
                cell.comment = Comment(comment, "Sistema")
            ws.column_dimensions[cell.column_letter].width = width
        for row, values in enumerate(EXAMPLES[name], start=2):
            for col, value in enumerate(values, start=1):
                cell = ws.cell(row=row, column=col, value=value)
                cell.fill, cell.font = EXAMPLE_FILL, EXAMPLE_FONT

    add_list(wb["Ubicaciones"], "B", "TIENDA,ALMACEN", "TIENDA o ALMACEN")
    add_list(wb["Productos"], "H", "SI,NO", "SI o NO")
    add_number(wb["Productos"], "G", "decimal", 0, "El costo debe ser un número mayor o igual a 0")
    add_number(wb["Presentaciones"], "C", "whole", 1, "El factor debe ser un entero mayor o igual a 1")
    add_number(wb["Precios"], "C", "whole", 1, "La cantidad debe ser un entero mayor o igual a 1")
    add_number(wb["Precios"], "D", "decimal", 0.01, "El precio debe ser mayor a 0")
    add_number(wb["Stock mínimo"], "C", "whole", 0, "El stock mínimo debe ser un entero mayor o igual a 0")
    for sheet, column in (("Productos", "G"), ("Precios", "D")):
        for row in range(2, MAX_ROWS + 1):
            wb[sheet][f"{column}{row}"].number_format = "0.00"

    wb.save(OUTPUT)
    print(f"Plantilla creada: {OUTPUT}")


if __name__ == "__main__":
    build()
