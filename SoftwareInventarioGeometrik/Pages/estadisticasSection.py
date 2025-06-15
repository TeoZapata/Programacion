import sys
from PyQt5.QtWidgets import ( QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                            QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from DataBase.storeDB import *
from src.utils.estadisticaManager import *
from src.utils.graficasEstadisticas import *


class estadisticasSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()


    def init_ui(self):
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(18)

        # Etiqueta de título
        self.title_label = QLabel("Estadísticas")
        self.title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignLeft)
        self.title_label.setStyleSheet("color: #222; margin-bottom: 12px;")
        self.layout.addWidget(self.title_label)

        # Barra de botones de acciones
        self.buttons_bar = QHBoxLayout()
        self.buttons_bar.setSpacing(12)

        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_actualizar.setIcon(QIcon.fromTheme("view-refresh"))
        self.btn_actualizar.setFixedHeight(36)
        self.btn_actualizar.clicked.connect(lambda: self.ok())
        self.buttons_bar.addWidget(self.btn_actualizar)

        self.btn_imprimir = QPushButton("Imprimir Reporte")
        self.btn_imprimir.setIcon(QIcon.fromTheme("document-print"))
        self.btn_imprimir.setFixedHeight(36)
        self.buttons_bar.addWidget(self.btn_imprimir)

        self.btn_exportar = QPushButton("Exportar CSV")
        self.btn_exportar.setIcon(QIcon.fromTheme("document-save"))
        self.btn_exportar.setFixedHeight(36)
        self.buttons_bar.addWidget(self.btn_exportar)

        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.setIcon(QIcon.fromTheme("view-filter"))
        self.btn_filtrar.setFixedHeight(36)
        self.buttons_bar.addWidget(self.btn_filtrar)

        self.buttons_bar.addStretch()
        self.layout.addLayout(self.buttons_bar)

        # Área de scroll para los gráficos
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")

        # Contenedor de páginas
        self.pages_container = QWidget()
        self.pages_layout = QVBoxLayout(self.pages_container)
        self.pages_layout.setContentsMargins(0, 0, 0, 0)
        self.pages_layout.setSpacing(18)

        # Espacios reservados para futuras gráficas
        self.gen_graphica("Gráfica 1: Distribución de Movimientos",generar_grafica())
        self.gen_graphica("Gráfica 2: Evolución Temporal",generar_grafica())
        self.gen_graphica("Gráfica 3: Distribución de Precios",generar_grafica())
        self.gen_graphica("Gráfica 4: Estadísticas de Proyectos",generar_grafica())

        self.scroll_area.setWidget(self.pages_container)
        self.layout.addWidget(self.scroll_area)
        
        # Aplicar estilos generales
        self.apply_styles()

    def gen_graphica(self, title, grafica_widget):
        card = QWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 18, 24, 18)
        card_layout.setSpacing(10)
        card.setStyleSheet("""
            background: #fff;
            border-radius: 18px;
        """)
        label = QLabel(title)
        label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        label.setStyleSheet("color: #3a3a3a; margin-bottom: 6px;")
        label.setAlignment(Qt.AlignLeft)
        card_layout.addWidget(label)

        # Placeholder visual para la gráfica
        placeholder = QLabel("Espacio para gráfica")
        placeholder.setMinimumHeight(180)
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #aaa; font-size: 16px; border: 1px dashed #bbb; border-radius: 12px;")

        grafica_widget.setMinimumHeight(220)
        card_layout.addWidget(grafica_widget)
        card_layout.addWidget(placeholder)
        self.pages_layout.addWidget(card)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background: #f5f7fa;
            }
            QLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QPushButton {
                background: #e3e7ef;
                border: none;
                border-radius: 8px;
                padding: 0 18px;
                font-size: 15px;
                color: #2a2a2a;
            }
            QPushButton:hover {
                background: #d0d6e6;
            }
        """)
   