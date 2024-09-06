<?php
// chat.php: This will send the user's message to the Python backend

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Get the message from the AJAX request
    $message = isset($_POST['message']) ? $_POST['message'] : '';

    // Check if the message is empty
    if (empty($message)) {
        echo json_encode(['error' => 'Message cannot be empty']);
        exit();
    }

    // API URL to the Gunicorn Flask app hosted at the given IP
    $apiUrl = 'http://15.165.204.98/chat';

    // Prepare the data for the POST request
    $data = json_encode(array('message' => $message));

    // Initialize a cURL session
    $ch = curl_init($apiUrl);

    // Set the cURL options
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));

    // Execute the request
    $response = curl_exec($ch);

    // Check for cURL errors
    if ($response === false) {
        $error = curl_error($ch);
        echo json_encode(['error' => 'Curl error: ' . $error]);
    } else {
        // Check if the response is a valid JSON
        $decodedResponse = json_decode($response, true);
        if (json_last_error() === JSON_ERROR_NONE) {
            // Return the JSON response from the Flask API
            echo $response;
        } else {
            // Handle invalid JSON response
            echo json_encode(['error' => 'Invalid JSON response from the API']);
        }
    }

    // Close the cURL session
    curl_close($ch);
}
