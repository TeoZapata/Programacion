import pandas as pd
from PyQt5.QtWidgets import QFileDialog, QProgressDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from src.utils.getDate import fecha_actual
from src.utils.getCodeBar import getCodeBar


class ImportExcelThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(pd.DataFrame)
    error = pyqtSignal(str)

    def __init__(self, db, file_path):
        super().__init__()
        self.db = db
        self.file_path = file_path

    def run(self):
        try:
            # Leer el archivo de Excel
            df = pd.read_excel(self.file_path)

            # Verificar si el DataFrame está vacío
            if df.empty:
                raise ValueError("El archivo de Excel está vacío.")

            # Insertar los datos en la tabla de inventario
            total_rows = len(df)
            for i, (_, row) in enumerate(df.iterrows()):
                self.db.ejecutar_consulta(
                    "INSERT INTO inventario (nombre, seccion, barcode, cantidad, unidad, precio, precioTotal, cantidad_minima, cantidad_maxima, proveedor, fecha_compra, subcategoria) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)",
                    				

                    (row['Nombre'], row['Sección'], getCodeBar(self, row['Sección'], row['Subsección'], False), row['Cantidad'], row['Unidad'], row['Precio'], row['Precio Total'], row['Cantidad Minima'], row['Cantidad Maxima'], row['Proveedor'], fecha_actual(), row['Subsección'])
                )
                # Emitir progreso
                self.progress.emit(int((i + 1) / total_rows * 100))

            # Emitir señal de finalización
            self.finished.emit(df)

        except Exception as e:
            # Emitir señal de error
            self.error.emit(str(e))


def import_excel_and_store_inventory(db):
    """
    Abre un cuadro de diálogo para seleccionar un archivo de Excel, lo convierte en un DataFrame de pandas
    y guarda los productos en la tabla de inventario de la base de datos en un hilo separado.
    """
    try:
        # Abrir cuadro de diálogo para seleccionar archivo
        file_dialog = QFileDialog()
        file_dialog.setNameFilters(["Archivos de Excel (*.xlsx *.xls)"])
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
        else:
            raise ValueError("No se seleccionó ningún archivo.")

        # Crear un cuadro de progreso
        progress_dialog = QProgressDialog("Importando datos...", "Cancelar", 0, 100)
        progress_dialog.setWindowTitle("Progreso de Importación")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setValue(0)

        # Crear y configurar el hilo
        thread = ImportExcelThread(db, file_path)
        thread.progress.connect(progress_dialog.setValue)
        thread.finished.connect(lambda df: on_import_finished(df, progress_dialog))
        thread.error.connect(lambda error: on_import_error(error, progress_dialog))
        thread.start()

        # Mostrar el cuadro de progreso
        progress_dialog.exec_()

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al importar el archivo de Excel: {e}")


def on_import_finished(df, progress_dialog):
    progress_dialog.close()
    QMessageBox.information(None, "Éxito", "La importación se completó correctamente.")


def on_import_error(error, progress_dialog):
    progress_dialog.close()
    QMessageBox.critical(None, "Error", f"Error al importar el archivo de Excel: {error}")
