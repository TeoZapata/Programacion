from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from app.core.database import SessionLocal
from app.services.services import ProyectoService, MovimientoService
import os
import subprocess
import platform


class CostosProyectoView(QWidget):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario
        self._build_ui()
        self._cargar_proyectos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(14)

        titulo = QLabel("💰  Costos de Material por Proyecto")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #1E3A5F;")
        layout.addWidget(titulo)

        top = QHBoxLayout()
        top.setSpacing(10)

        self.combo_proyecto = QComboBox()
        self.combo_proyecto.setMinimumWidth(420)
        self.combo_proyecto.currentIndexChanged.connect(self._cargar_resumen)
        top.addWidget(QLabel("Proyecto"))
        top.addWidget(self.combo_proyecto)
        top.addStretch()

        self.btn_pdf = QPushButton("📄  Reporte PDF")
        self.btn_pdf.setObjectName("btn_primary")
        self.btn_pdf.clicked.connect(self._generar_pdf)
        top.addWidget(self.btn_pdf)

        btn_ref = QPushButton("↻  Refrescar")
        btn_ref.setObjectName("btn_secondary")
        btn_ref.clicked.connect(self._cargar_resumen)
        top.addWidget(btn_ref)

        layout.addLayout(top)

        self.lbl_total = QLabel("Total proyecto: —")
        self.lbl_total.setStyleSheet("color: #1E3A5F; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.lbl_total)

        cols = ["Material", "Unidad", "Cantidad neta", "Costo neto"]
        self.tabla = QTableWidget(0, len(cols))
        self.tabla.setHorizontalHeaderLabels(cols)
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        layout.addWidget(self.tabla)

        hint = QLabel("El costo es neto: salidas − devoluciones. Se calcula con el precio guardado al registrar la salida.")
        hint.setStyleSheet("color: #7F8C8D; font-size: 12px;")
        layout.addWidget(hint)

    def _cargar_proyectos(self):
        db = SessionLocal()
        try:
            proyectos = ProyectoService(db).listar()
        finally:
            db.close()
        self.combo_proyecto.blockSignals(True)
        self.combo_proyecto.clear()
        self.combo_proyecto.addItem("Seleccionar proyecto...", None)
        for p in proyectos:
            cli = p.cliente.nombre if p.cliente else ""
            self.combo_proyecto.addItem(f"{p.nombre_proyecto} — {cli}", p.id)
        self.combo_proyecto.blockSignals(False)
        self._cargar_resumen()

    def _cargar_resumen(self):
        proyecto_id = self.combo_proyecto.currentData()
        self.tabla.setRowCount(0)
        if not proyecto_id:
            self.lbl_total.setText("Total proyecto: —")
            self.btn_pdf.setEnabled(False)
            return
        self.btn_pdf.setEnabled(True)

        db = SessionLocal()
        try:
            mov_svc = MovimientoService(db)
            total, filas = mov_svc.resumen_costos_por_proyecto(int(proyecto_id))
        finally:
            db.close()

        self.lbl_total.setText(f"Total proyecto: ${total:,.2f}")
        self.lbl_total.setForegroundRole(QColor("#1E3A5F"))

        for f in filas:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(str(f["material"])))
            self.tabla.setItem(row, 1, QTableWidgetItem(str(f["unidad"])))
            self.tabla.setItem(row, 2, QTableWidgetItem(f"{float(f['cantidad_neta']):g}"))

            costo = float(f["costo_neto"] or 0.0)
            it = QTableWidgetItem(f"${costo:,.2f}")
            it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if costo < 0:
                it.setForeground(QColor("#E74C3C"))
                it.setFont(QFont("", -1, QFont.Bold))
            self.tabla.setItem(row, 3, it)

    def _generar_pdf(self):
        proyecto_id = self.combo_proyecto.currentData()
        if not proyecto_id:
            return
        db = SessionLocal()
        try:
            proy = ProyectoService(db).obtener(int(proyecto_id))
            total, filas = MovimientoService(db).resumen_costos_por_proyecto(int(proyecto_id))
            from app.reports.reporte_costos_proyecto import generar_reporte_costos_proyecto
            ruta = generar_reporte_costos_proyecto(proy, filas, total, usuario=self.usuario)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            return
        finally:
            db.close()

        resp = QMessageBox.question(
            self, "Reporte generado",
            f"Reporte PDF generado:\n{ruta}\n\n¿Deseas abrirlo?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes,
        )
        if resp == QMessageBox.Yes:
            self._abrir_archivo(ruta)

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

