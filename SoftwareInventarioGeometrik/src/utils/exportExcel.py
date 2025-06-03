import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import pandas as pd


class ExportarExcelThread(QThread):
    progreso_actualizado = pyqtSignal(int)
    exportacion_completada = pyqtSignal(bool)

    def __init__(self, db, ruta_archivo):
        super().__init__()
        self.db = db
        self.ruta_archivo = ruta_archivo

    def run(self):
        try:
            datos = self.db.obtener_inventario()
            df = pd.DataFrame(datos, columns=[
                "ID",
                "Nombre",
                "Sección",
                "Código de Barras",
                "Cantidad",
                "Unidad",
                "Precio",
                "Precio Total",
                "Cantidad Mínima",
                "Cantidad Máxima",
                "Proveedor",
                "Fecha de Compra",
                "Subcategoría",
            ])
            # Simular progreso
            for i in range(1, 101):
                self.progreso_actualizado.emit(i)
                self.msleep(10)  # Simulación de tiempo de procesamiento
            df.to_excel(self.ruta_archivo, index=False)
            self.exportacion_completada.emit(True)
        except Exception as e:
            print(f"Error durante la exportación: {e}")
            self.exportacion_completada.emit(False)


def iniciar_exportacion(db):
    # Seleccionar carpeta de destino
    ruta_archivo, _ = QtWidgets.QFileDialog.getSaveFileName(
        None, "Guardar archivo", "", "Archivos Excel (*.xlsx)"
    )
    if not ruta_archivo:
        return

    ventana_progreso = QtWidgets.QProgressDialog("Exportando inventario...", "Cancelar", 0, 100)
    ventana_progreso.setWindowTitle("Progreso de Exportación")
    ventana_progreso.setWindowModality(Qt.ApplicationModal)
    ventana_progreso.setValue(0)
    ventana_progreso.show()

    def actualizar_progreso(valor):
        ventana_progreso.setValue(valor)

    def finalizar_exportacion(exito):
        ventana_progreso.close()
        if exito:
            QtWidgets.QMessageBox.information(None, "Exportación Completada", "El archivo se guardó correctamente.")
        else:
            QtWidgets.QMessageBox.critical(None, "Error", "Ocurrió un error durante la exportación.")

    # Mantener una referencia al hilo para evitar que sea destruido
    iniciar_exportacion.hilo_exportacion = ExportarExcelThread(db, ruta_archivo)
    hilo_exportacion = iniciar_exportacion.hilo_exportacion
    hilo_exportacion.progreso_actualizado.connect(actualizar_progreso)
    hilo_exportacion.exportacion_completada.connect(finalizar_exportacion)
    hilo_exportacion.start()