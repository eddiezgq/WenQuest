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

mtrace('WenQuest gateway access: web services, mobile service and multi-language filters enabled.');
