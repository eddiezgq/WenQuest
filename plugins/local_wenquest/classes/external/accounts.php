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
 * Accounts for WenQuest's own sign-up, sign-in and administration.
 *
 * These functions are only in the separate local_wenquest_accounts service, which the gateway
 * calls with the wqservice account (see moodle/setup_wenquest.php). The gateway has already
 * verified the person's email with a code, and checks that administrators are administrators.
 *
 * @package    local_wenquest
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
class accounts extends external_api {
    /** The service account's user name. */
    const SERVICE_USER = 'wqservice';

    /**
     * Check the caller may manage accounts.
     */
    private static function guard(): void {
        $context = \context_system::instance();
        self::validate_context($context);
        require_capability('local/wenquest:manageaccounts', $context);
    }

    /**
     * The system role that makes a person a teacher (may create courses).
     *
     * @return int
     */
    private static function teacher_role(): int {
        $roles = get_archetype_roles('coursecreator');
        if (!$roles) {
            throw new \moodle_exception('invalidrole');
        }
        return (int) reset($roles)->id;
    }

    /**
     * One user as the gateway sees them.
     *
     * @param \stdClass $u
     * @return array
     */
    private static function describe(\stdClass $u): array {
        $sys = \context_system::instance();
        return [
            'id' => (int) $u->id,
            'username' => $u->username,
            'firstname' => $u->firstname,
            'lastname' => $u->lastname,
            'fullname' => fullname($u),
            'email' => $u->email,
            'lang' => (string) $u->lang,
            'suspended' => (bool) $u->suspended,
            'teacher' => user_has_role_assignment($u->id, self::teacher_role(), $sys->id),
            'admin' => is_siteadmin($u->id),
            'timecreated' => (int) $u->timecreated,
            'lastaccess' => (int) $u->lastaccess,
        ];
    }

    /**
     * Structure of one user.
     *
     * @return external_single_structure
     */
    private static function user_structure(): external_single_structure {
        return new external_single_structure([
            'id' => new external_value(PARAM_INT, 'User id'),
            'username' => new external_value(PARAM_RAW, 'User name'),
            'firstname' => new external_value(PARAM_RAW, 'First name'),
            'lastname' => new external_value(PARAM_RAW, 'Last name'),
            'fullname' => new external_value(PARAM_RAW, 'Full name'),
            'email' => new external_value(PARAM_RAW, 'Email'),
            'lang' => new external_value(PARAM_RAW, 'Language'),
            'suspended' => new external_value(PARAM_BOOL, 'Suspended'),
            'teacher' => new external_value(PARAM_BOOL, 'May create courses'),
            'admin' => new external_value(PARAM_BOOL, 'Site administrator'),
            'timecreated' => new external_value(PARAM_INT, 'Created'),
            'lastaccess' => new external_value(PARAM_INT, 'Last access'),
        ]);
    }

    // --- find ---------------------------------------------------------------

    /**
     * Parameters.
     *
     * @return external_function_parameters
     */
    public static function find_parameters(): external_function_parameters {
        return new external_function_parameters([
            'email' => new external_value(PARAM_RAW_TRIMMED, 'Email or user name', VALUE_DEFAULT, ''),
            'userid' => new external_value(PARAM_INT, 'User id', VALUE_DEFAULT, 0),
        ]);
    }

    /**
     * Find one person by email, user name or id.
     *
     * @param string $email
     * @param int $userid
     * @return array
     */
    public static function find(string $email, int $userid): array {
        global $DB;
        $p = self::validate_parameters(self::find_parameters(), ['email' => $email, 'userid' => $userid]);
        self::guard();
        if ($p['userid']) {
            $users = $DB->get_records('user', ['id' => $p['userid'], 'deleted' => 0]);
        } else {
            $key = \core_text::strtolower($p['email']);
            $users = $DB->get_records_select('user',
                '(' . $DB->sql_equal('email', ':e', false) . ' OR username = :u) AND deleted = 0',
                ['e' => $key, 'u' => $key], 'id ASC', '*', 0, 2);
        }
        if (count($users) !== 1) {
            return ['found' => false, 'many' => count($users) > 1, 'users' => []];
        }
        return ['found' => true, 'many' => false, 'users' => [self::describe(reset($users))]];
    }

    /**
     * Result.
     *
     * @return external_single_structure
     */
    public static function find_returns(): external_single_structure {
        return new external_single_structure([
            'found' => new external_value(PARAM_BOOL, 'Exactly one match'),
            'many' => new external_value(PARAM_BOOL, 'More than one account uses this email'),
            'users' => new external_multiple_structure(self::user_structure()),
        ]);
    }

    // --- create -------------------------------------------------------------

    /**
     * Parameters.
     *
     * @return external_function_parameters
     */
    public static function create_parameters(): external_function_parameters {
        return new external_function_parameters([
            'email' => new external_value(PARAM_RAW_TRIMMED, 'Verified email; also the user name'),
            'password' => new external_value(PARAM_RAW, 'Password'),
            'firstname' => new external_value(PARAM_TEXT, 'First (given) name'),
            'lastname' => new external_value(PARAM_TEXT, 'Last (family) name'),
            'lang' => new external_value(PARAM_ALPHANUMEXT, 'Language, e.g. zh_cn or en', VALUE_DEFAULT, 'zh_cn'),
            'teacher' => new external_value(PARAM_BOOL, 'Make a teacher now', VALUE_DEFAULT, false),
        ]);
    }

    /**
     * Create an account whose email the gateway has verified.
     *
     * @param string $email
     * @param string $password
     * @param string $firstname
     * @param string $lastname
     * @param string $lang
     * @param bool $teacher
     * @return array
     */
    public static function create(string $email, string $password, string $firstname, string $lastname,
            string $lang, bool $teacher): array {
        global $CFG, $DB;
        require_once($CFG->dirroot . '/user/lib.php');
        $p = self::validate_parameters(self::create_parameters(), [
            'email' => $email, 'password' => $password, 'firstname' => $firstname, 'lastname' => $lastname,
            'lang' => $lang, 'teacher' => $teacher,
        ]);
        self::guard();
        $email = \core_text::strtolower($p['email']);
        if (!validate_email($email)) {
            throw new \invalid_parameter_exception('invalid email');
        }
        if (trim($p['firstname']) === '' || trim($p['lastname']) === '') {
            throw new \invalid_parameter_exception('name required');
        }
        $taken = $DB->record_exists_select('user',
            '(' . $DB->sql_equal('email', ':e', false) . ' OR username = :u) AND deleted = 0', ['e' => $email, 'u' => $email]);
        if ($taken) {
            throw new \moodle_exception('emailexists', 'local_wenquest');
        }
        $langs = get_string_manager()->get_list_of_translations();
        $user = (object) [
            'auth' => 'manual',
            'confirmed' => 1,
            'mnethostid' => $CFG->mnet_localhost_id,
            'username' => $email,
            'email' => $email,
            'firstname' => trim($p['firstname']),
            'lastname' => trim($p['lastname']),
            'lang' => isset($langs[$p['lang']]) ? $p['lang'] : $CFG->lang,
            'password' => $p['password'],
        ];
        $user->id = user_create_user($user, true, true);
        if ($p['teacher']) {
            role_assign(self::teacher_role(), $user->id, \context_system::instance()->id);
        }
        return self::describe($DB->get_record('user', ['id' => $user->id], '*', MUST_EXIST));
    }

    /**
     * Result.
     *
     * @return external_single_structure
     */
    public static function create_returns(): external_single_structure {
        return self::user_structure();
    }

    // --- update -------------------------------------------------------------

    /**
     * Parameters.
     *
     * @return external_function_parameters
     */
    public static function update_parameters(): external_function_parameters {
        return new external_function_parameters([
            'userid' => new external_value(PARAM_INT, 'User id'),
            'password' => new external_value(PARAM_RAW, 'New password (empty = keep)', VALUE_DEFAULT, ''),
            'suspended' => new external_value(PARAM_INT, '1 suspend, 0 restore, -1 keep', VALUE_DEFAULT, -1),
            'teacher' => new external_value(PARAM_INT, '1 make teacher, 0 remove, -1 keep', VALUE_DEFAULT, -1),
        ]);
    }

    /**
     * Change a password, suspend or restore, or make a teacher.
     *
     * @param int $userid
     * @param string $password
     * @param int $suspended
     * @param int $teacher
     * @return array
     */
    public static function update(int $userid, string $password, int $suspended, int $teacher): array {
        global $CFG, $DB;
        require_once($CFG->dirroot . '/user/lib.php');
        $p = self::validate_parameters(self::update_parameters(), [
            'userid' => $userid, 'password' => $password, 'suspended' => $suspended, 'teacher' => $teacher,
        ]);
        self::guard();
        $user = $DB->get_record('user', ['id' => $p['userid'], 'deleted' => 0], '*', MUST_EXIST);
        if (isguestuser($user) || $user->username === self::SERVICE_USER) {
            throw new \invalid_parameter_exception('this account cannot be changed');
        }
        if ($p['password'] !== '') {
            if ($user->auth !== 'manual') {
                throw new \invalid_parameter_exception('password is managed elsewhere');
            }
            update_internal_user_password($user, $p['password']);
            \core\session\manager::destroy_user_sessions($user->id);
        }
        if ($p['suspended'] !== -1) {
            if (is_siteadmin($user->id)) {
                throw new \invalid_parameter_exception('administrators cannot be suspended');
            }
            user_update_user((object) ['id' => $user->id, 'suspended' => $p['suspended'] ? 1 : 0], false, true);
            if ($p['suspended']) {
                \core\session\manager::destroy_user_sessions($user->id);
                $DB->delete_records('external_tokens', ['userid' => $user->id]);
            }
        }
        if ($p['teacher'] !== -1) {
            $ctx = \context_system::instance()->id;
            if ($p['teacher']) {
                role_assign(self::teacher_role(), $user->id, $ctx);
            } else {
                role_unassign(self::teacher_role(), $user->id, $ctx);
            }
        }
        return self::describe($DB->get_record('user', ['id' => $user->id], '*', MUST_EXIST));
    }

    /**
     * Result.
     *
     * @return external_single_structure
     */
    public static function update_returns(): external_single_structure {
        return self::user_structure();
    }

    // --- search -------------------------------------------------------------

    /**
     * Parameters.
     *
     * @return external_function_parameters
     */
    public static function search_parameters(): external_function_parameters {
        return new external_function_parameters([
            'query' => new external_value(PARAM_RAW_TRIMMED, 'Name or email contains', VALUE_DEFAULT, ''),
            'page' => new external_value(PARAM_INT, 'Page (from 0)', VALUE_DEFAULT, 0),
            'perpage' => new external_value(PARAM_INT, 'Per page', VALUE_DEFAULT, 50),
        ]);
    }

    /**
     * Everyone, newest first, for the administration page.
     *
     * @param string $query
     * @param int $page
     * @param int $perpage
     * @return array
     */
    public static function search(string $query, int $page, int $perpage): array {
        global $CFG, $DB;
        $p = self::validate_parameters(self::search_parameters(), ['query' => $query, 'page' => $page, 'perpage' => $perpage]);
        self::guard();
        $where = 'deleted = 0 AND id <> :guest AND username <> :svc';
        $params = ['guest' => $CFG->siteguest, 'svc' => self::SERVICE_USER];
        if ($p['query'] !== '') {
            $like = [];
            foreach (['firstname', 'lastname', 'email', 'username'] as $i => $f) {
                $like[] = $DB->sql_like($f, ":q$i", false);
                $params["q$i"] = '%' . $DB->sql_like_escape($p['query']) . '%';
            }
            $where .= ' AND (' . implode(' OR ', $like) . ')';
        }
        $per = max(1, min(200, $p['perpage']));
        $total = $DB->count_records_select('user', $where, $params);
        $users = $DB->get_records_select('user', $where, $params, 'timecreated DESC, id DESC', '*', max(0, $p['page']) * $per, $per);
        return ['total' => $total, 'users' => array_values(array_map([self::class, 'describe'], $users))];
    }

    /**
     * Result.
     *
     * @return external_single_structure
     */
    public static function search_returns(): external_single_structure {
        return new external_single_structure([
            'total' => new external_value(PARAM_INT, 'Matches'),
            'users' => new external_multiple_structure(self::user_structure()),
        ]);
    }

    // --- enrol --------------------------------------------------------------

    /**
     * Parameters.
     *
     * @return external_function_parameters
     */
    public static function enrol_parameters(): external_function_parameters {
        return new external_function_parameters([
            'userid' => new external_value(PARAM_INT, 'User id'),
            'courseid' => new external_value(PARAM_INT, 'Course id'),
        ]);
    }

    /**
     * Put a person in a course as a student (a free course they joined, or a paid one an administrator opened).
     *
     * @param int $userid
     * @param int $courseid
     * @return array
     */
    public static function enrol(int $userid, int $courseid): array {
        global $DB;
        $p = self::validate_parameters(self::enrol_parameters(), ['userid' => $userid, 'courseid' => $courseid]);
        self::guard();
        $course = get_course($p['courseid']);
        $user = $DB->get_record('user', ['id' => $p['userid'], 'deleted' => 0, 'suspended' => 0], 'id', MUST_EXIST);
        $context = \context_course::instance($course->id);
        if (is_enrolled($context, $user->id, '', true)) {
            return ['status' => 'already'];
        }
        $plugin = enrol_get_plugin('manual');
        $instance = null;
        foreach (enrol_get_instances($course->id, false) as $i) {
            if ($i->enrol === 'manual') {
                $instance = $i;
                break;
            }
        }
        if (!$instance) {
            $id = $plugin->add_default_instance($course);
            $instance = $DB->get_record('enrol', ['id' => $id], '*', MUST_EXIST);
        }
        if ((int) $instance->status !== ENROL_INSTANCE_ENABLED) {
            $plugin->update_status($instance, ENROL_INSTANCE_ENABLED);
        }
        $roles = get_archetype_roles('student');
        $plugin->enrol_user($instance, $user->id, $roles ? (int) reset($roles)->id : (int) $instance->roleid,
            0, 0, ENROL_USER_ACTIVE);
        return ['status' => 'added'];
    }

    /**
     * Result.
     *
     * @return external_single_structure
     */
    public static function enrol_returns(): external_single_structure {
        return new external_single_structure(['status' => new external_value(PARAM_ALPHA, 'added or already')]);
    }

    // --- course cards ---------------------------------------------------------

    /**
     * Parameters.
     *
     * @return external_function_parameters
     */
    public static function courses_parameters(): external_function_parameters {
        return new external_function_parameters([
            'courseids' => new external_multiple_structure(new external_value(PARAM_INT, 'Course id'), 'Courses', VALUE_DEFAULT, []),
            'userid' => new external_value(PARAM_INT, 'Also say whether this person is in each course', VALUE_DEFAULT, 0),
        ]);
    }

    /**
     * Public facts about courses, for the course catalogue (also shown to visitors who have not signed in).
     *
     * @param array $courseids
     * @param int $userid
     * @return array
     */
    public static function courses(array $courseids, int $userid): array {
        global $DB;
        $p = self::validate_parameters(self::courses_parameters(), ['courseids' => $courseids, 'userid' => $userid]);
        self::guard();
        $out = [];
        foreach (array_unique($p['courseids']) as $id) {
            $course = $DB->get_record('course', ['id' => $id]);
            if (!$course || $course->id == SITEID) {
                continue;
            }
            $context = \context_course::instance($course->id);
            $teachers = [];
            $roleids = array_keys(get_archetype_roles('editingteacher'));
            foreach (!$roleids ? [] : get_role_users($roleids, $context, false, 'u.id, u.firstname, u.lastname, u.firstnamephonetic, u.lastnamephonetic, u.middlename, u.alternatename',
                    'u.lastname ASC') as $t) {
                $teachers[] = fullname($t);
            }
            $sections = $DB->count_records_select('course_sections', 'course = :c AND section > 0', ['c' => $course->id]);
            $out[] = [
                'id' => (int) $course->id,
                'fullname' => $course->fullname,
                'shortname' => $course->shortname,
                'summary' => (string) $course->summary,
                'visible' => (bool) $course->visible,
                'startdate' => (int) $course->startdate,
                'sections' => $sections,
                'students' => count_enrolled_users($context, 'mod/assign:submit'),
                'teachers' => $teachers,
                'enrolled' => $p['userid'] ? is_enrolled($context, $p['userid'], '', true) : false,
            ];
        }
        return ['courses' => $out];
    }

    /**
     * Result.
     *
     * @return external_single_structure
     */
    public static function courses_returns(): external_single_structure {
        return new external_single_structure([
            'courses' => new external_multiple_structure(new external_single_structure([
                'id' => new external_value(PARAM_INT, 'Course id'),
                'fullname' => new external_value(PARAM_RAW, 'Name'),
                'shortname' => new external_value(PARAM_RAW, 'Short name'),
                'summary' => new external_value(PARAM_RAW, 'Summary HTML'),
                'visible' => new external_value(PARAM_BOOL, 'Visible to students'),
                'startdate' => new external_value(PARAM_INT, 'Start date'),
                'sections' => new external_value(PARAM_INT, 'Chapters'),
                'students' => new external_value(PARAM_INT, 'Students'),
                'teachers' => new external_multiple_structure(new external_value(PARAM_RAW, 'Teacher')),
                'enrolled' => new external_value(PARAM_BOOL, 'The given person is in the course'),
            ])),
        ]);
    }
}
