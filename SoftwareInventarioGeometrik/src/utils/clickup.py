import requests
import json

def get_available_lists(api_key):
    """
    Obtiene todas las listas disponibles en todos los espacios de trabajo de ClickUp
    
    Args:
        api_key (str): La API key de ClickUp
        
    Returns:
        dict: Un diccionario organizado con todos los equipos, espacios y listas
    """
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    result = {
        "teams": []
    }
    
    try:
        # 1. Obtener todos los equipos (workspaces)
        teams_url = "https://api.clickup.com/api/v2/team"
        teams_response = requests.get(teams_url, headers=headers)
        
        if teams_response.status_code != 200:
            print(f"Error al obtener equipos: {teams_response.status_code}")
            print(teams_response.text)
            return None
            
        teams = teams_response.json()["teams"]
        
        # 2. Para cada equipo, obtener sus espacios
        for team in teams:
            team_info = {
                "id": team["id"],
                "name": team["name"],
                "spaces": []
            }
            
            spaces_url = f"https://api.clickup.com/api/v2/team/{team['id']}/space"
            spaces_response = requests.get(spaces_url, headers=headers)
            
            if spaces_response.status_code == 200:
                spaces = spaces_response.json()["spaces"]
                
                # 3. Para cada espacio, obtener sus listas
                for space in spaces:
                    space_info = {
                        "id": space["id"],
                        "name": space["name"],
                        "lists": []
                    }
                    
                    lists_url = f"https://api.clickup.com/api/v2/space/{space['id']}/list"
                    lists_response = requests.get(lists_url, headers=headers)
                    
                    if lists_response.status_code == 200:
                        lists = lists_response.json()["lists"]
                        
                        for list_item in lists:
                            list_info = {
                                "id": list_item["id"],
                                "name": list_item["name"]
                            }
                            space_info["lists"].append(list_info)
                    else:
                        print(f"Error al obtener listas del espacio {space['name']}: {lists_response.status_code}")
                        
                    team_info["spaces"].append(space_info)
            else:
                print(f"Error al obtener espacios del equipo {team['name']}: {spaces_response.status_code}")
                
            result["teams"].append(team_info)
            
        return result
        
    except Exception as e:
        print(f"Error al obtener listas: {str(e)}")
        return None

def print_available_lists(api_key):
    """
    Imprime de manera formateada todas las listas disponibles
    
    Args:
        api_key (str): La API key de ClickUp
    """
    data = get_available_lists(api_key)
    
    if not data:
        print("No se pudieron obtener las listas.")
        return
    
    print("\n=== LISTAS DISPONIBLES EN CLICKUP ===\n")
    
    for team in data["teams"]:
        print(f"📂 EQUIPO: {team['name']} (ID: {team['id']})")
        
        if not team["spaces"]:
            print("  └─ No hay espacios en este equipo")
            continue
            
        for space in team["spaces"]:
            print(f"  ├─ 📁 ESPACIO: {space['name']} (ID: {space['id']})")
            
            if not space["lists"]:
                print("  │  └─ No hay listas en este espacio")
                continue
                
            for i, list_item in enumerate(space["lists"]):
                is_last = i == len(space["lists"]) - 1
                prefix = "  │  └─" if is_last else "  │  ├─"
                print(f"{prefix} 📋 LISTA: {list_item['name']} (ID: {list_item['id']})")
    
    print("\n== EJEMPLO DE USO PARA CREAR TAREA ==")
    print("Para crear una tarea, necesitas el ID de una lista. Por ejemplo:")
    
    # Encontrar la primera lista disponible para el ejemplo
    example_list = None
    for team in data["teams"]:
        for space in team["spaces"]:
            if space["lists"]:
                example_list = space["lists"][0]
                break
        if example_list:
            break
    
    if example_list:
        print(f"""
# Ejemplo para crear una tarea en la lista "{example_list['name']}"
import requests

API_KEY = "tu_api_key"  # Mejor usar variables de entorno
headers = {{
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}}

list_id = "{example_list['id']}"
url = f"https://api.clickup.com/api/v2/list/{{list_id}}/task"

payload = {{
    "name": "Nueva tarea de prueba",
    "description": "Esta es una tarea creada a través de la API"
}}

response = requests.post(url, headers=headers, json=payload)
task = response.json()
print(f"Tarea creada: {{task['name']}} (ID: {{task['id']}}")
""")

# Ejemplo de uso
if __name__ == "__main__":
    API_KEY = "pk_126014776_6XFCEVXQE0VRTDBMVKQBGJL1PA6YAI4M"  # En producción, usa variables de entorno
    print_available_lists(API_KEY)