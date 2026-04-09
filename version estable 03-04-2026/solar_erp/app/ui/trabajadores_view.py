from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QComboBox, QMessageBox, QTableWidgetItem
)
from PySide6.QtGui import QColor, QFont
from app.ui.base_view import BaseCRUDView
from app.core.database import SessionLocal
from app.ui.table_helpers import configurar_tabla
from app.services.services import TrabajadorService


class TrabajadoresView(BaseCRUDView):
    titulo = "Trabajadores"
    icono = "👷"
    placeholder_busqueda = "Buscar por nombre..."

    def get_columns(self):
        return ["ID", "Nombre", "Cargo", "Teléfono", "Estado"]

    def _poblar_tabla(self, trabajadores):
        self.tabla.setRowCount(0)
        for t in trabajadores:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(str(t.id)))
            self.tabla.setItem(row, 1, QTableWidgetItem(t.nombre))
            self.tabla.setItem(row, 2, QTableWidgetItem(t.cargo or ""))
            self.tabla.setItem(row, 3, QTableWidgetItem(t.telefono or ""))
            estado_item = QTableWidgetItem(t.estado or "activo")
            estado_item.setForeground(QColor("#2ECC71") if t.estado == "activo" else QColor("#E74C3C"))
            estado_item.setFont(QFont("", -1, QFont.Bold))
            self.tabla.setItem(row, 4, estado_item)
        self.actualizar_contador(self.tabla.rowCount())

    def cargar_tabla(self):
        db = SessionLocal()
        try:
            self._poblar_tabla(TrabajadorService(db).listar())
        finally:
            db.close()

    def buscar_tabla(self, texto):
        if not texto.strip():
            self.cargar_tabla()
            return
        db = SessionLocal()
        try:
            self._poblar_tabla(TrabajadorService(db).buscar(texto))
        finally:
            db.close()

    def abrir_dialogo_crear(self):
        TrabajadorDialog(self).exec()

    def abrir_dialogo_editar(self, id):
        TrabajadorDialog(self, trabajador_id=id).exec()

    def eliminar_registro(self, id):
        db = SessionLocal()
        try:
            TrabajadorService(db).eliminar(id)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            db.close()


class TrabajadorDialog(QDialog):
    def __init__(self, parent=None, trabajador_id=None):
        super().__init__(parent)
        self.trabajador_id = trabajador_id
        self.setWindowTitle("Nuevo Trabajador" if not trabajador_id else "Editar Trabajador")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._build_ui()
        if trabajador_id:
            self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        titulo = QLabel("👷  " + ("Nuevo Trabajador" if not self.trabajador_id else "Editar Trabajador"))
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A5F;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)
        self.input_nombre = QLineEdit(); self.input_nombre.setPlaceholderText("Nombre completo")
        self.input_cargo = QLineEdit(); self.input_cargo.setPlaceholderText("Ej: Técnico instalador")
        self.input_telefono = QLineEdit(); self.input_telefono.setPlaceholderText("Teléfono")
        self.combo_estado = QComboBox(); self.combo_estado.addItems(["activo", "inactivo"])
        form.addRow("Nombre *", self.input_nombre)
        form.addRow("Cargo", self.input_cargo)
        form.addRow("Teléfono", self.input_telefono)
        form.addRow("Estado", self.combo_estado)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar"); btn_cancelar.setObjectName("btn_secondary"); btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_guardar = QPushButton("💾  Guardar"); btn_guardar.setObjectName("btn_success"); btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)
        layout.addLayout(btns)

    def _cargar_datos(self):
        db = SessionLocal()
        try:
            t = TrabajadorService(db).obtener(self.trabajador_id)
            if not t: return
            self.input_nombre.setText(t.nombre or "")
            self.input_cargo.setText(t.cargo or "")
            self.input_telefono.setText(t.telefono or "")
            idx = self.combo_estado.findText(t.estado or "activo")
            if idx >= 0: self.combo_estado.setCurrentIndex(idx)
        finally:
            db.close()

    def _guardar(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Validación", "El nombre es obligatorio.")
            return
        db = SessionLocal()
        svc = TrabajadorService(db)
        try:
            if self.trabajador_id:
                t = svc.obtener(self.trabajador_id)
                if not t: return
                svc.actualizar(t, nombre,
                    self.input_cargo.text().strip(),
                    self.input_telefono.text().strip(),
                    self.combo_estado.currentText())
            else:
                svc.crear(nombre,
                    self.input_cargo.text().strip(),
                    self.input_telefono.text().strip(),
                    self.combo_estado.currentText())
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            db.close()
