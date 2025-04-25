import pandas as pd
from PyQt5.QtWidgets import QFileDialog
from src.utils.getDate import fecha_actual

def import_excel_and_store_inventory(db) -> pd.DataFrame:
        
        """
        Abre un cuadro de diálogo para seleccionar un archivo de Excel, lo convierte en un DataFrame de pandas
        y guarda los productos en la tabla de inventario de la base de datos.
        
        Args:
            db (storeBD): Instancia de la base de datos para ejecutar consultas.
        
        Returns:
            pd.DataFrame: DataFrame que contiene los datos del archivo de Excel.
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
            
            # Leer el archivo de Excel
            df = pd.read_excel(file_path)
            print(df)
            # Verificar si el DataFrame está vacío
            if df.empty:
                raise ValueError("El archivo de Excel está vacío.")
            
            # Insertar los datos en la tabla de inventario
            for _, row in df.iterrows():
                # Verificar si la fila tiene los campos necesarios
                print(row['nombre'], row['seccion'], row['barcode'], row['cantidad'], row['unidad'], row['precio'], row['precioTotal'],row['cantidad_minima'],row['cantidad_maxima'], row['proveedor'])
                db.ejecutar_consulta(
                        "INSERT INTO inventario (nombre, seccion, barcode, cantidad, unidad, precio, precioTotal, cantidad_minima, cantidad_maxima, proveedor, fecha_compra) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (row['nombre'], row['seccion'], row['barcode'], row['cantidad'], row['unidad'], row['precio'], row['precioTotal'], row['cantidad_minima'], row['cantidad_maxima'], row['proveedor'], fecha_actual())
                    )
                       
            return df
        
        except Exception as e:
            print(f"Error al importar el archivo de Excel: {e}")
        return None
