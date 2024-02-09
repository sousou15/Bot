import sys
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googletrans import Translator

# Recibimos el texto desde PHP
texto_usuario = ' '.join(sys.argv[1:])  # Unimos todos los argumentos en una sola cadena

try:
    # Creamos un objeto Translator de Google
    translator = Translator()

    # Traducimos el texto al inglés
    translated_text = translator.translate(texto_usuario, dest='en').text

    # Creamos un analizador de sentimientos de VADER
    analyzer = SentimentIntensityAnalyzer()

    # Obtenemos el análisis de sentimientos del texto traducido
    sentiment_scores = analyzer.polarity_scores(translated_text)

    # Convertimos el sentimiento detectado en un estado de ánimo
    compound_score = sentiment_scores['compound']

    if compound_score > 0.7:
        e_animo = "entusiasmado"
    elif 0.5 <= compound_score <= 0.7:
        e_animo = "contento"
    elif 0.3 <= compound_score < 0.5:
        e_animo = "emocionado"
    elif -0.3 <= compound_score <= 0.3:
        e_animo = "neutro"
    elif -0.5 <= compound_score < -0.3:
        e_animo = "mal"
    elif compound_score < -0.7:
        e_animo = "ansioso"
    else:
        e_animo = "triste"

    # Devolvemos el estado de ánimo al script PHP
    # print(e_animo, translated_text, compound_score)
    print(e_animo)

except Exception as e:
    print("Error:", e)
