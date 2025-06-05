from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PyQt5.QtWidgets import QMessageBox
import os
from datetime import datetime
from src.utils.standarFunc import *
from DataBase.managerInventario import *
from DataBase.storeDB import *

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
        c.drawString(50, 690, f"Fecha de salida: {data['fecha']}")
        # Intenta dibujar el logo con fondo blanco detrás
        logo_path = "./Fuentes/logo.png"
        logo_x, logo_y, logo_w, logo_h = 400, 700, 180, 50

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
        headers = ["Nombre", "Cantidad", "Unidad", "Precio Unitario", "Precio Total"]
        x_positions = [50, 200, 270, 340, 430]  # Adjusted positions for better spacing
        y = 630

        # Draw table headers
        for i, header in enumerate(headers):
            c.drawString(x_positions[i], y, header)

        # Draw a line under the headers
        c.setStrokeColor(colors.black)
        c.line(50, y - 5, 500, y - 5)

        y -= 20
        total_final = 0

        # Table content
        for producto in data["productos"]:
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

            # Dibuja cada línea del nombre
            for idx, nombre_line in enumerate(nombre_lines):
                c.drawString(x_positions[0], y - (idx * 15), nombre_line)

            # Solo la primera línea de nombre lleva los otros datos, las demás quedan vacías
            c.drawString(x_positions[1], y, str(cantidad))
            c.drawString(x_positions[2], y, unidad)
            c.drawString(x_positions[3], y, f"${precio_unitario:.2f}")
            c.drawString(x_positions[4], y, f"${precio_total:.2f}")

            # Dibuja una línea después de la fila
            c.line(50, y - (15 * (line_count - 1)) + 15, 500, y - (15 * (line_count - 1)) + 15)

            y -= row_height

        # Total
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y - 20, f"Precio Final Total: ${total_final:,.2f}")
        # Agrega un espacio para firmar el responsable de la salida
        c.drawString(50, y - 100, "Firma del Responsable de la Salida")
        c.drawString(50, y - 120, "Nombre: ______________________")  
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
            responsable = self.entry_responsable.text()
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
                    "nombre": self.selected_table.item(row, 1).text(),
                    "cantidad": int(self.selected_table.item(row, 2).text()),
                    "unidad": self.selected_table.item(row, 3).text(),
                    "precio_unitario": float(self.selected_table.item(row, 4).text()),
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
        