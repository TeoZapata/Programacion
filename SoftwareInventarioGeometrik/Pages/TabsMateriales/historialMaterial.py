from PyQt5.QtWidgets import (QDateEdit, QLineEdit, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget,QComboBox)
from PyQt5.QtCore import Qt, QSize,QDate
from PyQt5.QtGui import QFont, QIcon
from Style import *

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
        filter_layout.addWidget(self.responsible_input)

        # Buscar por concepto
        self.concept_input = QComboBox()
        self.concept_input.addItems(["Devolución", "Entrada", "Salida"])
        self.concept_input.setStyleSheet(COMBOBOX_GENERAL_DESIGN)
        filter_layout.addWidget(self.concept_input)

        # Buscar por fechas
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setDate(QDate(2025, 1, 1))  # Set start date to January 1, 2025
        self.date_input.setStyleSheet(QDATEEDIT_GENERAL_DESIGN)  # Apply appropriate style
        filter_layout.addWidget(self.date_input)

        # Botón de búsqueda
        self.search_button = QPushButton("Buscar")
        self.search_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        filter_layout.addWidget(self.search_button)

        self.layout.addLayout(filter_layout)

        # Tabla de visualización
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Example: 4 columns
        self.table.setHorizontalHeaderLabels(["Fecha", "Responsable", "Concepto", "Detalles"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { border: 1px solid #ccc; }")
        self.layout.addWidget(self.table)

        # Botón para generar reporte
        self.report_button = QPushButton("Generar Reporte")
        self.report_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.layout.addWidget(self.report_button)