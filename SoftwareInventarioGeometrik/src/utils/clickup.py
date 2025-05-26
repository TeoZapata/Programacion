import requests
import json

def get_available_lists(api_key):
    """
    Obtiene todas las listas disponibles en todos los espacios de trabajo de ClickUp, incluyendo carpetas y subcarpetas hasta 3 niveles.
    """
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    result = {
        "teams": []
    }
    try:
        teams_url = "https://api.clickup.com/api/v2/team"
        teams_response = requests.get(teams_url, headers=headers)
        if teams_response.status_code != 200:
            print(f"Error al obtener equipos: {teams_response.status_code}")
            print(teams_response.text)
            return None
        teams = teams_response.json()["teams"]
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
                for space in spaces:
                    space_info = {
                        "id": space["id"],
                        "name": space["name"],
                        "lists": [],
                        "folders": []
                    }
                    # Listas sueltas en el espacio
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
                    # Carpetas en el espacio
                    folders_url = f"https://api.clickup.com/api/v2/space/{space['id']}/folder"
                    folders_response = requests.get(folders_url, headers=headers)
                    if folders_response.status_code == 200:
                        folders = folders_response.json()["folders"]
                        for folder in folders:
                            folder_info = {
                                "id": folder["id"],
                                "name": folder["name"],
                                "lists": [],
                                "folders": []
                            }
                            # Listas en la carpeta
                            for list_item in folder.get("lists", []):
                                list_info = {
                                    "id": list_item["id"],
                                    "name": list_item["name"]
                                }
                                folder_info["lists"].append(list_info)
                            # Subcarpetas (nivel 3, si existen)
                            # ClickUp API no soporta subcarpetas anidadas por defecto, pero si tuvieras una estructura personalizada, aquí podrías agregar la lógica.
                            # Por ahora, solo agregamos un nivel de carpetas.
                            space_info["folders"].append(folder_info)
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
    Muestra de manera formateada todas las listas disponibles hasta 3 niveles (espacio, carpeta, lista).
    """
    data = get_available_lists(api_key)
    message = []
    if not data:
        message.append("No se pudieron obtener las listas.")
        return

    message.append("\n=== LISTAS DISPONIBLES EN CLICKUP ===\n")

    def print_folder(folder, prefix, is_last_folder):
        folder_prefix = f"{prefix}{'└─' if is_last_folder else '├─'} 📂 CARPETA: {folder['name']} (ID: {folder['id']})"
        message.append(folder_prefix)
        # Listas en la carpeta
        for i, list_item in enumerate(folder["lists"]):
            is_last_list = (i == len(folder["lists"]) - 1) and not folder["folders"]
            list_prefix = f"{prefix}{'   ' if is_last_folder else '│  '}{'└─' if is_last_list else '├─'} 📋 LISTA: {list_item['name']} (ID: {list_item['id']})"
            message.append(list_prefix)
        # Subcarpetas (nivel 3, si existieran)
        for j, subfolder in enumerate(folder.get("folders", [])):
            is_last_subfolder = j == len(folder["folders"]) - 1
            print_folder(subfolder, prefix + ('   ' if is_last_folder else '│  '), is_last_subfolder)

    for team in data["teams"]:
        message.append(f"📂 EQUIPO: {team['name']} (ID: {team['id']})")
        if not team["spaces"]:
            message.append("  └─ No hay espacios en este equipo")
            continue
        for space in team["spaces"]:
            message.append(f"  ├─ 📁 ESPACIO: {space['name']} (ID: {space['id']})")
            # Listas sueltas en el espacio
            if not space["lists"] and not space["folders"]:
                message.append("  │  └─ No hay listas ni carpetas en este espacio")
                continue
            for i, list_item in enumerate(space["lists"]):
                is_last_list = (i == len(space["lists"]) - 1) and not space["folders"]
                prefix = "  │  └─" if is_last_list else "  │  ├─"
                message.append(f"{prefix} 📋 LISTA: {list_item['name']} (ID: {list_item['id']})")
            # Carpetas en el espacio
            for j, folder in enumerate(space["folders"]):
                is_last_folder = j == len(space["folders"]) - 1
                print_folder(folder, "  │  ", is_last_folder)

    message.append("\n== EJEMPLO DE USO PARA CREAR TAREA ==")
    message.append("Para crear una tarea, necesitas el ID de una lista. Por ejemplo:")

    # Encontrar la primera lista disponible para el ejemplo
    example_list = None
    for team in data["teams"]:
        for space in team["spaces"]:
            if space["lists"]:
                example_list = space["lists"][0]
                break
            for folder in space["folders"]:
                if folder["lists"]:
                    example_list = folder["lists"][0]
                    break
            if example_list:
                break
        if example_list:
            break
    self.connection_status_label.setText("Estado: Conectado")
    self.connection_status_label.setStyleSheet("QLabel { font-weight: bold; color: green; }")
    self.api_info_display.setText("\n".join(message))