
from PyQt5.QtWidgets import QLineEdit,QTableWidgetItem, QMessageBox,QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from Style import  *
from DataBase.storeDB import storeBD
from src.utils.getCodeBar import getCodeBar
from src.utils.getDate import fecha_actual



def clear_entry(listaWidget: list, comp:bool = False ) -> None:

    """Limpia el campo de entrada y establece un nuevo marcador de posición."""
    lista:list[QLineEdit] = listaWidget
    for index, i in enumerate(lista):
        i.clear()
        if index == 3 and comp == False:
            i.setText(getCodeBar())
def cargar_invenario(self):
        """Carga el inventario desde la base de datos y lo muestra en la tabla."""
        # Limpiar la tabla antes de cargar nuevos datos
        self.data_table.setRowCount(0)
        db = conex()
        db.iniciar_bd()
        # Obtener los datos del inventario desde la base de datos
        materiales = db.obtener_inventario()
        # Llenar la tabla con los datos obtenidos
        for material in materiales:
            row_position = self.data_table.rowCount()
            self.data_table.insertRow(row_position)
            for column, data in enumerate(material):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)

                # Aplicar color según la cantidad
                if column == 4:  # Suponiendo que la columna 4 es la de cantidad
                    cantidad = int(data)
                    cantidad_minima = int(material[8])  # Suponiendo que la columna 8 es la cantidad mínima
                    cantidad_maxima = int(material[9])  # Suponiendo que la columna 9 es la cantidad máxima

                    if cantidad == 0:
                        item.setBackground(Qt.red)
                    elif cantidad < cantidad_minima:
                        item.setBackground(QColor("orange"))
                    elif cantidad_minima <= cantidad <= cantidad_maxima:
                        item.setBackground(Qt.green)
                    else: 
                        item.setBackground(QColor('#E10098'))

                self.data_table.setItem(row_position, column, item)
            
def agregar_cliente(self) -> None:
    """Agrega un nuevo cliente a la base de datos."""
    # Obtener los datos de los campos de entrada
    nombre = self.client_name_input.text()
    direccion = self.client_address_input.text()
    telefono = self.client_phone_input.text()
    correo = self.client_email_input.text()
    ciudad = self.client_city_input.text()
    fecha = fecha_actual()

    # Verificar si todos los campos están llenos
    if not all([nombre, direccion, telefono, correo]):
        QMessageBox.warning(None, "Error", "Por favor, completa todos los campos.")
        return

    # Confirmar la acción de agregar cliente
    respuesta = QMessageBox.question(
        None,
        "Confirmar Agregar Cliente",
        "¿Estás seguro de que deseas agregar este cliente?",
        QMessageBox.Yes | QMessageBox.No,
    )

    if respuesta == QMessageBox.Yes:
        try:
            # Crear una instancia de la base de datos
            db = conex()
            # Insertar el cliente en la base de datos
            db.ejecutar_consulta(
                "INSERT INTO clientes (nombre, email, telefono, direccion, ciudad, fecha) VALUES (?, ?, ?, ?, ?, ?)",
                (nombre, correo, telefono, direccion, ciudad, fecha)
            )
            QMessageBox.information(None, "Éxito", "Cliente agregado correctamente.")
            tabla_cliente(self)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al agregar el cliente: {str(e)}")
    else:
        QMessageBox.information(None, "Cancelado", "La acción de agregar cliente fue cancelada.")

def editar_cliente(self) -> None:
    """Edita el cliente seleccionado en la tabla."""
    # Obtener los datos de los campos de entrada
    id_cliente = self.client_id_input.text()
    nombre = self.client_name_input.text()
    direccion = self.client_address_input.text()
    telefono = self.client_phone_input.text()
    correo = self.client_email_input.text()
    ciudad = self.client_city_input.text()

    # Verificar si todos los campos están llenos
    if not all([id_cliente, nombre, direccion, telefono, correo]):
        QMessageBox.warning(None, "Error", "Por favor, completa todos los campos.")
        return

    # Confirmar la acción de editar cliente
    respuesta = QMessageBox.question(
        None,
        "Confirmar Edición de Cliente",
        f"¿Estás seguro de que deseas editar el cliente con ID {id_cliente}?",
        QMessageBox.Yes | QMessageBox.No,
    )

    if respuesta == QMessageBox.Yes:
        try:
            # Actualizar el cliente en la base de datos
            db = conex()
            db.ejecutar_consulta(
                "UPDATE clientes SET nombre=?, email=?, telefono=?, direccion=?, ciudad=? WHERE id=?",
                (nombre, correo, telefono, direccion, ciudad, id_cliente)
            )
            QMessageBox.information(None, "Éxito", "Cliente editado correctamente.")
            tabla_cliente(self)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al editar el cliente: {str(e)}")
    else:
        QMessageBox.information(None, "Cancelado", "La acción de editar cliente fue cancelada.")

def mostrar_cliente(self) -> None:
    """Muestra los datos del cliente seleccionado en los campos de entrada."""
    # Obtener el elemento seleccionado
    item = self.client_table.currentItem()
    if item is None:
        QMessageBox.warning(None, "Error", "No se seleccionó ningún elemento.")
        return

    # Obtener la fila del elemento seleccionado
    row = item.row()
    # Obtener el ID del cliente de la primera columna


    # Mostrar los datos en los campos de entrada
    self.client_id_input.setText(self.client_table.item(row, 0).text())
    self.client_name_input.setText(self.client_table.item(row, 1).text())
    self.client_email_input.setText(self.client_table.item(row, 2).text())
    self.client_phone_input.setText(self.client_table.item(row, 3).text())
    self.client_address_input.setText(self.client_table.item(row, 4).text())
    self.client_city_input.setText(self.client_table.item(row, 5).text())
    self.client_fecha_input.setText(self.client_table.item(row, 6).text())

def eliminar_cliente(self) -> None:
    """Elimina el cliente seleccionado en la tabla."""
    # Verificar si hay un elemento seleccionado
    item = self.client_table.currentItem()
    if item is None:
        QMessageBox.warning(None, "Error", "No se seleccionó ningún cliente.")
        return

    # Obtener la fila del elemento seleccionado
    row = item.row()
    # Obtener el ID del cliente de la primera columna
    id_cliente = self.client_table.item(row, 0).text()

    # Confirmar la eliminación
    respuesta = QMessageBox.question(
        None,
        "Confirmar Eliminación",
        f"¿Estás seguro de que deseas eliminar el cliente con ID {id_cliente}? Esta acción no se puede deshacer.",
        QMessageBox.Yes | QMessageBox.No,
    )

    if respuesta == QMessageBox.Yes:
        try:
            # Eliminar el cliente de la base de datos
            db = conex()
            if db:
                db.ejecutar_consulta(
                    "DELETE FROM clientes WHERE id=?",
                    (id_cliente,)
                )
                # Eliminar la fila de la tabla
                self.client_table.removeRow(row)
                QMessageBox.information(None, "Éxito", "Cliente eliminado correctamente.")
                tabla_cliente(self)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Ocurrió un error al eliminar el cliente: {str(e)}")
    else:
        QMessageBox.information(None, "Cancelado", "La eliminación del cliente fue cancelada.")

def tabla_cliente(self) -> None:
    """Carga la tabla de clientes desde la base de datos."""
    # Limpiar la tabla antes de cargar nuevos datos
    self.client_table.setRowCount(0)

    # Obtener los datos de los clientes desde la base de datos
    db = conex()

    clientes = db.ejecutar_consulta("SELECT * FROM clientes")    
    # Llenar la tabla con los datos obtenidos
    for cliente in clientes:
        row_position = self.client_table.rowCount()
        self.client_table.insertRow(row_position)
        for column, data in enumerate(cliente):
            item = QTableWidgetItem(str(data))
            item.setTextAlignment(Qt.AlignCenter)
            self.client_table.setItem(row_position, column, item)

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
        db = conex()
        if db:
            db.ejecutar_consulta(
                "DELETE FROM inventario WHERE id=?",
                (id_producto,)
            )
            # Limpiar los campos de entrada
            clear_entry(self.line_edits.values())
def conex():
    """Conecta a la base de datos y devuelve el objeto de conexión."""
    try:
        db = storeBD()
        db.iniciar_bd()
        return db
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Error al conectar a la base de datos: {str(e)}")
        return None

def actualizar_cantidad(self,datos:list):
        

    for dato in datos:
        id_producto = dato[0]
        nombre = dato[1]
        cantidad = dato[2]
        precio_unitario = dato[4]
        precio_total = dato[5]

        db = conex()
        if db:
            # Actualizar la cantidad en la base de datos
            db.ejecutar_consulta(
                "UPDATE inventario SET cantidad=cantidad-? WHERE id=?",
                (cantidad, id_producto)
            )
            db.ejecutar_consulta(" UPDATE inventario SET precioTotal = cantidad * precio WHERE id = ? ", (id_producto,))
            print(f"Cantidad actualizada para el producto {nombre} (ID: {id_producto})")

def cargar_proyecto_tabla(self):
    """Carga la tabla de proyectos desde la base de datos."""
    # Limpiar la tabla antes de cargar nuevos datos
    self.projectsTable.setRowCount(0)
    # Obtener los datos de los proyectos desde la base de datos
    db= conex()
    proyectos = db.ejecutar_consulta("SELECT * FROM proyectos")
    # Llenar la tabla con los datos obtenidos
    for proyecto in proyectos:
        row_position = self.projectsTable.rowCount()
        self.projectsTable.insertRow(row_position)
        for column, data in enumerate(proyecto):
            item = QTableWidgetItem(str(data))
            item.setTextAlignment(Qt.AlignCenter)
            self.projectsTable.setItem(row_position, column, item)


def eliminar_proyecto(self) -> None:
    """Elimina el proyecto seleccionado en la tabla."""
    item = self.projectsTable.currentItem()
    if item == None:
        return
    row = item.row()
    id_proyecto = self.projectsTable.item(row, 0).text()
    db = conex()
    db.ejecutar_consulta("DELETE FROM proyectos WHERE id=?", (id_proyecto,))
    QMessageBox.information(None, "Éxito", "Proyecto eliminado correctamente.")
    cargar_proyecto_tabla(self)

def agregar_proyecto(self) -> None:
    """Agrega un nuevo proyecto a la base de datos."""
    nombre = self.projectNameInput.text()
    cliente = self.clientDropdown.currentText()
    capacidad = self.capacityInput.text()
    ubicacion = self.locationInput.text()
    fecha_inicio = self.startDateInput.text()
    if not all([nombre, cliente, capacidad, ubicacion, fecha_inicio]):
        QMessageBox.warning(None, "Error", "Por favor, completa todos los campos.")
        return
    try:
        db = conex()
        db.ejecutar_consulta(
            "INSERT INTO proyectos (nombre, cliente, kwp, ubicacion, fechaCreacion) VALUES (?, ?, ?, ?, ?)",
            (nombre, cliente, capacidad, ubicacion, fecha_inicio)
        )

        QMessageBox.information(None, "Éxito", "Proyecto agregado correctamente.")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al agregar el proyecto: El NOMBRES es UNICO {str(e)}")
        return
    cargar_proyecto_tabla(self)

def edit_proyecto(self):
    """Edita el proyecto seleccionado en la tabla."""

    
    id_project = self.id_project_input.text()
    nombre = self.projectNameInput.text()
    cliente = self.clientDropdown.currentText()
    capacidad = self.capacityInput.text()
    ubicacion = self.locationInput.text()
    
    if not all([id_project, nombre, cliente, capacidad, ubicacion]):
        QMessageBox.warning(None, "Error", "Por favor, completa todos los campos.")
        return

    db = conex()
    db.ejecutar_consulta("UPDATE proyectos SET nombre=?, cliente=?, kwp=?, ubicacion=? WHERE id=? ",
    (nombre, cliente, capacidad, ubicacion, id_project))

    QMessageBox.information(None, "Éxito", "Proyecto editado correctamente.")
    cargar_proyecto_tabla(self)

    


def double_click_tabla_proyecto(self):
    """Maneja el evento de doble clic en la tabla de proyectos."""
    row = self.projectsTable.currentRow()
    id_proyecto = self.projectsTable.item(row, 0).text()
    nombre = self.projectsTable.item(row, 1).text()
    cliente = self.projectsTable.item(row, 2).text()
    ubicacion = self.projectsTable.item(row, 3).text()
    capacidad = self.projectsTable.item(row, 4).text()
    fecha_registro = self.projectsTable.item(row, 5).text()


    self.id_project_input.setText(id_proyecto)
    self.projectNameInput.setText(nombre)
    self.clientDropdown.setCurrentText(cliente)
    self.locationInput.setText(ubicacion)
    self.capacityInput.setText(capacidad)
    self.startDateInput.setText(fecha_registro)

def obtener_nombres_proyectos(combobox):
    """Carga los nombres de los proyectos desde la base de datos."""
    db = conex()
    proyectos = db.ejecutar_consulta("SELECT nombre FROM proyectos")
    combobox.addItems([proyecto[0] for proyecto in proyectos])

def cargar_salidaMaterial_proyecto(self):
    """Carga el material agrupado por proyecto y retorna las listas de materiales con su información."""
    self.table.setRowCount(0)
    proyecto = self.entry_proyecto.currentText()
    db = conex()
    datos = db.ejecutar_consulta('SELECT * FROM registro WHERE proyecto = ? AND descripcion = "salida" ', (proyecto,))
    for dato in datos:
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        for column, data in enumerate(dato):
            item = QTableWidgetItem(str(data))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_position, column, item)

    obtener_nombres_proyectos(self.entry_proyecto)
    self.selected_table.setRowCount(0)

def agregar_salida_material(data):
    
    db = conex()
    for i in range(len(data['productos'])):
        
        db.ejecutar_consulta("INSERT INTO registro (proyecto,cliente,responsable,id_material,material,cantidad,unidad,precio,precioTotal,descripcion,fecha) VALUES (?,?,?,?,?,?,?,?,?,?,? )",
                            (data['proyecto'],
                            data['cliente'],
                            data['responsable'],
                            data['productos'][i]['id'],
                            data['productos'][i]['nombre'],
                            data['productos'][i]['cantidad'],
                            data['productos'][i]['unidad'],
                            data['productos'][i]['precio_unitario'],
                            data['productos'][i]['precio_total'],
                            'salida',
                            data['fecha']))
def click_tablaDevolucion(self):
    row = self.table.currentRow()
    id_salida = self.table.item(row, 0).text()
    nombre = self.table.item(row, 1).text()
    cliente = self.table.item(row, 2).text()
    responsable = self.table.item(row, 3).text()
    id_material = self.table.item(row, 4).text()
    material = self.table.item(row, 5).text()
    cantida = self.table.item(row, 6).text()
    unidad = self.table.item(row, 7).text()
    precio_unitario = self.table.item(row, 8).text()

    if int(cantida)==0:
        QMessageBox.warning(None,"Error", f"{material} tiene una cantidad de 0")
        return

    cantidad_ingresada, ok = QInputDialog.getInt(
        None,
        "Seleccionar Cantidad",
        f"Selecciona la cantidad para el material {material}:",
        min=1,
        max=int(cantida),
        step=1
    )
    if ok:
        QMessageBox.information(None, "Cantidad Seleccionada", f"Has seleccionado {cantidad_ingresada} unidades de {material}.")
        row_position = self.selected_table.rowCount()
        self.selected_table.insertRow(row_position)
        self.selected_table.setItem(row_position, 0, QTableWidgetItem(id_salida))
        self.selected_table.setItem(row_position, 1, QTableWidgetItem(nombre))
        self.selected_table.setItem(row_position, 2, QTableWidgetItem(cliente))
        self.selected_table.setItem(row_position, 3, QTableWidgetItem(responsable))
        self.selected_table.setItem(row_position, 4, QTableWidgetItem(id_material))
        self.selected_table.setItem(row_position, 5, QTableWidgetItem(material))
        self.selected_table.setItem(row_position, 6, QTableWidgetItem(str(cantidad_ingresada)))
        self.selected_table.setItem(row_position, 7, QTableWidgetItem(unidad))
        self.selected_table.setItem(row_position, 8, QTableWidgetItem(precio_unitario))
        self.selected_table.setItem(row_position, 9, QTableWidgetItem(str(int(precio_unitario)*int(cantidad_ingresada))))