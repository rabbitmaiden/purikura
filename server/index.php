<?php
  $action = !empty($_REQUEST['action']) ? $_REQUEST['action'] : false;


  

  if ($action===false) {
    echo "hey now";
    exit;
  }

  switch ($action) {
    case "reprint":
      reprint();
    case "getset":
      get_set();
    case "listsets":
      list_sets();
    case "photo":
      receive_photos();  
      break;
    case "overlay":
      receive_overlay();
      break;
    // Put photos somewhere to be composited and printed
    case "done":
      mark_done();
      break;
  }

  function reprint(){
    $file = !empty($_REQUEST['file']) ? $_REQUEST['file']: false;
    if ($file === false) {
      exit;
    }
    $file = "/home/pi/purikura/" . $file;
    if (is_file($file)) {
      echo `lp $file`;
    }
    exit;
  }


  function get_set(){
    $side = !empty($_REQUEST['side']) ? $_REQUEST['side'] : false;
    if (empty($side)) {
      error("missing side");
    }

    $dir = getdirname($side);
    $files = getfilesfromdir($dir);
    $file = false;
    if (!empty($files)) {
      $file = $files[0];
    }

    output(array("code" => $file));
  }

  function list_sets(){
    $side = !empty($_REQUEST['side']) ? $_REQUEST['side'] : false;
    if (empty($side)) {
      error("missing side");
    }
    $dir = getdirname($side);
    $files = getfilesfromdir($dir);
    output(array("codes"=> $files));
  }


  function receive_photos() {
    // Make sure we have four photos
    for ($i=1; $i<5; $i++) {
      $key = 'photo'.$i;
      if(empty($_FILES[$key])) {
        error('missing '.$key);
      }
    }

    // Generate hash for these photos
    $code = time();
    
    // Figure out what the last one was
    $last = file_get_contents('lastside');
    $next = ($last == 'BLUE') ? 'PINK' : 'BLUE';

    $dirname = getdirname($next, $code);

    // Make directory for the photos
    mkdir($dirname);

    // Move photos into the directory
    for($i = 1; $i < 5; $i++) {
      $file = $_FILES['photo'.$i];
      $filename = $file['name'];
      $newpath = $dirname."/".$filename.".jpg";
      move_uploaded_file($file['tmp_name'], $newpath);
    }
    
    file_put_contents('lastside', $next);
    logstuff ("Photo - created code $code - sent to $next");

    output(array(
      'code' => $code,
      'side' => $next
    ));
  }

  function receive_overlay() {
    $code = !empty($_REQUEST['code']) ? $_REQUEST['code'] : false;
    $side = !empty($_REQUEST['side']) ? $_REQUEST['side'] : false;
    $num = !empty($_REQUEST['num']) ? $_REQUEST['num'] : false;
    $data = !empty($_REQUEST['overlay']) ? $_REQUEST['overlay'] : false;

    if ($code === false || $side === false || $num === false || $data === false ){
      error("missing shit");
    }

    $filename = "overlay{$num}.png";

    $newpath = getdirname($side, $code) . '/' . $filename;

    $handle = fopen($newpath, 'w+');

    $img = str_replace('data:image/png;base64,', '', $data);
    $img = str_replace(' ', '+', $img);
    $img = base64_decode($img);

    fwrite($handle, $img);
    fclose($handle);

    logstuff("Draw - got overlay $filename for $code on $side");

    ok();
  }

  function mark_done() {
    $code = !empty($_REQUEST['code']) ? $_REQUEST['code'] : false;
    $side = !empty($_REQUEST['side']) ? $_REQUEST['side'] : false;
    if ($code === false || $side === false) {
      error("missing shit");
    }

    $dirname = getdirname($side, $code);

    if (!is_dir($dirname)) {
      error ("not a dir");
    }
    $time = time();
    $printdir = "/home/pi/purikura/print/queue/{$code}-{$side}";

    // Move directory to the print queue
    `mv $dirname $printdir`;

    logstuff ("Done - Marked $code on side $side as done");
    ok();
  }




  function getfilesfromdir($dir) {    
    $files = scandir($dir);
    foreach ($files as $i=>$file) {
      if ($file == '.' || $file == '..') {
        unset($files[$i]);
      }
    }
    sort($files);
    return $files;
  }


  function getdirname($side, $code=false) {
    $dirname = '/home/pi/purikura/server/photos/'.$side;
    if (!empty($code)) {
      $dirname .= '/'.$code;
    }
    return $dirname;
  }


  function logstuff($message) {
    $logfile = fopen('server.log', 'a+');
    fwrite($logfile, $message."\n");
    fclose($logfile);
  }

  function ok(){
    output(array('message'=>'ok'));
  }

  function error($message) {
    output(array('error'=>$message));
  }

  function output($data) {
    header("content-type: application/json");
    echo json_encode($data, JSON_PRETTY_PRINT);
    exit;
  }
