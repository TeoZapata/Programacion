
from DataBase.storeDB import storeBD
from PyQt5.QtWidgets import QTableWidgetItem, QInputDialog, QPushButton, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from Style import *
from src.utils.standarFunc import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QLabel
from src.utils.generarPdf import *

class ManagerInventario():
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        

    def add_item(self, item_data):
        """Add a new item to the inventory."""
        self.db.insert_item(item_data)

    def update_item(self, item_id, updated_data):
        """Update an existing item in the inventory."""
        self.db.update_item(item_id, updated_data)

    def delete_item(self, item_id):
        """Delete an item from the inventory."""
        self.db.delete_item(item_id)

    def get_all_items(self):
        """Retrieve all items from the inventory."""
        return self.db.fetch_all_items()

    def get_item_by_id(self, item_id):
        """Retrieve a specific item by its ID."""
        return self.db.fetch_item_by_id(item_id)
    def getAllDisponible(db, self):
        """Retrieve a specific item by its ID."""
        dato = db.ejecutar_consulta(f"SELECT * FROM inventario WHERE cantidad > 0 ")
        print(dato)

        return dato
class DatabaseThread(QThread):
    data_fetched = pyqtSignal(list)  # Signal to emit the fetched data

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = storeBD()


    def run(self):
        # Fetch data from the database in a separate thread
        datos = self.db.ejecutar_consulta("SELECT * FROM inventario WHERE cantidad > 0")
        self.data_fetched.emit(datos)  # Emit the fetched data


def getManagerInventario(self):
    def update_table(datos):
        """Update the table with the fetched data."""
        self.table.blockSignals(True)  # Temporarily block signals to avoid triggering during updates

        # Clear the table before inserting new data
        self.table.setRowCount(0)

        for dato in datos:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # Assuming the columns are in the following order in the database:
            # ID, Nombre, Cantidad Disponible, Unidad, Precio Unitario, Precio Total
            self.table.setItem(row_position, 0, QTableWidgetItem(str(dato[0])))  # ID
            self.table.setItem(row_position, 1, QTableWidgetItem(dato[1]))       # Nombre
            self.table.setItem(row_position, 2, QTableWidgetItem(str(dato[4])))  # Cantidad Disponible
            self.table.setItem(row_position, 3, QTableWidgetItem(dato[5]))       # Unidad
            self.table.setItem(row_position, 4, QTableWidgetItem(str(dato[6])))  # Precio Unitario
            self.table.setItem(row_position, 5, QTableWidgetItem(str(dato[7])))  # Precio Total

            # Add a button for the "Agregar" column
            add_button = QPushButton("Agregar")
            add_button.setStyleSheet(BUTTON_ADD_MATERIAL)  # Set an icon for the button
            add_button.clicked.connect(lambda _, row=row_position: ventana_selec_cantidad(self, self.table.item(row, 0)))  # Connect to the selection function
            self.table.setCellWidget(row_position, 6, add_button)  # Add the button to the table


        self.table.blockSignals(False)  # Re-enable signals after updates
        

    # Create and start the database thread
    self.db_thread = DatabaseThread(self)
    self.db_thread.data_fetched.connect(update_table)  # Connect the signal to update the table
    self.db_thread.start()
def calcular_cuantas_SalidasDB():
    """Calcula cuantas salidas hay en la base de datos"""
    db = conex()
    db.iniciar_bd()
    # Obtener el número de salidas
    cantidad_salidas = db.ejecutar_consulta("SELECT COUNT(*) FROM registro WHERE descripcion = 'salida'")
    return cantidad_salidas[0][0] if cantidad_salidas else 0
def calcular_cuantas_EntradasDB():
    """Calcula cuantas entradas hay en la base de datos"""
    db = conex()
    db.iniciar_bd()
    # Obtener el número de entradas
    cantidad_entradas = db.ejecutar_consulta("SELECT COUNT(*) FROM registro WHERE descripcion = 'entrada'")
    return cantidad_entradas[0][0] if cantidad_entradas else 0
def calcular_cuantas_DevolucionesDB():
    """Calcula cuantas devoluciones hay en la base de datos"""
    db = conex()
    db.iniciar_bd()
    # Obtener el número de devoluciones
    cantidad_devoluciones = db.ejecutar_consulta("SELECT COUNT(*) FROM registro WHERE descripcion = 'devolucion'")
    return cantidad_devoluciones[0][0] if cantidad_devoluciones else 0

def ventana_selec_cantidad(self, item):
    """Se abre una ventana para elegir la cantidad cuando se selecciona el checkbox"""
    # Obtener información del material seleccionado
    nombre_item = self.table.item(item.row(), 1)  # Nombre del material
    cantidad_disponible_item = self.table.item(item.row(), 2)  # Cantidad disponible
    unidad_item = self.table.item(item.row(), 3)  # Unidad de medida
    precio_unitario_item = self.table.item(item.row(), 4)  # Precio Unitario

    if nombre_item and cantidad_disponible_item and unidad_item:
        nombre = nombre_item.text()
        cantidad_disponible = cantidad_disponible_item.text()
        unidad = unidad_item.text()
        precio_unitario = float(precio_unitario_item.text())
        
        # Crear una ventana emergente para elegir la cantidad
        cantidad, ok = QInputDialog.getInt(
            self,
            "Seleccione Cantidad",
            f"Cantidad disponible para {nombre}: {cantidad_disponible} {unidad}\nIngrese la cantidad a retirar:",
            1,  # Valor inicial
            1,  # Valor mínimo
            int(cantidad_disponible),  # Valor máximo
            1  # Incremento
        )
        
        if ok:    # Add the selected item to the selected_table
            self.entry_buscar_inventario.clear()  # Clear the search entry|
            row_position = self.selected_table.rowCount()
            self.selected_table.insertRow(row_position)
            precio_total = str(round(precio_unitario * cantidad, 2))  # Calculate total price
            # Copy relevant columns from the main table to the selected_table
            self.selected_table.setItem(row_position, 0, QTableWidgetItem(self.table.item(item.row(), 0).text()))  # ID
            self.selected_table.setItem(row_position, 1, QTableWidgetItem(nombre))  # Nombre
            self.selected_table.setItem(row_position, 2, QTableWidgetItem(str(cantidad)))  # Cantidad seleccionada
            self.selected_table.setItem(row_position, 3, QTableWidgetItem(unidad))  # Unidad
            self.selected_table.setItem(row_position, 4, QTableWidgetItem(self.table.item(item.row(), 4).text()))  # Precio Unitario
            self.selected_table.setItem(row_position, 5, QTableWidgetItem(precio_total))
            
            # Precio Total
            remove_button = QPushButton("Quitar")
            remove_button.clicked.connect(lambda:limpiar_tabla(self))  # Connect to remove_item
            remove_button.setStyleSheet(BUTTON_DELETE_MATERIAL)  # Set an icon for the button
            self.selected_table.setCellWidget(row_position, 6, remove_button)  # Add the button to the table
        
            # Set the checkbox to checked

def limpiarSelectTable(self):
    """Limpia todos los campos de entrada."""
    self.selected_table.setRowCount(0)
    self.entry_buscar_inventario.clear()  # Clear the search entry
        

def limpiar_tabla(self):
    """Limpia la tabla de materiales seleccionados."""
    row = self.selected_table.currentRow()
    if row >= 0:
        self.selected_table.removeRow(row)  # Remove the selected row from the table
        # Uncheck the checkbox in the main table


def filterTable(self, search_text):
    """Filtra las filas de la tabla principal según el texto ingresado."""
    search_text = search_text.lower()  # Convertir a minúsculas para búsqueda insensible a mayúsculas
    for row in range(self.table.rowCount()):
        match_found = False
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item and search_text in item.text().lower():
                match_found = True
                break
        self.table.setRowHidden(row, not match_found)
def filterTableInventario(self, search_text):
    """Filtra las filas de la tabla principal según el texto ingresado."""
    search_text = search_text.lower()  # Convertir a minúsculas para búsqueda insensible a mayúsculas
    for row in range(self.data_table.rowCount()):
        match_found = False
        for col in range(self.data_table.columnCount()):
            item = self.data_table.item(row, col)
            if item and search_text in item.text().lower():
                match_found = True
                break
        self.data_table.setRowHidden(row, not match_found)



def getSelectedTable(self):
    """Devuelve los datos de la tabla seleccionada."""
    selected_data = []
    for row in range(self.selected_table.rowCount()):
        row_data = []
        for col in range(self.selected_table.columnCount()):
            item = self.selected_table.item(row, col)
            if item:
                row_data.append(item.text())
            else:
                row_data.append(None)  # Agregar None si no hay elemento en la celda
        selected_data.append(row_data)
    
    actualizar_cantidad(self,selected_data)
    getManagerInventario(self)  # Actualizar la cantidad en la base de datos

def generar_devolucion(self):
    responsable = self.entry_responsable.text()
    if not responsable:
        QMessageBox.warning(None, "Error", "Debes ingresar un Responsable")
        return

    selected_data = []
    for row in range(self.selected_table.rowCount()):
        row_data = []
        for col in range(self.selected_table.columnCount()):
            item = self.selected_table.item(row, col)
            if item:
                row_data.append(item.text())
            else:
                row_data.append(None)  # Agregar None si no hay elemento en la celda
        selected_data.append(row_data)

    if not selected_data:
        QMessageBox.warning(None, "Error", "No hay materiales seleccionados para devolver")
        return

    confirmacion = QMessageBox.question(
        None,
        "Atención",
        f"Desea realizar la devolución para {responsable}?",
        QMessageBox.Yes | QMessageBox.No
    )

    if confirmacion == QMessageBox.Yes:
        db = conex()
        db.iniciar_bd()
        productos = []
        for material in selected_data:
            if len(material) < 10:
                QMessageBox.warning(None, "Error", "Datos incompletos en el material seleccionado")
                return

            item = {
                "id": material[4],
                "nombre": material[5],
                "cantidad": material[6],
                "unidad": material[7],
                "precio_unitario": material[8],
                "precio_total": material[9],
            }

            productos.append(item)
            # Update the 'registro' table
            db.ejecutar_consulta("UPDATE registro SET cantidad = cantidad - ? WHERE id = ?", (material[6], material[0]))
            db.ejecutar_consulta("UPDATE registro SET precioTotal=cantidad*precio WHERE id = ?", (material[0],))
            # Add the return entry with a description
            db.ejecutar_consulta(
                "INSERT INTO registro (proyecto, cliente, responsable, id_material, material, cantidad, unidad, precio, precioTotal, descripcion, fecha) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    material[1],  # proyecto
                    material[2],  # cliente
                    responsable,  # responsable
                    material[4],  # id_material
                    material[5],  # material
                    material[6],  # cantidad
                    material[7],  # unidad
                    material[8],  # precio
                    material[9],  # precioTotal
                    "devolucion",  # descripcion
                    fecha_actual(),  # fecha (función que genera la fecha actual)
                )
            )

            # Update the 'inventario' table
            db.ejecutar_consulta("UPDATE inventario SET cantidad = cantidad + ? WHERE id = ?", (material[6], material[4]))
            db.ejecutar_consulta("UPDATE inventario SET precioTotal = cantidad * precio WHERE id = ?",(material[4],))
     # Cambia el directorio según sea necesario
               
        generar_pdf_simple(data={
            "cliente": material[2],
            "proyecto": material[1],
            "responsable": responsable,
            "fecha": fecha_actual(),
            "productos": productos,
        }, save_directory="./Devoluciones", descripcion="Devolución") # Cambia el directorio según sea necesario
        
        db.ejecutar_consulta("UPDATE informacion SET cantDevoluciones = cantDevoluciones + 1 WHERE id = 0")
        QMessageBox.information(None, "Éxito", "Devolución registrada exitosamente")

    else:
        QMessageBox.warning(None, "Cancelado", "La devolución ha sido cancelada")

def tabla_registro_historial(self):
    db = conex()
    db.iniciar_bd()

    # Fetch all records from the 'registro' table
    registros = db.ejecutar_consulta("SELECT * FROM registro")

    # Clear the table before inserting new data
    self.table.setRowCount(0)
    # Populate the QTableWidget with the fetched data
    for registro in registros:
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # Assuming the columns are in the following order:
        # proyecto, cliente, responsable, id_material, material, cantidad, unidad, precio, precioTotal, descripcion, fecha
        for col, value in enumerate(registro[1:]):  # Skip the first column (index 0)
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignCenter)  # Align text to the center

            # Check the value in the "descripcion" column (index 9)
            if col == 9:
                if value.lower() == "entrada":
                    item.setBackground(QColor('#43B02A'))  # Paint the cell green for "entrada"
                elif value.lower() == "devolucion":
                    item.setBackground(QColor('#FF671F'))  # Paint the cell yellow for "devolucion"
                elif value.lower() == "salida":
                    item.setBackground(QColor('#00C1D5'))  # Paint the cell red for "salida"

            self.table.setItem(row_position, col, item)
def seleccion_material_entrada(self):
    """Ventana emergente cuando se da doble click al elemento de la tabla de entrada, 
    se creará una ventana pequeña que tenga un formulario para ingresar la entrada que pongan, 
    proveedor, precio, cantidad, etc."""
    row = self.data_table.currentRow()
    if row >= 0:
        # Obtener información del material seleccionado
        id_item = self.data_table.item(row, 0)  # ID
        nombre_item = self.data_table.item(row, 1)  # Nombre del material
        seccion_item = self.data_table.item(row, 2)  # Sección
        subseccion_item = self.data_table.item(row, 3)  # Subsección
        codigo_barras_item = self.data_table.item(row, 4)  # Codigo de Barras
        cantidad_disponible_item = self.data_table.item(row, 5)  # Cantidad disponible
        unidad_item = self.data_table.item(row, 6)  # Unidad
        precio_unitario_item = self.data_table.item(row, 7)  # Precio Unitario
        precio_total_item = self.data_table.item(row, 8)  # Precio Total
        cantidad_minima_item = self.data_table.item(row, 9)  # Cantidad Minima
        cantidad_maxima_item = self.data_table.item(row, 10)  # Cantidad Maxima
        proveedor_item = self.data_table.item(row, 11)  # Proveedor
        ultima_actualizacion_item = self.data_table.item(row, 12)  # Ultima Actualización  # Unidad de medida

        if nombre_item and cantidad_disponible_item and unidad_item:
            nombre = nombre_item.text()
            cantidad_disponible = cantidad_disponible_item.text()
            unidad = unidad_item.text()

            # Crear una ventana personalizada para ingresar los datos de entrada

            class EntradaDialog(QDialog):
                def __init__(self, nombre, cantidad_disponible, unidad,proveedor_Actual, parent=None):
                    super().__init__(parent)
                    self.setWindowTitle("Registrar Entrada")
                    self.setFixedWidth(400)
                    layout = QVBoxLayout(self)

                    info_label = QLabel(
                        f"<b>Material:</b> {nombre}<br>"
                        f"<b>Cantidad disponible:</b> {cantidad_disponible} {unidad}"
                    )
                    layout.addWidget(info_label)

                    form = QFormLayout()
                    self.proveedor_input = QLineEdit()
                    self.cantidad_input = QLineEdit()
                    self.precio_input = QLineEdit()
                    self.cantidad_input.setPlaceholderText("Ej: 10")
                    self.proveedor_input.setText(proveedor_Actual)
                    self.precio_input.setText('{:2}'.format(precio_unitario_item.text()))

                    form.addRow("Proveedor:", self.proveedor_input)
                    form.addRow("Cantidad:", self.cantidad_input)
                    form.addRow("Precio Unitario:", self.precio_input)
                    layout.addLayout(form)

                    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                    buttons.accepted.connect(self.accept)
                    buttons.rejected.connect(self.reject)
                    layout.addWidget(buttons)

                def get_data(self):
                    return (
                        self.proveedor_input.text(),
                        self.cantidad_input.text(),
                        self.precio_input.text()
                    )

            # Mostrar el diálogo personalizado
            dialog = EntradaDialog(nombre, cantidad_disponible, unidad, proveedor_item.text(), self)
            if dialog.exec_() == QDialog.Accepted:
                try:
                    proveedor, cantidad, precio = dialog.get_data()
                    if proveedor and cantidad and precio:
                        # Aquí puedes procesar y validar los datos ingresados
                        
                        row_position = self.selected_table.rowCount()
                        self.selected_table.insertRow(row_position)
                        self.selected_table.setItem(row_position, 0, QTableWidgetItem(id_item.text()))  # ID
                        self.selected_table.setItem(row_position, 1, QTableWidgetItem(nombre_item.text() ))  # Nombre
                        self.selected_table.setItem(row_position, 2, QTableWidgetItem(seccion_item.text() ))  # Sección
                        self.selected_table.setItem(row_position, 3, QTableWidgetItem(subseccion_item.text() ))  # Subsección
                        self.selected_table.setItem(row_position, 4, QTableWidgetItem(codigo_barras_item.text()))  # Codigo De Barras
                        self.selected_table.setItem(row_position, 5, QTableWidgetItem(cantidad))  # Cantidad Disponible
                        self.selected_table.setItem(row_position, 6, QTableWidgetItem(unidad_item.text() ))  # Unidad
                        self.selected_table.setItem(row_position, 7, QTableWidgetItem(precio))  # Precio Unitario
                        self.selected_table.setItem(row_position, 8, QTableWidgetItem(str(float(cantidad)*float(precio))))  # Precio Total
                        self.selected_table.setItem(row_position, 9, QTableWidgetItem(cantidad_minima_item.text()))  # Cantidad Minima
                        self.selected_table.setItem(row_position, 10, QTableWidgetItem(cantidad_maxima_item.text() ))  # Cantidad Maxima
                        self.selected_table.setItem(row_position, 11, QTableWidgetItem(proveedor))  # Proveedor
                        self.selected_table.setItem(row_position, 12, QTableWidgetItem(ultima_actualizacion_item.text()))  # Ultima Actualización  # Limpiar la tabla seleccionada
                except Exception as e:
                    QMessageBox.warning(
                        self, "Error", f"Error al registrar la entrada: {str(e)}"
                    )        
                  

            else:
                    QMessageBox.warning(
                        self, "Error", "Todos los campos son obligatorios."
                    )    


def generar_entrada_material(self):
    """Genera el PDF con los datos de la tabla seleccionada."""

    responsable = self.entry_responsable.text()

    if responsable == "":
        QMessageBox.warning(self, "Error", "Por favor, ingrese el nombre del responsable.")
        return
    productos = []
    
    for row in range(self.selected_table.rowCount()):
        item = {
            "id": self.selected_table.item(row, 0).text(),
            "nombre": self.selected_table.item(row, 1).text(),
            "seccion": self.selected_table.item(row, 2).text(),
            "subseccion": self.selected_table.item(row, 3).text(),
            "codigo_barras": self.selected_table.item(row, 4).text(),
            "cantidad": self.selected_table.item(row, 5).text(),
            "unidad": self.selected_table.item(row, 6).text(),
            "precio_unitario": self.selected_table.item(row, 7).text(),
            "precio_total": self.selected_table.item(row, 8).text(),
            "cantidad_minima": self.selected_table.item(row, 9).text(),
            "cantidad_maxima": self.selected_table.item(row, 10).text(),
            "proveedor": self.selected_table.item(row, 11).text(),
            "ultima_actualizacion": self.selected_table.item(row, 12).text(),
        }
        productos.append(item)

    print(productos)

    generar_pdf_simple(data={
            "cliente": 'N/A',
            "proyecto": "Almacen",
            "responsable": responsable,
            "fecha": fecha_actual(),
            "productos": productos,
        }, save_directory="./Entradas", descripcion="Entrada") # Cambia el directorio según sea necesario
        

    agregar_entrada_material(responsable, productos)
    actualizar_cantidad_entrada(productos)

    self.selected_table.setRowCount(0)  # Limpiar la barra de búsqueda