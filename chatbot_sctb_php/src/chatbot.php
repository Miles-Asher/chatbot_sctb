<?php
require 'vendor/autoload.php';

use GuzzleHttp\Client;
use Dotenv\Dotenv;

$dotenv = Dotenv::createImmutable(__DIR__);
$dotenv->load();

class FAQChatbot {
    private $client;
    private $apiKey;
    private $modelId;

    public function __construct($modelId) {
        $this->client = new Client();
        $this->apiKey = $_ENV['OPENAI_API_KEY'];
        $this->modelId = $modelId;
    }

    public function getAnswer($question) {
        $prompt = $this->generatePrompt($question);

        $response = $this->client->post('https://api.openai.com/v1/chat/completions', [
            'headers' => [
                'Authorization' => 'Bearer ' . $this->apiKey,
                'Content-Type' => 'application/json',
            ],
            'json' => [
                'model' => $this->modelId,
                'messages' => [
                    ['role' => 'system', 'content' => 'You are a helpful assistant for a tour bus company.'],
                    ['role' => 'user', 'content' => $prompt],
                ],
                'max_tokens' => 150,
            ],
        ]);

        $responseBody = json_decode($response->getBody(), true);

        if (isset($responseBody['choices']) && !empty($responseBody['choices'])) {
            return $responseBody['choices'][0]['message']['content'];
        } else {
            return 'Sorry, I couldn\'t find an answer to your question.';
        }
    }

    private function generatePrompt($question) {
        return "Question: $question\n\nAnswer:";
    }
}

// Example instantiation (for standalone testing purposes)
// $modelId = 'ft:gpt-3.5-turbo-1106:personal:sctb-proto:9qGUJ2Fx';
// $chatbot = new FAQChatbot($modelId);
// $question = "Where do I get on the bus?";
// echo $chatbot->getAnswer($question);
?>
