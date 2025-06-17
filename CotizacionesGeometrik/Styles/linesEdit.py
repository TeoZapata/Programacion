

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

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