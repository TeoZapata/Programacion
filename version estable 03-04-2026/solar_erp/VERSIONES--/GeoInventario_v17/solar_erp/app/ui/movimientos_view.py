from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QComboBox, QDateEdit, QLineEdit, QTextEdit,
    QDoubleSpinBox, QMessageBox, QTabWidget, QFrame, QScrollArea,
    QAbstractItemView, QListWidget, QListWidgetItem, QSizePolicy
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QColor, QFont
from app.core.database import SessionLocal
from app.ui.table_helpers import configurar_tabla, btn_acta_movimiento, normalizar
from app.services.services import (
    MovimientoService, InventarioService, ProyectoService,
    ProveedorService, TrabajadorService
)
import os
import subprocess
import platform


class MovimientosView(QWidget):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario
        self._build_ui()
        self._cargar_tabla()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(16)

        titulo = QLabel("🔄  Movimientos de Inventario")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #1E3A5F;")
        layout.addWidget(titulo)

        # Botones de acción
        btns_layout = QHBoxLayout()
        btns_layout.setSpacing(10)

        btn_entrada = QPushButton("⬆️  Registrar Entrada")
        btn_entrada.setObjectName("btn_success")
        btn_entrada.setMinimumHeight(40)
        btn_entrada.clicked.connect(self._nueva_entrada)
        btns_layout.addWidget(btn_entrada)

        btn_salida = QPushButton("⬇️  Registrar Salida")
        btn_salida.setObjectName("btn_primary")
        btn_salida.setMinimumHeight(40)
        btn_salida.clicked.connect(self._nueva_salida)
        btns_layout.addWidget(btn_salida)

        btn_devolucion = QPushButton("↩️  Registrar Devolución")
        btn_devolucion.setObjectName("btn_warning")
        btn_devolucion.setMinimumHeight(40)
        btn_devolucion.clicked.connect(self._nueva_devolucion)
        btns_layout.addWidget(btn_devolucion)

        btns_layout.addStretch()

        btn_refrescar = QPushButton("↻  Refrescar")
        btn_refrescar.setObjectName("btn_secondary")
        btn_refrescar.clicked.connect(self._cargar_tabla)
        btns_layout.addWidget(btn_refrescar)

        layout.addLayout(btns_layout)

        # Tabla
        cols = ["ID", "Tipo", "Proyecto / Proveedor", "Responsable", "Fecha", "Factura", "Materiales", "Acciones"]
        self.tabla = QTableWidget(0, len(cols))
        self.tabla.setHorizontalHeaderLabels(cols)
        configurar_tabla(self.tabla, col_stretch=1,
                         cols_fijas=[(0,90),(2,130),(3,110),(4,90),(5,100),(6,110),(7,105)])
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        layout.addWidget(self.tabla)

        self.lbl_total = QLabel("Total: 0 registros")
        self.lbl_total.setStyleSheet("color: #7F8C8D; font-size: 12px;")
        layout.addWidget(self.lbl_total)

    def _cargar_tabla(self):
        db = SessionLocal()
        movimientos = MovimientoService(db).ultimos(100)
        db.close()

        self.tabla.setRowCount(0)
        iconos = {"entrada": "⬆️", "salida": "⬇️", "devolucion": "↩️"}
        colores = {"entrada": "#2ECC71", "salida": "#1E3A5F", "devolucion": "#F39C12"}

        for mv in movimientos:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(str(mv.id)))

            tipo_item = QTableWidgetItem(f"{iconos.get(mv.tipo, '')}  {mv.tipo.capitalize()}")
            tipo_item.setForeground(QColor(colores.get(mv.tipo, "#2C3E50")))
            tipo_item.setFont(QFont("", -1, QFont.Bold))
            self.tabla.setItem(row, 1, tipo_item)

            ref = mv.proyecto.nombre_proyecto if mv.proyecto else (mv.proveedor.nombre if mv.proveedor else "—")
            self.tabla.setItem(row, 2, QTableWidgetItem(ref))
            self.tabla.setItem(row, 3, QTableWidgetItem(mv.responsable or "—"))
            self.tabla.setItem(row, 4, QTableWidgetItem(str(mv.fecha)))
            self.tabla.setItem(row, 5, QTableWidgetItem(mv.factura or "—"))
            n_items = len(mv.detalles)
            self.tabla.setItem(row, 6, QTableWidgetItem(f"{n_items} material(es)"))

            # Botón generar acta PDF (entrada, salida y devolución)
            if mv.tipo in ("entrada", "salida", "devolucion"):
                tipo_label = {"entrada": "Entrada", "salida": "Salida", "devolucion": "Devolución"}.get(mv.tipo, mv.tipo)
                btn_acta = btn_acta_movimiento(f"Ver acta de {tipo_label} — {mv.fecha}")
                btn_acta.clicked.connect(lambda _, m=mv: self._generar_acta(m))
                self.tabla.setCellWidget(row, 7, btn_acta)

        self.lbl_total.setText(f"Total: {self.tabla.rowCount()} registros")

    def _nueva_entrada(self):
        dlg = EntradaDialog(self, usuario=self.usuario)
        if dlg.exec():
            self._cargar_tabla()

    def _nueva_salida(self):
        dlg = SalidaDialog(self, usuario=self.usuario)
        if dlg.exec():
            self._cargar_tabla()

    def _nueva_devolucion(self):
        dlg = DevolucionDialog(self, usuario=self.usuario)
        if dlg.exec():
            self._cargar_tabla()

    def _generar_acta(self, movimiento):
        db = SessionLocal()
        try:
            if movimiento.tipo == "entrada":
                from app.reports.acta_pdf import generar_acta_entrada_pdf
                ruta = generar_acta_entrada_pdf(
                    movimiento=movimiento,
                    proveedor=movimiento.proveedor,
                    detalles=movimiento.detalles,
                    responsable=movimiento.responsable,
                )
            elif movimiento.tipo == "salida":
                from app.reports.acta_pdf import generar_acta_salida_pdf
                ruta = generar_acta_salida_pdf(
                    movimiento=movimiento,
                    proyecto=movimiento.proyecto,
                    cliente=movimiento.proyecto.cliente if movimiento.proyecto else None,
                    detalles=movimiento.detalles,
                    responsable=movimiento.responsable,
                )
            else:  # devolucion
                from app.reports.acta_pdf import generar_acta_devolucion_pdf
                ruta = generar_acta_devolucion_pdf(
                    movimiento=movimiento,
                    proyecto=movimiento.proyecto,
                    cliente=movimiento.proyecto.cliente if movimiento.proyecto else None,
                    detalles=movimiento.detalles,
                    responsable=movimiento.responsable,
                )
            resp = QMessageBox.question(
                self, "Acta PDF generada",
                f"Acta generada exitosamente:\n{ruta}\n\n¿Deseas abrirla?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes,
            )
            if resp == QMessageBox.Yes:
                self._abrir_archivo(ruta)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo generar el acta: {e}")
        finally:
            db.close()

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


class ItemsMovimientoWidget(QWidget):
    """Widget reutilizable para agregar ítems de material al movimiento — con buscador."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mat_seleccionado = None   # objeto Material seleccionado
        self._build_ui()
        self._cargar_materiales()

    def _cargar_materiales(self):
        """Carga/recarga TODOS los materiales desde la BD sin límite."""
        from app.models.inventario import Material as _Mat
        db = SessionLocal()
        try:
            materiales = (db.query(_Mat)
                          .order_by(_Mat.nombre_material)
                          .all())
            self.materiales_map  = {m.id: m for m in materiales}
            self.materiales_list = materiales
        finally:
            db.close()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # ── Fila buscador ─────────────────────────────────────────────────────
        busq_row = QHBoxLayout()
        busq_row.setSpacing(8)

        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("🔍  Buscar material por nombre o categoría...")
        self.input_buscar.setMinimumWidth(280)
        self.input_buscar.setStyleSheet(
            "QLineEdit { border: 1px solid #DDE2E8; border-radius: 6px; padding: 6px 10px; font-size: 12px; }"
            "QLineEdit:focus { border: 2px solid #2ECC71; }")
        self.input_buscar.textChanged.connect(self._filtrar_lista)
        busq_row.addWidget(self.input_buscar)

        self.lbl_sel = QLabel("Ningún material seleccionado")
        self.lbl_sel.setStyleSheet(
            "color: #7F8C8D; font-size: 11px; padding: 4px 8px;"
            "background: #F5F6FA; border-radius: 4px; min-width: 180px;")
        busq_row.addWidget(self.lbl_sel)

        btn_refrescar = QPushButton("↻ Actualizar")
        btn_refrescar.setObjectName("btn_secondary")
        btn_refrescar.setToolTip("Recargar lista de materiales desde la base de datos")
        btn_refrescar.setFixedHeight(34)
        btn_refrescar.clicked.connect(self._refrescar_materiales)
        busq_row.addWidget(btn_refrescar)

        btn_nuevo_mat = QPushButton("＋ Nuevo Material")
        btn_nuevo_mat.setObjectName("btn_warning")
        btn_nuevo_mat.setToolTip("Agregar un material nuevo al inventario sin salir de este diálogo")
        btn_nuevo_mat.setFixedHeight(34)
        btn_nuevo_mat.clicked.connect(self._agregar_material_rapido)
        busq_row.addWidget(btn_nuevo_mat)

        layout.addLayout(busq_row)

        # ── Lista de resultados de búsqueda ────────────────────────────────
        self.lista_resultados = QListWidget()
        self.lista_resultados.setMaximumHeight(130)
        self.lista_resultados.setVisible(False)
        self.lista_resultados.setStyleSheet(
            "QListWidget { border: 1px solid #2ECC71; border-radius: 4px; "
            "background: white; font-size: 12px; }"
            "QListWidget::item { padding: 5px 10px; }"
            "QListWidget::item:hover { background: #E8F8F0; }"
            "QListWidget::item:selected { background: #2ECC71; color: white; font-weight: bold; }")
        self.lista_resultados.itemClicked.connect(self._seleccionar_material)
        layout.addWidget(self.lista_resultados)

        # ── Fila cantidad + precio + agregar ──────────────────────────────
        add_row = QHBoxLayout()
        add_row.setSpacing(8)

        lbl_cant = QLabel("Cant.:")
        lbl_cant.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        add_row.addWidget(lbl_cant)

        self.spin_cant = QDoubleSpinBox()
        self.spin_cant.setRange(0.01, 99999)
        self.spin_cant.setDecimals(2)
        self.spin_cant.setValue(1)
        self.spin_cant.setFixedWidth(100)
        self.spin_cant.setToolTip("Cantidad a agregar al movimiento")
        self.spin_cant.valueChanged.connect(self._actualizar_subtotal)
        add_row.addWidget(self.spin_cant)

        lbl_precio = QLabel("Precio unit.:")
        lbl_precio.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        add_row.addWidget(lbl_precio)

        self.spin_precio = QDoubleSpinBox()
        self.spin_precio.setRange(0, 999_999_999)
        self.spin_precio.setDecimals(2)
        self.spin_precio.setPrefix("$ ")
        self.spin_precio.setFixedWidth(150)
        self.spin_precio.setToolTip("Precio unitario (se auto-rellena del inventario)")
        self.spin_precio.valueChanged.connect(self._actualizar_subtotal)
        add_row.addWidget(self.spin_precio)

        self.lbl_subtotal = QLabel("= $ 0.00")
        self.lbl_subtotal.setStyleSheet("color: #1E3A5F; font-weight: bold; min-width: 110px;")
        add_row.addWidget(self.lbl_subtotal)

        add_row.addStretch()

        self.btn_add = QPushButton("＋ Agregar a lista")
        self.btn_add.setObjectName("btn_success")
        self.btn_add.setEnabled(False)
        self.btn_add.clicked.connect(self._agregar_item)
        add_row.addWidget(self.btn_add)

        layout.addLayout(add_row)

        # ── Tabla de ítems ─────────────────────────────────────────────────
        self.tabla_items = QTableWidget(0, 5)
        self.tabla_items.setHorizontalHeaderLabels(
            ["Material", "Cantidad", "Precio Unit.", "Valor Total", ""])
        configurar_tabla(self.tabla_items, col_stretch=0,
                         cols_fijas=[(1, 90), (2, 120), (3, 120), (4, 36)])
        self.tabla_items.setMaximumHeight(210)
        self.tabla_items.verticalHeader().setVisible(False)
        self.tabla_items.setStyleSheet("QTableWidget { border: 1px solid #DDE2E8; }")
        layout.addWidget(self.tabla_items)

        # ── Total general ──────────────────────────────────────────────────
        total_row = QHBoxLayout()
        total_row.addStretch()
        self.lbl_total = QLabel("Total: $ 0.00")
        self.lbl_total.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #1E3A5F; padding: 4px 8px;"
            "background: #EBF5FB; border-radius: 6px;")
        total_row.addWidget(self.lbl_total)
        layout.addLayout(total_row)

    # ── Búsqueda ───────────────────────────────────────────────────────────
    def _filtrar_lista(self, texto):
        self.lista_resultados.clear()
        texto = texto.strip()
        if not texto:
            self.lista_resultados.setVisible(False)
            return

        # Buscar en BD completa (ilike cubre mayúsculas/minúsculas)
        from app.models.inventario import Material as _Mat
        from sqlalchemy import or_
        db = SessionLocal()
        try:
            patron = f"%{texto}%"
            resultados_bd = (db.query(_Mat)
                             .filter(or_(
                                 _Mat.nombre_material.ilike(patron),
                                 _Mat.categoria.ilike(patron),
                                 _Mat.ubicacion.ilike(patron),
                             ))
                             .order_by(_Mat.nombre_material)
                             .limit(50)
                             .all())
            # Búsqueda adicional normalizada (sin tildes) sobre lista en memoria
            texto_norm = normalizar(texto)
            resultados_norm = [
                m for m in self.materiales_list
                if texto_norm in normalizar(m.nombre_material)
                or texto_norm in normalizar(m.categoria or "")
            ]
            # Unir ambos resultados sin duplicados
            ids_bd = {m.id for m in resultados_bd}
            resultados = resultados_bd + [m for m in resultados_norm if m.id not in ids_bd]
            resultados = sorted(resultados, key=lambda m: m.nombre_material)[:30]
            # Actualizar mapa local
            for m in resultados:
                self.materiales_map[m.id] = m
        finally:
            db.close()

        if resultados:
            for m in resultados:
                stock_txt = f"{m.cantidad_actual or 0:g} {m.unidad or ''}"
                item = QListWidgetItem(
                    f"{m.nombre_material}  —  Stock: {stock_txt}  |  $ {m.precio_unitario or 0:,.0f}")
                item.setData(Qt.UserRole, m.id)
                if (m.cantidad_actual or 0) <= 0:
                    item.setForeground(QColor("#E74C3C"))
                elif (m.cantidad_actual or 0) <= (m.stock_minimo or 0):
                    item.setForeground(QColor("#F39C12"))
                self.lista_resultados.addItem(item)
            self.lista_resultados.setVisible(True)
        else:
            item_vacio = QListWidgetItem("  Sin resultados — usa '＋ Nuevo Material' para agregar")
            item_vacio.setForeground(QColor("#7F8C8D"))
            item_vacio.setFlags(Qt.NoItemFlags)
            self.lista_resultados.addItem(item_vacio)
            self.lista_resultados.setVisible(True)

    def _seleccionar_material(self, item):
        mat_id = item.data(Qt.UserRole)
        if not mat_id:
            return
        mat = self.materiales_map.get(mat_id)
        if not mat:
            return
        self._mat_seleccionado = mat
        self.input_buscar.setText(mat.nombre_material)
        self.lista_resultados.setVisible(False)
        self.lbl_sel.setText(f"✓ {mat.nombre_material}")
        self.lbl_sel.setStyleSheet(
            "color: #27AE60; font-size: 11px; font-weight: bold; padding: 4px 8px;"
            "background: #E8F8F0; border-radius: 4px; min-width: 180px;")
        # Auto-rellenar precio
        if mat.precio_unitario:
            self.spin_precio.setValue(mat.precio_unitario)
        self.btn_add.setEnabled(True)
        self._actualizar_subtotal()

    def _refrescar_materiales(self):
        """Recarga los materiales desde BD y limpia la búsqueda."""
        self._cargar_materiales()
        self.input_buscar.clear()
        self.lista_resultados.setVisible(False)
        self._mat_seleccionado = None
        self.btn_add.setEnabled(False)
        self.lbl_sel.setText("Materiales actualizados ✓")
        self.lbl_sel.setStyleSheet(
            "color: #27AE60; font-size: 11px; padding: 4px 8px;"
            "background: #E8F8F0; border-radius: 4px; min-width: 180px;")
        QTimer.singleShot(2000, lambda: self.lbl_sel.setText("Ningún material seleccionado") or
            self.lbl_sel.setStyleSheet(
                "color: #7F8C8D; font-size: 11px; padding: 4px 8px;"
                "background: #F5F6FA; border-radius: 4px; min-width: 180px;"))

    def _agregar_material_rapido(self):
        """Abre un mini-diálogo para crear un material nuevo sin cerrar el movimiento."""
        from PySide6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        from app.core.config import CATEGORIAS_INVENTARIO
        dlg = QDialog(self)
        dlg.setWindowTitle("Nuevo Material Rápido")
        dlg.setMinimumWidth(380)
        form = QFormLayout(dlg)
        inp_nombre = QLineEdit()
        inp_nombre.setPlaceholderText("Nombre del material")
        cmb_cat = QComboBox()
        for cat in CATEGORIAS_INVENTARIO:
            cmb_cat.addItem(cat)
        inp_unidad = QLineEdit("unidad")
        spin_stock = QDoubleSpinBox()
        spin_stock.setRange(0, 999999); spin_stock.setValue(0)
        spin_precio = QDoubleSpinBox()
        spin_precio.setRange(0, 999999999); spin_precio.setPrefix("$ ")
        form.addRow("Nombre *:", inp_nombre)
        form.addRow("Categoría:", cmb_cat)
        form.addRow("Unidad:", inp_unidad)
        form.addRow("Stock inicial:", spin_stock)
        form.addRow("Precio unitario:", spin_precio)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        form.addRow(btns)
        if dlg.exec():
            nombre = inp_nombre.text().strip()
            if not nombre:
                QMessageBox.warning(self, "Campo requerido", "El nombre del material es obligatorio.")
                return
            db = SessionLocal()
            try:
                mat = InventarioService(db).crear(
                    nombre_material=nombre,
                    categoria=cmb_cat.currentText(),
                    unidad=inp_unidad.text().strip() or "unidad",
                    cantidad_actual=spin_stock.value(),
                    stock_minimo=0,
                    ubicacion="",
                    proveedor_id=None,
                    precio_unitario=spin_precio.value(),
                )
                QMessageBox.information(self, "Material creado",
                    f"✓ '{nombre}' agregado al inventario.")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
            finally:
                db.close()
            self._refrescar_materiales()
            # Pre-seleccionar el material recién creado
            self.input_buscar.setText(nombre)
            self._filtrar_lista(nombre)

    # ── Lógica ítems ──────────────────────────────────────────────────────
    def _actualizar_subtotal(self):
        sub = self.spin_cant.value() * self.spin_precio.value()
        self.lbl_subtotal.setText(f"= $ {sub:,.2f}")

    def _recalcular_total(self):
        total = 0.0
        for row in range(self.tabla_items.rowCount()):
            item = self.tabla_items.item(row, 3)
            if item:
                try:
                    total += float(item.data(256))
                except Exception:
                    pass
        self.lbl_total.setText(f"Total: $ {total:,.2f}")

    def _agregar_item(self):
        mat      = self._mat_seleccionado
        cantidad = self.spin_cant.value()
        precio   = self.spin_precio.value()
        if not mat:
            return
        valor = round(cantidad * precio, 2)

        row = self.tabla_items.rowCount()
        self.tabla_items.insertRow(row)
        nom_item = QTableWidgetItem(mat.nombre_material)
        nom_item.setData(Qt.UserRole, mat.id)
        self.tabla_items.setItem(row, 0, nom_item)
        self.tabla_items.setItem(row, 1, QTableWidgetItem(str(cantidad)))
        pu_item = QTableWidgetItem(f"$ {precio:,.2f}")
        pu_item.setForeground(QColor("#1E3A5F"))
        self.tabla_items.setItem(row, 2, pu_item)
        vt_item = QTableWidgetItem(f"$ {valor:,.2f}")
        vt_item.setForeground(QColor("#27AE60"))
        vt_item.setFont(QFont("", -1, QFont.Bold))
        vt_item.setData(256, valor)
        self.tabla_items.setItem(row, 3, vt_item)

        btn_rem = QPushButton("✕")
        btn_rem.setObjectName("btn_danger")
        btn_rem.setFixedSize(28, 28)
        btn_rem.clicked.connect(lambda _, r=row: self._quitar_item(r))
        self.tabla_items.setCellWidget(row, 4, btn_rem)
        self._recalcular_total()

        # Limpiar selección para facilitar agregar otro
        self.input_buscar.clear()
        self.lista_resultados.setVisible(False)
        self._mat_seleccionado = None
        self.btn_add.setEnabled(False)
        self.lbl_sel.setText("Ningún material seleccionado")
        self.lbl_sel.setStyleSheet(
            "color: #7F8C8D; font-size: 11px; padding: 4px 8px;"
            "background: #F5F6FA; border-radius: 4px; min-width: 180px;")
        self.spin_cant.setValue(1)

    def _quitar_item(self, row):
        self.tabla_items.removeRow(row)
        self._recalcular_total()

    def get_items(self):
        """Retorna lista de (mat_id, cantidad, precio_unitario)."""
        items = []
        for row in range(self.tabla_items.rowCount()):
            mat_id   = self.tabla_items.item(row, 0).data(Qt.UserRole)
            cantidad = float(self.tabla_items.item(row, 1).text())
            precio_txt = self.tabla_items.item(row, 2).text().replace("$", "").replace(",", "").strip()
            precio   = float(precio_txt)
            if mat_id:
                items.append((mat_id, cantidad, precio))
        return items


class EntradaDialog(QDialog):
    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.usuario = usuario
        self.setWindowTitle("Registrar Entrada de Material")
        self.setMinimumWidth(600)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        titulo = QLabel("⬆️  Entrada de Material")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #2ECC71;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)

        self.combo_proveedor = QComboBox()
        db = SessionLocal()
        proveedores = ProveedorService(db).listar()
        db.close()
        self.combo_proveedor.addItem("Seleccionar proveedor...", None)
        for p in proveedores:
            self.combo_proveedor.addItem(p.nombre, p.id)
        form.addRow("Proveedor *", self.combo_proveedor)

        self.input_factura = QLineEdit(); self.input_factura.setPlaceholderText("Nro. de factura")
        form.addRow("Factura", self.input_factura)

        self.date_mov = QDateEdit(QDate.currentDate())
        self.date_mov.setCalendarPopup(True)
        self.date_mov.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Fecha", self.date_mov)

        self.input_resp = QLineEdit()
        self.input_resp.setText(self.usuario.nombre if self.usuario else "")
        form.addRow("Responsable", self.input_resp)

        self.input_obs = QLineEdit(); self.input_obs.setPlaceholderText("Observaciones (opcional)")
        form.addRow("Observaciones", self.input_obs)
        layout.addLayout(form)

        lbl_mat = QLabel("Materiales a ingresar")
        lbl_mat.setStyleSheet("font-weight: bold; color: #2C3E50;")
        layout.addWidget(lbl_mat)

        self.items_widget = ItemsMovimientoWidget()
        layout.addWidget(self.items_widget)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar"); btn_cancelar.setObjectName("btn_secondary")
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_guardar = QPushButton("💾  Registrar Entrada"); btn_guardar.setObjectName("btn_success")
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)
        layout.addLayout(btns)

    def _guardar(self):
        proveedor_id = self.combo_proveedor.currentData()
        items = self.items_widget.get_items()
        if not items:
            QMessageBox.warning(self, "Validación", "Agrega al menos un material.")
            return
        db = SessionLocal()
        try:
            mov = MovimientoService(db).registrar_entrada(
                proveedor_id=proveedor_id,
                factura=self.input_factura.text().strip(),
                fecha=self.date_mov.date().toPython(),
                responsable=self.input_resp.text().strip(),
                observaciones=self.input_obs.text().strip(),
                items=[(i[0], i[1], i[2]) for i in items],
            )
            # Generar acta PDF automáticamente
            try:
                from app.reports.acta_pdf import generar_acta_entrada_pdf
                ruta = generar_acta_entrada_pdf(
                    movimiento=mov,
                    proveedor=mov.proveedor,
                    detalles=mov.detalles,
                    responsable=mov.responsable,
                )
                resp = QMessageBox.question(
                    self, "Entrada registrada",
                    f"Entrada registrada correctamente.\nActa PDF generada:\n{ruta}\n\n¿Deseas abrirla?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes,
                )
                if resp == QMessageBox.Yes:
                    import os, subprocess, platform
                    if platform.system() == "Windows":
                        os.startfile(ruta)
                    elif platform.system() == "Darwin":
                        subprocess.call(["open", ruta])
                    else:
                        subprocess.call(["xdg-open", ruta])
            except Exception as e_pdf:
                QMessageBox.information(self, "Entrada registrada",
                    f"Entrada registrada correctamente.\nNo se pudo generar el acta PDF: {e_pdf}")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            db.close()


class SalidaDialog(QDialog):
    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.usuario = usuario
        self.setWindowTitle("Registrar Salida de Material")
        self.setMinimumWidth(600)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        titulo = QLabel("⬇️  Salida de Material por Proyecto")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A5F;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)

        self.combo_proyecto = QComboBox()
        db = SessionLocal()
        proyectos = ProyectoService(db).listar()
        db.close()
        self.combo_proyecto.addItem("Seleccionar proyecto...", None)
        for p in proyectos:
            self.combo_proyecto.addItem(f"{p.nombre_proyecto} — {p.cliente.nombre if p.cliente else ''}", p.id)
        form.addRow("Proyecto *", self.combo_proyecto)

        self.date_mov = QDateEdit(QDate.currentDate())
        self.date_mov.setCalendarPopup(True)
        self.date_mov.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Fecha", self.date_mov)

        self.input_resp = QLineEdit()
        self.input_resp.setText(self.usuario.nombre if self.usuario else "")
        form.addRow("Responsable", self.input_resp)

        self.input_obs = QLineEdit(); self.input_obs.setPlaceholderText("Observaciones (opcional)")
        form.addRow("Observaciones", self.input_obs)
        layout.addLayout(form)

        lbl_mat = QLabel("Materiales a entregar")
        lbl_mat.setStyleSheet("font-weight: bold; color: #2C3E50;")
        layout.addWidget(lbl_mat)

        self.items_widget = ItemsMovimientoWidget()
        self.items_widget.spin_precio.setVisible(False)
        layout.addWidget(self.items_widget)

        lbl_acta = QLabel("💡 Se generará un Acta de Entrega de Materiales en Word")
        lbl_acta.setStyleSheet("color: #7F8C8D; font-size: 12px; font-style: italic;")
        layout.addWidget(lbl_acta)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar"); btn_cancelar.setObjectName("btn_secondary")
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_guardar = QPushButton("💾  Registrar Salida + Generar Acta"); btn_guardar.setObjectName("btn_primary")
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)
        layout.addLayout(btns)

    def _guardar(self):
        proyecto_id = self.combo_proyecto.currentData()
        items = self.items_widget.get_items()
        if not proyecto_id:
            QMessageBox.warning(self, "Validación", "Selecciona un proyecto.")
            return
        if not items:
            QMessageBox.warning(self, "Validación", "Agrega al menos un material.")
            return
        db = SessionLocal()
        try:
            svc = MovimientoService(db)
            mov = svc.registrar_salida(
                proyecto_id=proyecto_id,
                fecha=self.date_mov.date().toPython(),
                responsable=self.input_resp.text().strip(),
                observaciones=self.input_obs.text().strip(),
                items=[(i[0], i[1]) for i in items],
            )
            # Generar acta Word
            try:
                from app.reports.acta_materiales import generar_acta_materiales
                mov_completo = svc.repo.get_by_id(mov.id)
                ruta = generar_acta_materiales(
                    movimiento=mov_completo,
                    proyecto=mov_completo.proyecto,
                    cliente=mov_completo.proyecto.cliente if mov_completo.proyecto else None,
                    detalles=mov_completo.detalles,
                    responsable=mov_completo.responsable,
                )
                QMessageBox.information(self, "Éxito",
                    f"Salida registrada y Acta generada:\n{ruta}")
            except Exception as e_doc:
                QMessageBox.information(self, "Salida registrada",
                    f"Salida registrada. No se pudo generar el acta: {e_doc}")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            db.close()


class DevolucionDialog(QDialog):
    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.usuario = usuario
        self.setWindowTitle("Registrar Devolución de Material")
        self.setMinimumWidth(580)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        titulo = QLabel("↩️  Devolución de Material")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #F39C12;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)

        self.combo_proyecto = QComboBox()
        db = SessionLocal()
        proyectos = ProyectoService(db).listar()
        db.close()
        self.combo_proyecto.addItem("Seleccionar proyecto...", None)
        for p in proyectos:
            self.combo_proyecto.addItem(f"{p.nombre_proyecto}", p.id)
        form.addRow("Proyecto", self.combo_proyecto)

        self.date_mov = QDateEdit(QDate.currentDate())
        self.date_mov.setCalendarPopup(True)
        self.date_mov.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Fecha", self.date_mov)

        self.input_resp = QLineEdit()
        self.input_resp.setText(self.usuario.nombre if self.usuario else "")
        form.addRow("Responsable", self.input_resp)

        self.input_obs = QLineEdit(); self.input_obs.setPlaceholderText("Motivo de la devolución")
        form.addRow("Observaciones", self.input_obs)
        layout.addLayout(form)

        lbl_mat = QLabel("Materiales a devolver")
        lbl_mat.setStyleSheet("font-weight: bold; color: #2C3E50;")
        layout.addWidget(lbl_mat)

        self.items_widget = ItemsMovimientoWidget()
        self.items_widget.spin_precio.setVisible(False)
        layout.addWidget(self.items_widget)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar"); btn_cancelar.setObjectName("btn_secondary")
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_guardar = QPushButton("💾  Registrar Devolución"); btn_guardar.setObjectName("btn_warning")
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)
        layout.addLayout(btns)

    def _guardar(self):
        items = self.items_widget.get_items()
        if not items:
            QMessageBox.warning(self, "Validación", "Agrega al menos un material.")
            return
        db = SessionLocal()
        try:
            mov = MovimientoService(db).registrar_devolucion(
                proyecto_id=self.combo_proyecto.currentData(),
                fecha=self.date_mov.date().toPython(),
                responsable=self.input_resp.text().strip(),
                observaciones=self.input_obs.text().strip(),
                items=[(i[0], i[1]) for i in items],
            )
            # Generar acta PDF automáticamente
            try:
                from app.reports.acta_pdf import generar_acta_devolucion_pdf
                ruta = generar_acta_devolucion_pdf(
                    movimiento=mov,
                    proyecto=mov.proyecto,
                    cliente=mov.proyecto.cliente if mov.proyecto else None,
                    detalles=mov.detalles,
                    responsable=mov.responsable,
                )
                resp = QMessageBox.question(
                    self, "Devolución registrada",
                    f"Devolución registrada correctamente.\nActa PDF generada:\n{ruta}\n\n¿Deseas abrirla?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes,
                )
                if resp == QMessageBox.Yes:
                    import os, subprocess, platform
                    if platform.system() == "Windows":
                        os.startfile(ruta)
                    elif platform.system() == "Darwin":
                        subprocess.call(["open", ruta])
                    else:
                        subprocess.call(["xdg-open", ruta])
            except Exception as e_pdf:
                QMessageBox.information(self, "Devolución registrada",
                    f"Devolución registrada correctamente.\nNo se pudo generar el acta PDF: {e_pdf}")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            db.close()
