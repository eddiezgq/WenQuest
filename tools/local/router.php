<?php
// Local stand-in for Apache in front of Moodle 5.2 (docroot = public/).
$root = '/home/claude/local/moodle/public';
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
// script.php/extra/path  ->  run script.php with PATH_INFO (pluginfile.php, webservice/pluginfile.php, ...)
if (preg_match('#^(.+?\.php)(/.*)$#', $path, $m) && is_file($root.$m[1])) {
    $_SERVER['SCRIPT_NAME'] = $m[1];
    $_SERVER['SCRIPT_FILENAME'] = $root.$m[1];
    $_SERVER['PHP_SELF'] = $m[1].$m[2];
    $_SERVER['PATH_INFO'] = rawurldecode($m[2]);
    chdir(dirname($root.$m[1]));
    require $root.$m[1];
    return true;
}
if ($path !== '/' && is_file($root.$path)) return false;
if (is_dir($root.$path) && is_file(rtrim($root.$path,'/').'/index.php')) {
    $_SERVER['SCRIPT_NAME'] = rtrim($path,'/').'/index.php';
    chdir(rtrim($root.$path,'/'));
    require rtrim($root.$path,'/').'/index.php';
    return true;
}
$_SERVER['SCRIPT_NAME'] = '/r.php';
require $root.'/r.php';
