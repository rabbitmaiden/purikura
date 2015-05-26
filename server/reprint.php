<?php


$dirs = scandir("./print/printed");
$files = array();
foreach ($dirs as $dir) {
	if ($dir == '.' || $dir == '..') {
		continue;
	}
  $fulldir = 'print/printed/'.$dir;
  if (!is_dir($fulldir)){
    continue;
  }
	if (is_file($fulldir."/composite.jpg")) {
		$files[] = $fulldir."/composite.jpg";
	}
}

rsort($files)
?>
<!doctype html>
<html>
  <head>
    <style>
.photo {
  width: 300px;
  height: 500px;
  float: left;
  margin-right: 20px;
  margin-bottom: 40px;
  text-align: center;
}

.photo,
.photo a{
  color: #ff00ff;
}

.photo a{
  text-decoration: none;
  font-weight: bold;
}
    </style>
  </head>
  <body>
    <?php 
      foreach($files as $file) {
        echo <<<HTML
    <div class="photo">
      <a href="/{$file}"><img src="{$file}" width="300"></a><br>
      {$file}<br/><br>
      <a href="index.php?action=reprint&file={$file}">Reprint</a>
    </div>
HTML;
      }
    ?>

  <script>
window.setTimeout(function(){
  location.reload();
}, 15000);
  </script>
  </body>
</html>
