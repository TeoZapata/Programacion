
from PyQt5.QtWidgets import QLineEdit,QTableWidgetItem
from PyQt5.QtCore import Qt
from Style import  *


def clear_entry(listaWidget: list) -> None:

    """Limpia el campo de entrada y establece un nuevo marcador de posición."""
    lista:list[QLineEdit] = listaWidget
    for i in lista:
        i.clear()
        i.setStyleSheet(ENTRY_GENERAL_DESIGN)
def cargar_invenario(self):
        """Carga el inventario desde la base de datos y lo muestra en la tabla."""
        # Limpiar la tabla antes de cargar nuevos datos
        self.data_table.setRowCount(0)

        # Obtener los datos del inventario desde la base de datos
        materiales = self.db.obtener_inventario()
        # Llenar la tabla con los datos obtenidos
        for material in materiales:
            row_position = self.data_table.rowCount()
            self.data_table.insertRow(row_position)
            for column, data in enumerate(material):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                self.data_table.setItem(row_position, column, item)
    