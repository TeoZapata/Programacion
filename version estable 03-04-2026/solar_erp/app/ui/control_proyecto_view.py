"""
Vista: Control Financiero por Proyecto
Muestra materiales retirados, devoluciones y costos por proyecto.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QPushButton, QScrollArea, QSplitter, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from app.core.database import SessionLocal
from app.ui.table_helpers import configurar_tabla
import os, platform, subprocess
from app.services.services import ProyectoService, SalidaProyectoService


def fmt_cop(v):
    return f"${v:,.0f}" if v >= 0 else f"-${abs(v):,.0f}"


class ResumenCard(QFrame):
    def __init__(self, titulo, valor, icono, color="#1E3A5F", bg="#FFFFFF"):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(90)
        self.setStyleSheet(f"""
            QFrame#card {{ background:{bg}; border-radius:10px; border:1px solid #DDE2E8; }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(12)
        lic = QLabel(icono)
        lic.setStyleSheet(f"font-size:30px; color:{color};")
        lic.setFixedWidth(44)
        lay.addWidget(lic)
        vl = QVBoxLayout()
        self.lbl_val = QLabel(valor)
        self.lbl_val.setStyleSheet(f"font-size:22px; font-weight:bold; color:{color};")
        vl.addWidget(self.lbl_val)
        lt = QLabel(titulo)
        lt.setStyleSheet("font-size:11px; color:#7F8C8D;")
        vl.addWidget(lt)
        lay.addLayout(vl)
        lay.addStretch()

    def set_valor(self, v):
        self.lbl_val.setText(v)


class ControlProyectoView(QWidget):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario
        self._proyectos = []
        self._build_ui()
        self._cargar_proyectos()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        container = QWidget()
        scroll.setWidget(container)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(18)

        # ── Título ───────────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        titulo = QLabel("📊  Control Financiero por Proyecto")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #1E3A5F;")
        hdr.addWidget(titulo)
        hdr.addStretch()
        btn_ref = QPushButton("↻  Refrescar")
        btn_ref.setObjectName("btn_secondary")
        btn_ref.setMinimumHeight(34)
        btn_ref.clicked.connect(self._cargar_proyectos)
        hdr.addWidget(btn_ref)

        btn_pdf_general = QPushButton("📊  Informe General")
        btn_pdf_general.setObjectName("btn_primary")
        btn_pdf_general.setMinimumHeight(34)
        btn_pdf_general.setToolTip("Genera PDF con el resumen financiero de todos los proyectos")
        btn_pdf_general.clicked.connect(self._pdf_general)
        hdr.addWidget(btn_pdf_general)

        btn_pdf_proy = QPushButton("📄  PDF Proyecto")
        btn_pdf_proy.setObjectName("btn_success")
        btn_pdf_proy.setMinimumHeight(34)
        btn_pdf_proy.setToolTip("Genera PDF del reporte financiero del proyecto seleccionado")
        btn_pdf_proy.clicked.connect(self._pdf_proyecto)
        hdr.addWidget(btn_pdf_proy)

        layout.addLayout(hdr)

        # ── Cards resumen global ──────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(14)
        self.card_total_sal   = ResumenCard("Total Salidas (todos los proyectos)", "—", "⬇️", "#1E3A5F")
        self.card_total_dev   = ResumenCard("Total Devoluciones",                  "—", "↩️", "#F39C12", "#FFFBF0")
        self.card_neto        = ResumenCard("Valor Neto Entregado",                "—", "💰", "#27AE60", "#F0FFF4")
        self.card_proyectos   = ResumenCard("Proyectos con Movimientos",           "—", "🏗️", "#9B59B6")
        for c in [self.card_total_sal, self.card_total_dev, self.card_neto, self.card_proyectos]:
            cards_row.addWidget(c)
        layout.addLayout(cards_row)

        # ── Tabla resumen por proyecto ────────────────────────────────────────
        sec_res = self._frame_section("📋  Resumen por Proyecto")
        self.tabla_resumen = QTableWidget(0, 5)
        self.tabla_resumen.setHorizontalHeaderLabels(
            ["Proyecto", "Salidas ($)", "Devoluciones ($)", "Valor Neto ($)", "Materiales"])
        configurar_tabla(self.tabla_resumen, col_stretch=0,
                         cols_fijas=[(1,120),(2,120),(3,120),(4,100)])
        self.tabla_resumen.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_resumen.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_resumen.setAlternatingRowColors(True)
        self.tabla_resumen.verticalHeader().setVisible(False)
        self.tabla_resumen.setMinimumHeight(160)
        self.tabla_resumen.setStyleSheet("QTableWidget { border: none; }")
        self.tabla_resumen.clicked.connect(self._on_resumen_click)
        sec_res[1].addWidget(self.tabla_resumen)
        layout.addWidget(sec_res[0])

        # ── Selector de proyecto para detalle ────────────────────────────────
        det_hdr = QHBoxLayout()
        lbl_det = QLabel("📂  Detalle del Proyecto:")
        lbl_det.setStyleSheet("font-size:14px; font-weight:bold; color:#1E3A5F;")
        det_hdr.addWidget(lbl_det)
        self.combo_proyecto = QComboBox()
        self.combo_proyecto.setMinimumWidth(280)
        self.combo_proyecto.currentIndexChanged.connect(self._cargar_detalle)
        det_hdr.addWidget(self.combo_proyecto)
        det_hdr.addStretch()
        layout.addLayout(det_hdr)

        # ── Tabs de detalle ───────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab { padding: 8px 18px; font-size: 12px; }
            QTabBar::tab:selected { font-weight: bold; color: #1E3A5F; }
        """)

        # Tab 1: Materiales retirados
        tab_salidas = QWidget()
        tsl = QVBoxLayout(tab_salidas)
        tsl.setContentsMargins(0, 10, 0, 0)
        self.tabla_salidas = self._make_tabla(
            ["Fecha", "Material", "Unidad", "Cantidad", "Precio Unit.", "Valor Total", "Responsable"])
        tsl.addWidget(self.tabla_salidas)
        self.tabs.addTab(tab_salidas, "⬇️  Salidas de Material")

        # Tab 2: Devoluciones
        tab_dev = QWidget()
        tdl = QVBoxLayout(tab_dev)
        tdl.setContentsMargins(0, 10, 0, 0)
        self.tabla_dev = self._make_tabla(
            ["Fecha", "Material", "Unidad", "Cantidad", "Precio Unit.", "Valor Devuelto", "Responsable"])
        tdl.addWidget(self.tabla_dev)
        self.tabs.addTab(tab_dev, "↩️  Devoluciones")

        # Tab 3: Resumen financiero del proyecto
        tab_fin = QWidget()
        tfl = QVBoxLayout(tab_fin)
        tfl.setContentsMargins(12, 12, 12, 12)
        tfl.setSpacing(14)
        self.lbl_fin_proyecto = QLabel("Selecciona un proyecto")
        self.lbl_fin_proyecto.setStyleSheet("font-size:15px; font-weight:bold; color:#1E3A5F;")
        tfl.addWidget(self.lbl_fin_proyecto)
        fin_cards = QHBoxLayout()
        fin_cards.setSpacing(12)
        self.fc_salidas = ResumenCard("Total Salidas",     "—", "⬇️", "#1E3A5F")
        self.fc_dev     = ResumenCard("Total Devuelto",    "—", "↩️", "#F39C12", "#FFFBF0")
        self.fc_neto    = ResumenCard("Costo Neto",        "—", "💰", "#27AE60", "#F0FFF4")
        for c in [self.fc_salidas, self.fc_dev, self.fc_neto]:
            fin_cards.addWidget(c)
        fin_cards.addStretch()
        tfl.addLayout(fin_cards)
        self.lbl_material_top = QLabel("")
        self.lbl_material_top.setStyleSheet("color:#7F8C8D; font-size:12px;")
        tfl.addWidget(self.lbl_material_top)
        tfl.addStretch()
        self.tabs.addTab(tab_fin, "💰  Resumen Financiero")

        layout.addWidget(self.tabs)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _frame_section(self, titulo):
        frame = QFrame()
        frame.setObjectName("card")
        frame.setStyleSheet("QFrame#card { background:white; border-radius:12px; border:1px solid #DDE2E8; }")
        vl = QVBoxLayout(frame)
        vl.setContentsMargins(16, 14, 16, 14)
        vl.setSpacing(8)
        lbl = QLabel(titulo)
        lbl.setStyleSheet("font-size:14px; font-weight:bold; color:#1E3A5F;")
        vl.addWidget(lbl)
        return frame, vl

    def _make_tabla(self, cols):
        t = QTableWidget(0, len(cols))
        t.setHorizontalHeaderLabels(cols)
        configurar_tabla(t, col_stretch=1,
                         cols_fijas=[(0,80),(2,75),(3,75),(4,110),(5,110),(6,120),(7,130)])
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectRows)
        t.setAlternatingRowColors(True)
        t.verticalHeader().setVisible(False)
        t.setMinimumHeight(200)
        t.setStyleSheet("QTableWidget { border: none; }")
        return t

    def _item_right(self, texto, color=None):
        it = QTableWidgetItem(texto)
        it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if color:
            it.setForeground(QColor(color))
            it.setFont(QFont("", -1, QFont.Bold))
        return it

    # ── Carga de datos ────────────────────────────────────────────────────────
    def _cargar_proyectos(self):
        db = SessionLocal()
        try:
            self._proyectos = ProyectoService(db).listar()
            resumen = SalidaProyectoService(db).todos_proyectos_resumen()

            # Cards globales
            total_sal = sum(r["total_salidas"] for r in resumen)
            total_dev = sum(r["devoluciones"]  for r in resumen)
            neto      = sum(r["neto"]          for r in resumen)
            self.card_total_sal.set_valor(fmt_cop(total_sal))
            self.card_total_dev.set_valor(fmt_cop(total_dev))
            self.card_neto.set_valor(fmt_cop(neto))
            self.card_proyectos.set_valor(str(len(resumen)))

            # Tabla resumen por proyecto
            self.tabla_resumen.setRowCount(0)
            self._resumen_data = resumen   # guardamos para click
            for r in resumen:
                row = self.tabla_resumen.rowCount()
                self.tabla_resumen.insertRow(row)
                self.tabla_resumen.setItem(row, 0, QTableWidgetItem(r["nombre"]))
                self.tabla_resumen.setItem(row, 1, self._item_right(fmt_cop(r["total_salidas"]), "#1E3A5F"))
                dev_txt = fmt_cop(r["devoluciones"])
                self.tabla_resumen.setItem(row, 2, self._item_right(dev_txt, "#F39C12" if r["devoluciones"] > 0 else None))
                color_neto = "#27AE60" if r["neto"] >= 0 else "#E74C3C"
                self.tabla_resumen.setItem(row, 3, self._item_right(fmt_cop(r["neto"]), color_neto))
                # contar materiales únicos
                sp_svc = SalidaProyectoService(db)
                registros = sp_svc.por_proyecto(r["proyecto_id"])
                unicos = len({reg.material_id for reg in registros})
                self.tabla_resumen.setItem(row, 4, self._item_right(str(unicos)))

            # Combo de proyectos para detalle
            self.combo_proyecto.blockSignals(True)
            self.combo_proyecto.clear()
            self.combo_proyecto.addItem("— Seleccionar proyecto —", None)
            for p in self._proyectos:
                self.combo_proyecto.addItem(p.nombre_proyecto, p.id)
            self.combo_proyecto.blockSignals(False)
        finally:
            db.close()

    def _on_resumen_click(self, index):
        """Al hacer clic en la tabla resumen, carga el detalle de ese proyecto."""
        row = index.row()
        if row < len(self._resumen_data or []):
            pid = self._resumen_data[row]["proyecto_id"]
            # Seleccionar en el combo
            for i in range(self.combo_proyecto.count()):
                if self.combo_proyecto.itemData(i) == pid:
                    self.combo_proyecto.setCurrentIndex(i)
                    break
            self.tabs.setCurrentIndex(2)  # abrir tab financiero

    def _cargar_detalle(self):
        proyecto_id = self.combo_proyecto.currentData()
        if not proyecto_id:
            return
        db = SessionLocal()
        try:
            svc = SalidaProyectoService(db)
            registros = svc.por_proyecto(proyecto_id)

            # Separar salidas y devoluciones
            salidas  = [r for r in registros if r.tipo == "salida"]
            devols   = [r for r in registros if r.tipo == "devolucion"]

            # Tabla salidas
            self.tabla_salidas.setRowCount(0)
            for r in salidas:
                row = self.tabla_salidas.rowCount()
                self.tabla_salidas.insertRow(row)
                self.tabla_salidas.setItem(row, 0, QTableWidgetItem(str(r.fecha)))
                self.tabla_salidas.setItem(row, 1, QTableWidgetItem(
                    r.material.nombre_material if r.material else "—"))
                self.tabla_salidas.setItem(row, 2, QTableWidgetItem(
                    r.material.unidad if r.material else "—"))
                self.tabla_salidas.setItem(row, 3, self._item_right(f"{r.cantidad:g}"))
                self.tabla_salidas.setItem(row, 4, self._item_right(fmt_cop(r.precio_unitario), "#1E3A5F"))
                self.tabla_salidas.setItem(row, 5, self._item_right(fmt_cop(r.valor_total), "#1E3A5F"))
                self.tabla_salidas.setItem(row, 6, QTableWidgetItem(r.responsable or "—"))

            # Tabla devoluciones
            self.tabla_dev.setRowCount(0)
            for r in devols:
                row = self.tabla_dev.rowCount()
                self.tabla_dev.insertRow(row)
                self.tabla_dev.setItem(row, 0, QTableWidgetItem(str(r.fecha)))
                self.tabla_dev.setItem(row, 1, QTableWidgetItem(
                    r.material.nombre_material if r.material else "—"))
                self.tabla_dev.setItem(row, 2, QTableWidgetItem(
                    r.material.unidad if r.material else "—"))
                self.tabla_dev.setItem(row, 3, self._item_right(f"{r.cantidad:g}"))
                self.tabla_dev.setItem(row, 4, self._item_right(fmt_cop(r.precio_unitario), "#F39C12"))
                # valor_total ya es negativo en BD; mostrar el ahorro positivo
                self.tabla_dev.setItem(row, 5, self._item_right(fmt_cop(abs(r.valor_total)), "#27AE60"))
                self.tabla_dev.setItem(row, 6, QTableWidgetItem(r.responsable or "—"))

            # Resumen financiero del proyecto
            total_sal = sum(r.valor_total for r in salidas)
            total_dev = sum(abs(r.valor_total) for r in devols)
            neto      = total_sal - total_dev

            nombre_proyecto = self.combo_proyecto.currentText()
            self.lbl_fin_proyecto.setText(f"Proyecto: {nombre_proyecto}")
            self.fc_salidas.set_valor(fmt_cop(total_sal))
            self.fc_dev.set_valor(fmt_cop(total_dev))
            self.fc_neto.set_valor(fmt_cop(neto))

            # Material más costoso
            costos_mat = {}
            for r in salidas:
                nombre = r.material.nombre_material if r.material else "—"
                costos_mat[nombre] = costos_mat.get(nombre, 0) + r.valor_total
            for r in devols:
                nombre = r.material.nombre_material if r.material else "—"
                costos_mat[nombre] = costos_mat.get(nombre, 0) - abs(r.valor_total)
            if costos_mat:
                top = max(costos_mat, key=costos_mat.get)
                self.lbl_material_top.setText(
                    f"📌 Material de mayor costo: {top}  —  {fmt_cop(costos_mat[top])}")
            else:
                self.lbl_material_top.setText("Sin movimientos registrados para este proyecto.")
        finally:
            db.close()

    # ── PDF Reports ──────────────────────────────────────────────────────────
    def _abrir_pdf(self, ruta):
        try:
            if platform.system() == "Windows":
                os.startfile(ruta)
            elif platform.system() == "Darwin":
                subprocess.call(["open", ruta])
            else:
                subprocess.call(["xdg-open", ruta])
        except Exception:
            pass

    def _pdf_proyecto(self):
        """Genera PDF del reporte financiero del proyecto actualmente seleccionado."""
        from PySide6.QtWidgets import QMessageBox
        proyecto_id = self.combo_proyecto.currentData()
        if not proyecto_id:
            QMessageBox.information(self, "Selección requerida",
                "Selecciona un proyecto en el combo para generar su reporte.")
            return
        nombre_proyecto = self.combo_proyecto.currentText()
        from app.core.database import SessionLocal
        from app.services.services import SalidaProyectoService
        db = SessionLocal()
        try:
            svc = SalidaProyectoService(db)
            registros = svc.por_proyecto(proyecto_id)
            salidas  = [r for r in registros if r.tipo == "salida"]
            devols   = [r for r in registros if r.tipo == "devolucion"]
            total_sal = sum(r.valor_total or 0 for r in salidas)
            total_dev = sum(abs(r.valor_total or 0) for r in devols)
            resumen = {
                "total_salidas": total_sal,
                "devoluciones":  total_dev,
                "neto":          total_sal - total_dev,
            }
            from app.reports.reporte_financiero_proyecto import generar_reporte_proyecto
            ruta = generar_reporte_proyecto(
                nombre_proyecto, resumen, salidas, devols, usuario=self.usuario)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo generar el reporte:\n{e}")
            return
        finally:
            db.close()
        resp = QMessageBox.question(self, "Reporte generado",
            f"Reporte PDF generado:\n{ruta}\n\n¿Deseas abrirlo?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if resp == QMessageBox.Yes:
            self._abrir_pdf(ruta)

    def _pdf_general(self):
        """Genera PDF del resumen financiero de todos los proyectos."""
        from PySide6.QtWidgets import QMessageBox
        from app.core.database import SessionLocal
        from app.services.services import SalidaProyectoService
        db = SessionLocal()
        try:
            svc = SalidaProyectoService(db)
            resumen = svc.todos_proyectos_resumen()
            if not resumen:
                QMessageBox.information(self, "Sin datos",
                    "No hay movimientos financieros registrados aún.")
                return
            from app.reports.reporte_financiero_proyecto import generar_reporte_general_financiero
            ruta = generar_reporte_general_financiero(resumen, usuario=self.usuario)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo generar el reporte:\n{e}")
            return
        finally:
            db.close()
        resp = QMessageBox.question(self, "Informe general generado",
            f"PDF generado:\n{ruta}\n\n¿Deseas abrirlo?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if resp == QMessageBox.Yes:
            self._abrir_pdf(ruta)

