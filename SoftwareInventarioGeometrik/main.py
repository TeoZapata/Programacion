import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from Pages import *
from Style import *
from DataBase import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana principal
        self.setWindowTitle("Geometrik - Inventario Version 2.0")
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowIcon(QIcon("path/to/your/icon.png"))
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Crear la barra de navegación
        self.init_navbar()
        
        # Crear el contenedor de páginas
        self.init_pages()
        
        # Establecer la primera página como predeterminada
        self.change_page(0)
    
    def init_navbar(self):
        # Crear el widget para la barra de navegación
        navbar = QWidget()
        navbar.setStyleSheet("background-color: #2C3E50;")
        navbar.setMinimumHeight(70)
        navbar.setMaximumHeight(70)
        
        # Layout horizontal para los botones de navegación
        nav_layout = QHBoxLayout(navbar)
        nav_layout.setContentsMargins(20, 5, 20, 5)
        nav_layout.setSpacing(15)
        
        # Crear los botones para las diferentes secciones
        self.nav_buttons = []
        sections = ["Inventario", "Materiales", "Proyectos", "Clientes", "Estadisticas"]
        name = ['inventario', 'in-out', 'proyecto', 'clientes', 'graph']
        
        # Añadir un espaciador al inicio para mejor distribución
        nav_layout.addStretch(1)
        
        for i, section in enumerate(sections):
            button = QPushButton(f'{section}')
            button.setCheckable(True)
            button.setStyleSheet(BUTTON_TAB_MAIN)
            button.setFont(QFont("Fantasy", 15))
            
            icon = QIcon(f'src/svg/{name[i]}.svg')
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(QSize(30, 30)))
            icon_label.setAlignment(Qt.AlignVCenter)
            
            nav_layout.addWidget(icon_label)
            nav_layout.addWidget(button)
            self.nav_buttons.append(button)
        
        # Añadir un espaciador al final para mejor distribución
        nav_layout.addStretch(1)
        
        # Añadir la barra de navegación al layout principal
        self.main_layout.addWidget(navbar)
    
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
        
        # Conectar los botones de navegación a la función de cambio de página
        for i, button in enumerate(self.nav_buttons):
            button.clicked.connect(lambda checked, idx=i: self.change_page(idx))

    def change_page(self, index):
        # Cargar la página si no ha sido inicializada
        if self.section_widgets[index] is None:
            self.section_widgets[index] = self.load_section(index)
            self.pages.insertWidget(index, self.section_widgets[index])
        
        # Cambiar a la página seleccionada
        self.pages.setCurrentIndex(index)
        
        # Actualizar el estado de los botones de navegación
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)
    
    def load_section(self, index):
        # Cargar la sección correspondiente
        sections = [
            inventarioSection,
            materialesSection,
            proyectoSecion,
            clientesSection,
            estadisticasSection,
        ]
        return sections[index]()

# Ejecutar la aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())