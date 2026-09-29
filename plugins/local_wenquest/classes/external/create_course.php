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
 * Create a complete course in one call: the WenQuest AI course builder publishes through this.
 *
 * The caller needs moodle/course:create in the default category and becomes the course's teacher.
 * Everything runs in one transaction, so a failure leaves no half-built course behind.
 *
 * @package    local_wenquest
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
class create_course extends external_api {
    /**
     * Parameters.
     *
     * @return external_function_parameters
     */
    public static function execute_parameters(): external_function_parameters {
        $activity = new external_single_structure([
            'type' => new external_value(PARAM_ALPHA, 'page, url, assign or resource'),
            'name' => new external_value(PARAM_TEXT, 'Activity name (multilang allowed)'),
            'intro' => new external_value(PARAM_RAW, 'Short description (HTML)', VALUE_DEFAULT, ''),
            'content' => new external_value(PARAM_RAW, 'Page content (HTML)', VALUE_DEFAULT, ''),
            'url' => new external_value(PARAM_URL, 'Link target for url activities', VALUE_DEFAULT, ''),
            'draftitemid' => new external_value(PARAM_INT, 'Draft area with the uploaded file (resource)', VALUE_DEFAULT, 0),
            'visible' => new external_value(PARAM_INT, '1 = students see it, 0 = teachers only', VALUE_DEFAULT, 1),
        ]);
        $section = new external_single_structure([
            'name' => new external_value(PARAM_TEXT, 'Section name (multilang allowed)'),
            'summary' => new external_value(PARAM_RAW, 'Section summary (HTML)', VALUE_DEFAULT, ''),
            'activities' => new external_multiple_structure($activity, 'Activities', VALUE_DEFAULT, []),
        ]);
        return new external_function_parameters([
            'fullname' => new external_value(PARAM_TEXT, 'Course full name (multilang allowed)'),
            'shortname' => new external_value(PARAM_TEXT, 'Preferred short name; made unique if taken'),
            'summary' => new external_value(PARAM_RAW, 'Course summary (HTML)', VALUE_DEFAULT, ''),
            'sections' => new external_multiple_structure($section, 'Sections'),
        ]);
    }

    /**
     * Create the course.
     *
     * @param string $fullname
     * @param string $shortname
     * @param string $summary
     * @param array $sections
     * @return array
     */
    public static function execute(string $fullname, string $shortname, string $summary, array $sections): array {
        global $CFG, $DB, $USER;
        require_once($CFG->dirroot . '/course/lib.php');
        require_once($CFG->dirroot . '/course/modlib.php');
        require_once($CFG->libdir . '/resourcelib.php');
        require_once($CFG->libdir . '/enrollib.php');

        $params = self::validate_parameters(self::execute_parameters(), [
            'fullname' => $fullname, 'shortname' => $shortname, 'summary' => $summary, 'sections' => $sections,
        ]);
        $category = \core_course_category::get_default();
        $catcontext = \context_coursecat::instance($category->id);
        self::validate_context($catcontext);
        require_capability('moodle/course:create', $catcontext);
        if (!$params['sections']) {
            throw new \moodle_exception('emptycourse', 'local_wenquest');
        }

        $transaction = $DB->start_delegated_transaction();

        $course = create_course((object) [
            'category' => $category->id,
            'fullname' => $params['fullname'],
            'shortname' => self::unique_shortname($params['shortname']),
            'summary' => clean_text($params['summary'], FORMAT_HTML),
            'summaryformat' => FORMAT_HTML,
            'format' => 'topics',
            'numsections' => count($params['sections']),
            'enablecompletion' => 1,
            'visible' => 1,
        ]);

        // The creator teaches the course, so it appears in their WenQuest course list.
        $teacherrole = $DB->get_field('role', 'id', ['shortname' => 'editingteacher']);
        if ($teacherrole) {
            enrol_try_internal_enrol($course->id, $USER->id, $teacherrole);
        }

        $activitycount = 0;
        foreach (array_values($params['sections']) as $index => $sectiondata) {
            $number = $index + 1;
            $section = $DB->get_record('course_sections', ['course' => $course->id, 'section' => $number], '*', MUST_EXIST);
            course_update_section($course, $section, [
                'name' => $sectiondata['name'],
                'summary' => clean_text($sectiondata['summary'], FORMAT_HTML),
                'summaryformat' => FORMAT_HTML,
            ]);
            foreach ($sectiondata['activities'] as $activity) {
                if (self::add_activity($course, $number, $activity)) {
                    $activitycount++;
                }
            }
        }

        $transaction->allow_commit();
        rebuild_course_cache($course->id, true);

        return [
            'courseid' => (int) $course->id,
            'shortname' => $course->shortname,
            'activities' => $activitycount,
        ];
    }

    /**
     * Add one activity to a section.
     *
     * @param \stdClass $course
     * @param int $section Section number
     * @param array $activity
     * @return int The new course module id, or 0 when the activity was skipped
     */
    public static function add_activity(\stdClass $course, int $section, array $activity): int {
        $base = [
            'course' => $course->id,
            'section' => $section,
            'visible' => $activity['visible'] ? 1 : 0,
            'visibleoncoursepage' => 1,
            'name' => $activity['name'],
            'cmidnumber' => '',
            'groupmode' => 0,
            'groupingid' => 0,
            'availability' => null,
            'introeditor' => [
                'text' => clean_text($activity['intro'], FORMAT_HTML),
                'format' => FORMAT_HTML,
                'itemid' => 0,
            ],
            'showdescription' => 0,
        ];
        switch ($activity['type']) {
            case 'page':
                $info = $base + [
                    'modulename' => 'page',
                    'content' => clean_text($activity['content'], FORMAT_HTML),
                    'contentformat' => FORMAT_HTML,
                    'display' => RESOURCELIB_DISPLAY_AUTO,
                    'printintro' => 0,
                    'printlastmodified' => 1,
                    // Reading a page marks it done, so course progress works out of the box.
                    'completion' => COMPLETION_TRACKING_AUTOMATIC,
                    'completionview' => 1,
                ];
                break;
            case 'url':
                if (!$activity['url']) {
                    return 0;
                }
                $info = $base + [
                    'modulename' => 'url',
                    'externalurl' => $activity['url'],
                    'display' => RESOURCELIB_DISPLAY_AUTO,
                    'completion' => COMPLETION_TRACKING_AUTOMATIC,
                    'completionview' => 1,
                ];
                break;
            case 'assign':
                $info = $base + [
                    'modulename' => 'assign',
                    'alwaysshowdescription' => 1,
                    'submissiondrafts' => 0,
                    'requiresubmissionstatement' => 0,
                    'sendnotifications' => 0,
                    'sendlatenotifications' => 0,
                    'sendstudentnotifications' => 1,
                    'duedate' => (int) ($activity['duedate'] ?? 0),
                    'cutoffdate' => 0,
                    'gradingduedate' => 0,
                    'allowsubmissionsfromdate' => 0,
                    'grade' => (float) ($activity['grade'] ?? 100) ?: 100,
                    'teamsubmission' => 0,
                    'requireallteammemberssubmit' => 0,
                    'teamsubmissiongroupingid' => 0,
                    'blindmarking' => 0,
                    'attemptreopenmethod' => 'untilpass',
                    'maxattempts' => -1,
                    'markingworkflow' => 0,
                    'markingallocation' => 0,
                    'markinganonymous' => 0,
                    'activityformat' => 0,
                    'timelimit' => 0,
                    'submissionattachments' => 0,
                    'assignsubmission_onlinetext_enabled' => 1,
                    'assignsubmission_file_enabled' => 1,
                    'assignsubmission_file_maxfiles' => 5,
                    'assignsubmission_file_maxsizebytes' => 0,
                    'assignfeedback_comments_enabled' => 1,
                    'completion' => COMPLETION_TRACKING_AUTOMATIC,
                    'completionsubmit' => 1,
                ];
                break;
            case 'resource':
                if (!$activity['draftitemid']) {
                    return 0;
                }
                $info = $base + [
                    'modulename' => 'resource',
                    'files' => $activity['draftitemid'],
                    'display' => RESOURCELIB_DISPLAY_AUTO,
                    'printintro' => 0,
                    'showsize' => 1,
                    'showtype' => 1,
                    'completion' => COMPLETION_TRACKING_NONE,
                ];
                break;
            case 'forum':
                $info = $base + [
                    'modulename' => 'forum',
                    'type' => 'general',
                    'forcesubscribe' => 0,
                    'trackingtype' => 1,
                    'maxbytes' => 0,
                    'maxattachments' => 9,
                    'displaywordcount' => 0,
                    'completion' => COMPLETION_TRACKING_NONE,
                ];
                break;
            default:
                return 0; // Unknown types are skipped rather than failing the whole course.
        }
        $created = create_module((object) $info);
        return (int) $created->coursemodule;
    }

    /**
     * Make a short name unique by appending -2, -3, ...
     *
     * @param string $wanted
     * @return string
     */
    protected static function unique_shortname(string $wanted): string {
        global $DB;
        $base = \core_text::substr(trim($wanted) ?: 'COURSE', 0, 90);
        $name = $base;
        $n = 2;
        while ($DB->record_exists('course', ['shortname' => $name])) {
            $name = $base . '-' . $n++;
        }
        return $name;
    }

    /**
     * Result structure.
     *
     * @return external_single_structure
     */
    public static function execute_returns(): external_single_structure {
        return new external_single_structure([
            'courseid' => new external_value(PARAM_INT, 'New course id'),
            'shortname' => new external_value(PARAM_TEXT, 'Short name actually used'),
            'activities' => new external_value(PARAM_INT, 'Number of activities created'),
        ]);
    }
}
