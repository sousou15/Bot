<?php

require 'vendor/autoload.php';
use GuzzleHttp\Client;

// Definimos el texto de entrada del usuario
$texto_usuario = "Estoy super aburrido";

$e_animo = exec("python sentiments.py \"" . $texto_usuario . "\"");





// Definimos los géneros deseados
$genre_ids_array = [];

switch ($e_animo) {
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
        echo "Estado de ánimo no reconocido";
        exit;
}

// Definimos la clave de la API de TMDb
$api_key = 'b2d11b0c7ab0e17b36609db82291a79f'; // Reemplaza con tu API Key de TMDb

// Configuramos el cliente Guzzle HTTP
$client = new Client([
    'base_uri' => 'https://api.themoviedb.org/3/',
]);

try {
    // Realizamos la llamada a la API de TMDb para obtener películas de los géneros deseados
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

    // Mostramos las películas de los géneros deseados
    echo "Películas adecuadas para cuando estás " . $e_animo . ":\n";
    foreach ($data['results'] as $movie) {
        echo $movie['title'] . " (" . $movie['release_date'] . ")\n";
        echo "<img src='https://image.tmdb.org/t/p/w500" . $movie['poster_path'] . "' alt='Póster de " . $movie['title'] . "'><br>";
        echo "<img src='https://image.tmdb.org/t/p/original" . $movie['backdrop_path'] . "' alt='Fondo de " . $movie['title'] . "'><br>";
    }
} catch (Exception $e) {
    // Manejamos errores de la API
    echo 'Error al obtener películas: ' . $e->getMessage();
}

?>
