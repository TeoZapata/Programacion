"""
RETIE Manager - Diálogo de Inicio de Sesión
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

from core.database import UsuarioDAO
from ui.styles import LOGIN_STYLESHEET


class LoginDialog(QDialog):
    """Ventana de inicio de sesión."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RETIE Manager — Ingreso al Sistema")
        self.setFixedSize(420, 520)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setStyleSheet(LOGIN_STYLESHEET)
        self.usuario_actual = None
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(0)

        # Card blanca central
        card = QFrame()
        card.setObjectName("login_card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(16)

        # Logo / icono
        lbl_icon = QLabel("⚡")
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 52px; background: transparent; color: #1B4F72;")
        card_layout.addWidget(lbl_icon)

        # Título
        lbl_title = QLabel("RETIE Manager")
        lbl_title.setObjectName("app_title")
        lbl_title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(lbl_title)

        # Subtítulo
        lbl_sub = QLabel("Gestión de Proyectos Eléctricos y Fotovoltaicos")
        lbl_sub.setObjectName("app_subtitle")
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setWordWrap(True)
        card_layout.addWidget(lbl_sub)

        card_layout.addSpacing(12)

        # Error label (oculto inicialmente)
        self.lbl_error = QLabel()
        self.lbl_error.setObjectName("error_label")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setWordWrap(True)
        self.lbl_error.hide()
        card_layout.addWidget(self.lbl_error)

        # Usuario
        lbl_user = QLabel("Usuario")
        lbl_user.setStyleSheet("font-weight: 600; font-size: 13px;")
        card_layout.addWidget(lbl_user)

        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Ingrese su usuario")
        self.input_user.setText("admin")
        card_layout.addWidget(self.input_user)

        # Contraseña
        lbl_pass = QLabel("Contraseña")
        lbl_pass.setStyleSheet("font-weight: 600; font-size: 13px;")
        card_layout.addWidget(lbl_pass)

        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Ingrese su contraseña")
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setText("admin123")
        card_layout.addWidget(self.input_pass)

        card_layout.addSpacing(8)

        # Botón ingresar
        self.btn_login = QPushButton("INGRESAR AL SISTEMA")
        self.btn_login.setObjectName("btn_login")
        card_layout.addWidget(self.btn_login)

        # Versión
        lbl_ver = QLabel("v1.0.0 — Normativa RETIE Colombia")
        lbl_ver.setAlignment(Qt.AlignCenter)
        lbl_ver.setStyleSheet("font-size: 10px; color: #95A5A6; background: transparent;")
        card_layout.addWidget(lbl_ver)

        main_layout.addWidget(card)

        # Conectar eventos
        self.btn_login.clicked.connect(self._intentar_login)
        self.input_pass.returnPressed.connect(self._intentar_login)
        self.input_user.returnPressed.connect(lambda: self.input_pass.setFocus())

    def _intentar_login(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text()

        if not username or not password:
            self._mostrar_error("Por favor ingrese usuario y contraseña.")
            return

        usuario = UsuarioDAO.autenticar(username, password)
        if usuario:
            self.usuario_actual = usuario
            self.accept()
        else:
            self._mostrar_error("Usuario o contraseña incorrectos.")
            self.input_pass.clear()
            self.input_pass.setFocus()

    def _mostrar_error(self, mensaje: str):
        self.lbl_error.setText(mensaje)
        self.lbl_error.show()

    def get_usuario(self):
        return self.usuario_actual
