"""
Generador de actas PDF para GeoInventario.
- Acta de Entrada de Materiales
- Acta de Salida de Materiales
- Reporte de Pedido de Material (disponible + a comprar)
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.colors import HexColor
from datetime import date
from pathlib import Path


# ── Colores corporativos ──────────────────────────────────────────────────────
AZUL        = HexColor("#1E3A5F")
VERDE       = HexColor("#2ECC71")
NARANJA     = HexColor("#F39C12")
ROJO        = HexColor("#E74C3C")
GRIS_CLARO  = HexColor("#F5F6FA")
GRIS_TEXTO  = HexColor("#7F8C8D")
BLANCO      = colors.white
AZUL_CLARO  = HexColor("#EBF5FB")


def _base_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("TituloApp",   fontName="Helvetica-Bold",   fontSize=16, textColor=AZUL,    alignment=TA_CENTER, spaceAfter=6, spaceBefore=0, leading=20))
    styles.add(ParagraphStyle("SubtituloApp",fontName="Helvetica-Bold",   fontSize=11, textColor=VERDE,   alignment=TA_CENTER, spaceAfter=6, spaceBefore=0, leading=14))
    styles.add(ParagraphStyle("Seccion",     fontName="Helvetica-Bold",   fontSize=11, textColor=AZUL,    spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle("Normal10",    fontName="Helvetica",        fontSize=10, textColor=HexColor("#2C3E50")))
    styles.add(ParagraphStyle("Pie",         fontName="Helvetica-Oblique",fontSize=8,  textColor=GRIS_TEXTO, alignment=TA_CENTER))
    styles.add(ParagraphStyle("Bold10",      fontName="Helvetica-Bold",   fontSize=10, textColor=HexColor("#2C3E50")))
    styles.add(ParagraphStyle("CeldaHdr",    fontName="Helvetica-Bold",   fontSize=9,  textColor=BLANCO,   alignment=TA_CENTER))
    styles.add(ParagraphStyle("CeldaVal",    fontName="Helvetica",        fontSize=9,  textColor=HexColor("#2C3E50"), alignment=TA_CENTER))
    return styles


def _encabezado(tipo_acta: str, styles) -> list:
    """Retorna los elementos del encabezado común."""
    return [
        Paragraph("GEOINVENTARIO", styles["TituloApp"]),
        Paragraph(tipo_acta, styles["SubtituloApp"]),
        HRFlowable(width="100%", thickness=1.5, color=VERDE, spaceAfter=8),
    ]


def _tabla_info(datos: list[tuple], col_widths=(4*cm, 12*cm)) -> Table:
    """Tabla de 2 columnas con etiqueta y valor."""
    table_data = []
    for etiqueta, valor in datos:
        table_data.append([
            Paragraph(f"<b>{etiqueta}</b>", ParagraphStyle("e", fontName="Helvetica-Bold", fontSize=10)),
            Paragraph(str(valor), ParagraphStyle("v", fontName="Helvetica", fontSize=10)),
        ])
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("GRID",        (0, 0), (-1, -1), 0.5, HexColor("#DDE2E8")),
        ("BACKGROUND",  (0, 0), (0, -1), GRIS_CLARO),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def _tabla_materiales(detalles, mostrar_precio=False, styles=None) -> Table:
    """Tabla de materiales de un movimiento."""
    if styles is None:
        styles = _base_styles()

    hdrs = ["#", "Material", "Unidad", "Cantidad"]
    if mostrar_precio:
        hdrs.append("Precio Unit.")

    header_row = [Paragraph(h, styles["CeldaHdr"]) for h in hdrs]
    rows = [header_row]

    for i, det in enumerate(detalles):
        mat = det.material
        fila = [
            Paragraph(str(i+1), styles["CeldaVal"]),
            Paragraph(mat.nombre_material if mat else "—",
                      ParagraphStyle("ml", fontName="Helvetica", fontSize=10)),
            Paragraph(mat.unidad if mat else "—", styles["CeldaVal"]),
            Paragraph(str(det.cantidad), styles["CeldaVal"]),
        ]
        if mostrar_precio:
            precio = f"${det.precio_unitario:,.2f}" if det.precio_unitario else "—"
            fila.append(Paragraph(precio, styles["CeldaVal"]))
        rows.append(fila)

    if mostrar_precio:
        col_w = [1.2*cm, 7.5*cm, 2*cm, 2.3*cm, 3*cm]
    else:
        col_w = [1.2*cm, 9.5*cm, 2.5*cm, 2.8*cm]

    t = Table(rows, colWidths=col_w)

    style_cmds = [
        ("BACKGROUND",   (0, 0), (-1, 0),  AZUL),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  BLANCO),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("GRID",         (0, 0), (-1, -1), 0.5, HexColor("#DDE2E8")),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("ALIGN",        (1, 1), (1, -1),  "LEFT"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (1, 1), (1, -1),  8),
    ]
    # Filas alternadas
    for i in range(1, len(rows)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), AZUL_CLARO))

    t.setStyle(TableStyle(style_cmds))
    return t


def _firmas(responsable: str) -> Table:
    """Tabla de firmas al pie."""
    data = [
        [Paragraph("<b>Entregado por:</b>",  ParagraphStyle("f", fontName="Helvetica-Bold", fontSize=10, alignment=TA_CENTER)),
         Paragraph("<b>Recibido por:</b>",   ParagraphStyle("f", fontName="Helvetica-Bold", fontSize=10, alignment=TA_CENTER))],
        [Spacer(1, 30), Spacer(1, 30)],
        [Paragraph(f"<u>{responsable or '________________________'}</u>",
                   ParagraphStyle("f2", fontName="Helvetica", fontSize=10, alignment=TA_CENTER)),
         Paragraph("<u>________________________</u>",
                   ParagraphStyle("f2", fontName="Helvetica", fontSize=10, alignment=TA_CENTER))],
    ]
    t = Table(data, colWidths=[8*cm, 8*cm])
    t.setStyle(TableStyle([
        ("ALIGN",  (0,0),(-1,-1), "CENTER"),
        ("VALIGN", (0,0),(-1,-1), "MIDDLE"),
    ]))
    return t


def _pie(styles) -> list:
    fecha_str = date.today().strftime("%d/%m/%Y")
    return [
        Spacer(1, 10),
        HRFlowable(width="100%", thickness=0.5, color=GRIS_TEXTO),
        Spacer(1, 4),
        Paragraph(
            f"Generado por GeoInventario  •  Ing. Mateo Salazar Zapata  •  {fecha_str}",
            styles["Pie"]
        ),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# ACTA DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────
def generar_acta_entrada_pdf(movimiento, proveedor, detalles, responsable, output_dir=None):
    """Genera PDF del acta de entrada de materiales. Retorna ruta del archivo."""
    styles = _base_styles()

    if output_dir is None:
        from app.core.config import BASE_DIR
        output_dir = BASE_DIR / "documentos"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    nombre = f"Acta_Entrada_{movimiento.id}_{date.today().strftime('%Y%m%d')}.pdf"
    ruta = Path(output_dir) / nombre

    doc = SimpleDocTemplate(
        str(ruta), pagesize=letter,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=2.5*cm, rightMargin=2.5*cm
    )

    story = []
    story += _encabezado("ACTA DE ENTRADA DE MATERIALES", styles)

    datos_info = [
        ("N° Acta:",        f"ENT-{movimiento.id:04d}"),
        ("Proveedor:",      proveedor.nombre if proveedor else "—"),
        ("NIT / CC:",       proveedor.nit if proveedor else "—"),
        ("Factura:",        movimiento.factura or "—"),
        ("Fecha:",          str(movimiento.fecha or date.today())),
        ("Responsable:",    responsable or movimiento.responsable or "—"),
    ]
    if movimiento.observaciones:
        datos_info.append(("Observaciones:", movimiento.observaciones))

    story.append(_tabla_info(datos_info))
    story.append(Spacer(1, 14))
    story.append(Paragraph("Materiales Recibidos", styles["Seccion"]))
    story.append(_tabla_materiales(detalles, mostrar_precio=True, styles=styles))
    story.append(Spacer(1, 20))
    story.append(_firmas(responsable or movimiento.responsable))
    story += _pie(styles)

    doc.build(story)
    return str(ruta)


# ─────────────────────────────────────────────────────────────────────────────
# ACTA DE SALIDA
# ─────────────────────────────────────────────────────────────────────────────
def generar_acta_salida_pdf(movimiento, proyecto, cliente, detalles, responsable, output_dir=None):
    """Genera PDF del acta de salida/entrega de materiales. Retorna ruta del archivo."""
    styles = _base_styles()

    if output_dir is None:
        from app.core.config import BASE_DIR
        output_dir = BASE_DIR / "documentos"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    nombre = f"Acta_Salida_{movimiento.id}_{date.today().strftime('%Y%m%d')}.pdf"
    ruta = Path(output_dir) / nombre

    doc = SimpleDocTemplate(
        str(ruta), pagesize=letter,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=2.5*cm, rightMargin=2.5*cm
    )

    story = []
    story += _encabezado("ACTA DE ENTREGA DE MATERIALES", styles)

    datos_info = [
        ("N° Acta:",        f"SAL-{movimiento.id:04d}"),
        ("Proyecto:",       proyecto.nombre_proyecto if proyecto else "—"),
        ("Cliente:",        cliente.nombre if cliente else "—"),
        ("Dirección:",      proyecto.direccion if proyecto else "—"),
        ("Fecha:",          str(movimiento.fecha or date.today())),
        ("Responsable:",    responsable or movimiento.responsable or "—"),
    ]
    if movimiento.observaciones:
        datos_info.append(("Observaciones:", movimiento.observaciones))

    story.append(_tabla_info(datos_info))
    story.append(Spacer(1, 14))
    story.append(Paragraph("Materiales Entregados", styles["Seccion"]))
    story.append(_tabla_materiales(detalles, mostrar_precio=False, styles=styles))
    story.append(Spacer(1, 20))
    story.append(_firmas(responsable or movimiento.responsable))
    story += _pie(styles)

    doc.build(story)
    return str(ruta)


# ─────────────────────────────────────────────────────────────────────────────
# ACTA DE DEVOLUCIÓN
# ─────────────────────────────────────────────────────────────────────────────
def generar_acta_devolucion_pdf(movimiento, proyecto, cliente, detalles, responsable, output_dir=None):
    """Genera PDF del acta de devolución de materiales. Retorna ruta del archivo."""
    styles = _base_styles()

    if output_dir is None:
        from app.core.config import BASE_DIR
        output_dir = BASE_DIR / "documentos"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    nombre = f"Acta_Devolucion_{movimiento.id}_{date.today().strftime('%Y%m%d')}.pdf"
    ruta = Path(output_dir) / nombre

    doc = SimpleDocTemplate(
        str(ruta), pagesize=letter,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=2.5*cm, rightMargin=2.5*cm
    )

    story = []
    story += _encabezado("ACTA DE DEVOLUCIÓN DE MATERIALES", styles)

    datos_info = [
        ("N° Acta:",      f"DEV-{movimiento.id:04d}"),
        ("Proyecto:",     proyecto.nombre_proyecto if proyecto else "—"),
        ("Cliente:",      cliente.nombre if cliente else "—"),
        ("Dirección:",    proyecto.direccion if proyecto else "—"),
        ("Fecha:",        str(movimiento.fecha or date.today())),
        ("Responsable:",  responsable or movimiento.responsable or "—"),
    ]
    if movimiento.observaciones:
        datos_info.append(("Motivo / Obs.:", movimiento.observaciones))

    story.append(_tabla_info(datos_info))
    story.append(Spacer(1, 14))

    # Encabezado de sección con color naranja para diferenciar de salidas
    from reportlab.platypus import Paragraph as P
    story.append(P("Materiales Devueltos al Almacén",
                   ParagraphStyle("sec_dev", fontName="Helvetica-Bold", fontSize=11,
                                  textColor=HexColor("#F39C12"), spaceBefore=4, spaceAfter=6)))
    story.append(_tabla_materiales(detalles, mostrar_precio=False, styles=styles))
    story.append(Spacer(1, 20))

    # Nota informativa
    nota = P("Nota: Los materiales listados han sido devueltos al inventario y el stock ha sido actualizado.",
             ParagraphStyle("nota", fontName="Helvetica-Oblique", fontSize=9,
                            textColor=HexColor("#7F8C8D")))
    story.append(nota)
    story.append(Spacer(1, 16))

    story.append(_firmas(responsable or movimiento.responsable))
    story += _pie(styles)

    doc.build(story)
    return str(ruta)


# ─────────────────────────────────────────────────────────────────────────────
# REPORTE DE PEDIDO DE MATERIAL
# ─────────────────────────────────────────────────────────────────────────────
def generar_reporte_pedido_pdf(
    nombre_solicitante: str,
    proyecto_nombre: str,
    items_disponibles: list,   # list of dict: {nombre, unidad, solicitado, disponible}
    items_comprar: list,       # list of dict: {nombre, unidad, solicitado, disponible, faltante}
    observaciones: str = "",
    output_dir=None
):
    """
    Genera reporte PDF de pedido de material:
    - Tabla de materiales disponibles en stock
    - Tabla de materiales a comprar (sin stock suficiente)
    Retorna la ruta del archivo PDF generado.
    """
    styles = _base_styles()

    if output_dir is None:
        from app.core.config import BASE_DIR
        output_dir = BASE_DIR / "documentos"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    fecha_str = date.today().strftime("%Y%m%d")
    nombre = f"Pedido_{proyecto_nombre.replace(' ', '_')}_{fecha_str}.pdf"
    ruta = Path(output_dir) / nombre

    doc = SimpleDocTemplate(
        str(ruta), pagesize=letter,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=2.5*cm, rightMargin=2.5*cm
    )

    story = []
    story += _encabezado("REPORTE DE PEDIDO DE MATERIAL", styles)

    # Info del pedido
    datos_info = [
        ("Proyecto:",       proyecto_nombre or "—"),
        ("Solicitante:",    nombre_solicitante or "—"),
        ("Fecha:",          date.today().strftime("%d/%m/%Y")),
        ("Total ítems:",    str(len(items_disponibles) + len(items_comprar))),
    ]
    if observaciones:
        datos_info.append(("Observaciones:", observaciones))
    story.append(_tabla_info(datos_info))
    story.append(Spacer(1, 14))

    # ── Resumen visual ────────────────────────────────────────────────────────
    resumen_data = [
        [
            Paragraph("<b>Materiales en stock</b>", ParagraphStyle("rs", fontName="Helvetica-Bold", fontSize=11, textColor=BLANCO, alignment=TA_CENTER)),
            Paragraph("<b>Materiales a comprar</b>", ParagraphStyle("rc", fontName="Helvetica-Bold", fontSize=11, textColor=BLANCO, alignment=TA_CENTER)),
        ],
        [
            Paragraph(str(len(items_disponibles)), ParagraphStyle("rn", fontName="Helvetica-Bold", fontSize=22, textColor=BLANCO, alignment=TA_CENTER)),
            Paragraph(str(len(items_comprar)),     ParagraphStyle("rn2", fontName="Helvetica-Bold", fontSize=22, textColor=BLANCO, alignment=TA_CENTER)),
        ],
    ]
    t_resumen = Table(resumen_data, colWidths=[8*cm, 8*cm])
    t_resumen.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), VERDE),
        ("BACKGROUND",    (1, 0), (1, -1), ROJO),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(t_resumen)
    story.append(Spacer(1, 16))

    # ── Tabla materiales disponibles ──────────────────────────────────────────
    if items_disponibles:
        story.append(KeepTogether([
            Paragraph("✅  Materiales Disponibles en Stock", styles["Seccion"]),
            _tabla_pedido(items_disponibles, color_estado=VERDE, mostrar_faltante=False, styles=styles),
        ]))
        story.append(Spacer(1, 14))

    # ── Tabla materiales a comprar ────────────────────────────────────────────
    if items_comprar:
        story.append(KeepTogether([
            Paragraph("🛒  Materiales a Comprar (sin stock suficiente)", styles["Seccion"]),
            _tabla_pedido(items_comprar, color_estado=ROJO, mostrar_faltante=True, styles=styles),
        ]))
        story.append(Spacer(1, 14))

    if not items_disponibles and not items_comprar:
        story.append(Paragraph("No se seleccionaron materiales.", styles["Normal10"]))

    story += _pie(styles)

    doc.build(story)
    return str(ruta)


def _tabla_pedido(items: list, color_estado, mostrar_faltante: bool, styles) -> Table:
    """Tabla para el reporte de pedido."""
    hdrs = ["#", "Material", "Unidad", "Solicitado", "En Stock"]
    if mostrar_faltante:
        hdrs.append("A Comprar")

    header_row = [Paragraph(h, styles["CeldaHdr"]) for h in hdrs]
    rows = [header_row]

    for i, it in enumerate(items):
        fila = [
            Paragraph(str(i+1), styles["CeldaVal"]),
            Paragraph(str(it.get("nombre", "—")), ParagraphStyle("ml2", fontName="Helvetica", fontSize=10)),
            Paragraph(str(it.get("unidad", "—")), styles["CeldaVal"]),
            Paragraph(str(it.get("solicitado", 0)), styles["CeldaVal"]),
            Paragraph(str(it.get("disponible", 0)), styles["CeldaVal"]),
        ]
        if mostrar_faltante:
            faltante = it.get("faltante", 0)
            fila.append(
                Paragraph(f"<b>{faltante}</b>",
                          ParagraphStyle("falt", fontName="Helvetica-Bold", fontSize=10,
                                         textColor=ROJO, alignment=TA_CENTER))
            )
        rows.append(fila)

    if mostrar_faltante:
        col_w = [1.2*cm, 6.5*cm, 2*cm, 2.3*cm, 2.3*cm, 2.7*cm]
    else:
        col_w = [1.2*cm, 8*cm, 2.5*cm, 2.8*cm, 2.5*cm]

    t = Table(rows, colWidths=col_w)

    style_cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0), AZUL),
        ("TEXTCOLOR",     (0, 0), (-1, 0), BLANCO),
        ("GRID",          (0, 0), (-1, -1), 0.5, HexColor("#DDE2E8")),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("ALIGN",         (1, 1), (1, -1),  "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (1, 1), (1, -1),  8),
    ]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), AZUL_CLARO))
    # Colorear columna "A Comprar"
    if mostrar_faltante:
        for i in range(1, len(rows)):
            style_cmds.append(("BACKGROUND", (-1, i), (-1, i), HexColor("#FDECEA")))

    t.setStyle(TableStyle(style_cmds))
    return t
