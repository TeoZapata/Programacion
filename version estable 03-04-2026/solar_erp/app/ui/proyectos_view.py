from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox,
    QMessageBox, QTableWidgetItem
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont
from app.ui.base_view import BaseCRUDView
from app.core.database import SessionLocal
from app.ui.table_helpers import configurar_tabla
from app.services.services import ProyectoService, ClienteService
from app.core.config import ESTADOS_PROYECTO


class ProyectosView(BaseCRUDView):
    titulo = "Proyectos Solares"
    icono = "☀️"
    placeholder_busqueda = "Buscar por nombre, cliente o estado..."

    def get_columns(self):
        return ["ID", "Proyecto", "Cliente", "Estado", "Paneles", "kWp DC", "kW AC", "Fecha Inicio"]

    def _poblar_tabla(self, proyectos):
        self.tabla.setRowCount(0)
        colores_estado = {
            "En ejecución": "#2ECC71", "Completado": "#3498DB",
            "Cancelado": "#E74C3C", "Prospecto": "#95A5A6",
            "Aprobado": "#F39C12", "En diseño": "#9B59B6",
        }
        for p in proyectos:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(str(p.id)))
            self.tabla.setItem(row, 1, QTableWidgetItem(p.nombre_proyecto))
            self.tabla.setItem(row, 2, QTableWidgetItem(p.cliente.nombre if p.cliente else "—"))
            estado_item = QTableWidgetItem(p.estado)
            estado_item.setForeground(QColor(colores_estado.get(p.estado, "#95A5A6")))
            estado_item.setFont(QFont("", -1, QFont.Bold))
            self.tabla.setItem(row, 3, estado_item)
            self.tabla.setItem(row, 4, QTableWidgetItem(str(p.cantidad_paneles or 0)))
            self.tabla.setItem(row, 5, QTableWidgetItem(f"{p.potencia_total_dc or 0:.2f}"))
            self.tabla.setItem(row, 6, QTableWidgetItem(f"{p.potencia_total_ac or 0:.2f}"))
            self.tabla.setItem(row, 7, QTableWidgetItem(str(p.fecha_inicio) if p.fecha_inicio else "—"))
        self.actualizar_contador(self.tabla.rowCount())

    def cargar_tabla(self):
        db = SessionLocal()
        try:
            self._poblar_tabla(ProyectoService(db).listar())
        finally:
            db.close()

    def buscar_tabla(self, texto):
        if not texto.strip():
            self.cargar_tabla()
            return
        db = SessionLocal()
        try:
            self._poblar_tabla(ProyectoService(db).buscar(texto))
        finally:
            db.close()

    def abrir_dialogo_crear(self):
        ProyectoDialog(self).exec()

    def abrir_dialogo_editar(self, id):
        ProyectoDialog(self, proyecto_id=id).exec()

    def eliminar_registro(self, id):
        db = SessionLocal()
        try:
            ProyectoService(db).eliminar(id)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            db.close()


class ProyectoDialog(QDialog):
    def __init__(self, parent=None, proyecto_id=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_id
        self.setWindowTitle("Nuevo Proyecto" if not proyecto_id else "Editar Proyecto")
        self.setMinimumWidth(560)
        self.setModal(True)
        self._build_ui()
        if proyecto_id:
            self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        titulo = QLabel("☀️  " + ("Nuevo Proyecto Solar" if not self.proyecto_id else "Editar Proyecto Solar"))
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A5F;")
        layout.addWidget(titulo)

        lbl_gen = QLabel("Información General")
        lbl_gen.setStyleSheet("font-weight: bold; color: #7F8C8D; font-size: 12px;")
        layout.addWidget(lbl_gen)

        form = QFormLayout()
        form.setSpacing(10)

        self.input_nombre = QLineEdit(); self.input_nombre.setPlaceholderText("Nombre descriptivo del proyecto")
        form.addRow("Nombre *", self.input_nombre)

        self.combo_cliente = QComboBox()
        self._cargar_clientes()
        form.addRow("Cliente *", self.combo_cliente)

        self.input_direccion = QLineEdit(); self.input_direccion.setPlaceholderText("Dirección de instalación")
        form.addRow("Dirección", self.input_direccion)

        self.date_inicio = QDateEdit(QDate.currentDate())
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Fecha Inicio", self.date_inicio)

        self.combo_estado = QComboBox()
        self.combo_estado.addItems(ESTADOS_PROYECTO)
        form.addRow("Estado", self.combo_estado)
        layout.addLayout(form)

        lbl_tec = QLabel("Datos Técnicos del Sistema")
        lbl_tec.setStyleSheet("font-weight: bold; color: #7F8C8D; font-size: 12px;")
        layout.addWidget(lbl_tec)

        form2 = QFormLayout()
        form2.setSpacing(10)

        row_paneles = QHBoxLayout()
        self.spin_paneles = QSpinBox(); self.spin_paneles.setRange(0, 9999); self.spin_paneles.setSuffix(" paneles")
        self.spin_potencia_panel = QDoubleSpinBox(); self.spin_potencia_panel.setRange(0, 9999); self.spin_potencia_panel.setSuffix(" Wp"); self.spin_potencia_panel.setDecimals(0)
        row_paneles.addWidget(self.spin_paneles)
        row_paneles.addWidget(QLabel("  @  "))
        row_paneles.addWidget(self.spin_potencia_panel)
        form2.addRow("Paneles", row_paneles)

        self.lbl_dc = QLabel("0.00 kWp")
        self.lbl_dc.setStyleSheet("color: #2ECC71; font-weight: bold; font-size: 14px;")
        form2.addRow("Potencia DC (calc.)", self.lbl_dc)
        self.spin_paneles.valueChanged.connect(self._calcular_dc)
        self.spin_potencia_panel.valueChanged.connect(self._calcular_dc)

        self.spin_ac = QDoubleSpinBox(); self.spin_ac.setRange(0, 9999); self.spin_ac.setSuffix(" kW"); self.spin_ac.setDecimals(2)
        form2.addRow("Potencia AC", self.spin_ac)

        self.input_inversor = QLineEdit(); self.input_inversor.setPlaceholderText("Modelo del inversor")
        form2.addRow("Modelo Inversor", self.input_inversor)

        self.spin_inversores = QSpinBox(); self.spin_inversores.setRange(0, 99)
        form2.addRow("Cantidad Inversores", self.spin_inversores)
        layout.addLayout(form2)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar"); btn_cancelar.setObjectName("btn_secondary"); btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_guardar = QPushButton("💾  Guardar"); btn_guardar.setObjectName("btn_success"); btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)
        layout.addLayout(btns)

    def _cargar_clientes(self):
        db = SessionLocal()
        try:
            clientes = ClienteService(db).listar()
        finally:
            db.close()
        self.combo_cliente.clear()
        for c in clientes:
            self.combo_cliente.addItem(c.nombre, c.id)

    def _calcular_dc(self):
        dc = round((self.spin_paneles.value() * self.spin_potencia_panel.value()) / 1000, 2)
        self.lbl_dc.setText(f"{dc:.2f} kWp")

    def _cargar_datos(self):
        db = SessionLocal()
        try:
            p = ProyectoService(db).obtener(self.proyecto_id)
            if not p: return
            self.input_nombre.setText(p.nombre_proyecto or "")
            for i in range(self.combo_cliente.count()):
                if self.combo_cliente.itemData(i) == p.cliente_id:
                    self.combo_cliente.setCurrentIndex(i); break
            self.input_direccion.setText(p.direccion or "")
            if p.fecha_inicio:
                self.date_inicio.setDate(QDate(p.fecha_inicio.year, p.fecha_inicio.month, p.fecha_inicio.day))
            idx = self.combo_estado.findText(p.estado)
            if idx >= 0: self.combo_estado.setCurrentIndex(idx)
            self.spin_paneles.setValue(p.cantidad_paneles or 0)
            self.spin_potencia_panel.setValue(p.potencia_panel or 0)
            self.spin_ac.setValue(p.potencia_total_ac or 0)
            self.input_inversor.setText(p.modelo_inversor or "")
            self.spin_inversores.setValue(p.cantidad_inversores or 0)
            self._calcular_dc()
        finally:
            db.close()

    def _guardar(self):
        nombre = self.input_nombre.text().strip()
        cliente_id = self.combo_cliente.currentData()
        if not nombre or not cliente_id:
            QMessageBox.warning(self, "Validación", "Nombre y Cliente son obligatorios.")
            return
        fecha = self.date_inicio.date().toPython()
        db = SessionLocal()
        svc = ProyectoService(db)
        try:
            if self.proyecto_id:
                p = svc.obtener(self.proyecto_id)
                if not p: return
                svc.actualizar(p, nombre, cliente_id,
                    self.input_direccion.text().strip(), fecha,
                    self.combo_estado.currentText(),
                    self.spin_paneles.value(), self.spin_potencia_panel.value(),
                    self.spin_ac.value(), self.input_inversor.text().strip(),
                    self.spin_inversores.value())
            else:
                svc.crear(nombre, cliente_id,
                    self.input_direccion.text().strip(), fecha,
                    self.combo_estado.currentText(),
                    self.spin_paneles.value(), self.spin_potencia_panel.value(),
                    self.spin_ac.value(), self.input_inversor.text().strip(),
                    self.spin_inversores.value())
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            db.close()
