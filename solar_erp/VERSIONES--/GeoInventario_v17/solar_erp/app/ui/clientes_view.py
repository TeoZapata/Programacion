from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFormLayout, QMessageBox, QTableWidgetItem
)
from app.ui.base_view import BaseCRUDView
from app.core.database import SessionLocal
from app.ui.table_helpers import configurar_tabla
from app.services.services import ClienteService


class ClientesView(BaseCRUDView):
    titulo = "Clientes"
    icono = "👥"
    placeholder_busqueda = "Buscar por nombre, identificación o email..."

    def get_columns(self):
        return ["ID", "Nombre", "Identificación", "Teléfono", "Email", "Dirección"]

    def _poblar_tabla(self, clientes):
        self.tabla.setRowCount(0)
        for c in clientes:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(str(c.id)))
            self.tabla.setItem(row, 1, QTableWidgetItem(c.nombre))
            self.tabla.setItem(row, 2, QTableWidgetItem(c.identificacion or ""))
            self.tabla.setItem(row, 3, QTableWidgetItem(c.telefono or ""))
            self.tabla.setItem(row, 4, QTableWidgetItem(c.email or ""))
            self.tabla.setItem(row, 5, QTableWidgetItem(c.direccion or ""))
        self.actualizar_contador(self.tabla.rowCount())

    def cargar_tabla(self):
        db = SessionLocal()
        try:
            self._poblar_tabla(ClienteService(db).listar())
        finally:
            db.close()

    def buscar_tabla(self, texto):
        if not texto.strip():
            self.cargar_tabla()
            return
        db = SessionLocal()
        try:
            self._poblar_tabla(ClienteService(db).buscar(texto))
        finally:
            db.close()

    def abrir_dialogo_crear(self):
        ClienteDialog(self).exec()

    def abrir_dialogo_editar(self, id):
        ClienteDialog(self, cliente_id=id).exec()

    def eliminar_registro(self, id):
        db = SessionLocal()
        try:
            ClienteService(db).eliminar(id)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo eliminar: {e}")
        finally:
            db.close()


class ClienteDialog(QDialog):
    def __init__(self, parent=None, cliente_id=None):
        super().__init__(parent)
        self.cliente_id = cliente_id
        self.setWindowTitle("Nuevo Cliente" if not cliente_id else "Editar Cliente")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()
        if cliente_id:
            self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        titulo = QLabel("👥  " + ("Nuevo Cliente" if not self.cliente_id else "Editar Cliente"))
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A5F;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)
        self.input_nombre = QLineEdit(); self.input_nombre.setPlaceholderText("Nombre completo o razón social")
        self.input_identificacion = QLineEdit(); self.input_identificacion.setPlaceholderText("Cédula o NIT")
        self.input_telefono = QLineEdit(); self.input_telefono.setPlaceholderText("Teléfono de contacto")
        self.input_email = QLineEdit(); self.input_email.setPlaceholderText("correo@ejemplo.com")
        self.input_direccion = QLineEdit(); self.input_direccion.setPlaceholderText("Dirección completa")
        self.input_obs = QTextEdit(); self.input_obs.setPlaceholderText("Notas u observaciones..."); self.input_obs.setMaximumHeight(80)
        form.addRow("Nombre *", self.input_nombre)
        form.addRow("Identificación *", self.input_identificacion)
        form.addRow("Teléfono", self.input_telefono)
        form.addRow("Email", self.input_email)
        form.addRow("Dirección", self.input_direccion)
        form.addRow("Observaciones", self.input_obs)
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
            c = ClienteService(db).obtener(self.cliente_id)
            if not c: return
            self.input_nombre.setText(c.nombre or "")
            self.input_identificacion.setText(c.identificacion or "")
            self.input_telefono.setText(c.telefono or "")
            self.input_email.setText(c.email or "")
            self.input_direccion.setText(c.direccion or "")
            self.input_obs.setPlainText(c.observaciones or "")
        finally:
            db.close()

    def _guardar(self):
        nombre = self.input_nombre.text().strip()
        identificacion = self.input_identificacion.text().strip()
        if not nombre or not identificacion:
            QMessageBox.warning(self, "Validación", "Nombre e Identificación son obligatorios.")
            return
        db = SessionLocal()
        svc = ClienteService(db)
        try:
            if self.cliente_id:
                c = svc.obtener(self.cliente_id)
                if not c: return
                svc.actualizar(c, nombre, identificacion,
                    self.input_telefono.text().strip(), self.input_email.text().strip(),
                    self.input_direccion.text().strip(), self.input_obs.toPlainText().strip())
            else:
                svc.crear(nombre, identificacion,
                    self.input_telefono.text().strip(), self.input_email.text().strip(),
                    self.input_direccion.text().strip(), self.input_obs.toPlainText().strip())
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar: {e}")
        finally:
            db.close()
