import sys
from googletrans import Translator
from transformers import pipeline

# Recibimos el texto desde PHP
texto_usuario = ' '.join(sys.argv[1:])  # Unimos todos los argumentos en una sola cadena

try:
    # Creamos un objeto Translator de Google
    translator = Translator()

    # Traducimos el texto al inglés
    translated_text = translator.translate(texto_usuario, dest='en').text

    # Cargamos un modelo pre-entrenado para análisis de sentimientos
    sentiment_analysis = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    # Obtenemos el análisis de sentimientos del texto traducido
    sentiment_result = sentiment_analysis(translated_text)[0]

    # Extraemos la etiqueta de sentimiento y la probabilidad
    label = sentiment_result['label']
    score = sentiment_result['score']

    # Convertimos el sentimiento detectado en un estado de ánimo
    if score > 0.7:
        e_animo = "entusiasmado"
    elif 0.5 <= score <= 0.7:
        e_animo = "emocionado"
    elif 0.3 <= score < 0.5:
        e_animo = "contento"
    elif -0.3 <= score <= 0.3:
        e_animo = "neutro"
    elif -0.5 <= score < -0.3:
        e_animo = "mal"
    elif score < -0.7:
        e_animo = "ansioso"
    else:
        e_animo = "triste"


    # Devolvemos el estado de ánimo al script PHP
    # print(e_animo, translated_text, score)       
    print(e_animo)

except Exception as e:
    print("Error:", e)
