from PyQt5.QtWidgets import (QComboBox, QHeaderView, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, QLineEdit)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from src.utils.getDate import *
from Style import *
from DataBase.managerInventario import *

class DevolucionMaterial(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)

        # Línea de selección de proyecto y responsable
        formlayout = QHBoxLayout()
        formlayout.setContentsMargins(0, 0, 0, 0)
        formlayout.setSpacing(10)

        self.entry_proyecto = QComboBox()
        self.entry_proyecto.setStyleSheet(COMBOBOX_GENERAL_DESIGN)
        obtener_nombres_proyectos(self.entry_proyecto)
        self.entry_proyecto.setMinimumWidth(150)

        self.entry_responsable = QLineEdit()
        self.entry_responsable.setPlaceholderText("Ingrese el nombre del responsable")
        self.entry_responsable.setStyleSheet(ENTRY_GENERAL_DESIGN)
        self.entry_responsable.setMinimumWidth(150)



        self.entry_fecha_Actual = QLineEdit()
        self.entry_fecha_Actual.setReadOnly(True)
        self.entry_fecha_Actual.setText(fecha_actual())
        self.entry_fecha_Actual.setMinimumWidth(150)
        self.entry_fecha_Actual.setStyleSheet(ENTRY_GENERAL_DESIGN)

        formlayout.addWidget(self.entry_proyecto, 1)
        formlayout.addWidget(self.entry_responsable, 1)
        formlayout.addWidget(self.entry_fecha_Actual, 1)

        self.entry_buscar_inventario = QLineEdit()
        self.entry_buscar_inventario.setPlaceholderText("Buscar Material")
        self.entry_buscar_inventario.setStyleSheet(ENTRY_GENERAL_DESIGN)

    # Agrega los resultados al QComboBox

        
        self.layout.addLayout(formlayout)
        self.layout.addWidget(self.entry_buscar_inventario)

        # Layout horizontal para las tablas
        tables_layout = QVBoxLayout()
        tables_layout.setSpacing(10)

        # Tabla de materiales disponibles
        available_table_layout = QVBoxLayout()
        available_table_layout.setSpacing(10)

        available_table_title = QLabel("Materiales Del Proyecto")
        available_table_title.setAlignment(Qt.AlignLeft)
        available_table_title.setFont(QFont("Arial", 14, QFont.Bold))
        available_table_layout.addWidget(available_table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Cliente", "Responsable\nde Salida","id Material" ,"Material","Cantidad","Unidad","Precio\nUnitario", "Precio\nTotal", "Descripción","Fecha de Salida"])
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

        selected_table_title = QLabel("Materiales en Devolución")
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

        btn_generar_recibo = QPushButton("Buscar Material")
        btn_generar_recibo.setStyleSheet(BUTTON_GENERAL_DESIGN)
        btn_generar_recibo.clicked.connect(lambda: cargar_salidaMaterial_proyecto(self))

        btn_limpiar = QPushButton("Limpiar Tabla")
        btn_limpiar.setStyleSheet(BUTTON_GENERAL_DESIGN)

        

        button_layout.addWidget(btn_generar_recibo)
        button_layout.addWidget(btn_limpiar)
        button_layout.addWidget(btn_gen_pdf)

        self.layout.addLayout(button_layout)
        self.layout.addLayout(tables_layout)
  
