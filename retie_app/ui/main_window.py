"""
RETIE Manager - Ventana Principal
Contiene el sidebar de navegación y el área de contenido principal.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget,
    QSizePolicy, QStatusBar, QSpacerItem
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont

from ui.styles import MAIN_STYLESHEET, COLORS
from ui.panels import (
    DashboardPanel, ClientesPanel, ProyectosPanel,
    ProyectoDetallePanel, PlantillasPanel, ConfiguracionPanel,
    UsuariosPanel
)


class MainWindow(QMainWindow):
    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario
        self.proyecto_actual_id = None

        self.setWindowTitle("⚡ RETIE Manager — Gestión de Proyectos Eléctricos y Fotovoltaicos")
        self.setMinimumSize(1200, 750)
        self.resize(1400, 860)
        self.setStyleSheet(MAIN_STYLESHEET)

        self._setup_ui()
        self._navegar(0)  # Mostrar dashboard al inicio

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── SIDEBAR ──────────────────────────────────────
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo / título
        logo_frame = QFrame()
        logo_frame.setStyleSheet(f"background: {COLORS['primary']}; padding: 0;")
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(16, 20, 16, 20)
        logo_layout.setSpacing(4)

        lbl_logo = QLabel("⚡")
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setStyleSheet("font-size: 36px; color: #F39C12; background: transparent;")
        logo_layout.addWidget(lbl_logo)

        lbl_app = QLabel("RETIE Manager")
        lbl_app.setAlignment(Qt.AlignCenter)
        lbl_app.setStyleSheet("font-size: 14px; font-weight: bold; color: white; background: transparent;")
        logo_layout.addWidget(lbl_app)

        lbl_ver = QLabel("v1.0 Colombia")
        lbl_ver.setAlignment(Qt.AlignCenter)
        lbl_ver.setStyleSheet("font-size: 10px; color: #7F8C8D; background: transparent;")
        logo_layout.addWidget(lbl_ver)
        sidebar_layout.addWidget(logo_frame)

        # Separador
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #2C3E50;")
        sidebar_layout.addWidget(sep)

        # Botones de navegación
        nav_items = [
            ("🏠", "Dashboard", 0),
            ("👥", "Clientes", 1),
            ("📁", "Proyectos", 2),
            ("📋", "Plantillas", 3),
        ]

        self.nav_buttons = []
        for icon, texto, idx in nav_items:
            btn = QPushButton(f"  {icon}  {texto}")
            btn.setObjectName("nav_btn")
            btn.setCheckable(True)
            btn.setFixedHeight(46)
            btn.setFont(QFont("Segoe UI", 12))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=idx: self._navegar(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        # Admin-only
        if self.usuario.get("rol") == "administrador":
            btn_users = QPushButton("  👤  Usuarios")
            btn_users.setObjectName("nav_btn")
            btn_users.setCheckable(True)
            btn_users.setFixedHeight(46)
            btn_users.setFont(QFont("Segoe UI", 12))
            btn_users.setCursor(Qt.PointingHandCursor)
            btn_users.clicked.connect(lambda: self._navegar(5))
            sidebar_layout.addWidget(btn_users)
            self.nav_buttons.append(btn_users)

        sidebar_layout.addStretch()

        # Configuración y usuario
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background: #2C3E50;")
        sidebar_layout.addWidget(sep2)

        btn_config = QPushButton("  ⚙️  Configuración")
        btn_config.setObjectName("nav_btn")
        btn_config.setCheckable(True)
        btn_config.setFixedHeight(46)
        btn_config.setFont(QFont("Segoe UI", 12))
        btn_config.setCursor(Qt.PointingHandCursor)
        btn_config.clicked.connect(lambda: self._navegar(4))
        sidebar_layout.addWidget(btn_config)
        self.nav_buttons.append(btn_config)

        # Info usuario
        user_frame = QFrame()
        user_frame.setStyleSheet(f"background: #0D1B2A; padding: 0;")
        user_layout = QHBoxLayout(user_frame)
        user_layout.setContentsMargins(14, 10, 14, 10)

        lbl_avatar = QLabel("👤")
        lbl_avatar.setStyleSheet("font-size: 20px; color: #BDC3C7; background: transparent;")
        user_layout.addWidget(lbl_avatar)

        user_info = QVBoxLayout()
        user_info.setSpacing(1)
        lbl_nombre = QLabel(self.usuario.get("nombre_completo", "Usuario"))
        lbl_nombre.setStyleSheet("font-size: 11px; color: white; font-weight: bold; background: transparent;")
        lbl_nombre.setWordWrap(True)
        user_info.addWidget(lbl_nombre)

        lbl_rol = QLabel(self.usuario.get("rol", "").capitalize())
        lbl_rol.setStyleSheet(f"font-size: 10px; color: {COLORS['accent']}; background: transparent;")
        user_info.addWidget(lbl_rol)
        user_layout.addLayout(user_info)
        user_layout.addStretch()

        btn_salir = QPushButton("⏏")
        btn_salir.setToolTip("Cerrar sesión")
        btn_salir.setFixedSize(28, 28)
        btn_salir.setStyleSheet("""
            QPushButton { background: #E74C3C; color: white; border-radius: 4px; font-size: 14px; }
            QPushButton:hover { background: #C0392B; }
        """)
        btn_salir.clicked.connect(self._cerrar_sesion)
        user_layout.addWidget(btn_salir)

        sidebar_layout.addWidget(user_frame)
        root_layout.addWidget(self.sidebar)

        # ── ÁREA PRINCIPAL ────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {COLORS['bg_main']};")

        # Paneles
        self.panel_dashboard = DashboardPanel(self.usuario)
        self.panel_clientes = ClientesPanel()
        self.panel_proyectos = ProyectosPanel()
        self.panel_plantillas = PlantillasPanel()
        self.panel_config = ConfiguracionPanel(self.usuario)
        self.panel_proyecto_detalle = None  # Se crea dinámicamente

        self.stack.addWidget(self.panel_dashboard)   # 0
        self.stack.addWidget(self.panel_clientes)    # 1
        self.stack.addWidget(self.panel_proyectos)   # 2
        self.stack.addWidget(self.panel_plantillas)  # 3
        self.stack.addWidget(self.panel_config)      # 4

        if self.usuario.get("rol") == "administrador":
            self.panel_usuarios = UsuariosPanel(self.usuario)
            self.stack.addWidget(self.panel_usuarios)   # 5

        # Conectar señal de abrir proyecto
        self.panel_proyectos.proyecto_abierto.connect(self._abrir_proyecto)

        root_layout.addWidget(self.stack)

        # ── STATUS BAR ────────────────────────────────────
        self.status = QStatusBar()
        self.status.showMessage("✅  Sistema listo — RETIE Manager v1.0  |  Normativa: RETIE Res. 90708/2013")
        self.setStatusBar(self.status)

    def _navegar(self, idx: int):
        """Cambia al panel correspondiente."""
        # Ocultar panel de detalle si está activo
        if self.panel_proyecto_detalle and self.stack.currentWidget() == self.panel_proyecto_detalle:
            pass

        # Actualizar botones
        all_btns = self.nav_buttons
        for i, btn in enumerate(all_btns):
            btn.setChecked(False)

        # Mapear índice al botón correcto
        nav_count = 4  # Dashboard, Clientes, Proyectos, Plantillas
        if idx < nav_count and idx < len(all_btns):
            all_btns[idx].setChecked(True)
        elif idx == 4:  # Config
            all_btns[-1].setChecked(True)
        elif idx == 5 and self.usuario.get("rol") == "administrador":
            # Usuarios
            for btn in all_btns:
                if "Usuarios" in btn.text():
                    btn.setChecked(True)
                    break

        # Cambiar panel
        if idx == 0:
            self.panel_dashboard.refresh()
            self.stack.setCurrentWidget(self.panel_dashboard)
        elif idx == 1:
            self.stack.setCurrentWidget(self.panel_clientes)
        elif idx == 2:
            self.stack.setCurrentWidget(self.panel_proyectos)
        elif idx == 3:
            self.stack.setCurrentWidget(self.panel_plantillas)
        elif idx == 4:
            self.stack.setCurrentWidget(self.panel_config)
        elif idx == 5 and hasattr(self, "panel_usuarios"):
            self.stack.setCurrentWidget(self.panel_usuarios)

    def _abrir_proyecto(self, proyecto_id: int):
        """Abre el panel de detalle de un proyecto."""
        # Eliminar panel anterior si existe
        if self.panel_proyecto_detalle:
            self.stack.removeWidget(self.panel_proyecto_detalle)
            self.panel_proyecto_detalle.deleteLater()

        self.panel_proyecto_detalle = ProyectoDetallePanel(proyecto_id, self.usuario)
        self.panel_proyecto_detalle.volver.connect(lambda: self._navegar(2))
        self.stack.addWidget(self.panel_proyecto_detalle)
        self.stack.setCurrentWidget(self.panel_proyecto_detalle)

        # Desmarcar todos los nav buttons
        for btn in self.nav_buttons:
            btn.setChecked(False)

    def _cerrar_sesion(self):
        from PySide6.QtWidgets import QApplication, QMessageBox
        resp = QMessageBox.question(
            self, "Cerrar sesión",
            "¿Desea cerrar la sesión actual?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            self.close()
            # Reiniciar la aplicación mostrando el login
            QTimer.singleShot(100, lambda: _reiniciar_app())


def _reiniciar_app():
    """Reinicia el flujo de autenticación."""
    from PySide6.QtWidgets import QApplication
    from ui.login import LoginDialog
    dlg = LoginDialog()
    if dlg.exec():
        usuario = dlg.get_usuario()
        if usuario:
            win = MainWindow(usuario)
            win.show()
            QApplication.instance()._main_window = win
