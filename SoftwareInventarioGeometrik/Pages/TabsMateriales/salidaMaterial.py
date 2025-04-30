from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,QComboBox,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QStackedWidget, QFormLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from Style import *
from src.utils.getDate import fecha_actual
from DataBase.managerInventario import *


class SalidaMaterial(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()


    def init_ui(self):
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)

        # Línea de selección de proyecto y responsable
        proyect_line = QHBoxLayout()
        proyect_line.setContentsMargins(0, 0, 0, 0)
        proyect_line.setSpacing(10)

        self.entry_proyecto = QComboBox()
        self.entry_proyecto.setStyleSheet(COMBOBOX_GENERAL_DESIGN)
        self.entry_proyecto.addItems(["Proyecto 1", "Proyecto 2", "Proyecto 3"])
        self.entry_proyecto.setMinimumWidth(150)

        self.entry_responsable = QLineEdit()
        self.entry_responsable.setPlaceholderText("Ingrese el nombre del responsable")
        self.entry_responsable.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.entry_responsable.setMinimumWidth(150)

        self.entry_cliente = QLineEdit()
        self.entry_cliente.setPlaceholderText("Nombre del cliente")
        self.entry_cliente.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.entry_cliente.setReadOnly(True)
        self.entry_cliente.setMinimumWidth(150)

        self.entry_ubicacion = QLineEdit()
        self.entry_ubicacion.setPlaceholderText("Ubicación del material")
        self.entry_ubicacion.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.entry_ubicacion.setMinimumWidth(150)

        self.entry_fecha_Actual = QLineEdit()
        self.entry_fecha_Actual.setReadOnly(True)
        self.entry_fecha_Actual.setText(fecha_actual())
        self.entry_fecha_Actual.setMinimumWidth(150)
        self.entry_fecha_Actual.setStyleSheet(ENTRY_GENERAL_DESIGN)

        proyect_line.addWidget(self.entry_proyecto, 1)
        proyect_line.addWidget(self.entry_responsable, 1)
        proyect_line.addWidget(self.entry_cliente, 1)
        proyect_line.addWidget(self.entry_ubicacion, 1)
        proyect_line.addWidget(self.entry_fecha_Actual, 1)

        self.entry_buscar_inventario = QLineEdit()
        self.entry_buscar_inventario.setPlaceholderText("Buscar Proyecto")
        self.entry_buscar_inventario.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.entry_buscar_inventario.textChanged.connect(self.buscar_inventario)

    # Agrega los resultados al QComboBox

        
        self.layout.addLayout(proyect_line)
        self.layout.addWidget(self.entry_buscar_inventario)

        # Layout horizontal para las tablas
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(10)

        # Tabla de materiales disponibles
        available_table_layout = QVBoxLayout()
        available_table_layout.setSpacing(10)

        available_table_title = QLabel("Materiales Disponibles")
        available_table_title.setAlignment(Qt.AlignLeft)
        available_table_title.setFont(QFont("Arial", 14, QFont.Bold))
        available_table_layout.addWidget(available_table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Cantidad\nDisponible", "Unidad", "Precio Unitario", "Precio Total", "Seleccionar"])
        self.table.setRowCount(0)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacer que la tabla sea de solo lectura
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # Seleccionar filas completas
        #quita el borde de la tabla y la enumeracion de filas
        self.table.setShowGrid(False)  # Quitar la cuadrícula
        #no motrar la numeracion de filas8
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)  # Alternar colores de fila+
        # 
        # Ocultar encabezado de filas
        self.table.setRowCount(0)  # Inicialmente no hay filas
        # hacer que la tabla se organice dando click en el encabezado
        #hacer que la tabla se ajuste al tamaño de la ventana y organice los encabezados que ocupen el mismo tamaño
        #hacer que la tabla se ajuste al ancho
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 100)

        self.table.horizontalHeader().setStretchLastSection(True)

        available_table_layout.addWidget(self.table)
        tables_layout.addLayout(available_table_layout)

        # Tabla de materiales seleccionados
        selected_table_layout = QVBoxLayout()
        selected_table_layout.setSpacing(10)

        selected_table_title = QLabel("Materiales Seleccionados")
        selected_table_title.setAlignment(Qt.AlignLeft)
        selected_table_title.setFont(QFont("Arial", 14, QFont.Bold))
        selected_table_layout.addWidget(selected_table_title)

        self.selected_table = QTableWidget()
        self.selected_table.setColumnCount(7)
        self.selected_table.setHorizontalHeaderLabels(["ID", "Nombre", "Cantidad Seleccionada", "Unidad", 'Precio Unitario', 'Precio Total', "Quitar"])
        self.selected_table.setRowCount(0)
        
        self.selected_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacer que la tabla sea de solo lectura
        self.selected_table.setSelectionBehavior(QTableWidget.SelectRows)  # Seleccionar filas completas
        #quita el borde de la tabla y la enumeracion de filas
        self.selected_table.setShowGrid(False)  # Quitar la cuadrícula
        #no motrar la numeracion de filas8
        self.selected_table.verticalHeader().setVisible(False)
        self.selected_table.setAlternatingRowColors(True)  # Alternar colores de fila+
        # 
        # Ocultar encabezado de filas
        self.selected_table.setRowCount(0)  
        

        self.selected_table.setColumnWidth(0, 50)
        self.selected_table.setColumnWidth(5, 50)
        self.selected_table.setColumnWidth(6, 50)

        self.selected_table.horizontalHeader().setStretchLastSection(True)

        selected_table_layout.addWidget(self.selected_table)
        tables_layout.addLayout(selected_table_layout)

        # Agregar el layout horizontal de tablas al layout principal
        self.layout.addLayout(tables_layout)

        # Botones de acción
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.btn_limpiar.clicked.connect(self.select_producto)

        self.btn_generar_recibo = QPushButton("Generar Recibo de Salida")
        self.btn_generar_recibo.setStyleSheet(BUTTON_GENERAL_DESIGN)
        self.btn_generar_recibo.clicked.connect(self.imprimir_tabla)

        button_layout.addWidget(self.btn_limpiar)
        button_layout.addWidget(self.btn_generar_recibo)

        self.layout.addLayout(button_layout)
    def imprimir_tabla(self):
        getManagerInventario(self)
    def select_producto(self):
        updateSelectedTable(self)
    def buscar_inventario(self, text):
        filterTable(self, text)
        