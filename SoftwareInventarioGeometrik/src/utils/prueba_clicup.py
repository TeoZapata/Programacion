import requests
from datetime import datetime

def crear_tarea(self, nombre_tarea, descripcion ,lista_id, api_token):
    url = f"https://api.clickup.com/api/v2/list/{lista_id}/task"
    
    headers = {
        "Authorization": api_token,
        "Content-Type": "application/json"
    }
    
    def convertir_a_timestamp(fecha_str):
        # Convierte una fecha en formato "YYYY-MM-DD HH:MM:SS" a timestamp en milisegundos
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
        "time_estimate": 3600000,  # 1 hour in milliseconds
        "time_tracking": 1800000  # 30 minutes in milliseconds
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("Tarea creada exitosamente:", response.json())
    else:
        print("Error al crear la tarea:", response.status_code, response.text)
