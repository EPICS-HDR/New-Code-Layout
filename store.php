<?php
// Get form data
$username = $_POST['username'];
$password = $_POST['password'];
$v_password = $_POST['v_password'];
$email = $_POST['email'];

// Write data to CSV file
$file = fopen('user_data.csv', 'a'); // Open CSV file in append mode
fputcsv($file, array($username, $password, $v_password, $email)); // Write data to CSV
fclose($file); // Close file

// Redirect back to registration page
header('Location: registration.html');
exit();
?>
