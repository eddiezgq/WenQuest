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
 * Course groups: create, rename, delete, set members, or apply a whole grouping plan (AI grouping).
 *
 * @package    local_wenquest
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
class manage_groups extends external_api {
    /**
     * Parameters.
     *
     * @return external_function_parameters
     */
    public static function execute_parameters(): external_function_parameters {
        $ids = new external_multiple_structure(new external_value(PARAM_INT, 'User id'), 'Members', VALUE_DEFAULT, []);
        return new external_function_parameters([
            'courseid' => new external_value(PARAM_INT, 'Course id'),
            'action' => new external_value(PARAM_ALPHA, 'create, rename, delete, setmembers or applyplan'),
            'groupid' => new external_value(PARAM_INT, 'Group (rename, delete, setmembers)', VALUE_DEFAULT, 0),
            'name' => new external_value(PARAM_TEXT, 'Group name (create, rename)', VALUE_DEFAULT, ''),
            'userids' => $ids,
            'plan' => new external_multiple_structure(new external_single_structure([
                'name' => new external_value(PARAM_TEXT, 'Group name'),
                'userids' => new external_multiple_structure(new external_value(PARAM_INT, 'User id'), 'Members'),
            ]), 'Groups to create (applyplan)', VALUE_DEFAULT, []),
            'replace' => new external_value(PARAM_BOOL, 'applyplan: delete the existing groups first', VALUE_DEFAULT, false),
        ]);
    }

    /**
     * Do it.
     *
     * @param int $courseid
     * @param string $action
     * @param int $groupid
     * @param string $name
     * @param array $userids
     * @param array $plan
     * @param bool $replace
     * @return array
     */
    public static function execute(int $courseid, string $action, int $groupid, string $name, array $userids,
            array $plan, bool $replace): array {
        global $CFG, $DB;
        require_once($CFG->dirroot . '/group/lib.php');
        $p = self::validate_parameters(self::execute_parameters(), [
            'courseid' => $courseid, 'action' => $action, 'groupid' => $groupid, 'name' => $name,
            'userids' => $userids, 'plan' => $plan, 'replace' => $replace,
        ]);
        $course = get_course($p['courseid']);
        $context = \context_course::instance($course->id);
        self::validate_context($context);
        require_capability('moodle/course:managegroups', $context);

        $group = null;
        if (in_array($p['action'], ['rename', 'delete', 'setmembers'], true)) {
            $group = $DB->get_record('groups', ['id' => $p['groupid'], 'courseid' => $course->id], '*', MUST_EXIST);
        }
        $skipped = [];
        $transaction = $DB->start_delegated_transaction();
        switch ($p['action']) {
            case 'create':
                $group = (object) ['courseid' => $course->id, 'name' => self::name($p['name'])];
                $group->id = groups_create_group($group);
                self::set_members($context, $group->id, $p['userids'], $skipped);
                break;
            case 'rename':
                $group->name = self::name($p['name']);
                groups_update_group($group);
                break;
            case 'delete':
                groups_delete_group($group);
                break;
            case 'setmembers':
                self::set_members($context, $group->id, $p['userids'], $skipped);
                break;
            case 'applyplan':
                if (count($p['plan']) > 200) {
                    throw new \invalid_parameter_exception('too many groups');
                }
                if ($p['replace']) {
                    groups_delete_groups($course->id, false);
                }
                foreach ($p['plan'] as $g) {
                    $id = groups_create_group((object) ['courseid' => $course->id, 'name' => self::name($g['name'])]);
                    self::set_members($context, $id, $g['userids'], $skipped);
                }
                break;
            default:
                throw new \invalid_parameter_exception('unknown action');
        }
        $transaction->allow_commit();

        $out = [];
        foreach (groups_get_all_groups($course->id) as $g) {
            $members = array_map('intval', array_keys(groups_get_members($g->id, 'u.id', 'u.id')));
            $out[] = ['id' => (int) $g->id, 'name' => format_string($g->name, true, ['context' => $context]), 'members' => $members];
        }
        return ['groups' => $out, 'skipped' => array_values(array_unique($skipped))];
    }

    /**
     * A usable group name.
     *
     * @param string $name
     * @return string
     */
    private static function name(string $name): string {
        $name = trim($name);
        if ($name === '') {
            throw new \invalid_parameter_exception('group name is empty');
        }
        return \core_text::substr($name, 0, 254);
    }

    /**
     * Make the group's members exactly these people (only people enrolled in the course).
     *
     * @param \context_course $context
     * @param int $groupid
     * @param array $userids
     * @param array $skipped collects people who are not in the course
     */
    private static function set_members(\context_course $context, int $groupid, array $userids, array &$skipped): void {
        $want = array_unique(array_map('intval', $userids));
        $have = array_map('intval', array_keys(groups_get_members($groupid, 'u.id', 'u.id')));
        foreach (array_diff($have, $want) as $uid) {
            groups_remove_member($groupid, $uid);
        }
        foreach (array_diff($want, $have) as $uid) {
            if (!is_enrolled($context, $uid) || !groups_add_member($groupid, $uid)) {
                $skipped[] = $uid;
            }
        }
    }

    /**
     * Result structure.
     *
     * @return external_single_structure
     */
    public static function execute_returns(): external_single_structure {
        return new external_single_structure([
            'groups' => new external_multiple_structure(new external_single_structure([
                'id' => new external_value(PARAM_INT, 'Group id'),
                'name' => new external_value(PARAM_TEXT, 'Name'),
                'members' => new external_multiple_structure(new external_value(PARAM_INT, 'User id')),
            ])),
            'skipped' => new external_multiple_structure(new external_value(PARAM_INT, 'User id not in the course')),
        ]);
    }
}
