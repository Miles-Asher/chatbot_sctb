<?php
// chat.php: This will send the user's message to the Python backend

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Get the message from the AJAX request
    $message = $_POST['message'];

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

    // Check for errors
    if (curl_errno($ch)) {
        echo 'Error: ' . curl_error($ch);
    } else {
        // Return the response from the Python API
        echo $response;
    }

    // Close the cURL session
    curl_close($ch);
}
?>
