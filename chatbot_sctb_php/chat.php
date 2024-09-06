<?php
// chat.php: This will send the user's message to the Python backend

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $message = isset($_POST['message']) ? $_POST['message'] : '';

    if (empty($message)) {
        echo json_encode(['error' => 'Message cannot be empty']);
        exit();
    }

    $apiUrl = 'http://15.165.204.98/chat';
    $data = json_encode(array('message' => $message));

    $ch = curl_init($apiUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));

    $response = curl_exec($ch);

    // Log raw response
    file_put_contents('response_log.txt', $response, FILE_APPEND);

    if ($response === false) {
        $error = curl_error($ch);
        echo json_encode(['error' => 'Curl error: ' . $error]);
    } else {
        $decodedResponse = json_decode($response, true);
        if (json_last_error() === JSON_ERROR_NONE) {
            echo $response;
        } else {
            echo json_encode(['error' => 'Invalid JSON response from the API']);
        }
    }

    curl_close($ch);
}
