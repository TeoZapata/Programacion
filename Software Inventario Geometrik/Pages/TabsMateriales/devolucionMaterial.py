from PyQt5.QtWidgets import (QComboBox, QTableWidgetItem, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, QLineEdit)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from src.utils.getDate import *
from Style import *

class DevolucionMaterial(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)

        # Línea de selección de proyecto y responsable
        proyect_line = QHBoxLayout()
        proyect_line.setContentsMargins(0, 0, 0, 0)
        proyect_line.setSpacing(10)

        self.entry_proyecto = QComboBox()
        self.entry_proyecto.addItems(["Proyecto 1", "Proyecto 2", "Proyecto 3"])
        self.entry_proyecto.setStyleSheet(COMBOBOX_GENERAL_DESIGN)

        self.entry_responsable = QLineEdit()
        self.entry_responsable.setPlaceholderText("Ingrese el nombre del responsable")
        self.entry_responsable.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.entry_ubicacion = QLineEdit()
        self.entry_ubicacion.setPlaceholderText("Ubicación del material")
        self.entry_ubicacion.setStyleSheet(ENTRY_GENERAL_DESIGN)
        

        self.entry_fecha_Actual = QLineEdit()
        self.entry_fecha_Actual.setText(fecha_actual())
        self.entry_fecha_Actual.setReadOnly(True)
        self.entry_fecha_Actual.setStyleSheet(ENTRY_GENERAL_DESIGN)

        proyect_line.addWidget(self.entry_responsable)
        proyect_line.addWidget(self.entry_ubicacion)
        proyect_line.addWidget(self.entry_fecha_Actual)

        self.layout.addLayout(proyect_line)

        # Tabla de materiales disponibles
        table_layout = QVBoxLayout()
        table_layout.setSpacing(10)

        table_title = QLabel("Devolucion de Materiales")
        table_title.setAlignment(Qt.AlignLeft)
        table_title.setFont(QFont("Arial", 14, QFont.Bold))
        table_layout.addWidget(table_title)
        table_layout.addWidget(self.entry_proyecto)
        # Crear la tabla de materiales disponibles
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Número de columnas
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Cantidad", "Unidad", "Descripción", "Seleccionar"])
        self.table.setRowCount(0)  # Inicialmente sin filas
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacer que la tabla sea de solo lectura
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # Seleccionar filas completas
        # hacer que la tabla se organice dando click en el encabezado
        self.table.setSortingEnabled(True)
        #hacer que la tabla se ajuste al tamaño de la ventana y organice los encabezados que ocupen el mismo tamaño
        self.table.horizontalHeader().setStretchLastSection(True)

        # Ajustar el comportamiento de las columnas
        self.table.horizontalHeader().setStretchLastSection(True)

        # Agregar una fila de ejemplo con un checkbox en la columna "Seleccionar"
        self.table.setRowCount(1)
        checkbox_item = QTableWidgetItem()
        checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        checkbox_item.setCheckState(Qt.Unchecked)
        self.table.setItem(0, 5, checkbox_item)

        table_layout.addWidget(self.table)

        self.layout.addLayout(table_layout)

        # Tabla de materiales seleccionados
        selected_table_layout = QVBoxLayout()
        selected_table_layout.setSpacing(10)

        selected_table_title = QLabel("Materiales Seleccionados")
        selected_table_title.setAlignment(Qt.AlignLeft)
        selected_table_title.setFont(QFont("Arial", 14, QFont.Bold))
        selected_table_layout.addWidget(selected_table_title)

        # Crear la tabla de materiales seleccionados
        self.selected_table = QTableWidget()
        self.selected_table.setColumnCount(6)  # Número de columnas
        self.selected_table.setHorizontalHeaderLabels(["ID", "Nombre", "Cantidad Seleccionada", "Unidad", "Descripción", "Seleccionar"])
        self.selected_table.setRowCount(0)  # Inicialmente sin filas

        # Ajustar el comportamiento de las columnas
        self.selected_table.horizontalHeader().setStretchLastSection(True)

        selected_table_layout.addWidget(self.selected_table)

        self.layout.addLayout(selected_table_layout)

        # Botones de acción
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setStyleSheet(BUTTON_GENERAL_DESIGN)

        self.btn_generar_recibo = QPushButton("Generar Recibo de Salida")
        self.btn_generar_recibo.setStyleSheet(BUTTON_GENERAL_DESIGN)

        button_layout.addWidget(self.btn_limpiar)
        button_layout.addWidget(self.btn_generar_recibo)

        self.layout.addLayout(button_layout)