import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener el bot_token de las variables de entorno
bot_token = os.environ.get('bot_token')

# URL base
base_url = f"https://api.telegram.org/bot{bot_token}/"
#GetUpdates
def get_updates():
    url = base_url + "getUpdates"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code)
        return None
updates = get_updates()
#Ver los update_id
def get_update_ids():
    url = base_url + "getUpdates"
    response = requests.get(url)
    if response.status_code == 200:
        updates = response.json()['result']
        update_ids = [update['update_id'] for update in updates]
        return update_ids
    else:
        print("Error:", response.status_code)
        return None

def get_updates_with_offset(update_ids):
    for update_id in update_ids:
        url = base_url + f"getUpdates?offset={update_id + 1}"
        # Send the GET request
        response = requests.get(url)
        if response.status_code == 200:
            updates = response.json()['result']
            print(updates)
        else:
            print("Error:", response.status_code)
# Call the function to get update IDs
update_ids = get_update_ids()
# Call the function to get updates with offset for each update ID
if update_ids is not None:
    get_updates_with_offset(update_ids)