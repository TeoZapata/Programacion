"""
Vista completa de Herramientas:
  - Inventario de herramientas (CRUD)
  - Asignación/devolución a trabajadores
  - Reporte general e individual (Word)
  - Importación masiva desde Excel
"""
import os
import subprocess
import platform
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QDialog, QFormLayout, QComboBox, QTextEdit,
    QMessageBox, QFileDialog, QTabWidget, QSplitter,
    QProgressBar, QSizePolicy, QAbstractItemView
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor

from app.core.database import SessionLocal
from app.ui.table_helpers import configurar_tabla
from app.services.services import HerramientaService, TrabajadorService
from app.reports.reporte_herramientas import generar_reporte_general, generar_reporte_trabajador
from app.utils.importar_herramientas import leer_plantilla_herramientas


# ── Helpers ───────────────────────────────────────────────────────────────────
ESTADO_COLORES = {
    "disponible":    "#27AE60",
    "asignada":      "#2980B9",
    "mantenimiento": "#F39C12",
    "baja":          "#E74C3C",
}
ESTADO_ETIQUETA = {
    "disponible":    "✅ Disponible",
    "asignada":      "🔧 Asignada",
    "mantenimiento": "🔄 Mantenimiento",
    "baja":          "❌ Baja",
}

def _item(texto, color=None):
    it = QTableWidgetItem(str(texto) if texto else "—")
    if color:
        it.setForeground(QColor(color))
    return it


# ═══════════════════════════════════════════════════════════════════════════════
#  Diálogo — Crear / Editar Herramienta
# ═══════════════════════════════════════════════════════════════════════════════
class HerramientaDialog(QDialog):
    CATEGORIAS = [
        "Herramienta Eléctrica", "Herramienta Manual", "Medición",
        "Seguridad", "Instalación Solar", "Elevación", "General",
    ]
    ESTADOS = ["disponible", "asignada", "mantenimiento", "baja"]

    def __init__(self, parent=None, herramienta_id=None):
        super().__init__(parent)
        self.herramienta_id = herramienta_id
        self.setWindowTitle("Editar Herramienta" if herramienta_id else "Nueva Herramienta")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(10)

        titulo = QLabel("🔧  " + ("Editar Herramienta" if self.herramienta_id else "Nueva Herramienta"))
        titulo.setStyleSheet("font-size:16px; font-weight:bold; color:#1E3A5F;")
        lay.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        def campo(placeholder="", echo=False):
            w = QLineEdit()
            w.setPlaceholderText(placeholder)
            w.setMinimumHeight(36)
            w.setStyleSheet("QLineEdit{background:#F0F4F8;color:#1A1A2E;border:1.5px solid #CBD5E0;"
                            "border-radius:6px;padding:4px 10px;font-size:13px;}"
                            "QLineEdit:focus{border:2px solid #2ECC71;background:white;}")
            return w

        self.inp_codigo  = campo("Ej: HERR-001 (opcional)")
        self.inp_nombre  = campo("Nombre de la herramienta *")
        self.cmb_cat     = QComboBox()
        self.cmb_cat.addItems(self.CATEGORIAS)
        self.cmb_cat.setMinimumHeight(36)
        self.inp_marca   = campo("Marca")
        self.inp_modelo  = campo("Modelo")
        self.inp_serie   = campo("Número de serie")
        self.cmb_estado  = QComboBox()
        self.cmb_estado.addItems(self.ESTADOS)
        self.cmb_estado.setMinimumHeight(36)
        self.inp_ubic    = campo("Bodega / Estante")
        self.txt_obs     = QTextEdit()
        self.txt_obs.setPlaceholderText("Observaciones...")
        self.txt_obs.setMaximumHeight(70)
        self.txt_obs.setStyleSheet("QTextEdit{background:#F0F4F8;color:#1A1A2E;border:1.5px solid #CBD5E0;"
                                   "border-radius:6px;padding:6px;font-size:13px;}"
                                   "QTextEdit:focus{border:2px solid #2ECC71;background:white;}")

        for lbl, w in [
            ("Código:",        self.inp_codigo),
            ("Nombre *:",      self.inp_nombre),
            ("Categoría:",     self.cmb_cat),
            ("Marca:",         self.inp_marca),
            ("Modelo:",        self.inp_modelo),
            ("N° Serie:",      self.inp_serie),
            ("Estado:",        self.cmb_estado),
            ("Ubicación:",     self.inp_ubic),
            ("Observaciones:", self.txt_obs),
        ]:
            lbl_w = QLabel(lbl)
            lbl_w.setStyleSheet("font-weight:bold; color:#4A5568; font-size:12px;")
            form.addRow(lbl_w, w)

        lay.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        btn_ok = QPushButton("💾  Guardar")
        btn_ok.setObjectName("btn_success")
        btn_ok.setMinimumHeight(40)
        btn_ok.clicked.connect(self._guardar)
        btns.addWidget(btn_ok)
        lay.addLayout(btns)

        if self.herramienta_id:
            self._cargar_datos()

    def _cargar_datos(self):
        db = SessionLocal()
        try:
            h = HerramientaService(db).obtener(self.herramienta_id)
            if h:
                self.inp_codigo.setText(h.codigo or "")
                self.inp_nombre.setText(h.nombre or "")
                idx = self.cmb_cat.findText(h.categoria or "General")
                if idx >= 0:
                    self.cmb_cat.setCurrentIndex(idx)
                self.inp_marca.setText(h.marca or "")
                self.inp_modelo.setText(h.modelo or "")
                self.inp_serie.setText(h.numero_serie or "")
                idx2 = self.cmb_estado.findText(h.estado or "disponible")
                if idx2 >= 0:
                    self.cmb_estado.setCurrentIndex(idx2)
                self.inp_ubic.setText(h.ubicacion or "")
                self.txt_obs.setPlainText(h.observaciones or "")
        finally:
            db.close()

    def _guardar(self):
        nombre = self.inp_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Campo requerido", "El nombre de la herramienta es obligatorio.")
            return
        db = SessionLocal()
        try:
            svc = HerramientaService(db)
            kwargs = dict(
                codigo=self.inp_codigo.text().strip(),
                nombre=nombre,
                categoria=self.cmb_cat.currentText(),
                marca=self.inp_marca.text().strip(),
                modelo=self.inp_modelo.text().strip(),
                numero_serie=self.inp_serie.text().strip(),
                estado=self.cmb_estado.currentText(),
                ubicacion=self.inp_ubic.text().strip(),
                observaciones=self.txt_obs.toPlainText().strip(),
            )
            if self.herramienta_id:
                h = svc.obtener(self.herramienta_id)
                svc.actualizar(h, **kwargs)
            else:
                svc.crear(**kwargs)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            db.close()


# ═══════════════════════════════════════════════════════════════════════════════
#  Diálogo — Asignar Herramienta a Trabajador
# ═══════════════════════════════════════════════════════════════════════════════
class AsignarDialog(QDialog):
    def __init__(self, parent=None, herramienta_id=None):
        super().__init__(parent)
        self.herramienta_id = herramienta_id
        self.setWindowTitle("Asignar Herramienta")
        self.setFixedSize(460, 320)
        self.setModal(True)
        # Stylesheet propio — aislado del tema global para garantizar visibilidad
        self.setStyleSheet("""
            QDialog { background-color: #F8FAFC; }
            QLabel  { color: #2C3E50; background: transparent; }
            QComboBox {
                background: #F0F4F8; color: #1A1A2E;
                border: 1.5px solid #CBD5E0; border-radius: 6px;
                padding: 6px 10px; font-size: 13px;
            }
            QComboBox:focus { border: 2px solid #2ECC71; background: white; }
            QComboBox QAbstractItemView {
                background: white; color: #1A1A2E;
                selection-background-color: #2ECC71; selection-color: white;
            }
            QTextEdit {
                background: #F0F4F8; color: #1A1A2E;
                border: 1.5px solid #CBD5E0; border-radius: 6px;
                padding: 6px; font-size: 13px;
            }
            QTextEdit:focus { border: 2px solid #2ECC71; background: white; }
            QPushButton#btn_cancel {
                background: #F5F6FA; color: #4A5568;
                border: 1.5px solid #CBD5E0; border-radius: 6px;
                padding: 8px 20px; font-size: 13px; font-weight: bold;
            }
            QPushButton#btn_cancel:hover { background: #DDE2E8; }
            QPushButton#btn_asignar {
                background: #27AE60; color: white;
                border: none; border-radius: 6px;
                padding: 8px 24px; font-size: 13px; font-weight: bold;
            }
            QPushButton#btn_asignar:hover { background: #1E8449; }
        """)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(14)

        # Título
        titulo = QLabel("👷  Asignar Herramienta a Trabajador")
        titulo.setStyleSheet("font-size:15px; font-weight:bold; color:#1E3A5F; background:transparent;")
        lay.addWidget(titulo)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background:#DDE2E8; border:none; max-height:1px;")
        lay.addWidget(sep)

        # Nombre de la herramienta
        db = SessionLocal()
        try:
            h = HerramientaService(db).obtener(self.herramienta_id)
            nombre_herr = h.nombre if h else "—"
        finally:
            db.close()

        lbl_herr = QLabel(f"Herramienta:  <b>{nombre_herr}</b>")
        lbl_herr.setStyleSheet("color:#2C3E50; font-size:13px; background:transparent;")
        lbl_herr.setTextFormat(Qt.RichText)
        lay.addWidget(lbl_herr)

        # Label + ComboBox trabajador
        lbl_trab = QLabel("Seleccionar trabajador *")
        lbl_trab.setStyleSheet("font-weight:bold; font-size:12px; color:#4A5568; background:transparent;")
        lay.addWidget(lbl_trab)

        self.cmb_trabajador = QComboBox()
        self.cmb_trabajador.setMinimumHeight(40)
        self.cmb_trabajador.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Forzar paleta para visibilidad garantizada
        from PySide6.QtGui import QPalette, QColor
        pal = self.cmb_trabajador.palette()
        pal.setColor(QPalette.ButtonText, QColor("#1A1A2E"))
        pal.setColor(QPalette.Text,       QColor("#1A1A2E"))
        pal.setColor(QPalette.Base,       QColor("#F0F4F8"))
        self.cmb_trabajador.setPalette(pal)
        lay.addWidget(self.cmb_trabajador)

        # Label + TextEdit observaciones
        lbl_obs = QLabel("Observaciones (opcional)")
        lbl_obs.setStyleSheet("font-weight:bold; font-size:12px; color:#4A5568; background:transparent;")
        lay.addWidget(lbl_obs)

        self.txt_obs = QTextEdit()
        self.txt_obs.setPlaceholderText("Ej: Asignada para proyecto Edificio Norte...")
        self.txt_obs.setFixedHeight(56)
        lay.addWidget(self.txt_obs)

        lay.addStretch()

        # Botones
        btns = QHBoxLayout()
        btns.setSpacing(10)
        btns.addStretch()

        btn_c = QPushButton("Cancelar")
        btn_c.setObjectName("btn_cancel")
        btn_c.setMinimumHeight(38)
        btn_c.clicked.connect(self.reject)
        btns.addWidget(btn_c)

        btn_ok = QPushButton("🔧  Asignar")
        btn_ok.setObjectName("btn_asignar")
        btn_ok.setMinimumHeight(38)
        btn_ok.clicked.connect(self._asignar)
        btns.addWidget(btn_ok)

        lay.addLayout(btns)

        # Cargar trabajadores al final
        self._cargar_trabajadores()

    def _cargar_trabajadores(self):
        db = SessionLocal()
        try:
            trabajadores = TrabajadorService(db).listar()
            self.cmb_trabajador.clear()
            if not trabajadores:
                self.cmb_trabajador.addItem("— Sin trabajadores registrados —", None)
            for t in trabajadores:
                self.cmb_trabajador.addItem(f"  {t.nombre}  —  {t.cargo or 'Sin cargo'}", t.id)
        finally:
            db.close()

    def _asignar(self):
        trabajador_id = self.cmb_trabajador.currentData()
        if not trabajador_id:
            QMessageBox.warning(self, "Sin trabajador", "Selecciona un trabajador de la lista.")
            return
        obs = self.txt_obs.toPlainText().strip()
        db = SessionLocal()
        try:
            HerramientaService(db).asignar(self.herramienta_id, trabajador_id, obs)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error al asignar", str(e))
        finally:
            db.close()


# ═══════════════════════════════════════════════════════════════════════════════
#  Diálogo — Importar desde Excel (hilo separado)
# ═══════════════════════════════════════════════════════════════════════════════
class _CargarWorker(QThread):
    """Worker para cargar herramientas y asignaciones en segundo plano."""
    listo = Signal(list, list)  # (herramientas, asignaciones)
    error = Signal(str)

    def run(self):
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            svc = HerramientaService(db)
            herramientas  = svc.listar()
            asignaciones  = svc.todas_asignaciones_activas()
            self.listo.emit(herramientas, asignaciones)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            db.close()


class _AccionWorker(QThread):
    """Worker genérico para operaciones BD que no deben bloquear la UI."""
    listo = Signal()
    error = Signal(str)

    def __init__(self, fn):
        super().__init__()
        self._fn = fn   # función lambda con la operación BD

    def run(self):
        try:
            self._fn()
            self.listo.emit()
        except Exception as e:
            self.error.emit(str(e))


class _ImportWorker(QThread):
    progreso   = Signal(int)
    fila_ok    = Signal(str)
    fila_err   = Signal(str)
    finalizado = Signal(int, int)

    def __init__(self, items):
        super().__init__()
        self.items = items

    def run(self):
        total = len(self.items)
        ok = err = 0
        db = SessionLocal()
        svc = HerramientaService(db)
        for idx, item in enumerate(self.items):
            try:
                svc.crear(**item)
                ok += 1
                self.fila_ok.emit(item["nombre"])
            except Exception as e:
                err += 1
                self.fila_err.emit(f"{item['nombre']}: {e}")
            self.progreso.emit(int((idx + 1) / total * 100))
        db.close()
        self.finalizado.emit(ok, err)


class ImportarHerramientasDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GeoInventario — Importar Herramientas desde Excel")
        self.setMinimumSize(760, 540)
        self.setModal(True)
        self._items = []
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        titulo = QLabel("📥  Importar Herramientas desde Excel")
        titulo.setStyleSheet("font-size:17px; font-weight:bold; color:#1E3A5F;")
        lay.addWidget(titulo)
        sub = QLabel("Selecciona un archivo .xlsx con la plantilla oficial de GeoInventario.")
        sub.setStyleSheet("color:#7F8C8D; font-size:12px;")
        lay.addWidget(sub)

        # Selección de archivo
        row = QHBoxLayout()
        self.lbl_archivo = QLabel("Ningún archivo seleccionado")
        self.lbl_archivo.setStyleSheet("background:#F5F6FA;border:1px dashed #DDE2E8;border-radius:6px;"
                                       "padding:8px 12px;color:#7F8C8D;font-size:12px;")
        self.lbl_archivo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row.addWidget(self.lbl_archivo)
        btn_sel = QPushButton("📂  Seleccionar")
        btn_sel.setObjectName("btn_primary")
        btn_sel.setMinimumHeight(36)
        btn_sel.clicked.connect(self._seleccionar)
        row.addWidget(btn_sel)
        lay.addLayout(row)

        # Preview
        self.lbl_conteo = QLabel("Carga un archivo para ver la vista previa.")
        self.lbl_conteo.setStyleSheet("color:#7F8C8D; font-size:12px;")
        lay.addWidget(self.lbl_conteo)

        self.tabla = QTableWidget(0, 5)
        self.tabla.setHorizontalHeaderLabels(["Nombre", "Categoría", "Marca", "Estado", "Ubicación"])
        configurar_tabla(self.tabla, col_stretch=1)
        configurar_tabla(self.tabla, col_stretch=1)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setMaximumHeight(160)
        lay.addWidget(self.tabla)

        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(100)
        self.log.setStyleSheet("background:#1E3A5F;color:#2ECC71;font-family:Consolas,monospace;"
                               "font-size:11px;border-radius:6px;padding:8px;")
        lay.addWidget(self.log)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setStyleSheet("QProgressBar{border-radius:5px;background:#DDE2E8;height:14px;}"
                                    "QProgressBar::chunk{background:#2ECC71;border-radius:5px;}")
        lay.addWidget(self.progress)

        btns = QHBoxLayout()
        btns.addStretch()
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setObjectName("btn_secondary")
        self.btn_cancel.clicked.connect(self.reject)
        btns.addWidget(self.btn_cancel)
        self.btn_importar = QPushButton("📥  Importar")
        self.btn_importar.setObjectName("btn_success")
        self.btn_importar.setMinimumHeight(40)
        self.btn_importar.setEnabled(False)
        self.btn_importar.clicked.connect(self._importar)
        btns.addWidget(self.btn_importar)
        lay.addLayout(btns)

    def _log(self, msg, color="#2ECC71"):
        self.log.append(f'<span style="color:{color};">{msg}</span>')

    def _seleccionar(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Excel", os.path.expanduser("~"), "Excel (*.xlsx *.xls)")
        if not ruta:
            return
        self.lbl_archivo.setText(ruta)
        self.lbl_archivo.setStyleSheet("background:#F0FFF4;border:1px solid #2ECC71;border-radius:6px;"
                                       "padding:8px 12px;color:#2C3E50;font-size:12px;")
        self.tabla.setRowCount(0)
        self.log.clear()
        self._log(f"📂 Leyendo: {os.path.basename(ruta)}")

        items, errores, adv = leer_plantilla_herramientas(ruta)
        self._items = items
        for a in adv:
            self._log(f"⚠️  {a}", "#F39C12")
        for e in errores:
            self._log(f"❌  {e}", "#E74C3C")

        for item in items:
            r = self.tabla.rowCount()
            self.tabla.insertRow(r)
            self.tabla.setItem(r, 0, QTableWidgetItem(item["nombre"]))
            self.tabla.setItem(r, 1, QTableWidgetItem(item["categoria"]))
            self.tabla.setItem(r, 2, QTableWidgetItem(item["marca"] or "—"))
            self.tabla.setItem(r, 3, QTableWidgetItem(item["estado"]))
            self.tabla.setItem(r, 4, QTableWidgetItem(item["ubicacion"] or "—"))

        n = len(items)
        color = "#2ECC71" if not errores else "#F39C12"
        self.lbl_conteo.setText(
            f'<span style="color:{color};font-weight:bold;">{n} herramientas listas</span>'
            + (f' | <span style="color:#E74C3C;">{len(errores)} errores</span>' if errores else "")
        )
        self.lbl_conteo.setTextFormat(Qt.RichText)
        self._log(f"✅  {n} herramientas válidas encontradas.", "#2ECC71")
        self.btn_importar.setEnabled(n > 0)

    def _importar(self):
        if not self._items:
            return
        resp = QMessageBox.question(
            self, "Confirmar",
            f"¿Importar {len(self._items)} herramientas al inventario?",
            QMessageBox.Yes | QMessageBox.No)
        if resp != QMessageBox.Yes:
            return

        self.btn_importar.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.progress.setVisible(True)

        self._worker = _ImportWorker(self._items)
        self._worker.progreso.connect(self.progress.setValue)
        self._worker.fila_ok.connect(lambda n: self._log(f"  ✓  {n}", "#2ECC71"))
        self._worker.fila_err.connect(lambda e: self._log(f"  ✗  {e}", "#E74C3C"))
        self._worker.finalizado.connect(self._fin)
        self._worker.start()

    def _fin(self, ok, err):
        self.progress.setValue(100)
        self.btn_cancel.setEnabled(True)
        self._log(f"\n✅ {ok} importadas, {err} errores.", "#2ECC71" if err == 0 else "#F39C12")
        if ok > 0:
            QMessageBox.information(self, "Listo", f"Se importaron {ok} herramientas.")
            self.accept()
        else:
            QMessageBox.warning(self, "Sin datos", "No se importó ninguna herramienta.")


# ═══════════════════════════════════════════════════════════════════════════════
#  Vista Principal de Herramientas
# ═══════════════════════════════════════════════════════════════════════════════
class HerramientasView(QWidget):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario
        self._build_ui()
        self._cargar_todo()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # ── Cabecera ──────────────────────────────────────────────────────────
        header = QHBoxLayout()
        lbl = QLabel("🔧  Herramientas")
        lbl.setStyleSheet("font-size:22px; font-weight:bold; color:#1E3A5F;")
        header.addWidget(lbl)
        header.addStretch()

        # Badges de estado
        self.badge_total = self._badge("Total: 0", "#1E3A5F")
        self.badge_disp  = self._badge("Disponibles: 0", "#27AE60")
        self.badge_asig  = self._badge("Asignadas: 0", "#2980B9")
        self.badge_mant  = self._badge("Mantenimiento: 0", "#F39C12")
        for b in [self.badge_total, self.badge_disp, self.badge_asig, self.badge_mant]:
            header.addWidget(b)

        layout.addLayout(header)

        # ── Tabs ──────────────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #DDE2E8; border-radius: 8px; background: white; }
            QTabBar::tab { background: #F5F6FA; color: #4A5568; padding: 10px 22px;
                           font-size: 13px; font-weight: bold; border-radius: 6px 6px 0 0;
                           margin-right: 3px; }
            QTabBar::tab:selected { background: #1E3A5F; color: white; }
            QTabBar::tab:hover { background: #DDE2E8; }
        """)
        self.tabs.addTab(self._build_tab_inventario(), "📦  Inventario")
        self.tabs.addTab(self._build_tab_asignaciones(), "👷  Asignaciones")
        layout.addWidget(self.tabs)

    def _badge(self, texto, color):
        lbl = QLabel(texto)
        lbl.setStyleSheet(
            f"background:{color}; color:white; border-radius:12px;"
            "padding:4px 14px; font-size:11px; font-weight:bold;"
        )
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    # ── Tab Inventario ────────────────────────────────────────────────────────
    def _build_tab_inventario(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(10)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.inp_buscar_inv = QLineEdit()
        self.inp_buscar_inv.setPlaceholderText("🔍  Buscar por nombre, código, categoría, marca...")
        self.inp_buscar_inv.setMinimumWidth(300)
        self.inp_buscar_inv.setStyleSheet("QLineEdit{background:#F0F4F8;color:#1A1A2E;"
            "border:1.5px solid #CBD5E0;border-radius:8px;padding:8px 12px;font-size:13px;}"
            "QLineEdit:focus{border:2px solid #2ECC71;background:white;}")
        self.inp_buscar_inv.textChanged.connect(self._buscar_inventario)
        toolbar.addWidget(self.inp_buscar_inv)

        self.cmb_filtro_estado = QComboBox()
        self.cmb_filtro_estado.addItems(["Todos los estados", "disponible", "asignada", "mantenimiento", "baja"])
        self.cmb_filtro_estado.setMinimumHeight(38)
        self.cmb_filtro_estado.currentIndexChanged.connect(self._buscar_inventario)
        toolbar.addWidget(self.cmb_filtro_estado)

        toolbar.addStretch()

        for txt, obj, slot in [
            ("↻ Refrescar",       "btn_secondary", self._cargar_todo),
            ("📥 Importar Excel", "btn_warning",   self._importar),
            ("⬇️ Plantilla",      "btn_secondary", self._descargar_plantilla),
            ("＋ Nueva",          "btn_success",   self._nueva_herramienta),
        ]:
            b = QPushButton(txt)
            b.setObjectName(obj)
            b.setMinimumHeight(38)
            b.clicked.connect(slot)
            toolbar.addWidget(b)

        lay.addLayout(toolbar)

        # Tabla inventario
        self.tabla_inv = QTableWidget(0, 9)
        self.tabla_inv.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Categoría", "Marca/Modelo", "N° Serie", "Estado", "Ubicación", "Acciones"
        ])
        configurar_tabla(self.tabla_inv, col_stretch=2,
                         cols_fijas=[(1,85),(3,110),(4,130),(5,110),(6,95),(7,110),(8,105)])
        self.tabla_inv.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_inv.setAlternatingRowColors(True)
        self.tabla_inv.verticalHeader().setVisible(False)
        self.tabla_inv.setColumnHidden(0, True)
        self.tabla_inv.setSelectionBehavior(QAbstractItemView.SelectRows)
        lay.addWidget(self.tabla_inv)

        # Botones de reporte
        rep_row = QHBoxLayout()
        rep_row.addStretch()
        btn_rep_general = QPushButton("📄  Reporte General (Word)")
        btn_rep_general.setObjectName("btn_primary")
        btn_rep_general.setMinimumHeight(38)
        btn_rep_general.clicked.connect(self._reporte_general)
        rep_row.addWidget(btn_rep_general)
        lay.addLayout(rep_row)

        return w

    # ── Tab Asignaciones ──────────────────────────────────────────────────────
    def _build_tab_asignaciones(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(10)

        toolbar = QHBoxLayout()
        self.inp_buscar_asig = QLineEdit()
        self.inp_buscar_asig.setPlaceholderText("🔍  Buscar por trabajador o herramienta...")
        self.inp_buscar_asig.setMinimumWidth(300)
        self.inp_buscar_asig.setStyleSheet("QLineEdit{background:#F0F4F8;color:#1A1A2E;"
            "border:1.5px solid #CBD5E0;border-radius:8px;padding:8px 12px;font-size:13px;}"
            "QLineEdit:focus{border:2px solid #2ECC71;background:white;}")
        self.inp_buscar_asig.textChanged.connect(self._filtrar_asignaciones)
        toolbar.addWidget(self.inp_buscar_asig)
        toolbar.addStretch()

        btn_rep_ind = QPushButton("📋  Reporte por Trabajador")
        btn_rep_ind.setObjectName("btn_primary")
        btn_rep_ind.setMinimumHeight(38)
        btn_rep_ind.clicked.connect(self._reporte_individual)
        toolbar.addWidget(btn_rep_ind)

        lay.addLayout(toolbar)

        self.tabla_asig = QTableWidget(0, 7)
        self.tabla_asig.setHorizontalHeaderLabels([
            "ID Asig", "Herramienta", "Código", "Trabajador", "Cargo", "Fecha Asignación", "Acciones"
        ])
        configurar_tabla(self.tabla_asig, col_stretch=1,
                         cols_fijas=[(2,90),(3,150),(4,110),(5,130),(6,105)])
        self.tabla_asig.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_asig.setAlternatingRowColors(True)
        self.tabla_asig.verticalHeader().setVisible(False)
        self.tabla_asig.setColumnHidden(0, True)
        self.tabla_asig.setSelectionBehavior(QAbstractItemView.SelectRows)
        lay.addWidget(self.tabla_asig)

        return w

    # ── Cargar datos ──────────────────────────────────────────────────────────
    def _cargar_todo(self):
        """Carga datos en QThread para no bloquear la UI."""
        # Deshabilitar botones mientras carga
        self.setEnabled(False)
        self._worker_carga = _CargarWorker()
        self._worker_carga.listo.connect(self._on_carga_lista)
        self._worker_carga.error.connect(self._on_carga_error)
        self._worker_carga.start()

    def _on_carga_lista(self, herramientas, asignaciones):
        self._herramientas = herramientas
        self._asignaciones = asignaciones
        self._poblar_inventario(herramientas)
        self._poblar_asignaciones(asignaciones)
        self._actualizar_badges()
        self.setEnabled(True)

    def _on_carga_error(self, msg):
        self.setEnabled(True)
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Error cargando herramientas", msg)

    def _actualizar_badges(self):
        herr = self._herramientas
        self.badge_total.setText(f"Total: {len(herr)}")
        self.badge_disp.setText(f"Disponibles: {sum(1 for h in herr if h.estado=='disponible')}")
        self.badge_asig.setText(f"Asignadas: {sum(1 for h in herr if h.estado=='asignada')}")
        self.badge_mant.setText(f"Mantenimiento: {sum(1 for h in herr if h.estado=='mantenimiento')}")

    # ── Poblar tabla inventario ───────────────────────────────────────────────
    def _poblar_inventario(self, herramientas):
        self.tabla_inv.setRowCount(0)
        for h in herramientas:
            r = self.tabla_inv.rowCount()
            self.tabla_inv.insertRow(r)
            estado_label = ESTADO_ETIQUETA.get(h.estado, h.estado)
            color_estado  = ESTADO_COLORES.get(h.estado, "#718096")
            self.tabla_inv.setItem(r, 0, _item(h.id))
            self.tabla_inv.setItem(r, 1, _item(h.codigo))
            self.tabla_inv.setItem(r, 2, _item(h.nombre))
            self.tabla_inv.setItem(r, 3, _item(h.categoria))
            self.tabla_inv.setItem(r, 4, _item(f"{h.marca or ''} {h.modelo or ''}".strip()))
            self.tabla_inv.setItem(r, 5, _item(h.numero_serie))
            it_estado = _item(estado_label, color_estado)
            it_estado.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.tabla_inv.setItem(r, 6, it_estado)
            self.tabla_inv.setItem(r, 7, _item(h.ubicacion))

            # Botones de acción
            cell_w = QWidget()
            btn_lay = QHBoxLayout(cell_w)
            btn_lay.setContentsMargins(4, 2, 4, 2)
            btn_lay.setSpacing(4)

            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(30, 28)
            btn_edit.setToolTip("Editar")
            btn_edit.setStyleSheet("QPushButton{background:#EBF5FB;border:1px solid #AED6F1;border-radius:5px;}"
                                   "QPushButton:hover{background:#AED6F1;}")
            btn_edit.clicked.connect(lambda _, hid=h.id: self._editar_herramienta(hid))
            btn_lay.addWidget(btn_edit)

            if h.estado == "disponible":
                btn_asig = QPushButton("👷")
                btn_asig.setFixedSize(30, 28)
                btn_asig.setToolTip("Asignar a trabajador")
                btn_asig.setStyleSheet("QPushButton{background:#EAFAF1;border:1px solid #A9DFBF;border-radius:5px;}"
                                       "QPushButton:hover{background:#A9DFBF;}")
                btn_asig.clicked.connect(lambda _, hid=h.id: self._asignar(hid))
                btn_lay.addWidget(btn_asig)

            btn_del = QPushButton("🗑")
            btn_del.setFixedSize(30, 28)
            btn_del.setToolTip("Eliminar")
            btn_del.setStyleSheet("QPushButton{background:#FDEDEC;border:1px solid #F5B7B1;border-radius:5px;}"
                                  "QPushButton:hover{background:#F5B7B1;}")
            btn_del.clicked.connect(lambda _, hid=h.id: self._eliminar(hid))
            btn_lay.addWidget(btn_del)

            self.tabla_inv.setCellWidget(r, 8, cell_w)
            self.tabla_inv.setRowHeight(r, 38)

    # ── Poblar tabla asignaciones ─────────────────────────────────────────────
    def _poblar_asignaciones(self, asignaciones):
        self.tabla_asig.setRowCount(0)
        for a in asignaciones:
            r = self.tabla_asig.rowCount()
            self.tabla_asig.insertRow(r)
            nombre_herr = a.herramienta.nombre if a.herramienta else "—"
            codigo_herr = (a.herramienta.codigo or "—") if a.herramienta else "—"
            nombre_trab = a.trabajador.nombre if a.trabajador else "—"
            cargo_trab  = (a.trabajador.cargo or "—") if a.trabajador else "—"
            fecha       = a.fecha_asignacion.strftime("%d/%m/%Y %H:%M") if a.fecha_asignacion else "—"

            self.tabla_asig.setItem(r, 0, _item(a.id))
            self.tabla_asig.setItem(r, 1, _item(nombre_herr))
            self.tabla_asig.setItem(r, 2, _item(codigo_herr))
            self.tabla_asig.setItem(r, 3, _item(nombre_trab))
            self.tabla_asig.setItem(r, 4, _item(cargo_trab))
            self.tabla_asig.setItem(r, 5, _item(fecha))

            cell_w = QWidget()
            b_lay  = QHBoxLayout(cell_w)
            b_lay.setContentsMargins(4, 2, 4, 2)
            b_lay.setSpacing(4)

            btn_dev = QPushButton("↩️ Devolver")
            btn_dev.setMinimumHeight(28)
            btn_dev.setStyleSheet("QPushButton{background:#EAFAF1;border:1px solid #A9DFBF;border-radius:5px;"
                                  "font-size:11px;padding:2px 8px;}"
                                  "QPushButton:hover{background:#27AE60;color:white;}")
            btn_dev.clicked.connect(lambda _, aid=a.id: self._devolver(aid))
            b_lay.addWidget(btn_dev)

            self.tabla_asig.setCellWidget(r, 6, cell_w)
            self.tabla_asig.setRowHeight(r, 38)

    # ── Búsqueda / filtros ────────────────────────────────────────────────────
    def _buscar_inventario(self):
        texto  = self.inp_buscar_inv.text().strip()
        estado = self.cmb_filtro_estado.currentText()

        db = SessionLocal()
        try:
            svc = HerramientaService(db)
            herr = svc.buscar(texto) if texto else svc.listar()
        finally:
            db.close()

        if estado != "Todos los estados":
            herr = [h for h in herr if h.estado == estado]

        self._poblar_inventario(herr)

    def _filtrar_asignaciones(self):
        texto = self.inp_buscar_asig.text().strip().lower()
        if not texto:
            self._poblar_asignaciones(self._asignaciones)
            return
        filtradas = [
            a for a in self._asignaciones
            if texto in (a.herramienta.nombre if a.herramienta else "").lower()
            or texto in (a.trabajador.nombre if a.trabajador else "").lower()
        ]
        self._poblar_asignaciones(filtradas)

    # ── CRUD ─────────────────────────────────────────────────────────────────
    def _nueva_herramienta(self):
        if HerramientaDialog(self).exec():
            self._cargar_todo()

    def _editar_herramienta(self, hid):
        if HerramientaDialog(self, herramienta_id=hid).exec():
            self._cargar_todo()

    def _asignar(self, hid):
        if AsignarDialog(self, herramienta_id=hid).exec():
            self._cargar_todo()
            self.tabs.setCurrentIndex(1)

    def _devolver(self, aid):
        resp = QMessageBox.question(
            self, "Confirmar devolución",
            "¿Confirmas la devolución de esta herramienta?\nQuedarará disponible nuevamente.",
            QMessageBox.Yes | QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        self._ejecutar_accion(
            lambda: self._op_devolver(aid),
            post_tab=None
        )

    def _op_devolver(self, aid):
        db = SessionLocal()
        try:
            HerramientaService(db).devolver(aid)
        finally:
            db.close()

    def _eliminar(self, hid):
        resp = QMessageBox.question(
            self, "Eliminar herramienta",
            "¿Estás seguro de eliminar esta herramienta?\nSe eliminará también su historial de asignaciones.",
            QMessageBox.Yes | QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        self._ejecutar_accion(
            lambda: self._op_eliminar(hid),
            post_tab=None
        )

    def _op_eliminar(self, hid):
        db = SessionLocal()
        try:
            HerramientaService(db).eliminar(hid)
        finally:
            db.close()

    def _ejecutar_accion(self, fn, post_tab=None):
        """Ejecuta una operación BD en QThread para no bloquear la UI."""
        self.setEnabled(False)
        self._accion_worker = _AccionWorker(fn)
        self._accion_worker.listo.connect(
            lambda: self._on_accion_ok(post_tab))
        self._accion_worker.error.connect(self._on_accion_error)
        self._accion_worker.start()

    def _on_accion_ok(self, post_tab):
        self._cargar_todo()
        if post_tab is not None:
            self.tabs.setCurrentIndex(post_tab)

    def _on_accion_error(self, msg):
        self.setEnabled(True)
        QMessageBox.critical(self, "Error", msg)

    # ── Importar ──────────────────────────────────────────────────────────────
    def _importar(self):
        if ImportarHerramientasDialog(self).exec():
            self._cargar_todo()

    def _descargar_plantilla(self):
        posibles = [
            os.path.join(os.path.expanduser("~"), "Plantilla_Herramientas_GeoInventario.xlsx"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Plantilla_Herramientas_GeoInventario.xlsx"),
        ]
        encontrada = next((p for p in posibles if os.path.exists(p)), None)
        if encontrada:
            try:
                if platform.system() == "Windows":
                    os.startfile(encontrada)
                elif platform.system() == "Darwin":
                    subprocess.call(["open", encontrada])
                else:
                    subprocess.call(["xdg-open", encontrada])
                return
            except Exception:
                pass
        QMessageBox.information(
            self, "Plantilla",
            "La plantilla 'Plantilla_Herramientas_GeoInventario.xlsx' se encuentra\n"
            "en la carpeta raíz del proyecto GeoInventario.\n\n"
            "También puedes copiarla desde la descarga inicial.")

    # ── Reportes ──────────────────────────────────────────────────────────────
    def _reporte_general(self):
        db = SessionLocal()
        try:
            svc  = HerramientaService(db)
            herr = svc.listar()
            asig = svc.todas_asignaciones_activas()
        finally:
            db.close()

        if not herr:
            QMessageBox.information(self, "Sin datos", "No hay herramientas registradas.")
            return

        try:
            ruta = generar_reporte_general(herr, asig)
            resp = QMessageBox.information(
                self, "✅ Reporte generado",
                f"Reporte guardado en:\n{ruta}\n\n¿Deseas abrirlo?",
                QMessageBox.Yes | QMessageBox.No)
            if resp == QMessageBox.Yes:
                self._abrir_archivo(ruta)
        except Exception as e:
            QMessageBox.critical(self, "Error al generar reporte", str(e))

    def _reporte_individual(self):
        # Obtener trabajadores únicos en asignaciones activas
        db = SessionLocal()
        try:
            svc  = HerramientaService(db)
            asig = svc.todas_asignaciones_activas()
            svc_t = TrabajadorService(db)
            trabajadores = svc_t.listar()
        finally:
            db.close()

        if not trabajadores:
            QMessageBox.information(self, "Sin datos", "No hay trabajadores registrados.")
            return

        # Diálogo de selección
        dlg = QDialog(self)
        dlg.setWindowTitle("Seleccionar Trabajador")
        dlg.setMinimumWidth(380)
        dlg.setModal(True)
        v = QVBoxLayout(dlg)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(12)

        v.addWidget(QLabel("Selecciona el trabajador para el reporte:"))
        cmb = QComboBox()
        cmb.setMinimumHeight(38)
        for t in trabajadores:
            cmb.addItem(f"{t.nombre} — {t.cargo or 'Sin cargo'}", t.id)
        v.addWidget(cmb)

        brow = QHBoxLayout()
        brow.addStretch()
        bc = QPushButton("Cancelar")
        bc.setObjectName("btn_secondary")
        bc.clicked.connect(dlg.reject)
        brow.addWidget(bc)
        bo = QPushButton("📋  Generar Reporte")
        bo.setObjectName("btn_primary")
        bo.setMinimumHeight(40)
        bo.clicked.connect(dlg.accept)
        brow.addWidget(bo)
        v.addLayout(brow)

        if dlg.exec() != QDialog.Accepted:
            return

        trabajador_id  = cmb.currentData()
        trabajador_obj = next((t for t in trabajadores if t.id == trabajador_id), None)

        db = SessionLocal()
        try:
            asig_trab = HerramientaService(db).asignaciones_activas_trabajador(trabajador_id)
        finally:
            db.close()

        try:
            ruta = generar_reporte_trabajador(trabajador_obj, asig_trab)
            resp = QMessageBox.information(
                self, "✅ Reporte generado",
                f"Reporte guardado en:\n{ruta}\n\n¿Deseas abrirlo?",
                QMessageBox.Yes | QMessageBox.No)
            if resp == QMessageBox.Yes:
                self._abrir_archivo(ruta)
        except Exception as e:
            QMessageBox.critical(self, "Error al generar reporte", str(e))

    def _abrir_archivo(self, ruta):
        try:
            if platform.system() == "Windows":
                os.startfile(ruta)
            elif platform.system() == "Darwin":
                subprocess.call(["open", ruta])
            else:
                subprocess.call(["xdg-open", ruta])
        except Exception:
            pass
