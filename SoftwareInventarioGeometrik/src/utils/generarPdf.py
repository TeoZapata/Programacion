from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PyQt5.QtWidgets import QMessageBox
import os
from datetime import datetime
from src.utils.standarFunc import *
from DataBase.managerInventario import *
from DataBase.storeDB import *

def generar_pdf_simple(data, save_directory):
    """
    Generate a simple PDF report with improved table design.

    Args:
        data (dict): A dictionary containing the required keys.
        save_directory (str): The directory to save the generated PDF.
    """

    required_keys = {"cliente", "proyecto", "responsable", "fecha", "productos"}
    if not isinstance(data, dict) or not required_keys.issubset(data.keys()):
        raise ValueError("Datos inválidos o incompletos para generar el PDF.")

    # Generate the file name
    file_name = f"{data['proyecto']}_{data['fecha'].replace('/', '-')}_{datetime.now().strftime('%H-%M-%S')}.pdf"
    save_path = os.path.join(save_directory, file_name)

    c = canvas.Canvas(save_path, pagesize=letter)
    c.setFont("Helvetica", 12)

    # Header
    c.drawString(50, 750, f"Cliente: {data['cliente']}")
    c.drawString(50, 730, f"Proyecto: {data['proyecto']}")
    c.drawString(50, 710, f"Responsable: {data['responsable']}")
    c.drawString(50, 690, f"Fecha de salida: {data['fecha']}")

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
        cantidad = producto.get("cantidad", 0)
        unidad = producto.get("unidad", "")
        precio_unitario = producto.get("precio_unitario", 0)
        precio_total = cantidad * precio_unitario
        total_final += precio_total

        values = [nombre, str(cantidad), unidad, f"${precio_unitario:.2f}", f"${precio_total:.2f}"]
        for i, value in enumerate(values):
            c.drawString(x_positions[i], y, value)
        y -= 20

        # Draw a line after each row
        c.line(50, y + 15, 500, y + 15)

    # Total
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y - 20, f"Precio Final Total: ${total_final:,.2f}")
    # Agrega un espacio para firmar el responsable de la salida
    c.drawString(50, y - 40, "______________________________")
    c.drawString(50, y - 60, "Firma del Responsable de la Salida")
    c.drawString(50, y - 120, "Nombre: ______________________")  
    # Save the PDF
    c.save()
    QMessageBox.information(None, "PDF Generado", f"El PDF ha sido generado y guardado en: {save_path}")


def gen_pdf(self):
        """Genera el PDF con los datos de la tabla seleccionada."""
        # Obtener los datos de la tabla seleccionada
        
        cliente = self.entry_cliente.text()
        proyecto = self.entry_proyecto.currentText()
        responsable = self.entry_responsable.text()
        fecha = self.entry_fecha_Actual.text()
        if not all([cliente, proyecto, responsable, fecha]):
            QMessageBox.warning(None, "Error", "Por favor, completa todos los campos.")
            return

        productos = []
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

        getSelectedTable(self)

        generar_pdf_simple(data={
            "cliente": cliente,
            "proyecto": proyecto,
            "responsable": responsable,
            "fecha": fecha,
            "productos": productos,
        }, save_directory="./") # Cambia el directorio según sea necesario
        
        