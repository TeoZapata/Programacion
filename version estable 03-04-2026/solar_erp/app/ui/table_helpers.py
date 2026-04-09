"""
Helpers centralizados para configurar tablas QTableWidget en GeoInventario.
- Redimensionado interactivo de columnas (el usuario arrastra el ancho)
- Una columna designada se estira para absorber el espacio sobrante
- Tooltip automático al pasar el cursor (muestra texto completo)
- Botones de acta PDF estandarizados
- Función normalizar() para búsquedas sin tildes ni distinción de caso
"""
from PySide6.QtWidgets import (QHeaderView, QTableWidget, QTableWidgetItem,
                                QPushButton, QAbstractItemView)
from PySide6.QtCore import Qt, QEvent, QObject
import unicodedata


# ── Normalización de texto ────────────────────────────────────────────────────
def normalizar(texto: str) -> str:
    """Convierte texto a minúsculas sin tildes para comparación flexible.
    Ejemplo: normalizar('Héroe') == 'heroe'  /  normalizar('CAÑERÍA') == 'caneria'
    """
    if not texto:
        return ""
    nfkd = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# ── Event filter para tooltips automáticos ───────────────────────────────────
class _TooltipFilter(QObject):
    """Instala un event filter en QTableWidget para mostrar tooltip con el
    texto completo de la celda cuando el cursor pasa sobre ella."""

    def __init__(self, tabla: QTableWidget):
        super().__init__(tabla)
        self._tabla = tabla
        tabla.setMouseTracking(True)
        tabla.viewport().setMouseTracking(True)
        tabla.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove:
            index = self._tabla.indexAt(event.pos())
            if index.isValid():
                item = self._tabla.item(index.row(), index.column())
                widget = self._tabla.cellWidget(index.row(), index.column())
                if item and item.text():
                    self._tabla.setToolTip(item.text())
                elif widget and widget.toolTip():
                    self._tabla.setToolTip(widget.toolTip())
                else:
                    self._tabla.setToolTip("")
            else:
                self._tabla.setToolTip("")
        return False   # no consumir el evento


# ── Configurar tabla ──────────────────────────────────────────────────────────
def configurar_tabla(tabla: QTableWidget,
                     col_stretch: int = 0,
                     cols_fijas: list = None,
                     altura_fila: int = 34):
    """
    Aplica a una QTableWidget:
      - Modo Interactive: el usuario arrastra CUALQUIER columna para ajustar
      - Una columna (col_stretch) se estira para llenar el espacio sobrante
      - cols_fijas: lista de (col_idx, ancho_px) para columnas con ancho inicial fijo
        pero aún arrastrables (Fixed solo como punto de partida)
      - Tooltip automático al pasar el cursor
      - Altura de fila uniforme
    """
    hdr = tabla.horizontalHeader()

    # Base: todas las columnas son interactivas
    hdr.setSectionResizeMode(QHeaderView.Interactive)
    hdr.setStretchLastSection(False)
    hdr.setMinimumSectionSize(40)

    # Columna principal que absorbe espacio libre
    if col_stretch is not None and tabla.columnCount() > col_stretch:
        hdr.setSectionResizeMode(col_stretch, QHeaderView.Stretch)

    # Anchos iniciales para otras columnas (quedan interactivas, no fijas)
    if cols_fijas:
        for col, ancho in cols_fijas:
            if col < tabla.columnCount():
                # Interactive + setColumnWidth da el ancho inicial pero permite arrastrar
                hdr.setSectionResizeMode(col, QHeaderView.Interactive)
                tabla.setColumnWidth(col, ancho)

    # Altura de filas uniforme
    tabla.verticalHeader().setDefaultSectionSize(altura_fila)

    # Instalar tooltip automático vía event filter (más robusto que reemplazar clase)
    tabla._tooltip_filter = _TooltipFilter(tabla)


# ── Helpers de ítems ──────────────────────────────────────────────────────────
def set_item_tooltip(item: QTableWidgetItem, extra: str = "") -> QTableWidgetItem:
    if item:
        tip = item.text()
        if extra:
            tip = f"{tip}\n{extra}"
        item.setToolTip(tip)
    return item


def make_item(texto: str, tooltip: str = None) -> QTableWidgetItem:
    """Crea un QTableWidgetItem con tooltip automático igual a su texto."""
    it = QTableWidgetItem(str(texto) if texto is not None else "—")
    it.setToolTip(tooltip if tooltip is not None else it.text())
    return it


# ── Botones de acta PDF ───────────────────────────────────────────────────────
def btn_acta(label: str = "📄 Acta PDF",
             color_bg: str = "#EBF5FB",
             color_txt: str = "#1E3A5F",
             color_border: str = "#AED6F1",
             color_hover: str = "#AED6F1",
             tooltip: str = "Ver / generar acta PDF") -> QPushButton:
    btn = QPushButton(label)
    btn.setMinimumHeight(28)
    btn.setMinimumWidth(95)
    btn.setToolTip(tooltip)
    btn.setStyleSheet(
        f"QPushButton {{"
        f"  background:{color_bg}; color:{color_txt};"
        f"  border:1px solid {color_border}; border-radius:5px;"
        f"  font-size:11px; font-weight:bold; padding:3px 10px;"
        f"}}"
        f"QPushButton:hover {{ background:{color_hover}; }}"
        f"QPushButton:pressed {{ background:{color_border}; }}"
    )
    return btn


def btn_acta_movimiento(tooltip: str = "Ver acta del movimiento") -> QPushButton:
    return btn_acta("📄 Acta PDF", "#EBF5FB", "#1E3A5F", "#AED6F1", "#AED6F1", tooltip)


def btn_acta_pedido(tooltip: str = "Ver acta del pedido") -> QPushButton:
    return btn_acta("📄 Pedido PDF", "#F5EEF8", "#9B59B6", "#D7BDE2", "#D7BDE2", tooltip)
