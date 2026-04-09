"""
Generador de Informe General del Dashboard — GeoInventario
Incluye: resumen de movimientos de inventario + pedidos de compra registrados
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.colors import HexColor
from datetime import date
from pathlib import Path
from collections import Counter

AZUL       = HexColor("#1E3A5F")
VERDE      = HexColor("#2ECC71")
NARANJA    = HexColor("#F39C12")
ROJO       = HexColor("#E74C3C")
MORADO     = HexColor("#9B59B6")
GRIS_CLARO = HexColor("#F5F6FA")
GRIS_TEXTO = HexColor("#7F8C8D")
AZUL_CLARO = HexColor("#EBF5FB")
BLANCO     = colors.white


def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("AppTitulo",  fontName="Helvetica-Bold",   fontSize=16, textColor=AZUL,    alignment=TA_CENTER, spaceAfter=6, spaceBefore=0, leading=20))
    s.add(ParagraphStyle("AppSub",     fontName="Helvetica-Bold",   fontSize=11, textColor=VERDE,   alignment=TA_CENTER, spaceAfter=6, spaceBefore=0, leading=14))
    s.add(ParagraphStyle("Seccion",    fontName="Helvetica-Bold",   fontSize=12, textColor=AZUL,    spaceBefore=10, spaceAfter=4))
    s.add(ParagraphStyle("Normal10",   fontName="Helvetica",        fontSize=10, textColor=HexColor("#2C3E50")))
    s.add(ParagraphStyle("Bold10",     fontName="Helvetica-Bold",   fontSize=10))
    s.add(ParagraphStyle("Pie",        fontName="Helvetica-Oblique",fontSize=8,  textColor=GRIS_TEXTO, alignment=TA_CENTER))
    s.add(ParagraphStyle("CeldaHdr",   fontName="Helvetica-Bold",   fontSize=9,  textColor=BLANCO,   alignment=TA_CENTER))
    s.add(ParagraphStyle("CeldaCent",  fontName="Helvetica",        fontSize=9,  textColor=HexColor("#2C3E50"), alignment=TA_CENTER))
    s.add(ParagraphStyle("CeldaLeft",  fontName="Helvetica",        fontSize=9,  textColor=HexColor("#2C3E50"), alignment=TA_LEFT))
    return s


def _encabezado(styles):
    return [
        Paragraph("GEOINVENTARIO", styles["AppTitulo"]),
        Paragraph("INFORME GENERAL — MOVIMIENTOS Y PEDIDOS", styles["AppSub"]),
        HRFlowable(width="100%", thickness=1.5, color=VERDE, spaceAfter=8),
    ]


def _tabla_resumen(movimientos, pedidos, styles, valor_inventario=0.0):
    """Tarjetas de resumen en tabla horizontal."""
    entradas   = sum(1 for m in movimientos if m.tipo == "entrada")
    salidas    = sum(1 for m in movimientos if m.tipo == "salida")
    devoluc    = sum(1 for m in movimientos if m.tipo == "devolucion")
    tot_ped    = len(pedidos)
    items_comp = sum(
        sum(1 for d in p.detalles if not d.en_stock) for p in pedidos
    ) if pedidos else 0

    val_inv_str = f"${valor_inventario:,.0f}"
    data = [
        [
            _card_cell("⬆️ Entradas",       str(entradas),  VERDE,              styles),
            _card_cell("⬇️ Salidas",        str(salidas),   AZUL,               styles),
            _card_cell("↩️ Devoluciones",   str(devoluc),   NARANJA,            styles),
            _card_cell("🛒 Pedidos",         str(tot_ped),   MORADO,             styles),
            _card_cell("🔴 A Comprar",       str(items_comp),ROJO,               styles),
            _card_cell("💰 Valor Inventario",val_inv_str,    HexColor("#16A085"),styles),
        ]
    ]
    t = Table(data, colWidths=[2.65*cm]*6)
    t.setStyle(TableStyle([
        ("ALIGN",   (0,0),(-1,-1), "CENTER"),
        ("VALIGN",  (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING",  (0,0),(-1,-1), 4),
        ("RIGHTPADDING", (0,0),(-1,-1), 4),
    ]))
    return t


def _card_cell(titulo, valor, color, styles):
    from reportlab.platypus import Table as T, TableStyle as TS
    # Adaptive font size: shorter values get bigger font
    val_str = str(valor)
    if len(val_str) <= 4:
        fsize = 18
    elif len(val_str) <= 8:
        fsize = 13
    elif len(val_str) <= 12:
        fsize = 10
    else:
        fsize = 8
    data = [
        [Paragraph(f"<b>{valor}</b>", ParagraphStyle("cv", fontName="Helvetica-Bold", fontSize=fsize, textColor=BLANCO, alignment=TA_CENTER, leading=fsize+2))],
        [Paragraph(titulo, ParagraphStyle("ct", fontName="Helvetica", fontSize=7, textColor=BLANCO, alignment=TA_CENTER, leading=9))],
    ]
    inner = T(data, colWidths=[2.6*cm])
    inner.setStyle(TS([
        ("BACKGROUND",    (0,0),(-1,-1), color),
        ("ROUNDEDCORNERS",[6]),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
    ]))
    return inner


def _tabla_movimientos(movimientos, styles):
    hdrs = ["#", "Tipo", "Proyecto / Proveedor", "Responsable", "Fecha", "Materiales"]
    rows = [[Paragraph(h, styles["CeldaHdr"]) for h in hdrs]]
    tipo_map = {"entrada": "⬆️ Entrada", "salida": "⬇️ Salida", "devolucion": "↩️ Devolución"}
    for i, mv in enumerate(movimientos):
        ref = mv.proyecto.nombre_proyecto if mv.proyecto else (mv.proveedor.nombre if mv.proveedor else "—")
        rows.append([
            Paragraph(str(i+1),                       styles["CeldaCent"]),
            Paragraph(tipo_map.get(mv.tipo, mv.tipo),  styles["CeldaCent"]),
            Paragraph(ref,                             styles["CeldaLeft"]),
            Paragraph(mv.responsable or "—",           styles["CeldaLeft"]),
            Paragraph(str(mv.fecha),                   styles["CeldaCent"]),
            Paragraph(str(len(mv.detalles)),           styles["CeldaCent"]),
        ])

    col_w = [1*cm, 3*cm, 5.5*cm, 4*cm, 2.5*cm, 2.3*cm]
    t = Table(rows, colWidths=col_w)
    cmds = [
        ("BACKGROUND",    (0,0),(-1,0),  AZUL),
        ("GRID",          (0,0),(-1,-1), 0.4, HexColor("#DDE2E8")),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("ALIGN",         (2,1),(3,-1),  "LEFT"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (2,1),(3,-1),  6),
    ]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0,i),(-1,i), AZUL_CLARO))
    t.setStyle(TableStyle(cmds))
    return t


def _tabla_pedidos(pedidos, styles):
    hdrs = ["#", "Fecha", "Solicitante", "Proyecto", "En Stock", "A Comprar"]
    rows = [[Paragraph(h, styles["CeldaHdr"]) for h in hdrs]]
    for i, ped in enumerate(pedidos):
        en_stock  = sum(1 for d in ped.detalles if d.en_stock)
        a_comprar = sum(1 for d in ped.detalles if not d.en_stock)
        rows.append([
            Paragraph(f"PED-{ped.id:04d}",        styles["CeldaCent"]),
            Paragraph(str(ped.fecha),              styles["CeldaCent"]),
            Paragraph(ped.solicitante or "—",      styles["CeldaLeft"]),
            Paragraph(ped.proyecto_nombre or "—",  styles["CeldaLeft"]),
            Paragraph(str(en_stock),               ParagraphStyle("es", fontName="Helvetica-Bold", fontSize=9, textColor=VERDE, alignment=TA_CENTER)),
            Paragraph(str(a_comprar),              ParagraphStyle("ac", fontName="Helvetica-Bold", fontSize=9, textColor=ROJO if a_comprar else VERDE, alignment=TA_CENTER)),
        ])

    col_w = [2*cm, 2.5*cm, 4.5*cm, 4.5*cm, 2.2*cm, 2.2*cm]
    t = Table(rows, colWidths=col_w)
    cmds = [
        ("BACKGROUND",    (0,0),(-1,0),  MORADO),
        ("GRID",          (0,0),(-1,-1), 0.4, HexColor("#DDE2E8")),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("ALIGN",         (2,1),(3,-1),  "LEFT"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (2,1),(3,-1),  6),
    ]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0,i),(-1,i), HexColor("#F5EEF8")))
    t.setStyle(TableStyle(cmds))
    return t


def generar_informe_dashboard(movimientos, pedidos, usuario=None, output_dir=None, valor_inventario=0.0):
    """
    Genera el informe PDF general del dashboard.
    Retorna la ruta del archivo generado.
    """
    styles = _styles()

    if output_dir is None:
        from app.core.config import BASE_DIR
        output_dir = BASE_DIR / "documentos"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    fecha_str = date.today().strftime("%Y%m%d")
    ruta = Path(output_dir) / f"Informe_Dashboard_{fecha_str}.pdf"

    doc = SimpleDocTemplate(
        str(ruta), pagesize=letter,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=2.5*cm, rightMargin=2.5*cm
    )

    story = []
    story += _encabezado(styles)

    # Info generación
    generado_por = usuario.nombre if usuario else "Sistema"
    info_data = [
        ("Generado por:", generado_por),
        ("Fecha del informe:", date.today().strftime("%d/%m/%Y")),
        ("Total movimientos:", str(len(movimientos))),
        ("Total pedidos:", str(len(pedidos))),
        ("💰 Valor total inventario:", f"$ {valor_inventario:,.0f} COP"),
    ]
    tbl_info = Table(
        [[Paragraph(f"<b>{k}</b>", ParagraphStyle("lk", fontName="Helvetica-Bold", fontSize=10)),
          Paragraph(v, ParagraphStyle("lv", fontName="Helvetica", fontSize=10))]
         for k, v in info_data],
        colWidths=[4*cm, 12*cm]
    )
    tbl_info.setStyle(TableStyle([
        ("GRID",        (0,0),(-1,-1), 0.5, HexColor("#DDE2E8")),
        ("BACKGROUND",  (0,0),(0,-1),  GRIS_CLARO),
        ("TOPPADDING",  (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING", (0,0),(-1,-1), 8),
    ]))
    story.append(tbl_info)
    story.append(Spacer(1, 12))

    # Tarjetas resumen
    story.append(Paragraph("Resumen General", styles["Seccion"]))
    story.append(_tabla_resumen(movimientos, pedidos, styles, valor_inventario))
    story.append(Spacer(1, 14))

    # Movimientos
    if movimientos:
        story.append(KeepTogether([
            Paragraph(f"🔄  Movimientos de Inventario ({len(movimientos)} registros)", styles["Seccion"]),
        ]))
        story.append(_tabla_movimientos(movimientos, styles))
        story.append(Spacer(1, 16))
    else:
        story.append(Paragraph("No hay movimientos registrados.", styles["Normal10"]))

    # Pedidos
    if pedidos:
        story.append(PageBreak())
        story.append(KeepTogether([
            Paragraph(f"🛒  Pedidos de Compra ({len(pedidos)} registros)", styles["Seccion"]),
        ]))
        story.append(_tabla_pedidos(pedidos, styles))

        # Detalle de materiales a comprar
        story.append(Spacer(1, 14))
        story.append(Paragraph("📋  Detalle de Materiales a Comprar (todos los pedidos)", styles["Seccion"]))

        conteo = {}
        for ped in pedidos:
            for d in ped.detalles:
                if not d.en_stock:
                    key = (d.nombre_material, d.unidad or "")
                    conteo[key] = conteo.get(key, 0) + d.faltante

        if conteo:
            hdrs_c = ["Material", "Unidad", "Total Faltante"]
            rows_c = [[Paragraph(h, styles["CeldaHdr"]) for h in hdrs_c]]
            for (nombre, unidad), total in sorted(conteo.items(), key=lambda x: -x[1]):
                rows_c.append([
                    Paragraph(nombre, styles["CeldaLeft"]),
                    Paragraph(unidad, styles["CeldaCent"]),
                    Paragraph(f"<b>{total:g}</b>", ParagraphStyle("tf", fontName="Helvetica-Bold", fontSize=10, textColor=ROJO, alignment=TA_CENTER)),
                ])
            tc = Table(rows_c, colWidths=[10*cm, 3*cm, 4.8*cm])
            tc.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,0),  ROJO),
                ("GRID",          (0,0),(-1,-1), 0.4, HexColor("#DDE2E8")),
                ("ALIGN",         (0,0),(-1,-1), "CENTER"),
                ("ALIGN",         (0,1),(0,-1),  "LEFT"),
                ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
                ("TOPPADDING",    (0,0),(-1,-1), 5),
                ("BOTTOMPADDING", (0,0),(-1,-1), 5),
                ("LEFTPADDING",   (0,1),(0,-1),  8),
            ]))
            for i in range(1, len(rows_c)):
                if i % 2 == 0:
                    tc._argW  # access to force table layout
            story.append(tc)
        else:
            story.append(Paragraph("Todos los materiales pedidos estaban en stock.", styles["Normal10"]))
    else:
        story.append(Paragraph("No hay pedidos de compra registrados.", styles["Normal10"]))

    # Pie
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS_TEXTO))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Informe generado por GeoInventario  •  Ing. Mateo Salazar Zapata  •  {date.today().strftime('%d/%m/%Y')}",
        styles["Pie"]
    ))

    doc.build(story)
    return str(ruta)
