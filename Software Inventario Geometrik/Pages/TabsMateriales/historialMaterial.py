from PyQt5.QtWidgets import (QDateEdit, QLineEdit, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget)
from PyQt5.QtCore import Qt, QSize
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

        # Título
        name_title = QLabel("Historial de Material")
        name_title.setAlignment(Qt.AlignCenter)
        name_title.setFont(QFont("Arial", 20, QFont.Bold))
        self.layout.addWidget(name_title)

        # Filtros de búsqueda
        filter_layout = QHBoxLayout()

        # Buscar por responsable
        responsible_label = QLabel("Responsable:")
        responsible_label.setFont(QFont("Arial", 12))
        self.responsible_input = QLineEdit()
        self.responsible_input.setPlaceholderText("Ingrese el nombre del responsable")
        filter_layout.addWidget(responsible_label)
        filter_layout.addWidget(self.responsible_input)

        # Buscar por concepto
        concept_label = QLabel("Concepto:")
        concept_label.setFont(QFont("Arial", 12))
        self.concept_input = QLineEdit()
        self.concept_input.setPlaceholderText("Ingrese el concepto")
        filter_layout.addWidget(concept_label)
        filter_layout.addWidget(self.concept_input)

        # Buscar por fechas
        date_label = QLabel("Fecha:")
        date_label.setFont(QFont("Arial", 12))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.date_input)

        # Botón de búsqueda
        self.search_button = QPushButton("Buscar")
        self.search_button.setFont(QFont("Arial", 12))
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

 