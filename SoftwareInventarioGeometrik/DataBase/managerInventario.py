
from DataBase.storeDB import storeBD
from PyQt5.QtWidgets import QTableWidgetItem, QInputDialog, QPushButton, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from Style import *
from src.utils.standarFunc import *

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

        for material in selected_data:
            if len(material) < 10:
                QMessageBox.warning(None, "Error", "Datos incompletos en el material seleccionado")
                return

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
                  

        QMessageBox.information(None, "Éxito", "Devolución registrada exitosamente")
        limpiarSelectTable(self)  # Limpiar la tabla seleccionada
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
        nombre_item = self.data_table.item(row, 1)  # Nombre del material
        cantidad_disponible_item = self.data_table.item(row, 2)  # Cantidad disponible
        unidad_item = self.data_table.item(row, 3)  # Unidad de medida

        if nombre_item and cantidad_disponible_item and unidad_item:
            nombre = nombre_item.text()
            cantidad_disponible = cantidad_disponible_item.text()
            unidad = unidad_item.text()

            # Crear una ventana emergente para ingresar los datos de entrada
            dialog = QInputDialog(self)
            dialog.setWindowTitle("Registrar Entrada")
            dialog.setLabelText(
                f"Ingrese los datos para el material '{nombre}':\n"
                f"Cantidad disponible: {cantidad_disponible} {unidad}"
            )
            dialog.setInputMode(QInputDialog.TextInput)
            dialog.setTextValue("Proveedor, Precio, Cantidad")
            ok = dialog.exec_()

            if ok:
                entrada_datos = dialog.textValue()
                # Procesar los datos ingresados
                if entrada_datos:
                    # Aquí puedes dividir los datos ingresados y realizar las operaciones necesarias
                    QMessageBox.information(
                        self, "Entrada Registrada", f"Datos ingresados: {entrada_datos}"
                    )
                else:
                    QMessageBox.warning(
                        self, "Error", "No se ingresaron datos válidos para la entrada."
                    )