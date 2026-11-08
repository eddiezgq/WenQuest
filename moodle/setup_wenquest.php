<?php
// This file is part of the WenQuest deployment package.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Let the WenQuest gateway talk to Moodle. Safe to run on every container start.
 *
 * - Web services over REST, and the built-in mobile service, which lets any user get a
 *   personal token with their own password (the gateway never uses an admin token for users).
 * - The multi-language filter, so bilingual course text also displays correctly in the classic view.
 *
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

define('CLI_SCRIPT', true);
require(__DIR__ . '/config.php');
require_once($CFG->libdir . '/filterlib.php');

set_config('enablewebservices', 1);
set_config('enablemobilewebservice', 1);
$protocols = array_filter(explode(',', (string) get_config('core', 'webserviceprotocols')));
if (!in_array('rest', $protocols)) {
    $protocols[] = 'rest';
    set_config('webserviceprotocols', implode(',', $protocols));
}
$DB->set_field('external_services', 'enabled', 1, ['shortname' => 'moodle_mobile_app']);

$systemcontext = context_system::instance();
$userrole = $DB->get_field('role', 'id', ['shortname' => 'user'], MUST_EXIST);
foreach (['webservice/rest:use', 'moodle/webservice:createmobiletoken'] as $capability) {
    assign_capability($capability, CAP_ALLOW, $userrole, $systemcontext->id, true);
}

filter_set_global_state('multilang', TEXTFILTER_ON);
filter_set_applies_to_strings('multilang', true);
if (core_component::get_component_directory('filter_multilang2')) {
    // Renders {mlang xx}...{mlang}, used for bilingual rich text (see the gateway's course builder).
    filter_set_global_state('multilang2', TEXTFILTER_ON);
    filter_set_applies_to_strings('multilang2', true);
}
set_config('filterall', 1);

// People sign in with their email as well as their user name.
set_config('authloginviaemail', 1);
// Deleted courses go to the recycle bin and stay there until someone deletes them for good (round 3).
set_config('categorybinenable', 1, 'tool_recyclebin');
set_config('categorybinexpiry', 0, 'tool_recyclebin');
// The same password rule as WenQuest's sign-up page: at least 8 characters with letters and digits
// (the gateway checks the letters; Moodle's policy cannot express "any letter").
set_config('passwordpolicy', 1);
set_config('minpasswordlength', 8);
set_config('minpassworddigits', 1);
set_config('minpasswordlower', 0);
set_config('minpasswordupper', 0);
set_config('minpasswordnonalphanum', 0);

// The gateway's service account for sign-up and administration (functions local_wenquest_account_*).
// Its token is derived from WQ_SECRET_KEY, which the gateway also knows, so nothing extra goes in .env.
$secret = (string) getenv('WQ_SECRET_KEY');
$service = $DB->get_record('external_services', ['shortname' => 'local_wenquest_accounts']);
if ($secret !== '' && $service) {
    require_once($CFG->dirroot . '/user/lib.php');
    $user = $DB->get_record('user', ['username' => 'wqservice', 'deleted' => 0, 'mnethostid' => $CFG->mnet_localhost_id]);
    if (!$user) {
        $id = user_create_user((object) [
            'auth' => 'manual', 'confirmed' => 1, 'mnethostid' => $CFG->mnet_localhost_id, 'username' => 'wqservice',
            'firstname' => 'WenQuest', 'lastname' => 'Service', 'email' => 'wqservice@invalid.invalid',
            'password' => bin2hex(random_bytes(24)) . 'Aa1!', 'emailstop' => 1,
        ], true, false);
        $user = $DB->get_record('user', ['id' => $id], '*', MUST_EXIST);
    }
    if ($user->suspended) {
        $DB->set_field('user', 'suspended', 0, ['id' => $user->id]);
    }
    $roleid = $DB->get_field('role', 'id', ['shortname' => 'wenquestservice']);
    if (!$roleid) {
        $roleid = create_role('WenQuest gateway service', 'wenquestservice',
            'Used only by the WenQuest gateway for sign-up and administration.');
        set_role_contextlevels($roleid, [CONTEXT_SYSTEM]);
    }
    foreach (['local/wenquest:manageaccounts', 'webservice/rest:use'] as $capability) {
        assign_capability($capability, CAP_ALLOW, $roleid, $systemcontext->id, true);
    }
    role_assign($roleid, $user->id, $systemcontext->id);
    if (!$DB->record_exists('external_services_users', ['externalserviceid' => $service->id, 'userid' => $user->id])) {
        $DB->insert_record('external_services_users', (object) [
            'externalserviceid' => $service->id, 'userid' => $user->id, 'timecreated' => time()]);
    }
    $token = substr(hash('sha256', 'wq-accounts:' . $secret), 0, 32);
    $DB->delete_records_select('external_tokens', 'externalserviceid = :s AND token <> :t',
        ['s' => $service->id, 't' => $token]);
    if (!$DB->record_exists('external_tokens', ['token' => $token])) {
        $DB->insert_record('external_tokens', (object) [
            'token' => $token, 'privatetoken' => random_string(64), 'tokentype' => EXTERNAL_TOKEN_PERMANENT,
            'userid' => $user->id, 'externalserviceid' => $service->id, 'contextid' => $systemcontext->id,
            'creatorid' => get_admin()->id, 'timecreated' => time(), 'name' => 'WenQuest gateway accounts',
        ]);
    }
    accesslib_clear_all_caches(true);
    mtrace('WenQuest accounts service ready.');
} else {
    mtrace('WenQuest accounts service not set up (WQ_SECRET_KEY missing or plugin not installed yet).');
}

// 在线编辑 Word、Excel（第 121 轮）：OnlyOffice 文档服务的地址和签名密钥。
// 浏览器走 learn.<主域名>/docs（Caddy 转给容器 docs）；Moodle 自己走内网 http://docs；
// 文档服务回调 Moodle 用公网地址（wwwroot），在服务器内网由 Caddy 的同名别名接住。插件（含 AI）一律关闭。
$docssecret = (string) getenv('DOCS_JWT_SECRET');
$appurl = rtrim((string) getenv('APP_URL'), '/');
if ($docssecret !== '' && $appurl !== '' && file_exists($CFG->dirroot . '/mod/onlyofficeeditor/version.php')) {
    set_config('documentserverurl', $appurl . '/docs', 'onlyofficeeditor');
    set_config('documentserverinternal', (string) (getenv('DOCS_INTERNAL_URL') ?: 'http://docs'), 'onlyofficeeditor');
    set_config('storageurl', '', 'onlyofficeeditor');
    set_config('documentserversecret', $docssecret, 'onlyofficeeditor');
    set_config('jwtheader', 'Authorization', 'onlyofficeeditor');
    set_config('disable_verify_ssl', 0, 'onlyofficeeditor');
    set_config('editor_security_plugin', 0, 'onlyofficeeditor');
    set_config('editor_security_macros', 0, 'onlyofficeeditor');
    set_config('editor_view_feedback', 0, 'onlyofficeeditor');
    mtrace('Online documents (OnlyOffice): ' . $appurl . '/docs');
} else {
    mtrace('Online documents not set up (DOCS_JWT_SECRET or APP_URL missing, or plugin not installed).');
}

mtrace('WenQuest gateway access: web services, mobile service and multi-language filters enabled.');
