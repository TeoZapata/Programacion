from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from app.core.database import SessionLocal
from app.services.services import AuthService


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.usuario_logueado = None
        self.setWindowTitle("GeoInventario — Iniciar Sesión")
        self.setFixedSize(420, 540)
        self.setWindowFlags(Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self._build_ui()

    def _build_ui(self):
        # Stylesheet completamente aislado — todos los colores explícitos
        self.setStyleSheet("""
            QDialog {
                background-color: #1E3A5F;
            }

            QFrame#card {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: none;
            }

            /* Todos los QLabel dentro del card */
            QFrame#card QLabel {
                background-color: transparent;
                color: #2C3E50;
                border: none;
            }

            /* Inputs — color de texto EXPLÍCITO */
            QFrame#card QLineEdit {
                background-color: #F0F4F8;
                color: #1A1A2E;
                border: 1.5px solid #CBD5E0;
                border-radius: 8px;
                padding: 11px 14px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                selection-background-color: #2ECC71;
                selection-color: #FFFFFF;
            }

            QFrame#card QLineEdit:focus {
                background-color: #FFFFFF;
                color: #1A1A2E;
                border: 2px solid #2ECC71;
            }

            QFrame#card QLineEdit:hover {
                background-color: #E8EDF2;
                color: #1A1A2E;
                border: 1.5px solid #A0AEC0;
            }

            /* Placeholder text visible */
            QFrame#card QLineEdit[text=""] {
                color: #A0AEC0;
            }

            QPushButton#btn_login {
                background-color: #2ECC71;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 13px;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton#btn_login:hover {
                background-color: #27AE60;
            }
            QPushButton#btn_login:pressed {
                background-color: #1E8449;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 30, 30, 30)
        outer.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 28, 35, 24)
        card_layout.setSpacing(12)

        # ── Icono ────────────────────────────────────────────────────────────
        logo_lbl = QLabel("🌍")
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_lbl.setStyleSheet("font-size: 46px; background: transparent; border: none;")
        card_layout.addWidget(logo_lbl)

        # ── Nombre ───────────────────────────────────────────────────────────
        titulo = QLabel("GeoInventario")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #1E3A5F;"
            "background: transparent; border: none;"
        )
        card_layout.addWidget(titulo)

        subtitulo = QLabel("Sistema de Gestión de Inventario")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet(
            "font-size: 11px; color: #718096; margin-bottom: 4px;"
            "background: transparent; border: none;"
        )
        card_layout.addWidget(subtitulo)

        # ── Campo Usuario ─────────────────────────────────────────────────────
        lbl_user = QLabel("Usuario")
        lbl_user.setStyleSheet(
            "font-weight: bold; font-size: 12px; color: #4A5568;"
            "background: transparent; border: none; margin-top: 4px;"
        )
        card_layout.addWidget(lbl_user)

        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Ingresa tu usuario")
        self.input_user.setMinimumHeight(44)
        # Forzar palette para garantizar color de texto en cualquier plataforma
        self._forzar_colores(self.input_user)
        card_layout.addWidget(self.input_user)

        # ── Campo Contraseña ──────────────────────────────────────────────────
        lbl_pass = QLabel("Contraseña")
        lbl_pass.setStyleSheet(
            "font-weight: bold; font-size: 12px; color: #4A5568;"
            "background: transparent; border: none;"
        )
        card_layout.addWidget(lbl_pass)

        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Ingresa tu contraseña")
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setMinimumHeight(44)
        self._forzar_colores(self.input_pass)
        card_layout.addWidget(self.input_pass)

        # ── Error ─────────────────────────────────────────────────────────────
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(
            "color: #E53E3E; font-size: 12px;"
            "background: transparent; border: none;"
        )
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setMinimumHeight(18)
        card_layout.addWidget(self.lbl_error)

        # ── Botón login ───────────────────────────────────────────────────────
        btn_login = QPushButton("  Iniciar Sesión")
        btn_login.setObjectName("btn_login")
        btn_login.setMinimumHeight(48)
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.clicked.connect(self._login)
        card_layout.addWidget(btn_login)

        # ── Separador ────────────────────────────────────────────────────────
        sep_line = QFrame()
        sep_line.setFrameShape(QFrame.HLine)
        sep_line.setStyleSheet("background-color: #E2E8F0; border: none; max-height: 1px; margin: 4px 0;")
        card_layout.addWidget(sep_line)

        # ── Créditos ──────────────────────────────────────────────────────────
        creditos = QLabel("© Creado por el Área de Ingeniería\nIng. Mateo Salazar Zapata")
        creditos.setAlignment(Qt.AlignCenter)
        creditos.setStyleSheet(
            "color: #A0AEC0; font-size: 10px; line-height: 1.6;"
            "background: transparent; border: none;"
        )
        card_layout.addWidget(creditos)

        outer.addWidget(card)

        # ── Conexiones ────────────────────────────────────────────────────────
        self.input_pass.returnPressed.connect(self._login)
        self.input_user.returnPressed.connect(self.input_pass.setFocus)

    def _forzar_colores(self, widget):
        """
        Fuerza colores de texto via QPalette además del stylesheet,
        para garantizar visibilidad en cualquier tema/plataforma (Win10/11, Linux, macOS).
        """
        from PySide6.QtGui import QPalette, QColor
        palette = widget.palette()
        palette.setColor(QPalette.Text,          QColor("#1A1A2E"))
        palette.setColor(QPalette.PlaceholderText, QColor("#A0AEC0"))
        palette.setColor(QPalette.Base,          QColor("#F0F4F8"))
        palette.setColor(QPalette.Window,        QColor("#F0F4F8"))
        widget.setPalette(palette)

    def _login(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text()

        if not username or not password:
            self.lbl_error.setText("⚠  Ingresa usuario y contraseña")
            return

        self.lbl_error.setText("")
        db = SessionLocal()
        svc = AuthService(db)
        user = svc.login(username, password)
        db.close()

        if user:
            self.usuario_logueado = user
            self.accept()
        else:
            self.lbl_error.setText("✗  Usuario o contraseña incorrectos")
            self.input_pass.clear()
            self.input_pass.setFocus()
