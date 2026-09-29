<?php
// This file is part of WenQuest - https://wenquestrobotics.com
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

namespace local_wenquest\external;

use core_external\external_api;
use core_external\external_function_parameters;
use core_external\external_multiple_structure;
use core_external\external_single_structure;
use core_external\external_value;

/**
 * Add people to a course by user name or email (manual enrolment), or take them out.
 *
 * @package    local_wenquest
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
class manage_members extends external_api {
    /**
     * Parameters.
     *
     * @return external_function_parameters
     */
    public static function execute_parameters(): external_function_parameters {
        return new external_function_parameters([
            'courseid' => new external_value(PARAM_INT, 'Course id'),
            'action' => new external_value(PARAM_ALPHA, 'enrol or unenrol'),
            'identifiers' => new external_multiple_structure(
                new external_value(PARAM_RAW_TRIMMED, 'User name or email'), 'People to add', VALUE_DEFAULT, []),
            'role' => new external_value(PARAM_ALPHA, 'student, teacher (non-editing) or editingteacher', VALUE_DEFAULT, 'student'),
            'userid' => new external_value(PARAM_INT, 'Person to take out (unenrol)', VALUE_DEFAULT, 0),
        ]);
    }

    /**
     * Enrol or unenrol.
     *
     * @param int $courseid
     * @param string $action
     * @param array $identifiers
     * @param string $role
     * @param int $userid
     * @return array
     */
    public static function execute(int $courseid, string $action, array $identifiers, string $role, int $userid): array {
        global $DB, $USER;
        $params = self::validate_parameters(self::execute_parameters(), [
            'courseid' => $courseid, 'action' => $action, 'identifiers' => $identifiers, 'role' => $role, 'userid' => $userid,
        ]);
        $course = get_course($params['courseid']);
        $context = \context_course::instance($course->id);
        self::validate_context($context);

        $plugin = enrol_get_plugin('manual');
        if (!$plugin) {
            throw new \moodle_exception('manualpluginnotinstalled', 'enrol_manual');
        }
        $instance = null;
        foreach (enrol_get_instances($course->id, false) as $i) {
            if ($i->enrol === 'manual') {
                $instance = $i;
                break;
            }
        }

        if ($params['action'] === 'unenrol') {
            require_capability('enrol/manual:unenrol', $context);
            if ((int) $params['userid'] === (int) $USER->id) {
                throw new \invalid_parameter_exception('you cannot remove yourself');
            }
            $removed = 0;
            foreach (enrol_get_instances($course->id, false) as $i) {
                if ($i->enrol === 'manual' && $DB->record_exists('user_enrolments', ['enrolid' => $i->id, 'userid' => $params['userid']])) {
                    $plugin->unenrol_user($i, $params['userid']);
                    $removed++;
                }
            }
            return ['added' => [], 'already' => [], 'notfound' => [], 'removed' => $removed];
        }

        if ($params['action'] !== 'enrol') {
            throw new \invalid_parameter_exception('unknown action');
        }
        require_capability('enrol/manual:enrol', $context);
        if (count($params['identifiers']) > 500) {
            throw new \invalid_parameter_exception('at most 500 people at a time');
        }
        if (!$instance) {
            $id = $plugin->add_default_instance($course);
            $instance = $DB->get_record('enrol', ['id' => $id], '*', MUST_EXIST);
        }
        $archetype = in_array($params['role'], ['student', 'teacher', 'editingteacher'], true) ? $params['role'] : 'student';
        if ($archetype !== 'student') {
            require_capability('moodle/role:assign', $context);
        }
        $roles = get_archetype_roles($archetype);
        $roleid = $roles ? (int) reset($roles)->id : (int) $instance->roleid;

        $added = [];
        $already = [];
        $notfound = [];
        foreach ($params['identifiers'] as $raw) {
            $key = \core_text::strtolower(trim($raw));
            if ($key === '') {
                continue;
            }
            $field = strpos($key, '@') !== false ? 'email' : 'username';
            $select = $field === 'email' ? $DB->sql_equal('email', ':v', false) : 'username = :v';
            $users = $DB->get_records_select('user', "$select AND deleted = 0 AND suspended = 0",
                ['v' => $key], 'id ASC', 'id, username', 0, 2);
            if (count($users) !== 1) {
                $notfound[] = $raw;
                continue;
            }
            $user = reset($users);
            if (is_enrolled($context, $user->id, '', true)) {
                $already[] = $raw;
                continue;
            }
            $plugin->enrol_user($instance, $user->id, $roleid);
            $added[] = $raw;
        }
        return ['added' => $added, 'already' => $already, 'notfound' => $notfound, 'removed' => 0];
    }

    /**
     * Result structure.
     *
     * @return external_single_structure
     */
    public static function execute_returns(): external_single_structure {
        $list = fn($d) => new external_multiple_structure(new external_value(PARAM_RAW, $d));
        return new external_single_structure([
            'added' => $list('Added'),
            'already' => $list('Already in the course'),
            'notfound' => $list('No such user'),
            'removed' => new external_value(PARAM_INT, 'Enrolments removed'),
        ]);
    }
}
