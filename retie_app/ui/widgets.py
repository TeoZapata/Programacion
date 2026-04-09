"""
RETIE Manager - Componentes UI Reutilizables
Widgets personalizados para uso en toda la aplicación.
"""

from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame,
    QPushButton, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFileDialog, QMessageBox, QDialog, QDialogButtonBox,
    QFormLayout, QScrollArea, QGroupBox, QSizePolicy,
    QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QColor

from ui.styles import COLORS


class StatCard(QFrame):
    """Tarjeta de estadística para el dashboard."""
    def __init__(self, title: str, value: str, color: str = None, icon: str = ""):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumSize(160, 100)
        color = color or COLORS["primary"]
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                border: none;
            }}
            QLabel {{
                color: white;
                background: transparent;
                border: none;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        row = QHBoxLayout()
        if icon:
            lbl_icon = QLabel(icon)
            lbl_icon.setStyleSheet("font-size: 28px;")
            row.addWidget(lbl_icon)
        row.addStretch()
        layout.addLayout(row)

        lbl_val = QLabel(str(value))
        lbl_val.setObjectName("stat_value")
        lbl_val.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(lbl_val)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 12px; opacity: 0.85;")
        lbl_title.setWordWrap(True)
        layout.addWidget(lbl_title)

        self._lbl_val = lbl_val

    def set_value(self, v: str):
        self._lbl_val.setText(str(v))


class SectionHeader(QLabel):
    """Encabezado de sección con línea decorativa."""
    def __init__(self, text: str):
        super().__init__(text)
        self.setObjectName("section_header")
        self.setStyleSheet(f"""
            font-size: 15px;
            font-weight: bold;
            color: {COLORS['primary']};
            padding: 6px 0px 6px 0px;
            border-bottom: 2px solid {COLORS['primary_light']};
            margin-bottom: 4px;
        """)


class RetieTable(QTableWidget):
    """Tabla estilizada estándar del sistema."""
    def __init__(self, columns: list, parent=None):
        super().__init__(0, len(columns), parent)
        self.setHorizontalHeaderLabels(columns)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setMinimumSectionSize(80)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setShowGrid(True)
        self.setWordWrap(False)
        for i in range(len(columns) - 1):
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(len(columns)-1, QHeaderView.Stretch)

    def set_rows(self, data: list, fields: list):
        """Llena la tabla con una lista de diccionarios."""
        self.setRowCount(0)
        for row_data in data:
            row = self.rowCount()
            self.insertRow(row)
            for col, field in enumerate(fields):
                val = str(row_data.get(field, "") or "")
                item = QTableWidgetItem(val)
                item.setData(Qt.UserRole, row_data)
                self.setItem(row, col, item)
            self.setRowHeight(row, 36)

    def selected_data(self):
        """Retorna el dict del item seleccionado."""
        items = self.selectedItems()
        if not items:
            return None
        return items[0].data(Qt.UserRole)


class SearchBar(QWidget):
    """Barra de búsqueda con icono."""
    search_changed = Signal(str)

    def __init__(self, placeholder: str = "Buscar...", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        lbl = QLabel("🔍")
        lbl.setStyleSheet("font-size: 16px; color: #7F8C8D;")
        layout.addWidget(lbl)

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setClearButtonEnabled(True)
        self.input.setMinimumWidth(240)
        layout.addWidget(self.input)

        self.input.textChanged.connect(self.search_changed.emit)

    def text(self):
        return self.input.text()

    def clear(self):
        self.input.clear()


class ActionBar(QWidget):
    """Barra de acciones con botones estándar (Nuevo, Editar, Eliminar)."""
    new_clicked = Signal()
    edit_clicked = Signal()
    delete_clicked = Signal()

    def __init__(self, with_search: bool = True, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        if with_search:
            self.search = SearchBar()
            layout.addWidget(self.search)
            self.search_changed = self.search.search_changed
        else:
            self.search = None

        layout.addStretch()

        self.btn_new = QPushButton("➕  Nuevo")
        self.btn_new.setObjectName("btn_success")
        self.btn_new.setFixedHeight(36)
        layout.addWidget(self.btn_new)

        self.btn_edit = QPushButton("✏️  Editar")
        self.btn_edit.setObjectName("btn_flat")
        self.btn_edit.setFixedHeight(36)
        layout.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("🗑️  Eliminar")
        self.btn_delete.setObjectName("btn_danger")
        self.btn_delete.setFixedHeight(36)
        layout.addWidget(self.btn_delete)

        self.btn_new.clicked.connect(self.new_clicked.emit)
        self.btn_edit.clicked.connect(self.edit_clicked.emit)
        self.btn_delete.clicked.connect(self.delete_clicked.emit)


class FormField(QWidget):
    """Campo de formulario con label arriba."""
    def __init__(self, label: str, widget: QWidget = None, required: bool = False):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 6)
        layout.setSpacing(3)

        lbl_text = label + (" *" if required else "")
        lbl = QLabel(lbl_text)
        lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #555;")
        layout.addWidget(lbl)

        if widget:
            self.input = widget
            layout.addWidget(widget)

    def set_widget(self, widget: QWidget):
        self.input = widget
        self.layout().addWidget(widget)


class ImageCard(QFrame):
    """Tarjeta para mostrar imagen del proyecto con opciones de carga."""
    image_selected = Signal(str, str)  # (tipo, ruta)
    image_removed = Signal(int)        # (imagen_id)

    def __init__(self, tipo: str, titulo: str, imagen_id: int = None,
                 ruta: str = None, parent=None):
        super().__init__(parent)
        self.tipo = tipo
        self.imagen_id = imagen_id
        self.ruta = ruta

        self.setObjectName("card")
        self.setFixedSize(180, 180)
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {COLORS['border']};
                border-radius: 8px;
                background: white;
            }}
            QFrame:hover {{
                border-color: {COLORS['primary_light']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Imagen preview
        self.lbl_img = QLabel()
        self.lbl_img.setAlignment(Qt.AlignCenter)
        self.lbl_img.setMinimumHeight(100)
        self.lbl_img.setStyleSheet("border: none;")
        layout.addWidget(self.lbl_img)

        # Título
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {COLORS['text_secondary']}; border: none;")
        lbl_titulo.setWordWrap(True)
        layout.addWidget(lbl_titulo)

        # Botones
        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)

        self.btn_cargar = QPushButton("📁")
        self.btn_cargar.setToolTip("Cargar imagen")
        self.btn_cargar.setFixedSize(28, 28)
        self.btn_cargar.setStyleSheet(f"QPushButton {{ background: {COLORS['primary']}; color: white; border-radius: 4px; font-size: 12px; padding: 0; }} QPushButton:hover {{ background: {COLORS['primary_light']}; }}")
        btn_row.addWidget(self.btn_cargar)

        if imagen_id:
            self.btn_quitar = QPushButton("✕")
            self.btn_quitar.setToolTip("Quitar imagen")
            self.btn_quitar.setFixedSize(28, 28)
            self.btn_quitar.setStyleSheet(f"QPushButton {{ background: {COLORS['danger']}; color: white; border-radius: 4px; font-size: 12px; padding: 0; }} QPushButton:hover {{ background: #C0392B; }}")
            btn_row.addWidget(self.btn_quitar)
            self.btn_quitar.clicked.connect(lambda: self.image_removed.emit(self.imagen_id))

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.btn_cargar.clicked.connect(self._cargar)

        # Cargar imagen si existe
        if ruta and ruta:
            self._mostrar_imagen(ruta)
        else:
            self.lbl_img.setText("📷\nSin imagen")
            self.lbl_img.setStyleSheet(f"font-size: 24px; color: {COLORS['border']}; border: none;")

    def _cargar(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif *.tiff)"
        )
        if ruta:
            self.ruta = ruta
            self._mostrar_imagen(ruta)
            self.image_selected.emit(self.tipo, ruta)

    def _mostrar_imagen(self, ruta: str):
        try:
            pixmap = QPixmap(ruta)
            if not pixmap.isNull():
                scaled = pixmap.scaled(160, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_img.setPixmap(scaled)
        except Exception:
            self.lbl_img.setText("⚠️ Error")


class ConfirmDialog(QMessageBox):
    """Diálogo de confirmación estándar."""
    @staticmethod
    def ask(parent, titulo: str, mensaje: str) -> bool:
        dlg = QMessageBox(parent)
        dlg.setWindowTitle(titulo)
        dlg.setText(mensaje)
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setDefaultButton(QMessageBox.No)
        dlg.button(QMessageBox.Yes).setText("Sí, continuar")
        dlg.button(QMessageBox.No).setText("Cancelar")
        return dlg.exec() == QMessageBox.Yes


class InfoBanner(QFrame):
    """Banner informativo de color."""
    def __init__(self, mensaje: str, tipo: str = "info", parent=None):
        super().__init__(parent)
        colores = {
            "info": ("#D6EAF8", "#2E86AB", "ℹ️"),
            "success": ("#D5F5E3", "#27AE60", "✅"),
            "warning": ("#FEF9E7", "#F39C12", "⚠️"),
            "error": ("#FDEDEC", "#E74C3C", "❌"),
        }
        bg, border, icon = colores.get(tipo, colores["info"])
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 8px;
            }}
            QLabel {{ background: transparent; color: #1A252F; font-size: 13px; }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        lbl = QLabel(f"{icon}  {mensaje}")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)
