from PyQt5.QtWidgets import (QComboBox, QTableWidgetItem, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, QLineEdit)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from src.utils.getDate import *
from Style import *

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

        self.entry_proyecto = QComboBox()
        self.entry_proyecto.addItems(["Proyecto 1", "Proyecto 2", "Proyecto 3"])
        self.entry_proyecto.setStyleSheet(COMBOBOX_GENERAL_DESIGN)
        self.entry_proyecto.setMinimumWidth(150)

        self.entry_responsable = QLineEdit()
        self.entry_responsable.setPlaceholderText("Ingrese el nombre del responsable")
        self.entry_responsable.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.entry_fecha_actual = QLineEdit()
        self.entry_fecha_actual.setText(fecha_actual())
        self.entry_fecha_actual.setReadOnly(True)
        self.entry_fecha_actual.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.entry_factura = QLineEdit()
        self.entry_factura.setPlaceholderText("Número de factura")
        self.entry_factura.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.btn_buscar_factura = QPushButton("Buscar Factura")
        self.btn_buscar_factura.setStyleSheet(BUTTON_GENERAL_DESIGN)

        top_line.addWidget(self.entry_proyecto)
        top_line.addWidget(self.entry_responsable)
        top_line.addWidget(self.entry_fecha_actual)
        top_line.addWidget(self.entry_factura)
        top_line.addWidget(self.btn_buscar_factura)

        self.setLayout(self.layout)
        self.layout.addLayout(top_line)

        # Línea de búsqueda de material
        search_line = QHBoxLayout()
        search_line.setSpacing(10)

        self.entry_buscar_material = QLineEdit()
        self.entry_buscar_material.setPlaceholderText("Buscar material existente")
        self.entry_buscar_material.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.btn_buscar_material = QPushButton("Buscar")
        self.btn_buscar_material.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.btn_agregar_material = QPushButton("Agregar Material")
        self.btn_agregar_material.setStyleSheet(BUTTON_GENERAL_DESIGN)

        search_line.addWidget(self.entry_buscar_material)
        search_line.addWidget(self.btn_buscar_material)
        search_line.addWidget(self.btn_agregar_material)

        self.layout.addLayout(search_line)

        # Tabla de materiales con cantidad 0
        zero_quantity_table_layout = QVBoxLayout()
        zero_quantity_table_layout.setSpacing(10)

        zero_quantity_table_title = QLabel("Materiales con Cantidad 0")
        zero_quantity_table_title.setAlignment(Qt.AlignLeft)
        zero_quantity_table_title.setFont(QFont("Arial", 14, QFont.Bold))
        zero_quantity_table_layout.addWidget(zero_quantity_table_title)

        self.zero_quantity_table = QTableWidget()
        self.zero_quantity_table.setColumnCount(5)
        self.zero_quantity_table.setHorizontalHeaderLabels(["ID", "Nombre", "Cantidad", "Unidad", "Descripción"])
        self.zero_quantity_table.setRowCount(0)
        self.zero_quantity_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.zero_quantity_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.zero_quantity_table.horizontalHeader().setStretchLastSection(True)

        zero_quantity_table_layout.addWidget(self.zero_quantity_table)

        self.layout.addLayout(zero_quantity_table_layout)

        # Tabla de materiales seleccionados para entrada
        selected_table_layout = QVBoxLayout()
        selected_table_layout.setSpacing(10)

        selected_table_title = QLabel("Materiales Seleccionados para Entrada")
        selected_table_title.setAlignment(Qt.AlignLeft)
        selected_table_title.setFont(QFont("Arial", 14, QFont.Bold))
        selected_table_layout.addWidget(selected_table_title)

        self.selected_table = QTableWidget()
        self.selected_table.setColumnCount(6)
        self.selected_table.setHorizontalHeaderLabels(["ID", "Nombre", "Cantidad", "Unidad", "Descripción", "Eliminar"])
        self.selected_table.setRowCount(0)
        self.selected_table.horizontalHeader().setStretchLastSection(True)

        selected_table_layout.addWidget(self.selected_table)

        self.layout.addLayout(selected_table_layout)

        # Botones de acción
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.btn_generar_entrada = QPushButton("Generar Entrada de Almacén")
        self.btn_generar_entrada.setStyleSheet(BUTTON_GENERAL_DESIGN)

        button_layout.addWidget(self.btn_limpiar)
        button_layout.addWidget(self.btn_generar_entrada)

        self.layout.addLayout(button_layout)
