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
    'local_wenquest_manage_members' => [
        'classname'    => \local_wenquest\external\manage_members::class,
        'description'  => 'Add people to a course by user name or email, or take them out.',
        'type'         => 'write',
        'services'     => [MOODLE_OFFICIAL_MOBILE_SERVICE],
    ],
    'local_wenquest_manage_groups' => [
        'classname'    => \local_wenquest\external\manage_groups::class,
        'description'  => 'Create, rename and delete groups, set members, or apply a grouping plan.',
        'type'         => 'write',
        'capabilities' => 'moodle/course:managegroups',
        'services'     => [MOODLE_OFFICIAL_MOBILE_SERVICE],
    ],
    'local_wenquest_get_meetings' => [
        'classname'    => \local_wenquest\external\meetings::class,
        'methodname'   => 'get',
        'description'  => 'Online class sessions (Tencent Meeting / Zoom) of a course.',
        'type'         => 'read',
        'services'     => [MOODLE_OFFICIAL_MOBILE_SERVICE],
    ],
    'local_wenquest_save_meeting' => [
        'classname'    => \local_wenquest\external\meetings::class,
        'methodname'   => 'save',
        'description'  => 'Add or change an online class session (also in the course calendar).',
        'type'         => 'write',
        'capabilities' => 'moodle/course:update',
        'services'     => [MOODLE_OFFICIAL_MOBILE_SERVICE],
    ],
    'local_wenquest_delete_meeting' => [
        'classname'    => \local_wenquest\external\meetings::class,
        'methodname'   => 'delete',
        'description'  => 'Delete an online class session.',
        'type'         => 'write',
        'capabilities' => 'moodle/course:update',
        'services'     => [MOODLE_OFFICIAL_MOBILE_SERVICE],
    ],
    'local_wenquest_create_quiz' => [
        'classname'    => \local_wenquest\external\create_quiz::class,
        'description'  => 'Create a quiz with its questions, or update a quiz and replace its questions.',
        'type'         => 'write',
        'capabilities' => 'moodle/course:manageactivities',
        'services'     => [MOODLE_OFFICIAL_MOBILE_SERVICE],
    ],
    'local_wenquest_edit_course' => [
        'classname'    => \local_wenquest\external\edit_course::class,
        'description'  => 'Edit a course in WenQuest: settings, sections and activities.',
        'type'         => 'write',
        'services'     => [MOODLE_OFFICIAL_MOBILE_SERVICE],
    ],
    'local_wenquest_get_quiz' => [
        'classname'    => \local_wenquest\external\get_quiz::class,
        'description'  => 'A quiz with its questions, for editing in WenQuest.',
        'type'         => 'read',
        'capabilities' => 'mod/quiz:manage',
        'services'     => [MOODLE_OFFICIAL_MOBILE_SERVICE],
    ],
];
