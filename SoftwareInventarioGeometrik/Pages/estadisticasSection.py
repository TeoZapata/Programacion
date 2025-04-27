import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon

class estadisticasSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Etiqueta de título
        self.title_label = QLabel("Estadísticas")
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Contenedor de páginas
        self.pages_container = QStackedWidget()
        self.layout.addWidget(self.pages_container)

        # Página de gráficos
        self.graphs_page = QWidget()
        self.graphs_layout = QVBoxLayout(self.graphs_page)
        self.graphs_layout.setContentsMargins(10, 10, 10, 10)
        self.graphs_layout.setSpacing(10)

        # Gráfica de torta
        self.pie_chart_label = QLabel("Gráfica de Torta")
        self.pie_chart_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.pie_chart_label.setAlignment(Qt.AlignCenter)
        self.graphs_layout.addWidget(self.pie_chart_label)

        # Placeholder para la gráfica de torta
        self.pie_chart_placeholder = QLabel("Aquí irá la gráfica de torta")
        self.pie_chart_placeholder.setAlignment(Qt.AlignCenter)
        self.pie_chart_placeholder.setStyleSheet("border: 1px solid black;")
        self.graphs_layout.addWidget(self.pie_chart_placeholder)

        # Gráfica de línea para el precio del inventario
        self.line_chart_label = QLabel("Gráfica de Línea - Precio del Inventario")
        self.line_chart_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.line_chart_label.setAlignment(Qt.AlignCenter)
        self.graphs_layout.addWidget(self.line_chart_label)

        # Placeholder para la gráfica de línea
        self.line_chart_placeholder = QLabel("Aquí irá la gráfica de línea")
        self.line_chart_placeholder.setAlignment(Qt.AlignCenter)
        self.line_chart_placeholder.setStyleSheet("border: 1px solid black;")
        self.graphs_layout.addWidget(self.line_chart_placeholder)

        # Gráfica de barras
        self.bar_chart_label = QLabel("Gráfica de Barras")
        self.bar_chart_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.bar_chart_label.setAlignment(Qt.AlignCenter)
        self.graphs_layout.addWidget(self.bar_chart_label)

        # Placeholder para la gráfica de barras
        self.bar_chart_placeholder = QLabel("Aquí irá la gráfica de barras")
        self.bar_chart_placeholder.setAlignment(Qt.AlignCenter)
        self.bar_chart_placeholder.setStyleSheet("border: 1px solid black;")
        self.graphs_layout.addWidget(self.bar_chart_placeholder)

        # Agregar la página de gráficos al contenedor de páginas
        self.pages_container.addWidget(self.graphs_page)