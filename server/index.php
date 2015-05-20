<?php
  $action = !empty($_REQUEST['action']) ? $_REQUEST['action'] : false;

  $logfile = fopen('server.log', 'a+');
  

  if ($action===false) {
    echo "hey now";
    exit;
  }

  switch ($action) {
    case "photo":
      receive_photos();  
      break;
    case "overlay":
      break;
    // Put photos somewhere to be composited and printed
    case "done":
      break;
  }


  // Upload photos from photopi
  
  // Poll for info on latest batch

  // Save photos while drawing


  function receive_photos() {
    // Make sure we have four photos
    print_r($_FILES);
    exit;

    // Generate hash for these photos
    $code = md5(time());
    
    // Figure out what the last one was
    $last = file_get_contents('lastside');
    $next = ($last == 'BLUE') ? 'PINK' : 'BLUE';

    $dirname = '/home/pi/purikura/server/photos/'.$next.'/'.$code;

    // Make directory for the photos
    mkdir($dirname);

    // Move photos into the directory
    foreach ($_FILES['photos']['name'] as $tmppath) {
      $pieces = explode("/", $tmppath);
      $filename = array_pop($pieces);

      $newpath = $dirname."/".$filename;
      move_uploaded_file($tmppath, $newpath);
    }
    
    file_put_contents('last', $next);
    logstuff ("Photo - created code $code - sent to $next");

    output(array(
      'code' => $code,
      'side' => $next
    ));
  }

  function logstuff($message) {
    fwrite($logfile, $message."\n");
  }

  function output($data) {
    header("content-type: text/plain");
    echo json_encode($data, JSON_PRETTY_PRINT);
    exit;
  }
