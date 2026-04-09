"""
Reporte PDF de Alertas de Stock Bajo — GeoInventario
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

AZUL       = HexColor("#1E3A5F")
VERDE      = HexColor("#2ECC71")
NARANJA    = HexColor("#F39C12")
ROJO       = HexColor("#E74C3C")
ROJO_CLA   = HexColor("#FDEDEC")
AMARILLO   = HexColor("#FFF3CD")
GRIS_CLA   = HexColor("#F5F6FA")
GRIS_TXT   = HexColor("#7F8C8D")
BLANCO     = colors.white
VERDE_OCS  = HexColor("#27AE60")


def generar_alertas_stock_pdf(materiales_alerta, valor_inventario=0.0, usuario=None, output_dir=None):
    """
    Genera un PDF con los materiales que tienen stock bajo o en cero.
    materiales_alerta: lista de objetos Material con cantidad_actual <= stock_minimo
    """
    if output_dir is None:
        from app.core.config import BASE_DIR
        output_dir = BASE_DIR / "documentos"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    fecha_str = date.today().strftime("%Y%m%d")
    ruta = Path(output_dir) / f"Alertas_Stock_{fecha_str}.pdf"

    doc = SimpleDocTemplate(
        str(ruta), pagesize=letter,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        leftMargin=2*cm, rightMargin=2*cm
    )

    styles = getSampleStyleSheet()
    ST = {
        "titulo":  ParagraphStyle("t",  fontName="Helvetica-Bold",   fontSize=16, textColor=AZUL,    alignment=TA_CENTER, spaceAfter=6, spaceBefore=0, leading=20),
        "sub":     ParagraphStyle("s",  fontName="Helvetica-Bold",   fontSize=11, textColor=ROJO,    alignment=TA_CENTER, spaceAfter=6, spaceBefore=0, leading=14),
        "seccion": ParagraphStyle("se", fontName="Helvetica-Bold",   fontSize=11, textColor=AZUL,    spaceBefore=10, spaceAfter=4),
        "normal":  ParagraphStyle("n",  fontName="Helvetica",        fontSize=10, textColor=HexColor("#2C3E50")),
        "pie":     ParagraphStyle("p",  fontName="Helvetica-Oblique",fontSize=8,  textColor=GRIS_TXT, alignment=TA_CENTER),
        "hdr":     ParagraphStyle("h",  fontName="Helvetica-Bold",   fontSize=9,  textColor=BLANCO,   alignment=TA_CENTER),
        "cel_c":   ParagraphStyle("cc", fontName="Helvetica",        fontSize=9,  textColor=HexColor("#2C3E50"), alignment=TA_CENTER),
        "cel_l":   ParagraphStyle("cl", fontName="Helvetica",        fontSize=9,  textColor=HexColor("#2C3E50"), alignment=TA_LEFT),
        "cel_r":   ParagraphStyle("cr", fontName="Helvetica",        fontSize=9,  textColor=HexColor("#2C3E50"), alignment=TA_RIGHT),
        "rojo_b":  ParagraphStyle("rb", fontName="Helvetica-Bold",   fontSize=9,  textColor=ROJO,     alignment=TA_CENTER),
        "verd_b":  ParagraphStyle("vb", fontName="Helvetica-Bold",   fontSize=9,  textColor=VERDE_OCS,alignment=TA_CENTER),
    }

    story = []

    # ── Encabezado ─────────────────────────────────────────────────────────
    story.append(Paragraph("GEOINVENTARIO", ST["titulo"]))
    story.append(Paragraph("ALERTA DE STOCK BAJO — MATERIALES CRÍTICOS", ST["sub"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ROJO, spaceAfter=8))

    # ── Info generación ───────────────────────────────────────────────────
    generado_por = usuario.nombre if usuario else "Sistema"
    en_cero    = [m for m in materiales_alerta if (m.cantidad_actual or 0) == 0]
    bajo_min   = [m for m in materiales_alerta if 0 < (m.cantidad_actual or 0) <= m.stock_minimo]

    info_data = [
        ("Generado por:",          generado_por),
        ("Fecha del informe:",     date.today().strftime("%d/%m/%Y")),
        ("Total alertas:",         f"{len(materiales_alerta)} materiales"),
        ("Stock en CERO:",         f"{len(en_cero)} materiales — requieren reposición inmediata"),
        ("Stock bajo mínimo:",     f"{len(bajo_min)} materiales — por debajo del umbral"),
        ("Valor total inventario:", f"$ {valor_inventario:,.0f} COP"),
    ]
    tbl_info = Table(
        [[Paragraph(f"<b>{k}</b>", ParagraphStyle("lk", fontName="Helvetica-Bold", fontSize=9, textColor=AZUL)),
          Paragraph(v, ParagraphStyle("lv", fontName="Helvetica", fontSize=9))]
         for k, v in info_data],
        colWidths=[4.5*cm, 12*cm]
    )
    tbl_info.setStyle(TableStyle([
        ("GRID",         (0,0),(-1,-1), 0.4, HexColor("#DDE2E8")),
        ("BACKGROUND",   (0,0),(0,-1),  GRIS_CLA),
        ("BACKGROUND",   (0,3),(1,3),   ROJO_CLA),
        ("TOPPADDING",   (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
    ]))
    story.append(tbl_info)
    story.append(Spacer(1, 14))

    # ── Tarjetas resumen ──────────────────────────────────────────────────
    def card(titulo, valor, color):
        from reportlab.platypus import Table as T, TableStyle as TS
        val_str = str(valor)
        if len(val_str) <= 4:
            fsize = 20
        elif len(val_str) <= 8:
            fsize = 14
        elif len(val_str) <= 12:
            fsize = 10
        else:
            fsize = 8
        data = [
            [Paragraph(f"<b>{valor}</b>", ParagraphStyle("cv", fontName="Helvetica-Bold", fontSize=fsize, textColor=BLANCO, alignment=TA_CENTER, leading=fsize+2))],
            [Paragraph(titulo, ParagraphStyle("ct", fontName="Helvetica", fontSize=7, textColor=BLANCO, alignment=TA_CENTER, leading=9))],
        ]
        inner = T(data, colWidths=[4.0*cm])
        inner.setStyle(TS([
            ("BACKGROUND",    (0,0),(-1,-1), color),
            ("ROUNDEDCORNERS",[6]),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ]))
        return inner

    cards_data = [[
        card("🔴 Stock en CERO",    str(len(en_cero)),               ROJO),
        card("⚠️ Bajo mínimo",      str(len(bajo_min)),              NARANJA),
        card("📦 Total alertas",    str(len(materiales_alerta)),     AZUL),
        card("💰 Valor inventario", f"${valor_inventario:,.0f}",     HexColor("#16A085")),
    ]]
    tbl_cards = Table(cards_data, colWidths=[4.1*cm]*4)
    tbl_cards.setStyle(TableStyle([
        ("ALIGN", (0,0),(-1,-1), "CENTER"),
        ("LEFTPADDING",  (0,0),(-1,-1), 3),
        ("RIGHTPADDING", (0,0),(-1,-1), 3),
    ]))
    story.append(tbl_cards)
    story.append(Spacer(1, 16))

    # ── Tabla: Stock en CERO ──────────────────────────────────────────────
    if en_cero:
        story.append(KeepTogether([
            Paragraph("🔴  Materiales con STOCK EN CERO — Reposición Inmediata", ST["seccion"]),
        ]))
        _tabla_alertas(story, en_cero, ROJO, ROJO_CLA, ST)
        story.append(Spacer(1, 14))

    # ── Tabla: Stock bajo mínimo ──────────────────────────────────────────
    if bajo_min:
        story.append(KeepTogether([
            Paragraph("⚠️  Materiales con Stock Bajo el Mínimo", ST["seccion"]),
        ]))
        _tabla_alertas(story, bajo_min, NARANJA, AMARILLO, ST)

    # ── Pie ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS_TXT))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Reporte de Alertas de Stock  •  GeoInventario  •  Ing. Mateo Salazar Zapata  •  {date.today().strftime('%d/%m/%Y')}",
        ST["pie"]
    ))

    doc.build(story)
    return str(ruta)


def _tabla_alertas(story, materiales, color_hdr, color_alt, ST):
    hdrs = ["#", "Material", "Categoría", "Stock Actual", "Stock Mín.", "Unidad", "Precio Unit.", "Valor Total"]
    rows = [[Paragraph(h, ST["hdr"]) for h in hdrs]]

    for i, m in enumerate(sorted(materiales, key=lambda x: x.cantidad_actual or 0)):
        actual = m.cantidad_actual or 0
        minimo = m.stock_minimo or 0
        precio = m.precio_unitario or 0
        total  = actual * precio

        est_style = ParagraphStyle("es", fontName="Helvetica-Bold", fontSize=9,
            textColor=ROJO if actual == 0 else NARANJA, alignment=TA_CENTER)

        rows.append([
            Paragraph(str(i + 1),                   ST["cel_c"]),
            Paragraph(m.nombre_material,             ST["cel_l"]),
            Paragraph(m.categoria or "—",            ST["cel_c"]),
            Paragraph(f"{actual:g}",                 est_style),
            Paragraph(f"{minimo:g}",                 ST["cel_c"]),
            Paragraph(m.unidad or "—",               ST["cel_c"]),
            Paragraph(f"$ {precio:,.0f}",            ST["cel_r"]),
            Paragraph(f"$ {total:,.0f}",             ST["cel_r"]),
        ])

    col_w = [0.7*cm, 5.5*cm, 2.5*cm, 1.8*cm, 1.8*cm, 1.5*cm, 2.4*cm, 2.4*cm]
    t = Table(rows, colWidths=col_w)
    cmds = [
        ("BACKGROUND",    (0,0), (-1,0),  color_hdr),
        ("GRID",          (0,0), (-1,-1), 0.4, HexColor("#DDE2E8")),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("ALIGN",         (1,1), (1,-1),  "LEFT"),
        ("ALIGN",         (6,1), (7,-1),  "RIGHT"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (1,1), (1,-1),  6),
        ("RIGHTPADDING",  (6,1), (7,-1),  6),
    ]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0,i), (-1,i), color_alt))
    t.setStyle(TableStyle(cmds))
    story.append(t)
