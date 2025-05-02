from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QTabWidget, QLabel
from .TabsMateriales import *
from Style import *


class materialesSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(0)
        # Contenedor de pestañas
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        # Agregar pestañas
        # Aplicar un estilo personalizado a las pestañas
        self.tab_widget.setStyleSheet(TAB_DESIGN_GENERAL)
        # hace que tab_widget ocupe todo el espacio disponible
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabBarAutoHide(True)
        
        self.tab_widget.addTab(SalidaMaterial(), "Salida de Material")
        self.tab_widget.addTab(EntradaMaterial(), "Entrada de Material")
        self.tab_widget.addTab(DevolucionMaterial(), "Devolución de Material")
        self.tab_widget.addTab(SubirListadoClickUp(), "Subir Listado de Material")
        self.tab_widget.addTab(HistorialMaterial(), "Historial de Material")

        # Establecer el tamaño mínimo de la pestaña