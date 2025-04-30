
from DataBase.storeDB import storeBD
from PyQt5.QtWidgets import QTableWidgetItem, QInputDialog, QMessageBox, QWidget
from PyQt5.QtCore import Qt


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
def getManagerInventario(self):
            db = storeBD()
            datos = db.ejecutar_consulta("SELECT * FROM inventario WHERE cantidad > 0")
            print(datos)
            
            # Clear the table before inserting new rows
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
                
                # Add a checkbox for the "Seleccionar" column
                checkbox_item = QTableWidgetItem()
                checkbox_item.setCheckState(Qt.Unchecked)

                
                self.table.setItem(row_position, 6, checkbox_item)
                
                # Connect the checkbox state change to updateSelectedTable
                
            self.table.itemChanged.connect(lambda item: ventana_selec_cantidad(self, item) )  # Connect itemChanged to the function

def ventana_selec_cantidad(self, item):
    """Se abre una ventana para elegir la cantidad cuando se selecciona el checkbox"""
    # Obtener información del material seleccionado
    nombre_item = self.table.item(item.row(), 1)  # Nombre del material
    cantidad_disponible_item = self.table.item(item.row(), 2)  # Cantidad disponible
    unidad_item = self.table.item(item.row(), 3)  # Unidad de medida

    if nombre_item and cantidad_disponible_item and unidad_item:
        nombre = nombre_item.text()
        cantidad_disponible = cantidad_disponible_item.text()
        unidad = unidad_item.text()

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
        
        # Add the selected item to the selected_table
        row_position = self.selected_table.rowCount()
        self.selected_table.insertRow(row_position)
        
        # Copy relevant columns from the main table to the selected_table
        self.selected_table.setItem(row_position, 0, QTableWidgetItem(self.table.item(item.row(), 0).text()))  # ID
        self.selected_table.setItem(row_position, 1, QTableWidgetItem(nombre))  # Nombre
        self.selected_table.setItem(row_position, 2, QTableWidgetItem(str(cantidad)))  # Cantidad seleccionada
        self.selected_table.setItem(row_position, 3, QTableWidgetItem(unidad))  # Unidad
        self.selected_table.setItem(row_position, 4, QTableWidgetItem(self.table.item(item.row(), 4).text()))  # Precio Unitario
        self.selected_table.setItem(row_position, 5, QTableWidgetItem(self.table.item(item.row(), 5).text()))  # Precio Total
     

def updateSelectedTable(self):
            """Update the selected_table with items that are checked in the main table."""
            self.selected_table.setRowCount(0)  # Clear the selected_table

            for row in range(self.table.rowCount()):
                checkbox_item = self.table.item(row, 6)  # Get the checkbox item
                if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                    row_position = self.selected_table.rowCount()
                    self.selected_table.insertRow(row_position)
                    
                    # Copy all columns from the main table to the selected_table
                    for col in range(6):  # Assuming there are 6 columns to copy
                        item = self.table.item(row, col)
                        if item:
                            self.selected_table.setItem(row_position, col, QTableWidgetItem(item.text()))
                    
                    # Copy the quantity to withdraw
                    quantity_item = self.table.item(row, 7)  # Get the quantity item
                    if quantity_item:
                        self.selected_table.setItem(row_position, 6, QTableWidgetItem(quantity_item.text()))  # Add to selected_table

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