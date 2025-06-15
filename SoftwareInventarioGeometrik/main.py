import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QStackedWidget, QTabWidget, QSizePolicy)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon
from Pages import *
from Style import *

class MainWindow(QMainWindow):
    # Configuration for pages/tabs
    PAGE_CONFIG = [
        ("Inventario", inventarioSection),
        ("Materiales", materialesSection),
        ("Herramientas", HerramientasSection),
        ("Registros", RegistroSection),
        ("Estadísticas", estadisticasSection)
    ]

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

        # Initialize attributes that will be created by initialize_ui
        self.navbar = None
        self.pages = None
        self.section_widgets = [] # Will be sized in init_pages
        self.initialize_ui_called = False

        self.setWindowState(Qt.WindowMaximized)  # Maximizar

        # Defer full UI initialization to make the window appear faster
        QTimer.singleShot(0, self.initialize_ui)

    def initialize_ui(self):
        """Initializes navbar, pages, and loads the first page."""
        self.init_navbar()
        self.init_pages()
        self.initialize_ui_called = True
        if self.PAGE_CONFIG: # Ensure there's at least one page
            self.change_page(0) # Load the first page

    def init_navbar(self):
        # Crear un QTabWidget para la barra de navegación
        self.navbar = QTabWidget()
        self.navbar.setStyleSheet(TAB_MAIN_DESIGN) # Asegurar que las pestañas estén en la parte superior
        self.navbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Ajustar la política de tamaño

        # Añadir pestañas al QTabWidget
        for tab_name, _ in self.PAGE_CONFIG:
            self.navbar.addTab(QWidget(), tab_name) # Add placeholder tab content

        # Conectar el cambio de pestaña al cambio de página
        self.navbar.currentChanged.connect(self.change_page)

        # Añadir el QTabWidget al layout principal
        self.main_layout.addWidget(self.navbar)

    def init_pages(self):
        # Crear el widget apilado para manejar las páginas
        self.pages = QStackedWidget()
        self.section_widgets = [None] * len(self.PAGE_CONFIG)

        # Añadir placeholders al QStackedWidget
        for _ in range(len(self.PAGE_CONFIG)):
            self.pages.addWidget(QWidget())  # Placeholder vacío

        # Añadir el widget apilado al layout principal
        self.main_layout.addWidget(self.pages)

    def change_page(self, index):
        if not self.initialize_ui_called:
            # UI not fully initialized, defer this call
            QTimer.singleShot(10, lambda: self.change_page(index))
            return

        if not (self.pages and self.navbar): # Should not happen if initialize_ui_called is true
            print("Warning: change_page called but UI widgets (pages/navbar) not fully initialized.")
            QTimer.singleShot(10, lambda: self.change_page(index)) # Retry
            return

        if 0 <= index < len(self.PAGE_CONFIG):
            if self.section_widgets[index] is None:
                _tab_name, PageClass = self.PAGE_CONFIG[index]
                self.section_widgets[index] = PageClass() # Instantiate the actual page

                # Replace the placeholder widget in QStackedWidget
                placeholder_widget = self.pages.widget(index)
                if placeholder_widget:
                    self.pages.removeWidget(placeholder_widget)
                    placeholder_widget.deleteLater()
                
                self.pages.insertWidget(index, self.section_widgets[index])

            self.pages.setCurrentIndex(index)

            # Sync navbar if the change didn't originate from it
            if self.navbar.currentIndex() != index:
                self.navbar.setCurrentIndex(index)
        else:
            print(f"Error: Page index {index} is out of bounds.")

if __name__ == "__main__":
    app = QApplication(sys.argv) # Use sys.argv
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) # Ensure proper exit

# Function to be called by app.py (if you have a separate entry point like app.py)
def run_app(username=None):
    """
    Initializes and shows the main application window.
    Assumes QApplication instance is already created and managed by the caller.
    """
    # The username parameter is available if needed by MainWindow or its pages
    main_window = MainWindow()
    main_window.show()
    # The app.exec_() is handled by the calling script (e.g., app.py)
