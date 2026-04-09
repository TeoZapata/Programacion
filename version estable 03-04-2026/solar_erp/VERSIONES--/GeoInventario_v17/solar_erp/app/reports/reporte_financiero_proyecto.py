"""
Reporte PDF financiero por proyecto — GeoInventario
Muestra salidas, devoluciones, valor neto y detalle de materiales por proyecto.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.colors import HexColor
from datetime import date
from pathlib import Path

AZUL      = HexColor("#1E3A5F")
AZUL_MED  = HexColor("#2980B9")
VERDE     = HexColor("#2ECC71")
VERDE_OSC = HexColor("#27AE60")
NARANJA   = HexColor("#F39C12")
ROJO      = HexColor("#E74C3C")
MORADO    = HexColor("#9B59B6")
GRIS_CLA  = HexColor("#F5F6FA")
GRIS_TXT  = HexColor("#7F8C8D")
TEAL      = HexColor("#16A085")
BLANCO    = colors.white
AZUL_CLA  = HexColor("#EBF5FB")
VERDE_CLA = HexColor("#E8F8F0")


def _ST():
    """Diccionario de estilos de párrafo."""
    return {
        "titulo":  ParagraphStyle("ti", fontName="Helvetica-Bold",   fontSize=16, textColor=AZUL,    alignment=TA_CENTER, spaceAfter=6, leading=20),
        "sub":     ParagraphStyle("su", fontName="Helvetica-Bold",   fontSize=11, textColor=VERDE,   alignment=TA_CENTER, spaceAfter=6, leading=14),
        "seccion": ParagraphStyle("se", fontName="Helvetica-Bold",   fontSize=11, textColor=AZUL,    spaceBefore=10, spaceAfter=4),
        "normal":  ParagraphStyle("no", fontName="Helvetica",        fontSize=10, textColor=HexColor("#2C3E50")),
        "pie":     ParagraphStyle("pi", fontName="Helvetica-Oblique",fontSize=8,  textColor=GRIS_TXT, alignment=TA_CENTER),
        "hdr":     ParagraphStyle("hd", fontName="Helvetica-Bold",   fontSize=9,  textColor=BLANCO,   alignment=TA_CENTER),
        "cel_c":   ParagraphStyle("cc", fontName="Helvetica",        fontSize=9,  textColor=HexColor("#2C3E50"), alignment=TA_CENTER),
        "cel_l":   ParagraphStyle("cl", fontName="Helvetica",        fontSize=9,  textColor=HexColor("#2C3E50"), alignment=TA_LEFT),
        "cel_r":   ParagraphStyle("cr", fontName="Helvetica",        fontSize=9,  textColor=HexColor("#2C3E50"), alignment=TA_RIGHT),
        "num_g":   ParagraphStyle("ng", fontName="Helvetica-Bold",   fontSize=9,  textColor=VERDE_OSC, alignment=TA_RIGHT),
        "num_r":   ParagraphStyle("nr", fontName="Helvetica-Bold",   fontSize=9,  textColor=ROJO,     alignment=TA_RIGHT),
        "num_b":   ParagraphStyle("nb", fontName="Helvetica-Bold",   fontSize=9,  textColor=AZUL,     alignment=TA_RIGHT),
    }


def _card_mini(titulo, valor, color, ancho=3.8*cm):
    """Mini tarjeta de resumen."""
    from reportlab.platypus import Table as T, TableStyle as TS
    val_str = str(valor)
    fsize = 18 if len(val_str) <= 6 else (13 if len(val_str) <= 12 else 9)
    data = [
        [Paragraph(f"<b>{valor}</b>", ParagraphStyle("cv", fontName="Helvetica-Bold",
                   fontSize=fsize, textColor=BLANCO, alignment=TA_CENTER, leading=fsize+2))],
        [Paragraph(titulo, ParagraphStyle("ct", fontName="Helvetica",
                   fontSize=7, textColor=BLANCO, alignment=TA_CENTER, leading=9))],
    ]
    inner = T(data, colWidths=[ancho - 0.2*cm])
    inner.setStyle(TS([
        ("BACKGROUND",    (0,0),(-1,-1), color),
        ("ROUNDEDCORNERS",[5]),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
    ]))
    return inner


def generar_reporte_proyecto(proyecto_nombre, resumen, registros_salidas,
                              registros_devoluciones, usuario=None, output_dir=None):
    """
    Genera PDF del reporte financiero de un proyecto específico.
    resumen: dict con keys total_salidas, devoluciones, neto
    registros_salidas: lista de SalidaProyecto tipo='salida'
    registros_devoluciones: lista de SalidaProyecto tipo='devolucion'
    """
    if output_dir is None:
        from app.core.config import BASE_DIR
        output_dir = BASE_DIR / "documentos"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    fecha_str = date.today().strftime("%Y%m%d")
    nombre_safe = "".join(c for c in proyecto_nombre if c.isalnum() or c in " _-")[:30].strip().replace(" ", "_")
    ruta = Path(output_dir) / f"Financiero_{nombre_safe}_{fecha_str}.pdf"

    doc = SimpleDocTemplate(str(ruta), pagesize=letter,
                             topMargin=1.8*cm, bottomMargin=1.8*cm,
                             leftMargin=2*cm, rightMargin=2*cm)
    ST = _ST()
    story = []

    # ── Encabezado ──────────────────────────────────────────────────────────
    story.append(Paragraph("GEOINVENTARIO", ST["titulo"]))
    story.append(Paragraph("REPORTE FINANCIERO DE PROYECTO", ST["sub"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=VERDE, spaceAfter=8))

    # ── Info del proyecto ────────────────────────────────────────────────────
    gen_por = usuario.nombre if usuario else "Sistema"
    info = [
        ("Proyecto:",          proyecto_nombre),
        ("Generado por:",      gen_por),
        ("Fecha del informe:", date.today().strftime("%d/%m/%Y")),
        ("Total salidas:",     f"{len(registros_salidas)} registros"),
        ("Total devoluciones:",f"{len(registros_devoluciones)} registros"),
    ]
    tbl_info = Table(
        [[Paragraph(f"<b>{k}</b>", ParagraphStyle("lk", fontName="Helvetica-Bold", fontSize=9, textColor=AZUL)),
          Paragraph(v,             ParagraphStyle("lv", fontName="Helvetica",       fontSize=9))]
         for k, v in info],
        colWidths=[4*cm, 13*cm]
    )
    tbl_info.setStyle(TableStyle([
        ("GRID",         (0,0),(-1,-1), 0.4, HexColor("#DDE2E8")),
        ("BACKGROUND",   (0,0),(0,-1),  GRIS_CLA),
        ("TOPPADDING",   (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
    ]))
    story.append(tbl_info)
    story.append(Spacer(1, 12))

    # ── Tarjetas resumen ─────────────────────────────────────────────────────
    salidas  = resumen.get("total_salidas", 0)
    devol    = resumen.get("devoluciones", 0)
    neto     = resumen.get("neto", 0)

    cards = [[
        _card_mini("⬇️  Total Salidas",    f"${salidas:,.0f}",  AZUL,      4.2*cm),
        _card_mini("↩️  Devoluciones",     f"${devol:,.0f}",   NARANJA,   4.2*cm),
        _card_mini("💰 Valor Neto",         f"${neto:,.0f}",    TEAL,      4.2*cm),
        _card_mini("📦 Ítems Salida",       str(len(registros_salidas)),   AZUL_MED, 4.2*cm),
    ]]
    tbl_cards = Table(cards, colWidths=[4.4*cm]*4)
    tbl_cards.setStyle(TableStyle([
        ("ALIGN",        (0,0),(-1,-1), "CENTER"),
        ("LEFTPADDING",  (0,0),(-1,-1), 3),
        ("RIGHTPADDING", (0,0),(-1,-1), 3),
    ]))
    story.append(tbl_cards)
    story.append(Spacer(1, 14))

    # ── Tabla salidas ────────────────────────────────────────────────────────
    if registros_salidas:
        story.append(KeepTogether([
            Paragraph(f"⬇️  Materiales Entregados al Proyecto ({len(registros_salidas)} registros)",
                      ST["seccion"]),
        ]))
        story.append(_tabla_movimientos(registros_salidas, AZUL, AZUL_CLA, ST, tipo="salida"))
        story.append(Spacer(1, 12))
    else:
        story.append(Paragraph("No hay salidas registradas para este proyecto.", ST["normal"]))

    # ── Tabla devoluciones ───────────────────────────────────────────────────
    if registros_devoluciones:
        story.append(KeepTogether([
            Paragraph(f"↩️  Materiales Devueltos ({len(registros_devoluciones)} registros)",
                      ST["seccion"]),
        ]))
        story.append(_tabla_movimientos(registros_devoluciones, NARANJA, HexColor("#FFF3CD"), ST, tipo="devolucion"))
        story.append(Spacer(1, 12))

    # ── Resumen por material ─────────────────────────────────────────────────
    todos = registros_salidas + registros_devoluciones
    if todos:
        story.append(Paragraph("📋  Resumen por Material", ST["seccion"]))
        story.append(_tabla_resumen_material(registros_salidas, registros_devoluciones, ST))

    # ── Pie ──────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS_TXT))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Reporte Financiero  •  GeoInventario  •  Ing. Mateo Salazar Zapata  •  {date.today().strftime('%d/%m/%Y')}",
        ST["pie"]
    ))

    doc.build(story)
    return str(ruta)


def _tabla_movimientos(registros, color_hdr, color_alt, ST, tipo="salida"):
    hdrs = ["#", "Fecha", "Material", "Unidad", "Cantidad", "Precio Unit.", "Valor Total", "Responsable"]
    rows = [[Paragraph(h, ST["hdr"]) for h in hdrs]]

    total_valor = 0
    for i, reg in enumerate(registros):
        mat_nombre = reg.material.nombre_material if reg.material else "—"
        mat_unidad = reg.material.unidad if reg.material else "—"
        valor = abs(reg.valor_total or 0)
        total_valor += valor
        fecha_str = reg.fecha.strftime("%d/%m/%Y") if reg.fecha else "—"
        precio = reg.precio_unitario or 0

        rows.append([
            Paragraph(str(i+1),               ST["cel_c"]),
            Paragraph(fecha_str,               ST["cel_c"]),
            Paragraph(mat_nombre,              ST["cel_l"]),
            Paragraph(mat_unidad,              ST["cel_c"]),
            Paragraph(f"{reg.cantidad or 0:g}", ST["cel_c"]),
            Paragraph(f"$ {precio:,.0f}",      ST["cel_r"]),
            Paragraph(f"$ {valor:,.0f}",
                      ST["num_g"] if tipo == "devolucion" else ST["num_b"]),
            Paragraph(reg.responsable or "—",  ST["cel_l"]),
        ])

    # Fila total
    rows.append([
        Paragraph("", ST["cel_c"]),
        Paragraph("", ST["cel_c"]),
        Paragraph("<b>TOTAL</b>", ParagraphStyle("tot", fontName="Helvetica-Bold", fontSize=9, textColor=AZUL)),
        Paragraph("", ST["cel_c"]),
        Paragraph("", ST["cel_c"]),
        Paragraph("", ST["cel_c"]),
        Paragraph(f"<b>$ {total_valor:,.0f}</b>",
                  ParagraphStyle("totv", fontName="Helvetica-Bold", fontSize=9,
                                 textColor=VERDE_OSC if tipo=="devolucion" else AZUL, alignment=TA_RIGHT)),
        Paragraph("", ST["cel_c"]),
    ])

    col_w = [0.7*cm, 2*cm, 5*cm, 1.5*cm, 1.5*cm, 2.2*cm, 2.2*cm, 2.7*cm]
    t = Table(rows, colWidths=col_w)
    n = len(rows)
    cmds = [
        ("BACKGROUND",    (0,0),  (-1,0),  color_hdr),
        ("BACKGROUND",    (0,n-1),(-1,n-1),GRIS_CLA),
        ("GRID",          (0,0),  (-1,-1), 0.4, HexColor("#DDE2E8")),
        ("ALIGN",         (0,0),  (-1,-1), "CENTER"),
        ("ALIGN",         (2,1),  (2,-1),  "LEFT"),
        ("ALIGN",         (5,1),  (6,-1),  "RIGHT"),
        ("ALIGN",         (7,1),  (7,-1),  "LEFT"),
        ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),  (-1,-1), 4),
        ("BOTTOMPADDING", (0,0),  (-1,-1), 4),
        ("LEFTPADDING",   (2,1),  (2,-1),  6),
        ("LINEABOVE",     (0,n-1),(-1,n-1),1, color_hdr),
    ]
    for i in range(1, n-1):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0,i),(-1,i), color_alt))
    t.setStyle(TableStyle(cmds))
    return t


def _tabla_resumen_material(salidas, devoluciones, ST):
    """Agrupa por material: total salido, devuelto, neto."""
    resumen = {}
    for reg in salidas:
        nom = reg.material.nombre_material if reg.material else "—"
        uni = reg.material.unidad if reg.material else "—"
        if nom not in resumen:
            resumen[nom] = {"unidad": uni, "salidas": 0, "devol": 0}
        resumen[nom]["salidas"] += abs(reg.valor_total or 0)

    for reg in devoluciones:
        nom = reg.material.nombre_material if reg.material else "—"
        uni = reg.material.unidad if reg.material else "—"
        if nom not in resumen:
            resumen[nom] = {"unidad": uni, "salidas": 0, "devol": 0}
        resumen[nom]["devol"] += abs(reg.valor_total or 0)

    hdrs = ["Material", "Unidad", "Total Salidas", "Total Devuelto", "Valor Neto"]
    rows = [[Paragraph(h, ST["hdr"]) for h in hdrs]]
    total_s = total_d = total_n = 0

    for nom, dat in sorted(resumen.items()):
        neto = dat["salidas"] - dat["devol"]
        total_s += dat["salidas"]; total_d += dat["devol"]; total_n += neto
        rows.append([
            Paragraph(nom,                          ST["cel_l"]),
            Paragraph(dat["unidad"],                ST["cel_c"]),
            Paragraph(f"$ {dat['salidas']:,.0f}",   ST["cel_r"]),
            Paragraph(f"$ {dat['devol']:,.0f}",     ST["num_g"] if dat["devol"] else ST["cel_r"]),
            Paragraph(f"$ {neto:,.0f}",
                      ST["num_b"] if neto >= 0 else ST["num_r"]),
        ])

    rows.append([
        Paragraph("<b>TOTAL</b>",            ParagraphStyle("tot", fontName="Helvetica-Bold", fontSize=9, textColor=AZUL)),
        Paragraph("",                        ST["cel_c"]),
        Paragraph(f"<b>$ {total_s:,.0f}</b>",ParagraphStyle("ts", fontName="Helvetica-Bold", fontSize=9, textColor=AZUL, alignment=TA_RIGHT)),
        Paragraph(f"<b>$ {total_d:,.0f}</b>",ParagraphStyle("td", fontName="Helvetica-Bold", fontSize=9, textColor=VERDE_OSC, alignment=TA_RIGHT)),
        Paragraph(f"<b>$ {total_n:,.0f}</b>",ParagraphStyle("tn", fontName="Helvetica-Bold", fontSize=9,
                  textColor=VERDE_OSC if total_n >= 0 else ROJO, alignment=TA_RIGHT)),
    ])

    col_w = [6.5*cm, 1.5*cm, 2.8*cm, 2.8*cm, 2.8*cm]
    t = Table(rows, colWidths=col_w)
    n = len(rows)
    cmds = [
        ("BACKGROUND",    (0,0),  (-1,0),  TEAL),
        ("BACKGROUND",    (0,n-1),(-1,n-1),GRIS_CLA),
        ("LINEABOVE",     (0,n-1),(-1,n-1),1, TEAL),
        ("GRID",          (0,0),  (-1,-1), 0.4, HexColor("#DDE2E8")),
        ("ALIGN",         (0,0),  (-1,-1), "CENTER"),
        ("ALIGN",         (0,1),  (0,-1),  "LEFT"),
        ("ALIGN",         (2,1),  (4,-1),  "RIGHT"),
        ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),  (-1,-1), 4),
        ("BOTTOMPADDING", (0,0),  (-1,-1), 4),
        ("LEFTPADDING",   (0,1),  (0,-1),  6),
    ]
    for i in range(1, n-1):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0,i),(-1,i), AZUL_CLA))
    t.setStyle(TableStyle(cmds))
    return t


def generar_reporte_general_financiero(proyectos_resumen, usuario=None, output_dir=None):
    """
    Genera un PDF con el resumen financiero de TODOS los proyectos.
    proyectos_resumen: lista de dicts {nombre, total_salidas, devoluciones, neto}
    """
    if output_dir is None:
        from app.core.config import BASE_DIR
        output_dir = BASE_DIR / "documentos"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    fecha_str = date.today().strftime("%Y%m%d")
    ruta = Path(output_dir) / f"Financiero_General_{fecha_str}.pdf"

    doc = SimpleDocTemplate(str(ruta), pagesize=letter,
                             topMargin=1.8*cm, bottomMargin=1.8*cm,
                             leftMargin=2*cm, rightMargin=2*cm)
    ST = _ST()
    story = []

    story.append(Paragraph("GEOINVENTARIO", ST["titulo"]))
    story.append(Paragraph("REPORTE FINANCIERO GENERAL — TODOS LOS PROYECTOS", ST["sub"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=VERDE, spaceAfter=8))

    gen_por = usuario.nombre if usuario else "Sistema"
    info = [
        ("Generado por:",      gen_por),
        ("Fecha del informe:", date.today().strftime("%d/%m/%Y")),
        ("Total proyectos:",   str(len(proyectos_resumen))),
    ]
    tbl_info = Table(
        [[Paragraph(f"<b>{k}</b>", ParagraphStyle("lk", fontName="Helvetica-Bold", fontSize=9, textColor=AZUL)),
          Paragraph(v,             ParagraphStyle("lv", fontName="Helvetica",       fontSize=9))]
         for k, v in info],
        colWidths=[4*cm, 13*cm]
    )
    tbl_info.setStyle(TableStyle([
        ("GRID",         (0,0),(-1,-1), 0.4, HexColor("#DDE2E8")),
        ("BACKGROUND",   (0,0),(0,-1),  GRIS_CLA),
        ("TOPPADDING",   (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
    ]))
    story.append(tbl_info)
    story.append(Spacer(1, 12))

    # Cards totales globales
    total_s = sum(p.get("total_salidas", 0) for p in proyectos_resumen)
    total_d = sum(p.get("devoluciones", 0)  for p in proyectos_resumen)
    total_n = sum(p.get("neto", 0)           for p in proyectos_resumen)

    cards = [[
        _card_mini("⬇️  Total Salidas",  f"${total_s:,.0f}", AZUL,     4.2*cm),
        _card_mini("↩️  Devoluciones",   f"${total_d:,.0f}", NARANJA,  4.2*cm),
        _card_mini("💰 Valor Neto Total", f"${total_n:,.0f}", TEAL,     4.2*cm),
        _card_mini("🏗️  Proyectos",      str(len(proyectos_resumen)), MORADO, 4.2*cm),
    ]]
    tbl_cards = Table(cards, colWidths=[4.4*cm]*4)
    tbl_cards.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3)]))
    story.append(tbl_cards)
    story.append(Spacer(1, 14))

    # Tabla general por proyecto
    story.append(Paragraph("📊  Detalle por Proyecto", ST["seccion"]))
    hdrs = ["#", "Proyecto", "Total Salidas", "Devoluciones", "Valor Neto"]
    rows = [[Paragraph(h, ST["hdr"]) for h in hdrs]]
    for i, p in enumerate(sorted(proyectos_resumen, key=lambda x: -x.get("neto",0))):
        neto = p.get("neto", 0)
        rows.append([
            Paragraph(str(i+1),                      ST["cel_c"]),
            Paragraph(p.get("nombre","—"),            ST["cel_l"]),
            Paragraph(f"$ {p.get('total_salidas',0):,.0f}", ST["cel_r"]),
            Paragraph(f"$ {p.get('devoluciones',0):,.0f}",  ST["num_g"] if p.get("devoluciones",0) else ST["cel_r"]),
            Paragraph(f"$ {neto:,.0f}",
                      ST["num_b"] if neto >= 0 else ST["num_r"]),
        ])
    # Fila total
    rows.append([
        Paragraph("",                 ST["cel_c"]),
        Paragraph("<b>TOTAL</b>",     ParagraphStyle("tot",fontName="Helvetica-Bold",fontSize=9,textColor=AZUL)),
        Paragraph(f"<b>$ {total_s:,.0f}</b>", ParagraphStyle("ts",fontName="Helvetica-Bold",fontSize=9,textColor=AZUL,alignment=TA_RIGHT)),
        Paragraph(f"<b>$ {total_d:,.0f}</b>", ParagraphStyle("td",fontName="Helvetica-Bold",fontSize=9,textColor=VERDE_OSC,alignment=TA_RIGHT)),
        Paragraph(f"<b>$ {total_n:,.0f}</b>", ParagraphStyle("tn",fontName="Helvetica-Bold",fontSize=9,textColor=VERDE_OSC if total_n>=0 else ROJO,alignment=TA_RIGHT)),
    ])

    col_w = [0.8*cm, 7.5*cm, 2.8*cm, 2.8*cm, 2.8*cm]
    t = Table(rows, colWidths=col_w)
    n = len(rows)
    cmds = [
        ("BACKGROUND",    (0,0),  (-1,0),  TEAL),
        ("BACKGROUND",    (0,n-1),(-1,n-1),GRIS_CLA),
        ("LINEABOVE",     (0,n-1),(-1,n-1),1, TEAL),
        ("GRID",          (0,0),  (-1,-1), 0.4, HexColor("#DDE2E8")),
        ("ALIGN",         (0,0),  (-1,-1), "CENTER"),
        ("ALIGN",         (1,1),  (1,-1),  "LEFT"),
        ("ALIGN",         (2,1),  (4,-1),  "RIGHT"),
        ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),  (-1,-1), 4),
        ("BOTTOMPADDING", (0,0),  (-1,-1), 4),
        ("LEFTPADDING",   (1,1),  (1,-1),  6),
    ]
    for i in range(1, n-1):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0,i),(-1,i), AZUL_CLA))
    t.setStyle(TableStyle(cmds))
    story.append(t)

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS_TXT))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Reporte Financiero General  •  GeoInventario  •  Ing. Mateo Salazar Zapata  •  {date.today().strftime('%d/%m/%Y')}",
        ST["pie"]
    ))
    doc.build(story)
    return str(ruta)
