from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class reporteSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reporte")
        self.setGeometry(100, 100, 800, 600)

        # Create a layout
        layout = QVBoxLayout()

        # Create a label
        label = QLabel("This is a report section.")
        layout.addWidget(label)

        # Set the layout for the widget
        self.setLayout(layout)
