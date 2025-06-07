from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QTabWidget, QLabel
from .TabsMateriales import *
from Style import *
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


class ProveedoresSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Formulario de entrada
        self.form_layout = QVBoxLayout()

        # Grid layout para organizar los campos
        self.grid_layout = QHBoxLayout()

        # Columna izquierda del formulario
        self.left_form_layout = QFormLayout()

        self.client_id_label = QLabel("ID del Cliente")
        self.client_id_label.setStyleSheet(LABEL_GENERAL_DESIGN)

        self.client_id_input = QLineEdit()
        self.client_id_input.setStyleSheet(ENTRY_ONLY_READ_DESIGN)
        self.client_id_input.setReadOnly(True)

        self.client_name_label = QLabel("Nombre del Cliente")
        self.client_name_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.client_name_input = QLineEdit()
        self.client_name_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.client_address_label = QLabel("Dirección del Cliente")
        self.client_address_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.client_address_input = QLineEdit()
        self.client_address_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.client_city_label = QLabel("Ciudad del Cliente")
        self.client_city_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.client_city_input = QLineEdit()
        self.client_city_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.left_form_layout.addRow(self.client_name_label,self.client_name_input)
        self.left_form_layout.addRow(self.client_address_label,self.client_address_input)
        self.left_form_layout.addRow(self.client_city_label,self.client_city_input)
        self.left_form_layout.addRow(self.client_id_label,self.client_id_input)

        # Columna derecha del formulario
        self.right_form_layout = QFormLayout()

        self.client_phone_label = QLabel("Teléfono del Cliente")
        self.client_phone_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.client_phone_input = QLineEdit()
        self.client_phone_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.client_email_label = QLabel("Correo Electrónico del Cliente")
        self.client_email_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.client_email_input = QLineEdit()
        self.client_email_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.client_fecha_label = QLabel("Fecha de Registro")
        self.client_fecha_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.client_fecha_input = QLineEdit()
        self.client_fecha_input.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.client_fecha_input.setText(fecha_actual())
        self.client_fecha_input.setReadOnly(True)

        self.button_clear=QPushButton("Limpiar Registro")
        self.button_clear.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.button_clear.clicked.connect(lambda: clear_entry([self.client_id_input,self.client_name_input,self.client_address_input,self.client_city_input,self.client_phone_input,self.client_email_input], True))


        self.right_form_layout.addRow(self.client_phone_label,self.client_phone_input)
        self.right_form_layout.addRow(self.client_email_label,self.client_email_input)
        self.right_form_layout.addRow(self.client_fecha_label,self.client_fecha_input)
        self.right_form_layout.addWidget(self.button_clear)

        # Agregar columnas al layout principal
        self.grid_layout.addLayout(self.left_form_layout)
        self.grid_layout.addLayout(self.right_form_layout)

        # Título del formulario
        self.form_layout.addLayout(self.grid_layout)

        self.layout.addLayout(self.form_layout)
        self.buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Agregar")
        self.add_button.setStyleSheet(BUTTON_GENERAL_DESIGN)

        self.edit_button = QPushButton("Editar")
        self.edit_button.setStyleSheet(BUTTON_GENERAL_DESIGN)

        self.delete_button = QPushButton("Eliminar")
        self.delete_button.setStyleSheet(BUTTON_GENERAL_DESIGN)

        self.update_button = QPushButton("Actualizar")
        self.update_button.setStyleSheet(BUTTON_GENERAL_DESIGN)

        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.edit_button)
        self.buttons_layout.addWidget(self.delete_button)
        self.buttons_layout.addWidget(self.update_button)
        self.layout.addLayout(self.buttons_layout)

        # Tabla para mostrar proyectos registrados
        self.table_label = QLabel("HERRAMIENTA DISPONIBLE:")
        self.layout.addWidget(self.table_label)

        self.client_table = QTableWidget()
        self.client_table.setColumnCount(7)
        self.client_table.setHorizontalHeaderLabels(["ID", "Nombre", "Correo", "Telefono", "Dirección", "Ciudad", "Fecha de Registro"])
        self.client_table.setAlternatingRowColors(True)
        self.client_table.horizontalHeader().setStretchLastSection(True)
        self.client_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.client_table.setSelectionMode(QTableWidget.SingleSelection)
        self.client_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacer que la tabla sea de solo lectura
        self.client_table.setSelectionBehavior(QTableWidget.SelectRows)  # Seleccionar filas completas
        #quita el borde de la tabla y la enumeracion de filas
        self.client_table.setShowGrid(False)  # Quitar la cuadrícula
        #no motrar la numeracion de filas8
        self.client_table.verticalHeader().setVisible(False)
        
        


        self.client_table.setRowCount(4)

        # Datos ficticios
        
        self.layout.addWidget(self.client_table)

        # Botones CRUD
