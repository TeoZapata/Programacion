from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QTabWidget, QLabel
from Style import *
from Pages import *
from Pages.empleadosSection import EmpleadosSection  # Add this import if EmpleadosSection is defined in Pages/EmpleadosSection.py
from Pages.proveedoresSection import ProveedoresSection  # Add this import if ProveedoresSection is defined in Pages/ProveedoresSection.py

class RegistroSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(15)
        # Contenedor de pestañas
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        # Agregar pestañas
        # Aplicar un estilo personalizado a las pestañas
        self.tab_widget.setStyleSheet(TAB_DESIGN_GENERAL)
        # hace que tab_widget ocupe todo el espacio disponible
        
        self.tab_widget.addTab(clientesSection(), "Clientes")
        self.tab_widget.addTab(proyecto(), "Proyectos")
        self.tab_widget.addTab(EmpleadosSection(), "Empleados")
        self.tab_widget.addTab(ProveedoresSection(), "Proveedores")


        # Establecer el tamaño mínimo de la pestaña