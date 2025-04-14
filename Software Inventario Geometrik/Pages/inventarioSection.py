import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget, QFormLayout, QLineEdit, QTextEdit)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from Style import *

class inventarioSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        layout_table = QHBoxLayout()
        layout_table.setSpacing(10)

        botton_box = QHBoxLayout()
        botton_box.setSpacing(10)

        self.add_button = QPushButton("Agregar")
        self.add_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.edit_button = QPushButton("Editar")
        self.edit_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.delete_button = QPushButton("Eliminar")
        self.delete_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.import_excel_button = QPushButton("Importar Excel")
        self.import_excel_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.export_excel_button = QPushButton("Exportar Excel")
        self.export_excel_button.setStyleSheet(BUTTON_GENERAL_DESIGN)

        botton_box.addWidget(self.add_button)
        botton_box.addWidget(self.edit_button)
        botton_box.addWidget(self.delete_button)
        botton_box.addWidget(self.import_excel_button)
        botton_box.addWidget(self.export_excel_button)
        # Crear la tabla para mostrar datos

        self.data_table = QTableWidget()
        self.data_table.setColumnCount(8)  # Número de columnas
        self.data_table.setHorizontalHeaderLabels(["ID",
                                                    "Nombre",
                                                    "Codigo\nde\nBarras",
                                                    "Sección",
                                                    "Cantidad\nDisponible",
                                                    "Unidad\nde\nMedida",
                                                    "Precio\nUnitario",
                                                    "Precio\nTotal",
                                                    "Fecha\nde\nActualizacion"])  # Encabezados de columna
        self.data_table.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc;")
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacer que la tabla sea de solo lectura
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)  # Seleccionar filas completas
        # hacer que la tabla se organice dando click en el encabezado
        self.data_table.setSortingEnabled(True)
        #hacer que la tabla se ajuste al tamaño de la ventana y organice los encabezados que ocupen el mismo tamaño
        self.data_table.horizontalHeader().setStretchLastSection(True)  # Hacer que la última sección se estire
        #hacer que la tabla se ajuste al ancho
        
        self.data_table.setColumnWidth(0, 20)  # Ancho de la columna ID

        #agregar un Qfrom para la entrada de datos
        entry_formulario = QFormLayout()
        entry_formulario.setSpacing(10)

        label_name = QLabel("Nombre")
        label_name.setStyleSheet(LABEL_GENERAL_DESIGN)
        line_edit_name = QLineEdit()
        line_edit_name.setStyleSheet(ENTRY_GENERAL_DESIGN)

        label_barcode = QLabel("Codigo de Barras")
        label_barcode.setStyleSheet(LABEL_GENERAL_DESIGN)
        line_edit_barcode = QLineEdit()
        line_edit_barcode.setStyleSheet(ENTRY_GENERAL_DESIGN)

        label_supplier = QLabel("Proveedor")
        label_supplier.setStyleSheet(LABEL_GENERAL_DESIGN)
        line_edit_supplier = QLineEdit()
        line_edit_supplier.setStyleSheet(ENTRY_GENERAL_DESIGN)

        label_section = QLabel("Sección")
        label_section.setStyleSheet(LABEL_GENERAL_DESIGN)
        line_edit_section = QLineEdit()
        line_edit_section.setStyleSheet(ENTRY_GENERAL_DESIGN)

        label_min_quantity = QLabel("Cantidad Minima")
        label_min_quantity.setStyleSheet(LABEL_GENERAL_DESIGN)
        line_edit_min_quantity = QLineEdit()
        line_edit_min_quantity.setStyleSheet(ENTRY_GENERAL_DESIGN)

        label_max_quantity = QLabel("Cantidad Maxima")
        label_max_quantity.setStyleSheet(LABEL_GENERAL_DESIGN)
        line_edit_max_quantity = QLineEdit()
        line_edit_max_quantity.setStyleSheet(ENTRY_GENERAL_DESIGN)

        label_available_quantity = QLabel("Cantidad Disponible")
        label_available_quantity.setStyleSheet(LABEL_GENERAL_DESIGN)
        line_edit_available_quantity = QLineEdit()
        line_edit_available_quantity.setStyleSheet(ENTRY_GENERAL_DESIGN)

        label_unit = QLabel("Unidad de Medida")
        label_unit.setStyleSheet(LABEL_GENERAL_DESIGN)
        line_edit_unit = QLineEdit()
        line_edit_unit.setStyleSheet(ENTRY_GENERAL_DESIGN)

        label_unit_price = QLabel("Precio Unitario")
        label_unit_price.setStyleSheet(LABEL_GENERAL_DESIGN)
        line_edit_unit_price = QLineEdit()
        line_edit_unit_price.setStyleSheet(ENTRY_GENERAL_DESIGN)

        label_total_price = QLabel("Precio Total")
        label_total_price.setStyleSheet(LABEL_GENERAL_DESIGN)
        line_edit_total_price = QLineEdit()
        line_edit_total_price.setStyleSheet(ENTRY_GENERAL_DESIGN)

        label_last_update = QLabel("Ultima Fecha de Actualizacion")
        label_last_update.setStyleSheet(LABEL_GENERAL_DESIGN)
        line_edit_last_update = QLineEdit()
        line_edit_last_update.setStyleSheet(ENTRY_GENERAL_DESIGN)

        entry_formulario.addRow(label_name, line_edit_name)
        entry_formulario.addRow(label_barcode, line_edit_barcode)
        entry_formulario.addRow(label_supplier, line_edit_supplier)
        entry_formulario.addRow(label_section, line_edit_section)
        entry_formulario.addRow(label_min_quantity, line_edit_min_quantity)
        entry_formulario.addRow(label_max_quantity, line_edit_max_quantity)
        entry_formulario.addRow(label_available_quantity, line_edit_available_quantity)
        entry_formulario.addRow(label_unit, line_edit_unit)
        entry_formulario.addRow(label_unit_price, line_edit_unit_price)
        entry_formulario.addRow(label_total_price, line_edit_total_price)
        entry_formulario.addRow(label_last_update, line_edit_last_update)
        entry_formulario.setLabelAlignment(Qt.AlignLeft)  # Alinear etiquetas a la derecha
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

        # Información del inventario
        label_precio_total = QLabel("Precio Total Almacén:")
        label_precio_total.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.precio_total_edit = QLineEdit()
        self.precio_total_edit.setReadOnly(True)
        self.precio_total_edit.setStyleSheet(ENTRY_GENERAL_DESIGN)

        label_estado_rojo = QLabel("Estado Rojo:")
        label_estado_rojo.setStyleSheet(LABEL_GENERAL_DESIGN)
        label_estado_rojo.setFont(QFont("Arial", 12))
        self.estado_rojo_edit = QLineEdit()
        self.estado_rojo_edit.setReadOnly(True)
        self.estado_rojo_edit.setStyleSheet(ENTRY_GENERAL_DESIGN)

        label_estado_naranja = QLabel("Estado Naranja:")
        label_estado_naranja.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.estado_naranja_edit = QLineEdit()
        self.estado_naranja_edit.setReadOnly(True)
        self.estado_naranja_edit.setStyleSheet(ENTRY_GENERAL_DESIGN)

        label_estado_verde = QLabel("Estado Verde:")
        label_estado_verde.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.estado_verde_edit = QLineEdit()
        self.estado_verde_edit.setReadOnly(True)
        self.estado_verde_edit.setStyleSheet(ENTRY_GENERAL_DESIGN)

        # Agregar widgets al layout
        informacion_almacen_layout.addWidget(label_precio_total)
        informacion_almacen_layout.addWidget(self.precio_total_edit)
        informacion_almacen_layout.addWidget(label_estado_rojo)
        informacion_almacen_layout.addWidget(self.estado_rojo_edit)
        informacion_almacen_layout.addWidget(label_estado_naranja)
        informacion_almacen_layout.addWidget(self.estado_naranja_edit)
        informacion_almacen_layout.addWidget(label_estado_verde)
        informacion_almacen_layout.addWidget(self.estado_verde_edit)

        layout.addLayout(search_and_crud_layout)
        layout.addLayout(layout_table)
        layout.addLayout(botton_box)
        layout.addLayout(informacion_almacen_layout)
      
        pages_container = QStackedWidget()
        layout.addWidget(pages_container)