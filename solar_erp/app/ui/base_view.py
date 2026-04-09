from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from app.ui.table_helpers import configurar_tabla, normalizar


class BaseCRUDView(QWidget):
    """
    Vista base reutilizable para módulos CRUD.
    Subclases deben implementar: get_columns(), cargar_tabla(), abrir_dialogo_crear(), abrir_dialogo_editar()
    """
    titulo = "Módulo"
    icono = "📋"
    placeholder_busqueda = "Buscar..."
    mostrar_btn_nuevo = True

    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario
        self._texto_busqueda_pendiente = ""
        self._timer_busqueda = QTimer(self)
        self._timer_busqueda.setSingleShot(True)
        self._timer_busqueda.setInterval(180)
        self._timer_busqueda.timeout.connect(self._ejecutar_busqueda_pendiente)
        self._build_ui()
        self._cargar()

    def get_columns(self):
        return []

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        titulo_lbl = QLabel(f"{self.icono}  {self.titulo}")
        titulo_lbl.setObjectName("page_title")
        titulo_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #1E3A5F;")
        header.addWidget(titulo_lbl)
        header.addStretch()
        layout.addLayout(header)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.input_busqueda = QLineEdit()
        self.input_busqueda.setObjectName("search_bar")
        self.input_busqueda.setPlaceholderText(f"🔍  {self.placeholder_busqueda}")
        self.input_busqueda.setMinimumWidth(280)
        self.input_busqueda.setMaximumWidth(400)
        self.input_busqueda.textChanged.connect(self._buscar)
        toolbar.addWidget(self.input_busqueda)

        toolbar.addStretch()

        btn_refrescar = QPushButton("↻  Refrescar")
        btn_refrescar.setObjectName("btn_secondary")
        btn_refrescar.clicked.connect(self._cargar)
        toolbar.addWidget(btn_refrescar)

        if self.mostrar_btn_nuevo:
            self.btn_nuevo = QPushButton("\uff0b  Nuevo")
            self.btn_nuevo.setObjectName("btn_success")
            self.btn_nuevo.clicked.connect(self._nuevo)
            toolbar.addWidget(self.btn_nuevo)

        # Hook para botones extra que subclases pueden agregar
        self._agregar_botones_extra(toolbar)

        layout.addLayout(toolbar)

        # Tabla
        cols = self.get_columns()
        self.tabla = QTableWidget(0, len(cols))
        self.tabla.setHorizontalHeaderLabels(cols)
        configurar_tabla(self.tabla, col_stretch=1,
                         cols_fijas=[(0, 55)])  # ID fijo, nombre se estira, resto interactivo
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.doubleClicked.connect(self._editar_seleccionado)
        layout.addWidget(self.tabla)

        # Barra inferior
        bottom = QHBoxLayout()
        self.lbl_total = QLabel("Total: 0 registros")
        self.lbl_total.setStyleSheet("color: #7F8C8D; font-size: 12px;")
        bottom.addWidget(self.lbl_total)
        bottom.addStretch()

        self.btn_editar = QPushButton("✏️  Editar")
        self.btn_editar.setObjectName("btn_primary")
        self.btn_editar.clicked.connect(self._editar_seleccionado)
        bottom.addWidget(self.btn_editar)

        self.btn_eliminar = QPushButton("🗑️  Eliminar")
        self.btn_eliminar.setObjectName("btn_danger")
        self.btn_eliminar.clicked.connect(self._eliminar_seleccionado)
        bottom.addWidget(self.btn_eliminar)

        layout.addLayout(bottom)

    def _cargar(self):
        self.input_busqueda.clear()
        self.cargar_tabla()

    def _buscar(self, texto):
        self._texto_busqueda_pendiente = texto
        self._timer_busqueda.start()

    def _ejecutar_busqueda_pendiente(self):
        # normalizar elimina tildes y diferencias mayúsculas/minúsculas
        self.buscar_tabla(self._texto_busqueda_pendiente)

    def _nuevo(self):
        self.abrir_dialogo_crear()
        self._cargar()

    def _editar_seleccionado(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Selección", "Selecciona un registro para editar.")
            return
        id_item = self.tabla.item(row, 0)
        if id_item:
            self.abrir_dialogo_editar(int(id_item.text()))
            self._cargar()

    def _eliminar_seleccionado(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Selección", "Selecciona un registro para eliminar.")
            return
        id_item = self.tabla.item(row, 0)
        nombre_item = self.tabla.item(row, 1)
        nombre = nombre_item.text() if nombre_item else "este registro"
        resp = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Deseas eliminar '{nombre}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            self.eliminar_registro(int(id_item.text()))
            self._cargar()

    def actualizar_contador(self, n):
        self.lbl_total.setText(f"Total: {n} registros")

    def _agregar_botones_extra(self, toolbar):
        """Subclases pueden sobrescribir para agregar botones al toolbar."""
        pass

    # Métodos a implementar en subclases
    def cargar_tabla(self): pass
    def buscar_tabla(self, texto): pass
    def abrir_dialogo_crear(self): pass
    def abrir_dialogo_editar(self, id): pass
    def eliminar_registro(self, id): pass
