<?php
require 'vendor/autoload.php';

use Slim\Factory\AppFactory;
use Slim\Psr7\Response;
use Slim\Psr7\Request;
use Slim\Routing\RouteCollectorProxy;

// Load chatbot
require 'src/chatbot.php';

$app = AppFactory::create();

$app->get('/', function (Request $request, Response $response) {
    $response->getBody()->write(file_get_contents('index.html'));
    return $response;
});

// Serve static files
$app->group('/static', function (RouteCollectorProxy $group) {
    $group->get('/{file:.+}', function (Request $request, Response $response, array $args) {
        $filePath = __DIR__ . '/static/' . $args['file'];
        if (file_exists($filePath)) {
            $response->getBody()->write(file_get_contents($filePath));
            return $response->withHeader('Content-Type', mime_content_type($filePath));
        }
        return $response->withStatus(404, 'File not found');
    });
});

$app->post('/chat', function (Request $request, Response $response) {
    $data = json_decode($request->getBody(), true);
    $question = $data['message'] ?? '';

    // Initialize chatbot with fine-tuned model ID
    $modelId = 'ft:gpt-3.5-turbo-1106:personal:sctb-proto:9qGUJ2Fx';
    $chatbot = new FAQChatbot($modelId);
    $answer = $chatbot->getAnswer($question);

    $response->getBody()->write(json_encode(["answer" => $answer]));
    return $response->withHeader('Content-Type', 'application/json');
});

$app->run();
