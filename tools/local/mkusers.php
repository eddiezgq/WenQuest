<?php
define('CLI_SCRIPT', true);
require('/home/claude/local/moodle/config.php');
require_once($CFG->dirroot.'/user/lib.php');
foreach ([['teacher1','Wang','Laoshi','t'],['student1','Li','Xuesheng','s'],['student2','Chen','Tongxue','s'],['student3','Zhao','Tongxue','s']] as [$u,$f,$l,$k]) {
  if ($DB->record_exists('user',['username'=>$u])) continue;
  $id = user_create_user((object)['username'=>$u,'password'=>'Test#2026','firstname'=>$f,'lastname'=>$l,'email'=>"$u@example.com",'auth'=>'manual','confirmed'=>1,'mnethostid'=>$CFG->mnet_localhost_id]);
  if ($k==='t') role_assign($DB->get_field('role','id',['shortname'=>'coursecreator']), $id, context_system::instance()->id);
  echo "$u $id\n";
}
