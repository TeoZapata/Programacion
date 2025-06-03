import sys
import os
import pandas as pd
import sqlite3
import threading
from src.utils.getCodeBar import getCodeBar
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QProgressBar, QLabel, 
                             QMessageBox, QSpinBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont
from DataBase.storeDB import *  # Asegúrate de que esta función esté definida en tu módulo de base de datos


class ImportWorker(QThread):
    """Clase worker para manejar la importación en un hilo separado"""
    progress_update = pyqtSignal(int)
    status_update = pyqtSignal(str)
    import_finished = pyqtSignal(bool, str)
    
    def __init__(self, excel_path, batch_size=100):
        super().__init__()
        self.excel_path = excel_path
        self.batch_size = batch_size
        
    def run(self):
        try:
            self.status_update.emit("Cargando archivo Excel...")
            # Usar optimizaciones de pandas para leer Excel eficientemente
            df = pd.read_excel(self.excel_path, engine='openpyxl', header=0)
            
            if df.empty:
                self.import_finished.emit(False, "El archivo Excel está vacío")
                return
                
            # Verificar columnas necesarias
            required_columns = ["Nombre",
                                "Sección",
                                "Subsección",
                                "Cantidad",
                                "Unidad",
                                "Precio",
                                "Precio Total",
                                "Cantidad Mínima",
                                "Cantidad Máxima",
                                "Proveedor"]
            
            # Renombrar columnas si es necesario (ajustar según formato de entrada)
            df.columns = df.columns.str.strip().str.lower()
            
            # Verificar si faltan columnas requeridas
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.import_finished.emit(False, f"Faltan columnas requeridas: {', '.join(missing_columns)}")
                return
            
            total_rows = len(df)
            self.status_update.emit(f"Procesando {total_rows} registros...")
            
            # Procesar e insertar datos en lotes
            for i in range(0, total_rows, self.batch_size):
                end_idx = min(i + self.batch_size, total_rows)
                batch = df.iloc[i:end_idx]
                
                # Insertar lote en la base de datos
                success = self.insert_batch_to_db(batch)
                if not success:
                    self.import_finished.emit(False, "Error al insertar datos en la base de datos")
                    return
                
                # Actualizar progreso
                progress = int((end_idx / total_rows) * 100)
                self.progress_update.emit(progress)
            
            self.status_update.emit("Importación completada con éxito")
            self.import_finished.emit(True, f"Se importaron {total_rows} registros correctamente")
            
        except Exception as e:
            self.import_finished.emit(False, f"Error durante la importación: {str(e)}")
    
    def insert_batch_to_db(self, batch_df):
        """Inserta un lote de datos en la base de datos"""
        try:
            # Convertir DataFrame a lista de tuplas para inserción masiva
            records = []
            for _, row in batch_df.iterrows():
                record = (
                    row.get('nombre', ''),
                    row.get('sección', ''),
                    float(row.get('cantidad', 0)),
                    row.get('unidad', ''),
                    float(row.get('precio', 0)),
                    float(row.get('precio total', 0)),
                    float(row.get('cantidad mínima', 0)),
                    float(row.get('cantidad máxima', 0)),
                    row.get('proveedor', '')
                )
                records.append(record)
                print(f"Registro procesado: {record}")
            # Llamar a la función para insertar en la base de datos
            insert_db(records)
        
            return True
        except Exception as e:
            print(f"Error en insert_batch_to_db: {e}")
            return False


class ExcelImportWidget(QWidget):
    """Widget para importar archivos Excel a la base de datos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.import_worker = None
        
    def init_ui(self):
        # Configuración principal
        self.setWindowTitle("Importar desde Excel")
        self.setMinimumWidth(500)
        
        # Crear layout principal
        main_layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Importar Inventario desde Excel")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Layout para selección de archivo
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel("Ningún archivo seleccionado")
        self.file_path_label.setWordWrap(True)
        file_layout.addWidget(self.file_path_label, 1)
        
        self.select_file_btn = QPushButton("Seleccionar Excel")
        self.select_file_btn.clicked.connect(self.select_excel_file)
        file_layout.addWidget(self.select_file_btn)
        
        main_layout.addLayout(file_layout)
        
        # Layout para tamaño de lote
        batch_layout = QHBoxLayout()
        batch_label = QLabel("Tamaño de lote:")
        batch_layout.addWidget(batch_label)
        
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(50, 1000)
        self.batch_size_spin.setValue(100)
        self.batch_size_spin.setSingleStep(50)
        batch_layout.addWidget(self.batch_size_spin)
        
        batch_layout.addStretch()
        main_layout.addLayout(batch_layout)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Etiqueta de estado
        self.status_label = QLabel("Listo para importar")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("Importar Datos")
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self.start_import)
        button_layout.addWidget(self.import_btn)
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def select_excel_file(self):
        """Abre un diálogo para seleccionar un archivo Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo Excel", "", "Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
            self.import_btn.setEnabled(True)
    
    def start_import(self):
        """Inicia el proceso de importación en un hilo separado"""
        excel_path = self.file_path_label.text()
        
        if excel_path == "Ningún archivo seleccionado":
            QMessageBox.warning(self, "Error", "Por favor seleccione un archivo Excel")
            return
        
        if not os.path.exists(excel_path):
            QMessageBox.warning(self, "Error", "El archivo seleccionado no existe")
            return
        
        # Deshabilitar botones durante la importación
        self.select_file_btn.setEnabled(False)
        self.import_btn.setEnabled(False)
        self.cancel_btn.setText("Cancelar Importación")
        
        # Resetear progreso
        self.progress_bar.setValue(0)
        self.status_label.setText("Iniciando importación...")
        
        # Crear e iniciar el worker
        batch_size = self.batch_size_spin.value()
        self.import_worker = ImportWorker(excel_path, batch_size)
        self.import_worker.progress_update.connect(self.update_progress)
        self.import_worker.status_update.connect(self.update_status)
        self.import_worker.import_finished.connect(self.on_import_finished)
        self.import_worker.start()
    
    @pyqtSlot(int)
    def update_progress(self, value):
        """Actualiza la barra de progreso"""
        self.progress_bar.setValue(value)
    
    @pyqtSlot(str)
    def update_status(self, message):
        """Actualiza el mensaje de estado"""
        self.status_label.setText(message)
    
    @pyqtSlot(bool, str)
    def on_import_finished(self, success, message):
        """Maneja la finalización del proceso de importación"""
        # Restaurar estado de botones
        self.select_file_btn.setEnabled(True)
        self.import_btn.setEnabled(True)
        self.cancel_btn.setText("Cerrar")
        
        # Mostrar mensaje de resultado
        if success:
            QMessageBox.information(self, "Éxito", message)
            # Completar barra de progreso si no estaba al 100%
            if self.progress_bar.value() < 100:
                self.progress_bar.setValue(100)
        else:
            QMessageBox.critical(self, "Error", message)
    
    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        if self.import_worker and self.import_worker.isRunning():
            reply = QMessageBox.question(
                self, "Confirmar cancelación",
                "¿Está seguro que desea cancelar la importación en curso?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.import_worker.terminate()
                self.import_worker.wait()
            else:
                event.ignore()
                return
        
        event.accept()


def create_db_connection():
    """Crea y retorna una conexión a la base de datos"""
    try:
        conn = sqlite3.connect('storeDB.db')
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


def insert_db(records):
    """
    Inserta registros en la base de datos
    
    Args:
        records: Lista de tuplas con los datos a insertar
    """
    conn = create_db_connection()
    if not conn:
        raise Exception("No se pudo conectar a la base de datos")
    
    try:
        cursor = conn.cursor()
        
        # Verificar si la tabla existe, si no, crearla

        # Insertar registros
        cursor.executemany('''
        INSERT INTO inventario (
            nombre, seccion, subcategoria, barcode, cantidad, unidad, 
            precio, precioTotal, cantidad_minima, cantidad_maxima, 
            proveedor
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', records)
        
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Error al insertar datos: {e}")
    finally:
        if conn:
            conn.close()


# Función para mostrar el módulo de importación como ventana independiente
def show_import_dialog(parent=None):
    """Muestra el diálogo de importación"""
    import_widget = ExcelImportWidget(parent)
    import_widget.setWindowModality(Qt.ApplicationModal)
    import_widget.show()
    return import_widget

