"""
Vista de Pedido de Material — GeoInventario
- Busca materiales del inventario
- Si no se encuentra, permite agregarlo al pedido como "externo" (a comprar)
  y opcionalmente registrarlo en la base de datos
- Reporte PDF con materiales disponibles y materiales a comprar
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDoubleSpinBox,
    QLineEdit, QTextEdit, QMessageBox, QComboBox, QFrame,
    QFormLayout, QDialog, QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
from app.core.database import SessionLocal
from app.ui.table_helpers import configurar_tabla
from app.services.services import InventarioService, ProyectoService
from app.core.config import CATEGORIAS_INVENTARIO
from app.utils.files import open_file


# ─── Diálogo: material no encontrado ─────────────────────────────────────────
class MaterialNoEncontradoDialog(QDialog):
    def __init__(self, nombre_sugerido: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Material no encontrado")
        self.setMinimumWidth(460)
        self.setModal(True)
        self.result_data = None
        self.guardar_en_bd = False
        self._build_ui(nombre_sugerido)

    def _build_ui(self, nombre_sugerido):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 16)
        layout.setSpacing(10)

        icono = QLabel("🔍")
        icono.setStyleSheet("font-size: 30px;")
        icono.setAlignment(Qt.AlignCenter)
        layout.addWidget(icono)

        titulo = QLabel("Material no encontrado en inventario")
        titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E3A5F;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        desc = QLabel("Puedes agregar este material al pedido.\nAparecerá en la lista de materiales a comprar.")
        desc.setStyleSheet("font-size: 11px; color: #7F8C8D;")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #DDE2E8;")
        layout.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(8)

        self.input_nombre = QLineEdit(nombre_sugerido)
        self.input_nombre.setPlaceholderText("Nombre del material")
        form.addRow("Nombre:*", self.input_nombre)

        self.input_unidad = QLineEdit()
        self.input_unidad.setPlaceholderText("unidad, metro, kg, ...")
        form.addRow("Unidad:*", self.input_unidad)

        self.spin_cantidad = QDoubleSpinBox()
        self.spin_cantidad.setMinimum(0.01)
        self.spin_cantidad.setMaximum(99999)
        self.spin_cantidad.setValue(1)
        self.spin_cantidad.setDecimals(2)
        form.addRow("Cantidad requerida:*", self.spin_cantidad)

        self.combo_categoria = QComboBox()
        for cat in CATEGORIAS_INVENTARIO:
            self.combo_categoria.addItem(cat)
        form.addRow("Categoría:", self.combo_categoria)

        layout.addLayout(form)

        # Toggle guardar en BD
        self.toggle_frame = QFrame()
        self.toggle_frame.setStyleSheet(
            "QFrame { background: #EBF5FB; border-radius: 6px; border: 1px solid #AED6F1; }")
        tl = QHBoxLayout(self.toggle_frame)
        tl.setContentsMargins(12, 8, 12, 8)
        self.btn_toggle = QPushButton("☐  También guardar en la base de datos")
        self.btn_toggle.setCheckable(True)
        self.btn_toggle.setStyleSheet("""
            QPushButton { background: transparent; border: none; font-size: 12px;
                          color: #1E3A5F; text-align: left; font-weight: bold; }
            QPushButton:checked { color: #27AE60; }
        """)
        self.btn_toggle.clicked.connect(self._toggle_bd)
        tl.addWidget(self.btn_toggle)
        layout.addWidget(self.toggle_frame)

        # Campos extra para BD
        self.bd_frame = QFrame()
        self.bd_frame.setVisible(False)
        self.bd_frame.setStyleSheet(
            "QFrame { background: #F0FFF4; border-radius: 6px; border: 1px solid #A9DFBF; }")
        bdl = QFormLayout(self.bd_frame)
        bdl.setContentsMargins(12, 10, 12, 10)
        bdl.setSpacing(6)
        bdl.addRow(QLabel("Datos adicionales para inventario:"))
        self.input_stock_min = QDoubleSpinBox()
        self.input_stock_min.setMinimum(0)
        self.input_stock_min.setMaximum(99999)
        self.input_stock_min.setValue(0)
        bdl.addRow("Stock mínimo:", self.input_stock_min)
        self.input_ubicacion = QLineEdit()
        self.input_ubicacion.setPlaceholderText("Bodega, estante...")
        bdl.addRow("Ubicación:", self.input_ubicacion)
        layout.addWidget(self.bd_frame)

        # Botones
        btns = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btn_secondary")
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btns.addStretch()

        self.btn_solo = QPushButton("📋  Solo al Pedido")
        self.btn_solo.setObjectName("btn_primary")
        self.btn_solo.clicked.connect(self._aceptar_solo)
        btns.addWidget(self.btn_solo)

        self.btn_con_bd = QPushButton("💾  Al Pedido + Guardar en BD")
        self.btn_con_bd.setObjectName("btn_success")
        self.btn_con_bd.setVisible(False)
        self.btn_con_bd.clicked.connect(self._aceptar_con_bd)
        btns.addWidget(self.btn_con_bd)
        layout.addLayout(btns)

    def _toggle_bd(self, checked):
        self.bd_frame.setVisible(checked)
        self.btn_con_bd.setVisible(checked)
        self.btn_solo.setVisible(not checked)
        txt = "☑  También guardar en la base de datos" if checked else "☐  También guardar en la base de datos"
        self.btn_toggle.setText(txt)
        self.adjustSize()

    def _validar(self):
        if not self.input_nombre.text().strip():
            QMessageBox.warning(self, "Validación", "El nombre es obligatorio.")
            return False
        if not self.input_unidad.text().strip():
            QMessageBox.warning(self, "Validación", "La unidad es obligatoria.")
            return False
        return True

    def _aceptar_solo(self):
        if not self._validar():
            return
        self.result_data = {
            "nombre": self.input_nombre.text().strip(),
            "unidad": self.input_unidad.text().strip(),
            "cantidad": self.spin_cantidad.value(),
            "categoria": self.combo_categoria.currentText(),
        }
        self.guardar_en_bd = False
        self.accept()

    def _aceptar_con_bd(self):
        if not self._validar():
            return
        self.result_data = {
            "nombre": self.input_nombre.text().strip(),
            "unidad": self.input_unidad.text().strip(),
            "cantidad": self.spin_cantidad.value(),
            "categoria": self.combo_categoria.currentText(),
            "stock_min": self.input_stock_min.value(),
            "ubicacion": self.input_ubicacion.text().strip(),
        }
        self.guardar_en_bd = True
        self.accept()


# ─── Vista Principal ──────────────────────────────────────────────────────────
class PedidoMaterialView(QWidget):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario
        self._materiales_db = []
        self._pedido = {}     # {material_id: cantidad}
        self._extras = {}     # {key: {nombre,unidad,cantidad,categoria}}
        self._indice_busqueda = {}
        self._filtro_pendiente = ""
        self._timer_busqueda = QTimer(self)
        self._timer_busqueda.setSingleShot(True)
        self._timer_busqueda.setInterval(180)
        self._timer_busqueda.timeout.connect(self._aplicar_filtro_pendiente)
        self._build_ui()
        self._cargar_materiales()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(14)

        # Título + refrescar
        header = QHBoxLayout()
        titulo = QLabel("🛒  Pedido de Material")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #1E3A5F;")
        header.addWidget(titulo)
        header.addStretch()
        btn_ref = QPushButton("↻  Refrescar Inventario")
        btn_ref.setObjectName("btn_secondary")
        btn_ref.setMinimumHeight(34)
        btn_ref.setToolTip("Actualiza el stock desde la base de datos")
        btn_ref.clicked.connect(self._refrescar)
        header.addWidget(btn_ref)
        layout.addLayout(header)

        desc = QLabel("Indica las cantidades que necesitas. Si un material no aparece, el sistema te dará la opción de agregarlo al pedido o al inventario.")
        desc.setStyleSheet("font-size: 12px; color: #7F8C8D;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Info pedido
        info_frame = QFrame()
        info_frame.setStyleSheet("QFrame { background: #F5F6FA; border-radius: 8px; border: 1px solid #DDE2E8; }")
        info_l = QFormLayout(info_frame)
        info_l.setContentsMargins(16, 12, 16, 12)
        info_l.setSpacing(8)
        self.input_solicitante = QLineEdit()
        self.input_solicitante.setPlaceholderText("Nombre del solicitante")
        info_l.addRow("Solicitante:", self.input_solicitante)
        self.combo_proyecto = QComboBox()
        self._cargar_proyectos()
        info_l.addRow("Proyecto:", self.combo_proyecto)
        self.input_obs = QTextEdit()
        self.input_obs.setMaximumHeight(54)
        self.input_obs.setPlaceholderText("Observaciones (opcional)")
        info_l.addRow("Observaciones:", self.input_obs)
        layout.addWidget(info_frame)

        # Búsqueda
        busq_l = QHBoxLayout()
        busq_l.setSpacing(8)
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("🔍  Buscar material por nombre o categoría...")
        self.input_buscar.setMinimumHeight(36)
        self.input_buscar.textChanged.connect(self._programar_filtro)
        busq_l.addWidget(self.input_buscar)
        btn_x = QPushButton("✕")
        btn_x.setObjectName("btn_secondary")
        btn_x.setFixedWidth(36)
        btn_x.setMinimumHeight(36)
        btn_x.clicked.connect(lambda: self.input_buscar.clear())
        busq_l.addWidget(btn_x)
        btn_ne = QPushButton("➕  No encontré el material")
        btn_ne.setObjectName("btn_warning")
        btn_ne.setMinimumHeight(36)
        btn_ne.setToolTip("Agregar un material que no está en el inventario")
        btn_ne.clicked.connect(self._agregar_externo)
        busq_l.addWidget(btn_ne)
        layout.addLayout(busq_l)

        # Banner sin resultados
        self.banner = QFrame()
        self.banner.setStyleSheet("QFrame { background: #FFF8E1; border: 1px solid #F9A825; border-radius: 6px; }")
        bl = QHBoxLayout(self.banner)
        bl.setContentsMargins(12, 8, 12, 8)
        bl.addWidget(QLabel("⚠️  No se encontraron resultados. ¿El material no existe en inventario?"))
        bl.addStretch()
        btn_ba = QPushButton("➕ Agregar al pedido de todas formas")
        btn_ba.setObjectName("btn_warning")
        btn_ba.clicked.connect(self._agregar_externo)
        bl.addWidget(btn_ba)
        self.banner.setVisible(False)
        layout.addWidget(self.banner)

        # Tabla inventario
        lbl_t = QLabel("Inventario de Materiales")
        lbl_t.setStyleSheet("font-size: 13px; font-weight: bold; color: #1E3A5F;")
        layout.addWidget(lbl_t)

        cols = ["ID", "Material", "Categoría", "Unidad", "Stock Actual", "Stock Mín.", "Estado", "Solicitar Cant."]
        self.tabla = QTableWidget(0, len(cols))
        self.tabla.setHorizontalHeaderLabels(cols)
        configurar_tabla(self.tabla, col_stretch=1)
        configurar_tabla(self.tabla, col_stretch=1,
                         cols_fijas=[(0,40),(2,75),(3,75),(4,90),(5,90),(6,90),(7,105)])
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setMinimumHeight(220)
        layout.addWidget(self.tabla)

        # Sección extras
        self.seccion_ext = QWidget()
        ext_l = QVBoxLayout(self.seccion_ext)
        ext_l.setContentsMargins(0, 0, 0, 0)
        ext_l.setSpacing(4)
        lbl_ext = QLabel("📋  Materiales agregados manualmente (no en inventario) — se incluirán en la lista a comprar")
        lbl_ext.setStyleSheet("font-size: 12px; font-weight: bold; color: #E67E22;")
        lbl_ext.setWordWrap(True)
        ext_l.addWidget(lbl_ext)
        self.tabla_extras = QTableWidget(0, 5)
        self.tabla_extras.setHorizontalHeaderLabels(["Material", "Categoría", "Unidad", "Cantidad", ""])
        configurar_tabla(self.tabla_extras, col_stretch=0,
                         cols_fijas=[(1,75),(2,90),(3,75),(4,105)])
        self.tabla_extras.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_extras.setAlternatingRowColors(True)
        self.tabla_extras.verticalHeader().setVisible(False)
        self.tabla_extras.setMaximumHeight(150)
        ext_l.addWidget(self.tabla_extras)
        self.seccion_ext.setVisible(False)
        layout.addWidget(self.seccion_ext)

        # Resumen
        res_frame = QFrame()
        res_frame.setStyleSheet("QFrame { background: #EBF5FB; border-radius: 8px; border: 1px solid #AED6F1; }")
        res_l = QHBoxLayout(res_frame)
        res_l.setContentsMargins(16, 10, 16, 10)
        self.lbl_total = QLabel("📋 En pedido: 0")
        self.lbl_total.setStyleSheet("font-size: 13px; color: #1E3A5F; font-weight: bold;")
        res_l.addWidget(self.lbl_total)
        res_l.addStretch()
        self.lbl_disp = QLabel("✅ En stock: 0")
        self.lbl_disp.setStyleSheet("font-size: 13px; color: #27AE60; font-weight: bold;")
        res_l.addWidget(self.lbl_disp)
        self.lbl_comp = QLabel("🛒 A comprar: 0")
        self.lbl_comp.setStyleSheet("font-size: 13px; color: #E74C3C; font-weight: bold;")
        res_l.addWidget(self.lbl_comp)
        layout.addWidget(res_frame)

        # Botones finales
        bot_l = QHBoxLayout()
        btn_lp = QPushButton("🗑  Limpiar Pedido")
        btn_lp.setObjectName("btn_secondary")
        btn_lp.setMinimumHeight(40)
        btn_lp.clicked.connect(self._limpiar_pedido)
        bot_l.addWidget(btn_lp)
        bot_l.addStretch()
        btn_pv = QPushButton("👁  Vista Previa")
        btn_pv.setObjectName("btn_primary")
        btn_pv.setMinimumHeight(40)
        btn_pv.clicked.connect(self._ver_preview)
        bot_l.addWidget(btn_pv)
        btn_pdf = QPushButton("📄  Generar Reporte PDF")
        btn_pdf.setMinimumHeight(40)
        btn_pdf.setStyleSheet("background-color: #1E3A5F; color: white; border-radius: 6px; font-weight: bold; padding: 0 16px;")
        btn_pdf.clicked.connect(self._generar_reporte)
        bot_l.addWidget(btn_pdf)
        layout.addLayout(bot_l)

    # ─── Datos ───────────────────────────────────────────────────────────────
    def _cargar_proyectos(self):
        self.combo_proyecto.clear()
        self.combo_proyecto.addItem("— Sin proyecto —", None)
        db = SessionLocal()
        try:
            from app.models.proyecto import Proyecto as _Proyecto
            proyectos = (db.query(_Proyecto)
                         .order_by(_Proyecto.nombre_proyecto)
                         .all())
            for p in proyectos:
                self.combo_proyecto.addItem(p.nombre_proyecto, p.id)
        except Exception as e:
            pass  # tabla vacía o BD no inicializada aún
        finally:
            db.close()

    def showEvent(self, event):
        """Recarga proyectos cada vez que la vista se muestra."""
        super().showEvent(event)
        self._cargar_proyectos()

    def _cargar_materiales(self):
        db = SessionLocal()
        try:
            self._materiales_db = InventarioService(db).listar()
        finally:
            db.close()
        self._reconstruir_indice_busqueda()
        self._poblar_tabla(self._materiales_db)

    def _refrescar(self):
        texto = self.input_buscar.text()
        db = SessionLocal()
        try:
            self._materiales_db = InventarioService(db).listar()
        finally:
            db.close()
        self._reconstruir_indice_busqueda()
        if texto:
            self._filtrar_tabla(texto)
        else:
            self._poblar_tabla(self._materiales_db)
        self._actualizar_resumen()

    def _reconstruir_indice_busqueda(self):
        self._indice_busqueda = {
            m.id: f"{(m.nombre_material or '').lower()} {(m.categoria or '').lower()}".strip()
            for m in self._materiales_db
        }

    def _poblar_tabla(self, materiales):
        self.tabla.setUpdatesEnabled(False)
        self.tabla.setRowCount(0)
        for m in materiales:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(str(m.id)))
            ni = QTableWidgetItem(m.nombre_material)
            ni.setFont(QFont("", -1, QFont.Bold))
            self.tabla.setItem(row, 1, ni)
            self.tabla.setItem(row, 2, QTableWidgetItem(m.categoria or ""))
            self.tabla.setItem(row, 3, QTableWidgetItem(m.unidad or "unidad"))
            si = QTableWidgetItem(str(m.cantidad_actual))
            si.setForeground(QColor("#E74C3C") if m.stock_bajo else QColor("#27AE60"))
            if m.stock_bajo:
                si.setFont(QFont("", -1, QFont.Bold))
            self.tabla.setItem(row, 4, si)
            self.tabla.setItem(row, 5, QTableWidgetItem(str(m.stock_minimo)))
            ei = QTableWidgetItem("⚠️ BAJO" if m.stock_bajo else "✓ OK")
            ei.setForeground(QColor("#E74C3C") if m.stock_bajo else QColor("#27AE60"))
            ei.setFont(QFont("", -1, QFont.Bold))
            self.tabla.setItem(row, 6, ei)
            spin = QDoubleSpinBox()
            spin.setMinimum(0); spin.setMaximum(99999); spin.setDecimals(2); spin.setSingleStep(1)
            spin.setValue(self._pedido.get(m.id, 0))
            spin.setSpecialValueText("0")
            spin.setStyleSheet("QDoubleSpinBox { border: 1px solid #AED6F1; border-radius: 4px; padding: 2px 6px; }")
            spin.valueChanged.connect(lambda val, mid=m.id: self._on_cantidad(mid, val))
            self.tabla.setCellWidget(row, 7, spin)
        self.tabla.resizeRowsToContents()
        self.tabla.setUpdatesEnabled(True)

    def _programar_filtro(self, texto):
        self._filtro_pendiente = (texto or "").lower().strip()
        self._timer_busqueda.start()

    def _aplicar_filtro_pendiente(self):
        self._filtrar_tabla(self._filtro_pendiente)

    def _filtrar_tabla(self, texto):
        texto = (texto or "").lower().strip()
        if not texto:
            filtrados = self._materiales_db
        else:
            filtrados = [
                m for m in self._materiales_db
                if texto in self._indice_busqueda.get(m.id, "")
            ]
        self.banner.setVisible(bool(texto) and not filtrados)
        self._poblar_tabla(filtrados)

    def _on_cantidad(self, mid, val):
        if val > 0:
            self._pedido[mid] = val
        else:
            self._pedido.pop(mid, None)
        self._actualizar_resumen()

    # ─── Material externo ─────────────────────────────────────────────────────
    def _agregar_externo(self):
        nombre_sug = self.input_buscar.text().strip()
        dlg = MaterialNoEncontradoDialog(nombre_sug, self)
        if dlg.exec() != QDialog.Accepted or not dlg.result_data:
            return
        data = dlg.result_data
        if dlg.guardar_en_bd:
            db = SessionLocal()
            try:
                nuevo = InventarioService(db).crear(
                    nombre_material=data["nombre"],
                    categoria=data["categoria"],
                    unidad=data["unidad"],
                    cantidad_actual=0.0,
                    stock_minimo=data.get("stock_min", 0.0),
                    ubicacion=data.get("ubicacion", ""),
                    proveedor_id=None,
                )
                self._pedido[nuevo.id] = data["cantidad"]
                self._materiales_db = InventarioService(db).listar()
                self._reconstruir_indice_busqueda()
                self._poblar_tabla(self._materiales_db)
                self._filtrar_tabla(self.input_buscar.text())
                QMessageBox.information(self, "Guardado en inventario",
                    f"'{data['nombre']}' fue guardado con stock 0 y agregado al pedido.\n"
                    "Aparecerá en la lista de materiales a comprar.")
            except Exception as e:
                QMessageBox.warning(self, "Error al guardar", str(e))
            finally:
                db.close()
        else:
            key = f"ext_{id(data)}"
            self._extras[key] = data
            self._refrescar_extras()
            QMessageBox.information(self, "Agregado al pedido",
                f"'{data['nombre']}' fue agregado al pedido como material a comprar.")
        self._actualizar_resumen()

    def _refrescar_extras(self):
        self.tabla_extras.setRowCount(0)
        for key, d in self._extras.items():
            row = self.tabla_extras.rowCount()
            self.tabla_extras.insertRow(row)
            self.tabla_extras.setItem(row, 0, QTableWidgetItem(d["nombre"]))
            self.tabla_extras.setItem(row, 1, QTableWidgetItem(d.get("categoria", "—")))
            self.tabla_extras.setItem(row, 2, QTableWidgetItem(d["unidad"]))
            self.tabla_extras.setItem(row, 3, QTableWidgetItem(str(d["cantidad"])))
            btn = QPushButton("✕  Quitar")
            btn.setStyleSheet("QPushButton { background: #E74C3C; color: white; border-radius: 3px; font-size: 11px; padding: 2px 8px; } QPushButton:hover { background: #C0392B; }")
            btn.clicked.connect(lambda _, k=key: self._quitar_extra(k))
            self.tabla_extras.setCellWidget(row, 4, btn)
        self.seccion_ext.setVisible(bool(self._extras))

    def _quitar_extra(self, key):
        self._extras.pop(key, None)
        self._refrescar_extras()
        self._actualizar_resumen()

    # ─── Resumen ─────────────────────────────────────────────────────────────
    def _actualizar_resumen(self):
        disp, comp = self._calcular_items()
        total = len(self._pedido) + len(self._extras)
        self.lbl_total.setText(f"📋 En pedido: {total}")
        self.lbl_disp.setText(f"✅ En stock: {len(disp)}")
        self.lbl_comp.setText(f"🛒 A comprar: {len(comp)}")

    def _calcular_items(self):
        mat_map = {m.id: m for m in self._materiales_db}
        disp, comp = [], []
        for mid, cant in self._pedido.items():
            m = mat_map.get(mid)
            if not m:
                continue
            if m.cantidad_actual >= cant:
                disp.append({"nombre": m.nombre_material, "unidad": m.unidad or "unidad",
                              "solicitado": cant, "disponible": m.cantidad_actual})
            else:
                comp.append({"nombre": m.nombre_material, "unidad": m.unidad or "unidad",
                              "solicitado": cant, "disponible": m.cantidad_actual,
                              "faltante": round(cant - m.cantidad_actual, 2)})
        for d in self._extras.values():
            comp.append({"nombre": d["nombre"], "unidad": d["unidad"],
                         "solicitado": d["cantidad"], "disponible": 0, "faltante": d["cantidad"]})
        return disp, comp

    def _limpiar_pedido(self):
        self._pedido.clear()
        self._extras.clear()
        self._refrescar_extras()
        self._poblar_tabla(self._materiales_db)
        self._actualizar_resumen()
        self.input_buscar.clear()

    def _ver_preview(self):
        disp, comp = self._calcular_items()
        if not disp and not comp:
            QMessageBox.information(self, "Pedido vacío", "Agrega cantidades a los materiales.")
            return
        PreviewPedidoDialog(disp, comp, self).exec()

    def _generar_reporte(self):
        disp, comp = self._calcular_items()
        if not disp and not comp:
            QMessageBox.information(self, "Pedido vacío", "Agrega cantidades a los materiales.")
            return
        solicitante = self.input_solicitante.text().strip()
        if not solicitante:
            QMessageBox.warning(self, "Validación", "Ingresa el nombre del solicitante.")
            return
        pnombre = self.combo_proyecto.currentText()
        if pnombre == "— Sin proyecto —":
            pnombre = "Sin Proyecto"
        obs = self.input_obs.toPlainText().strip()
        try:
            from app.reports.acta_pdf import generar_reporte_pedido_pdf
            ruta = generar_reporte_pedido_pdf(
                nombre_solicitante=solicitante, proyecto_nombre=pnombre,
                items_disponibles=disp, items_comprar=comp,
                observaciones=obs,
            )
            # Registrar el pedido en la base de datos
            from app.core.database import SessionLocal
            from app.services.services import PedidoCompraService
            db = SessionLocal()
            try:
                PedidoCompraService(db).registrar(
                    solicitante=solicitante,
                    proyecto_nombre=pnombre,
                    observaciones=obs,
                    ruta_pdf=ruta,
                    items_disponibles=disp,
                    items_comprar=comp,
                )
            except Exception:
                pass
            finally:
                db.close()

            resp = QMessageBox.question(self, "Pedido registrado",
                f"Pedido guardado y PDF generado:\n{ruta}\n\n¿Deseas abrir el acta?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if resp == QMessageBox.Yes:
                self._abrir(ruta)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _abrir(self, ruta):
        try:
            open_file(ruta)
        except Exception:
            pass


# ─── Vista previa ─────────────────────────────────────────────────────────────
class PreviewPedidoDialog(QDialog):
    def __init__(self, disp, comp, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vista Previa del Pedido")
        self.setMinimumSize(700, 480)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        titulo = QLabel("📋  Resumen del Pedido")
        titulo.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E3A5F;")
        layout.addWidget(titulo)

        rl = QHBoxLayout()
        for txt, col, val in [("✅ En stock", "#27AE60", len(disp)), ("🛒 A comprar", "#E74C3C", len(comp))]:
            card = QFrame()
            card.setStyleSheet(f"QFrame {{ background: {col}; border-radius: 8px; }}")
            cl = QVBoxLayout(card); cl.setContentsMargins(16, 10, 16, 10)
            l1 = QLabel(str(val)); l1.setStyleSheet("font-size: 26px; font-weight: bold; color: white;"); l1.setAlignment(Qt.AlignCenter)
            l2 = QLabel(txt); l2.setStyleSheet("font-size: 12px; color: white;"); l2.setAlignment(Qt.AlignCenter)
            cl.addWidget(l1); cl.addWidget(l2)
            rl.addWidget(card)
        layout.addLayout(rl)

        if disp:
            layout.addWidget(QLabel("Materiales disponibles:"))
            layout.addWidget(self._tabla(disp, False))
        if comp:
            layout.addWidget(QLabel("Materiales a comprar:"))
            layout.addWidget(self._tabla(comp, True))

        btn = QPushButton("Cerrar"); btn.setObjectName("btn_secondary"); btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def _tabla(self, items, faltante):
        hdrs = ["Material", "Unidad", "Solicitado", "En Stock"] + (["A Comprar"] if faltante else [])
        t = QTableWidget(len(items), len(hdrs))
        t.setHorizontalHeaderLabels(hdrs)
        configurar_tabla(t, col_stretch=0)
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setAlternatingRowColors(True)
        t.verticalHeader().setVisible(False)
        t.setMaximumHeight(160)
        for r, it in enumerate(items):
            t.setItem(r, 0, QTableWidgetItem(it["nombre"]))
            t.setItem(r, 1, QTableWidgetItem(it["unidad"]))
            t.setItem(r, 2, QTableWidgetItem(str(it["solicitado"])))
            t.setItem(r, 3, QTableWidgetItem(str(it["disponible"])))
            if faltante:
                fi = QTableWidgetItem(str(it["faltante"]))
                fi.setForeground(QColor("#E74C3C")); fi.setFont(QFont("", -1, QFont.Bold))
                t.setItem(r, 4, fi)
        return t
