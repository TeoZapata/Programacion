from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

from app.ui.styles import STYLESHEET
from app.ui.dashboard import DashboardView
from app.ui.clientes_view import ClientesView
from app.ui.proveedores_view import ProveedoresView
from app.ui.trabajadores_view import TrabajadoresView
from app.ui.proyectos_view import ProyectosView
from app.ui.inventario_view import InventarioView
from app.ui.movimientos_view import MovimientosView
from app.ui.usuarios_view import UsuariosView
from app.ui.herramientas_view import HerramientasView
from app.ui.pedido_view import PedidoMaterialView
from app.ui.control_proyecto_view import ControlProyectoView
from app.core.config import APP_NAME, APP_VERSION, APP_AUTHOR, ROLES

SIDEBAR_EXPANDED  = 230
SIDEBAR_COLLAPSED = 64


class MainWindow(QMainWindow):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario
        self._sidebar_expanded = True
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1000, 700)
        self.resize(1400, 850)
        self.setStyleSheet(STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── SIDEBAR ──────────────────────────────────────────────────────────
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(SIDEBAR_EXPANDED)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # ── Header / Logo ─────────────────────────────────────────────────────
        logo_frame = QFrame()
        logo_frame.setStyleSheet("background-color: #162D4A;")
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(0)

        # Fila del botón toggle
        toggle_row = QHBoxLayout()
        toggle_row.setContentsMargins(10, 10, 10, 0)
        self.btn_toggle = QPushButton("☰")
        self.btn_toggle.setFixedSize(36, 36)
        self.btn_toggle.setToolTip("Mostrar / ocultar menú  (Ctrl+B)")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.08);
                color: #A0B4C8;
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.20);
                color: white;
            }
            QPushButton:pressed { background: rgba(46,204,113,0.35); }
        """)
        self.btn_toggle.clicked.connect(self._toggle_sidebar)
        toggle_row.addWidget(self.btn_toggle)
        toggle_row.addStretch()
        logo_layout.addLayout(toggle_row)

        # Ícono + nombre
        logo_center = QVBoxLayout()
        logo_center.setContentsMargins(16, 6, 16, 14)
        logo_center.setSpacing(3)

        self.logo_icon = QLabel("🌍")
        self.logo_icon.setStyleSheet("font-size: 30px; background: transparent;")
        self.logo_icon.setAlignment(Qt.AlignCenter)
        logo_center.addWidget(self.logo_icon)

        self.logo_text = QLabel(APP_NAME)
        self.logo_text.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: white; background: transparent;")
        self.logo_text.setAlignment(Qt.AlignCenter)
        logo_center.addWidget(self.logo_text)

        self.version_lbl = QLabel(f"v{APP_VERSION}")
        self.version_lbl.setStyleSheet("font-size: 10px; color: #5D8AA8; background: transparent;")
        self.version_lbl.setAlignment(Qt.AlignCenter)
        logo_center.addWidget(self.version_lbl)

        logo_layout.addLayout(logo_center)
        sidebar_layout.addWidget(logo_frame)

        sep = QFrame()
        sep.setStyleSheet("background-color: #2980B9;")
        sep.setFixedHeight(1)
        sidebar_layout.addWidget(sep)

        # ── Navegación ────────────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.nav_buttons = []
        self._nav_data = []   # lista de (icono, texto)

        nav_items = [
            ("🏠", "Dashboard",        self._make_view(DashboardView,    usuario=self.usuario)),
            ("☀️",  "Proyectos",        self._make_view(ProyectosView,    usuario=self.usuario)),
            ("👥", "Clientes",         self._make_view(ClientesView,     usuario=self.usuario)),
            ("🏭", "Proveedores",      self._make_view(ProveedoresView,  usuario=self.usuario)),
            ("👷", "Trabajadores",     self._make_view(TrabajadoresView, usuario=self.usuario)),
            ("📦", "Inventario",       self._make_view(InventarioView,   usuario=self.usuario)),
            ("🔄", "Movimientos",      self._make_view(MovimientosView,  usuario=self.usuario)),
            ("🔧", "Herramientas",     self._make_view(HerramientasView, usuario=self.usuario)),
            ("🛒", "Pedido Material",  self._make_view(PedidoMaterialView,  usuario=self.usuario)),
            ("📊", "Control Proyecto", self._make_view(ControlProyectoView, usuario=self.usuario)),
        ]

        if self.usuario and self.usuario.rol == "administrador":
            nav_items.append(("🔐", "Usuarios", self._make_view(UsuariosView, usuario=self.usuario)))

        for idx, (icono, texto, vista) in enumerate(nav_items):
            self.stack.addWidget(vista)
            self._nav_data.append((icono, texto))

            btn = QPushButton(f"  {icono}   {texto}")
            btn.setObjectName("nav_btn")
            btn.setCheckable(True)
            btn.setMinimumHeight(48)
            btn.setFont(QFont("Segoe UI", 11))
            btn.setToolTip(texto)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=idx: self._navegar(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        sep2 = QFrame()
        sep2.setStyleSheet("background-color: #2C4F73;")
        sep2.setFixedHeight(1)
        sidebar_layout.addWidget(sep2)

        # ── Pie de sidebar ────────────────────────────────────────────────────
        self.user_frame = QFrame()
        self.user_frame.setStyleSheet("background-color: #162D4A;")
        user_layout = QVBoxLayout(self.user_frame)
        user_layout.setContentsMargins(12, 10, 12, 8)
        user_layout.setSpacing(2)

        self.lbl_user = QLabel()
        self.lbl_rol  = QLabel()
        if self.usuario:
            self.lbl_user.setText(f"👤  {self.usuario.nombre}")
            self.lbl_user.setStyleSheet(
                "color: #ECF0F1; font-size: 12px; font-weight: bold; background: transparent;")
            user_layout.addWidget(self.lbl_user)

            self.lbl_rol.setText(ROLES.get(self.usuario.rol, self.usuario.rol))
            self.lbl_rol.setStyleSheet("color: #5D8AA8; font-size: 10px; background: transparent;")
            user_layout.addWidget(self.lbl_rol)

        self.btn_salir = QPushButton("⏻  Cerrar sesión")
        self.btn_salir.setCursor(Qt.PointingHandCursor)
        self.btn_salir.setStyleSheet("""
            QPushButton { background: transparent; color: #E74C3C; border: none;
                          font-size: 12px; padding: 6px 0px; text-align: left; }
            QPushButton:hover { color: #FF6B6B; }
        """)
        self.btn_salir.clicked.connect(self._cerrar_sesion)
        user_layout.addWidget(self.btn_salir)

        sep3 = QFrame()
        sep3.setStyleSheet("background-color: #2C4F73;")
        sep3.setFixedHeight(1)
        user_layout.addWidget(sep3)

        self.creditos_lbl = QLabel("© Área de Ingeniería\nIng. Mateo Salazar Zapata")
        self.creditos_lbl.setStyleSheet(
            "color: #4A6880; font-size: 9px; padding: 4px 0px; background: transparent;")
        self.creditos_lbl.setAlignment(Qt.AlignCenter)
        user_layout.addWidget(self.creditos_lbl)

        sidebar_layout.addWidget(self.user_frame)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)

        self._navegar(0)

    # ── Toggle con animación ──────────────────────────────────────────────────
    def _toggle_sidebar(self):
        self._sidebar_expanded = not self._sidebar_expanded
        target = SIDEBAR_EXPANDED if self._sidebar_expanded else SIDEBAR_COLLAPSED

        # Dos animaciones paralelas: min y max width
        self._anim_min = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self._anim_min.setDuration(240)
        self._anim_min.setEasingCurve(QEasingCurve.InOutQuad)
        self._anim_min.setStartValue(self.sidebar.width())
        self._anim_min.setEndValue(target)

        self._anim_max = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self._anim_max.setDuration(240)
        self._anim_max.setEasingCurve(QEasingCurve.InOutQuad)
        self._anim_max.setStartValue(self.sidebar.width())
        self._anim_max.setEndValue(target)

        self._anim_min.finished.connect(self._post_toggle)
        self._anim_min.start()
        self._anim_max.start()

    def _post_toggle(self):
        """Actualiza textos e ícono del toggle después de la animación."""
        exp = self._sidebar_expanded

        # Icono del toggle
        self.btn_toggle.setText("☰" if exp else "▶")

        # Botones nav: texto completo ↔ solo emoji
        ESTILO_ICONO = """
            QPushButton {
                background-color: transparent;
                color: #BDC3C7;
                text-align: center;
                padding: 10px 0px;
                border: none;
                border-radius: 0px;
                font-size: 20px;
            }
            QPushButton:hover { background-color: #2980B9; color: white; }
            QPushButton:checked {
                background-color: #2ECC71;
                color: white;
                border-left: 4px solid #27AE60;
            }
        """
        for idx, (icono, texto) in enumerate(self._nav_data):
            btn = self.nav_buttons[idx]
            if exp:
                btn.setText(f"  {icono}   {texto}")
                btn.setFont(QFont("Segoe UI", 11))
                btn.setStyleSheet("")          # hereda estilo global nav_btn
            else:
                btn.setText(icono)
                btn.setFont(QFont("Segoe UI", 18))
                btn.setStyleSheet(ESTILO_ICONO)

        # Logo: ocultar/mostrar nombre y versión
        self.logo_text.setVisible(exp)
        self.version_lbl.setVisible(exp)

        # Pie de usuario
        if self.usuario:
            self.lbl_user.setVisible(exp)
            self.lbl_rol.setVisible(exp)
        self.creditos_lbl.setVisible(exp)
        self.btn_salir.setText("⏻  Cerrar sesión" if exp else "⏻")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _make_view(self, view_class, **kwargs):
        try:
            return view_class(**kwargs)
        except Exception as e:
            lbl = QLabel(f"Error cargando vista: {e}")
            lbl.setAlignment(Qt.AlignCenter)
            return lbl

    def _navegar(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def _cerrar_sesion(self):
        resp = QMessageBox.question(self, "Cerrar Sesión",
            "¿Deseas cerrar sesión?", QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.Yes:
            self.close()
            from app.ui.login import LoginDialog
            login = LoginDialog()
            if login.exec():
                nueva_ventana = MainWindow(usuario=login.usuario_logueado)
                nueva_ventana.show()
                self._nueva_ventana = nueva_ventana
