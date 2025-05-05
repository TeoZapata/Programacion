import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie
import main

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventario Geometrik")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ingrese su nombre")

        self.start_button = QPushButton("Iniciar")
        self.start_button.clicked.connect(self.start_app)

        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setVisible(False)

        self.movie = QMovie("loading.gif")  # Asegúrate de tener un archivo loading.gif en el mismo directorio
        self.loading_label.setMovie(self.movie)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Bienvenido al Inventario Geometrik"))
        layout.addWidget(self.name_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.loading_label)

        self.setLayout(layout)

    def start_app(self):
        name = self.name_input.text()
        if name:
            self.name_input.setEnabled(False)
            self.start_button.setEnabled(False)
            self.loading_label.setVisible(True)
            self.movie.start()

            # Simula la carga de main.py (reemplaza con la lógica real)
            QTimer.singleShot(3000, lambda: self.run_main(name))  # Espera 3 segundos

    def run_main(self, name):
        self.movie.stop()
        self.loading_label.setVisible(False)
        # Aquí deberías llamar a la función principal de main.py y pasar el nombre
        # Por ejemplo, si main.py tiene una función llamada 'run_app':
        
        main.run_app(name)
        self.close()  # Cierra la ventana principal después de iniciar la aplicación principal

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()