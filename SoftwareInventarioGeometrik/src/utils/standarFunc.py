
from PyQt5.QtWidgets import QLineEdit,QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from Style import  *
from DataBase.storeDB import storeBD
from src.utils.getCodeBar import getCodeBar
from src.utils.getDate import fecha_actual


def clear_entry(listaWidget: list) -> None:

    """Limpia el campo de entrada y establece un nuevo marcador de posición."""
    lista:list[QLineEdit] = listaWidget
    for index, i in enumerate(lista):
        i.clear()
        if index == 3:
            i.setText(getCodeBar())
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
    nombre = lista[1].text()
    seccion = lista[2].text()
    barcode = lista[3].text()
    cantidad = lista[4].text()
    unidad = lista[5].text()
    precio = lista[6].text()
    precioTotal = round(float(precio) * float(cantidad), 2) if cantidad else 0.0
    cantidad_minima = lista[8].text()
    cantidad_maxima = lista[9].text()
    proveedor = lista[10].text()
    fecha = fecha_actual()
    # 
    # Verificar si todos los campos están llenos
    if not all([nombre, seccion, cantidad, unidad, precio, cantidad_minima, cantidad_maxima, proveedor]):
        QMessageBox.warning(None, "Error", "Por favor, completa todos los campos.")
        return
    

    # crea una instancia de la base de datos
    try:
        db = storeBD()
        db.iniciar_bd()
        # Inserta el producto en la base de datos
        db.ejecutar_consulta(
            "INSERT INTO inventario (nombre, seccion, barcode, cantidad, unidad, precio, precioTotal, cantidad_minima, cantidad_maxima, proveedor, fecha_compra) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (nombre, seccion, barcode, cantidad, unidad, precio, precioTotal, cantidad_minima, cantidad_maxima, proveedor,fecha)
        )
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Error al agregar el producto: {str(e)}")
        return
    # Cargar el inventario actualizado
def editar_producto(self) -> None:
    """Edita el producto seleccionado en la tabla."""
    # Obtener el elemento seleccionado
    if self.line_edits['ID'] is None:
        QMessageBox.warning(None, "Error", "No hay ID para buscar.")
        return

    # Obtener los nuevos datos de los campos de entrada
    id_producto = self.line_edits['ID'].text()
    nombre = self.line_edits['Nombre'].text()
    seccion = self.line_edits['Sección'].text()
    barcode = self.line_edits['Código de Barras'].text()
    cantidad = self.line_edits['Cantidad Disponible'].text()
    unidad = self.line_edits['Unidad de Medida'].text()
    precio = self.line_edits['Precio Unitario'].text()
    precioTotal = round(float(precio) * float(cantidad), 2) if cantidad else 0.0
    cantidad_minima = self.line_edits['Cantidad Mínima'].text()
    cantidad_maxima = self.line_edits['Cantidad Máxima'].text()
    proveedor = self.line_edits['Proveedor'].text()

    # Verificar si todos los campos están llenos
    if not all([nombre, seccion, cantidad, unidad, precio, cantidad_minima, cantidad_maxima, proveedor]):
        QMessageBox.warning(None, "Error", "Por favor, completa todos los campos.")
        return

    # Actualizar el producto en la base de datos
    db = storeBD()
    db.iniciar_bd()
    db.ejecutar_consulta(
        "UPDATE inventario SET nombre=?, seccion=?, barcode=?, cantidad=?, unidad=?, precio=?, precioTotal=?, cantidad_minima=?, cantidad_maxima=?, proveedor=? WHERE id=?",
        (nombre, seccion, barcode, cantidad, unidad, precio, precioTotal, cantidad_minima, cantidad_maxima, proveedor,id_producto)
    )
    # Limpiar los campos de entrada 

def doble_click(self) -> None:
    """Maneja el evento de doble clic en la tabla."""
    # Obtener el elemento seleccionado
    item = self.data_table.currentItem()
    if item is None:
        QMessageBox.warning(None, "Error", "No se seleccionó ningún elemento.")
        return

    # Obtener la fila del elemento seleccionado
    row = item.row()
    # Obtener el ID del producto de la primera columnad

    self.line_edits['ID'].setText(self.data_table.item(row, 0).text())
    self.line_edits['Nombre'].setText(self.data_table.item(row, 1).text())
    self.line_edits['Sección'].setText(self.data_table.item(row, 2).text())
    self.line_edits['Código de Barras'].setText(self.data_table.item(row, 3).text())
    self.line_edits['Cantidad Disponible'].setText(self.data_table.item(row, 4).text())
    self.line_edits['Unidad de Medida'].setText(self.data_table.item(row, 5).text())
    self.line_edits['Precio Unitario'].setText(self.data_table.item(row, 6).text())
    self.line_edits['Precio Total'].setText(self.data_table.item(row, 7).text())
    self.line_edits['Cantidad Mínima'].setText(self.data_table.item(row, 8).text())
    self.line_edits['Cantidad Máxima'].setText(self.data_table.item(row, 9).text())
    self.line_edits['Proveedor'].setText(self.data_table.item(row, 10).text())
    self.line_edits['Última Fecha de Actualización'].setText(self.data_table.item(row, 11).text())


def eliminar_producto(self) -> None:
    """Elimina el producto seleccionado en la tabla."""
    # Obtener el elemento seleccionado
    item = self.data_table.currentItem()
    if item is None:
        QMessageBox.warning(None, "Error", "No se seleccionó ningún elemento.")
        return

    # Obtener la fila del elemento seleccionado
    row = item.row()
    # Obtener el ID del producto de la primera columna
    id_producto = self.data_table.item(row, 0).text()

    # Confirmar la eliminación
    respuesta = QMessageBox.question(None, "Confirmar Eliminación", f"¿Estás seguro de que deseas eliminar el producto con ID {id_producto}?",
                                     QMessageBox.Yes | QMessageBox.No)
    if respuesta == QMessageBox.Yes:
        # Eliminar el producto de la base de datos
        db = storeBD()
        db.iniciar_bd()
        db.ejecutar_consulta(
            "DELETE FROM inventario WHERE id=?",
            (id_producto,)
        )
        # Limpiar los campos de entrada
        clear_entry(self.line_edits.values())