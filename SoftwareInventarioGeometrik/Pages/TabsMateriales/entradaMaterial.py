from PyQt5.QtWidgets import (QComboBox, QTableWidgetItem, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, QLineEdit, QHeaderView)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from src.utils.getDate import *
from src.utils.standarFunc import *
from Style import *
from DataBase.managerInventario import *

class EntradaMaterial(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()


    def init_ui(self):
        # Layout principal
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)

        # Línea de selección de proyecto y responsable
        top_line = QHBoxLayout()
        top_line.setContentsMargins(0, 0, 0, 0)
        top_line.setSpacing(10)

        label_responsable = QLabel("Factura o Identificación:")
        label_responsable.setStyleSheet(LABEL_GENERAL_DESIGN)

        self.entry_responsable = QLineEdit()
        self.entry_responsable.setPlaceholderText("Ingrese el numero de factura o identificación")
        self.entry_responsable.setFont(QFont("Arial", 10))
        self.entry_responsable.setStyleSheet(ENTRY_GENERAL_DESIGN)

        label_fecha_actual = QLabel("Fecha Actual:")
        label_fecha_actual.setStyleSheet(LABEL_GENERAL_DESIGN)

        self.entry_fecha_actual = QLineEdit()
        self.entry_fecha_actual.setText(fecha_actual())
        self.entry_fecha_actual.setReadOnly(True)
        self.entry_fecha_actual.setStyleSheet(ENTRY_ONLY_READ_DESIGN)


        top_line.addWidget(label_responsable)
        top_line.addWidget(self.entry_responsable,1)
        top_line.addWidget(label_fecha_actual)
        top_line.addWidget(self.entry_fecha_actual,1)

        self.setLayout(self.layout)
        self.layout.addLayout(top_line)

        # Línea de búsqueda de material
        search_line = QHBoxLayout()
        search_line.setSpacing(10)

        self.entry_buscar_material = QLineEdit()
        self.entry_buscar_material.setPlaceholderText("Buscar material existente")
        self.entry_buscar_material.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.entry_buscar_material.textChanged.connect(self.buscar_inventario)

        self.btn_buscar_material = QPushButton("Buscar")
        self.btn_buscar_material.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.btn_buscar_material.clicked.connect(lambda : cargar_invenario(self))

        search_line.addWidget(self.entry_buscar_material)
        search_line.addWidget(self.btn_buscar_material)

        self.layout.addLayout(search_line)

        # Tabla de materiales con cantidad 0
        zero_quantity_table_layout = QVBoxLayout()
        zero_quantity_table_layout.setSpacing(10)

        label_material = QLabel("Material Existente")
        label_material.setAlignment(Qt.AlignLeft)
        zero_quantity_table_layout.addWidget(label_material)

        self.data_table = QTableWidget()
        self.data_table.setColumnCount(13)
        self.data_table.setHorizontalHeaderLabels(["ID","Nombre","Sección","Subsección","Codigo\nDe\nBarras","Cantidad\nDisponible","Unidad", "Precio\nUnitario", "Precio\nTotal", "Cantidad\nMinima","Cantidad\nMaxima","Proveedor", "Ultima\nActualización"])
        self.data_table.setRowCount(0)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacer que la tabla sea de solo lectura
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setSelectionMode(QTableWidget.SingleSelection)
        self.data_table.setShowGrid(False)
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.doubleClicked.connect(lambda: seleccion_material_entrada(self))
        zero_quantity_table_layout.addWidget(self.data_table)

        label_selected_table = QLabel("Material Existente")
        label_selected_table.setAlignment(Qt.AlignLeft)

        zero_quantity_table_layout.addWidget(label_selected_table)

        self.selected_table = QTableWidget()
        self.selected_table.setColumnCount(13)
        self.selected_table.setHorizontalHeaderLabels(["ID","Nombre","Sección","Subsección","Codigo\nDe\nBarras","Cantidad\nDisponible","Unidad", "Precio\nUnitario", "Precio\nTotal", "Cantidad\nMinima","Cantidad\nMaxima","Proveedor", "Ultima\nActualización"])
        self.selected_table.setRowCount(0)
        self.selected_table.setAlternatingRowColors(True)
        self.selected_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacer que la tabla sea de solo lectura
        self.selected_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.selected_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.selected_table.setSelectionMode(QTableWidget.SingleSelection)
        self.selected_table.setShowGrid(False)
        self.selected_table.verticalHeader().setVisible(False)


        zero_quantity_table_layout.addWidget(self.selected_table)

        self.layout.addLayout(zero_quantity_table_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setStyleSheet(BUTTON_GENERAL_DESIGN)


        self.btn_generar_entrada = QPushButton("Generar Entrada de Almacén")
        self.btn_generar_entrada.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.btn_generar_entrada.clicked.connect(lambda: (generar_entrada_material(self), cargar_invenario(self)))
        


        button_layout.addWidget(self.btn_limpiar)
        button_layout.addWidget(self.btn_generar_entrada)

        self.layout.addLayout(button_layout)
    def buscar_inventario(self, text):
        filterTableInventario(self, text)