
import google.generativeai as genai
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFileDialog, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QWidget, QDialog,
                             QTabWidget, QMenuBar, QMenu, QAction, QStackedWidget)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt

class HistorialCotizacionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        
        # Tabla de historial de cotizaciones
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Fecha', 'Cliente', 'Monto', 'Estado'])
        layout.addWidget(self.table)
        
        self.setLayout(layout)