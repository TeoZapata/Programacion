from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QComboBox, QCheckBox, QMessageBox, QTableWidgetItem
)
from PySide6.QtGui import QColor, QFont
from app.ui.base_view import BaseCRUDView
from app.core.database import SessionLocal
from app.ui.table_helpers import configurar_tabla
from app.services.services import AuthService
from app.core.config import ROLES


class UsuariosView(BaseCRUDView):
    titulo = "Usuarios del Sistema"
    icono = "🔐"
    placeholder_busqueda = "Buscar usuario..."

    def get_columns(self):
        return ["ID", "Nombre", "Usuario", "Rol", "Activo"]

    def _poblar_tabla(self, usuarios):
        self.tabla.setRowCount(0)
        for u in usuarios:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(str(u.id)))
            self.tabla.setItem(row, 1, QTableWidgetItem(u.nombre))
            self.tabla.setItem(row, 2, QTableWidgetItem(u.username))
            self.tabla.setItem(row, 3, QTableWidgetItem(ROLES.get(u.rol, u.rol)))
            activo_item = QTableWidgetItem("✓ Activo" if u.activo else "✗ Inactivo")
            activo_item.setForeground(QColor("#2ECC71") if u.activo else QColor("#E74C3C"))
            activo_item.setFont(QFont("", -1, QFont.Bold))
            self.tabla.setItem(row, 4, activo_item)
        self.actualizar_contador(self.tabla.rowCount())

    def cargar_tabla(self):
        db = SessionLocal()
        try:
            self._poblar_tabla(AuthService(db).get_all())
        finally:
            db.close()

    def buscar_tabla(self, texto):
        self.cargar_tabla()

    def abrir_dialogo_crear(self):
        UsuarioDialog(self).exec()

    def abrir_dialogo_editar(self, id):
        UsuarioDialog(self, usuario_id=id).exec()

    def eliminar_registro(self, id):
        db = SessionLocal()
        try:
            AuthService(db).eliminar(id)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            db.close()


class UsuarioDialog(QDialog):
    def __init__(self, parent=None, usuario_id=None):
        super().__init__(parent)
        self.usuario_id = usuario_id
        self.setWindowTitle("Nuevo Usuario" if not usuario_id else "Editar Usuario")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._build_ui()
        if usuario_id:
            self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        titulo = QLabel("🔐  " + ("Nuevo Usuario" if not self.usuario_id else "Editar Usuario"))
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A5F;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)
        self.input_nombre = QLineEdit(); self.input_nombre.setPlaceholderText("Nombre completo")
        self.input_username = QLineEdit(); self.input_username.setPlaceholderText("nombre_usuario")
        self.input_password = QLineEdit(); self.input_password.setPlaceholderText("Contraseña"); self.input_password.setEchoMode(QLineEdit.Password)
        self.combo_rol = QComboBox()
        for k, v in ROLES.items(): self.combo_rol.addItem(v, k)
        self.check_activo = QCheckBox("Usuario activo"); self.check_activo.setChecked(True)

        form.addRow("Nombre *", self.input_nombre)
        form.addRow("Usuario *", self.input_username)
        form.addRow("Contraseña" + ("" if self.usuario_id else " *"), self.input_password)
        if self.usuario_id:
            hint = QLabel("Dejar vacío para no cambiar la contraseña")
            hint.setStyleSheet("color: #95A5A6; font-size: 11px;")
            form.addRow("", hint)
        form.addRow("Rol", self.combo_rol)
        form.addRow("", self.check_activo)
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
            u = AuthService(db).repo.get_by_id(self.usuario_id)
            if not u: return
            self.input_nombre.setText(u.nombre or "")
            self.input_username.setText(u.username or "")
            for i in range(self.combo_rol.count()):
                if self.combo_rol.itemData(i) == u.rol:
                    self.combo_rol.setCurrentIndex(i); break
            self.check_activo.setChecked(u.activo)
        finally:
            db.close()

    def _guardar(self):
        nombre = self.input_nombre.text().strip()
        username = self.input_username.text().strip()
        password = self.input_password.text()
        if not nombre or not username:
            QMessageBox.warning(self, "Validación", "Nombre y Usuario son obligatorios.")
            return
        if not self.usuario_id and not password:
            QMessageBox.warning(self, "Validación", "La contraseña es obligatoria para nuevos usuarios.")
            return
        db = SessionLocal()
        svc = AuthService(db)
        try:
            if self.usuario_id:
                u = svc.repo.get_by_id(self.usuario_id)
                if not u: return
                svc.actualizar_usuario(u, nombre, self.combo_rol.currentData(),
                    self.check_activo.isChecked(), password if password else None)
            else:
                svc.crear_usuario(nombre, username, password, self.combo_rol.currentData())
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            db.close()
