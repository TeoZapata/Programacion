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

def inventario_grafica():
    # Datos de ejemplo para la gráfica
    datos = get_datos()
    x = datos.inventario_stats['Datos'].keys()
    y = datos.inventario_stats['Datos'].values()

    # Crear la figura de matplotlib
    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o', linestyle='-', color='b')
    ax.set_title('Gráfica de Prueba')
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')

    # Crear el canvas de Qt para mostrar la gráfica
    canvas = FigureCanvas(fig)
    return canvas

def proveedor_grafica():
    # Datos de ejemplo para la gráfica
    datos = get_datos()
    x = datos.proveedores_stats['Datos'].keys()
    y = datos.proveedores_stats['Datos'].values()

    # Crear la figura de matplotlib
    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o', linestyle='-', color='b')
    ax.set_title('Gráfica de Prueba')
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')

    # Crear el canvas de Qt para mostrar la gráfica
    canvas = FigureCanvas(fig)
    return canvas
def herramientas_grafica():
    # Datos de ejemplo para la gráfica
    datos = get_datos()

    x = datos.herramientas_stats['Datos'].keys()
    y = datos.herramientas_stats['Datos'].values()

    # Crear la figura de matplotlib
    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o', linestyle='-', color='b')
    ax.set_title('Gráfica de Prueba')
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')

    # Crear el canvas de Qt para mostrar la gráfica
    canvas = FigureCanvas(fig)
    return canvas
def empleados_grafica():
    # Datos de ejemplo para la gráfica
    datos = get_datos()
    

    x = datos.empleados_stats['Datos'].keys()
    y = datos.empleados_stats['Datos'].values()

    # Crear la figura de matplotlib
    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o', linestyle='-', color='b')
    ax.set_title('Gráfica de Prueba')
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')

    # Crear el canvas de Qt para mostrar la gráfica
    canvas = FigureCanvas(fig)
    return canvas

def proyectos_grafica():
    # Datos de ejemplo para la gráfica
    datos = get_datos()
    

    x = datos.proyectos_stats['Datos'].keys()
    y = datos.proyectos_stats['Datos'].values()

    # Crear la figura de matplotlib
    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o', linestyle='-', color='b')
    ax.set_title('Gráfica de Prueba')
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')

    # Crear el canvas de Qt para mostrar la gráfica
    canvas = FigureCanvas(fig)
    return canvas

