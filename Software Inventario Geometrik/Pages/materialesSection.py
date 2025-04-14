from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QTabWidget, QLabel
from .TabsMateriales.salidaMaterial import salidaMaterial


class materialesSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # Contenedor de pestañas
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        # Agregar pestañas
        self.tab_widget.addTab(salidaMaterial(), "Salida de Material")
        self.add_tab("Entrada de Material")
        self.add_tab("Devolución de Material")
        self.add_tab("Historia")

    def add_tab(self, tab_name):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_label = QLabel(tab_name)
        tab_label.setAlignment(Qt.AlignCenter)
        tab_layout.addWidget(tab_label)
        self.tab_widget.addTab(tab, tab_name)