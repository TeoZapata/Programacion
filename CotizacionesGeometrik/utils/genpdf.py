
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class PDFGenerator:
    @staticmethod
    def generar_pdf(datos_cliente, datos_cotizacion, calculos):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.darkblue,
            alignment=1
        )
        story.append(Paragraph("COTIZACIÓN SISTEMA SOLAR FOTOVOLTAICO", title_style))
        story.append(Spacer(1, 20))
        
        # Información del cliente
        story.append(Paragraph("INFORMACIÓN DEL CLIENTE", styles['Heading2']))
        cliente_data = [
            ['Nombre:', datos_cliente['nombre']],
            ['Cédula:', datos_cliente['cedula']],
            ['Teléfono:', datos_cliente['telefono']],
            ['Email:', datos_cliente['email']],
            ['Dirección:', datos_cliente['direccion']],
            ['Ciudad:', datos_cliente['ciudad']]
        ]
        
        cliente_table = Table(cliente_data, colWidths=[2*inch, 4*inch])
        cliente_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(cliente_table)
        story.append(Spacer(1, 20))
        
        # Análisis de consumo
        story.append(Paragraph("ANÁLISIS DE CONSUMO", styles['Heading2']))
        consumo_data = [
            ['Consumos registrados:', ', '.join(map(str, datos_cotizacion['consumos'])) + ' kWh'],
            ['Tipo de facturación:', datos_cotizacion['tipo_facturacion']],
            ['Consumo promedio mensual:', f"{calculos['consumo_promedio']:.2f} kWh"],
            ['Consumo anual estimado:', f"{calculos['consumo_anual']:.2f} kWh"],
            ['Irradiación solar:', f"{datos_cotizacion['irradiacion']} kWh/m²/año"]
        ]
        
        consumo_table = Table(consumo_data, colWidths=[3*inch, 3*inch])
        consumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(consumo_table)
        story.append(Spacer(1, 20))
        
        # Dimensionamiento del sistema
        story.append(Paragraph("DIMENSIONAMIENTO DEL SISTEMA", styles['Heading2']))
        sistema_data = [
            ['Potencia requerida:', f"{calculos['potencia_requerida']:.2f} kW"],
            ['Generación anual estimada:', f"{calculos['generacion_anual']:.2f} kWh"]
        ]
        
        sistema_table = Table(sistema_data, colWidths=[3*inch, 3*inch])
        sistema_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(sistema_table)
        story.append(Spacer(1, 20))
        
        # Cotización
        story.append(Paragraph("COTIZACIÓN", styles['Heading2']))
        cotizacion_data = [
            ['Costo base del sistema:', f"${calculos['costo_base']:,.0f} COP"],
            ['Costo mano de obra:', f"${calculos['costo_mano_obra']:,.0f} COP"],
            ['Utilidad (%s%%):'% datos_cotizacion['utilidad_porcentaje'], f"${calculos['utilidad']:,.0f} COP"],
            ['Imprevistos (%s%%):'% datos_cotizacion['imprevistos_porcentaje'], f"${calculos['imprevistos']:,.0f} COP"],
            ['IVA (%s%%):'% datos_cotizacion['iva_porcentaje'], f"${calculos['iva']:,.0f} COP"],
            ['TOTAL:', f"${calculos['costo_total']:,.0f} COP"]
        ]
        
        cotizacion_table = Table(cotizacion_data, colWidths=[3*inch, 3*inch])
        cotizacion_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -2), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, -2), colors.black),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(cotizacion_table)
        
        # Fecha
        story.append(Spacer(1, 30))
        fecha_actual = datetime.now().strftime("%d de %B de %Y")
        story.append(Paragraph(f"Fecha: {fecha_actual}", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer