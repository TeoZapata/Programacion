
from PyQt5.QtWidgets import QLineEdit,QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from Style import  *
from DataBase.storeDB import storeBD
from src.utils.getCodeBar import getCodeBar
from src.utils.getDate import fecha_actual


def clear_entry(listaWidget: list) -> None:

    """Limpia el campo de entrada y establece un nuevo marcador de posición."""
    lista:list[QLineEdit] = listaWidget
    for i in lista:
        i.clear()
        i.setStyleSheet(ENTRY_GENERAL_DESIGN)
def cargar_invenario(self):
        """Carga el inventario desde la base de datos y lo muestra en la tabla."""
        # Limpiar la tabla antes de cargar nuevos datos
        self.data_table.setRowCount(0)

        # Obtener los datos del inventario desde la base de datos
        materiales = self.db.obtener_inventario()
        # Llenar la tabla con los datos obtenidos
        for material in materiales:
            row_position = self.data_table.rowCount()
            self.data_table.insertRow(row_position)
            for column, data in enumerate(material):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                self.data_table.setItem(row_position, column, item)
def agregar_producto(listaWidget: list):
     
    lista = list(listaWidget)  # Convertir a lista para que sea subscriptable
    # Obtener los datos de los campos de entrada
    for i in lista:
        print(i.text())
    nombre = lista[0].text()
    barcode = getCodeBar()
    proveedor = lista[2].text()
    seccion = lista[3].text()
    cantidad_minima = lista[4].text()
    cantidad_maxima = lista[5].text()
    cantidad = lista[6].text()
    unidad = lista[7].text()
    precio = lista[8].text()
    precioTotal = round(float(precio) * float(cantidad), 2) if cantidad else 0.0
    # 
    # Verificar si todos los campos están llenos
    if not all([nombre, seccion, cantidad, unidad, precio, cantidad_minima, cantidad_maxima, proveedor]):
        QMessageBox.warning(None, "Error", "Por favor, completa todos los campos.")
    

    # crea una instancia de la base de datos
    db = storeBD()
    db.iniciar_bd()
    # Inserta el producto en la base de datos
    db.ejecutar_consulta(
        "INSERT INTO inventario (nombre, seccion, barcode, cantidad, unidad, precio, precioTotal, cantidad_minima, cantidad_maxima, proveedor, fecha_compra) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (nombre, seccion, barcode, cantidad, unidad, precio, precioTotal, cantidad_minima, cantidad_maxima, proveedor,fecha_actual())
    )
    # Cargar el inventario actualizado
