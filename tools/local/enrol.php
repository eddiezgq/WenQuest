<?php
define('CLI_SCRIPT', true);
require('/home/claude/local/moodle/config.php');
require_once($CFG->libdir.'/enrollib.php');
$courseid = (int)($argv[1] ?? 2);
$sr = $DB->get_field('role','id',['shortname'=>'student']);
foreach (['student1','student2','student3'] as $u) { $id=$DB->get_field('user','id',['username'=>$u]); enrol_try_internal_enrol($courseid, $id, $sr); echo "$u\n"; }
