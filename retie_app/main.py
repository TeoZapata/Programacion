"""
RETIE Manager — Punto de entrada de la aplicación
Sistema de Gestión de Proyectos Eléctricos y Fotovoltaicos bajo normativa RETIE Colombia
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont, QColor, QPainter, QLinearGradient


def crear_splash() -> QSplashScreen:
    """Crea una pantalla de carga personalizada."""
    # Crear un pixmap para el splash
    pm = QPixmap(560, 320)
    pm.fill(QColor("#1B4F72"))

    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing)

    # Rectángulo de fondo gradiente
    grad = QLinearGradient(0, 0, 560, 320)
    grad.setColorAt(0, QColor("#1B2631"))
    grad.setColorAt(1, QColor("#1B4F72"))
    painter.fillRect(pm.rect(), grad)

    # Icono y título
    painter.setPen(QColor("#F39C12"))
    font = QFont("Segoe UI", 48, QFont.Bold)
    painter.setFont(font)
    painter.drawText(pm.rect().adjusted(0, -60, 0, 0), Qt.AlignCenter, "⚡")

    painter.setPen(QColor("white"))
    font2 = QFont("Segoe UI", 22, QFont.Bold)
    painter.setFont(font2)
    painter.drawText(pm.rect().adjusted(0, 40, 0, 0), Qt.AlignCenter, "RETIE Manager")

    painter.setPen(QColor("#AED6F1"))
    font3 = QFont("Segoe UI", 11)
    painter.setFont(font3)
    painter.drawText(pm.rect().adjusted(0, 90, 0, 0), Qt.AlignCenter,
                     "Gestión de Proyectos Eléctricos y Fotovoltaicos")

    painter.setPen(QColor("#7F8C8D"))
    font4 = QFont("Segoe UI", 9)
    painter.setFont(font4)
    painter.drawText(pm.rect().adjusted(0, 120, 0, 0), Qt.AlignCenter,
                     "Normativa RETIE  •  Colombia  •  v1.0.0")

    painter.setPen(QColor("#2ECC71"))
    painter.drawText(pm.rect().adjusted(0, 150, 0, 0), Qt.AlignCenter, "Iniciando sistema...")

    painter.end()

    splash = QSplashScreen(pm, Qt.WindowStaysOnTopHint)
    return splash


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("RETIE Manager")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("RETIE Colombia")
    app.setStyle("Fusion")

    # Splash screen
    splash = crear_splash()
    splash.show()
    app.processEvents()

    try:
        # Inicializar base de datos
        splash.showMessage("  Iniciando base de datos...", Qt.AlignBottom | Qt.AlignLeft, QColor("#2ECC71"))
        app.processEvents()

        from core.database import initialize_database
        initialize_database()

        splash.showMessage("  Cargando interfaz...", Qt.AlignBottom | Qt.AlignLeft, QColor("#2ECC71"))
        app.processEvents()

        from ui.login import LoginDialog
        from ui.main_window import MainWindow

        # Cerrar splash después de 1.5 segundos y mostrar login
        QTimer.singleShot(1500, splash.close)
        splash.finish(None)

        # Login
        login = LoginDialog()
        if login.exec():
            usuario = login.get_usuario()
            if usuario:
                window = MainWindow(usuario)
                window.show()
                app._main_window = window
                sys.exit(app.exec())
        else:
            sys.exit(0)

    except Exception as e:
        splash.close()
        QMessageBox.critical(
            None, "Error de inicio",
            f"No se pudo iniciar RETIE Manager:\n\n{str(e)}\n\n"
            "Verifique que todas las dependencias estén instaladas:\n"
            "pip install PySide6 python-docx"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
