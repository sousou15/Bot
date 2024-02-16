const axios = require('axios');
const dotenv = require('dotenv');
dotenv.config();

const { execSync } = require('child_process');

/**
 * Token de acceso del bot de Telegram.
 */
const botToken = process.env.bot_token;

/**
 * Clave de API de The Movie Database (TMDb).
 */
const apiKey = process.env.api_key; // Cambia por tu clave de API real

/**
 * Variable para almacenar el ID del último mensaje procesado.
 */
let lastProcessedMessageId = 0;

/**
 * Método para enviar mensajes al chat de Telegram.
 *
 * @param {number} chat_id El ID del chat.
 * @param {string} mensaje El mensaje a enviar.
 * @return {Promise<any>}
 */

async function enviarMensaje(chat_id, mensaje) {
    try {
        const response = await axios.get(`https://api.telegram.org/bot${botToken}/sendMessage`, {
            params: {
                chat_id: chat_id,
                text: mensaje
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error al enviar el mensaje:', error);
    }
}

/**
 * Función para manejar mensajes normales.
 *
 * @param {object} mensaje El mensaje a manejar.
 * @return {Promise<void>}
 */
async function manejarMensajeNormal(mensaje) {
    // Obtener el estado de ánimo del mensaje
    const estado_animo = mensaje.text;

    // Ejecutar el script de Python con el estado de ánimo como argumento
    const output = execSync(`python sentiments3.py "${estado_animo}"`).toString().trim();

    // Definimos los géneros deseados
    let genre_ids_array = [];

    // Switch para seleccionar los géneros según el estado de ánimo
    switch (output) {
        case "feliz":
            genre_ids_array = [28, 12, 16, 35];
            break;
        case "triste":
            genre_ids_array = [18, 80, 10749];
            break;
        case "neutro":
            genre_ids_array = [878, 12, 28, 27];
            break;
        case "contento":
            genre_ids_array = [28, 12, 878];
            break;
        case "emocionado":
            genre_ids_array = [18, 27, 53];
            break;
        case "mal":
            genre_ids_array = [99];
            break;
        case "entusiasmado":
            genre_ids_array = [35, 10751, 10749, 35];
            break;
        case "ansioso":
            genre_ids_array = [53, 9648, 10749, 27];
            break;
        default:
            await enviarMensaje(mensaje.chat.id, "Estado de ánimo no reconocido");
            return;
    }

    // Ejecutar la llamada a la API de TMDb para obtener películas de los géneros deseados
    try {
        // Realizamos la llamada a la API de TMDb para obtener películas de los géneros deseados
        const response = await axios.get('https://api.themoviedb.org/3/discover/movie', {
            params: {
                api_key: apiKey,
                with_genres: genre_ids_array.join(','), // Especificamos los géneros deseados
                language: 'es', // Establecemos el idioma de las películas (opcional)
                page: 1 // Página de resultados (opcional)
            }
        });

        // Construir el mensaje con las películas encontradas
        let mensaje_estado = `Películas adecuadas para cuando estás ${output}:\n`;
        await enviarMensaje(mensaje.chat.id, mensaje_estado);
        for (const movie of response.data.results) {
            let respuesta = `${movie.title} (${movie.release_date})\n`;
            respuesta += `Póster de la peli aquí: https://image.tmdb.org/t/p/w500${movie.poster_path}\n`;
            respuesta += `https://image.tmdb.org/t/p/original${movie.backdrop_path}\n\n`;
            // Enviar la respuesta al chat de Telegram
            await enviarMensaje(mensaje.chat.id, respuesta);
        }
    } catch (error) {
        // Manejamos errores de la API
        await enviarMensaje(mensaje.chat.id, 'Error al obtener películas: ' + error.message);
    }
}

// Bucle de polling para obtener actualizaciones de Telegram
setInterval(async () => {
    try {
        // Obtener actualizaciones
        const response = await axios.get(`https://api.telegram.org/bot${botToken}/getUpdates`);
        const updates = response.data;

        // Manejar cada mensaje
        for (const update of updates.result) {
            if (update.message) {
                const mensaje = update.message;
                // Verificar si el mensaje es más reciente que el último procesado
                if (mensaje.message_id > lastProcessedMessageId) {
                    if (mensaje.text && mensaje.text === '/start') {
                        await enviarMensaje(mensaje.chat.id, 'Hola! ¿Cómo te sientes hoy? Por favor, describe tu estado de ánimo. /help para consultar ayuda.');
                    } else if (mensaje.text && mensaje.text === '/help') {
                        // Aquí proporciona la ayuda que deseas dar al usuario, por ejemplo:
                        let ayuda = "Bienvenido al bot de películas! Aquí puedes encontrar recomendaciones de películas basadas en tu estado de ánimo.";
                        ayuda += " Para comenzar, simplemente usa /start y envía un mensaje describiendo cómo te sientes hoy cuando el bot te lo pida.";
                        ayuda += " El bot te entenderá y te recomendará algunas películas.";
                        ayuda += " El bot procesa el lenguaje natural.";
                        await enviarMensaje(mensaje.chat.id, ayuda);
                    } else {
                        // Si no es el comando /start, llamar a la función para manejar el mensaje normalmente
                        await manejarMensajeNormal(mensaje);
                    }
                    // Actualizar el ID del último mensaje procesado
                    lastProcessedMessageId = mensaje.message_id;
                }
            }
        }
    } catch (error) {
        console.error('Error al procesar actualizaciones:', error);
    }
}, 1000);
