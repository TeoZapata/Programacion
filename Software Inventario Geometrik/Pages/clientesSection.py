import sys
from PyQt5.QtWidgets import (QComboBox, QLineEdit, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from Style import *
from src.utils.getDate import *


class clientesSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Formulario de entrada
        self.form_layout = QHBoxLayout()

        # Columna izquierda del formulario
        self.left_form_layout = QVBoxLayout()

        # Entrada para el nombre del cliente
        self.client_name_input = QLineEdit()
        self.client_name_input.setPlaceholderText("Nombre del Cliente")
        self.client_name_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.client_address_input = QLineEdit()
        self.client_address_input.setPlaceholderText("Dirección del Cliente")
        self.client_address_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.left_form_layout.addWidget(self.client_name_input)
        self.left_form_layout.addWidget(self.client_address_input)

        # Columna derecha del formulario
        self.right_form_layout = QVBoxLayout()

        # Entrada para el teléfono del cliente y correo electrónico (lado derecho)
        self.client_phone_input = QLineEdit()
        self.client_phone_input.setPlaceholderText("Teléfono del Cliente")
        self.client_phone_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.client_email_input = QLineEdit()
        self.client_email_input.setPlaceholderText("Correo Electrónico del Cliente")
        self.client_email_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.right_form_layout.addWidget(self.client_phone_input)
        self.right_form_layout.addWidget(self.client_email_input)

        # Agregar columnas al formulario principal
        self.form_layout.addLayout(self.left_form_layout)
        self.form_layout.addLayout(self.right_form_layout)

        self.layout.addLayout(self.form_layout)

        # Tabla para mostrar proyectos registrados
        self.table_label = QLabel("Clientes Registrados:")
        self.table_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.layout.addWidget(self.table_label)

        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(6)
        self.projects_table.setHorizontalHeaderLabels(["Nombre", "Cliente", "Capacidad (kW)", "Ubicación", "Fecha Inicio", "Estado"])
        self.projects_table.setAlternatingRowColors(True)
        self.projects_table.setRowCount(4)

        # Datos ficticios
        sample_data = [
            ["Proyecto A", "Cliente 1", "100", "Ubicación 1", "01/01/2023", "En Progreso"],
            ["Proyecto B", "Cliente 2", "200", "Ubicación 2", "15/02/2023", "Completado"],
            ["Proyecto C", "Cliente 3", "300", "Ubicación 3", "10/03/2023", "Pendiente"],
            ["Proyecto D", "Cliente 4", "400", "Ubicación 4", "20/04/2023", "En Progreso"]
        ]

        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.projects_table.setItem(row, col, item)

        self.layout.addWidget(self.projects_table)

        # Botones CRUD
        self.buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Agregar")
        self.add_button.setIcon(QIcon("icons/add.png"))
        self.add_button.setStyleSheet(BUTTON_GENERAL_DESIGN)

        self.edit_button = QPushButton("Editar")
        self.edit_button.setIcon(QIcon("icons/edit.png"))
        self.edit_button.setStyleSheet(BUTTON_GENERAL_DESIGN)

        self.delete_button = QPushButton("Eliminar")
        self.delete_button.setIcon(QIcon("icons/delete.png"))
        self.delete_button.setStyleSheet(BUTTON_GENERAL_DESIGN)

        self.save_button = QPushButton("Guardar")
        self.save_button.setIcon(QIcon("icons/save.png"))
        self.save_button.setStyleSheet(BUTTON_GENERAL_DESIGN)

        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.edit_button)
        self.buttons_layout.addWidget(self.delete_button)
        self.buttons_layout.addWidget(self.save_button)

        self.layout.addLayout(self.buttons_layout)