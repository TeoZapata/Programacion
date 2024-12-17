


from PyQt5.QtWidgets import ( QVBoxLayout, QWidget,QTableWidget)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class BDInversoresWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        
        # Tabla de base de datos de inversores
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Nombre', 'Contacto', 'Inversión', 'Fecha', 'Estado'])
        layout.addWidget(self.table)
        
        self.setLayout(layout)