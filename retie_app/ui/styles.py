"""
RETIE Manager - Estilos y Tema de la Interfaz
Fondo claro / Letra oscura en toda la aplicación.
"""

# Paleta de colores corporativa
COLORS = {
    "primary":        "#1B4F72",   # Azul oscuro principal
    "primary_light":  "#2E86AB",   # Azul medio
    "primary_hover":  "#1A6FA3",   # Azul hover
    "accent":         "#E67E22",   # Naranja solar
    "success":        "#1E8449",   # Verde
    "success_hover":  "#196F3D",
    "danger":         "#C0392B",   # Rojo
    "danger_hover":   "#A93226",
    # ── Fondos ──────────────────────────────
    "bg_main":        "#EEF2F5",   # Gris muy claro (fondo general)
    "bg_card":        "#FFFFFF",   # Blanco (tarjetas)
    "bg_sidebar":     "#1C2833",   # Sidebar oscuro (única zona oscura)
    "bg_input":       "#FFFFFF",   # Fondo de inputs
    "bg_input_ro":    "#F4F6F7",   # Input solo lectura
    "bg_table_alt":   "#F7F9FA",   # Fila alternada en tabla
    "bg_tab":         "#DDE4EA",   # Tab no seleccionada
    # ── Textos ──────────────────────────────
    "text_dark":      "#1A252F",   # Casi negro - texto principal
    "text_medium":    "#2C3E50",   # Gris oscuro
    "text_muted":     "#566573",   # Gris medio
    "text_white":     "#FFFFFF",
    # ── Bordes ──────────────────────────────
    "border":         "#C8D6DF",
    "border_focus":   "#2E86AB",
    # ── Encabezado de tabla ─────────────────
    "table_header_bg":"#2C3E50",
    "table_header_fg":"#FFFFFF",
}

MAIN_STYLESHEET = f"""
/* ════════════════════════════════════════
   GLOBAL - fondo claro, letra oscura
   ════════════════════════════════════════ */
QMainWindow, QDialog, QWidget {{
    background-color: {COLORS['bg_main']};
    color: {COLORS['text_dark']};
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}}

/* ── Labels ──────────────────────────── */
QLabel {{
    color: {COLORS['text_dark']};
    background: transparent;
    font-size: 13px;
}}

QLabel#title_label {{
    font-size: 21px;
    font-weight: bold;
    color: {COLORS['primary']};
    background: transparent;
}}

QLabel#subtitle_label {{
    font-size: 13px;
    color: {COLORS['text_muted']};
    background: transparent;
}}

QLabel#section_header {{
    font-size: 14px;
    font-weight: bold;
    color: {COLORS['primary']};
    background: transparent;
    padding: 6px 0px 5px 0px;
    border-bottom: 2px solid {COLORS['primary_light']};
}}

/* ── Buttons ─────────────────────────── */
QPushButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_white']};
    border: none;
    border-radius: 6px;
    padding: 7px 18px;
    font-size: 13px;
    font-weight: 600;
    min-height: 32px;
}}
QPushButton:hover   {{ background-color: {COLORS['primary_hover']}; color: white; }}
QPushButton:pressed {{ background-color: #154360; color: white; }}
QPushButton:disabled {{
    background-color: #C8D6DF;
    color: {COLORS['text_muted']};
}}

QPushButton#btn_success         {{ background-color: {COLORS['success']}; color: white; }}
QPushButton#btn_success:hover   {{ background-color: {COLORS['success_hover']}; color: white; }}

QPushButton#btn_danger          {{ background-color: {COLORS['danger']}; color: white; }}
QPushButton#btn_danger:hover    {{ background-color: {COLORS['danger_hover']}; color: white; }}

QPushButton#btn_warning         {{ background-color: {COLORS['accent']}; color: white; }}
QPushButton#btn_warning:hover   {{ background-color: #D35400; color: white; }}

QPushButton#btn_flat {{
    background-color: transparent;
    color: {COLORS['primary']};
    border: 1.5px solid {COLORS['primary']};
    font-weight: 600;
}}
QPushButton#btn_flat:hover {{
    background-color: {COLORS['primary']};
    color: white;
}}

/* ── Inputs de texto ─────────────────── */
QLineEdit,
QTextEdit,
QPlainTextEdit {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_dark']};
    border: 1.5px solid {COLORS['border']};
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 13px;
    min-height: 30px;
    selection-background-color: {COLORS['primary_light']};
    selection-color: white;
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {COLORS['border_focus']};
    background-color: #FDFEFF;
    color: {COLORS['text_dark']};
}}
QLineEdit:read-only {{
    background-color: {COLORS['bg_input_ro']};
    color: {COLORS['text_muted']};
}}

/* ── SpinBox ─────────────────────────── */
QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_dark']};
    border: 1.5px solid {COLORS['border']};
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 13px;
    min-height: 30px;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {COLORS['border_focus']};
    color: {COLORS['text_dark']};
}}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background-color: {COLORS['border']};
    border-radius: 3px;
    width: 18px;
    color: {COLORS['text_dark']};
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {COLORS['primary_light']};
}}

/* ── DateEdit ────────────────────────── */
QDateEdit {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_dark']};
    border: 1.5px solid {COLORS['border']};
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 13px;
    min-height: 30px;
}}
QDateEdit:focus {{
    border: 2px solid {COLORS['border_focus']};
    color: {COLORS['text_dark']};
}}
QDateEdit::drop-down {{
    background-color: {COLORS['border']};
    border-radius: 0 4px 4px 0;
    width: 24px;
}}
QCalendarWidget {{
    background-color: white;
    color: {COLORS['text_dark']};
}}
QCalendarWidget QAbstractItemView {{
    background-color: white;
    color: {COLORS['text_dark']};
    selection-background-color: {COLORS['primary_light']};
    selection-color: white;
}}
QCalendarWidget QToolButton {{
    background-color: {COLORS['primary']};
    color: white;
    border-radius: 4px;
    padding: 4px 8px;
}}

/* ── ComboBox ────────────────────────── */
QComboBox {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_dark']};
    border: 1.5px solid {COLORS['border']};
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 13px;
    min-height: 30px;
}}
QComboBox:focus {{
    border: 2px solid {COLORS['border_focus']};
    color: {COLORS['text_dark']};
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 26px;
    background-color: {COLORS['border']};
    border-left: 1px solid {COLORS['border']};
    border-radius: 0px 4px 4px 0px;
}}
/* Lista desplegable */
QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_dark']};
    border: 1.5px solid {COLORS['border_focus']};
    border-radius: 4px;
    selection-background-color: {COLORS['primary_light']};
    selection-color: white;
    outline: none;
    padding: 2px;
}}
QComboBox QAbstractItemView::item {{
    color: {COLORS['text_dark']};
    background-color: {COLORS['bg_card']};
    padding: 6px 10px;
    min-height: 26px;
}}
QComboBox QAbstractItemView::item:hover {{
    background-color: #D6EAF8;
    color: {COLORS['text_dark']};
}}
QComboBox QAbstractItemView::item:selected {{
    background-color: {COLORS['primary_light']};
    color: white;
}}

/* ── Tables ──────────────────────────── */
QTableWidget {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_dark']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    gridline-color: {COLORS['border']};
    selection-background-color: #D6EAF8;
    selection-color: {COLORS['text_dark']};
    font-size: 13px;
    alternate-background-color: {COLORS['bg_table_alt']};
}}
QTableWidget::item {{
    padding: 5px 10px;
    color: {COLORS['text_dark']};
    border: none;
}}
QTableWidget::item:selected {{
    background-color: #D6EAF8;
    color: {COLORS['text_dark']};
}}
QHeaderView {{
    background-color: {COLORS['table_header_bg']};
}}
QHeaderView::section {{
    background-color: {COLORS['table_header_bg']};
    color: {COLORS['table_header_fg']};
    padding: 8px 10px;
    font-weight: bold;
    font-size: 12px;
    border: none;
    border-right: 1px solid #3D5166;
}}

/* ── Sidebar (única zona oscura) ─────── */
QFrame#sidebar {{
    background-color: {COLORS['bg_sidebar']};
    border-right: 2px solid #111B22;
}}
QPushButton#nav_btn {{
    background-color: transparent;
    color: #A9B7C0;
    border: none;
    border-radius: 0px;
    padding: 11px 20px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
    min-height: 42px;
}}
QPushButton#nav_btn:hover {{
    background-color: rgba(255,255,255,0.08);
    color: #FFFFFF;
}}
QPushButton#nav_btn:checked {{
    background-color: {COLORS['primary_light']};
    color: #FFFFFF;
    border-left: 4px solid {COLORS['accent']};
    font-weight: bold;
}}

/* ── GroupBox ────────────────────────── */
QGroupBox {{
    background-color: {COLORS['bg_card']};
    border: 1.5px solid {COLORS['border']};
    border-radius: 7px;
    margin-top: 18px;
    padding: 14px 12px 12px 12px;
    font-weight: bold;
    font-size: 13px;
    color: {COLORS['primary']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    background-color: {COLORS['bg_card']};
    color: {COLORS['primary']};
    padding: 2px 8px;
    left: 14px;
}}
QGroupBox QLabel {{
    color: {COLORS['text_dark']};
    background: transparent;
    font-weight: normal;
    font-size: 13px;
}}
QGroupBox QWidget {{
    color: {COLORS['text_dark']};
}}

/* ── Tabs ────────────────────────────── */
QTabWidget::pane {{
    background-color: {COLORS['bg_card']};
    border: 1.5px solid {COLORS['border']};
    border-radius: 0px 6px 6px 6px;
}}
QTabBar::tab {{
    background-color: {COLORS['bg_tab']};
    color: {COLORS['text_medium']};
    padding: 8px 22px;
    border: 1.5px solid {COLORS['border']};
    border-bottom: none;
    border-radius: 6px 6px 0px 0px;
    margin-right: 2px;
    font-size: 13px;
    font-weight: 500;
}}
QTabBar::tab:selected {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['primary']};
    font-weight: bold;
    border-bottom: 2px solid {COLORS['bg_card']};
}}
QTabBar::tab:hover:!selected {{
    background-color: #C5D8E8;
    color: {COLORS['text_dark']};
}}

/* ── ScrollArea ──────────────────────── */
QScrollArea {{
    background-color: {COLORS['bg_main']};
    border: none;
}}
QScrollArea > QWidget > QWidget {{
    background-color: {COLORS['bg_main']};
}}

/* ── Scrollbars ──────────────────────── */
QScrollBar:vertical {{
    background: {COLORS['bg_main']};
    width: 10px;
    border-radius: 5px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: #B0BEC5;
    border-radius: 5px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {COLORS['primary_light']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {COLORS['bg_main']};
    height: 10px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal {{
    background: #B0BEC5;
    border-radius: 5px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{ background: {COLORS['primary_light']}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Frames / Cards ──────────────────── */
QFrame#card {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
}}

/* ── CheckBox / RadioButton ──────────── */
QCheckBox, QRadioButton {{
    color: {COLORS['text_dark']};
    spacing: 8px;
    font-size: 13px;
    background: transparent;
}}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {COLORS['border']};
    border-radius: 3px;
    background-color: white;
}}
QCheckBox::indicator:checked {{
    background-color: {COLORS['primary_light']};
    border-color: {COLORS['primary_light']};
}}
QRadioButton::indicator {{ border-radius: 8px; }}
QRadioButton::indicator:checked {{
    background-color: {COLORS['primary_light']};
    border-color: {COLORS['primary_light']};
}}

/* ── ProgressBar ─────────────────────── */
QProgressBar {{
    background-color: {COLORS['border']};
    border: none;
    border-radius: 5px;
    height: 14px;
    text-align: center;
    font-size: 11px;
    color: {COLORS['text_dark']};
}}
QProgressBar::chunk {{
    background-color: {COLORS['primary_light']};
    border-radius: 5px;
}}

/* ── MessageBox ──────────────────────── */
QMessageBox {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_dark']};
}}
QMessageBox QLabel {{
    color: {COLORS['text_dark']};
    background: transparent;
}}
QMessageBox QPushButton {{
    min-width: 90px;
    background-color: {COLORS['primary']};
    color: white;
}}

/* ── ToolTip ─────────────────────────── */
QToolTip {{
    background-color: {COLORS['text_dark']};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 5px 8px;
    font-size: 12px;
}}

/* ── Splitter ────────────────────────── */
QSplitter::handle {{ background-color: {COLORS['border']}; }}

/* ── StatusBar ───────────────────────── */
QStatusBar {{
    background-color: {COLORS['primary']};
    color: white;
    font-size: 12px;
    padding: 2px 10px;
}}
QStatusBar QLabel {{ color: white; background: transparent; }}

/* ── ListWidget ──────────────────────── */
QListWidget {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_dark']};
    border: 1.5px solid {COLORS['border']};
    border-radius: 5px;
    outline: none;
}}
QListWidget::item {{
    color: {COLORS['text_dark']};
    padding: 5px 10px;
}}
QListWidget::item:selected {{
    background-color: #D6EAF8;
    color: {COLORS['text_dark']};
}}
QListWidget::item:hover {{
    background-color: #EAF4FB;
    color: {COLORS['text_dark']};
}}

/* ── DialogButtonBox ─────────────────── */
QDialogButtonBox QPushButton {{
    min-width: 90px;
    background-color: {COLORS['primary']};
    color: white;
}}
"""


LOGIN_STYLESHEET = f"""
/* Fondo exterior azul oscuro */
QDialog, QWidget {{
    background-color: {COLORS['primary']};
    font-family: 'Segoe UI', Arial, sans-serif;
}}

/* Tarjeta blanca central */
QFrame#login_card {{
    background-color: {COLORS['bg_card']};
    border-radius: 14px;
}}

/* Labels dentro de la tarjeta */
QFrame#login_card QLabel {{
    color: {COLORS['text_dark']};
    background: transparent;
    font-size: 13px;
}}

QLabel#app_title {{
    color: {COLORS['primary']};
    font-size: 23px;
    font-weight: bold;
    background: transparent;
}}

QLabel#app_subtitle {{
    color: {COLORS['text_muted']};
    font-size: 11px;
    background: transparent;
}}

QLabel#error_label {{
    color: {COLORS['danger']};
    font-size: 12px;
    background-color: #FDEDEC;
    padding: 7px 12px;
    border-radius: 5px;
    border: 1px solid #F1948A;
}}

/* Inputs del login */
QLineEdit {{
    background-color: #F4F6F7;
    color: {COLORS['text_dark']};
    border: 1.5px solid {COLORS['border']};
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 14px;
    min-height: 36px;
}}
QLineEdit:focus {{
    border: 2px solid {COLORS['border_focus']};
    background-color: white;
    color: {COLORS['text_dark']};
}}

/* Botón principal */
QPushButton#btn_login {{
    background-color: {COLORS['primary']};
    color: white;
    border: none;
    border-radius: 7px;
    padding: 12px;
    font-size: 14px;
    font-weight: bold;
    min-height: 44px;
}}
QPushButton#btn_login:hover   {{ background-color: {COLORS['primary_hover']}; color: white; }}
QPushButton#btn_login:pressed {{ background-color: #154360; color: white; }}
"""
