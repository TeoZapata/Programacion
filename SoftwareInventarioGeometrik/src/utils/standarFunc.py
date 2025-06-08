
from PyQt5.QtWidgets import QLineEdit,QTableWidgetItem, QMessageBox,QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from Style import  *
from DataBase.storeDB import *
from src.utils.getCodeBar import getCodeBar
from src.utils.getDate import fecha_actual



def clear_entry(listaWidget: list, confirm:bool=False) -> None:

    """Limpia el campo de entrada y establece un nuevo marcador de posición."""
    lista:list[QLineEdit] = listaWidget
    if not confirm:
        for index, i in enumerate(lista):
            if not (index == 2 or index ==3 or index ==6 or index ==4):
                i.clear()
    else:
        for index, i in enumerate(lista):
            i.clear()
            if index == 4:
                i.setText(fecha_actual())
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

            # Asignar variables explícitas a cada campo de la base de datos
            id_producto = material[0]
            nombre = material[1]
            seccion = material[2]
            barcode = material[3]
            cantidad = int(material[4])
            unidad = material[5]
            precio = material[6]
            precio_total = material[7]
            cantidad_minima = int(material[8])
            cantidad_maxima = int(material[9])
            proveedor = material[10]
            fecha_compra = material[11]
            subcategoria = material[12]

            # Crear QTableWidgetItem para cada columna
            item_id = QTableWidgetItem(str(id_producto))
            item_id.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(row_position, 0, item_id)

            item_nombre = QTableWidgetItem(str(nombre))
            item_nombre.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(row_position, 1, item_nombre)

            item_seccion = QTableWidgetItem(str(seccion))
            item_seccion.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(row_position, 2, item_seccion)

            item_subcategoria = QTableWidgetItem(str(subcategoria))
            item_subcategoria.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(row_position, 3, item_subcategoria)

            item_barcode = QTableWidgetItem(str(barcode))
            item_barcode.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(row_position, 4, item_barcode)

            item_cantidad = QTableWidgetItem(str(cantidad))
            item_cantidad.setTextAlignment(Qt.AlignCenter)
            # Aplicar color según la cantidad
            if cantidad == 0:
                item_cantidad.setBackground(Qt.red)
            elif cantidad < cantidad_minima:
                item_cantidad.setBackground(QColor("orange"))
            elif cantidad_minima <= cantidad <= cantidad_maxima:
                item_cantidad.setBackground(Qt.green)
            else:
                item_cantidad.setBackground(QColor('#E10098'))
            self.data_table.setItem(row_position, 5, item_cantidad)

            item_unidad = QTableWidgetItem(str(unidad))
            item_unidad.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(row_position, 6, item_unidad)

            item_precio = QTableWidgetItem(str(precio))
            item_precio.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(row_position, 7, item_precio)

            item_precio_total = QTableWidgetItem(str(precio_total))
            item_precio_total.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(row_position, 8, item_precio_total)

            item_cantidad_minima = QTableWidgetItem(str(cantidad_minima))
            item_cantidad_minima.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(row_position, 9, item_cantidad_minima)

            item_cantidad_maxima = QTableWidgetItem(str(cantidad_maxima))
            item_cantidad_maxima.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(row_position, 10, item_cantidad_maxima)

            item_proveedor = QTableWidgetItem(str(proveedor))
            item_proveedor.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(row_position, 11, item_proveedor)

            item_fecha_compra = QTableWidgetItem(str(fecha_compra))
            item_fecha_compra.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(row_position, 12, item_fecha_compra)

            
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
    seccion = lista[2].currentText()
    subcategoria = lista[3].currentText()
    barcode = lista[4].text()
    cantidad = lista[5].text()
    unidad = lista[6].currentText()
    precio = lista[7].text()
    precioTotal = round(float(precio) * float(cantidad), 2) if cantidad else 0.0
    cantidad_minima = lista[9].text()
    cantidad_maxima = lista[10].text()
    proveedor = lista[11].text()
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
            "INSERT INTO inventario (nombre, seccion, barcode, cantidad, unidad, precio, precioTotal, cantidad_minima, cantidad_maxima, proveedor, fecha_compra, subcategoria) VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (nombre, seccion, barcode, cantidad, unidad, precio, precioTotal, cantidad_minima, cantidad_maxima, proveedor,fecha, subcategoria)
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
    # Verificar si todos los campos están llenos

    # Obtener los nuevos datos de los campos de entrada
    id_producto = self.line_edits['ID'].text()
    nombre = self.line_edits['Nombre'].text()
    seccion = self.line_edits['Sección'].currentText()
    subcategoria = self.line_edits['Subsección'].currentText()
    barcode = self.line_edits['Código de Barras'].text()
    cantidad = self.line_edits['Cantidad Disponible'].text()
    unidad = self.line_edits['Unidad de Medida'].currentText()
    precio = self.line_edits['Precio Unitario'].text()
    precioTotal = round(float(precio) * float(cantidad), 2) if cantidad else 0.0
    cantidad_minima = self.line_edits['Cantidad Mínima'].text()
    cantidad_maxima = self.line_edits['Cantidad Máxima'].text()
    proveedor = self.line_edits['Proveedor'].text()
    
    if not all([nombre, seccion, cantidad, unidad, precio, cantidad_minima, cantidad_maxima, proveedor]):
        QMessageBox.warning(None, "Error", "Por favor, completa todos los campos.")
        return
    
    print(f"ID: {id_producto}, Nombre: {nombre}, Sección: {seccion}, Código de Barras: {barcode}, Cantidad: {cantidad}, Unidad: {unidad}, Precio: {precio}, Precio Total: {precioTotal}, Cantidad Mínima: {cantidad_minima}, Cantidad Máxima: {cantidad_maxima}, Proveedor: {proveedor}, Subcategoría: {subcategoria}")

    # Actualizar el producto en la base de datos
    db = conex()
    db.ejecutar_consulta(
        "UPDATE inventario SET nombre=?, seccion=?, barcode=?, cantidad=?, unidad=?, precio=?, precioTotal=?, cantidad_minima=?, cantidad_maxima=?, proveedor=? , subcategoria=?  WHERE id=?",
        (nombre, seccion, barcode, cantidad, unidad, precio, precioTotal, cantidad_minima, cantidad_maxima, proveedor, subcategoria, id_producto)
    )
    # Limpiar los campos de entrada 

def doble_click(self) -> None:
    """Maneja el evento de doble clic en la tabla."""
    # Obtener el elemento seleccionado
    try:
        item = self.data_table.currentItem()
        if item is None:
            QMessageBox.warning(None, "Error", "No se seleccionó ningún elemento.")
            return

        # Obtener la fila del elemento seleccionado
        row = item.row()
        # Obtener el ID del producto de la primera columnad

        self.line_edits['ID'].setText(self.data_table.item(row, 0).text())
        self.line_edits['Nombre'].setText(self.data_table.item(row, 1).text())
        self.line_edits['Sección'].setCurrentText(self.data_table.item(row, 2).text())
        self.line_edits['Subsección'].setCurrentText(self.data_table.item(row, 3).text())
        self.line_edits['Código de Barras'].setText(self.data_table.item(row, 4).text())
        self.line_edits['Cantidad Disponible'].setText(self.data_table.item(row, 5).text())
        self.line_edits['Unidad de Medida'].setCurrentText(self.data_table.item(row, 6).text())
        self.line_edits['Precio Unitario'].setText(self.data_table.item(row, 7).text())
        self.line_edits['Precio Total'].setText(self.data_table.item(row, 8).text())
        self.line_edits['Cantidad Mínima'].setText(self.data_table.item(row, 9).text())
        self.line_edits['Cantidad Máxima'].setText(self.data_table.item(row, 10).text())
        self.line_edits['Proveedor'].setText(self.data_table.item(row, 11).text())
        self.line_edits['Última Fecha de Actualización'].setText(self.data_table.item(row, 12).text())
        
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Ocurrió un error al manejar el doble clic: {str(e)}")
        return

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
    try:

        ok = QMessageBox.question(
            None,
            "Confirmar Eliminación",
            "¿Estás seguro de que deseas eliminar este proyecto? Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )
        if ok != QMessageBox.Yes:
            return
        row = item.row()
        id_proyecto = self.projectsTable.item(row, 0).text()
        db = conex()
        db.ejecutar_consulta("DELETE FROM proyectos WHERE id=?", (id_proyecto,))
        QMessageBox.information(None, "Éxito", "Proyecto eliminado correctamente.")
        cargar_proyecto_tabla(self)
        
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al eliminar el proyecto: {str(e)}")
        return

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

def obtener_nombres_proyectos(combobox, tabla):
    """Carga los nombres de los proyectos desde la base de datos."""
    db = conex()
    proyectos = db.ejecutar_consulta(f"SELECT nombre FROM {tabla}")
    combobox.clear()  # Limpiar el combobox antes de agregar nuevos elementos
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

    self.selected_table.setRowCount(0)

def agregar_salida_material(data):
    
    db = conex()
    for i in range(len(data['productos'])):
        
        db.ejecutar_consulta("INSERT INTO registro (proyecto,cliente,responsable,id_material,codigo,material,cantidad,unidad,precio,precioTotal,descripcion,fecha) VALUES (?,?,?,?,?,?,?,?,?,?,?,? )",
                            (data['proyecto'],
                            data['cliente'],
                            data['responsable'],
                            data['productos'][i]['id'],
                            data['productos'][i]['codigo_barras'],
                            data['productos'][i]['nombre'],
                            data['productos'][i]['cantidad'],
                            data['productos'][i]['unidad'],
                            data['productos'][i]['precio_unitario'],
                            data['productos'][i]['precio_total'],
                            'salida',
                            data['fecha']))
        db.ejecutar_consulta("UPDATE inventario SET cantidad=cantidad-? WHERE id=?", (data['productos'][i]['cantidad'], data['productos'][i]['id']))
        db.ejecutar_consulta("UPDATE inventario SET precioTotal = cantidad * precio WHERE id = ?", (data['productos'][i]['id'],))

    db.ejecutar_consulta("UPDATE informacion SET cantSalidas = cantSalidas + 1 WHERE id = 0")

        
def click_tablaDevolucion(self):
    row = self.table.currentRow()
    id_salida = self.table.item(row, 0).text()
    nombre = self.table.item(row, 1).text()
    cliente = self.table.item(row, 2).text()
    responsable = self.table.item(row, 3).text()
    id_material = self.table.item(row, 4).text()
    codigo = self.table.item(row, 5).text()
    material = self.table.item(row, 6).text()
    cantida = self.table.item(row, 7).text()
    unidad = self.table.item(row, 8).text()
    precio_unitario = self.table.item(row, 9).text()

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
        self.selected_table.setItem(row_position, 5, QTableWidgetItem(codigo))
        self.selected_table.setItem(row_position, 6, QTableWidgetItem(material))
        self.selected_table.setItem(row_position, 7, QTableWidgetItem(str(cantidad_ingresada)))
        self.selected_table.setItem(row_position, 8, QTableWidgetItem(unidad))
        self.selected_table.setItem(row_position, 9, QTableWidgetItem(precio_unitario))
        self.selected_table.setItem(row_position, 10, QTableWidgetItem(str(int(precio_unitario)*int(cantidad_ingresada))))

def informacion_cliente(self):
    """obtiene los datos en los ordenes de la tabla clientes"""
    proyecto = self.entry_proyecto.currentText()

    try:
        db = conex()
        db.iniciar_bd()
        datos = db.ejecutar_consulta("SELECT cliente, ubicacion direccion FROM proyectos WHERE nombre = ?", (proyecto,))
        if datos:
            cliente = datos[0][0]
            proyecto = datos[0][1]
            return cliente, proyecto
        else:
            QMessageBox.warning(None, "Error", "No se encontró información del cliente.")
            return None

       
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Error al obtener la información del cliente: {str(e)}")
        return None

def agregar_entrada_material(responsable, productos):
    """
    Agrega registros de entrada para una lista de productos seleccionados.
    Cada producto debe ser un diccionario con la estructura especificada.
    """
    db = conex()
    for producto in productos:
        db.ejecutar_consulta(
            "INSERT INTO registro (proyecto,cliente,responsable,id_material,material,cantidad,unidad,precio,precioTotal,descripcion,fecha) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                'Almacen',                # proyecto
                'N/A',                    # cliente
                responsable,              # responsable
                producto['id'],           # id_material
                producto['nombre'],       # material
                producto['cantidad'], # cantidad
                producto['unidad'],       # unidad
                producto['precio_unitario'],     # precio
                producto['precio_total'],        # precioTotal
                'entrada',                # descripcion
                fecha_actual()                     # fecha
            )
        )
    
    db.ejecutar_consulta("UPDATE informacion SET cantEntradas = cantEntradas + 1 WHERE id = 0")
    

def actualizar_cantidad_entrada(productos):
    """Actualiza la cantidad de los productos en la base de datos después de una entrada."""
    for dato in productos:

        db = conex()
        if db:
            # Actualizar la cantidad en la base de datos
            db.ejecutar_consulta(
                "UPDATE inventario SET cantidad=cantidad+? , precio=?, proveedor=? WHERE id=?",
                (dato['cantidad'], dato['precio_unitario'], dato['proveedor'],dato['id'])
            
            )
            db.ejecutar_consulta("UPDATE inventario SET precioTotal = cantidad * precio WHERE id = ?", (dato['id'],))
def agregar_empleado(nombre, cedula, cargo, telefono, fechaRegistro):
    """Agrega un nuevo empleado a la base de datos."""
    ok = QMessageBox.question(
        None,
        "Confirmar Agregar Empleado",
        "¿Estás seguro de que deseas agregar este empleado?",
        QMessageBox.Yes | QMessageBox.No
    )
    if ok != QMessageBox.Yes:
        return
    

    db = conex()
    try:
        db.ejecutar_consulta(
            "INSERT INTO empleados (nombre, cedula, cargo, telefono, fecha) VALUES (?, ?, ?, ?, ?)",
            (nombre, cedula, cargo, telefono, fechaRegistro)
        )
        QMessageBox.information(None, "Éxito", "Empleado agregado correctamente.")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al agregar el empleado: {str(e)}")
        return

def cargar_empleados(tabla):
    """Actualiza la tabla de empleados con los datos de la base de datos."""
    tabla.setRowCount(0)  # Limpiar la tabla antes de cargar nuevos datos
    db = conex()
    empleados = db.ejecutar_consulta("SELECT * FROM empleados")
    for empleado in empleados:
        row_position = tabla.rowCount()
        tabla.insertRow(row_position)
        for column, data in enumerate(empleado):
            item = QTableWidgetItem(str(data))
            item.setTextAlignment(Qt.AlignCenter)
            tabla.setItem(row_position, column, item)

def doble_click_empleado(tabla, line_edits):
    """Maneja el evento de doble clic en la tabla de empleados."""
    item = tabla.currentItem()
    if item is None:
        QMessageBox.warning(None, "Error", "No se seleccionó ningún empleado.")
        return

    row = item.row()
    # Obtener los datos del empleado seleccionado
    id_empleado = tabla.item(row, 0).text()
    nombre = tabla.item(row, 1).text()
    cedula = tabla.item(row, 2).text()
    cargo = tabla.item(row, 3).text()
    telefono = tabla.item(row, 4).text()
    fecha_registro = tabla.item(row, 5).text()

    # Mostrar los datos en los campos de entrada
    line_edits['ID'].setText(id_empleado)
    line_edits['Nombre'].setText(nombre)
    line_edits['Cedula'].setText(cedula)
    line_edits['Cargo'].setCurrentText(cargo)
    line_edits['Telefono'].setText(telefono)
    line_edits['Fecha'].setText(fecha_registro)
def eliminar_empleado(current_item):
    """Elimina el empleado seleccionado de la base de datos y de la tabla."""

    if current_item is None:
        QMessageBox.warning(None, "Error", "No se seleccionó ningún empleado.")
        return

    row = current_item.row()
    id_empleado = current_item.tableWidget().item(row, 0).text()
    nombre = current_item.tableWidget().item(row, 1).text()

    ok = QMessageBox.question(
        None,
        "Confirmar Eliminación",
        f"¿Estás seguro de que deseas eliminar a {nombre} con ID {id_empleado}?",
        QMessageBox.Yes | QMessageBox.No
    )
    if ok != QMessageBox.Yes:
        return

    db = conex()
    try:
        db.ejecutar_consulta("DELETE FROM empleados WHERE id=?", (id_empleado,))
        QMessageBox.information(None, "Éxito", "Empleado eliminado correctamente.")
        cargar_empleados(current_item.tableWidget())
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al eliminar el empleado: {str(e)}")

def editar_empleado(data: dict):
    """Edita los datos del empleado seleccionado en la base de datos."""
    id_empleado = data['ID'].text()
    nombre = data['Nombre'].text()
    cedula = data['Cedula'].text()
    cargo = data['Cargo'].currentText()
    telefono = data['Telefono'].text()

    if not all([id_empleado, nombre, cedula, cargo, telefono]):
        QMessageBox.warning(None, "Error", "Por favor, completa todos los campos.")
        return

    db = conex()
    try:
        db.ejecutar_consulta(
            "UPDATE empleados SET nombre=?, cedula=?, cargo=?, telefono=? WHERE id=?",
            (nombre, cedula, cargo, telefono, id_empleado)
        )
        QMessageBox.information(None, "Éxito", "Empleado editado correctamente.")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al editar el empleado: {str(e)}")

def agregar_proveedor(NIT,Nombre,Dirección,Electrónico,Teléfono,Ciudad,Fecha_Registro ):
    """Agrega un nuevo proveedor a la base de datos."""
    ok = QMessageBox.question(
        None,
        "Confirmar Agregar Proveedor",
        "¿Estás seguro de que deseas agregar este proveedor?",
        QMessageBox.Yes | QMessageBox.No
    )
    if ok != QMessageBox.Yes:
        return
    if not all([NIT, Nombre, Dirección, Electrónico, Teléfono, Ciudad, Fecha_Registro]):
        QMessageBox.warning(None, "Error", "Por favor, completa todos los campos.")
        return
    db = conex()
    try:
        db.ejecutar_consulta(
            "INSERT INTO proveedores (nit, nombre, direccion, email, telefono, ciudad, fecha) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (NIT, Nombre, Dirección, Electrónico, Teléfono, Ciudad, Fecha_Registro)
        )
        QMessageBox.information(None, "Éxito", "Proveedor agregado correctamente.")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al agregar el proveedor: {str(e)}")

def cargar_proveedores(tabla):
    """Actualiza la tabla de proveedores con los datos de la base de datos."""
    tabla.setRowCount(0)  # Limpiar la tabla antes de cargar nuevos datos
    db = conex()
    proveedores = db.ejecutar_consulta("SELECT * FROM proveedores")
    for proveedor in proveedores:
        row_position = tabla.rowCount()
        tabla.insertRow(row_position)
        for column, data in enumerate(proveedor):
            item = QTableWidgetItem(str(data))
            item.setTextAlignment(Qt.AlignCenter)
            tabla.setItem(row_position, column, item)

def doble_click_proveedor(tabla, line_edits):
    """Maneja el evento de doble clic en la tabla de proveedores."""
    item = tabla.currentItem()
    if item is None:
        QMessageBox.warning(None, "Error", "No se seleccionó ningún proveedor.")
        return

    row = item.row()
    # Obtener los datos del proveedor seleccionado
    id_proveedor = tabla.item(row, 0).text()
    nit = tabla.item(row, 1).text()
    nombre = tabla.item(row, 2).text()
    email = tabla.item(row, 3).text()
    telefono = tabla.item(row, 4).text()
    direccion = tabla.item(row, 5).text()
    ciudad = tabla.item(row, 6).text()
    fecha_registro = tabla.item(row, 7).text()

    # Mostrar los datos en los campos de entrada
    line_edits['ID'].setText(id_proveedor)
    line_edits['NIT'].setText(nit)
    line_edits['Nombre'].setText(nombre)
    line_edits['Direccion'].setText(direccion)
    line_edits['Email'].setText(email)
    line_edits['Telefono'].setText(telefono)
    line_edits['Ciudad'].setText(ciudad)
    line_edits['Fecha'].setText(fecha_registro)

def editar_proveedor(data: dict):
    """Edita los datos del proveedor seleccionado en la base de datos."""
    id_proveedor = data['ID'].text()
    nit = data['NIT'].text()
    nombre = data['Nombre'].text()
    direccion = data['Direccion'].text()
    email = data['Email'].text()
    telefono = data['Telefono'].text()
    ciudad = data['Ciudad'].text()

    if not all([id_proveedor, nit, nombre, direccion, email, telefono, ciudad]):
        QMessageBox.warning(None, "Error", "Por favor, completa todos los campos.")
        return
    ok = QMessageBox.question(None, "Confirmar Edición", "¿Esta seguro de realizar el cambio?",QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    if ok != QMessageBox.Yes: 
        return;

    db = conex()
    try:
        db.ejecutar_consulta(
            "UPDATE proveedores SET nit=?, nombre=?, direccion=?, email=?, telefono=?, ciudad=? WHERE id=?",
            (nit, nombre, direccion, email, telefono, ciudad, id_proveedor)
        )
        QMessageBox.information(None, "Éxito", "Proveedor editado correctamente.")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al editar el proveedor: {str(e)}")

def search_herramienta(clasificacion, subclasificacion, digitos, linesEdit:dict):
    if not all([clasificacion, subclasificacion, digitos]):
        return
    ID = '71'+clasificacion+subclasificacion+digitos
    print(ID)
    
    try:
        db = conex()
        material = db.ejecutar_consulta("SELECT id, nombre, barcode, cantidad FROM inventario WHERE barcode=?",(ID,))
        if not material:
            QMessageBox.information(None,'Sin Coincidencias', 'No se encontraron resultados para la busqueda')
            
            return
        print(material)
        print(material[0][0])
        linesEdit['ID'].setText(str(material[0][0]))
        linesEdit['Herramienta'].setText(material[0][1])
        linesEdit['Codigo'].setText(material[0][2])
        linesEdit['Cantidad'].setText(str(material[0][3]))
    except Exception as e:
        QMessageBox.warning(None, 'Error', 'Revisa Los datos ingresados')



    


