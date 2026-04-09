from PyQt5.QtWidgets import (QTextEdit, QLineEdit, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, QComboBox, QTableWidgetItem)
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

        # Proyecto y Empleado
        project_employee_layout = QHBoxLayout()
        project_employee_layout.setSpacing(10)

        self.project_label = QLabel("Proyecto:")
        self.project_label.setStyleSheet(MODERN_LABEL_STYLE)
        self.project_combo = QComboBox()
        self.project_combo.setStyleSheet(MODERN_ENTRY_STYLE)
        self.project_combo.setFixedWidth(200)
        # TODO: Llenar con nombres de proyectos desde la base de datos
        self.project_combo.addItems(get_project_names_from_db())

        self.employee_label = QLabel("Empleado:")
        self.employee_label.setStyleSheet(MODERN_LABEL_STYLE)
        self.employee_combo = QComboBox()
        self.employee_combo.setStyleSheet(MODERN_ENTRY_STYLE)
        self.employee_combo.setFixedWidth(200)
        # TODO: Llenar con nombres de empleados desde la base de datos
        self.employee_combo.addItems(get_employee_names_from_db())

        project_employee_layout.addWidget(self.project_label)
        project_employee_layout.addWidget(self.project_combo)
        project_employee_layout.addSpacing(16)
        project_employee_layout.addWidget(self.employee_label)
        project_employee_layout.addWidget(self.employee_combo)
        project_employee_layout.addStretch()
        self.layout.addLayout(project_employee_layout)

        # Buscador de materiales por nombre o ID
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        self.material_search_label = QLabel("Buscar material:")
        self.material_search_label.setStyleSheet(MODERN_LABEL_STYLE)
        self.material_search_input = QLineEdit()
        self.material_search_input.setPlaceholderText("Nombre o ID del material")
        self.material_search_input.setStyleSheet(MODERN_ENTRY_STYLE)
        self.material_search_input.setFixedWidth(200)

        self.material_search_button = QPushButton("Buscar")
        self.material_search_button.setStyleSheet(MODERN_BUTTON_STYLE)
        self.material_search_button.setFixedWidth(110)
        self.material_search_button.clicked.connect(self.search_material)

        search_layout.addWidget(self.material_search_label)
        search_layout.addWidget(self.material_search_input)
        search_layout.addWidget(self.material_search_button)
        search_layout.addStretch()
        self.layout.addLayout(search_layout)

        # Tabla de resultados de búsqueda
        self.search_results_table = QTableWidget()
        self.search_results_table.setColumnCount(4)
        self.search_results_table.setHorizontalHeaderLabels(["ID", "Nombre", "Unidad", "Disponible"])
        self.search_results_table.setColumnWidth(0, 80)
        self.search_results_table.setColumnWidth(1, 180)
        self.search_results_table.setColumnWidth(2, 110)
        self.search_results_table.setColumnWidth(3, 110)
        self.search_results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.search_results_table.setRowCount(0)
        self.search_results_table.setStyleSheet(MODERN_TABLE_STYLE)
        self.search_results_table.horizontalHeader().setStretchLastSection(True)
        self.search_results_table.verticalHeader().setVisible(False)
        self.search_results_table.setAlternatingRowColors(True)
        self.layout.addWidget(self.search_results_table)

        # Botón para agregar material seleccionado a la orden
        self.add_material_button = QPushButton("Agregar a orden")
        self.add_material_button.setStyleSheet(MODERN_BUTTON_STYLE)
        self.add_material_button.setFixedWidth(140)
        self.add_material_button.clicked.connect(self.add_material_to_order)
        add_btn_layout = QHBoxLayout()
        add_btn_layout.addStretch()
        add_btn_layout.addWidget(self.add_material_button)
        add_btn_layout.addStretch()
        self.layout.addLayout(add_btn_layout)

        # Tabla de materiales para la orden de compra
        self.order_materials_label = QLabel("Materiales para orden de compra:")
        self.order_materials_label.setStyleSheet(MODERN_LABEL_STYLE + "font-size: 15px; margin-top: 10px;")
        self.layout.addWidget(self.order_materials_label)

        self.order_materials_table = QTableWidget()
        self.order_materials_table.setColumnCount(5)
        self.order_materials_table.setHorizontalHeaderLabels(["ID", "Nombre", "Cantidad solicitada", "Unidad", "Disponible"])
        self.order_materials_table.setColumnWidth(0, 80)
        self.order_materials_table.setColumnWidth(1, 180)
        self.order_materials_table.setColumnWidth(2, 110)
        self.order_materials_table.setColumnWidth(3, 110)
        self.order_materials_table.setColumnWidth(4, 110)
        self.order_materials_table.setEditTriggers(QTableWidget.AllEditTriggers)
        self.order_materials_table.setRowCount(0)
        self.order_materials_table.setStyleSheet(MODERN_TABLE_STYLE)
        self.order_materials_table.horizontalHeader().setStretchLastSection(True)
        self.order_materials_table.verticalHeader().setVisible(False)
        self.order_materials_table.setAlternatingRowColors(True)
        self.layout.addWidget(self.order_materials_table)

        # Botón para generar PDF de orden de compra
        self.generate_pdf_button = QPushButton("Generar PDF Orden de Compra")
        self.generate_pdf_button.setStyleSheet(MODERN_BUTTON_STYLE)
        self.generate_pdf_button.setFixedWidth(200)
        self.generate_pdf_button.clicked.connect(self.generate_order_pdf)
        pdf_btn_layout = QHBoxLayout()
        pdf_btn_layout.addStretch()
        pdf_btn_layout.addWidget(self.generate_pdf_button)
        pdf_btn_layout.addStretch()
        self.layout.addLayout(pdf_btn_layout)

        # Botón para subir PDF a ClickUp
        self.upload_pdf_button = QPushButton("Subir PDF a ClickUp")
        self.upload_pdf_button.setStyleSheet(MODERN_BUTTON_STYLE)
        self.upload_pdf_button.setFixedWidth(200)
        upload_btn_layout = QHBoxLayout()
        upload_btn_layout.addStretch()
        upload_btn_layout.addWidget(self.upload_pdf_button)
        upload_btn_layout.addStretch()
        self.layout.addLayout(upload_btn_layout)

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

        # Botones de acción
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setSpacing(16)

        self.clear_button = QPushButton("Limpiar")
        self.clear_button.setStyleSheet(MODERN_BUTTON_STYLE)
        self.clear_button.setFixedWidth(110)
        self.clear_button.clicked.connect(self.clear_all)
        action_buttons_layout.addWidget(self.clear_button)

        action_buttons_layout.addStretch()
        self.layout.addLayout(action_buttons_layout)

    # Métodos auxiliares (debes implementarlos según tu lógica y base de datos)
    def search_material(self):
        search_text = self.material_search_input.text()
        # TODO: Buscar en la base de datos por nombre o ID y llenar la tabla de resultados
        results = search_materials_in_db(search_text)
        self.search_results_table.setRowCount(len(results))
        for row, material in enumerate(results):
            self.search_results_table.setItem(row, 0, QTableWidgetItem(str(material['id'])))
            self.search_results_table.setItem(row, 1, QTableWidgetItem(material['nombre']))
            self.search_results_table.setItem(row, 2, QTableWidgetItem(material['unidad']))
            self.search_results_table.setItem(row, 3, QTableWidgetItem(str(material['disponible'])))

    def add_material_to_order(self):
        selected_row = self.search_results_table.currentRow()
        if selected_row < 0:
            return
        material_id = self.search_results_table.item(selected_row, 0).text()
        nombre = self.search_results_table.item(selected_row, 1).text()
        unidad = self.search_results_table.item(selected_row, 2).text()
        disponible = self.search_results_table.item(selected_row, 3).text()
        row_position = self.order_materials_table.rowCount()
        self.order_materials_table.insertRow(row_position)
        self.order_materials_table.setItem(row_position, 0, QTableWidgetItem(material_id))
        self.order_materials_table.setItem(row_position, 1, QTableWidgetItem(nombre))
        self.order_materials_table.setItem(row_position, 2, QTableWidgetItem("1"))  # Default cantidad
        self.order_materials_table.setItem(row_position, 3, QTableWidgetItem(unidad))
        self.order_materials_table.setItem(row_position, 4, QTableWidgetItem(disponible))

    def generate_order_pdf(self):
        # TODO: Implementa la generación de PDF con los materiales que no hay suficiente en inventario
        # y muestra la cantidad existente en el inventario
        materiales_faltantes = []
        for row in range(self.order_materials_table.rowCount()):
            cantidad_solicitada = int(self.order_materials_table.item(row, 2).text())
            disponible = int(self.order_materials_table.item(row, 4).text())
            if cantidad_solicitada > disponible:
                materiales_faltantes.append({
                    'id': self.order_materials_table.item(row, 0).text(),
                    'nombre': self.order_materials_table.item(row, 1).text(),
                    'cantidad_solicitada': cantidad_solicitada,
                    'unidad': self.order_materials_table.item(row, 3).text(),
                    'disponible': disponible
                })
        # Llama a tu función para generar el PDF y guarda la ruta
        self.generated_pdf_path = generar_pdf_orden_compra(
            self.project_combo.currentText(),
            self.employee_combo.currentText(),
            materiales_faltantes
        )
        self.api_info_display.setText(f"PDF generado: {self.generated_pdf_path}")

    def upload_pdf_to_clickup(self):
        # Usa la función existente para subir el PDF generado a ClickUp
        if hasattr(self, 'generated_pdf_path') and self.generated_pdf_path:
            crear_tarea(
                self,
                f"Orden de compra {self.project_combo.currentText()}",
                f"Empleado: {self.employee_combo.currentText()}",
                self.api,
                [self.generated_pdf_path]
            )
            self.api_info_display.setText("PDF subido a ClickUp correctamente.")
        else:
            self.api_info_display.setText("Primero genera el PDF de la orden de compra.")

    def clear_all(self):
        self.material_search_input.clear()
        self.search_results_table.setRowCount(0)
        self.order_materials_table.setRowCount(0)
        self.api_info_display.clear()

# Funciones auxiliares (debes implementarlas según tu base de datos y lógica)
def get_project_names_from_db():
    # TODO: Devuelve una lista de nombres de proyectos desde la base de datos
    return ["Proyecto A", "Proyecto B", "Proyecto C"]

def get_employee_names_from_db():
    # TODO: Devuelve una lista de nombres de empleados desde la base de datos
    return ["Empleado 1", "Empleado 2", "Empleado 3"]

def search_materials_in_db(search_text):
    # TODO: Busca materiales por nombre o ID en la base de datos y devuelve una lista de dicts
    # Ejemplo:
    return [
        {'id': 'MAT001', 'nombre': 'Tornillo', 'unidad': 'pieza', 'disponible': 10},
        {'id': 'MAT002', 'nombre': 'Tuerca', 'unidad': 'pieza', 'disponible': 5}
    ]

def generar_pdf_orden_compra(proyecto, empleado, materiales_faltantes):
    # TODO: Genera el PDF de la orden de compra y devuelve la ruta del archivo
    # Aquí solo se simula la ruta
    return "orden_compra.pdf"
