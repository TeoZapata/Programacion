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

def print_available_lists(self, api_key):
    """
    Muestra de manera formateada todas las listas disponibles utilizando componentes de la clase
    
    Args:
        api_key (str): La API key de ClickUp
    """
    data = get_available_lists(api_key)
    message = []
    if not data:
        message.append("No se pudieron obtener las listas.")
        return
    
    message.append("\n=== LISTAS DISPONIBLES EN CLICKUP ===\n")
    
    for team in data["teams"]:
        message.append(f"📂 EQUIPO: {team['name']} (ID: {team['id']})")
        
        if not team["spaces"]:
            message.append("  └─ No hay espacios en este equipo")
            continue
            
        for space in team["spaces"]:
            message.append(f"  ├─ 📁 ESPACIO: {space['name']} (ID: {space['id']})")
            
            if not space["lists"]:
                message.append("  │  └─ No hay listas en este espacio")
                continue
                
            for i, list_item in enumerate(space["lists"]):
                is_last = i == len(space["lists"]) - 1
                prefix = "  │  └─" if is_last else "  │  ├─"
                message.append(f"{prefix} 📋 LISTA: {list_item['name']} (ID: {list_item['id']})")
    
    message.append("\n== EJEMPLO DE USO PARA CREAR TAREA ==")
    message.append("Para crear una tarea, necesitas el ID de una lista. Por ejemplo:")

    # Encontrar la primera lista disponible para el ejemplo
    example_list = None
    for team in data["teams"]:
        for space in team["spaces"]:
            if space["lists"]:
                example_list = space["lists"][0]
                break
        if example_list:
            break
    self.connection_status_label.setText("Estado: Conectado")
    self.connection_status_label.setStyleSheet("QLabel { font-weight: bold; color: green; }")
    self.api_info_display.setText("\n".join(message))