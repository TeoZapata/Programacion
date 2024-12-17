import sys
import google.generativeai as genai
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,QFileDialog,
                             QWidget, QAction, QStackedWidget)
from src.IniciarCotizaciones import IniciarCotizacionWindow
from src.HistorialCotizaciones import HistorialCotizacionWindow
from src.DBInversores import BDInversoresWindow
from src.GenerarDocumentos import DocumentoGenerarWindow


# Configura tu clave de API de Gemini
GEMINI_API_KEY = 'AIzaSyCbjnUU79z4mnAo4VVa7QxLSLuOiYNNjlo'  # Reemplaza con tu clave real

class ImageAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setup_gemini()

    def setup_gemini(self):
        """Configurar cliente de Gemini"""
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def initUI(self):
        """Inicializar la interfaz de usuario"""
        self.setWindowTitle('Sistema de Gestión de Inversiones')
        self.setGeometry(100, 100, 1000, 700)

        # Crear widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Crear barra de navegación
        self.create_navbar()

        # Crear área de pestañas/ventanas
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Crear ventanas
        self.iniciar_cotizacion = IniciarCotizacionWindow()
        self.historial_cotizacion = HistorialCotizacionWindow()
        self.bd_inversores = BDInversoresWindow()
        self.documento_generar = DocumentoGenerarWindow()

        # Agregar ventanas al stacked widget
        self.stacked_widget.addWidget(self.iniciar_cotizacion)
        self.stacked_widget.addWidget(self.historial_cotizacion)
        self.stacked_widget.addWidget(self.bd_inversores)
        self.stacked_widget.addWidget(self.documento_generar)

    def create_navbar(self):
        """Crear barra de navegación"""
        navbar = self.menuBar()
        
        # Menú Cotizaciones
        cotizaciones_menu = navbar.addMenu('Cotizaciones')
        
        iniciar_action = QAction('Iniciar Cotización', self)
        iniciar_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.iniciar_cotizacion))
        cotizaciones_menu.addAction(iniciar_action)
        
        historial_action = QAction('Historial de Cotizaciones', self)
        historial_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.historial_cotizacion))
        cotizaciones_menu.addAction(historial_action)

        # Menú Base de Datos
        bd_menu = navbar.addMenu('Base de Datos')
        
        inversores_action = QAction('BD Inversores', self)
        inversores_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.bd_inversores))
        bd_menu.addAction(inversores_action)

        # Menú Documentos
        documentos_menu = navbar.addMenu('Documentos')
        
        generar_action = QAction('Generar Documento', self)
        generar_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.documento_generar))
        documentos_menu.addAction(generar_action)

    def select_image(self):
        """Seleccionar imagen y analizar"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            'Seleccionar Imagen', 
            '', 
            'Archivos de Imagen (*.png *.jpg *.jpeg *.bmp *.gif)'
        )
        
        if file_path:
            # Lógica para análisis de imagen (similar al código original)
            pass

def main():
    app = QApplication(sys.argv)
    # Establecer estilo fusion para una apariencia moderna
    app.setStyle('Fusion')
    window = ImageAnalysisApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()