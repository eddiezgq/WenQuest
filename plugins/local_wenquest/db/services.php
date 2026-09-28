<?php
// This file is part of WenQuest - https://wenquestrobotics.com
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Web service functions. They are added to the built-in mobile service, so the gateway can
 * call them with each user's own token; Moodle capabilities decide what that user may do.
 *
 * @package    local_wenquest
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$functions = [
    'local_wenquest_get_permissions' => [
        'classname'   => \local_wenquest\external\get_permissions::class,
        'description' => 'What the current user may do in WenQuest (for example create courses).',
        'type'        => 'read',
        'services'    => [MOODLE_OFFICIAL_MOBILE_SERVICE],
    ],
    'local_wenquest_create_course' => [
        'classname'    => \local_wenquest\external\create_course::class,
        'description'  => 'Create a complete course (sections, pages, links, assignments) in one call.',
        'type'         => 'write',
        'capabilities' => 'moodle/course:create',
        'services'     => [MOODLE_OFFICIAL_MOBILE_SERVICE],
    ],
    'local_wenquest_add_activities' => [
        'classname'    => \local_wenquest\external\add_activities::class,
        'description'  => 'Add lessons and files to one section of an existing course (publish lesson by lesson).',
        'type'         => 'write',
        'capabilities' => 'moodle/course:manageactivities',
        'services'     => [MOODLE_OFFICIAL_MOBILE_SERVICE],
    ],
];
