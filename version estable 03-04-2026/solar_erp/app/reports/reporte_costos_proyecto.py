"""
Reporte PDF de costos de material por proyecto — GeoInventario
Calcula el costo neto (salidas - devoluciones) según los snapshots guardados
en detalle_movimientos (precio_unitario / valor_total).
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.colors import HexColor
from datetime import date
from pathlib import Path

AZUL = HexColor("#1E3A5F")
VERDE = HexColor("#2ECC71")
GRIS = HexColor("#7F8C8D")
AZUL_CLARO = HexColor("#EBF5FB")
ROJO = HexColor("#E74C3C")


def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("Titulo", fontName="Helvetica-Bold", fontSize=18, textColor=AZUL, alignment=TA_CENTER))
    s.add(ParagraphStyle("Sub", fontName="Helvetica-Bold", fontSize=12, textColor=VERDE, alignment=TA_CENTER))
    s.add(ParagraphStyle("Normal10", fontName="Helvetica", fontSize=10, textColor=HexColor("#2C3E50")))
    s.add(ParagraphStyle("Hdr", fontName="Helvetica-Bold", fontSize=9, textColor=colors.white, alignment=TA_CENTER))
    s.add(ParagraphStyle("C", fontName="Helvetica", fontSize=9, textColor=HexColor("#2C3E50"), alignment=TA_CENTER))
    s.add(ParagraphStyle("L", fontName="Helvetica", fontSize=9, textColor=HexColor("#2C3E50"), alignment=TA_LEFT))
    s.add(ParagraphStyle("R", fontName="Helvetica", fontSize=9, textColor=HexColor("#2C3E50"), alignment=TA_RIGHT))
    return s


def generar_reporte_costos_proyecto(proyecto, filas, total, usuario=None, output_dir=None):
    """
    filas: list[dict] con keys material, unidad, cantidad_neta, costo_neto
    total: float
    Retorna ruta str del PDF.
    """
    styles = _styles()
    if output_dir is None:
        from app.core.config import BASE_DIR
        output_dir = BASE_DIR / "documentos"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    fecha_str = date.today().strftime("%Y%m%d")
    nombre_proy = (proyecto.nombre_proyecto or f"PROY-{proyecto.id}").replace("/", "-").replace("\\", "-")
    ruta = Path(output_dir) / f"Reporte_Costos_{nombre_proy}_{fecha_str}.pdf"

    doc = SimpleDocTemplate(str(ruta), pagesize=letter, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2.2*cm, rightMargin=2.2*cm)
    story = []

    story.append(Paragraph("GEOINVENTARIO", styles["Titulo"]))
    story.append(Paragraph("REPORTE DE COSTOS DE MATERIAL POR PROYECTO", styles["Sub"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=VERDE))
    story.append(Spacer(1, 10))

    cliente = proyecto.cliente.nombre if getattr(proyecto, "cliente", None) else "—"
    generado_por = usuario.nombre if usuario else "Sistema"
    info = [
        ["Proyecto:", proyecto.nombre_proyecto or "—"],
        ["Cliente:", cliente],
        ["Generado por:", generado_por],
        ["Fecha:", date.today().strftime("%d/%m/%Y")],
        ["Costo neto (salidas - devoluciones):", f"${total:,.2f}"],
    ]
    tinfo = Table([[Paragraph(f"<b>{k}</b>", styles["Normal10"]), Paragraph(str(v), styles["Normal10"])] for k, v in info], colWidths=[6*cm, 10*cm])
    tinfo.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#DDE2E8")),
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#F5F6FA")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tinfo)
    story.append(Spacer(1, 12))

    hdrs = ["Material", "Unidad", "Cant. neta", "Costo neto"]
    rows = [[Paragraph(h, styles["Hdr"]) for h in hdrs]]
    for f in filas:
        costo = float(f.get("costo_neto", 0.0) or 0.0)
        costo_style = ParagraphStyle("cr", parent=styles["R"], textColor=(ROJO if costo < 0 else HexColor("#2C3E50")))
        rows.append([
            Paragraph(str(f.get("material", "")), styles["L"]),
            Paragraph(str(f.get("unidad", "")), styles["C"]),
            Paragraph(f"{float(f.get('cantidad_neta', 0.0) or 0.0):g}", styles["C"]),
            Paragraph(f"${costo:,.2f}", costo_style),
        ])

    tbl = Table(rows, colWidths=[8.5*cm, 2.2*cm, 2.8*cm, 2.8*cm])
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#DDE2E8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (2, 1), (3, -1), "RIGHT"),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
    ]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), AZUL_CLARO))
    tbl.setStyle(TableStyle(cmds))
    story.append(tbl)

    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<i>Nota:</i> El costo se calcula con el precio guardado al momento de la salida (snapshot).", ParagraphStyle("nota", fontName="Helvetica-Oblique", fontSize=8, textColor=GRIS, alignment=TA_LEFT)))

    doc.build(story)
    return str(ruta)

