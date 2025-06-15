import sys
import json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

class LoadingScreen(QSplashScreen):
    """Pantalla de carga elegante con animación"""
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Crear pixmap transparente
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.transparent)
        self.setPixmap(pixmap)
        
        # Configurar animación
        self.movie = QMovie()
        self.setup_animation()
        
    def setup_animation(self):
        """Configurar animación de carga"""
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)
        
    def update_progress(self):
        self.progress += 2
        if self.progress > 100:
            self.progress = 0
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fondo glassmorphism
        painter.fillRect(self.rect(), QColor(255, 255, 255, 30))
        
        # Borde redondeado
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 15, 15)
        painter.setClipPath(path)
        
        # Gradiente de fondo
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(64, 224, 208, 100))
        gradient.setColorAt(1, QColor(0, 191, 255, 100))
        painter.fillRect(self.rect(), gradient)
        
        # Texto principal
        painter.setPen(QColor(50, 50, 50))
        font = QFont("Segoe UI", 18, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, "SolarQuote Pro\nCargando...")
        
        # Barra de progreso circular
        center = QPoint(self.width()//2, self.height()//2 + 50)
        radius = 30
        angle = int(self.progress * 3.6)
        
        painter.setPen(QPen(QColor(100, 100, 100, 150), 4))
        painter.drawEllipse(center, radius, radius)
        
        painter.setPen(QPen(QColor(0, 255, 127), 6))
        painter.drawArc(center.x()-radius, center.y()-radius, 2*radius, 2*radius, 90*16, -angle*16)

class GlassWidget(QWidget):
    """Widget base con efecto cristal"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fondo glassmorphism
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 12, 12)
        
        # Gradiente de fondo
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 40))
        gradient.setColorAt(1, QColor(255, 255, 255, 20))
        
        painter.fillPath(path, gradient)
        
        # Borde sutil
        painter.setPen(QPen(QColor(255, 255, 255, 80), 1))
        painter.drawPath(path)

class StyledButton(QPushButton):
    """Botón personalizado con efecto glassmorphism"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 12px 24px;
                color: #2c3e50;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
                color: #1a252f;
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.1);
            }
        """)

class StyledLineEdit(QLineEdit):
    """Campo de texto personalizado"""
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                padding: 10px;
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(0, 255, 127, 0.8);
                background: rgba(255, 255, 255, 0.15);
            }
        """)

class ConsumptionWidget(GlassWidget):
    """Widget para gestionar consumos mensuales"""
    def __init__(self):
        super().__init__()
        self.consumptions = {}
        self.billing_type = "mensual"
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("Consumos de Energía")
        title.setStyleSheet("color: #2c3e50; font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Tipo de facturación
        billing_layout = QHBoxLayout()
        billing_label = QLabel("Tipo de facturación:")
        billing_label.setStyleSheet("color: #2c3e50; font-size: 14px;")
        
        self.billing_combo = QComboBox()
        self.billing_combo.addItems(["Mensual", "Bimensual"])
        self.billing_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                padding: 8px;
                color: #2c3e50;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2c3e50;
            }
        """)
        self.billing_combo.currentTextChanged.connect(self.on_billing_changed)
        
        billing_layout.addWidget(billing_label)
        billing_layout.addWidget(self.billing_combo)
        billing_layout.addStretch()
        layout.addLayout(billing_layout)
        
        # Área de scroll para consumos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 5px;
            }
        """)
        
        self.consumption_widget = QWidget()
        self.consumption_layout = QVBoxLayout(self.consumption_widget)
        scroll.setWidget(self.consumption_widget)
        
        layout.addWidget(scroll)
        
        # Botón agregar consumo
        add_btn = StyledButton("+ Agregar Consumo")
        add_btn.clicked.connect(self.add_consumption_field)
        layout.addWidget(add_btn)
        
        # Agregar algunos campos iniciales
        self.update_consumption_fields()
        
    def on_billing_changed(self, text):
        self.billing_type = text.lower()
        self.update_consumption_fields()
        
    def update_consumption_fields(self):
        # Limpiar campos existentes
        for i in reversed(range(self.consumption_layout.count())):
            self.consumption_layout.itemAt(i).widget().deleteLater()
            
        months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        if self.billing_type == "bimensual":
            periods = ["Ene-Feb", "Mar-Abr", "May-Jun", "Jul-Ago", "Sep-Oct", "Nov-Dic"]
        else:
            periods = months
            
        for period in periods:
            self.add_consumption_field(period)
            
    def add_consumption_field(self, period=None):
        if period is None:
            period = f"Período {len(self.consumptions) + 1}"
            
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        period_label = QLabel(period)
        period_label.setStyleSheet("color: #2c3e50; min-width: 100px; font-size: 14px;")
        period_label.setAlignment(Qt.AlignLeft)
        
        consumption_field = StyledLineEdit("kWh")
        consumption_field.setValidator(QDoubleValidator(0.00, 99999.99, 2))
        
        unit_label = QLabel("kWh")
        unit_label.setStyleSheet("color: rgba(44, 62, 80, 0.7); font-size: 12px;")
        
        row_layout.addWidget(period_label)
        row_layout.addWidget(consumption_field)
        row_layout.addWidget(unit_label)
        
        self.consumption_layout.addWidget(row_widget)
        self.consumptions[period] = consumption_field

class CustomerInfoWidget(GlassWidget):
    """Widget para información del cliente"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("Información del Cliente")
        title.setStyleSheet("color: #2c3e50; font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Campos del cliente
        self.name_field = StyledLineEdit("Nombre completo")
        self.account_field = StyledLineEdit("Número de cuenta")
        self.email_field = StyledLineEdit("Email")
        self.phone_field = StyledLineEdit("Teléfono")
        self.address_field = StyledLineEdit("Dirección")
        
        # Organizar en grid
        grid = QGridLayout()
        grid.setSpacing(15)
        
        grid.addWidget(QLabel("Nombre:"), 0, 0)
        grid.addWidget(self.name_field, 0, 1)
        
        grid.addWidget(QLabel("No. Cuenta:"), 1, 0)
        grid.addWidget(self.account_field, 1, 1)
        
        grid.addWidget(QLabel("Email:"), 2, 0)
        grid.addWidget(self.email_field, 2, 1)
        
        grid.addWidget(QLabel("Teléfono:"), 3, 0)
        grid.addWidget(self.phone_field, 3, 1)
        
        grid.addWidget(QLabel("Dirección:"), 4, 0)
        grid.addWidget(self.address_field, 4, 1)
        
        # Estilo para labels
        for i in range(5):
            label = grid.itemAtPosition(i, 0).widget()
            label.setStyleSheet("color: #2c3e50; font-size: 14px; font-weight: bold;")
            
        layout.addLayout(grid)
        layout.addStretch()

class QuoteResultWidget(GlassWidget):
    """Widget para mostrar resultados de cotización"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("Cotización Solar")
        title.setStyleSheet("color: #2c3e50; font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Área de resultados
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 15px;
                color: #2c3e50;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.results_area)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.calculate_btn = StyledButton("Calcular Cotización")
        self.export_btn = StyledButton("Exportar PDF")
        self.save_btn = StyledButton("Guardar Proyecto")
        
        button_layout.addWidget(self.calculate_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)

class SidebarWidget(GlassWidget):
    """Barra lateral de navegación"""
    page_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_page = 0
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 20)
        
        # Logo/Título
        logo_label = QLabel("SolarQuote\nPro")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            color: #2c3e50;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 30px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
        """)
        layout.addWidget(logo_label)
        
        # Botones de navegación
        self.nav_buttons = []
        pages = [
            ("Cliente", "👤"),
            ("Consumos", "📊"),
            ("Cotización", "💰"),
            ("Configuración", "⚙️")
        ]
        
        for i, (name, icon) in enumerate(pages):
            btn = QPushButton(f"{icon} {name}")
            btn.setCheckable(True)
            btn.setStyleSheet(self.get_nav_button_style())
            btn.clicked.connect(lambda checked, idx=i: self.on_page_select(idx))
            
            self.nav_buttons.append(btn)
            layout.addWidget(btn)
            
        # Seleccionar primera página
        self.nav_buttons[0].setChecked(True)
        
        layout.addStretch()
        
        # Información adicional
        info_label = QLabel("v1.0.0\n© 2024")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: rgba(44, 62, 80, 0.5); font-size: 12px;")
        layout.addWidget(info_label)
        
    def get_nav_button_style(self):
        return """
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 15px;
                color: #2c3e50;
                font-size: 14px;
                text-align: left;
                min-height: 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.4);
                color: #1a252f;
            }
            QPushButton:checked {
                background: rgba(0, 255, 127, 0.3);
                border: 1px solid rgba(0, 255, 127, 0.6);
                color: #1a252f;
            }
        """
        
    def on_page_select(self, index):
        # Desmarcar todos los botones
        for btn in self.nav_buttons:
            btn.setChecked(False)
            
        # Marcar el botón seleccionado
        self.nav_buttons[index].setChecked(True)
        self.current_page = index
        self.page_changed.emit(index)

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        self.setWindowTitle("SolarQuote Pro - Cotizador de Proyectos Solares")
        self.setMinimumSize(1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = SidebarWidget()
        self.sidebar.setFixedWidth(200)
        main_layout.addWidget(self.sidebar)
        
        # Área de contenido
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)
        
        # Páginas
        self.customer_page = CustomerInfoWidget()
        self.consumption_page = ConsumptionWidget()
        self.quote_page = QuoteResultWidget()
        self.config_page = GlassWidget()  # Placeholder para configuración
        
        self.content_stack.addWidget(self.customer_page)
        self.content_stack.addWidget(self.consumption_page)
        self.content_stack.addWidget(self.quote_page)
        self.content_stack.addWidget(self.config_page)
        
        # Estilo de ventana
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e3c72, stop:1 #2a5298);
            }
        """)
        
    def setup_connections(self):
        self.sidebar.page_changed.connect(self.content_stack.setCurrentIndex)
        
        # Conectar botón de calcular
        self.quote_page.calculate_btn.clicked.connect(self.calculate_quote)
        self.quote_page.export_btn.clicked.connect(self.export_pdf)
        self.quote_page.save_btn.clicked.connect(self.save_project)
        
    def calculate_quote(self):
        """Calcular cotización básica"""
        # Obtener datos del cliente
        customer_name = self.customer_page.name_field.text()
        account_number = self.customer_page.account_field.text()
        
        # Obtener consumos
        total_consumption = 0
        consumptions = []
        
        for period, field in self.consumption_page.consumptions.items():
            try:
                value = float(field.text()) if field.text() else 0
                consumptions.append((period, value))
                total_consumption += value
            except ValueError:
                continue
                
        # Cálculos básicos (simplificados)
        avg_monthly = total_consumption / len(consumptions) if consumptions else 0
        annual_consumption = avg_monthly * 12
        
        # Estimación de sistema solar (ejemplo)
        system_size_kw = annual_consumption / 1200  # Factor simplificado
        panel_count = int(system_size_kw / 0.4)  # Paneles de 400W
        estimated_cost = system_size_kw * 1200  # $1200 por kW instalado
        
        # Mostrar resultados
        results = f"""
        COTIZACIÓN SISTEMA SOLAR FOTOVOLTAICO
        =====================================
        
        CLIENTE: {customer_name}
        CUENTA: {account_number}
        FECHA: {datetime.now().strftime('%d/%m/%Y')}
        
        ANÁLISIS DE CONSUMO:
        - Consumo promedio mensual: {avg_monthly:.2f} kWh
        - Consumo anual estimado: {annual_consumption:.2f} kWh
        - Tipo de facturación: {self.consumption_page.billing_type}
        
        DIMENSIONAMIENTO DEL SISTEMA:
        - Potencia recomendada: {system_size_kw:.2f} kW
        - Número de paneles: {panel_count}
        - Generación anual estimada: {annual_consumption * 0.95:.2f} kWh
        
        INVERSIÓN:
        - Costo estimado del sistema: ${estimated_cost:,.2f}
        - Ahorro anual estimado: ${annual_consumption * 0.12:.2f}
        - Tiempo de retorno: {estimated_cost / (annual_consumption * 0.12):.1f} años
        
        DETALLES DE CONSUMO:
        """
        
        for period, value in consumptions:
            results += f"- {period}: {value:.2f} kWh\n"
            
        self.quote_page.results_area.setPlainText(results)
        
    def export_pdf(self):
        """Exportar cotización a PDF"""
        QMessageBox.information(self, "Exportar", "Función de exportar PDF en desarrollo")
        
    def save_project(self):
        """Guardar proyecto"""
        QMessageBox.information(self, "Guardar", "Función de guardar proyecto en desarrollo")

class SolarQuoteApp(QApplication):
    """Aplicación principal optimizada"""
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("SolarQuote Pro")
        self.setApplicationVersion("1.0.0")
        
        # Configurar estilo global
        self.setStyle("Fusion")
        
        # Mostrar splash screen
        self.splash = LoadingScreen()
        self.splash.show()
        
        # Timer para simular carga
        QTimer.singleShot(2000, self.show_main_window)
        
    def show_main_window(self):
        """Mostrar ventana principal después de la carga"""
        self.main_window = MainWindow()
        self.main_window.show()
        self.splash.finish(self.main_window)

def main():
    app = SolarQuoteApp(sys.argv)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()