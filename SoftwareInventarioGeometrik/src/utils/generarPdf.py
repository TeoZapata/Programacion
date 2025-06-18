from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PyQt5.QtWidgets import QMessageBox
import os
from datetime import datetime
from src.utils.standarFunc import *
from DataBase.managerInventario import *
from DataBase.storeDB import *
from reportlab.lib.pagesizes import landscape, letter

def calcular_cuantas_SalidasDB():
    """Calcula cuantas salidas hay en la base de datos"""
    db = conex()
    db.iniciar_bd()
    resultado = db.ejecutar_consulta("SELECT cantSalidas FROM informacion WHERE id = 0")
    if resultado:
        return resultado[0][0]
    return 0
def calcular_cuantas_EntradasDB():
    """Calcula cuantas entradas hay en la base de datos"""
    db = conex()
    db.iniciar_bd()
    resultado = db.ejecutar_consulta("SELECT cantEntradas FROM informacion WHERE id = 0")
    if resultado:
        return resultado[0][0]
    return 0
def calcular_cuantas_DevolucionesDB():
    """Calcula cuantas devoluciones hay en la base de datos"""
    db = conex()
    db.iniciar_bd()
    resultado = db.ejecutar_consulta("SELECT cantDevoluciones FROM informacion WHERE id = 0")
    if resultado:
        return resultado[0][0]
    return 0
def calcular_cuantas_ReporteHerramientasDB():
    db = conex()
    db.iniciar_bd()
    resultado = db.ejecutar_consulta("SELECT cantReporteHerramientas FROM informacion WHERE id = 0")
    if resultado:
        return resultado[0][0]
    return 0


def generar_pdf_simple(data, save_directory, descripcion):
    """
    Generate a simple PDF report with improved table design.

    Args:
        data (dict): A dictionary containing the required keys.
        save_directory (str): The directory to save the generated PDF.
    """
    try:
        required_keys = {"cliente", "proyecto", "responsable", "fecha", "productos"}
        if not isinstance(data, dict) or not required_keys.issubset(data.keys()):
            raise ValueError("Datos inválidos o incompletos para generar el PDF.")

        if descripcion == "Salida":
            num = calcular_cuantas_SalidasDB()
        elif descripcion == "Entrada":
            num = calcular_cuantas_EntradasDB()
        else:
            num = calcular_cuantas_DevolucionesDB()
        # Generate the file name
        file_name = f"{descripcion}_{num+1}_{data['proyecto']}_{fecha_actual().replace('/', '-')}.pdf"
        save_path = os.path.join(save_directory, file_name)

        c = canvas.Canvas(save_path, pagesize=letter)
        c.setFont("Helvetica", 12)

        # Header
        # Centra el título en la parte superior
        titulo = f"{descripcion} No. {num+1}"
        page_width, _ = letter
        text_width = c.stringWidth(titulo, "Helvetica-Bold", 14)
        c.setFont("Helvetica-Bold", 14)
        c.drawString((page_width - text_width) / 2, 770, titulo)
        c.setFont("Helvetica", 12)  # Restablece la fuente para el resto del documento
        c.drawString(50, 750, f"Cliente: {data['cliente']}")
        c.drawString(50, 730, f"Proyecto: {data['proyecto']}")
        c.drawString(50, 710, f"{'No. Remisión/Factura' if descripcion == 'Entrada' else 'Responsable'}: {data['responsable']}")
        c.drawString(50, 690, f"Fecha de {descripcion.lower()}: {data['fecha']}")
        # Intenta dibujar el logo con fondo blanco detrás
        logo_path = "./Fuentes/logo.png"
        logo_x, logo_y, logo_w, logo_h = 400, 700, 100, 50

        # Dibuja un rectángulo blanco como fondo del logo
        c.setFillColor(colors.white)
        c.rect(logo_x, logo_y, logo_w, logo_h, fill=1, stroke=0)
        c.setFillColor(colors.black)  # Restablece el color de relleno

        # Dibuja el logo encima del fondo blanco
        c.drawImage(logo_path, logo_x, logo_y, width=logo_w, height=logo_h, mask='auto')

        # Table header
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 650, "Productos:")
        c.setFont("Helvetica", 10)

        # Draw table headers
        headers = ["Código","Nombre", "Cantidad", "Unidad", "Precio Unitario", "Precio Total"]
        x_positions = [50,120,270, 330, 400, 490]  # Adjusted positions for better spacing
        y = 630

        # Draw table headers
        for i, header in enumerate(headers):
            c.drawString(x_positions[i], y, header)

        # Draw a line under the headers
        c.setStrokeColor(colors.black)
        c.line(50, y - 5, 550, y - 5)

        y -= 20
        total_final = 0

        # Table content
        for producto in data["productos"]:
            codigo = producto.get("codigo_barras", "")
            nombre = producto.get("nombre", "")
            cantidad = float(producto.get("cantidad", 0))
            unidad = producto.get("unidad", "")
            precio_unitario = float(producto.get("precio_unitario", 0))
            precio_total = float(cantidad) * float(precio_unitario)
            total_final += precio_total

            # Divide el nombre en partes de máximo 30 caracteres
            nombre_lines = [nombre[i:i+20] for i in range(0, len(nombre), 30)]
            line_count = len(nombre_lines)
            row_height = 20 * line_count  # Ajusta la altura de la fila según las líneas

            c.drawString(x_positions[0], y, codigo)  # Dibuja el código de barras en la primera columna
            # Dibuja cada línea del nombre
            for idx, nombre_line in enumerate(nombre_lines):
                c.drawString(x_positions[1], y - (idx * 15), nombre_line)

            # Solo la primera línea de nombre lleva los otros datos, las demás quedan vacías
            c.drawString(x_positions[2], y, str(cantidad))
            c.drawString(x_positions[3], y, unidad)
            c.drawString(x_positions[4], y, f"${precio_unitario:.2f}")
            c.drawString(x_positions[5], y, f"${precio_total:.2f}")


            y -= row_height

        # Total
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y - 20, f"Precio Final Total: ${total_final:,.2f}")
        # Agrega un espacio para firmar el responsable de la salida
        c.drawString(50, y - 100, f"Firma del Responsable")
        c.drawString(50, y - 140, "Nombre: ______________________")  
        # Save the PDF
        c.save()
        QMessageBox.information(None, "PDF Generado", f"El PDF ha sido generado y guardado en: {save_path}")
    except Exception as e:
        QMessageBox.critical(None, "Error al generar PDF", f"Ocurrió un error al generar el PDF:\n{str(e)}")


def gen_pdf(self):
        """Genera el PDF con los datos de la tabla seleccionada."""
        # Obtener los datos de la tabla seleccionada
        try:
            cliente , proyecto = informacion_cliente(self)
            proyecto = self.entry_proyecto.currentText()
            responsable = self.entry_responsable.currentText()
            fecha = self.entry_fecha_Actual.text()

            if responsable == "":
                QMessageBox.warning(self, "Error", "Por favor, ingrese el nombre del responsable.")
                return
            productos = []
            
            ok = QMessageBox.question(
                self,
                "COnfirmación",
                "¿Está seguro de que desea generar el PDF con los datos seleccionados?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes )
            if ok == QMessageBox.No:
                return
            for row in range(self.selected_table.rowCount()):
                item = {
                    "id": self.selected_table.item(row, 0).text(),
                    "codigo_barras": self.selected_table.item(row, 1).text(),
                    "nombre": self.selected_table.item(row, 2).text(),
                    "cantidad": int(self.selected_table.item(row, 3).text()),
                    "unidad": self.selected_table.item(row, 4).text(),
                    "precio_unitario": float(self.selected_table.item(row, 5).text()),
                }
                item["precio_total"] = item["cantidad"] * item["precio_unitario"]
                productos.append(item)


            agregar_salida_material(data={
                "cliente": cliente,
                "proyecto": proyecto,
                "responsable": responsable,
                "fecha": fecha,
                "productos": productos,
            })

            
            QMessageBox.information(self, "Éxito", "Salida de materiales registrada correctamente.")

            generar_pdf_simple(data={
                "cliente": cliente,
                "proyecto": proyecto,
                "responsable": responsable,
                "fecha": fecha,
                "productos": productos,
            }, save_directory="./Salidas", descripcion="Salida") # Cambia el directorio según sea necesario
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al generar el PDF:\n{str(e)}")

def gen_pdf_reporte(table_widget, save_directory="./Reportes", titulo="Reporte de Herramientas"):
    """
    Genera un PDF elegante con los datos de un QTableWidget.
    Solo incluye las filas actualmente visibles (no ocultas) en la tabla.
    Ajusta el ancho de columnas y permite encabezados y celdas de texto largo en varias líneas.
    Args:
        table_widget (QTableWidget): La tabla con los datos.
        save_directory (str): Carpeta donde guardar el PDF.
        titulo (str): Título del reporte.
    """
    if table_widget.rowCount()==0:
        QMessageBox.warning(None, "Error", "No hay datos para generar el reporte.")
        return
    
    try:
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)


        num = calcular_cuantas_ReporteHerramientasDB()
        fecha_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        file_name = f"{titulo.replace(' ', '_')}_{num+1}_{fecha_str}.pdf"
        save_path = os.path.join(save_directory, file_name)

        # Usar orientación horizontal (landscape)
        page_size = landscape(letter)
        c = canvas.Canvas(save_path, pagesize=page_size)
        width, height = page_size

        # Encabezado
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.darkblue)
        c.drawCentredString(width / 2, height - 50, f'{titulo} No. {num+1}')
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        c.drawString(40, height - 70, f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        # Encabezados de la tabla (con salto de línea manual para nombres largos)
        headers = [
            "ID", "ID\nHerram.", "Código", "Herramienta", "ID\nEmpleado", "Responsable",
            "Cédula", "Fecha\nAsign.", "Fecha\nCambio", "Estado", "Observación"
        ]
        # Columnas más angostas para optimizar espacio
        col_widths = [28, 38, 45, 80, 38, 70, 38, 50, 60, 38, 70]
        x_start = 40
        y_start = height - 100
        row_height = 20

        # Obtener solo las filas visibles
        visible_rows = [row for row in range(table_widget.rowCount()) if not table_widget.isRowHidden(row)]

        # Fondo de encabezado
        c.setFillColor(colors.lightblue)
        c.rect(x_start, y_start, sum(col_widths), row_height, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 8)
        x = x_start
        for i, header in enumerate(headers):
            # Soporta salto de línea en el header
            for idx, line in enumerate(header.split('\n')):
                c.drawString(x + 2, y_start + 12 - idx * 9, line)
            x += col_widths[i]

        # Líneas verticales de la tabla
        c.setStrokeColor(colors.grey)
        x = x_start
        for w in col_widths:
            c.line(x, y_start, x, y_start - row_height * (len(visible_rows) + 1))
            x += w
        c.line(x_start + sum(col_widths), y_start, x_start + sum(col_widths), y_start - row_height * (len(visible_rows) + 1))

        # Líneas horizontales
        for i in range(len(visible_rows) + 2):
            y = y_start - i * row_height
            c.line(x_start, y, x_start + sum(col_widths), y)

        # Filas de datos (solo visibles)
        c.setFont("Helvetica", 7)
        y = y_start - row_height
        for row in visible_rows:
            x = x_start
            for col in range(len(headers)):
                text = table_widget.item(row, col).text() if table_widget.item(row, col) else ""
                # Ajuste de texto largo: dividir en varias líneas si excede el ancho de la columna
                max_chars = int(col_widths[col] // 4.5)  # Ajusta el divisor para calibrar el corte
                lines = []
                while len(text) > max_chars:
                    lines.append(text[:max_chars])
                    text = text[max_chars:]
                lines.append(text)
                for idx, line in enumerate(lines[:2]):  # máximo 2 líneas por celda
                    c.drawString(x + 2, y + 12 - idx * 8, line)
                x += col_widths[col]
            y -= row_height

        c.save()
        db = conex()
        db.ejecutar_consulta("UPDATE informacion SET cantReporteHerramientas=cantReporteHerramientas+1 WHERE id = 0")

        QMessageBox.information(None, "PDF Generado", f"El PDF ha sido generado y guardado en: {save_path}")
    except Exception as e:
        QMessageBox.critical(None, "Error al generar PDF", f"Ocurrió un error al generar el PDF:\n{str(e)}")
