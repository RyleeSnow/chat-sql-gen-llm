<?php
// Define the API endpoint
$apiUrl = "http://localhost:8000/generate";  // Optional: change this to the API endpoint

// Record the start time
$startTime = microtime(true);

// Prepare the request data

if (isset($_GET['question'])) {
    $question = $_GET['question'];
} else {
    $question = "";
}

if (isset($_GET['examples'])) {
    $examples = $_GET['examples'];
} else {
    $examples = "";
}

$data = [
    "question" => $question,
    "examples" => $examples,
    "prompt_file" => "/home/hury1001/multi_channel_bert_full_module/llm/prompt.md", // Optional: specify if different from default
    "metadata_file" => "/home/hury1001/multi_channel_bert_full_module/llm/metadata.sql" // Optional: specify if different from default
];

// Initialize cURL session
$ch = curl_init($apiUrl);

// Set cURL options
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));

// Execute the request
$response = curl_exec($ch);

// Check for errors
if ($response === false) {
    $error = curl_error($ch);
    echo "cURL Error: $error";
} else {
    // Decode the response
    $responseData = json_decode($response, true);
    if (isset($responseData['query'])) {
        echo "Generated SQL Query: " . $responseData['query'] . "\n";  // Optional: hide it if not needed
    } else {
        echo "Error: " . $responseData['detail'] . "\n";  // Optional: hide it if not needed
    }
}

// Close the cURL session
curl_close($ch);
?>