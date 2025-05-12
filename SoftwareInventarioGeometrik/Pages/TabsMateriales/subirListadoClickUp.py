from PyQt5.QtWidgets import (QTextEdit, QLineEdit, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget,QComboBox)
from PyQt5.QtCore import Qt, QSize,QDate
from PyQt5.QtGui import QFont, QIcon
from Style import *
from src.utils.clickup import *
from src.utils.prueba_clicup import *
from PyQt5.QtWidgets import QFileDialog

class SubirListadoClickUp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):

        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Sección de conexión con API
        api_layout = QHBoxLayout()

        # QLineEdit para ingresar la API Key de ClickUp
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Ingrese la API Key de ClickUp")
        self.api_key_input.setStyleSheet(ENTRY_GENERAL_DESIGN)
        api_layout.addWidget(self.api_key_input)

        # Botón para conectar con la API
        self.connect_button = QPushButton("Conectar")
        self.connect_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.connect_button.clicked.connect(lambda: print_available_lists(self, self.api_key_input.text()))
        api_layout.addWidget(self.connect_button)

        # Etiqueta para mostrar el estado de la conexión
        self.connection_status_label = QLabel("Estado: Desconectado")
        self.connection_status_label.setStyleSheet("QLabel { font-weight: bold; color: red; }")
        api_layout.addWidget(self.connection_status_label)

        self.layout.addLayout(api_layout)


        tarea_layout = QHBoxLayout()
        # QLabe para ingresar nombre de la tarea
        self.task_name_label = QLabel("Nombre de la tarea:")
        self.task_name_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.task_name_label.setFont(QFont("Arial", 10, QFont.Bold))

        # QLineEdit para ingresar el nombre de la tarea
        self.task_name_input = QLineEdit()
        self.task_name_input.setPlaceholderText("Ingrese el nombre de la tarea")
        self.task_name_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        # Agregar el QLabel y QLineEdit para el id de la lista
        self.list_id_label = QLabel("ID de la lista:")
        self.list_id_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.list_id_label.setFont(QFont("Arial", 10, QFont.Bold))

        self.list_id_input = QLineEdit()
        self.list_id_input.setPlaceholderText("Ingrese el ID de la lista")
        self.list_id_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        tarea_layout.addWidget(self.task_name_label)
        tarea_layout.addWidget(self.task_name_input)
        tarea_layout.addWidget(self.list_id_label)
        tarea_layout.addWidget(self.list_id_input)


        # QTextEdit para mostrar información de la API
        self.api_info_display = QTextEdit()
        self.api_info_display.setReadOnly(True)
        self.api_info_display.setStyleSheet("QTextEdit { border: 1px solid #ccc; }")
        self.layout.addWidget(self.api_info_display)


        self.layout.addLayout(tarea_layout)

        # Tabla para mostrar los materiales
        self.text_materiales = QLabel("Materiales:")
        self.text_materiales.setStyleSheet(LABEL_GENERAL_DESIGN)

        # QTableWidget que permita ingresar los materiales
        self.materiales_table = QTableWidget()  
        self.materiales_table.setColumnCount(3)
        self.materiales_table.setHorizontalHeaderLabels(["Nombre", "Cantidad", "Unidad"])
        self.materiales_table.setColumnWidth(0, 150)
        self.materiales_table.setColumnWidth(1, 100)
        self.materiales_table.setColumnWidth(2, 100)

        # Permitir al usuario ingresar datos directamente en la tabla
        self.materiales_table.setEditTriggers(QTableWidget.AllEditTriggers)

        # Agregar algunas filas iniciales para que el usuario pueda comenzar a ingresar datos
        self.materiales_table.setRowCount(5)

        self.layout.addWidget(self.text_materiales)
        self.layout.addWidget(self.materiales_table)

        # Botón para generar PDF con los materiales seleccionados
        self.generate_pdf_button = QPushButton("Generar PDF")
        self.generate_pdf_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        def select_file():
            file_dialog = QFileDialog()
            file_dialog.setNameFilter("PDF Files (*.pdf)")
            if file_dialog.exec_():
                selected_file = file_dialog.selectedFiles()[0]
                return [selected_file]
            return None

        self.generate_pdf_button.clicked.connect(lambda: crear_tarea(
            self,
            self.task_name_input.text(),
            ", ".join([f"{self.materiales_table.item(row, 0).text()} ({self.materiales_table.item(row, 1).text()} {self.materiales_table.item(row, 2).text()})"
               for row in range(self.materiales_table.rowCount())
               if self.materiales_table.item(row, 0) and self.materiales_table.item(row, 1) and self.materiales_table.item(row, 2)]),
            self.list_id_input.text(),
            self.api_key_input.text(),
            select_file()  # Allow the user to select the file
        ))
        self.layout.addWidget(self.generate_pdf_button)

        # Botones de acción
        action_buttons_layout = QHBoxLayout()

        # Botón para confirmar
        self.confirm_button = QPushButton("Confirmar")
        self.confirm_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        action_buttons_layout.addWidget(self.confirm_button)

        # Botón para subir
        self.upload_button = QPushButton("Subir")
        self.upload_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        action_buttons_layout.addWidget(self.upload_button)

        # Botón para limpiar
        self.clear_button = QPushButton("Limpiar")
        self.clear_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        action_buttons_layout.addWidget(self.clear_button)

        self.layout.addLayout(action_buttons_layout)
