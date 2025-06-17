

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

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
        