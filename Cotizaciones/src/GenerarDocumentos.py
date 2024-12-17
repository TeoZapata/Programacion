
from PyQt5.QtWidgets import ( QVBoxLayout,
                             QLabel, QPushButton,
                             QWidget, )

class DocumentoGenerarWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        
        # Componentes para generar documentos
        titulo = QLabel("Generación de Documentos")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)
        
        # Botones para diferentes tipos de documentos
        doc_tipos = [
            'Propuesta de Inversión',
            'Contrato',
            'Informe Financiero',
            'Resumen Ejecutivo'
        ]
        
        for doc in doc_tipos:
            boton = QPushButton(doc)
            boton.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    padding: 10px;
                    margin: 5px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            layout.addWidget(boton)
        
        self.setLayout(layout)
