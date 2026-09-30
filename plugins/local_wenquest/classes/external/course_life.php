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
 * A course's life after teaching (round 3): delete into the recycle bin, list the bin, restore, delete for good,
 * and make a backup file to download. Hiding / showing a course (下架 / 重新开课) is edit_course's visible field.
 *
 * Built on Moodle's own category recycle bin (tool_recyclebin): deleting keeps a full backup (content, people,
 * grades, submissions). WenQuest remembers who taught the course, so its teachers can find and restore it.
 *
 * Actions: delete (courseid), list, restore (binid), purge (binid), backup (courseid), binfile (binid).
 *
 * @package    local_wenquest
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
class course_life extends external_api {
    /** File area (in the user's own context) that holds the backup made for that user to download. */
    const AREA = 'backup';

    /**
     * Parameters.
     *
     * @return external_function_parameters
     */
    public static function execute_parameters(): external_function_parameters {
        return new external_function_parameters([
            'action' => new external_value(PARAM_ALPHA, 'delete, list, restore, purge, backup or binfile'),
            'courseid' => new external_value(PARAM_INT, 'Course (delete, backup)', VALUE_DEFAULT, 0),
            'binid' => new external_value(PARAM_INT, 'Recycle bin item (restore, purge, binfile)', VALUE_DEFAULT, 0),
        ]);
    }

    /**
     * Do one action.
     *
     * @param string $action
     * @param int $courseid
     * @param int $binid
     * @return array
     */
    public static function execute(string $action, int $courseid = 0, int $binid = 0): array {
        global $CFG, $DB, $USER;
        require_once($CFG->dirroot . '/course/lib.php');
        $p = self::validate_parameters(self::execute_parameters(), compact('action', 'courseid', 'binid'));
        self::validate_context(\context_system::instance());
        $out = ['ok' => true, 'courseid' => 0, 'oldcourseid' => 0, 'binid' => 0, 'fileurl' => '', 'filesize' => 0, 'items' => []];

        switch ($p['action']) {
            case 'delete':
                $course = get_course($p['courseid']);
                self::require_teacher($course->id);
                if ($course->id == SITEID) {
                    throw new \invalid_parameter_exception('the site cannot be deleted');
                }
                if ($course->visible) {
                    throw new \moodle_exception('coursevisible', 'local_wenquest');   // 先下架，再删除
                }
                self::enable_bin();
                $teachers = self::teacher_ids($course->id);
                $before = (int) $DB->get_field_sql('SELECT MAX(id) FROM {tool_recyclebin_category}');
                \core_php_time_limit::raise(0);
                raise_memory_limit(MEMORY_EXTRA);
                if (!delete_course($course, false)) {
                    throw new \moodle_exception('cannotdeletecourse');
                }
                fix_course_sortorder();
                $bin = $DB->get_records_select('tool_recyclebin_category', 'id > ? AND shortname = ? AND categoryid = ?',
                    [$before, $course->shortname, $course->category], 'id DESC', '*', 0, 1);
                $bin = reset($bin);
                if (!$bin) {
                    throw new \moodle_exception('nobin', 'local_wenquest');
                }
                $DB->insert_record('local_wenquest_trash', (object) [
                    'binid' => $bin->id, 'oldcourseid' => $course->id, 'categoryid' => $course->category,
                    'fullname' => $course->fullname, 'shortname' => $course->shortname,
                    'teachers' => ',' . implode(',', array_unique(array_merge($teachers, [(int) $USER->id]))) . ',',
                    'deletedby' => $USER->id, 'filesize' => self::bin_file($bin) ? self::bin_file($bin)->get_filesize() : 0,
                    'timecreated' => time(),
                ]);
                $out['binid'] = (int) $bin->id;
                $out['oldcourseid'] = (int) $course->id;
                break;

            case 'list':
                $admin = is_siteadmin();
                $rows = $DB->get_records('local_wenquest_trash', null, 'timecreated DESC');
                foreach ($rows as $r) {
                    if (!$admin && strpos($r->teachers, ',' . $USER->id . ',') === false) {
                        continue;
                    }
                    if (!$DB->record_exists('tool_recyclebin_category', ['id' => $r->binid])) {
                        $DB->delete_records('local_wenquest_trash', ['id' => $r->id]);   // emptied elsewhere
                        continue;
                    }
                    $by = $DB->get_record('user', ['id' => $r->deletedby], 'id, firstname, lastname, firstnamephonetic,
                        lastnamephonetic, middlename, alternatename');
                    $out['items'][] = [
                        'binid' => (int) $r->binid, 'oldcourseid' => (int) $r->oldcourseid, 'fullname' => $r->fullname,
                        'shortname' => $r->shortname, 'deletedby' => $by ? fullname($by) : '', 'filesize' => (int) $r->filesize,
                        'timecreated' => (int) $r->timecreated,
                    ];
                }
                break;

            case 'restore':
                [$row, $bin, $item] = self::bin_item($p['binid']);
                \core_php_time_limit::raise(0);
                raise_memory_limit(MEMORY_EXTRA);
                $before = (int) $DB->get_field_sql('SELECT MAX(id) FROM {course}');
                $bin->restore_item($item);
                $DB->delete_records('local_wenquest_trash', ['id' => $row->id]);   // the bin item is gone now
                // The restore makes a new course (its short name may get a suffix like _1 on the way).
                $new = $DB->get_records_select('course', 'id > ? AND category = ?', [$before, $item->categoryid], 'id DESC',
                    'id, shortname', 0, 1);
                $new = reset($new);
                if (!$new) {
                    throw new \moodle_exception('restorefailed', 'local_wenquest');
                }
                // A restored course comes back taken down (下架), with its own short name; its teachers check it first.
                $data = (object) ['id' => $new->id, 'visible' => 0];
                if ($new->shortname !== $item->shortname && !$DB->record_exists('course', ['shortname' => $item->shortname])) {
                    $data->shortname = $item->shortname;
                }
                update_course($data);
                $out['courseid'] = (int) $new->id;
                $out['oldcourseid'] = (int) $row->oldcourseid;
                break;

            case 'purge':
                [$row, $bin, $item] = self::bin_item($p['binid']);
                $bin->delete_item($item);
                $DB->delete_records('local_wenquest_trash', ['id' => $row->id]);
                $out['oldcourseid'] = (int) $row->oldcourseid;
                break;

            case 'backup':
                $course = get_course($p['courseid']);
                self::require_teacher($course->id);
                $file = self::make_backup($course);
                [$out['fileurl'], $out['filesize']] = self::give($file, $course->shortname);
                break;

            case 'binfile':
                [$row, , $item] = self::bin_item($p['binid']);
                $file = self::bin_file($item);
                if (!$file) {
                    throw new \moodle_exception('nobin', 'local_wenquest');
                }
                [$out['fileurl'], $out['filesize']] = self::give($file, $row->shortname);
                $out['oldcourseid'] = (int) $row->oldcourseid;
                break;

            default:
                throw new \invalid_parameter_exception('unknown action');
        }
        return $out;
    }

    /**
     * Only the course's teachers (who may edit it) and site admins.
     *
     * @param int $courseid
     */
    private static function require_teacher(int $courseid): void {
        if (!is_siteadmin()) {
            require_capability('moodle/course:update', \context_course::instance($courseid));
        }
    }

    /**
     * Users who can edit the course (its teachers), recorded when it is deleted.
     *
     * @param int $courseid
     * @return int[]
     */
    private static function teacher_ids(int $courseid): array {
        $users = get_enrolled_users(\context_course::instance($courseid), 'moodle/course:update', 0, 'u.id');
        return array_map('intval', array_keys($users));
    }

    /**
     * The recycle bin keeps deleted courses until someone deletes them for good.
     */
    private static function enable_bin(): void {
        if (!get_config('tool_recyclebin', 'categorybinenable')) {
            set_config('categorybinenable', 1, 'tool_recyclebin');
            set_config('categorybinexpiry', 0, 'tool_recyclebin');
        }
    }

    /**
     * Our record, the bin and the bin item — only for the course's teachers or site admins.
     *
     * @param int $binid
     * @return array
     */
    private static function bin_item(int $binid): array {
        global $DB, $USER;
        $row = $DB->get_record('local_wenquest_trash', ['binid' => $binid], '*', MUST_EXIST);
        if (!is_siteadmin() && strpos($row->teachers, ',' . $USER->id . ',') === false) {
            throw new \required_capability_exception(\context_system::instance(), 'tool/recyclebin:restoreitems', 'nopermissions', '');
        }
        $item = $DB->get_record('tool_recyclebin_category', ['id' => $binid], '*', MUST_EXIST);
        return [$row, new \tool_recyclebin\category_bin($item->categoryid), $item];
    }

    /**
     * The backup file the recycle bin keeps for an item.
     *
     * @param \stdClass $item
     * @return \stored_file|null
     */
    private static function bin_file(\stdClass $item): ?\stored_file {
        $context = \context_coursecat::instance($item->categoryid, IGNORE_MISSING);
        if (!$context) {
            return null;
        }
        $files = get_file_storage()->get_area_files($context->id, 'tool_recyclebin', 'recyclebin_coursecat', $item->id,
            'itemid, filepath, filename', false);
        return $files ? reset($files) : null;
    }

    /**
     * A full backup of the course (content, people, grades, submissions) as a .mbz file.
     *
     * @param \stdClass $course
     * @return \stored_file
     */
    private static function make_backup(\stdClass $course): \stored_file {
        global $CFG;
        require_once($CFG->dirroot . '/backup/util/includes/backup_includes.php');
        \core_php_time_limit::raise(0);
        raise_memory_limit(MEMORY_EXTRA);
        // Made on the site's behalf, like the recycle bin's own backup, so it includes the people and their work
        // (teachers normally may not back up user data); only the course's teachers get here (require_teacher).
        $bc = new \backup_controller(\backup::TYPE_1COURSE, $course->id, \backup::FORMAT_MOODLE, \backup::INTERACTIVE_NO,
            \backup::MODE_GENERAL, get_admin()->id);
        foreach (['users' => 1, 'role_assignments' => 1, 'activities' => 1, 'blocks' => 1, 'files' => 1, 'filters' => 1,
                  'comments' => 1, 'userscompletion' => 1, 'logs' => 0, 'grade_histories' => 0, 'anonymize' => 0] as $k => $v) {
            if ($bc->get_plan()->setting_exists($k)) {
                $setting = $bc->get_plan()->get_setting($k);
                if ($setting->get_status() == \base_setting::NOT_LOCKED) {
                    $setting->set_value($v);
                }
            }
        }
        $bc->execute_plan();
        $result = $bc->get_results();
        $bc->destroy();
        if (empty($result['backup_destination'])) {
            throw new \moodle_exception('backupfailed', 'local_wenquest');
        }
        return $result['backup_destination'];
    }

    /**
     * Put a copy of the file in the user's own WenQuest area (only the newest one is kept) and return its URL.
     *
     * @param \stored_file $file
     * @param string $shortname
     * @return array [url, size]
     */
    private static function give(\stored_file $file, string $shortname): array {
        global $USER;
        $fs = get_file_storage();
        $context = \context_user::instance($USER->id);
        $fs->delete_area_files($context->id, 'local_wenquest', self::AREA);
        $name = clean_filename(($shortname ?: 'course') . '-' . date('Ymd-His') . '.mbz');
        $copy = $fs->create_file_from_storedfile(['contextid' => $context->id, 'component' => 'local_wenquest',
            'filearea' => self::AREA, 'itemid' => 0, 'filepath' => '/', 'filename' => $name], $file);
        if ($file->get_component() === 'backup' && $file->get_filearea() === 'course') {
            $file->delete();   // the copy in the course's backup area is not needed
        }
        $url = \moodle_url::make_webservice_pluginfile_url($context->id, 'local_wenquest', self::AREA, 0, '/', $name);
        return [$url->out(false), (int) $copy->get_filesize()];
    }

    /**
     * Result.
     *
     * @return external_single_structure
     */
    public static function execute_returns(): external_single_structure {
        return new external_single_structure([
            'ok' => new external_value(PARAM_BOOL, 'Done'),
            'courseid' => new external_value(PARAM_INT, 'restore: the restored course'),
            'oldcourseid' => new external_value(PARAM_INT, 'The course id before it was deleted'),
            'binid' => new external_value(PARAM_INT, 'delete: the recycle bin item'),
            'fileurl' => new external_value(PARAM_RAW, 'backup, binfile: download address (web service file URL)'),
            'filesize' => new external_value(PARAM_INT, 'backup, binfile: bytes'),
            'items' => new external_multiple_structure(new external_single_structure([
                'binid' => new external_value(PARAM_INT, 'Recycle bin item'),
                'oldcourseid' => new external_value(PARAM_INT, 'Course id before deletion'),
                'fullname' => new external_value(PARAM_TEXT, 'Course name'),
                'shortname' => new external_value(PARAM_TEXT, 'Short name'),
                'deletedby' => new external_value(PARAM_TEXT, 'Who deleted it'),
                'filesize' => new external_value(PARAM_INT, 'Backup size in bytes'),
                'timecreated' => new external_value(PARAM_INT, 'When it was deleted'),
            ])),
        ]);
    }
}
