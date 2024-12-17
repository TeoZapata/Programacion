
from PyQt5.QtWidgets import ( QVBoxLayout, QLabel, QPushButton, QFileDialog,  QWidget)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class IniciarCotizacionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        
        # Componentes para iniciar cotización
        titulo = QLabel("Iniciar Nueva Cotización")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)
        
        # Área similar a la selección de imagen del código original
        select_button = QPushButton('Seleccionar Imagen para Cotización')
        select_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a066;
            }
        """)
        layout.addWidget(select_button)
        
        self.setLayout(layout)        
        select_button.clicked.connect(self.select_image)
        self.image_label = QLabel()
        layout.addWidget(self.image_label)

    def select_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)", options=options)
        if file_name:
            pixmap = QPixmap(file_name)
            pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)
