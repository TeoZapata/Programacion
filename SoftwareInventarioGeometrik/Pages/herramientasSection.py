from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,QSizePolicy)
from PyQt5.QtCore import Qt, QSize, QEvent
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QTabWidget, QLabel
from .TabsMateriales import *
from Style import *
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from src.utils.getCodeBar import *


class HerramientasSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Layouts principales
        self.form_layout = QVBoxLayout()
        self.grid_layout = QHBoxLayout()

        # Columna izquierda del formulario
        self.left_form_layout = QFormLayout()
        # Layout para búsqueda de material
        self.search_layout = QHBoxLayout()
        self.search_layout.setContentsMargins(10, 10, 10, 10)

        # Widget contenedor para el área de búsqueda
        self.search_container = QWidget()
        self.search_container.setLayout(self.search_layout)
        self.search_container.setStyleSheet("""
            QWidget {
            background-color: #f0f4ff;
            border: 2px solid #3a6ea5;
            border-radius: 10px;
            }
        """)

        # Búsqueda por Clasificación
        self.clasificacion_label = QLabel("Clasificación:")
        self.clasificacion_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.clasificacion_dropdown = QComboBox()
        self.clasificacion_dropdown.setStyleSheet(COMBOBOX_GENERAL_DESIGN)
        categoria, subcategoria = obtener_categorias()
        self.clasificacion_dropdown.addItems(categoria.keys())
        self.search_layout.addWidget(self.clasificacion_label)
        self.search_layout.addWidget(self.clasificacion_dropdown)

        # Búsqueda por Subclasificación
        self.subclasificacion_label = QLabel("Subclasificación:")
        self.subclasificacion_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.subclasificacion_dropdown = QComboBox()
        self.subclasificacion_dropdown.setStyleSheet(COMBOBOX_GENERAL_DESIGN)
        self.subclasificacion_dropdown.addItems(subcategoria.keys())
        self.search_layout.addWidget(self.subclasificacion_label)
        self.search_layout.addWidget(self.subclasificacion_dropdown)

        # Entrada manual de últimos 4 dígitos
        self.last_digits_label = QLabel("Últimos 4 dígitos:")
        self.last_digits_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.last_digits_input = QLineEdit()
        self.last_digits_input.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.last_digits_input.setPlaceholderText("Ej: 0001")
        self.last_digits_input.returnPressed.connect(lambda: self.search_button.click())
        self.search_layout.addWidget(self.last_digits_label)
        self.search_layout.addWidget(self.last_digits_input)

        # Botón de búsqueda
        self.search_button = QPushButton("Buscar Material")
        self.search_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.search_button.clicked.connect(lambda: search_herramienta(
            categoria[self.clasificacion_dropdown.currentText()],
            subcategoria[self.subclasificacion_dropdown.currentText()],
            self.last_digits_input.text(),
            {'ID': self.id_input,
             'Codigo': self.codigo_input,
             'Herramienta': self.herramienta_input,
             'Cantidad': self.cantidad_input}
        ))
        self.search_layout.addWidget(self.search_button)

        # Agregar el contenedor estilizado al layout principal
        self.layout.addWidget(self.search_container)
        # Input para mostrar información del material/herramient
        # ID Herramienta (solo lectura, autogenerado)
        self.id_label = QLabel("ID Material")
        self.id_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.id_input = QLineEdit()
        self.id_input.setReadOnly(True)
        self.id_input.setStyleSheet(ENTRY_ONLY_READ_DESIGN)

        # Código de la herramienta
        self.codigo_label = QLabel("Código Herramienta")
        self.codigo_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.codigo_input = QLineEdit()
        self.codigo_input.setReadOnly(True)
        self.codigo_input.setStyleSheet(ENTRY_ONLY_READ_DESIGN)

        # Nombre de la herramienta
        self.herramienta_label = QLabel("Nombre Herramienta")
        self.herramienta_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.herramienta_input = QLineEdit()
        self.herramienta_input.setReadOnly(True)
        self.herramienta_input.setStyleSheet(ENTRY_ONLY_READ_DESIGN)

        self.cantidad_label = QLabel("Cantidad En Inventario")
        self.cantidad_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.cantidad_input = QLineEdit()
        self.cantidad_input.setReadOnly(True)
        self.cantidad_input.setStyleSheet(ENTRY_ONLY_READ_DESIGN)

        # Estado de la herramienta
        self.estado_label = QLabel("Estado")
        self.estado_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.estado_input = QComboBox()
        self.estado_input.setStyleSheet(COMBOBOX_GENERAL_DESIGN)
        self.estado_input.addItems(["Asignada", "Disponible", "En reparación", "Dañada", "Devuelta"])

        # Observación
        self.observacion_label = QLabel("Observación")
        self.observacion_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.observacion_input = QLineEdit()
        self.observacion_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        self.left_form_layout.addRow(self.id_label, self.id_input)
        self.left_form_layout.addRow(self.codigo_label, self.codigo_input)
        self.left_form_layout.addRow(self.herramienta_label, self.herramienta_input)
        self.left_form_layout.addRow(self.cantidad_label, self.cantidad_input)
        self.left_form_layout.addRow(self.estado_label, self.estado_input)
        self.left_form_layout.addRow(self.observacion_label, self.observacion_input)

        # Columna derecha del formulario
        self.right_form_layout = QFormLayout()

        # ID Empleado (puede ser autocompletado o buscado)
        self.id_empleado_label = QLabel("ID Empleado")
        self.id_empleado_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.id_empleado_input = QLineEdit()
        self.id_empleado_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        # Responsable (nombre del empleado)
        self.responsable_label = QLabel("Responsable")
        self.responsable_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.responsable_input = QComboBox()
        self.responsable_input.setStyleSheet(COMBOBOX_GENERAL_DESIGN)

        # Cédula del responsable
        self.cedula_label = QLabel("Cédula")
        self.cedula_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.cedula_input = QLineEdit()
        self.cedula_input.setStyleSheet(ENTRY_GENERAL_DESIGN)

        # Fecha de asignación (por defecto hoy)
        self.fecha_asignacion_label = QLabel("Fecha Asignación")
        self.fecha_asignacion_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.fecha_asignacion_input = QLineEdit()
        self.fecha_asignacion_input.setStyleSheet(ENTRY_ONLY_READ_DESIGN)
        self.fecha_asignacion_input.setText(fecha_actual())
        self.fecha_asignacion_input.setReadOnly(True)

        # Fecha de cambio de estado (por defecto hoy)
        self.fecha_cambio_estado_label = QLabel("Fecha Cambio Estado")
        self.fecha_cambio_estado_label.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.fecha_cambio_estado_input = QLineEdit()
        self.fecha_cambio_estado_input.setStyleSheet(ENTRY_ONLY_READ_DESIGN)
        self.fecha_cambio_estado_input.setText(fecha_actual())
        self.fecha_cambio_estado_input.setReadOnly(True)


        self.button_search_responsable = QPushButton('Buscar Responsable')
        self.button_search_responsable.setStyleSheet(BUTTON_GENERAL_DESIGN)


        self.button_clear = QPushButton("Limpiar Registro")
        self.button_clear.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.button_clear.clicked.connect(
            lambda: clear_entry([
            self.id_input, self.codigo_input, self.herramienta_input, self.estado_input,
            self.fecha_cambio_estado_input, self.observacion_input, self.id_empleado_input, self.cedula_input, self.cantidad_input,
            self.fecha_asignacion_input
            ], True)
        )

        # Crear un layout horizontal para el campo Responsable y el botón Buscar
        self.responsable_row_layout = QHBoxLayout()
        self.responsable_row_layout.addWidget(self.responsable_input)
        self.button_buscar_responsable = QPushButton("Buscar")
        self.button_buscar_responsable.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.responsable_row_layout.addWidget(self.button_buscar_responsable)

        self.right_form_layout.addRow(self.responsable_label, self.responsable_row_layout)
        self.right_form_layout.addRow(self.id_empleado_label, self.id_empleado_input)
        self.right_form_layout.addRow(self.cedula_label, self.cedula_input)
        self.right_form_layout.addRow(self.fecha_asignacion_label, self.fecha_asignacion_input)
        self.right_form_layout.addRow(self.fecha_cambio_estado_label, self.fecha_cambio_estado_input)
        # Crear un layout horizontal para los dos botones
        self.buttons_row_layout = QHBoxLayout()
        self.buttons_row_layout.addWidget(self.button_clear)
        self.buttons_row_layout.addWidget(self.button_search_responsable)

        # Agregar el layout horizontal como una fila al formulario derecho
        self.right_form_layout.addRow(self.buttons_row_layout)

        # Agregar columnas al layout principal
        self.grid_layout.addLayout(self.left_form_layout)
        self.grid_layout.addLayout(self.right_form_layout)
        self.form_layout.addLayout(self.grid_layout)
        self.layout.addLayout(self.form_layout)

        # Botones de acción
        self.buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Agregar")
        self.add_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.edit_button = QPushButton("Editar")
        self.edit_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.delete_button = QPushButton("Eliminar")
        self.delete_button.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.update_button = QPushButton("Actualizar Estado")
        self.update_button.setStyleSheet(BUTTON_GENERAL_DESIGN)


        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.edit_button)
        self.buttons_layout.addWidget(self.delete_button)
        self.buttons_layout.addWidget(self.update_button)

        self.layout.addLayout(self.buttons_layout)

        # Tabla para mostrar herramientas asignadas
        self.table_label = QLabel("Herramientas Asignadas")
        self.table_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.layout.addWidget(self.table_label)

        self.herramientas_table = QTableWidget()
        self.herramientas_table.setColumnCount(11)
        self.herramientas_table.setHorizontalHeaderLabels([
            "ID", "ID Herramienta", "Código", "Herramienta", "ID Empleado", "Responsable",
            "Cédula", "Fecha Asignación", "Fecha Cambio Estado", "Estado", "Observación"
        ])
        self.herramientas_table.setAlternatingRowColors(True)
        self.herramientas_table.horizontalHeader().setStretchLastSection(True)
        self.herramientas_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.herramientas_table.setSelectionMode(QTableWidget.SingleSelection)
        self.herramientas_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.herramientas_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.herramientas_table.setShowGrid(False)
        self.herramientas_table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.herramientas_table)

        # Escalabilidad: los campos y la tabla están listos para integrarse con la base de datos y lógica de negocio.
        # Puedes conectar los botones a funciones para agregar, editar, eliminar y actualizar el estado de las herramientas.
