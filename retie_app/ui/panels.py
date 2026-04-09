"""
RETIE Manager - Paneles Principales
Dashboard, Clientes, Proyectos, Sistema FV, Plantillas, Documentos, Configuración.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox,
    QTextEdit, QDialog, QDialogButtonBox, QFileDialog,
    QMessageBox, QGridLayout, QGroupBox, QScrollArea,
    QTabWidget, QSplitter, QListWidget, QListWidgetItem,
    QProgressBar, QSizePolicy, QCheckBox
)
from PySide6.QtCore import Qt, QDate, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QPixmap, QColor

from core.database import (
    ClienteDAO, ProyectoDAO, SistemaFVDAO, ImagenDAO,
    PlantillaDAO, DocumentoDAO, IngenieroDAO, UsuarioDAO
)
from modules.dimensionamiento import (
    calcular_dimensionamiento, RADIACION_COLOMBIA, generar_resumen_calculo
)
from modules.generador_docs import (
    construir_contexto, procesar_docx, crear_carpeta_proyecto,
    guardar_json_proyecto, copiar_imagen_proyecto, listar_variables_plantilla,
    crear_plantillas_ejemplo, PROYECTOS_DIR
)
from ui.widgets import (
    StatCard, SectionHeader, RetieTable, ActionBar,
    FormField, ImageCard, ConfirmDialog, InfoBanner
)
from ui.styles import COLORS


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

class DashboardPanel(QWidget):
    def __init__(self, usuario: dict, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self._setup_ui()
        self._cargar_datos()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        # Encabezado
        header = QHBoxLayout()
        vbox = QVBoxLayout()
        lbl_bienvenida = QLabel(f"Bienvenido, {self.usuario.get('nombre_completo', '')} 👋")
        lbl_bienvenida.setObjectName("title_label")
        vbox.addWidget(lbl_bienvenida)
        lbl_fecha = QLabel(datetime.now().strftime("📅  %A, %d de %B de %Y"))
        lbl_fecha.setObjectName("subtitle_label")
        vbox.addWidget(lbl_fecha)
        header.addLayout(vbox)
        header.addStretch()
        layout.addLayout(header)

        # Tarjetas de estadísticas
        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)

        self.card_clientes = StatCard("Clientes registrados", "0", COLORS["primary"], "👥")
        self.card_proyectos = StatCard("Proyectos activos", "0", COLORS["primary_light"], "📁")
        self.card_fv = StatCard("Sistemas FV", "0", "#1E8449", "☀️")
        self.card_docs = StatCard("Documentos generados", "0", "#7D3C98", "📄")

        for card in [self.card_clientes, self.card_proyectos, self.card_fv, self.card_docs]:
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            stats_row.addWidget(card)

        layout.addLayout(stats_row)

        # Proyectos recientes
        lbl_rec = SectionHeader("Proyectos Recientes")
        layout.addWidget(lbl_rec)

        self.tabla_recientes = RetieTable(
            ["Proyecto", "Cliente", "Ciudad", "Tipo", "Estado", "Actualizado"]
        )
        self.tabla_recientes.setMaximumHeight(280)
        layout.addWidget(self.tabla_recientes)

        # Información RETIE
        banner = InfoBanner(
            "Sistema certificado bajo normativa RETIE (Res. 90708/2013). "
            "Todos los documentos generados cumplen con los requisitos técnicos del reglamento colombiano.",
            tipo="info"
        )
        layout.addWidget(banner)
        layout.addStretch()

    def _cargar_datos(self):
        clientes = ClienteDAO.listar()
        proyectos = ProyectoDAO.listar()
        fv = [p for p in proyectos if p.get("tipo") == "fotovoltaico"]

        self.card_clientes.set_value(str(len(clientes)))
        self.card_proyectos.set_value(str(len([p for p in proyectos if p.get("estado") == "activo"])))
        self.card_fv.set_value(str(len(fv)))

        self.tabla_recientes.set_rows(
            proyectos[:10],
            ["nombre", "cliente_nombre", "ciudad", "tipo", "estado", "updated_at"]
        )

    def refresh(self):
        self._cargar_datos()


# ─── CLIENTES ─────────────────────────────────────────────────────────────────

class ClientesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._cargar()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        lbl = QLabel("👥 Gestión de Clientes")
        lbl.setObjectName("title_label")
        layout.addWidget(lbl)

        self.action_bar = ActionBar()
        layout.addWidget(self.action_bar)

        self.tabla = RetieTable(["Nombre", "Cédula/NIT", "Ciudad", "Teléfono", "Correo"])
        layout.addWidget(self.tabla)

        self.action_bar.new_clicked.connect(self._nuevo)
        self.action_bar.edit_clicked.connect(self._editar)
        self.action_bar.delete_clicked.connect(self._eliminar)
        self.action_bar.search_changed.connect(self._buscar)
        self.tabla.doubleClicked.connect(self._editar)

    def _cargar(self, filtro: str = ""):
        todos = ClienteDAO.listar()
        if filtro:
            todos = [c for c in todos if filtro.lower() in (c.get("nombre") or "").lower()
                     or filtro.lower() in (c.get("cedula_nit") or "").lower()]
        self.tabla.set_rows(todos, ["nombre", "cedula_nit", "direccion", "telefono", "correo"])

    def _buscar(self, texto: str):
        self._cargar(texto)

    def _nuevo(self):
        dlg = ClienteDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self._cargar()

    def _editar(self):
        data = self.tabla.selected_data()
        if not data:
            QMessageBox.information(self, "Aviso", "Seleccione un cliente para editar.")
            return
        dlg = ClienteDialog(self, data)
        if dlg.exec() == QDialog.Accepted:
            self._cargar()

    def _eliminar(self):
        data = self.tabla.selected_data()
        if not data:
            return
        if ConfirmDialog.ask(self, "Eliminar", f"¿Eliminar al cliente '{data['nombre']}'?"):
            ClienteDAO.eliminar(data["id"])
            self._cargar()


class ClienteDialog(QDialog):
    def __init__(self, parent=None, datos: dict = None):
        super().__init__(parent)
        self.datos = datos or {}
        self.setWindowTitle("Nuevo Cliente" if not datos else "Editar Cliente")
        self.setMinimumWidth(460)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(8)

        def inp(key, placeholder=""):
            w = QLineEdit(str(self.datos.get(key, "") or ""))
            w.setPlaceholderText(placeholder)
            return w

        self.f_nombre = inp("nombre", "Nombre completo o razón social")
        self.f_cedula = inp("cedula_nit", "CC o NIT")
        self.f_dir = inp("direccion", "Dirección")
        self.f_tel = inp("telefono", "Teléfono")
        self.f_correo = inp("correo", "Correo electrónico")

        form.addRow("Nombre *:", self.f_nombre)
        form.addRow("Cédula/NIT:", self.f_cedula)
        form.addRow("Dirección:", self.f_dir)
        form.addRow("Teléfono:", self.f_tel)
        form.addRow("Correo:", self.f_correo)

        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._guardar)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.Save).setText("💾 Guardar")
        btns.button(QDialogButtonBox.Cancel).setText("Cancelar")
        layout.addWidget(btns)

    def _guardar(self):
        if not self.f_nombre.text().strip():
            QMessageBox.warning(self, "Aviso", "El nombre del cliente es obligatorio.")
            return
        datos = {
            "nombre": self.f_nombre.text().strip(),
            "cedula_nit": self.f_cedula.text().strip(),
            "direccion": self.f_dir.text().strip(),
            "telefono": self.f_tel.text().strip(),
            "correo": self.f_correo.text().strip(),
        }
        if self.datos.get("id"):
            datos["id"] = self.datos["id"]
        ClienteDAO.guardar(datos)
        self.accept()


# ─── PROYECTOS ────────────────────────────────────────────────────────────────

class ProyectosPanel(QWidget):
    proyecto_abierto = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._cargar()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        lbl = QLabel("📁 Gestión de Proyectos")
        lbl.setObjectName("title_label")
        layout.addWidget(lbl)

        bar = QHBoxLayout()
        self.action_bar = ActionBar()
        bar.addLayout(self.action_bar.layout())

        btn_abrir = QPushButton("📂  Abrir Proyecto")
        btn_abrir.setObjectName("btn_warning")
        btn_abrir.setFixedHeight(36)
        btn_abrir.clicked.connect(self._abrir_proyecto)
        self.action_bar.layout().addWidget(btn_abrir)

        layout.addWidget(self.action_bar)

        self.tabla = RetieTable(
            ["Proyecto", "Cliente", "Tipo", "Ciudad", "Departamento",
             "Consumo kWh/mes", "Estado", "Fecha inicio"]
        )
        layout.addWidget(self.tabla)

        self.action_bar.new_clicked.connect(self._nuevo)
        self.action_bar.edit_clicked.connect(self._editar)
        self.action_bar.delete_clicked.connect(self._eliminar)
        self.action_bar.search_changed.connect(self._buscar)
        self.tabla.doubleClicked.connect(self._abrir_proyecto)

    def _cargar(self, filtro: str = ""):
        proyectos = ProyectoDAO.listar(filtro)
        self.tabla.set_rows(
            proyectos,
            ["nombre", "cliente_nombre", "tipo", "ciudad", "departamento",
             "consumo_kwh_mes", "estado", "fecha_inicio"]
        )

    def _buscar(self, t):
        self._cargar(t)

    def _nuevo(self):
        dlg = ProyectoDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self._cargar()

    def _editar(self):
        data = self.tabla.selected_data()
        if not data:
            QMessageBox.information(self, "Aviso", "Seleccione un proyecto.")
            return
        proyecto = ProyectoDAO.obtener(data["id"])
        dlg = ProyectoDialog(self, proyecto)
        if dlg.exec() == QDialog.Accepted:
            self._cargar()

    def _abrir_proyecto(self):
        data = self.tabla.selected_data()
        if data:
            self.proyecto_abierto.emit(data["id"])

    def _eliminar(self):
        data = self.tabla.selected_data()
        if not data:
            return
        if ConfirmDialog.ask(self, "Eliminar", f"¿Eliminar el proyecto '{data['nombre']}'?\nEsta acción eliminará todos los datos asociados."):
            ProyectoDAO.eliminar(data["id"])
            self._cargar()

    def refresh(self):
        self._cargar()


class ProyectoDialog(QDialog):
    def __init__(self, parent=None, datos: dict = None):
        super().__init__(parent)
        self.datos = datos or {}
        self.setWindowTitle("Nuevo Proyecto" if not datos else f"Editar: {datos.get('nombre', '')}")
        self.setMinimumWidth(540)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignRight)

        def inp(key, ph=""):
            return QLineEdit(str(self.datos.get(key, "") or ""))

        self.f_nombre = inp("nombre")
        self.f_nombre.setPlaceholderText("Nombre del proyecto")

        # Selector de cliente
        self.cb_cliente = QComboBox()
        clientes = ClienteDAO.listar()
        self.cb_cliente.addItem("-- Seleccione cliente --", None)
        for c in clientes:
            self.cb_cliente.addItem(c["nombre"], c["id"])
        if self.datos.get("cliente_id"):
            idx = self.cb_cliente.findData(self.datos["cliente_id"])
            if idx >= 0:
                self.cb_cliente.setCurrentIndex(idx)

        self.cb_tipo = QComboBox()
        self.cb_tipo.addItems(["electrico", "fotovoltaico"])
        if self.datos.get("tipo"):
            self.cb_tipo.setCurrentText(self.datos["tipo"])

        self.f_dir = inp("direccion")
        self.f_ciudad = inp("ciudad")

        self.cb_depto = QComboBox()
        deptos = sorted(RADIACION_COLOMBIA.keys())
        self.cb_depto.addItems(["-- Departamento --"] + deptos)
        if self.datos.get("departamento"):
            self.cb_depto.setCurrentText(self.datos["departamento"])

        self.f_consumo = QDoubleSpinBox()
        self.f_consumo.setRange(0, 999999)
        self.f_consumo.setDecimals(2)
        self.f_consumo.setSuffix(" kWh/mes")
        self.f_consumo.setValue(float(self.datos.get("consumo_kwh_mes", 0) or 0))

        self.dt_inicio = QDateEdit()
        self.dt_inicio.setCalendarPopup(True)
        self.dt_inicio.setDisplayFormat("dd/MM/yyyy")
        if self.datos.get("fecha_inicio"):
            try:
                d = QDate.fromString(self.datos["fecha_inicio"], "yyyy-MM-dd")
                self.dt_inicio.setDate(d)
            except Exception:
                self.dt_inicio.setDate(QDate.currentDate())
        else:
            self.dt_inicio.setDate(QDate.currentDate())

        self.dt_fin = QDateEdit()
        self.dt_fin.setCalendarPopup(True)
        self.dt_fin.setDisplayFormat("dd/MM/yyyy")
        if self.datos.get("fecha_fin"):
            try:
                d = QDate.fromString(self.datos["fecha_fin"], "yyyy-MM-dd")
                self.dt_fin.setDate(d)
            except Exception:
                self.dt_fin.setDate(QDate.currentDate())
        else:
            self.dt_fin.setDate(QDate.currentDate())

        self.cb_estado = QComboBox()
        self.cb_estado.addItems(["activo", "en_proceso", "finalizado", "pausado"])
        if self.datos.get("estado"):
            self.cb_estado.setCurrentText(self.datos["estado"])

        form.addRow("Nombre *:", self.f_nombre)
        form.addRow("Cliente *:", self.cb_cliente)
        form.addRow("Tipo:", self.cb_tipo)
        form.addRow("Dirección:", self.f_dir)
        form.addRow("Ciudad:", self.f_ciudad)
        form.addRow("Departamento:", self.cb_depto)
        form.addRow("Consumo:", self.f_consumo)
        form.addRow("Fecha inicio:", self.dt_inicio)
        form.addRow("Fecha fin:", self.dt_fin)
        form.addRow("Estado:", self.cb_estado)

        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._guardar)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.Save).setText("💾 Guardar")
        btns.button(QDialogButtonBox.Cancel).setText("Cancelar")
        layout.addWidget(btns)

    def _guardar(self):
        if not self.f_nombre.text().strip():
            QMessageBox.warning(self, "Aviso", "El nombre del proyecto es obligatorio.")
            return
        if self.cb_cliente.currentData() is None:
            QMessageBox.warning(self, "Aviso", "Seleccione un cliente.")
            return
        datos = {
            "nombre": self.f_nombre.text().strip(),
            "cliente_id": self.cb_cliente.currentData(),
            "tipo": self.cb_tipo.currentText(),
            "direccion": self.f_dir.text().strip(),
            "ciudad": self.f_ciudad.text().strip(),
            "departamento": self.cb_depto.currentText() if self.cb_depto.currentIndex() > 0 else "",
            "consumo_kwh_mes": self.f_consumo.value(),
            "fecha_inicio": self.dt_inicio.date().toString("yyyy-MM-dd"),
            "fecha_fin": self.dt_fin.date().toString("yyyy-MM-dd"),
            "estado": self.cb_estado.currentText(),
        }
        if self.datos.get("id"):
            datos["id"] = self.datos["id"]
        ProyectoDAO.guardar(datos)
        self.accept()


# ─── DETALLE DE PROYECTO ───────────────────────────────────────────────────────

class ProyectoDetallePanel(QWidget):
    """Panel completo de edición de un proyecto con todas sus pestañas."""
    volver = Signal()

    def __init__(self, proyecto_id: int, usuario: dict, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_id
        self.usuario = usuario
        self._setup_ui()
        self._cargar()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # Barra superior
        top = QHBoxLayout()
        btn_volver = QPushButton("← Volver a proyectos")
        btn_volver.setObjectName("btn_flat")
        btn_volver.setFixedHeight(34)
        btn_volver.clicked.connect(self.volver.emit)
        top.addWidget(btn_volver)
        top.addStretch()

        self.lbl_proyecto = QLabel("Proyecto")
        self.lbl_proyecto.setObjectName("title_label")
        top.addWidget(self.lbl_proyecto)
        top.addStretch()

        btn_carpeta = QPushButton("📂 Abrir Carpeta")
        btn_carpeta.setFixedHeight(34)
        btn_carpeta.clicked.connect(self._abrir_carpeta)
        top.addWidget(btn_carpeta)

        layout.addLayout(top)

        # Tabs
        self.tabs = QTabWidget()
        self.tab_fv = SistemaFVTab(self.proyecto_id)
        self.tab_imagenes = ImagenesTab(self.proyecto_id)
        self.tab_docs = DocumentosTab(self.proyecto_id, self.usuario)
        self.tab_calculo = CalculoSolarTab(self.proyecto_id)

        self.tabs.addTab(self.tab_fv, "☀️ Sistema FV")
        self.tabs.addTab(self.tab_imagenes, "🖼️ Imágenes")
        self.tabs.addTab(self.tab_docs, "📄 Documentos")
        self.tabs.addTab(self.tab_calculo, "🔢 Dimensionamiento")
        layout.addWidget(self.tabs)

    def _cargar(self):
        proyecto = ProyectoDAO.obtener(self.proyecto_id)
        self.lbl_proyecto.setText(f"📁 {proyecto.get('nombre', '')}")
        self.tab_fv.cargar()
        self.tab_imagenes.cargar()
        self.tab_docs.cargar()

    def _abrir_carpeta(self):
        proyecto = ProyectoDAO.obtener(self.proyecto_id)
        carpeta = criar_carpeta_proyecto_si_existe(proyecto.get("nombre", ""))
        if os.path.exists(carpeta):
            import subprocess, platform
            if platform.system() == "Windows":
                os.startfile(carpeta)
            elif platform.system() == "Darwin":
                subprocess.call(["open", carpeta])
            else:
                subprocess.call(["xdg-open", carpeta])
        else:
            QMessageBox.information(self, "Aviso", f"La carpeta no existe aún:\n{carpeta}")


def criar_carpeta_projeto_si_existe(nombre: str) -> str:
    from modules.generador_docs import _limpiar_nombre_carpeta, PROYECTOS_DIR
    nombre_limpio = _limpiar_nombre_carpeta(nombre)
    return os.path.join(PROYECTOS_DIR, nombre_limpio)


# ─── TAB SISTEMA FV ────────────────────────────────────────────────────────────

class SistemaFVTab(QScrollArea):
    def __init__(self, proyecto_id: int, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_id
        self.setWidgetResizable(True)
        content = QWidget()
        self.setWidget(content)
        self._layout = QVBoxLayout(content)
        self._layout.setContentsMargins(20, 16, 20, 16)
        self._layout.setSpacing(16)
        self._build_form()

    def _build_form(self):
        # ── Paneles
        grp_paneles = QGroupBox("🔆 Módulos Fotovoltaicos")
        fl = QFormLayout(grp_paneles)
        fl.setSpacing(8)

        self.f_cant_pan = QSpinBox(); self.f_cant_pan.setRange(0, 9999)
        self.f_pot_pan = QDoubleSpinBox(); self.f_pot_pan.setRange(0, 9999); self.f_pot_pan.setSuffix(" Wp")
        self.f_marca_pan = QLineEdit()
        self.f_ref_pan = QLineEdit()

        fl.addRow("Cantidad de paneles:", self.f_cant_pan)
        fl.addRow("Potencia por panel:", self.f_pot_pan)
        fl.addRow("Marca:", self.f_marca_pan)
        fl.addRow("Referencia:", self.f_ref_pan)
        self._layout.addWidget(grp_paneles)

        # ── Inversores
        grp_inv = QGroupBox("🔌 Inversores")
        fi = QFormLayout(grp_inv)
        fi.setSpacing(8)

        self.f_cant_inv = QSpinBox(); self.f_cant_inv.setRange(0, 999)
        self.f_marca_inv = QLineEdit()
        self.f_ref_inv = QLineEdit()
        self.f_pot_inv = QDoubleSpinBox(); self.f_pot_inv.setRange(0, 9999); self.f_pot_inv.setSuffix(" kW")

        fi.addRow("Cantidad de inversores:", self.f_cant_inv)
        fi.addRow("Marca:", self.f_marca_inv)
        fi.addRow("Referencia:", self.f_ref_inv)
        fi.addRow("Potencia por inversor:", self.f_pot_inv)
        self._layout.addWidget(grp_inv)

        # ── Datos eléctricos
        grp_elec = QGroupBox("⚡ Datos Eléctricos")
        fe = QFormLayout(grp_elec)
        fe.setSpacing(8)

        self.f_calibre = QLineEdit()
        self.f_calibre.setPlaceholderText("Ej: 10 AWG")
        self.f_tipo_cond = QLineEdit()
        self.f_tipo_cond.setPlaceholderText("Ej: THW-LS 90°C")
        self.f_breaker = QLineEdit()
        self.f_breaker.setPlaceholderText("Ej: 40A / 2P")

        fe.addRow("Calibre conductor:", self.f_calibre)
        fe.addRow("Tipo de conductor:", self.f_tipo_cond)
        fe.addRow("Protección (breaker):", self.f_breaker)
        self._layout.addWidget(grp_elec)

        # ── Calculados
        grp_calc = QGroupBox("📊 Resultados Calculados")
        fc = QFormLayout(grp_calc)
        fc.setSpacing(8)

        self.f_kwp_total = QDoubleSpinBox(); self.f_kwp_total.setRange(0, 99999); self.f_kwp_total.setSuffix(" kWp")
        self.f_gen_est = QDoubleSpinBox(); self.f_gen_est.setRange(0, 999999); self.f_gen_est.setSuffix(" kWh/mes")
        self.f_hsp = QDoubleSpinBox(); self.f_hsp.setRange(0, 10); self.f_hsp.setSuffix(" HSP"); self.f_hsp.setValue(4.5)
        self.f_efic = QDoubleSpinBox(); self.f_efic.setRange(0, 1); self.f_efic.setDecimals(2); self.f_efic.setValue(0.80)

        fc.addRow("Potencia total instalada:", self.f_kwp_total)
        fc.addRow("Generación estimada:", self.f_gen_est)
        fc.addRow("Irradiación zona (HSP):", self.f_hsp)
        fc.addRow("Eficiencia del sistema:", self.f_efic)
        self._layout.addWidget(grp_calc)

        # Botón guardar
        btn = QPushButton("💾  Guardar Sistema FV")
        btn.setObjectName("btn_success")
        btn.setFixedHeight(40)
        btn.clicked.connect(self._guardar)
        self._layout.addWidget(btn)
        self._layout.addStretch()

    def cargar(self):
        datos = SistemaFVDAO.obtener(self.proyecto_id)
        if not datos:
            return
        self.f_cant_pan.setValue(int(datos.get("cantidad_paneles", 0) or 0))
        self.f_pot_pan.setValue(float(datos.get("potencia_panel", 0) or 0))
        self.f_marca_pan.setText(datos.get("marca_panel", "") or "")
        self.f_ref_pan.setText(datos.get("referencia_panel", "") or "")
        self.f_cant_inv.setValue(int(datos.get("cantidad_inversores", 0) or 0))
        self.f_marca_inv.setText(datos.get("marca_inversor", "") or "")
        self.f_ref_inv.setText(datos.get("referencia_inversor", "") or "")
        self.f_pot_inv.setValue(float(datos.get("potencia_inversor", 0) or 0))
        self.f_calibre.setText(datos.get("calibre_conductor", "") or "")
        self.f_tipo_cond.setText(datos.get("tipo_conductor", "") or "")
        self.f_breaker.setText(datos.get("proteccion_breaker", "") or "")
        self.f_kwp_total.setValue(float(datos.get("potencia_total_kwp", 0) or 0))
        self.f_gen_est.setValue(float(datos.get("generacion_estimada_kwh", 0) or 0))
        self.f_hsp.setValue(float(datos.get("irradiacion_zona", 4.5) or 4.5))
        self.f_efic.setValue(float(datos.get("eficiencia_sistema", 0.80) or 0.80))

    def _guardar(self):
        datos = {
            "cantidad_paneles": self.f_cant_pan.value(),
            "potencia_panel": self.f_pot_pan.value(),
            "marca_panel": self.f_marca_pan.text(),
            "referencia_panel": self.f_ref_pan.text(),
            "cantidad_inversores": self.f_cant_inv.value(),
            "marca_inversor": self.f_marca_inv.text(),
            "referencia_inversor": self.f_ref_inv.text(),
            "potencia_inversor": self.f_pot_inv.value(),
            "calibre_conductor": self.f_calibre.text(),
            "tipo_conductor": self.f_tipo_cond.text(),
            "proteccion_breaker": self.f_breaker.text(),
            "potencia_total_kwp": self.f_kwp_total.value(),
            "generacion_estimada_kwh": self.f_gen_est.value(),
            "irradiacion_zona": self.f_hsp.value(),
            "eficiencia_sistema": self.f_efic.value(),
        }
        SistemaFVDAO.guardar(self.proyecto_id, datos)
        QMessageBox.information(self, "✅ Guardado", "Datos del sistema FV guardados correctamente.")


# ─── TAB IMÁGENES ──────────────────────────────────────────────────────────────

class ImagenesTab(QScrollArea):
    TIPOS = [
        ("ubicacion", "Ubicación del Proyecto"),
        ("cuadro_cargas", "Cuadro de Cargas"),
        ("caida_tension", "Caída de Tensión"),
        ("regulacion_perdidas", "Regulación y Pérdidas"),
        ("diagrama_unifilar", "Diagrama Unifilar"),
        ("otro_1", "Imagen Extra 1"),
        ("otro_2", "Imagen Extra 2"),
    ]

    def __init__(self, proyecto_id: int, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_id
        self.setWidgetResizable(True)
        content = QWidget()
        self.setWidget(content)
        self._layout = QVBoxLayout(content)
        self._layout.setContentsMargins(20, 16, 20, 16)
        self._layout.setSpacing(14)
        self._cards = {}
        self._build()

    def _build(self):
        lbl = SectionHeader("Imágenes del Proyecto")
        self._layout.addWidget(lbl)
        banner = InfoBanner("Cargue las imágenes técnicas del proyecto. Se guardarán en la carpeta del proyecto.", "info")
        self._layout.addWidget(banner)

        grid = QGridLayout()
        grid.setSpacing(14)
        for i, (tipo, titulo) in enumerate(self.TIPOS):
            card = ImageCard(tipo, titulo)
            card.image_selected.connect(self._imagen_seleccionada)
            self._cards[tipo] = card
            grid.addWidget(card, i // 4, i % 4)
        self._layout.addLayout(grid)
        self._layout.addStretch()

    def cargar(self):
        imagenes = ImagenDAO.listar(self.proyecto_id)
        for img in imagenes:
            tipo = img.get("tipo", "")
            if tipo in self._cards and img.get("ruta"):
                card = self._cards[tipo]
                card.imagen_id = img["id"]
                card.ruta = img["ruta"]
                card._mostrar_imagen(img["ruta"])

    def _imagen_seleccionada(self, tipo: str, ruta: str):
        proyecto = ProyectoDAO.obtener(self.proyecto_id)
        try:
            carpeta = crear_carpeta_proyecto(proyecto["nombre"])
            nueva_ruta = copiar_imagen_proyecto(ruta, carpeta, tipo)
            datos = {
                "proyecto_id": self.proyecto_id,
                "tipo": tipo,
                "nombre_archivo": os.path.basename(nueva_ruta),
                "ruta": nueva_ruta,
                "descripcion": tipo,
                "created_at": datetime.now().isoformat(),
            }
            ImagenDAO.guardar(datos)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar la imagen:\n{str(e)}")


# ─── TAB DOCUMENTOS ────────────────────────────────────────────────────────────

class DocumentosTab(QWidget):
    def __init__(self, proyecto_id: int, usuario: dict, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_id
        self.usuario = usuario
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        lbl = SectionHeader("📄 Generador de Documentos RETIE")
        layout.addWidget(lbl)

        # Selección de plantilla
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Plantilla:"))
        self.cb_plantilla = QComboBox()
        self.cb_plantilla.setMinimumWidth(300)
        row1.addWidget(self.cb_plantilla)
        btn_refrescar = QPushButton("🔄")
        btn_refrescar.setFixedSize(34, 34)
        btn_refrescar.clicked.connect(self._cargar_plantillas)
        row1.addWidget(btn_refrescar)
        row1.addStretch()
        layout.addLayout(row1)

        # Nombre del documento
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Nombre del documento:"))
        self.f_nombre_doc = QLineEdit()
        self.f_nombre_doc.setPlaceholderText("Nombre del archivo a generar (sin extensión)")
        row2.addWidget(self.f_nombre_doc)
        layout.addLayout(row2)

        # Botón generar
        btn_gen = QPushButton("⚡  Generar Documento RETIE")
        btn_gen.setObjectName("btn_success")
        btn_gen.setMinimumHeight(44)
        btn_gen.clicked.connect(self._generar)
        layout.addWidget(btn_gen)

        # Ver variables de la plantilla
        btn_vars = QPushButton("🔍 Ver variables de la plantilla seleccionada")
        btn_vars.setObjectName("btn_flat")
        btn_vars.clicked.connect(self._ver_variables)
        layout.addWidget(btn_vars)

        layout.addWidget(SectionHeader("Documentos Generados"))

        self.tabla = RetieTable(["Documento", "Plantilla", "Fecha generación"])
        layout.addWidget(self.tabla)

        row_doc = QHBoxLayout()
        btn_abrir = QPushButton("📂 Abrir documento")
        btn_abrir.clicked.connect(self._abrir_doc)
        btn_eliminar = QPushButton("🗑️ Eliminar registro")
        btn_eliminar.setObjectName("btn_danger")
        btn_eliminar.clicked.connect(self._eliminar_doc)
        row_doc.addWidget(btn_abrir)
        row_doc.addWidget(btn_eliminar)
        row_doc.addStretch()
        layout.addLayout(row_doc)

        self._cargar_plantillas()

    def _cargar_plantillas(self):
        self.cb_plantilla.clear()
        self.cb_plantilla.addItem("-- Seleccione plantilla --", None)
        for p in PlantillaDAO.listar():
            self.cb_plantilla.addItem(f"{p['nombre']} ({p.get('tipo', '')})", p)

    def cargar(self):
        docs = DocumentoDAO.listar(self.proyecto_id)
        self.tabla.set_rows(docs, ["nombre_documento", "plantilla_nombre", "fecha_generacion"])

    def _ver_variables(self):
        datos_plantilla = self.cb_plantilla.currentData()
        if not datos_plantilla:
            QMessageBox.information(self, "Aviso", "Seleccione una plantilla primero.")
            return
        ruta = datos_plantilla.get("ruta_archivo", "")
        if not os.path.exists(ruta):
            QMessageBox.warning(self, "Error", "El archivo de plantilla no existe.")
            return
        vars_lista = listar_variables_plantilla(ruta)
        if not vars_lista:
            QMessageBox.information(self, "Variables", "No se encontraron variables {{}} en la plantilla.")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Variables en la plantilla")
        dlg.setMinimumSize(400, 300)
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel(f"Variables encontradas ({len(vars_lista)}):"))
        lista = QListWidget()
        for v in vars_lista:
            lista.addItem(f"  {{{{{v}}}}}")
        lay.addWidget(lista)
        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(dlg.accept)
        lay.addWidget(btns)
        dlg.exec()

    def _generar(self):
        datos_plantilla = self.cb_plantilla.currentData()
        if not datos_plantilla:
            QMessageBox.warning(self, "Aviso", "Seleccione una plantilla.")
            return

        nombre_doc = self.f_nombre_doc.text().strip()
        if not nombre_doc:
            nombre_doc = datos_plantilla["nombre"].replace(".docx", "")

        ruta_plantilla = datos_plantilla.get("ruta_archivo", "")
        if not os.path.exists(ruta_plantilla):
            QMessageBox.critical(self, "Error", f"La plantilla no existe:\n{ruta_plantilla}")
            return

        try:
            proyecto = ProyectoDAO.obtener(self.proyecto_id)
            cliente = ClienteDAO.obtener(proyecto.get("cliente_id", 0))
            ingeniero = IngenieroDAO.obtener(self.usuario["id"])
            sistema_fv = SistemaFVDAO.obtener(self.proyecto_id)

            ctx = construir_contexto(proyecto, cliente, ingeniero, sistema_fv)
            carpeta = crear_carpeta_proyecto(proyecto["nombre"])
            nombre_archivo = f"{nombre_doc}.docx"
            ruta_salida = os.path.join(carpeta, "documentos", nombre_archivo)

            procesar_docx(ruta_plantilla, ctx, ruta_salida)
            guardar_json_proyecto(carpeta, proyecto, cliente, ingeniero, sistema_fv)

            DocumentoDAO.registrar({
                "proyecto_id": self.proyecto_id,
                "plantilla_id": datos_plantilla["id"],
                "nombre_documento": nombre_archivo,
                "ruta_archivo": ruta_salida,
                "fecha_generacion": datetime.now().isoformat(),
            })

            self.cargar()
            QMessageBox.information(
                self, "✅ Documento Generado",
                f"Documento generado exitosamente:\n{ruta_salida}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error al generar", str(e))

    def _abrir_doc(self):
        data = self.tabla.selected_data()
        if not data:
            return
        ruta = data.get("ruta_archivo", "")
        if os.path.exists(ruta):
            import subprocess, platform
            if platform.system() == "Windows":
                os.startfile(ruta)
            elif platform.system() == "Darwin":
                subprocess.call(["open", ruta])
            else:
                subprocess.call(["xdg-open", ruta])
        else:
            QMessageBox.warning(self, "Error", f"El archivo no existe:\n{ruta}")

    def _eliminar_doc(self):
        pass  # Simplificado


# ─── TAB DIMENSIONAMIENTO SOLAR ────────────────────────────────────────────────

class CalculoSolarTab(QWidget):
    def __init__(self, proyecto_id: int, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_id
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(20)

        # Panel izquierdo - Entradas
        izq = QGroupBox("📥 Parámetros de Entrada")
        izq.setMaximumWidth(340)
        fl = QFormLayout(izq)
        fl.setSpacing(10)

        # Cargar consumo del proyecto
        proyecto = ProyectoDAO.obtener(self.proyecto_id)
        consumo = float(proyecto.get("consumo_kwh_mes", 0) or 0)

        self.f_consumo = QDoubleSpinBox()
        self.f_consumo.setRange(1, 999999)
        self.f_consumo.setSuffix(" kWh/mes")
        self.f_consumo.setValue(consumo if consumo > 0 else 300)

        self.f_pot_panel = QDoubleSpinBox()
        self.f_pot_panel.setRange(10, 9999)
        self.f_pot_panel.setSuffix(" Wp")
        self.f_pot_panel.setValue(550)

        self.cb_depto = QComboBox()
        deptos = sorted(RADIACION_COLOMBIA.keys())
        self.cb_depto.addItems(deptos)
        if proyecto.get("departamento") in deptos:
            self.cb_depto.setCurrentText(proyecto["departamento"])

        self.f_hsp_manual = QDoubleSpinBox()
        self.f_hsp_manual.setRange(0, 10)
        self.f_hsp_manual.setSuffix(" HSP")
        self.f_hsp_manual.setSpecialValueText("(usar departamento)")

        self.f_eficiencia = QDoubleSpinBox()
        self.f_eficiencia.setRange(0.50, 1.00)
        self.f_eficiencia.setDecimals(2)
        self.f_eficiencia.setSingleStep(0.01)
        self.f_eficiencia.setValue(0.80)

        fl.addRow("Consumo mensual:", self.f_consumo)
        fl.addRow("Potencia del panel:", self.f_pot_panel)
        fl.addRow("Departamento:", self.cb_depto)
        fl.addRow("HSP manual (0=auto):", self.f_hsp_manual)
        fl.addRow("Eficiencia sistema:", self.f_eficiencia)

        btn_calc = QPushButton("⚡  Calcular Dimensionamiento")
        btn_calc.setObjectName("btn_success")
        btn_calc.setMinimumHeight(42)
        btn_calc.clicked.connect(self._calcular)
        fl.addRow(btn_calc)

        btn_aplicar = QPushButton("📋  Aplicar al Sistema FV")
        btn_aplicar.setObjectName("btn_warning")
        btn_aplicar.setMinimumHeight(38)
        btn_aplicar.clicked.connect(self._aplicar)
        btn_aplicar.setEnabled(False)
        self.btn_aplicar = btn_aplicar
        fl.addRow(btn_aplicar)

        layout.addWidget(izq)

        # Panel derecho - Resultados
        der = QGroupBox("📊 Resultados del Dimensionamiento")
        der_layout = QVBoxLayout(der)
        der_layout.setSpacing(8)

        self.txt_resultado = QTextEdit()
        self.txt_resultado.setReadOnly(True)
        self.txt_resultado.setFont(QFont("Courier New", 10))
        self.txt_resultado.setPlaceholderText("Presione 'Calcular' para ver los resultados...")
        der_layout.addWidget(self.txt_resultado)

        btn_copiar = QPushButton("📋 Copiar memoria de cálculo")
        btn_copiar.clicked.connect(lambda: self._copiar_texto())
        der_layout.addWidget(btn_copiar)

        layout.addWidget(der)
        self._resultado = None

    def _calcular(self):
        try:
            consumo = self.f_consumo.value()
            pot_panel = self.f_pot_panel.value()
            depto = self.cb_depto.currentText()
            hsp_manual = self.f_hsp_manual.value() if self.f_hsp_manual.value() > 0 else None
            eficiencia = self.f_eficiencia.value()

            resultado = calcular_dimensionamiento(
                consumo_kwh_mes=consumo,
                potencia_panel_wp=pot_panel,
                departamento=depto,
                hsp_manual=hsp_manual,
                eficiencia_sistema=eficiencia,
            )
            self._resultado = resultado

            proyecto = ProyectoDAO.obtener(self.proyecto_id)
            texto = generar_resumen_calculo(resultado, proyecto.get("nombre", ""))
            self.txt_resultado.setPlainText(texto)
            self.btn_aplicar.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error de cálculo", str(e))

    def _aplicar(self):
        if not self._resultado:
            return
        res = self._resultado
        datos = {
            "cantidad_paneles": res.cantidad_paneles,
            "potencia_panel": res.potencia_panel_wp,
            "potencia_total_kwp": round(res.potencia_real_kwp, 3),
            "generacion_estimada_kwh": round(res.generacion_mensual_kwh, 2),
            "irradiacion_zona": res.hsp,
            "eficiencia_sistema": res.eficiencia_sistema,
        }
        SistemaFVDAO.guardar(self.proyecto_id, datos)
        QMessageBox.information(self, "✅ Aplicado", "Los resultados se aplicaron al Sistema FV.")

    def _copiar_texto(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.txt_resultado.toPlainText())


# ─── PLANTILLAS ───────────────────────────────────────────────────────────────

class PlantillasPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._cargar()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        lbl = QLabel("📋 Gestión de Plantillas Word")
        lbl.setObjectName("title_label")
        layout.addWidget(lbl)

        banner = InfoBanner(
            "Cargue plantillas .docx con variables {{variable}}. "
            "El sistema reemplazará automáticamente los datos del proyecto al generar documentos.",
            "info"
        )
        layout.addWidget(banner)

        bar = QHBoxLayout()
        btn_nuevo = QPushButton("📁  Cargar Plantilla")
        btn_nuevo.setObjectName("btn_success")
        btn_nuevo.setFixedHeight(36)
        btn_nuevo.clicked.connect(self._cargar_plantilla)
        bar.addWidget(btn_nuevo)

        btn_ejemplos = QPushButton("⭐  Crear Plantillas de Ejemplo")
        btn_ejemplos.setFixedHeight(36)
        btn_ejemplos.clicked.connect(self._crear_ejemplos)
        bar.addWidget(btn_ejemplos)

        btn_eliminar = QPushButton("🗑️  Desactivar")
        btn_eliminar.setObjectName("btn_danger")
        btn_eliminar.setFixedHeight(36)
        btn_eliminar.clicked.connect(self._eliminar)
        bar.addWidget(btn_eliminar)
        bar.addStretch()
        layout.addLayout(bar)

        self.tabla = RetieTable(["Nombre", "Tipo", "Ruta del Archivo", "Descripción"])
        layout.addWidget(self.tabla)

        # Variables disponibles
        layout.addWidget(SectionHeader("Variables disponibles para usar en plantillas"))
        self.txt_vars = QTextEdit()
        self.txt_vars.setReadOnly(True)
        self.txt_vars.setMaximumHeight(160)
        self.txt_vars.setFont(QFont("Courier New", 10))
        self.txt_vars.setPlainText(self._texto_variables())
        layout.addWidget(self.txt_vars)

    def _cargar(self):
        plantillas = PlantillaDAO.listar()
        self.tabla.set_rows(plantillas, ["nombre", "tipo", "ruta_archivo", "descripcion"])

    def _cargar_plantilla(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar plantilla Word", "",
            "Documentos Word (*.docx)"
        )
        if not ruta:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Datos de la plantilla")
        dlg.setMinimumWidth(400)
        lay = QVBoxLayout(dlg)
        form = QFormLayout()
        f_nombre = QLineEdit(os.path.basename(ruta))
        cb_tipo = QComboBox()
        cb_tipo.addItems(["acta_inicio", "declaracion_construccion", "declaracion_diseno",
                          "memoria_calculo", "anexo_acuerdo", "matricula_terceros", "otro"])
        f_desc = QLineEdit()
        form.addRow("Nombre:", f_nombre)
        form.addRow("Tipo:", cb_tipo)
        form.addRow("Descripción:", f_desc)
        lay.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        btns.button(QDialogButtonBox.Save).setText("Guardar")
        lay.addWidget(btns)

        if dlg.exec() == QDialog.Accepted:
            # Copiar al directorio de plantillas
            dir_plantillas = os.path.join(Path.home(), "RETIE_Manager", "Plantillas")
            os.makedirs(dir_plantillas, exist_ok=True)
            destino = os.path.join(dir_plantillas, os.path.basename(ruta))
            shutil.copy2(ruta, destino)
            PlantillaDAO.guardar({
                "nombre": f_nombre.text(),
                "tipo": cb_tipo.currentText(),
                "ruta_archivo": destino,
                "descripcion": f_desc.text(),
                "activa": 1,
                "created_at": datetime.now().isoformat(),
            })
            self._cargar()

    def _crear_ejemplos(self):
        dir_plantillas = os.path.join(Path.home(), "RETIE_Manager", "Plantillas")
        creadas = crear_plantillas_ejemplo(dir_plantillas)
        if creadas:
            for ruta in creadas:
                nombre = os.path.basename(ruta)
                tipo = nombre.replace(".docx", "").replace("_", " ")
                PlantillaDAO.guardar({
                    "nombre": nombre,
                    "tipo": nombre.replace(".docx", ""),
                    "ruta_archivo": ruta,
                    "descripcion": f"Plantilla de ejemplo - {tipo}",
                    "activa": 1,
                    "created_at": datetime.now().isoformat(),
                })
            self._cargar()
            QMessageBox.information(self, "✅ Plantillas creadas",
                                    f"Se crearon {len(creadas)} plantillas de ejemplo en:\n{dir_plantillas}")
        else:
            QMessageBox.information(self, "Aviso",
                                    "Las plantillas de ejemplo ya existen o no se pudo crear (instale python-docx).")

    def _eliminar(self):
        data = self.tabla.selected_data()
        if not data:
            return
        if ConfirmDialog.ask(self, "Desactivar", f"¿Desactivar la plantilla '{data['nombre']}'?"):
            PlantillaDAO.eliminar(data["id"])
            self._cargar()

    def _texto_variables(self) -> str:
        vars_lista = [
            "{{fecha_actual}}           {{fecha_actual_corta}}      {{año_actual}}",
            "{{ingeniero_nombre}}        {{ingeniero_cedula}}         {{ingeniero_matricula}}",
            "{{empresa_nombre}}          {{empresa_nit}}              {{empresa_correo}}",
            "{{empresa_direccion}}       {{empresa_telefono}}",
            "{{cliente_nombre}}          {{cliente_cedula_nit}}       {{cliente_correo}}",
            "{{cliente_direccion}}       {{cliente_telefono}}",
            "{{nombre_proyecto}}         {{proyecto_ciudad}}          {{proyecto_departamento}}",
            "{{proyecto_direccion}}      {{proyecto_tipo}}            {{consumo_kwh_mes}}",
            "{{fecha_inicio}}            {{fecha_fin}}",
            "{{cantidad_paneles}}        {{potencia_panel}}           {{marca_panel}}",
            "{{referencia_panel}}        {{cantidad_inversores}}      {{marca_inversor}}",
            "{{referencia_inversor}}     {{potencia_inversor}}        {{potencia_total_kwp}}",
            "{{calibre_conductor}}       {{tipo_conductor}}           {{proteccion_breaker}}",
            "{{generacion_estimada_kwh}} {{irradiacion_zona}}         {{eficiencia_sistema}}",
        ]
        return "\n".join(vars_lista)


# ─── CONFIGURACIÓN DEL INGENIERO ───────────────────────────────────────────────

class ConfiguracionPanel(QWidget):
    def __init__(self, usuario: dict, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self._setup_ui()
        self._cargar()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(0)

        content = QWidget()
        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        lbl = QLabel("⚙️ Configuración del Ingeniero")
        lbl.setObjectName("title_label")
        layout.addWidget(lbl)

        # Datos personales
        grp = QGroupBox("Datos del Profesional / Empresa")
        form = QFormLayout(grp)
        form.setSpacing(10)

        def inp(ph=""):
            w = QLineEdit()
            w.setPlaceholderText(ph)
            return w

        self.f_nombre = inp("Nombre completo del ingeniero")
        self.f_cedula = inp("Número de cédula")
        self.f_matricula = inp("No. de matrícula profesional")
        self.f_empresa = inp("Nombre de la empresa")
        self.f_nit = inp("NIT de la empresa")
        self.f_dir = inp("Dirección de la empresa")
        self.f_tel = inp("Teléfono de contacto")
        self.f_correo = inp("Correo electrónico")

        form.addRow("Nombre del ingeniero *:", self.f_nombre)
        form.addRow("Cédula:", self.f_cedula)
        form.addRow("Matrícula profesional *:", self.f_matricula)
        form.addRow("Empresa:", self.f_empresa)
        form.addRow("NIT:", self.f_nit)
        form.addRow("Dirección:", self.f_dir)
        form.addRow("Teléfono:", self.f_tel)
        form.addRow("Correo:", self.f_correo)
        layout.addWidget(grp)

        # Cambio de contraseña
        grp_pass = QGroupBox("Cambiar Contraseña")
        fp = QFormLayout(grp_pass)
        fp.setSpacing(8)
        self.f_pass_actual = QLineEdit()
        self.f_pass_actual.setEchoMode(QLineEdit.Password)
        self.f_pass_nueva = QLineEdit()
        self.f_pass_nueva.setEchoMode(QLineEdit.Password)
        self.f_pass_confirm = QLineEdit()
        self.f_pass_confirm.setEchoMode(QLineEdit.Password)
        fp.addRow("Contraseña actual:", self.f_pass_actual)
        fp.addRow("Nueva contraseña:", self.f_pass_nueva)
        fp.addRow("Confirmar nueva:", self.f_pass_confirm)

        btn_pass = QPushButton("🔐 Cambiar Contraseña")
        btn_pass.clicked.connect(self._cambiar_password)
        fp.addRow(btn_pass)
        layout.addWidget(grp_pass)

        # Configuración de red/BD
        grp_bd = QGroupBox("📡 Configuración de Base de Datos (Red Local)")
        fb = QFormLayout(grp_bd)
        from core.database import DB_PATH
        lbl_path = QLabel(DB_PATH)
        lbl_path.setStyleSheet("font-size: 11px; color: #555;")
        lbl_path.setWordWrap(True)
        fb.addRow("Ruta de la BD:", lbl_path)
        self.f_db_path = QLineEdit(DB_PATH)
        self.f_db_path.setPlaceholderText("Ruta a la base de datos (puede ser una ruta de red //servidor/...)")
        fb.addRow("Cambiar ruta BD:", self.f_db_path)
        banner_red = InfoBanner(
            "Para uso en red local, coloque la base de datos en una carpeta compartida "
            "y configure todos los equipos con la misma ruta de red (\\\\servidor\\compartida\\retie.db).",
            "info"
        )
        fb.addRow(banner_red)
        layout.addWidget(grp_bd)

        # Botón guardar
        btn_save = QPushButton("💾  Guardar Configuración")
        btn_save.setObjectName("btn_success")
        btn_save.setMinimumHeight(42)
        btn_save.clicked.connect(self._guardar)
        layout.addWidget(btn_save)
        layout.addStretch()

    def _cargar(self):
        datos = IngenieroDAO.obtener(self.usuario["id"])
        self.f_nombre.setText(datos.get("nombre", "") or "")
        self.f_cedula.setText(datos.get("cedula", "") or "")
        self.f_matricula.setText(datos.get("matricula_profesional", "") or "")
        self.f_empresa.setText(datos.get("empresa", "") or "")
        self.f_nit.setText(datos.get("nit", "") or "")
        self.f_dir.setText(datos.get("direccion", "") or "")
        self.f_tel.setText(datos.get("telefono", "") or "")
        self.f_correo.setText(datos.get("correo", "") or "")

    def _guardar(self):
        datos = {
            "nombre": self.f_nombre.text().strip(),
            "cedula": self.f_cedula.text().strip(),
            "matricula_profesional": self.f_matricula.text().strip(),
            "empresa": self.f_empresa.text().strip(),
            "nit": self.f_nit.text().strip(),
            "direccion": self.f_dir.text().strip(),
            "telefono": self.f_tel.text().strip(),
            "correo": self.f_correo.text().strip(),
        }
        IngenieroDAO.guardar(self.usuario["id"], datos)
        QMessageBox.information(self, "✅ Guardado", "Configuración guardada correctamente.")

    def _cambiar_password(self):
        actual = self.f_pass_actual.text()
        nueva = self.f_pass_nueva.text()
        confirm = self.f_pass_confirm.text()
        if not actual or not nueva:
            QMessageBox.warning(self, "Aviso", "Complete todos los campos de contraseña.")
            return
        if nueva != confirm:
            QMessageBox.warning(self, "Error", "La nueva contraseña y su confirmación no coinciden.")
            return
        from core.database import hash_password, get_connection
        conn = get_connection()
        row = conn.execute(
            "SELECT id FROM usuarios WHERE id=? AND password_hash=?",
            (self.usuario["id"], hash_password(actual))
        ).fetchone()
        conn.close()
        if not row:
            QMessageBox.critical(self, "Error", "La contraseña actual es incorrecta.")
            return
        UsuarioDAO.cambiar_password(self.usuario["id"], nueva)
        self.f_pass_actual.clear()
        self.f_pass_nueva.clear()
        self.f_pass_confirm.clear()
        QMessageBox.information(self, "✅", "Contraseña cambiada correctamente.")


# ─── PANEL USUARIOS (ADMIN) ───────────────────────────────────────────────────

class UsuariosPanel(QWidget):
    def __init__(self, usuario: dict, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self._setup_ui()
        self._cargar()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        lbl = QLabel("👤 Gestión de Usuarios")
        lbl.setObjectName("title_label")
        layout.addWidget(lbl)

        bar = QHBoxLayout()
        btn_nuevo = QPushButton("➕  Nuevo Usuario")
        btn_nuevo.setObjectName("btn_success")
        btn_nuevo.setFixedHeight(36)
        btn_nuevo.clicked.connect(self._nuevo)
        bar.addWidget(btn_nuevo)
        bar.addStretch()
        layout.addLayout(bar)

        self.tabla = RetieTable(["Usuario", "Nombre completo", "Rol", "Activo"])
        layout.addWidget(self.tabla)

    def _cargar(self):
        usuarios = UsuarioDAO.listar()
        self.tabla.set_rows(usuarios, ["username", "nombre_completo", "rol", "activo"])

    def _nuevo(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Nuevo Usuario")
        dlg.setMinimumWidth(380)
        lay = QVBoxLayout(dlg)
        form = QFormLayout()
        form.setSpacing(8)
        f_user = QLineEdit(); f_user.setPlaceholderText("nombre_usuario")
        f_nombre = QLineEdit(); f_nombre.setPlaceholderText("Nombre completo")
        f_pass = QLineEdit(); f_pass.setEchoMode(QLineEdit.Password)
        f_pass.setPlaceholderText("Contraseña")
        cb_rol = QComboBox(); cb_rol.addItems(["ingeniero", "administrador"])
        form.addRow("Usuario *:", f_user)
        form.addRow("Nombre *:", f_nombre)
        form.addRow("Contraseña *:", f_pass)
        form.addRow("Rol:", cb_rol)
        lay.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        btns.button(QDialogButtonBox.Save).setText("Crear Usuario")
        lay.addWidget(btns)
        if dlg.exec() == QDialog.Accepted:
            if not f_user.text() or not f_nombre.text() or not f_pass.text():
                QMessageBox.warning(self, "Aviso", "Complete todos los campos.")
                return
            try:
                UsuarioDAO.crear(f_user.text().strip(), f_pass.text(), f_nombre.text().strip(), cb_rol.currentText())
                self._cargar()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo crear el usuario:\n{str(e)}")
