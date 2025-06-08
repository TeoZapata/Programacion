
from PyQt5.QtWidgets import (QComboBox, QHeaderView, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,QFormLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QTabWidget, QLabel
from Style import *
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from src.utils.standarFunc import *
from DataBase.managerInventario import *


class EmpleadosSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    def init_ui(self):    
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        
        # Formulario de entrada
        self.form_layout = QVBoxLayout()
        self.grid_layout = QHBoxLayout()

        # Columna izquierda del formulario
        self.left_form_layout = QFormLayout()

        self.nombre_label = QLabel("Nombre")
        self.nombre_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.nombre_input = QLineEdit()
        self.nombre_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.cedula_label = QLabel("Cédula")
        self.cedula_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.cedula_input = QLineEdit()
        self.cedula_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.id_label = QLabel("ID")
        self.id_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.id_input = QLineEdit()
        self.id_input.setStyleSheet(ENTRY_ONLY_READ_DESIGN)
        self.id_input.setReadOnly(True)

        self.button_clear = QPushButton("Limpiar")
        self.button_clear.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.button_clear.clicked.connect(
            lambda: (clear_entry(
            [self.nombre_input, self.cedula_input, self.cargo_input, self.telefono_input, self.fecha_input, self.id_input], True
            ), self.cargo_input.addItems(["Tecnico", "administrativo"])
        ) )

        self.left_form_layout.addRow(self.nombre_label, self.nombre_input)
        self.left_form_layout.addRow(self.cedula_label, self.cedula_input)
        self.left_form_layout.addRow(self.id_label, self.id_input)
        self.left_form_layout.addWidget(self.button_clear)

        # Columna derecha del formulario
        self.right_form_layout = QFormLayout()

        self.cargo_label = QLabel("Cargo")
        self.cargo_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.cargo_input = QComboBox()
        self.cargo_input.addItems([
            "Tecnico", "administrativo"
        ])
        self.cargo_input.setStyleSheet(COMBOBOX_GENERAL_DESIGN)

        self.telefono_label = QLabel("Teléfono")
        self.telefono_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.telefono_input = QLineEdit()
        self.telefono_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.fecha_label = QLabel("Fecha de Registro")
        self.fecha_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.fecha_input = QLineEdit()
        self.fecha_input.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.fecha_input.setText(fecha_actual())
        self.fecha_input.setReadOnly(True)

        self.right_form_layout.addRow(self.cargo_label, self.cargo_input)
        self.right_form_layout.addRow(self.telefono_label, self.telefono_input)
        self.right_form_layout.addRow(self.fecha_label, self.fecha_input)

        

        self.grid_layout.addLayout(self.left_form_layout)
        self.grid_layout.addLayout(self.right_form_layout)
        self.form_layout.addLayout(self.grid_layout)
        self.layout.addLayout(self.form_layout)

        # Botones CRUD
        self.buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Agregar")
        self.add_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.add_button.clicked.connect(lambda : (agregar_empleado(
            self.nombre_input.text(),
            self.cedula_input.text(),
            self.cargo_input.currentText(),
            self.telefono_input.text(),
            self.fecha_input.text()
        ), cargar_empleados(self.table)))

        self.edit_button = QPushButton("Editar")
        self.edit_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.edit_button.clicked.connect(lambda: (editar_empleado(
                {'ID':self.id_input,
                'Nombre':self.nombre_input,
                'Cedula':self.cedula_input,
                'Cargo':self.cargo_input,
                'Telefono':self.telefono_input,
                'Fecha':self.fecha_input}
                    ), cargar_empleados(self.table))
                )

        self.delete_button = QPushButton("Eliminar")
        self.delete_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.delete_button.clicked.connect(lambda: eliminar_empleado(self.table.currentItem()))
        self.update_button = QPushButton("Actualizar")
        self.update_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.update_button.clicked.connect(lambda: cargar_empleados(self.table))

        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.edit_button)
        self.buttons_layout.addWidget(self.delete_button)
        self.buttons_layout.addWidget(self.update_button)
        self.layout.addLayout(self.buttons_layout)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar empleado por nombre o cédula...")
        self.search_input.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.search_input.textChanged.connect(self.buscar_empleado)

        self.layout.addWidget(self.search_input)
        # table de empleados
        self.table_label = QLabel("Empleados Registrados:")
        self.layout.addWidget(self.table_label)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID","Nombre", "Cédula", "Cargo", "Teléfono", "Fecha de Registro"]
        )
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(
            lambda: doble_click_empleado(
                self.table, 
                {
                    'ID':self.id_input,
                    'Nombre':self.nombre_input,
                    'Cedula':self.cedula_input,
                    'Cargo':self.cargo_input,
                    'Telefono':self.telefono_input,
                    'Fecha':self.fecha_input
                }
            )
        )

        self.layout.addWidget(self.table)

        # Botones CRUD
    def buscar_empleado(self):
        filterTable(self, self.search_input.text())