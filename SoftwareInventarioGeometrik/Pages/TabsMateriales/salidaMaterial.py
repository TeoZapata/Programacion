from PyQt5.QtWidgets import (QHeaderView, QMainWindow, QWidget, QVBoxLayout,QComboBox,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QStackedWidget, QFormLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from Style import *
from src.utils.getDate import fecha_actual
from DataBase.managerInventario import *
from src.utils.generarPdf import *


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

        self.label_proyecto = QLabel("Proyecto")
        self.label_proyecto.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.entry_proyecto = QComboBox()
        self.entry_proyecto.setStyleSheet(COMBOBOX_GENERAL_DESIGN)

        
        
        self.entry_proyecto.setMinimumWidth(150)
        

        self.label_responsable = QLabel("Responsable")
        self.label_responsable.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.entry_responsable = QLineEdit()
        self.entry_responsable.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.entry_responsable.setMinimumWidth(150)

        self.label_fecha_actual = QLabel("Fecha Actual")
        self.label_fecha_actual.setStyleSheet(LABEL_GENERAL_DESIGN)
        self.entry_fecha_Actual = QLineEdit()
        self.entry_fecha_Actual.setText(fecha_actual())
        self.entry_fecha_Actual.setReadOnly(True)
        self.entry_fecha_Actual.setMinimumWidth(150)
        self.entry_fecha_Actual.setStyleSheet(ENTRY_ONLY_READ_DESIGN)



        proyect_line.addWidget(self.label_proyecto)
        proyect_line.addWidget(self.entry_proyecto, 1)
        proyect_line.addWidget(self.label_responsable)
        proyect_line.addWidget(self.entry_responsable, 1)
        proyect_line.addWidget(self.label_fecha_actual)
        proyect_line.addWidget(self.entry_fecha_Actual, 1)

        self.entry_buscar_inventario = QLineEdit()
        self.entry_buscar_inventario.setPlaceholderText("Buscar Proyecto")
        self.entry_buscar_inventario.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.entry_buscar_inventario.textChanged.connect(self.buscar_inventario)

    # Agrega los resultados al QComboBox

        
        self.layout.addLayout(proyect_line)
        self.layout.addWidget(self.entry_buscar_inventario)

        # Layout horizontal para las tablas
        tables_layout = QVBoxLayout()
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
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Cantidad\nDisponible", "Unidad", "Precio\nUnitario", "Precio\nTotal", "Seleccionar"])
        self.table.setRowCount(0)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacer que la tabla sea de solo lectura
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
    
        

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
        self.selected_table.setHorizontalHeaderLabels(["ID", "Nombre", "Cantidad\nSeleccionada", "Unidad", 'Precio\nUnitario', 'Precio\nTotal', "Quitar"])
        self.selected_table.setRowCount(0)
        self.selected_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacer que la tabla sea de solo lectura
        self.selected_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.selected_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.selected_table.setSelectionMode(QTableWidget.SingleSelection)
        self.selected_table.setShowGrid(False)
        
        self.selected_table.verticalHeader().setVisible(False)
        self.selected_table.setAlternatingRowColors(True)

        selected_table_layout.addWidget(self.selected_table)


      

        tables_layout.addLayout(selected_table_layout)

        # Agregar el layout horizontal de tablas al layout principal

        # Botones de acción
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        btn_gen_pdf = QPushButton("Generar PDF")
        btn_gen_pdf.setStyleSheet(BUTTON_GENERAL_DESIGN)
        btn_gen_pdf.clicked.connect(lambda :(gen_pdf(self), getManagerInventario(self), limpiarSelectTable(self)))

        btn_actualizar_tabla = QPushButton("Actualizar Tabla")
        btn_actualizar_tabla.setStyleSheet(BUTTON_GENERAL_DESIGN)
        def actualizar_tabla():
            try:
                getManagerInventario(self)
                obtener_nombres_proyectos(self.entry_proyecto, 'proyectos')
            except Exception as e:
                print(f"Error al actualizar la tabla: {e}")
        btn_actualizar_tabla.clicked.connect(actualizar_tabla)

        btn_limpiar = QPushButton("Limpiar Tabla")
        btn_limpiar.setStyleSheet(BUTTON_GENERAL_DESIGN)
        btn_limpiar.clicked.connect(lambda: limpiarSelectTable(self))


        button_layout.addWidget(btn_actualizar_tabla)
        button_layout.addWidget(btn_limpiar)
        button_layout.addWidget(btn_gen_pdf)

        self.layout.addLayout(button_layout)
        self.layout.addLayout(tables_layout)
    


    def buscar_inventario(self, text):
        filterTable(self, text) 

        
