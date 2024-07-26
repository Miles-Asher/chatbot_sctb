<?php
require 'vendor/autoload.php';

use GuzzleHttp\Client;

$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->load();

$PINECONE_API_KEY = $_ENV['PINECONE_API_KEY'];
$OPENAI_API_KEY = $_ENV['OPENAI_API_KEY'];

function generate_embeddings($text) {
    global $OPENAI_API_KEY;
    $client = new Client();
    $response = $client->request('POST', 'https://api.openai.com/v1/embeddings', [
        'headers' => [
            'Authorization' => "Bearer $OPENAI_API_KEY",
            'Content-Type' => 'application/json',
        ],
        'json' => [
            'model' => 'text-embedding-ada-002',
            'input' => $text,
        ],
    ]);

    $data = json_decode($response->getBody(), true);
    return $data['data'][0]['embedding'];
}

function get_answer($question) {
    global $PINECONE_API_KEY;
    
    $embedding = generate_embeddings($question);
    
    $client = new Client();
    $response = $client->request('POST', 'https://your-pinecone-environment-url/query', [
        'headers' => [
            'Api-Key' => $PINECONE_API_KEY,
        ],
        'json' => [
            'vector' => $embedding,
            'top_k' => 1,
            'include_metadata' => true,
        ],
    ]);

    $data = json_decode($response->getBody(), true);
    if (isset($data['matches'][0]) && $data['matches'][0]['score'] >= 0.6) {
        return $data['matches'][0]['metadata']['answer'];
    }

    return get_gpt_answer($question);
}

function get_gpt_answer($question) {
    global $OPENAI_API_KEY;
    $client = new Client();
    $response = $client->request('POST', 'https://api.openai.com/v1/chat/completions', [
        'headers' => [
            'Authorization' => "Bearer $OPENAI_API_KEY",
        ],
        'json' => [
            'model' => 'gpt-3.5-turbo',
            'messages' => [['role' => 'user', 'content' => $question]],
            'max_tokens' => 150,
        ],
    ]);

    $data = json_decode($response->getBody(), true);
    return trim($data['choices'][0]['message']['content']);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    $question = $input['message'];
    
    $answer = get_answer($question);

    echo json_encode(['answer' => $answer]);
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot</title>
    <link rel="stylesheet" href="static/styles.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap">
</head>
<body>
    <header>
        <div class="header-container">
            <h1>Chat with Seoul City Tour Bus</h1>
        </div>
    </header>
    <main>
        <div class="chat-container">
            <div class="chat-log" id="chat-log"></div>
            <div class="chat-input-container">
                <div class="loading-indicator" id="loading-indicator" style="display: none;">Typing...</div>
                <input type="text" id="user-input" placeholder="Type a message...">
                <button id="send-button">Send</button>
                <button id="clear-button">Clear History</button>
            </div>
        </div>
    </main>
    <footer>
        <div class="footer-container">
            <p>&copy; 2024 Seoul City Tour Bus. All Rights Reserved.</p>
        </div>
    </footer>

    <script src="static/chatbot.js"></script>
</body>
</html>
