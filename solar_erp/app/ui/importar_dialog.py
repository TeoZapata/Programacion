"""
Diálogo de importación masiva de materiales desde Excel.
"""
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QTextEdit, QFrame, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont

from app.core.database import SessionLocal
from app.ui.table_helpers import configurar_tabla
from app.services.services import InventarioService, ProveedorService
from app.utils.files import open_file
from app.utils.importar_excel import leer_plantilla_excel


class ImportWorker(QThread):
    """Hilo separado para importar sin bloquear la UI."""
    progreso      = Signal(int)          # 0-100
    fila_ok       = Signal(str)          # nombre del material importado
    fila_error    = Signal(str)          # mensaje de error
    finalizado    = Signal(int, int)     # (insertados, errores)

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items

    def run(self):
        total     = len(self.items)
        insertados = 0
        errores   = 0

        db = SessionLocal()
        svc      = InventarioService(db)
        prov_svc = ProveedorService(db)

        # Cache NIT -> proveedor_id
        proveedores = {p.nit: p.id for p in prov_svc.listar() if p.nit}

        for idx, item in enumerate(self.items):
            try:
                proveedor_id = None
                if item.get("proveedor_nit"):
                    proveedor_id = proveedores.get(item["proveedor_nit"])

                svc.crear(
                    nombre_material = item["nombre_material"],
                    categoria       = item["categoria"],
                    unidad          = item["unidad"],
                    cantidad_actual = item["cantidad_actual"],
                    stock_minimo    = item["stock_minimo"],
                    ubicacion       = item["ubicacion"],
                    proveedor_id    = proveedor_id,
                    precio_unitario = item.get("precio_unitario", 0.0),
                    merge_if_exists = True,
                )
                insertados += 1
                self.fila_ok.emit(item["nombre_material"])
            except Exception as e:
                errores += 1
                self.fila_error.emit(f"{item['nombre_material']}: {e}")

            self.progreso.emit(int((idx + 1) / total * 100))

        db.close()
        self.finalizado.emit(insertados, errores)


class ImportarMaterialesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GeoInventario — Importar Materiales desde Excel")
        self.setMinimumSize(780, 580)
        self.setModal(True)
        self._items_preview = []
        self._errores_lectura = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # ── Título ──────────────────────────────────────────────────────────
        titulo = QLabel("📥  Importar Materiales desde Excel")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E3A5F;")
        layout.addWidget(titulo)

        sub = QLabel("Selecciona un archivo Excel (.xlsx) con la plantilla oficial de GeoInventario.")
        sub.setStyleSheet("color: #7F8C8D; font-size: 12px;")
        layout.addWidget(sub)

        # ── Paso 1: Seleccionar archivo ─────────────────────────────────────
        paso1 = self._crear_card("Paso 1 — Seleccionar archivo Excel")
        p1_layout = QHBoxLayout()
        p1_layout.setSpacing(10)

        self.lbl_archivo = QLabel("Ningún archivo seleccionado")
        self.lbl_archivo.setStyleSheet(
            "color: #7F8C8D; background: #F5F6FA; border: 1px dashed #DDE2E8;"
            "border-radius: 6px; padding: 8px 12px; font-size: 12px;"
        )
        self.lbl_archivo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        p1_layout.addWidget(self.lbl_archivo)

        btn_seleccionar = QPushButton("📂  Seleccionar archivo")
        btn_seleccionar.setObjectName("btn_primary")
        btn_seleccionar.setMinimumHeight(38)
        btn_seleccionar.clicked.connect(self._seleccionar_archivo)
        p1_layout.addWidget(btn_seleccionar)

        btn_plantilla = QPushButton("⬇️  Descargar plantilla")
        btn_plantilla.setObjectName("btn_secondary")
        btn_plantilla.setMinimumHeight(38)
        btn_plantilla.setToolTip("Abre la carpeta donde está guardada la plantilla")
        btn_plantilla.clicked.connect(self._abrir_plantilla)
        p1_layout.addWidget(btn_plantilla)

        paso1.layout().addLayout(p1_layout)
        layout.addWidget(paso1)

        # ── Paso 2: Vista previa ────────────────────────────────────────────
        paso2 = self._crear_card("Paso 2 — Vista previa de datos")
        p2_v = QVBoxLayout()
        p2_v.setSpacing(6)

        self.lbl_conteo = QLabel("Carga un archivo para ver la vista previa.")
        self.lbl_conteo.setStyleSheet("color: #7F8C8D; font-size: 12px;")
        p2_v.addWidget(self.lbl_conteo)

        self.tabla_preview = QTableWidget(0, 8)
        self.tabla_preview.setHorizontalHeaderLabels([
            "Material", "Categoría", "Unidad", "Cantidad", "Stock Mín.",
            "Precio Unit.", "Valor Total", "Ubicación"
        ])
        configurar_tabla(self.tabla_preview, col_stretch=0,
                         cols_fijas=[(1,100),(2,70),(3,75),(4,75),(5,100),(6,110),(7,120)])
        self.tabla_preview.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_preview.setAlternatingRowColors(True)
        self.tabla_preview.verticalHeader().setVisible(False)
        self.tabla_preview.setMaximumHeight(180)
        p2_v.addWidget(self.tabla_preview)

        paso2.layout().addLayout(p2_v)
        layout.addWidget(paso2)

        # ── Log / errores ───────────────────────────────────────────────────
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(110)
        self.txt_log.setStyleSheet(
            "background: #1E3A5F; color: #2ECC71; font-family: Consolas, monospace;"
            "font-size: 11px; border-radius: 6px; padding: 8px;"
        )
        self.txt_log.setPlaceholderText("El registro de importación aparecerá aquí...")
        layout.addWidget(self.txt_log)

        # ── Barra de progreso ───────────────────────────────────────────────
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar { border-radius: 5px; background: #DDE2E8; height: 14px; text-align: center; font-size: 11px; }
            QProgressBar::chunk { background: #2ECC71; border-radius: 5px; }
        """)
        layout.addWidget(self.progress)

        # ── Botones finales ─────────────────────────────────────────────────
        btns = QHBoxLayout()
        btns.addStretch()

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btn_secondary")
        self.btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(self.btn_cancelar)

        self.btn_importar = QPushButton("📥  Importar materiales")
        self.btn_importar.setObjectName("btn_success")
        self.btn_importar.setMinimumHeight(42)
        self.btn_importar.setEnabled(False)
        self.btn_importar.clicked.connect(self._iniciar_importacion)
        btns.addWidget(self.btn_importar)

        layout.addLayout(btns)

    def _crear_card(self, titulo_texto):
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background: white; border-radius: 10px; border: 1px solid #DDE2E8; }"
        )
        v = QVBoxLayout(frame)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(8)
        lbl = QLabel(titulo_texto)
        lbl.setStyleSheet("font-weight: bold; font-size: 13px; color: #1E3A5F; border: none;")
        v.addWidget(lbl)
        return frame

    def _log(self, mensaje, color="#2ECC71"):
        self.txt_log.append(f'<span style="color:{color};">{mensaje}</span>')

    def _seleccionar_archivo(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo Excel",
            os.path.expanduser("~"),
            "Archivos Excel (*.xlsx *.xls)"
        )
        if not ruta:
            return

        self.lbl_archivo.setText(ruta)
        self.lbl_archivo.setStyleSheet(
            "color: #2C3E50; background: #F0FFF4; border: 1px solid #2ECC71;"
            "border-radius: 6px; padding: 8px 12px; font-size: 12px;"
        )
        self._cargar_preview(ruta)

    def _cargar_preview(self, ruta):
        self.tabla_preview.setRowCount(0)
        self.txt_log.clear()
        self._log(f"📂 Leyendo archivo: {os.path.basename(ruta)}")

        items, errores, advertencias = leer_plantilla_excel(ruta)
        self._items_preview  = items
        self._errores_lectura = errores

        # Mostrar advertencias
        for adv in advertencias:
            self._log(f"⚠️  {adv}", "#F39C12")

        # Mostrar errores de lectura
        for err in errores:
            self._log(f"❌  {err}", "#E74C3C")

        if not items and errores:
            self.lbl_conteo.setText("❌ No se pudieron leer datos válidos. Revisa los errores.")
            self.btn_importar.setEnabled(False)
            return

        # Poblar tabla preview
        valor_total_general = 0.0
        for item in items:
            row = self.tabla_preview.rowCount()
            self.tabla_preview.insertRow(row)
            self.tabla_preview.setItem(row, 0, QTableWidgetItem(item["nombre_material"]))
            self.tabla_preview.setItem(row, 1, QTableWidgetItem(item["categoria"]))
            self.tabla_preview.setItem(row, 2, QTableWidgetItem(item["unidad"]))
            self.tabla_preview.setItem(row, 3, QTableWidgetItem(str(item["cantidad_actual"])))
            self.tabla_preview.setItem(row, 4, QTableWidgetItem(str(item["stock_minimo"])))
            precio_u = item.get("precio_unitario", 0.0)
            precio_total = item.get("precio_total", 0.0)
            valor_total_general += precio_total
            pu_item = QTableWidgetItem(f"${precio_u:,.0f}" if precio_u else "—")
            pu_item.setForeground(QColor("#1E3A5F"))
            self.tabla_preview.setItem(row, 5, pu_item)
            vt_item = QTableWidgetItem(f"${precio_total:,.0f}" if precio_total else "—")
            vt_item.setForeground(QColor("#27AE60"))
            vt_item.setFont(QFont("", -1, QFont.Bold))
            self.tabla_preview.setItem(row, 6, vt_item)
            self.tabla_preview.setItem(row, 7, QTableWidgetItem(item["ubicacion"] or "—"))

        n_ok  = len(items)
        n_err = len(errores)
        color_badge = "#2ECC71" if n_err == 0 else "#F39C12"
        self.lbl_conteo.setText(
            f'<span style="color:{color_badge}; font-weight:bold;">'
            f'{n_ok} materiales listos para importar</span>'
            + (f' &nbsp;|&nbsp; <span style="color:#E74C3C;">{n_err} filas con errores</span>' if n_err else "")
        )
        self.lbl_conteo.setTextFormat(Qt.RichText)

        self._log(f"✅  {n_ok} materiales válidos encontrados.", "#2ECC71")
        self.btn_importar.setEnabled(n_ok > 0)

    def _iniciar_importacion(self):
        if not self._items_preview:
            return

        resp = QMessageBox.question(
            self, "Confirmar importación",
            f"¿Deseas importar {len(self._items_preview)} materiales al inventario?\n\n"
            "Los materiales que ya existan con el mismo nombre se agregarán de todas formas.",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp != QMessageBox.Yes:
            return

        self.btn_importar.setEnabled(False)
        self.btn_cancelar.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self._log("⏳ Iniciando importación...", "#F39C12")

        self._worker = ImportWorker(self._items_preview)
        self._worker.progreso.connect(self.progress.setValue)
        self._worker.fila_ok.connect(lambda n: self._log(f"  ✓  {n}", "#2ECC71"))
        self._worker.fila_error.connect(lambda e: self._log(f"  ✗  {e}", "#E74C3C"))
        self._worker.finalizado.connect(self._importacion_finalizada)
        self._worker.start()

    def _importacion_finalizada(self, insertados, errores):
        self.progress.setValue(100)
        self.btn_cancelar.setEnabled(True)
        self._log(
            f"\n✅ Importación completada: {insertados} insertados, {errores} errores.",
            "#2ECC71" if errores == 0 else "#F39C12"
        )
        if insertados > 0:
            QMessageBox.information(
                self, "Importación exitosa",
                f"Se importaron {insertados} materiales correctamente."
                + (f"\n\n{errores} filas no pudieron importarse. Revisa el log." if errores else "")
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Sin datos importados",
                "No se pudo importar ningún material. Revisa el log de errores.")

    def _abrir_plantilla(self):
        """Genera (si no existe) y abre la plantilla oficial de GeoInventario."""
        import platform, subprocess, shutil
        from pathlib import Path

        # Buscar en ubicaciones conocidas
        posibles = [
            Path(__file__).parent.parent.parent.parent / "Plantilla_GeoInventario.xlsx",
            Path(__file__).parent.parent.parent / "Plantilla_GeoInventario.xlsx",
            Path(os.path.expanduser("~")) / "Plantilla_GeoInventario.xlsx",
        ]
        encontrado = next((str(p) for p in posibles if p.exists()), None)

        if not encontrado:
            # Generar la plantilla en el directorio raíz del proyecto
            try:
                from app.utils.generar_plantilla import generar_plantilla_excel
                destino = str(posibles[0])
                generar_plantilla_excel(destino)
                encontrado = destino
                self._log(f"✅ Plantilla generada en: {destino}", "#2ECC71")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo generar la plantilla:\n{e}")
                return

        # Copiar al escritorio si no está ahí
        escritorio = Path(os.path.expanduser("~")) / "Desktop" / "Plantilla_GeoInventario.xlsx"
        if not escritorio.exists():
            try:
                shutil.copy2(encontrado, str(escritorio))
                self._log(f"📋 Plantilla copiada al escritorio.", "#2ECC71")
            except Exception:
                pass

        # Abrir archivo
        try:
            open_file(encontrado)
        except Exception as e:
            QMessageBox.information(self, "Plantilla",
                f"Plantilla disponible en:\n{encontrado}")
