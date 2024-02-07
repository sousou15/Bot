from telegram.ext import Updater, CommandHandler
from queue import Queue

def start(update, context):
    update.message.reply_text('¡Hola! Gracias por iniciar el bot.')

def main():
    updater = Updater("6940266318:AAFY6syLocYDKe3ZtTFC1lTWjGkp5YpgFL0", use_context=True, update_queue=Queue())

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
