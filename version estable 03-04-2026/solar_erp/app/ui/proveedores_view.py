from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QMessageBox, QTableWidgetItem
)
from app.ui.base_view import BaseCRUDView
from app.core.database import SessionLocal
from app.ui.table_helpers import configurar_tabla
from app.services.services import ProveedorService


class ProveedoresView(BaseCRUDView):
    titulo = "Proveedores"
    icono = "🏭"
    placeholder_busqueda = "Buscar por nombre o NIT..."

    def get_columns(self):
        return ["ID", "Nombre", "NIT", "Teléfono", "Email", "Dirección"]

    def _poblar_tabla(self, proveedores):
        self.tabla.setRowCount(0)
        for p in proveedores:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(str(p.id)))
            self.tabla.setItem(row, 1, QTableWidgetItem(p.nombre))
            self.tabla.setItem(row, 2, QTableWidgetItem(p.nit or ""))
            self.tabla.setItem(row, 3, QTableWidgetItem(p.telefono or ""))
            self.tabla.setItem(row, 4, QTableWidgetItem(p.email or ""))
            self.tabla.setItem(row, 5, QTableWidgetItem(p.direccion or ""))
        self.actualizar_contador(self.tabla.rowCount())

    def cargar_tabla(self):
        db = SessionLocal()
        try:
            self._poblar_tabla(ProveedorService(db).listar())
        finally:
            db.close()

    def buscar_tabla(self, texto):
        if not texto.strip():
            self.cargar_tabla()
            return
        db = SessionLocal()
        try:
            self._poblar_tabla(ProveedorService(db).buscar(texto))
        finally:
            db.close()

    def abrir_dialogo_crear(self):
        ProveedorDialog(self).exec()

    def abrir_dialogo_editar(self, id):
        ProveedorDialog(self, proveedor_id=id).exec()

    def eliminar_registro(self, id):
        db = SessionLocal()
        try:
            ProveedorService(db).eliminar(id)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            db.close()


class ProveedorDialog(QDialog):
    def __init__(self, parent=None, proveedor_id=None):
        super().__init__(parent)
        self.proveedor_id = proveedor_id
        self.setWindowTitle("Nuevo Proveedor" if not proveedor_id else "Editar Proveedor")
        self.setMinimumWidth(460)
        self.setModal(True)
        self._build_ui()
        if proveedor_id:
            self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        titulo = QLabel("🏭  " + ("Nuevo Proveedor" if not self.proveedor_id else "Editar Proveedor"))
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A5F;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)
        self.input_nombre = QLineEdit(); self.input_nombre.setPlaceholderText("Nombre del proveedor")
        self.input_nit = QLineEdit(); self.input_nit.setPlaceholderText("NIT o RUT")
        self.input_telefono = QLineEdit(); self.input_telefono.setPlaceholderText("Teléfono")
        self.input_email = QLineEdit(); self.input_email.setPlaceholderText("correo@proveedor.com")
        self.input_direccion = QLineEdit(); self.input_direccion.setPlaceholderText("Dirección")
        form.addRow("Nombre *", self.input_nombre)
        form.addRow("NIT *", self.input_nit)
        form.addRow("Teléfono", self.input_telefono)
        form.addRow("Email", self.input_email)
        form.addRow("Dirección", self.input_direccion)
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
            p = ProveedorService(db).obtener(self.proveedor_id)
            if not p: return
            self.input_nombre.setText(p.nombre or "")
            self.input_nit.setText(p.nit or "")
            self.input_telefono.setText(p.telefono or "")
            self.input_email.setText(p.email or "")
            self.input_direccion.setText(p.direccion or "")
        finally:
            db.close()

    def _guardar(self):
        nombre = self.input_nombre.text().strip()
        nit = self.input_nit.text().strip()
        if not nombre or not nit:
            QMessageBox.warning(self, "Validación", "Nombre y NIT son obligatorios.")
            return
        db = SessionLocal()
        svc = ProveedorService(db)
        try:
            if self.proveedor_id:
                p = svc.obtener(self.proveedor_id)
                if not p: return
                svc.actualizar(p, nombre, nit,
                    self.input_telefono.text().strip(),
                    self.input_email.text().strip(),
                    self.input_direccion.text().strip())
            else:
                svc.crear(nombre, nit,
                    self.input_telefono.text().strip(),
                    self.input_email.text().strip(),
                    self.input_direccion.text().strip())
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            db.close()
