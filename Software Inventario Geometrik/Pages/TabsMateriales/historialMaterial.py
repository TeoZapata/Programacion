from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon


class HistorialMaterial(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Contenedor de pestañas
        name_title = QLabel("Historial de Material")
        name_title.setAlignment(Qt.AlignCenter)
        name_title.setFont(QFont("Arial", 20, QFont.Bold))

        self.layout.addWidget(name_title)
   