from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QComboBox, QDoubleSpinBox,
    QMessageBox, QTableWidgetItem, QFrame
)
from PySide6.QtGui import QColor, QFont
from app.ui.base_view import BaseCRUDView
from app.ui.importar_dialog import ImportarMaterialesDialog
from app.core.database import SessionLocal
from app.ui.table_helpers import configurar_tabla, make_item
from app.services.services import InventarioService, ProveedorService
from app.core.config import CATEGORIAS_INVENTARIO


def fmt_cop(valor):
    """Formatea un número como moneda COP."""
    return f"${valor:,.0f}"


class InventarioView(BaseCRUDView):
    titulo = "Inventario de Materiales"
    icono  = "📦"
    placeholder_busqueda = "Buscar material o categoría..."

    def get_columns(self):
        return ["ID", "Material", "Categoría", "Unidad",
                "Stock Actual", "Stock Mín.", "Precio Unit.",
                "Valor Total", "Ubicación", "Estado"]

    def _poblar_tabla(self, materiales):
        self.tabla.setRowCount(0)
        valor_total_inv = 0.0
        for m in materiales:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(str(m.id)))
            self.tabla.setItem(row, 1, QTableWidgetItem(m.nombre_material))
            self.tabla.setItem(row, 2, QTableWidgetItem(m.categoria or ""))
            self.tabla.setItem(row, 3, QTableWidgetItem(m.unidad or "unidad"))

            # Stock
            cant_item = QTableWidgetItem(str(m.cantidad_actual))
            if m.stock_bajo:
                cant_item.setForeground(QColor("#E74C3C"))
                cant_item.setFont(QFont("", -1, QFont.Bold))
            else:
                cant_item.setForeground(QColor("#27AE60"))
            self.tabla.setItem(row, 4, cant_item)
            self.tabla.setItem(row, 5, QTableWidgetItem(str(m.stock_minimo)))

            # Precio unitario
            precio_u = m.precio_unitario or 0.0
            pu_item = QTableWidgetItem(fmt_cop(precio_u))
            pu_item.setForeground(QColor("#1E3A5F"))
            self.tabla.setItem(row, 6, pu_item)

            # Valor total
            vt = m.precio_total
            valor_total_inv += vt
            vt_item = QTableWidgetItem(fmt_cop(vt))
            vt_item.setFont(QFont("", -1, QFont.Bold))
            vt_item.setForeground(QColor("#2ECC71") if vt > 0 else QColor("#95A5A6"))
            self.tabla.setItem(row, 7, vt_item)

            self.tabla.setItem(row, 8, QTableWidgetItem(m.ubicacion or ""))

            estado = "⚠️ BAJO" if m.stock_bajo else "✓ OK"
            estado_item = QTableWidgetItem(estado)
            estado_item.setForeground(QColor("#E74C3C") if m.stock_bajo else QColor("#27AE60"))
            estado_item.setFont(QFont("", -1, QFont.Bold))
            self.tabla.setItem(row, 9, estado_item)

        self.actualizar_contador(self.tabla.rowCount())
        # Mostrar valor total del inventario en el label de conteo
        if hasattr(self, 'lbl_valor_inv'):
            self.lbl_valor_inv.setText(f"Valor total inventario: {fmt_cop(valor_total_inv)}")

    def _agregar_header_extra(self, header_layout):
        """Llamado por BaseCRUDView si existe — agrega label de valor total."""
        pass  # se agrega en cargar_tabla

    def cargar_tabla(self):
        db = SessionLocal()
        try:
            svc = InventarioService(db)
            materiales = svc.listar()
            self._poblar_tabla(materiales)
            # Actualizar label valor
            if hasattr(self, 'lbl_valor_inv'):
                vt = svc.valor_total_inventario()
                self.lbl_valor_inv.setText(f"💰 Valor total: {fmt_cop(vt)}")
        finally:
            db.close()

    def buscar_tabla(self, texto):
        if not texto.strip():
            self.cargar_tabla()
            return
        db = SessionLocal()
        try:
            self._poblar_tabla(InventarioService(db).buscar(texto))
        finally:
            db.close()

    def abrir_dialogo_crear(self):
        MaterialDialog(self).exec()
        self.cargar_tabla()

    def _agregar_botones_extra(self, toolbar):
        btn_importar = QPushButton("📥  Importar Excel")
        btn_importar.setObjectName("btn_warning")
        btn_importar.setToolTip("Importar múltiples materiales desde un archivo Excel (.xlsx)")
        btn_importar.clicked.connect(self._abrir_importacion)
        toolbar.addWidget(btn_importar)

        btn_siigo = QPushButton("📤  Exportar SIIGO")
        btn_siigo.setObjectName("btn_secondary")
        btn_siigo.setToolTip("Exportar todo el inventario en formato SIIGO (.xlsx) para importar en el software contable")
        btn_siigo.clicked.connect(self._exportar_siigo)
        toolbar.addWidget(btn_siigo)

        # Label valor total inventario
        self.lbl_valor_inv = QLabel("💰 Valor total: calculando...")
        self.lbl_valor_inv.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #27AE60; padding: 0 12px;"
        )
        toolbar.addWidget(self.lbl_valor_inv)

    def _abrir_importacion(self):
        dlg = ImportarMaterialesDialog(self)
        if dlg.exec():
            self._cargar()

    def _exportar_siigo(self):
        """Exporta todo el inventario al formato de importación SIIGO."""
        import os, platform, subprocess
        from app.core.database import SessionLocal
        from app.services.services import InventarioService
        from app.utils.exportar_siigo import exportar_siigo
        from PySide6.QtWidgets import QMessageBox, QFileDialog
        db = SessionLocal()
        try:
            materiales = db.query(__import__('app.models.inventario', fromlist=['Material']).Material).all()
            if not materiales:
                QMessageBox.information(self, "Sin datos",
                    "No hay materiales en el inventario para exportar.")
                return
            # Preguntar carpeta destino
            carpeta = QFileDialog.getExistingDirectory(
                self, "Seleccionar carpeta de destino", os.path.expanduser("~"))
            if not carpeta:
                return
            ruta = exportar_siigo(materiales, output_dir=carpeta)
            resp = QMessageBox.question(self, "Exportación SIIGO",
                f"✅ Exportado exitosamente ({len(materiales)} materiales):\n{ruta}\n\n¿Abrir el archivo?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if resp == QMessageBox.Yes:
                try:
                    if platform.system() == "Windows":
                        os.startfile(ruta)
                    elif platform.system() == "Darwin":
                        subprocess.call(["open", ruta])
                    else:
                        subprocess.call(["xdg-open", ruta])
                except Exception:
                    pass
        except Exception as e:
            QMessageBox.warning(self, "Error SIIGO", f"No se pudo exportar:\n{e}")
        finally:
            db.close()

    def abrir_dialogo_editar(self, id):
        MaterialDialog(self, material_id=id).exec()
        self.cargar_tabla()

    def eliminar_registro(self, id):
        db = SessionLocal()
        try:
            InventarioService(db).eliminar(id)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            db.close()


class MaterialDialog(QDialog):
    def __init__(self, parent=None, material_id=None):
        super().__init__(parent)
        self.material_id = material_id
        self.setWindowTitle("Nuevo Material" if not material_id else "Editar Material")
        self.setMinimumWidth(500)
        self.setModal(True)
        self._build_ui()
        if material_id:
            self._cargar_datos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        titulo = QLabel("📦  " + ("Nuevo Material" if not self.material_id else "Editar Material"))
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A5F;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre del material")
        form.addRow("Nombre *", self.input_nombre)

        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(CATEGORIAS_INVENTARIO)
        form.addRow("Categoría", self.combo_categoria)

        self.input_unidad = QLineEdit()
        self.input_unidad.setPlaceholderText("ej: unidad, metro, rollo, caja")
        form.addRow("Unidad", self.input_unidad)

        self.spin_cantidad = QDoubleSpinBox()
        self.spin_cantidad.setRange(0, 999999)
        self.spin_cantidad.setDecimals(2)
        form.addRow("Cantidad Actual", self.spin_cantidad)

        self.spin_minimo = QDoubleSpinBox()
        self.spin_minimo.setRange(0, 999999)
        self.spin_minimo.setDecimals(2)
        form.addRow("Stock Mínimo", self.spin_minimo)

        # ── PRECIO UNITARIO ──────────────────────────────────────────────────
        self.spin_precio = QDoubleSpinBox()
        self.spin_precio.setRange(0, 999_999_999)
        self.spin_precio.setDecimals(2)
        self.spin_precio.setPrefix("$ ")
        self.spin_precio.setSingleStep(1000)
        self.spin_precio.valueChanged.connect(self._actualizar_precio_total)
        form.addRow("Precio Unitario", self.spin_precio)

        self.lbl_precio_total = QLabel("Precio total: $ 0.00")
        self.lbl_precio_total.setStyleSheet("color: #27AE60; font-weight: bold; font-size: 12px;")
        form.addRow("Precio Total", self.lbl_precio_total)
        self.spin_cantidad.valueChanged.connect(self._actualizar_precio_total)
        # ────────────────────────────────────────────────────────────────────

        self.input_ubicacion = QLineEdit()
        self.input_ubicacion.setPlaceholderText("ej: Bodega A, Estante 3")
        form.addRow("Ubicación", self.input_ubicacion)

        self.combo_proveedor = QComboBox()
        self.combo_proveedor.addItem("Sin proveedor", None)
        db = SessionLocal()
        try:
            for p in ProveedorService(db).listar():
                self.combo_proveedor.addItem(p.nombre, p.id)
        finally:
            db.close()
        form.addRow("Proveedor", self.combo_proveedor)

        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btn_secondary")
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_guardar = QPushButton("💾  Guardar")
        btn_guardar.setObjectName("btn_success")
        btn_guardar.clicked.connect(self._guardar)
        btns.addWidget(btn_guardar)
        layout.addLayout(btns)

    def _actualizar_precio_total(self):
        total = self.spin_precio.value() * self.spin_cantidad.value()
        self.lbl_precio_total.setText(f"Precio total: $ {total:,.2f}")

    def _cargar_datos(self):
        db = SessionLocal()
        try:
            m = InventarioService(db).obtener(self.material_id)
            if not m:
                return
            self.input_nombre.setText(m.nombre_material or "")
            idx = self.combo_categoria.findText(m.categoria or "")
            if idx >= 0:
                self.combo_categoria.setCurrentIndex(idx)
            self.input_unidad.setText(m.unidad or "")
            self.spin_cantidad.setValue(m.cantidad_actual or 0)
            self.spin_minimo.setValue(m.stock_minimo or 0)
            self.spin_precio.setValue(m.precio_unitario or 0)
            self.input_ubicacion.setText(m.ubicacion or "")
            if m.proveedor_id:
                for i in range(self.combo_proveedor.count()):
                    if self.combo_proveedor.itemData(i) == m.proveedor_id:
                        self.combo_proveedor.setCurrentIndex(i)
                        break
        finally:
            db.close()

    def _guardar(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Validación", "El nombre es obligatorio.")
            return
        db = SessionLocal()
        svc = InventarioService(db)
        try:
            kwargs = dict(
                nombre_material = nombre,
                categoria       = self.combo_categoria.currentText(),
                unidad          = self.input_unidad.text().strip() or "unidad",
                cantidad_actual = self.spin_cantidad.value(),
                stock_minimo    = self.spin_minimo.value(),
                ubicacion       = self.input_ubicacion.text().strip(),
                proveedor_id    = self.combo_proveedor.currentData(),
                precio_unitario = self.spin_precio.value(),
            )
            if self.material_id:
                m = svc.obtener(self.material_id)
                if not m:
                    QMessageBox.warning(self, "Error", "Material no encontrado.")
                    return
                svc.actualizar(m, **kwargs)
            else:
                svc.crear(**kwargs)
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            db.close()
