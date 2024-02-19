import requests
import time
import subprocess
import os
from dotenv import load_dotenv
import urllib.parse

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener el bot_token de las variables de entorno
bot_token = os.environ.get('bot_token')
api_key = os.environ.get('api_key')

last_processed_message_id = 0

def enviar_mensaje(chat_id, mensaje):
    """
    Envía un mensaje al chat de Telegram.

    :param chat_id: El ID del chat.
    :param mensaje: El mensaje a enviar.
    :return: La respuesta JSON del servidor de Telegram.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {'chat_id': chat_id, 'text': mensaje}
    response = requests.get(url, params=params)
    return response.json()

def obtener_videos(movie_id):
    """
    Obtiene los videos asociados a una película desde la API de The Movie Database (TMDb).

    :param movie_id: El ID de la película.
    :return: Una lista de videos asociados a la película.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
    params = {'api_key': api_key}
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('results', [])

def manejar_mensaje_normal(mensaje):
    """
    Maneja mensajes normales.

    :param mensaje: El mensaje a manejar.
    """
    global last_processed_message_id

    estado_animo = mensaje['text']
    output = subprocess.check_output(["python", "sentiments3.py", estado_animo]).decode().strip()

    genre_ids_dict = {
        "feliz": [28, 12, 878],
        "triste": [18, 80, 10749],
        "neutro": [878, 12, 28, 27],
        "emocionado":[99, 18],
        "contento": [35, 14, 53],
        "mal": [35, 16, 10402, 10770],
        "entusiasmado": [35, 10751, 10749, 35],
        "ansioso": [53, 9648, 10749, 27]
    }

    if output not in genre_ids_dict:
        enviar_mensaje(mensaje['chat']['id'], "Estado de ánimo no reconocido")
        return

    genre_ids_array = genre_ids_dict[output]

    try:
        response = requests.get("https://api.themoviedb.org/3/discover/movie", params={
            'api_key': api_key,
            'with_genres': ','.join(map(str, genre_ids_array)),
            'language': 'es',
            'page': 1
        })
        data = response.json()

        mensaje_estado = f"Películas adecuadas para cuando estás {output}:\n"
        enviar_mensaje(mensaje['chat']['id'], mensaje_estado)
        
        for movie in data['results']:
            respuesta = f"*{movie['title']}* ({movie['release_date']})\n\n"
            respuesta += f"📝Puntuación: {movie['vote_average']}/10 - ({movie['vote_count']}) votos\n\n"
            respuesta += f"🎬Sinopsis: {movie['overview']}\n\n"
            respuesta += f"Póster de la peli aquí: https://image.tmdb.org/t/p/w500{movie['poster_path']}\n"
            respuesta += f"https://image.tmdb.org/t/p/original{movie['backdrop_path']}\n\n"
            termino_busqueda = movie['title'] + " película" + movie['release_date']
            # Codificar el término de búsqueda
            termino_busqueda_codificado = urllib.parse.quote(termino_busqueda)
            # Crear la URL del enlace a Google con el término de búsqueda
            respuesta += f"🌐Google: https://www.google.com/search?q={termino_busqueda_codificado}\n\n"
              # Obtener los videos de la película
            videos = obtener_videos(movie['id'])
            
            # Agregar los trailers y videos a la respuesta
            for video in videos:
                if video['type'] == 'Trailer':
                    respuesta += f"Trailer: {video['name']} - [Ver](https://www.youtube.com/watch?v={video['key']})\n"

            enviar_mensaje(mensaje['chat']['id'], respuesta)
    except Exception as e:
        enviar_mensaje(mensaje['chat']['id'], f"Error al obtener películas: {str(e)}")

def poll_updates():
    """
    Realiza el polling de actualizaciones de Telegram y maneja los mensajes.
    """
    global last_processed_message_id

    while True:
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getUpdates")
        updates = response.json()['result']

        for update in updates:
            if 'message' in update:
                mensaje = update['message']
                if mensaje['message_id'] > last_processed_message_id:
                    if 'text' in mensaje:
                        if mensaje['text'] == '/start':
                            enviar_mensaje(mensaje['chat']['id'], 'Hola! ¿Cómo te sientes hoy? Por favor, describe tu estado de ánimo. /help para consultar ayuda.')
                        elif mensaje['text'] == '/help':
                            ayuda = "Bienvenido al bot de películas! Aquí puedes encontrar recomendaciones de películas basadas en tu estado de ánimo.\n"
                            ayuda += "Para comenzar, simplemente usa /start y envía un mensaje describiendo cómo te sientes hoy cuando el bot te lo pida.\n"
                            ayuda += "El bot te entenderá y te recomendará algunas películas.\n"
                            ayuda += "El bot procesa el lenguaje natural."
                            enviar_mensaje(mensaje['chat']['id'], ayuda)
                        else:
                            manejar_mensaje_normal(mensaje)
                    last_processed_message_id = mensaje['message_id']

        time.sleep(1)

if __name__ == "__main__":
    poll_updates()
