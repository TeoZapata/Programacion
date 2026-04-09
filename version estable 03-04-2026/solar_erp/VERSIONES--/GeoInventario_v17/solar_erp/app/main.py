import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont
from app.core.database import init_db
from app.ui.login import LoginDialog
from app.ui.main_window import MainWindow


def _lanzar_app():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("GeoInventario")
    app.setOrganizationName("Área de Ingeniería")
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    return app


def main():
    app = _lanzar_app()
    try:
        init_db()
    except Exception as e:
        QMessageBox.critical(None, "Error de base de datos",
            f"No se pudo inicializar la base de datos:\n{e}")
        sys.exit(1)

    login = LoginDialog()
    if login.exec():
        usuario = login.usuario_logueado
        ventana = MainWindow(usuario=usuario)
        ventana.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
