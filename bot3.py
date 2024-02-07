from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import ytdl
import ytsearch

# Token de tu bot de Telegram
token = '6697268667:AAGLMdTC8XYqAfn46sIuMQZghrbYbx7Dkdg'

# Crear el objeto Updater y el objeto bot
updater = Updater(token)
bot = updater.bot

# Manejador del comando /start
def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id, '¡Hola! Puedes buscarme canciones enviando el comando /play seguido de una consulta o enlace de YouTube.')

# Manejador del comando /play
def play(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    query = context.args[0] if context.args else None

    try:
        # Verificar si la consulta es un enlace de YouTube
        if ytdl.validate_url(query):
            # Si es un enlace, usar directamente
            audio_url = query
            context.bot.send_audio(chat_id, audio_url)
        else:
            # Si no es un enlace, realizar búsqueda y obtener el primer resultado
            result = ytsearch.search(query)
            if result and result['videos'] and len(result['videos']) > 0:
                first_video = result['videos'][0]
                audio_url = first_video['url']
                context.bot.send_audio(chat_id, audio_url)
            else:
                context.bot.send_message(chat_id, 'No se encontraron resultados para la búsqueda.')
    except Exception as e:
        print(f'Error al obtener la información del video: {str(e)}')
        context.bot.send_message(chat_id, 'Error al obtener la información del video.')

# Agregar los manejadores al objeto updater
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('play', play))

# Iniciar el bot
updater.start_polling()
updater.idle()
