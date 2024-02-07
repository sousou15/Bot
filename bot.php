<?php

require 'vendor/autoload.php';
use GuzzleHttp\Client;

// Token de acceso del bot de Telegram
$bot_token = '6940266318:AAFY6syLocYDKe3ZtTFC1lTWjGkp5YpgFL0';

$api_key = 'b2d11b0c7ab0e17b36609db82291a79f'; // Cambia 'TU_CLAVE_DE_API_DE_TMDB' por tu clave de API real

// Variable para almacenar el ID del último mensaje procesado
$last_processed_message_id = 0;

// Método para enviar mensajes al chat de Telegram
function enviarMensaje($chat_id, $mensaje) {
    global $bot_token;
    $client = new Client();
    $response = $client->request('GET', "https://api.telegram.org/bot$bot_token/sendMessage", [
        'query' => [
            'chat_id' => $chat_id,
            'text' => $mensaje
        ]
    ]);
    return $response->getBody();
}

// Definir la función para manejar los mensajes recibidos
function manejarMensaje($mensaje) {
    global $client, $api_key, $last_processed_message_id;

    // Verificar si el mensaje es el comando /start
    if ((isset($mensaje['text']) && $mensaje['text']) == '/start') {
        // Verificar si ya se envió el mensaje de inicio antes
        if ($mensaje['message_id'] > $last_processed_message_id) {
            enviarMensaje($mensaje['chat']['id'], 'Hola! ¿Cómo te sientes hoy? Por favor, describe tu estado de ánimo.');
            // Actualizar el ID del último mensaje procesado
            $last_processed_message_id = $mensaje['message_id'];
        }
    } else {
        // Si no es el comando /start, manejar el mensaje normalmente
        manejarMensajeNormal($mensaje);
        $last_processed_message_id = $mensaje['message_id'];

    }
}

function manejarMensajeNormal($mensaje) {
    global $client, $api_key;

    // Obtener el estado de ánimo del mensaje
    $estado_animo = $mensaje['text'];

    // Ejecutar el script de Python con el estado de ánimo como argumento
    $output = exec("python sentiments.py \"$estado_animo\"");

    // Definimos los géneros deseados
    $genre_ids_array = [];

    // Switch para seleccionar los géneros según el estado de ánimo
    switch ($output) {
        case "feliz":
            $genre_ids_array = [28, 12, 16, 35];
            break;
        case "triste":
            $genre_ids_array = [10752, 18, 80, 10751];
            break;    
        case "neutro":
            $genre_ids_array = [878, 12, 28, 27];
            break;
        case "contento":
            $genre_ids_array = [28, 12, 878];
            break;
        case "emocionado":
            $genre_ids_array = [18, 27, 53];
            break;
        case "entusiasmado":
            $genre_ids_array = [35, 10751, 10749];
            break;
        case "ansioso":
            $genre_ids_array = [53, 9648, 10749];
            break;
        default:
            enviarMensaje($mensaje['chat']['id'], "Estado de ánimo no reconocido");
            exit;
    }


    // Ejecutar la llamada a la API de TMDb para obtener películas de los géneros deseados
    try {
        // Realizamos la llamada a la API de TMDb para obtener películas de los géneros deseados
        $client = new Client([
            'base_uri' => 'https://api.themoviedb.org/3/',
        ]);
        $response = $client->request('GET', 'discover/movie', [
            'query' => [
                'api_key' => $api_key,
                'with_genres' => implode(',', $genre_ids_array), // Especificamos los géneros deseados
                'language' => 'es', // Establecemos el idioma de las películas (opcional)
                'page' => 1 // Página de resultados (opcional)
            ]
        ]);

        // Decodificamos la respuesta JSON
        $data = json_decode($response->getBody(), true);

        // Construir el mensaje con las películas encontradas
        $respuesta = "Películas adecuadas para cuando estás $output:\n";
        foreach ($data['results'] as $movie) {
            $respuesta .= $movie['title'] . " (" . $movie['release_date'] . ")\n";
            $respuesta .= "https://image.tmdb.org/t/p/w500" . $movie['poster_path'] . "\n";
            $respuesta .= "https://image.tmdb.org/t/p/original" . $movie['backdrop_path'] . "\n\n";
        }

        // Enviar la respuesta al chat de Telegram
        enviarMensaje($mensaje['chat']['id'], $respuesta);
    } catch (Exception $e) {
        // Manejamos errores de la API
        enviarMensaje($mensaje['chat']['id'], 'Error al obtener películas: ' . $e->getMessage());
    }
}



// Inicializar el cliente Guzzle HTTP
$client = new Client([
    'base_uri' => 'https://api.themoviedb.org/3/',
]);

// Bucle de polling para obtener actualizaciones de Telegram
while (true) {
    // Obtener actualizaciones
    $response = $client->request('GET', "https://api.telegram.org/bot$bot_token/getUpdates");
    $updates = json_decode($response->getBody(), true);

    // Manejar cada mensaje
    foreach ($updates['result'] as $update) {
        if (isset($update['message'])) {
            $mensaje = $update['message'];
            // Verificar si el mensaje es más reciente que el último procesado
            if ($mensaje['message_id'] > $last_processed_message_id) {
                if (isset($mensaje['text']) && $mensaje['text'] == '/start') {
                    enviarMensaje($mensaje['chat']['id'], 'Hola! ¿Cómo te sientes hoy? Por favor, describe tu estado de ánimo.');
                } else {
                    // Si no es el comando /start, llamar a la función para manejar el mensaje normalmente
                    manejarMensajeNormal($mensaje);
                }
                // Actualizar el ID del último mensaje procesado
                $last_processed_message_id = $mensaje['message_id'];
            }
        }
    }
    // Esperar un segundo antes de la próxima consulta (evitar exceso de consumo de recursos)
    sleep(1);
}


?>