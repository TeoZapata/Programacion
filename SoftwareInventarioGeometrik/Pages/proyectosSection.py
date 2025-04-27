import sys
from PyQt5.QtWidgets import (QComboBox, QLineEdit, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from Style import *
from src.utils.getDate import *


class proyectoSecion(QWidget):
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

        # Entrada para el nombre del proyecto
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Ingrese el nombre del proyecto")
        self.project_name_input.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.left_form_layout.addWidget(self.project_name_input)

        # Selección de cliente
        self.client_dropdown = QComboBox()
        self.client_dropdown.setStyleSheet(COMBOBOX_GENERAL_DESIGN)
        self.client_dropdown.addItems(["Cliente 1", "Cliente 2", "Cliente 3", "Cliente 4"])
        self.left_form_layout.addWidget(self.client_dropdown)

        # Entrada para capacidad DC
        self.capacity_input = QLineEdit()
        self.capacity_input.setPlaceholderText("Ingrese la capacidad en kWp")
        self.capacity_input.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.left_form_layout.addWidget(self.capacity_input)

        # Columna derecha del formulario
        self.right_form_layout = QVBoxLayout()

        # Entrada para ubicación del proyecto
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Ingrese la ubicación del proyecto")
        self.location_input.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.right_form_layout.addWidget(self.location_input)

        # Fecha de inicio del proyecto
        self.start_date_input = QLineEdit()
        self.start_date_input.setText(fecha_actual())
        self.start_date_input.setReadOnly(True)
        self.start_date_input.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.right_form_layout.addWidget(self.start_date_input)

        # Estado del proyecto
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(["En Progreso", "Completado", "Pendiente"])
        self.status_dropdown.setStyleSheet(COMBOBOX_GENERAL_DESIGN)
        self.right_form_layout.addWidget(self.status_dropdown)

        # Agregar columnas al formulario principal
        self.form_layout.addLayout(self.left_form_layout)
        self.form_layout.addLayout(self.right_form_layout)
        self.layout.addLayout(self.form_layout)

        # Tabla para mostrar proyectos registrados
        self.table_label = QLabel("Proyectos Registrados:")
        self.table_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.layout.addWidget(self.table_label)

        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(6)
        self.projects_table.setHorizontalHeaderLabels(["Nombre", "Cliente", "Capacidad (kW)", "Ubicación", "Fecha Inicio", "Estado"])
        self.projects_table.setStyleSheet("border: 1px solid #ccc; border-radius: 5px;")
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
                self.projects_table.setItem(row, col, QTableWidgetItem(value))

        self.layout.addWidget(self.projects_table)

        # Botones CRUD
        self.buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Agregar")
        self.add_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        
        self.edit_button = QPushButton("Editar")
        self.edit_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        
        self.delete_button = QPushButton("Eliminar")
        self.delete_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        
        self.save_button = QPushButton("Guardar")
        self.save_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        
        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.edit_button)
        self.buttons_layout.addWidget(self.delete_button)
        self.buttons_layout.addWidget(self.save_button)

        self.layout.addLayout(self.buttons_layout)
