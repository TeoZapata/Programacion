import sys
from PyQt5.QtWidgets import (QComboBox, QLineEdit, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTableWidget, QFormLayout, QHeaderView)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from Style import *
from src.utils.getDate import *
from src.utils.standarFunc import *


class proyecto(QWidget):
    def __init__(self):
        super().__init__()
        self.initUi()
        
    def initUi(self):
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Formulario de entrada
        self.formLayout = QHBoxLayout()

        # Columna izquierda del formulario
        self.leftFormLayout = QFormLayout()

        # Entrada para el nombre del proyecto
        self.projectNameLabel = QLabel("Nombre del Proyecto:")
        self.projectNameLabel.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.projectNameInput = QLineEdit()
        self.projectNameInput.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.leftFormLayout.addRow(self.projectNameLabel, self.projectNameInput)

        # Selección de cliente
        self.clientLabel = QLabel("Cliente:")
        self.clientLabel.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.clientDropdown = QComboBox()
        self.clientDropdown.setStyleSheet(COMBOBOX_GENERAL_DESIGN)
        self.leftFormLayout.addRow(self.clientLabel, self.clientDropdown)

        # Entrada para capacidad DC
        self.capacityLabel = QLabel("Capacidad (kWp):")
        self.capacityLabel.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.capacityInput = QLineEdit()
        self.capacityInput.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.leftFormLayout.addRow(self.capacityLabel, self.capacityInput)

        # Columna derecha del formulario
        self.rightFormLayout = QFormLayout()

        # Entrada para ubicación del proyecto
        self.locationLabel = QLabel("Ubicación del Proyecto:")
        self.locationLabel.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.locationInput = QLineEdit()
        self.locationInput.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.rightFormLayout.addRow(self.locationLabel, self.locationInput)

        # Fecha de inicio del proyecto
        self.startDateLabel = QLabel("Fecha de Registro:")
        self.startDateLabel.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.startDateInput = QLineEdit()
        self.startDateInput.setText(fecha_actual())
        self.startDateInput.setReadOnly(True)
        self.startDateInput.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.rightFormLayout.addRow(self.startDateLabel, self.startDateInput)

        self.id_project = QLabel("ID del Proyecto")
        self.id_project.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.id_project_input = QLineEdit()
        self.id_project_input.setStyleSheet(ENTRY_ONLY_READ_DESIGN)
        self.id_project_input.setReadOnly(True)
        self.rightFormLayout.addRow(self.id_project, self.id_project_input)

        # Agregar columnas al formulario principal
        self.formLayout.addLayout(self.leftFormLayout)
        self.formLayout.addLayout(self.rightFormLayout)
        self.layout.addLayout(self.formLayout)

        self.buttonsLayout = QHBoxLayout()

        self.addButton = QPushButton("Agregar")
        self.addButton.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.addButton.clicked.connect(lambda : agregar_proyecto(self))

        self.editButton = QPushButton("Editar")
        self.editButton.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.editButton.clicked.connect(lambda : edit_proyecto(self))
        
        self.deleteButton = QPushButton("Eliminar")
        self.deleteButton.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.deleteButton.clicked.connect(lambda : eliminar_proyecto(self))

        self.updateButton = QPushButton("Actualizar")
        self.updateButton.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.updateButton.clicked.connect(lambda : (cargar_proyecto_tabla(self), obtener_nombres_proyectos(self.clientDropdown, "clientes")))

        self.clear_input = QPushButton("Limpiar")
        self.clear_input.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.clear_input.clicked.connect(lambda : clear_entry([self.projectNameInput,self.id_project_input ,self.capacityInput, self.locationInput, self.startDateInput], True))
        
        
        self.buttonsLayout.addWidget(self.addButton)
        self.buttonsLayout.addWidget(self.editButton)
        self.buttonsLayout.addWidget(self.deleteButton)
        self.buttonsLayout.addWidget(self.updateButton)
        self.buttonsLayout.addWidget(self.clear_input)


        self.layout.addLayout(self.buttonsLayout)
        # Tabla para mostrar proyectos registrados
        self.tableLabel = QLabel("Proyectos Registrados:")
        self.tableLabel.setFont(QFont("Arial", 16, QFont.Bold))
        self.layout.addWidget(self.tableLabel)

        self.projectsTable = QTableWidget()
        self.projectsTable.setColumnCount(6)
        self.projectsTable.setHorizontalHeaderLabels(["ID","Nombre", "Cliente", "Ubicación", "Capacidad (kW)", "Fecha Registro"])
        self.projectsTable.setAlternatingRowColors(True)
        self.projectsTable.setSelectionMode(QTableWidget.SingleSelection)
        self.projectsTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.projectsTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.projectsTable.setShowGrid(False)
        self.projectsTable.verticalHeader().setVisible(False)
        self.projectsTable.horizontalHeader().setStretchLastSection(True)
        self.projectsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.projectsTable.doubleClicked.connect(lambda _: double_click_tabla_proyecto(self))

        self.layout.addWidget(self.projectsTable)

        # Botones CRUD

