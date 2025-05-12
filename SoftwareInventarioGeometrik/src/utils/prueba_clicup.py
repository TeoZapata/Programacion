import requests
from datetime import datetime
import os

def crear_tarea(self, nombre_tarea, descripcion, lista_id, api_token, archivos=None):
    """
    Crea una tarea en ClickUp y adjunta archivos si se proporcionan.
    
    Args:
        nombre_tarea (str): Nombre de la tarea
        descripcion (str): Descripción de la tarea
        lista_id (str): ID de la lista donde se creará la tarea
        api_token (str): Token de API de ClickUp
        archivos (list, optional): Lista de rutas de archivo para adjuntar a la tarea
    
    Returns:
        dict: Respuesta JSON de la API de ClickUp
    """
    # Paso 1: Crear la tarea
    url = f"https://api.clickup.com/api/v2/list/{lista_id}/task"
    
    headers = {
        "Authorization": api_token,
        "Content-Type": "application/json"
    }
    
    def convertir_a_timestamp(fecha_str):
        # Convierte una fecha en formato "YYYY-MM-DD" a timestamp en milisegundos
        dt = datetime.strptime(fecha_str, "%Y-%m-%d")
        return int(dt.timestamp() * 1000)

    # Ejemplo de fechas
    fecha_inicio = "2024-11-01"
    fecha_vencimiento = "2024-12-10"

    payload = {
        "name": nombre_tarea,
        "status": "in progress",
        "priority": 2,
        "due_date": convertir_a_timestamp(fecha_vencimiento),
        "start_date": convertir_a_timestamp(fecha_inicio),
        "description": descripcion,
        "assignees": [12345678],  # Example assignee ID
        "tags": ["ejemplo", "automático"],
        "custom_fields": [
            {
                "id": "custom_field_id_1",
                "value": "Valor personalizado 1"
            },
            {
                "id": "custom_field_id_2",
                "value": 42
            }
        ],
        "check_required_custom_fields": True,
        "notify_all": True,
        "time_estimate": 3600000,  # 1 hora en milisegundos
        "time_tracking": 1800000  # 30 minutos en milisegundos
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("Tarea creada exitosamente:", response.json())
        tarea_id = response.json()["id"]
        
        # Paso 2: Adjuntar archivos si se proporcionaron
        if archivos and len(archivos) > 0:
            attachments_added = adjuntar_archivos_a_tarea(tarea_id, archivos, api_token)
            if attachments_added:
                print(f"Se adjuntaron {attachments_added} archivos a la tarea")
        
        return response.json()
    else:
        print("Error al crear la tarea:", response.status_code, response.text)
        return None

def adjuntar_archivos_a_tarea(tarea_id, archivos, api_token):
    """
    Adjunta archivos a una tarea existente en ClickUp.
    
    Args:
        tarea_id (str): ID de la tarea a la que adjuntar archivos
        archivos (list): Lista de rutas de archivo para adjuntar
        api_token (str): Token de API de ClickUp
    
    Returns:
        int: Número de archivos adjuntados exitosamente
    """
    url = f"https://api.clickup.com/api/v2/task/{tarea_id}/attachment"
    
    headers = {
        "Authorization": api_token
    }
    
    archivos_adjuntados = 0
    
    for ruta_archivo in archivos:
        if not os.path.exists(ruta_archivo):
            print(f"El archivo {ruta_archivo} no existe, omitiendo...")
            continue
            
        # Preparar el archivo para enviar
        nombre_archivo = os.path.basename(ruta_archivo)
        
        # Abrir el archivo en modo binario
        with open(ruta_archivo, 'rb') as file:
            files = {
                'attachment': (nombre_archivo, file, 'application/octet-stream')
            }
            
            # Hacer la solicitud para adjuntar el archivo
            response = requests.post(url, headers=headers, files=files)
            
            if response.status_code == 200:
                print(f"Archivo {nombre_archivo} adjuntado exitosamente")
                archivos_adjuntados += 1
            else:
                print(f"Error al adjuntar el archivo {nombre_archivo}:", response.status_code, response.text)
    
    return archivos_adjuntados


# Ejemplo de uso:
"""
client = TuClase()  # Suponiendo que esta función es parte de una clase
archivos_para_adjuntar = [
    "/ruta/al/documento.pdf",
    "/ruta/a/imagen.jpg"
]

client.crear_tarea(
    nombre_tarea="Tarea con archivos adjuntos", 
    descripcion="Esta tarea tiene archivos adjuntos",
    lista_id="123456789", 
    api_token="pk_12345678_abcdefghijklmnopqrstuvwxyz", 
    archivos=archivos_para_adjuntar
)
"""