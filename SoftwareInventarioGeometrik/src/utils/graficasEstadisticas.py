from PyQt5.QtWidgets import QLineEdit,QTableWidgetItem, QMessageBox,QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from Style import  *
from DataBase.storeDB import *
from src.utils.getCodeBar import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from src.utils.estadisticaManager import *

def get_datos():
    manager = EstadisticaManager()
    manager.start()
    manager.join()
    return manager

def generar_grafica():
    # Datos de ejemplo para la gráfica
    datos = get_datos()
    print(datos.clientes_stats)

    x = [1, 2, 3, 4, 5]
    y = [10, 20, 15, 25, 30]

    # Crear la figura de matplotlib
    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o', linestyle='-', color='b')
    ax.set_title('Gráfica de Prueba')
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')

    # Crear el canvas de Qt para mostrar la gráfica
    canvas = FigureCanvas(fig)
    return canvas


