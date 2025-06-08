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

        self.provider_id_label = QLabel("ID")
        self.provider_id_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.provider_id_input = QLineEdit()
        self.provider_id_input.setStyleSheet(ENTRY_ONLY_READ_DESIGN)
        self.provider_id_input.setReadOnly(True)

        self.provider_nit_label = QLabel("NIT")
        self.provider_nit_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.provider_nit_input = QLineEdit()
        self.provider_nit_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.provider_nombre_label = QLabel("Nombre")
        self.provider_nombre_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.provider_nombre_input = QLineEdit()
        self.provider_nombre_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.provider_direccion_label = QLabel("Dirección")
        self.provider_direccion_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.provider_direccion_input = QLineEdit()
        self.provider_direccion_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.left_form_layout.addRow(self.provider_nit_label, self.provider_nit_input)
        self.left_form_layout.addRow(self.provider_nombre_label, self.provider_nombre_input)
        self.left_form_layout.addRow(self.provider_direccion_label, self.provider_direccion_input)
        self.left_form_layout.addRow(self.provider_id_label, self.provider_id_input)

        # Columna derecha del formulario
        self.right_form_layout = QFormLayout()

        self.provider_email_label = QLabel("Correo Electrónico")
        self.provider_email_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.provider_email_input = QLineEdit()
        self.provider_email_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.provider_telefono_label = QLabel("Teléfono")
        self.provider_telefono_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.provider_telefono_input = QLineEdit()
        self.provider_telefono_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.provider_ciudad_label = QLabel("Ciudad")
        self.provider_ciudad_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.provider_ciudad_input = QLineEdit()
        self.provider_ciudad_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.provider_fecha_label = QLabel("Fecha de Registro")
        self.provider_fecha_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.provider_fecha_input = QLineEdit()
        self.provider_fecha_input.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.provider_fecha_input.setText(fecha_actual())
        self.provider_fecha_input.setReadOnly(True)

        self.button_clear = QPushButton("Limpiar Registro")
        self.button_clear.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.button_clear.clicked.connect(lambda: clear_entry([
            self.provider_id_input,
            self.provider_nit_input,
            self.provider_nombre_input,
            self.provider_email_input,
            self.provider_fecha_input,
            self.provider_telefono_input,
            self.provider_direccion_input,
            self.provider_ciudad_input
        ], True))

        self.right_form_layout.addRow(self.provider_email_label, self.provider_email_input)
        self.right_form_layout.addRow(self.provider_telefono_label, self.provider_telefono_input)
        self.right_form_layout.addRow(self.provider_ciudad_label, self.provider_ciudad_input)
        self.right_form_layout.addRow(self.provider_fecha_label, self.provider_fecha_input)
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
        self.add_button.clicked.connect(lambda: (agregar_proveedor(
            self.provider_nit_input.text(),
            self.provider_nombre_input.text(),
            self.provider_direccion_input.text(),
            self.provider_email_input.text(),
            self.provider_telefono_input.text(),
            self.provider_ciudad_input.text(),
            self.provider_fecha_input.text()
        ), cargar_proveedores(self.table)))

        self.edit_button = QPushButton("Editar")
        self.edit_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.edit_button.clicked.connect(lambda: (editar_proveedor({
            'ID': self.provider_id_input,
            'NIT': self.provider_nit_input,
            'Nombre': self.provider_nombre_input,
            'Email': self.provider_email_input,
            'Telefono': self.provider_telefono_input,
            'Direccion': self.provider_direccion_input,
            'Ciudad': self.provider_ciudad_input
        }), cargar_proveedores(self.table)))

        self.delete_button = QPushButton("Eliminar")
        self.delete_button.setStyleSheet(BUTTON_GENERAL_DESIGN)

        self.update_button = QPushButton("Actualizar")
        self.update_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.update_button.clicked.connect(lambda: cargar_proveedores(self.table))

        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.edit_button)
        self.buttons_layout.addWidget(self.delete_button)
        self.buttons_layout.addWidget(self.update_button)
        self.layout.addLayout(self.buttons_layout)

        # Tabla para mostrar proveedores registrados
        self.table_label = QLabel("PROVEEDORES REGISTRADOS:")
        self.layout.addWidget(self.table_label)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "NIT", "Nombre", "Correo", "Teléfono", "Dirección", "Ciudad", "Fecha de Registro"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(lambda: doble_click_proveedor(self.table, {
            'ID':self.provider_id_input,
            'NIT':self.provider_nit_input,
            'Nombre':self.provider_nombre_input,
            'Email':self.provider_email_input,
            'Telefono':self.provider_telefono_input,
            'Direccion':self.provider_direccion_input,
            'Ciudad':self.provider_ciudad_input,
            'Fecha':self.provider_fecha_input
        }))

        # self.table.setRowCount(0)  # Inicialmente vacía

        self.layout.addWidget(self.table)
