import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                            QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from DataBase.storeDB import *

class StatisticsWorker(QThread):
    """Worker thread para cargar datos sin bloquear la UI"""
    data_loaded = pyqtSignal(dict)
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        
    def run(self):
        try:
            data = {}
            
            # Datos de registro (ingresos, salidas, devoluciones)
            registro_query = """
                SELECT tipo_movimiento, COUNT(*) as cantidad, 
                       SUM(CASE WHEN precio IS NOT NULL THEN precio ELSE 0 END) as total_valor
                FROM registro 
                GROUP BY tipo_movimiento
            """
            registro_data = self.db.ejecutar_consulta(registro_query, ())
            data['registro'] = registro_data if registro_data else []
            
            # Datos de inventario por rangos de precio
            inventario_query = """
                SELECT nombre, precio_unitario, cantidad_stock
                FROM inventario 
                WHERE precio_unitario IS NOT NULL AND precio_unitario > 0
                ORDER BY precio_unitario
            """
            inventario_data = self.db.ejecutar_consulta(inventario_query, ())
            data['inventario'] = inventario_data if inventario_data else []
            
            # Datos de proyectos
            proyectos_query = """
                SELECT estado, COUNT(*) as cantidad,
                       AVG(CASE WHEN presupuesto IS NOT NULL THEN presupuesto ELSE 0 END) as promedio_presupuesto
                FROM proyectos 
                GROUP BY estado
            """
            proyectos_data = self.db.ejecutar_consulta(proyectos_query, ())
            data['proyectos'] = proyectos_data if proyectos_data else []
            
            # Evolución temporal de registros
            temporal_query = """
                SELECT DATE(fecha) as fecha, tipo_movimiento, COUNT(*) as cantidad
                FROM registro 
                WHERE fecha IS NOT NULL
                GROUP BY DATE(fecha), tipo_movimiento
                ORDER BY fecha DESC
                LIMIT 30
            """
            temporal_data = self.db.ejecutar_consulta(temporal_query, ())
            data['temporal'] = temporal_data if temporal_data else []
            
            self.data_loaded.emit(data)
            
        except Exception as e:
            print(f"Error loading statistics data: {e}")
            self.data_loaded.emit({})

class ChartWidget(QWidget):
    """Widget personalizado para contener gráficos de matplotlib"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def clear(self):
        self.figure.clear()
        self.canvas.draw()

class estadisticasSection(QWidget):
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.charts_data = {}
        self.init_ui()
        if self.db:
            self.load_statistics_data()
        
    def init_ui(self):
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Etiqueta de título
        self.title_label = QLabel("Estadísticas")
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("padding: 15px; background-color: #f0f0f0; border-bottom: 2px solid #ccc;")
        self.layout.addWidget(self.title_label)

        # Área de scroll para los gráficos
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Contenedor de páginas
        self.pages_container = QWidget()
        self.pages_layout = QVBoxLayout(self.pages_container)
        self.pages_layout.setContentsMargins(10, 10, 10, 10)
        self.pages_layout.setSpacing(20)

        # Crear los widgets de los gráficos
        self.create_chart_widgets()
        
        self.scroll_area.setWidget(self.pages_container)
        self.layout.addWidget(self.scroll_area)

    def create_chart_widgets(self):
        """Crear los widgets para cada gráfico"""
        
        # Gráfica de torta - Movimientos de registro
        self.pie_chart_frame = QFrame()
        self.pie_chart_frame.setFrameStyle(QFrame.Box)
        self.pie_chart_layout = QVBoxLayout(self.pie_chart_frame)
        
        self.pie_chart_label = QLabel("Distribución de Movimientos (Registro)")
        self.pie_chart_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.pie_chart_label.setAlignment(Qt.AlignCenter)
        self.pie_chart_layout.addWidget(self.pie_chart_label)
        
        self.pie_chart_widget = ChartWidget()
        self.pie_chart_layout.addWidget(self.pie_chart_widget)
        self.pages_layout.addWidget(self.pie_chart_frame)

        # Gráfica de línea - Evolución temporal
        self.line_chart_frame = QFrame()
        self.line_chart_frame.setFrameStyle(QFrame.Box)
        self.line_chart_layout = QVBoxLayout(self.line_chart_frame)
        
        self.line_chart_label = QLabel("Evolución Temporal de Movimientos")
        self.line_chart_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.line_chart_label.setAlignment(Qt.AlignCenter)
        self.line_chart_layout.addWidget(self.line_chart_label)
        
        self.line_chart_widget = ChartWidget()
        self.line_chart_layout.addWidget(self.line_chart_widget)
        self.pages_layout.addWidget(self.line_chart_frame)

        # Gráfica de barras - Rangos de precios del inventario
        self.bar_chart_frame = QFrame()
        self.bar_chart_frame.setFrameStyle(QFrame.Box)
        self.bar_chart_layout = QVBoxLayout(self.bar_chart_frame)
        
        self.bar_chart_label = QLabel("Distribución de Precios - Inventario")
        self.bar_chart_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.bar_chart_label.setAlignment(Qt.AlignCenter)
        self.bar_chart_layout.addWidget(self.bar_chart_label)
        
        self.bar_chart_widget = ChartWidget()
        self.bar_chart_layout.addWidget(self.bar_chart_widget)
        self.pages_layout.addWidget(self.bar_chart_frame)

        # Gráfica de proyectos
        self.projects_chart_frame = QFrame()
        self.projects_chart_frame.setFrameStyle(QFrame.Box)
        self.projects_chart_layout = QVBoxLayout(self.projects_chart_frame)
        
        self.projects_chart_label = QLabel("Estadísticas de Proyectos")
        self.projects_chart_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.projects_chart_label.setAlignment(Qt.AlignCenter)
        self.projects_chart_layout.addWidget(self.projects_chart_label)
        
        self.projects_chart_widget = ChartWidget()
        self.projects_chart_layout.addWidget(self.projects_chart_widget)
        self.pages_layout.addWidget(self.projects_chart_frame)

        # Placeholders iniciales
        self.show_loading_placeholders()

    def show_loading_placeholders(self):
        """Mostrar placeholders mientras cargan los datos"""
        for chart_widget in [self.pie_chart_widget, self.line_chart_widget, 
                           self.bar_chart_widget, self.projects_chart_widget]:
            ax = chart_widget.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Cargando datos...', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            chart_widget.canvas.draw()

    def load_statistics_data(self):
        """Cargar datos estadísticos en un hilo separado"""
        if not self.db:
            return
            
        self.worker = StatisticsWorker(self.db)
        self.worker.data_loaded.connect(self.on_data_loaded)
        self.worker.start()

    def on_data_loaded(self, data):
        """Callback cuando se cargan los datos"""
        self.charts_data = data
        self.create_pie_chart()
        self.create_line_chart()
        self.create_bar_chart()
        self.create_projects_chart()

    def create_pie_chart(self):
        """Crear gráfica de torta para movimientos de registro"""
        self.pie_chart_widget.clear()
        
        if not self.charts_data.get('registro'):
            ax = self.pie_chart_widget.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No hay datos de registro disponibles', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
            self.pie_chart_widget.canvas.draw()
            return

        # Preparar datos
        tipos = []
        cantidades = []
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        
        for row in self.charts_data['registro']:
            tipo = row[0] if row[0] else 'Sin tipo'
            cantidad = row[1] if row[1] else 0
            tipos.append(tipo.capitalize())
            cantidades.append(cantidad)

        if sum(cantidades) == 0:
            ax = self.pie_chart_widget.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No hay movimientos registrados', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
            self.pie_chart_widget.canvas.draw()
            return

        # Crear gráfica
        ax = self.pie_chart_widget.figure.add_subplot(111)
        wedges, texts, autotexts = ax.pie(cantidades, labels=tipos, autopct='%1.1f%%',
                                         colors=colors[:len(tipos)], startangle=90)
        
        ax.set_title('Distribución de Movimientos por Tipo', fontsize=14, fontweight='bold')
        
        # Mejorar legibilidad
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            
        self.pie_chart_widget.canvas.draw()

    def create_line_chart(self):
        """Crear gráfica de líneas para evolución temporal"""
        self.line_chart_widget.clear()
        
        if not self.charts_data.get('temporal'):
            ax = self.line_chart_widget.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No hay datos temporales disponibles', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
            self.line_chart_widget.canvas.draw()
            return

        # Procesar datos temporales
        fechas_dict = {}
        for row in self.charts_data['temporal']:
            fecha_str = row[0]
            tipo = row[1] if row[1] else 'Sin tipo'
            cantidad = row[2] if row[2] else 0
            
            if fecha_str not in fechas_dict:
                fechas_dict[fecha_str] = {}
            fechas_dict[fecha_str][tipo] = cantidad

        if not fechas_dict:
            ax = self.line_chart_widget.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No hay datos temporales para mostrar', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
            self.line_chart_widget.canvas.draw()
            return

        # Preparar datos para el gráfico
        fechas = sorted(fechas_dict.keys())
        tipos_movimiento = set()
        for fecha_data in fechas_dict.values():
            tipos_movimiento.update(fecha_data.keys())
        
        tipos_movimiento = sorted(list(tipos_movimiento))
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

        ax = self.line_chart_widget.figure.add_subplot(111)
        
        for i, tipo in enumerate(tipos_movimiento):
            cantidades = []
            for fecha in fechas:
                cantidades.append(fechas_dict[fecha].get(tipo, 0))
            
            ax.plot(fechas, cantidades, marker='o', label=tipo.capitalize(),
                   color=colors[i % len(colors)], linewidth=2, markersize=6)

        ax.set_title('Evolución Temporal de Movimientos (Últimos 30 días)', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Fecha', fontsize=12)
        ax.set_ylabel('Cantidad de Movimientos', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Rotar etiquetas de fechas si son muchas
        if len(fechas) > 5:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.line_chart_widget.figure.tight_layout()
        self.line_chart_widget.canvas.draw()

    def create_bar_chart(self):
        """Crear gráfica de barras para rangos de precios del inventario"""
        self.bar_chart_widget.clear()
        
        if not self.charts_data.get('inventario'):
            ax = self.bar_chart_widget.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No hay datos de inventario disponibles', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
            self.bar_chart_widget.canvas.draw()
            return

        # Extraer precios
        precios = []
        for row in self.charts_data['inventario']:
            precio = row[1] if row[1] else 0
            if precio > 0:
                precios.append(precio)

        if not precios:
            ax = self.bar_chart_widget.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No hay precios válidos en el inventario', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
            self.bar_chart_widget.canvas.draw()
            return

        # Crear rangos de precios
        min_precio = min(precios)
        max_precio = max(precios)
        
        if min_precio == max_precio:
            rangos = ['Precio único']
            counts = [len(precios)]
        else:
            # Crear 5 rangos
            step = (max_precio - min_precio) / 5
            rangos = []
            counts = []
            
            for i in range(5):
                inicio = min_precio + i * step
                fin = min_precio + (i + 1) * step
                if i == 4:  # Último rango incluye el máximo
                    count = sum(1 for p in precios if inicio <= p <= fin)
                    rangos.append(f'${inicio:.0f} - ${fin:.0f}')
                else:
                    count = sum(1 for p in precios if inicio <= p < fin)
                    rangos.append(f'${inicio:.0f} - ${fin:.0f}')
                counts.append(count)

        # Crear gráfica
        ax = self.bar_chart_widget.figure.add_subplot(111)
        bars = ax.bar(range(len(rangos)), counts, color='#2E8B57', alpha=0.7)
        
        ax.set_title('Distribución de Productos por Rango de Precios', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Rango de Precios', fontsize=12)
        ax.set_ylabel('Cantidad de Productos', fontsize=12)
        ax.set_xticks(range(len(rangos)))
        ax.set_xticklabels(rangos, rotation=45, ha='right')
        
        # Agregar valores en las barras
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(count)}', ha='center', va='bottom', fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='y')
        self.bar_chart_widget.figure.tight_layout()
        self.bar_chart_widget.canvas.draw()

    def create_projects_chart(self):
        """Crear gráfica para estadísticas de proyectos"""
        self.projects_chart_widget.clear()
        
        if not self.charts_data.get('proyectos'):
            ax = self.projects_chart_widget.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No hay datos de proyectos disponibles', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
            self.projects_chart_widget.canvas.draw()
            return

        # Preparar datos
        estados = []
        cantidades = []
        presupuestos = []
        
        for row in self.charts_data['proyectos']:
            estado = row[0] if row[0] else 'Sin estado'
            cantidad = row[1] if row[1] else 0
            presupuesto = row[2] if row[2] else 0
            
            estados.append(estado.capitalize())
            cantidades.append(cantidad)
            presupuestos.append(presupuesto)

        if not estados:
            ax = self.projects_chart_widget.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No hay proyectos para mostrar', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
            self.projects_chart_widget.canvas.draw()
            return

        # Crear gráfica combinada (barras + línea)
        fig = self.projects_chart_widget.figure
        ax1 = fig.add_subplot(111)
        
        # Gráfica de barras para cantidad
        color1 = '#4CAF50'
        bars = ax1.bar(estados, cantidades, color=color1, alpha=0.7, label='Cantidad de Proyectos')
        ax1.set_xlabel('Estado del Proyecto', fontsize=12)
        ax1.set_ylabel('Cantidad de Proyectos', color=color1, fontsize=12)
        ax1.tick_params(axis='y', labelcolor=color1)
        
        # Segundo eje para presupuestos promedio
        ax2 = ax1.twinx()
        color2 = '#FF5722'
        line = ax2.plot(estados, presupuestos, color=color2, marker='o', 
                       linewidth=3, markersize=8, label='Presupuesto Promedio')
        ax2.set_ylabel('Presupuesto Promedio ($)', color=color2, fontsize=12)
        ax2.tick_params(axis='y', labelcolor=color2)
        
        # Título
        ax1.set_title('Proyectos por Estado y Presupuesto Promedio', 
                     fontsize=14, fontweight='bold')
        
        # Agregar valores en las barras
        for bar, cantidad in zip(bars, cantidades):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(cantidad)}', ha='center', va='bottom', fontweight='bold')
        
        # Agregar valores en la línea
        for i, (estado, presupuesto) in enumerate(zip(estados, presupuestos)):
            if presupuesto > 0:
                ax2.text(i, presupuesto + max(presupuestos) * 0.05,
                        f'${presupuesto:.0f}', ha='center', va='bottom', 
                        color=color2, fontweight='bold')
        
        # Leyenda combinada
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax1.grid(True, alpha=0.3)
        fig.tight_layout()
        self.projects_chart_widget.canvas.draw()

    def refresh_statistics(self):
        """Actualizar estadísticas (método público para refrescar desde fuera)"""
        if self.db:
            self.show_loading_placeholders()
            self.load_statistics_data()

# Mantener compatibilidad con nombres antiguos (por si están siendo usados)
# Estos son alias para mantener la compatibilidad
def init_ui(self):
    return self.init_ui()

def create_chart_widgets(self):
    return self.create_chart_widgets()

if __name__ == "__main__":
    # Código de prueba
    app = QApplication(sys.argv)
    
    # Simulación de base de datos para prueba

     # Usar una base de datos en memoria para pruebas
    mock_db = storeBD.iniciar_bd()
    
    window = estadisticasSection(db=mock_db)
    window.show()
    
    sys.exit(app.exec_())