import subprocess
from telegram import Update
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, filters

# Token de acceso al bot proporcionado por BotFather
TOKEN = '6940266318:AAFY6syLocYDKe3ZtTFC1lTWjGkp5YpgFL0'

# Función para manejar el comando /start
def start(update, context):
    update.message.reply_text("¡Hola! ¿Cuál es tu estado de ánimo?")

# Función para manejar los mensajes de texto
def echo(update, context):
    estado_animo = update.message.text
    output = subprocess.getoutput(f"python sentiments.py \"{estado_animo}\"")
    
    switch_output = {
        "feliz": [28, 12, 16, 35],
        "triste": [10752, 18, 80, 10751],
        "neutro": [878, 12, 28, 27],
        "contento": [28, 12, 878],
        "emocionado": [18, 27, 53],
        "entusiasmado": [35, 10751, 10749],
        "ansioso": [53, 9648, 10749]
    }

    genre_ids_array = switch_output.get(output, [])
    
    if not genre_ids_array:
        update.message.reply_text("Estado de ánimo no reconocido")
        return

    try:
        url = 'https://api.themoviedb.org/3/discover/movie'
        params = {'api_key': 'b2d11b0c7ab0e17b36609db82291a79f', 'with_genres': ','.join(map(str, genre_ids_array)), 'language': 'es', 'page': 1}
        response = requests.get(url, params=params)
        data = response.json()

        respuesta = "Películas adecuadas para cuando estás {}:\n".format(estado_animo)
        for movie in data['results']:
            respuesta += "{} ({})\n".format(movie['title'], movie['release_date'])
            respuesta += "https://image.tmdb.org/t/p/w500{}\n".format(movie['poster_path'])
            respuesta += "https://image.tmdb.org/t/p/original{}\n\n".format(movie['backdrop_path'])

        update.message.reply_text(respuesta)
    except Exception as e:
        update.message.reply_text('Error al obtener películas: {}'.format(e))

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.text & ~filters.command, echo))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
