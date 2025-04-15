from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,QComboBox,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QStackedWidget, QFormLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon


class SalidaMaterial(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(0)


        proyect_line = QHBoxLayout()
        proyect_line.setContentsMargins(0, 0, 0, 0)
        proyect_line.setSpacing(0)
        proyect_line.setAlignment(Qt.AlignTop)
 

        self.entry_proyecto = QComboBox()
        self.entry_proyecto.addItems(["Proyecto 1", "Proyecto 2", "Proyecto 3"])


        self.entry_responsable = QLineEdit()
        self.entry_responsable.setPlaceholderText("Ingrese el nombre del responsable")

        self.entry_cliente = QLineEdit()
        self.entry_cliente.setPlaceholderText("Nombre del cliente")
        self.entry_cliente.setReadOnly(True)
    
        self.entry_ubicacion = QLineEdit()
        self.entry_ubicacion.setPlaceholderText("Ubicacion del material")

        self.entry_fecha_Actual = QLineEdit()
        self.entry_fecha_Actual.setReadOnly(True)

        proyect_line.addWidget(self.entry_responsable)
        proyect_line.addWidget(self.entry_proyecto)
        proyect_line.addWidget(self.entry_cliente)
        proyect_line.addWidget(self.entry_ubicacion)
        proyect_line.addWidget(self.entry_fecha_Actual)

        



        # Contenedor de pestañas
        name_title = QLabel("Salida de Material")
        name_title.setAlignment(Qt.AlignCenter)
        name_title.setFont(QFont("Arial", 20, QFont.Bold))

        self.layout.addWidget(name_title)
        self.layout.addLayout(proyect_line)

        pages_container = QStackedWidget()
        self.layout.addWidget(pages_container)