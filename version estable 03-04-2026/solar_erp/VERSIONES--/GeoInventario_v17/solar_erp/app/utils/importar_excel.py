"""
Utilidad para importar materiales desde el archivo Excel de plantilla oficial.
Retorna:
  - items_ok      : list[dict]   — filas válidas listas para insertar
  - errores       : list[str]    — mensajes de error por fila
  - advertencias  : list[str]    — avisos no bloqueantes
"""
from pathlib import Path


def leer_plantilla_excel(ruta_archivo: str):
    try:
        import openpyxl
    except ImportError:
        return [], ["openpyxl no está instalado. Ejecuta: pip install openpyxl"], []

    try:
        wb = openpyxl.load_workbook(ruta_archivo, data_only=True)
    except Exception as e:
        return [], [f"No se pudo abrir el archivo: {e}"], []

    # Buscar hoja de importación
    hoja = None
    for nombre in wb.sheetnames:
        nl = nombre.lower()
        if "importar" in nl or "material" in nl:
            hoja = wb[nombre]
            break
    if hoja is None:
        hoja = wb.active

    # Detectar fila de encabezados (buscar "nombre_material" en primeras 20 filas)
    fila_encabezado = None
    for row in hoja.iter_rows(min_row=1, max_row=20):
        for cell in row:
            if cell.value and "nombre_material" in str(cell.value).lower():
                fila_encabezado = cell.row
                break
        if fila_encabezado:
            break

    if fila_encabezado is None:
        return [], [
            "No se encontró la fila de encabezados. "
            "Asegúrate de usar la plantilla oficial de GeoInventario."
        ], []

    # Mapear columnas por nombre (búsqueda flexible)
    col_map = {}
    for cell in hoja[fila_encabezado]:
        if cell.value:
            col_map[str(cell.value).strip().lower()] = cell.column

    def _col(keyword):
        """Retorna el índice de columna cuyo nombre contiene la keyword."""
        for k, v in col_map.items():
            if keyword in k:
                return v
        return None

    col_nombre    = _col("nombre_material")
    col_categoria = _col("categoria")
    col_unidad    = _col("unidad")
    col_cantidad  = _col("cantidad_actual")
    col_minimo    = _col("stock_minimo")
    col_precio_u  = _col("precio_unitario")
    # precio_total NO se importa — se recalcula internamente
    col_ubicacion = _col("ubicacion")
    col_proveedor = _col("proveedor_nit")
    col_obs       = _col("observaciones")

    if not col_nombre:
        return [], [
            "No se encontró la columna 'nombre_material'. Usa la plantilla oficial."
        ], []

    CATEGORIAS_VALIDAS = {
        "paneles solares", "inversores", "baterías", "baterias",
        "estructuras", "cableado", "protecciones", "herramientas",
        "consumibles", "otros",
    }

    items_ok     = []
    errores      = []
    advertencias = []
    fila_datos   = fila_encabezado + 1

    for row_idx in range(fila_datos, hoja.max_row + 1):

        def val(col):
            if col is None:
                return None
            v = hoja.cell(row=row_idx, column=col).value
            if v is None:
                return None
            return str(v).strip() if not isinstance(v, (int, float)) else v

        nombre    = val(col_nombre)
        categoria = val(col_categoria)
        unidad    = val(col_unidad)
        cantidad  = val(col_cantidad)
        minimo    = val(col_minimo)
        precio_u  = val(col_precio_u)
        ubicacion = val(col_ubicacion)
        proveedor = val(col_proveedor)
        obs       = val(col_obs)

        # Saltar filas vacías o de totales
        if not nombre or str(nombre).upper().startswith("TOTAL"):
            continue

        fila_label   = f"Fila {row_idx}"
        fila_errores = []

        # ── Validar obligatorios ──────────────────────────────────────────────
        if not nombre:
            fila_errores.append(f"{fila_label}: 'nombre_material' es obligatorio.")
        if not categoria:
            advertencias.append(f"{fila_label}: Categoría vacía, se usará 'Otros'.")
            categoria = "Otros"
        elif str(categoria).lower() not in CATEGORIAS_VALIDAS:
            advertencias.append(
                f"{fila_label}: Categoría '{categoria}' no reconocida — se importará tal como está."
            )
        if not unidad:
            advertencias.append(f"{fila_label}: Unidad vacía, se usará 'unidad'.")
            unidad = "unidad"

        # ── Parsear números ───────────────────────────────────────────────────
        def parse_num(raw, campo):
            if raw is None or raw == "":
                return 0.0, None
            try:
                v = float(str(raw).replace(",", ".").replace(" ", ""))
                if v < 0:
                    return 0.0, f"{fila_label}: '{campo}' no puede ser negativo ('{raw}'), se usará 0."
                return v, None
            except (ValueError, TypeError):
                return 0.0, f"{fila_label}: '{campo}' debe ser un número (valor: '{raw}')."

        cantidad_num, err = parse_num(cantidad,  "cantidad_actual");  err and fila_errores.append(err)
        minimo_num,   err = parse_num(minimo,    "stock_minimo");     err and advertencias.append(err)
        precio_u_num, err = parse_num(precio_u,  "precio_unitario");  err and advertencias.append(err)

        # precio_total se calcula internamente (no se lee del Excel)
        precio_total_num = round(precio_u_num * cantidad_num, 2)

        if fila_errores:
            errores.extend(fila_errores)
            continue

        items_ok.append({
            "nombre_material": str(nombre),
            "categoria":       str(categoria) if categoria else "Otros",
            "unidad":          str(unidad),
            "cantidad_actual": cantidad_num,
            "stock_minimo":    minimo_num,
            "precio_unitario": precio_u_num,
            "precio_total":    precio_total_num,   # calculado, informativo
            "ubicacion":       str(ubicacion) if ubicacion else "",
            "proveedor_nit":   str(proveedor).strip() if proveedor else None,
            "observaciones":   str(obs) if obs else "",
        })

    return items_ok, errores, advertencias
