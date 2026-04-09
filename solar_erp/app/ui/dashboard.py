from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea,
    QPushButton, QDialog, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from app.core.database import SessionLocal
from app.ui.table_helpers import configurar_tabla, btn_acta_movimiento, btn_acta_pedido, make_item
from app.services.services import ProyectoService, InventarioService, MovimientoService, SalidaProyectoService
from app.utils.files import open_file


class StatCard(QFrame):
    def __init__(self, titulo, valor, icono, color_icono="#1E3A5F", bg_color="#FFFFFF"):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(110)
        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: {bg_color};
                border-radius: 12px;
                border: 1px solid #DDE2E8;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        icono_lbl = QLabel(icono)
        icono_lbl.setStyleSheet(f"font-size: 36px; color: {color_icono};")
        icono_lbl.setFixedWidth(50)
        layout.addWidget(icono_lbl)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        self.lbl_valor = QLabel(str(valor))
        self.lbl_valor.setObjectName("card_number")
        self.lbl_valor.setStyleSheet(f"font-size: 30px; font-weight: bold; color: {color_icono};")
        text_layout.addWidget(self.lbl_valor)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("card_title")
        lbl_titulo.setStyleSheet("font-size: 12px; color: #7F8C8D;")
        text_layout.addWidget(lbl_titulo)

        layout.addLayout(text_layout)
        layout.addStretch()

    def actualizar(self, valor):
        self.lbl_valor.setText(str(valor))


class DashboardView(QWidget):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario
        self._build_ui()
        self._cargar_datos()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._cargar_datos)
        self.timer.start(30000)

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        container = QWidget()
        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        # ── Título + botones ────────────────────────────────────────────────
        header_layout = QHBoxLayout()
        titulo = QLabel("Dashboard")
        titulo.setObjectName("page_title")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E3A5F;")
        header_layout.addWidget(titulo)
        header_layout.addStretch()

        btn_alertas = QPushButton("🔴  PDF Alertas Stock")
        btn_alertas.setObjectName("btn_danger")
        btn_alertas.setMinimumHeight(36)
        btn_alertas.setToolTip("Genera un PDF con los materiales en stock bajo o crítico")
        btn_alertas.clicked.connect(self._generar_alertas_pdf)
        header_layout.addWidget(btn_alertas)

        btn_informe = QPushButton("📊  Generar Informe")
        btn_informe.setObjectName("btn_primary")
        btn_informe.setMinimumHeight(36)
        btn_informe.setToolTip("Genera un PDF con el resumen de movimientos y pedidos")
        btn_informe.clicked.connect(self._generar_informe)
        header_layout.addWidget(btn_informe)

        btn_refrescar = QPushButton("↻  Refrescar")
        btn_refrescar.setObjectName("btn_secondary")
        btn_refrescar.setMinimumHeight(36)
        btn_refrescar.clicked.connect(self._cargar_datos)
        header_layout.addWidget(btn_refrescar)

        layout.addLayout(header_layout)

        nombre = f"Bienvenido, {self.usuario.nombre}" if self.usuario else "Bienvenido"
        subtitulo = QLabel(nombre)
        subtitulo.setStyleSheet("color: #7F8C8D; font-size: 14px; margin-top: -10px;")
        layout.addWidget(subtitulo)

        # ── Stat Cards ──────────────────────────────────────────────────────
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        self.card_proyectos   = StatCard("Proyectos Activos",      "—", "🏗️",  "#1E3A5F")
        self.card_stock       = StatCard("Stock Bajo",             "—", "⚠️",  "#E74C3C", "#FFF5F5")
        self.card_materiales  = StatCard("Materiales en Stock",    "—", "📦",  "#2ECC71")
        self.card_movimientos = StatCard("Movimientos (Hoy)",      "—", "🔄",  "#F39C12")
        self.card_valor_inv   = StatCard("Valor Inventario",       "—", "💰",  "#27AE60", "#F0FFF4")
        self.card_valor_proy  = StatCard("Entregado a Proyectos",  "—", "📤",  "#9B59B6", "#F9F0FF")
        for card in [self.card_proyectos, self.card_stock, self.card_materiales,
                     self.card_movimientos, self.card_valor_inv, self.card_valor_proy]:
            cards_layout.addWidget(card)
        layout.addLayout(cards_layout)

        # ── Fila: Proyectos + Stock ─────────────────────────────────────────
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(16)

        proy_frame, self.tabla_proyectos = self._crear_tabla_section(
            "📋  Proyectos Recientes", ["Proyecto", "Cliente", "Estado", "Fecha"])
        bottom_layout.addWidget(proy_frame, 3)

        stock_frame, self.tabla_stock = self._crear_tabla_section(
            "⚠️  Alertas de Inventario", ["Material", "Stock Actual", "Mínimo"])
        bottom_layout.addWidget(stock_frame, 2)

        layout.addLayout(bottom_layout)

        # ── Últimos Movimientos ─────────────────────────────────────────────
        mov_frame = QFrame()
        mov_frame.setObjectName("card")
        mov_frame.setStyleSheet("QFrame#card { background: white; border-radius: 12px; border: 1px solid #DDE2E8; }")
        mov_vl = QVBoxLayout(mov_frame)
        mov_vl.setContentsMargins(16, 14, 16, 14)
        mov_vl.setSpacing(10)

        mov_header = QHBoxLayout()
        lbl_mov = QLabel("🔄  Últimos Movimientos de Inventario")
        lbl_mov.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E3A5F;")
        mov_header.addWidget(lbl_mov)
        mov_header.addStretch()
        btn_ver_mov = QPushButton("Ver todos →")
        btn_ver_mov.setStyleSheet("QPushButton { background: transparent; color: #1E3A5F; border: none; font-size: 12px; font-weight: bold; } QPushButton:hover { color: #2980B9; }")
        btn_ver_mov.clicked.connect(lambda: None)  # navegación futura
        mov_header.addWidget(btn_ver_mov)
        mov_vl.addLayout(mov_header)

        cols_mov = ["Tipo", "Proyecto / Proveedor", "Responsable", "Fecha", "Acta PDF"]
        self.tabla_movimientos = QTableWidget(0, len(cols_mov))
        self.tabla_movimientos.setHorizontalHeaderLabels(cols_mov)
        configurar_tabla(self.tabla_movimientos, col_stretch=1,
                         cols_fijas=[(0,90),(2,130),(3,90),(4,105)])
        self.tabla_movimientos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_movimientos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_movimientos.setAlternatingRowColors(True)
        self.tabla_movimientos.verticalHeader().setVisible(False)
        self.tabla_movimientos.setMinimumHeight(180)
        self.tabla_movimientos.setStyleSheet("QTableWidget { border: none; }")
        mov_vl.addWidget(self.tabla_movimientos)
        layout.addWidget(mov_frame)

        # ── Pedidos de Compra ───────────────────────────────────────────────
        ped_frame = QFrame()
        ped_frame.setObjectName("card")
        ped_frame.setStyleSheet("QFrame#card { background: white; border-radius: 12px; border: 1px solid #DDE2E8; }")
        ped_vl = QVBoxLayout(ped_frame)
        ped_vl.setContentsMargins(16, 14, 16, 14)
        ped_vl.setSpacing(10)

        ped_header = QHBoxLayout()
        lbl_ped = QLabel("🛒  Pedidos de Compra Registrados")
        lbl_ped.setStyleSheet("font-size: 15px; font-weight: bold; color: #9B59B6;")
        ped_header.addWidget(lbl_ped)
        ped_header.addStretch()
        ped_vl.addLayout(ped_header)

        cols_ped = ["ID", "Fecha", "Solicitante", "Proyecto", "En Stock", "A Comprar", "Acta PDF"]
        self.tabla_pedidos = QTableWidget(0, len(cols_ped))
        self.tabla_pedidos.setHorizontalHeaderLabels(cols_ped)
        configurar_tabla(self.tabla_pedidos, col_stretch=2,
                         cols_fijas=[(0,80),(1,90),(4,70),(5,80),(6,115)])
        self.tabla_pedidos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_pedidos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_pedidos.setAlternatingRowColors(True)
        self.tabla_pedidos.verticalHeader().setVisible(False)
        self.tabla_pedidos.setMinimumHeight(180)
        self.tabla_pedidos.setStyleSheet("QTableWidget { border: none; }")
        ped_vl.addWidget(self.tabla_pedidos)
        layout.addWidget(ped_frame)

    # ─── Helpers ─────────────────────────────────────────────────────────────
    def _crear_tabla_section(self, titulo, columnas):
        frame = QFrame()
        frame.setObjectName("card")
        frame.setStyleSheet("QFrame#card { background: white; border-radius: 12px; border: 1px solid #DDE2E8; }")
        v = QVBoxLayout(frame)
        v.setContentsMargins(16, 14, 16, 14)
        v.setSpacing(10)
        lbl = QLabel(titulo)
        lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E3A5F;")
        v.addWidget(lbl)
        tabla = QTableWidget(0, len(columnas))
        tabla.setHorizontalHeaderLabels(columnas)
        configurar_tabla(tabla, col_stretch=1)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setSelectionBehavior(QTableWidget.SelectRows)
        tabla.setAlternatingRowColors(True)
        tabla.verticalHeader().setVisible(False)
        tabla.setMinimumHeight(180)
        tabla.setStyleSheet("QTableWidget { border: none; }")
        v.addWidget(tabla)
        return frame, tabla

    def _abrir_pdf(self, ruta):
        if not ruta:
            QMessageBox.warning(self, "Archivo no encontrado",
                f"No se encontró el archivo PDF:\n{ruta}")
            return
        try:
            open_file(ruta)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    # ─── Carga de datos ───────────────────────────────────────────────────────
    def _cargar_datos(self):
        db = SessionLocal()
        try:
            proy_svc = ProyectoService(db)
            inv_svc  = InventarioService(db)
            mov_svc  = MovimientoService(db)

            # Stats básicas
            self.card_proyectos.actualizar(proy_svc.count_activos())
            stock_bajo = inv_svc.stock_bajo()
            self.card_stock.actualizar(len(stock_bajo))
            self.card_materiales.actualizar(len(inv_svc.listar()))
            from datetime import date
            ultimos_mov = mov_svc.ultimos(50)
            hoy = date.today()
            self.card_movimientos.actualizar(len([m for m in ultimos_mov if m.fecha == hoy]))

            # Valor inventario y valor entregado a proyectos
            try:
                valor_inv = inv_svc.valor_total_inventario()
                self.card_valor_inv.actualizar(f"${valor_inv:,.0f}")
            except Exception:
                self.card_valor_inv.actualizar("—")
            try:
                sp_svc = SalidaProyectoService(db)
                valor_neto = sp_svc.valor_total_salidas()
                self.card_valor_proy.actualizar(f"${valor_neto:,.0f}")
            except Exception:
                self.card_valor_proy.actualizar("—")

            # Pedidos
            try:
                from app.services.services import PedidoCompraService
                ped_svc = PedidoCompraService(db)
                todos_pedidos = ped_svc.todos()
            except Exception:
                todos_pedidos = []

            # Proyectos recientes
            self.tabla_proyectos.setRowCount(0)
            estados_colores = {
                "En ejecución": "#2ECC71", "Completado": "#3498DB",
                "Cancelado": "#E74C3C",    "Prospecto": "#95A5A6",
                "Aprobado": "#F39C12",     "En diseño": "#9B59B6",
            }
            for p in proy_svc.recientes(8):
                row = self.tabla_proyectos.rowCount()
                self.tabla_proyectos.insertRow(row)
                self.tabla_proyectos.setItem(row, 0, QTableWidgetItem(p.nombre_proyecto))
                self.tabla_proyectos.setItem(row, 1, QTableWidgetItem(p.cliente.nombre if p.cliente else "—"))
                ei = QTableWidgetItem(p.estado)
                ei.setForeground(QColor(estados_colores.get(p.estado, "#95A5A6")))
                ei.setFont(QFont("", -1, QFont.Bold))
                self.tabla_proyectos.setItem(row, 2, ei)
                self.tabla_proyectos.setItem(row, 3, QTableWidgetItem(str(p.fecha_inicio) if p.fecha_inicio else "—"))

            # Stock bajo
            self.tabla_stock.setRowCount(0)
            for m in stock_bajo[:10]:
                row = self.tabla_stock.rowCount()
                self.tabla_stock.insertRow(row)
                self.tabla_stock.setItem(row, 0, QTableWidgetItem(m.nombre_material))
                ci = QTableWidgetItem(f"{m.cantidad_actual} {m.unidad}")
                ci.setForeground(QColor("#E74C3C"))
                ci.setFont(QFont("", -1, QFont.Bold))
                self.tabla_stock.setItem(row, 1, ci)
                self.tabla_stock.setItem(row, 2, QTableWidgetItem(f"{m.stock_minimo} {m.unidad}"))

            # Movimientos recientes con botón PDF
            self.tabla_movimientos.setRowCount(0)
            iconos_tipo = {"entrada": "⬆️ Entrada", "salida": "⬇️ Salida", "devolucion": "↩️ Devolución"}
            colores_tipo = {"entrada": "#27AE60", "salida": "#1E3A5F", "devolucion": "#F39C12"}
            for mv in ultimos_mov[:12]:
                row = self.tabla_movimientos.rowCount()
                self.tabla_movimientos.insertRow(row)

                tipo_item = QTableWidgetItem(iconos_tipo.get(mv.tipo, mv.tipo.capitalize()))
                tipo_item.setForeground(QColor(colores_tipo.get(mv.tipo, "#2C3E50")))
                tipo_item.setFont(QFont("", -1, QFont.Bold))
                self.tabla_movimientos.setItem(row, 0, tipo_item)

                ref = mv.proyecto.nombre_proyecto if mv.proyecto else (mv.proveedor.nombre if mv.proveedor else "—")
                self.tabla_movimientos.setItem(row, 1, QTableWidgetItem(ref))
                self.tabla_movimientos.setItem(row, 2, QTableWidgetItem(mv.responsable or "—"))
                self.tabla_movimientos.setItem(row, 3, QTableWidgetItem(str(mv.fecha)))

                if mv.tipo in ("entrada", "salida", "devolucion"):
                    btn = btn_acta_movimiento(f"Ver acta de {mv.tipo} — {str(mv.fecha)}")
                    btn.clicked.connect(lambda _, m=mv: self._generar_acta_movimiento(m))
                    self.tabla_movimientos.setCellWidget(row, 4, btn)

            # Pedidos de compra
            self.tabla_pedidos.setRowCount(0)
            for ped in todos_pedidos[:15]:
                row = self.tabla_pedidos.rowCount()
                self.tabla_pedidos.insertRow(row)
                self.tabla_pedidos.setItem(row, 0, QTableWidgetItem(f"PED-{ped.id:04d}"))
                self.tabla_pedidos.setItem(row, 1, QTableWidgetItem(str(ped.fecha)))
                self.tabla_pedidos.setItem(row, 2, QTableWidgetItem(ped.solicitante or "—"))
                self.tabla_pedidos.setItem(row, 3, QTableWidgetItem(ped.proyecto_nombre or "—"))

                en_stock  = sum(1 for d in ped.detalles if d.en_stock)
                a_comprar = sum(1 for d in ped.detalles if not d.en_stock)

                es_item = QTableWidgetItem(str(en_stock))
                es_item.setForeground(QColor("#27AE60"))
                es_item.setFont(QFont("", -1, QFont.Bold))
                self.tabla_pedidos.setItem(row, 4, es_item)

                ac_item = QTableWidgetItem(str(a_comprar))
                ac_item.setForeground(QColor("#E74C3C") if a_comprar > 0 else QColor("#27AE60"))
                ac_item.setFont(QFont("", -1, QFont.Bold))
                self.tabla_pedidos.setItem(row, 5, ac_item)

                if ped.ruta_pdf:
                    btn_pdf = btn_acta_pedido(f"Ver pedido PDF — {ped.solicitante or ''}")
                    btn_pdf.clicked.connect(lambda _, r=ped.ruta_pdf: self._abrir_pdf(r))
                    self.tabla_pedidos.setCellWidget(row, 6, btn_pdf)
        finally:
            db.close()

    def _generar_acta_movimiento(self, movimiento):
        """Genera (o regenera) el acta PDF de un movimiento y la abre."""
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
            self._abrir_pdf(ruta)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo generar el acta:\n{e}")
        finally:
            db.close()

    def _generar_informe(self):
        """Genera un PDF con resumen de movimientos y pedidos."""
        db = SessionLocal()
        try:
            from app.services.services import PedidoCompraService
            movimientos = MovimientoService(db).ultimos(100)
            try:
                pedidos = PedidoCompraService(db).todos()
            except Exception:
                pedidos = []
            from app.reports.informe_dashboard import generar_informe_dashboard
            valor_inv = InventarioService(db).valor_total_inventario()
            ruta = generar_informe_dashboard(movimientos, pedidos, self.usuario, valor_inventario=valor_inv)
            resp = QMessageBox.question(self, "Informe generado",
                f"Informe PDF generado:\n{ruta}\n\n¿Deseas abrirlo?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if resp == QMessageBox.Yes:
                self._abrir_pdf(ruta)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo generar el informe:\n{e}")
        finally:
            db.close()

    def _generar_alertas_pdf(self):
        """Genera PDF con materiales en stock bajo o en cero."""
        db = SessionLocal()
        try:
            inv_svc = InventarioService(db)
            materiales = inv_svc.listar()
            alertas = [m for m in materiales if m.cantidad_actual <= m.stock_minimo]
            if not alertas:
                QMessageBox.information(self, "Sin alertas",
                    "¡Excelente! No hay materiales con stock bajo en este momento.")
                return
            from app.reports.alertas_stock import generar_alertas_stock_pdf
            valor_inv = inv_svc.valor_total_inventario()
            ruta = generar_alertas_stock_pdf(alertas, valor_inv, self.usuario)
            resp = QMessageBox.question(self, "Alertas generadas",
                f"PDF de alertas generado:\n{ruta}\n\n¿Deseas abrirlo?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if resp == QMessageBox.Yes:
                self._abrir_pdf(ruta)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo generar el PDF de alertas:\n{e}")
        finally:
            db.close()

    def refrescar(self):
        self._cargar_datos()
