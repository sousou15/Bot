import sys
from googletrans import Translator
from textblob import TextBlob

# Recibimos el texto desde PHP
texto_usuario = ' '.join(sys.argv[1:])  # Unimos todos los argumentos en una sola cadena

try:
    # Creamos un objeto Translator de Google
    translator = Translator()

    # Traducimos el texto al inglés
    translated_text = translator.translate(texto_usuario, dest='en').text

    # Creamos un nuevo objeto TextBlob con el texto traducido
    translated_blob = TextBlob(translated_text)

    # Obtenemos el sentimiento del texto traducido
    sentimiento = translated_blob.sentiment

    # Convertimos el sentimiento detectado en un estado de ánimo
    e_animo = ""
    print("Polaridad del sentimiento:", sentimiento.polarity)

    if sentimiento.polarity > 0.3:
        e_animo = "feliz"
    elif sentimiento.polarity < -0.3:
        e_animo = "triste"
    elif 0 <= sentimiento.polarity <= 0.3:
        e_animo = "neutro"
    elif 0.3 < sentimiento.polarity <= 0.5:
        e_animo = "contento"
    elif 0.5 < sentimiento.polarity <= 0.7:
        e_animo = "emocionado"
    elif 0.7 < sentimiento.polarity <= 0.9:
        e_animo = "entusiasmado"
    else:
        e_animo = "ansioso"

    # Devolvemos el estado de ánimo al script PHP
    print(e_animo)

except Exception as e:
    print("Error:", e)
