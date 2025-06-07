import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from Pages import *
from Style import *
from DataBase import *
from Pages.registrosSection import RegistroSection



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana principal
        self.setWindowTitle("Geometrik - Inventario Version 2.0")
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color:hsl(180, 29%, 78%);")

        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.init_navbar()
        self.init_pages()
        self.change_page(0)
        self.setWindowState(Qt.WindowMaximized)  # Maximizar)
    
    def init_navbar(self):
        # Crear un QTabWidget para la barra de navegación
        self.navbar = QTabWidget()
        self.navbar.setStyleSheet(TAB_MAIN_DESIGN) # Asegurar que las pestañas estén en la parte superior
        self.navbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Ajustar la política de tamaño
        
        # Añadir pestañas al QTabWidget
        self.navbar.addTab(QWidget(), "Inventario")
        self.navbar.addTab(QWidget(), "Materiales")
        self.navbar.addTab(QWidget(), "Herramientas")
        self.navbar.addTab(QWidget(), "Registros")
        self.navbar.addTab(QWidget(), "Estadísticas")
        
        # Conectar el cambio de pestaña al cambio de página
        self.navbar.currentChanged.connect(self.change_page)
        
        # Añadir el QTabWidget al layout principal
        self.main_layout.addWidget(self.navbar)

    def init_pages(self):
        # Crear el widget apilado para manejar las páginas
        self.pages = QStackedWidget()
        
        # Inicializar las páginas como None para cargarlas de forma diferida
        self.section_widgets = [None] * 5
        
        # Añadir placeholders al QStackedWidget
        for _ in range(5):
            self.pages.addWidget(QWidget())  # Placeholder vacío
        
        # Añadir el widget apilado al layout principal
        self.main_layout.addWidget(self.pages)

    def change_page(self, index):
        # Cargar la página correspondiente solo si no ha sido inicializada
        if index == 0:
            if self.section_widgets[0] is None:
                self.section_widgets[0] = inventarioSection()
                self.pages.insertWidget(0, self.section_widgets[0])
            self.pages.setCurrentWidget(self.section_widgets[0])

        elif index == 1:
            if self.section_widgets[1] is None:
                self.section_widgets[1] = materialesSection()
                self.pages.insertWidget(1, self.section_widgets[1])
            self.pages.setCurrentWidget(self.section_widgets[1])
        elif index == 2:
            if self.section_widgets[2] is None:
                self.section_widgets[2] = HerramientasSection()
                self.pages.insertWidget(2, self.section_widgets[2])
            self.pages.setCurrentWidget(self.section_widgets[2])

        elif index == 3:
            if self.section_widgets[3] is None:
                self.section_widgets[3] = RegistroSection()
                self.pages.insertWidget(3, self.section_widgets[3])
            self.pages.setCurrentWidget(self.section_widgets[3])

        elif index == 4:
            if self.section_widgets[4] is None:
                self.section_widgets[4] = estadisticasSection()
                self.pages.insertWidget(4, self.section_widgets[4])
            self.pages.setCurrentWidget(self.section_widgets[4])


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
