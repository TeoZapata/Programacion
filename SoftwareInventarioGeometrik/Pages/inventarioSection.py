import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget, QFormLayout, QLineEdit, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTableWidget
from Style import *
from src.utils.getDate import *
from src.utils.getCodeBar import *
from src.utils.standarFunc import *
from src.utils.importExcel import import_excel_and_store_inventory
from src.utils.exportExcel import iniciar_exportacion
from src.utils.calcularInventario import *
from DataBase.storeDB import *



class inventarioSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.db = storeBD()
        self.db.iniciar_bd()
        cargar_invenario(self)


    def init_ui(self):
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        layout_table = QHBoxLayout()
        layout_table.setSpacing(10)

        
        # Crear la tabla para mostrar datos

        self.data_table = QTableWidget()
        self.data_table.setColumnCount(12)  # Número de columnas
        self.data_table.setHorizontalHeaderLabels(["ID","Nombre",
                                "Sección",
                                "Código de Barras",
                                "Cantidad",
                                "Unidad",
                                "Precio",
                                "Precio Total",
                                "Cantidad Mínima",
                                "Cantidad Máxima",
                                "Proveedor",
                                "Fecha de Compra"])  # Encabezados de columna
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacer que la tabla sea de solo lectura
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)  # Seleccionar filas completas
        #quita el borde de la tabla y la enumeracion de filas
        self.data_table.setShowGrid(False)  # Quitar la cuadrícula
        #no motrar la numeracion de filas8
        self.data_table.verticalHeader().setVisible(False)
        # Ocultar encabezado de filas
        self.data_table.setRowCount(0)  # Inicialmente no hay filas
        # hacer que la tabla se organice dando click en el encabezado
        self.data_table.setSortingEnabled(True)
        #hacer que la tabla se ajuste al tamaño de la ventana y organice los encabezados que ocupen el mismo tamaño
        self.data_table.horizontalHeader().setStretchLastSection(True)  # Hacer que la última sección se estire
        #hacer que la tabla se ajuste al ancho
        self.data_table.setColumnWidth(0, 20)  # Ancho de la columna ID
        self.data_table.doubleClicked.connect(lambda: doble_click(self))  # Desactivar la ordenación al hacer doble clic

        # agregar un QForm para la entrada de datos
        entry_formulario = QFormLayout()
        entry_formulario.setSpacing(9)
        # Crear un diccionario para los QLineEdit con sus respectivos placeholders
        self.line_edits = {
            "ID": None,
            "Nombre": None,
            "Sección": None,
            "Código de Barras": None,
            "Cantidad Disponible": None,
            "Unidad de Medida": None,
            "Precio Unitario": None,
            "Precio Total": None,
            "Cantidad Mínima": None,
            "Cantidad Máxima": None,
            "Proveedor": None,
            "Última Fecha de Actualización": None
        }
        
        # Crear los QLineEdit dinámicamente
        for placeholder, widget in self.line_edits.items():
            # Crear QLabel con el nombre del placeholder
            label = QLabel(placeholder)
            label.setStyleSheet(LABEL_GENERAL_DESIGN)
            
            # Crear QLineEdit asociado
            self.line_edit = QLineEdit()
            self.line_edit.setStyleSheet(ENTRY_GENERAL_DESIGN)
            self.line_edit.setPlaceholderText(placeholder)
            
            # Agregar QLabel y QLineEdit al formulario
            entry_formulario.addRow(label, self.line_edit)
            self.line_edits[placeholder] = self.line_edit
            
            # Configurar campos de solo lectura con estilos específicos
            read_only_fields = ["Última Fecha de Actualización", "ID", "Precio Total", "Código de Barras"]
            if placeholder in read_only_fields:
                self.line_edit.setReadOnly(True)
                self.line_edit.setStyleSheet(ENTRY_ONLY_READ_DESIGN)
            if placeholder == "Código de Barras":
                self.line_edit.setText(str(getCodeBar()))  # Generar código de barras automáticamente
            
        # Botón para limpiar las entradas
        bnt_clear = QPushButton("Limpiar")
        bnt_clear.setStyleSheet(BUTTON_GENERAL_DESIGN)
        bnt_clear.setMinimumHeight(30)
        bnt_clear.clicked.connect(lambda: clear_entry(self.line_edits.values()))  # Conectar el botón a la función de limpieza
         # Espacio a la izquierda
        botton_box = QHBoxLayout()
        botton_box.setSpacing(10)

        self.add_button = QPushButton("Agregar")
        self.add_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.add_button.clicked.connect(lambda: (agregar_producto(self.line_edits.values()), cargar_invenario(self)))  # Conectar el botón a la función de agregar producto y cargar inventario nuevamente
        
        self.edit_button = QPushButton("Editar")
        self.edit_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.edit_button.clicked.connect(lambda: (editar_producto(self), cargar_invenario(self)))  # Conectar el botón a la función de editar producto y cargar inventario nuevamente
        
        self.delete_button = QPushButton("Eliminar")
        self.delete_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.delete_button.clicked.connect(lambda: (eliminar_producto(self), cargar_invenario(self)))  # Conectar el botón a la función de eliminar producto y cargar inventario nuevamente
        
        self.import_excel_button = QPushButton("Importar Excel")
        self.import_excel_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.import_excel_button.clicked.connect(self.get_import)  # Conectar el botón a la función de importación
        
        self.export_excel_button = QPushButton("Exportar Excel")
        self.export_excel_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.export_excel_button.clicked.connect(self.get_export)  # Conectar el botón a la función de exportación

        botton_box.addWidget(self.add_button)
        botton_box.addWidget(self.edit_button)
        botton_box.addWidget(self.delete_button)
        botton_box.addWidget(self.import_excel_button)
        botton_box.addWidget(self.export_excel_button)
  
        entry_formulario.addRow(bnt_clear)
        entry_formulario.setFormAlignment(Qt.AlignLeft)  # Alinear formulario a la izquierda



        layout_table.addWidget(self.data_table)
        layout_table.addLayout(entry_formulario)

        

        # Layout para la barra de búsqueda y botones CRUD
        search_and_crud_layout = QHBoxLayout()
        search_and_crud_layout.setSpacing(10)

        # Entrada de búsqueda
        search_input = QLabel("Buscar por nombre:")
        search_input.setFont(QFont("Arial", 12))

        self.entry_search = QLineEdit()
        self.entry_search.setMinimumHeight(30)
        self.entry_search.setPlaceholderText("Ingrese el nombre del producto")
        self.entry_search.setStyleSheet(ENTRY_GENERAL_DESIGN)
        #agrega espacio al ente_search
        self.entry_search.setContentsMargins(10, 0, 0, 0)  # Espacio a la izquierda
        search_and_crud_layout.addWidget(search_input)
        search_and_crud_layout.addWidget(self.entry_search)

        # Botones CRUD
        informacion_almacen_layout = QHBoxLayout()


        btnActualizarEstado = QPushButton("Actualizar Estado")
        btnActualizarEstado.setStyleSheet(BUTTON_GENERAL_DESIGN)
        btnActualizarEstado.setMinimumHeight(60)
        btnActualizarEstado.clicked.connect(lambda: (iniciar_calculo_inventario(self), cargar_invenario(self)))  # Conectar el botón a la función de calcular inventario y cargar inventario nuevamente

        
        # Información del inventario
        labels_and_edits = [
            ("Precio Total Almacén:", "precio_total_edit"),
            ("Estado Rojo:", "estado_rojo_edit"),
            ("Estado Naranja:", "estado_naranja_edit"),
            ("Estado Verde:", "estado_verde_edit")
        ]

        for label_text, edit_attr in labels_and_edits:
            label = QLabel(label_text)
            label.setStyleSheet(LABEL_GENERAL_DESIGN)
            label.setFont(QFont("Arial", 12)) if "Estado" in label_text else None
            edit = QLineEdit()
            edit.setReadOnly(True)
            edit.setStyleSheet(ENTRY_GENERAL_DESIGN)
            setattr(self, edit_attr, edit)
            informacion_almacen_layout.addWidget(label)
            informacion_almacen_layout.addWidget(edit)

        informacion_almacen_layout.addWidget(btnActualizarEstado)
        layout.addLayout(search_and_crud_layout)
        layout.addLayout(layout_table)
        layout.addLayout(botton_box)
        layout.addLayout(informacion_almacen_layout)

        pages_container = QStackedWidget()
        layout.addWidget(pages_container)


    def get_import(self):
        import_excel_and_store_inventory(self.db)
        cargar_invenario(self)
    def get_export(self):
        iniciar_exportacion(self.db)
        cargar_invenario(self)

