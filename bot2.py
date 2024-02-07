import requests

# Token de acceso del bot de Telegram
bot_token = '6940266318:AAFY6syLocYDKe3ZtTFC1lTWjGkp5YpgFL0'

# Método para enviar mensajes al chat de Telegram
def enviarMensaje(chat_id, mensaje):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {'chat_id': chat_id, 'text': mensaje}
    response = requests.get(url, params=params)
    return response.json()

# Función para manejar los mensajes recibidos
def manejarMensaje(mensaje):
    # Verificar si el mensaje es el comando /start
    if 'text' in mensaje and mensaje['text'] == '/start':
        # Enviar mensaje de bienvenida y pedir al usuario cómo se siente
        enviarMensaje(mensaje['chat']['id'], '¡Hola! ¿Cómo te sientes hoy?')
        return True  # Indicar que se ha procesado el comando /start
    elif 'text' in mensaje:
        # Procesar el estado de ánimo utilizando un script externo de Python
        estado_animo = mensaje['text']
        # Aquí debes ejecutar tu script de Python externo y obtener el resultado
        # Ejemplo:
        # resultado = subprocess.getoutput(f"python sentiments.py \"{estado_animo}\"")
        
        # Supongamos que el resultado es una lista de películas
        # Aquí reemplaza este ejemplo con tu lógica real para obtener películas
        peliculas = ["Titanic", "Matrix", "El Padrino"]
        
        # Construir el mensaje de respuesta con la lista de películas
        mensaje_respuesta = f"Aquí tienes algunas películas para cuando te sientes {estado_animo}:\n"
        mensaje_respuesta += "\n".join(peliculas)
        
        # Enviar el mensaje de respuesta al chat de Telegram
        enviarMensaje(mensaje['chat']['id'], mensaje_respuesta)
        return False  # Indicar que se ha procesado un mensaje después de /start

# Bucle de polling para obtener actualizaciones de Telegram
def obtenerActualizaciones():
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(url)
    updates = response.json()
    return updates.get('result', [])

def procesarMensajes():
    last_update_id = None
    esperando_inicio = True  # Variable para controlar si estamos esperando el comando /start
    while True:
        updates = obtenerActualizaciones()
        for update in updates:
            if last_update_id is None or update['update_id'] > last_update_id:
                last_update_id = update['update_id']
                if 'message' in update:
                    mensaje_procesado = False
                    if esperando_inicio:
                        mensaje_procesado = manejarMensaje(update['message'])
                        if mensaje_procesado:
                            esperando_inicio = False
                    else:
                        mensaje_procesado = manejarMensaje(update['message'])
                    if mensaje_procesado:
                        last_update_id = update['update_id']  # Actualizar el último ID procesado si se ha procesado un mensaje

# Iniciar el procesamiento de mensajes
procesarMensajes()