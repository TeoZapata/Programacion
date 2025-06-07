from PyQt5.QtWidgets import (QDateEdit, QLineEdit, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QHeaderView, QTableWidget,QComboBox)
from PyQt5.QtCore import Qt, QSize,QDate
from PyQt5.QtGui import QFont, QIcon
from Style import *
from DataBase.managerInventario import *

class HistorialMaterial(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):

        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Filtros de búsqueda
        filter_layout = QHBoxLayout()

        # Buscar por responsable
        self.responsible_input = QLineEdit()
        self.responsible_input.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.responsible_input.setPlaceholderText("Ingrese el nombre del responsable")
        self.responsible_input.textChanged.connect(self.buscar_inventario)
        filter_layout.addWidget(self.responsible_input)

   
        self.search_button = QPushButton("Actualizar Historial")
        self.search_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.search_button.clicked.connect(lambda: tabla_registro_historial(self))
        filter_layout.addWidget(self.search_button)

        self.layout.addLayout(filter_layout)

        # Tabla de visualización
        self.table = QTableWidget()
        self.table.setColumnCount(12)  # Example: 4 columns
        self.table.setHorizontalHeaderLabels(['proyecto' ,
                        'cliente' ,
                        'responsable' ,
                        'id_material' ,
                        'Código',
                        'material' ,
                        'cantidad' ,
                        'unidad' ,
                        'precio' ,
                        'precioTotal' ,
                        'descripcion' ,
                        'fecha' ])
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacer que la tabla sea de solo lectura
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.table)

        # Botón para generar reporte
        self.report_button = QPushButton("Generar Reporte")
        self.report_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.layout.addWidget(self.report_button)   
    def buscar_inventario(self, text):
        filterTable(self, text)