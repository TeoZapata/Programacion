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
        self.api = 'pk_9903299_1659PNSLP7K8QIVBSU7QAS91DW4L1CFC'

    def init_ui(self):
        # Modern Styles
        MODERN_ENTRY_STYLE = """
            QLineEdit {
                border: 1.5px solid #6c63ff;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 14px;
                background: #f7f7fa;
            }
            QLineEdit:focus {
                border: 2px solid #3f3d56;
                background: #fff;
            }
        """
        MODERN_LABEL_STYLE = """
            QLabel {
                font-size: 13px;
                color: #3f3d56;
                font-weight: 600;
            }
        """
        MODERN_BUTTON_STYLE = """
            QPushButton {
                background-color: #6c63ff;
                color: white;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5548c8;
            }
        """
        MODERN_TABLE_STYLE = """
            QTableWidget {
                border: 1.5px solid #e0e0e0;
                border-radius: 8px;
                background: #f7f7fa;
                font-size: 13px;
            }
            QHeaderView::section {
                background: #6c63ff;
                color: white;
                font-weight: bold;
                border: none;
                height: 28px;
            }
        """

        self.setStyleSheet("background: #f4f6fb;")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(18)

        # Sección de conexión con API
        api_layout = QHBoxLayout()
        api_layout.setSpacing(10)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("API Key de ClickUp")
        self.api_key_input.setStyleSheet(MODERN_ENTRY_STYLE)
        self.api_key_input.setFixedWidth(260)
        api_layout.addWidget(self.api_key_input)

        self.connect_button = QPushButton("Conectar")
        self.connect_button.setStyleSheet(MODERN_BUTTON_STYLE)
        self.connect_button.setFixedWidth(110)
        self.connect_button.clicked.connect(lambda: print_available_lists(self, self.api))
        api_layout.addWidget(self.connect_button)

        self.connection_status_label = QLabel("Estado: Desconectado")
        self.connection_status_label.setStyleSheet("QLabel { font-weight: bold; color: #e74c3c; font-size: 13px; }")
        api_layout.addWidget(self.connection_status_label)

        api_layout.addStretch()
        self.layout.addLayout(api_layout)

        # Sección de tarea y lista
        tarea_layout = QHBoxLayout()
        tarea_layout.setSpacing(10)

        self.task_name_label = QLabel("Nombre de la tarea:")
        self.task_name_label.setStyleSheet(MODERN_LABEL_STYLE)
        self.task_name_input = QLineEdit()
        self.task_name_input.setPlaceholderText("Nombre de la tarea")
        self.task_name_input.setStyleSheet(MODERN_ENTRY_STYLE)
        self.task_name_input.setFixedWidth(200)

        self.list_id_label = QLabel("ID de la lista:")
        self.list_id_label.setStyleSheet(MODERN_LABEL_STYLE)
        self.list_id_input = QLineEdit()
        self.list_id_input.setPlaceholderText("ID de la lista")
        self.list_id_input.setStyleSheet(MODERN_ENTRY_STYLE)
        self.list_id_input.setFixedWidth(140)

        tarea_layout.addWidget(self.task_name_label)
        tarea_layout.addWidget(self.task_name_input)
        tarea_layout.addSpacing(16)
        tarea_layout.addWidget(self.list_id_label)
        tarea_layout.addWidget(self.list_id_input)
        tarea_layout.addStretch()
        self.layout.addLayout(tarea_layout)

        # Información de la API
        self.api_info_display = QTextEdit()
        self.api_info_display.setReadOnly(True)
        self.api_info_display.setStyleSheet("""
            QTextEdit {
                border: 1.5px solid #e0e0e0;
                border-radius: 8px;
                background: #f7f7fa;
                font-size: 13px;
                min-height: 40px;
            }
        """)
        self.layout.addWidget(self.api_info_display)

        # Tabla de materiales
        self.text_materiales = QLabel("Materiales:")
        self.text_materiales.setStyleSheet(MODERN_LABEL_STYLE + "font-size: 15px; margin-top: 10px;")
        self.layout.addWidget(self.text_materiales)

        self.materiales_table = QTableWidget()
        self.materiales_table.setColumnCount(3)
        self.materiales_table.setHorizontalHeaderLabels(["Nombre", "Cantidad", "Unidad"])
        self.materiales_table.setColumnWidth(0, 180)
        self.materiales_table.setColumnWidth(1, 110)
        self.materiales_table.setColumnWidth(2, 110)
        self.materiales_table.setEditTriggers(QTableWidget.AllEditTriggers)
        self.materiales_table.setRowCount(5)
        self.materiales_table.setStyleSheet(MODERN_TABLE_STYLE)
        self.materiales_table.horizontalHeader().setStretchLastSection(True)
        self.materiales_table.verticalHeader().setVisible(False)
        self.materiales_table.setAlternatingRowColors(True)
        self.layout.addWidget(self.materiales_table)

        # Botón para generar PDF
        self.generate_pdf_button = QPushButton("Generar PDF")
        self.generate_pdf_button.setStyleSheet(MODERN_BUTTON_STYLE)
        self.generate_pdf_button.setFixedWidth(140)
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
            self.api,
            select_file()
        ))
        pdf_btn_layout = QHBoxLayout()
        pdf_btn_layout.addStretch()
        pdf_btn_layout.addWidget(self.generate_pdf_button)
        pdf_btn_layout.addStretch()
        self.layout.addLayout(pdf_btn_layout)

        # Botones de acción
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setSpacing(16)

        self.confirm_button = QPushButton("Confirmar")
        self.confirm_button.setStyleSheet(MODERN_BUTTON_STYLE)
        self.confirm_button.setFixedWidth(110)
        action_buttons_layout.addWidget(self.confirm_button)

        self.upload_button = QPushButton("Subir")
        self.upload_button.setStyleSheet(MODERN_BUTTON_STYLE)
        self.upload_button.setFixedWidth(110)
        action_buttons_layout.addWidget(self.upload_button)

        self.clear_button = QPushButton("Limpiar")
        self.clear_button.setStyleSheet(MODERN_BUTTON_STYLE)
        self.clear_button.setFixedWidth(110)
        action_buttons_layout.addWidget(self.clear_button)

        action_buttons_layout.addStretch()
        self.layout.addLayout(action_buttons_layout)
