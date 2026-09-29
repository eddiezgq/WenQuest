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
 * Add activities to one section of an existing course, so the AI professor team can publish
 * a course lesson by lesson. The section is created when it does not exist yet, and can be
 * (re)named at the same time.
 *
 * @package    local_wenquest
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
class add_activities extends external_api {
    /**
     * Parameters.
     *
     * @return external_function_parameters
     */
    public static function execute_parameters(): external_function_parameters {
        $activity = new external_single_structure([
            'type' => new external_value(PARAM_ALPHA, 'page, url, assign, resource or forum'),
            'name' => new external_value(PARAM_TEXT, 'Activity name (multilang allowed)'),
            'intro' => new external_value(PARAM_RAW, 'Short description (HTML)', VALUE_DEFAULT, ''),
            'content' => new external_value(PARAM_RAW, 'Page content (HTML)', VALUE_DEFAULT, ''),
            'url' => new external_value(PARAM_URL, 'Link target for url activities', VALUE_DEFAULT, ''),
            'draftitemid' => new external_value(PARAM_INT, 'Draft area with the uploaded file (resource)', VALUE_DEFAULT, 0),
            'visible' => new external_value(PARAM_INT, '1 = students see it, 0 = teachers only', VALUE_DEFAULT, 1),
        ]);
        return new external_function_parameters([
            'courseid' => new external_value(PARAM_INT, 'Course id'),
            'section' => new external_value(PARAM_INT, 'Section number (1 = first chapter); created if missing'),
            'sectionname' => new external_value(PARAM_TEXT, 'New section name; empty keeps the current one', VALUE_DEFAULT, ''),
            'sectionsummary' => new external_value(PARAM_RAW, 'New section summary (HTML); empty keeps it', VALUE_DEFAULT, ''),
            'activities' => new external_multiple_structure($activity, 'Activities', VALUE_DEFAULT, []),
        ]);
    }

    /**
     * Add the activities.
     *
     * @param int $courseid
     * @param int $section
     * @param string $sectionname
     * @param string $sectionsummary
     * @param array $activities
     * @return array
     */
    public static function execute(int $courseid, int $section, string $sectionname, string $sectionsummary,
            array $activities): array {
        global $CFG, $DB;
        require_once($CFG->dirroot . '/course/lib.php');
        require_once($CFG->dirroot . '/course/modlib.php');
        require_once($CFG->libdir . '/resourcelib.php');

        $params = self::validate_parameters(self::execute_parameters(), [
            'courseid' => $courseid, 'section' => $section, 'sectionname' => $sectionname,
            'sectionsummary' => $sectionsummary, 'activities' => $activities,
        ]);
        $course = get_course($params['courseid']);
        $context = \context_course::instance($course->id);
        self::validate_context($context);
        require_capability('moodle/course:manageactivities', $context);
        require_capability('moodle/course:update', $context);
        if ($params['section'] < 0 || $params['section'] > 200) {
            throw new \invalid_parameter_exception('section out of range');
        }

        $transaction = $DB->start_delegated_transaction();
        course_create_sections_if_missing($course, range(0, $params['section']));
        $record = $DB->get_record('course_sections', ['course' => $course->id, 'section' => $params['section']], '*', MUST_EXIST);
        $update = [];
        if (trim($params['sectionname']) !== '') {
            $update['name'] = $params['sectionname'];
        }
        if (trim($params['sectionsummary']) !== '') {
            $update['summary'] = clean_text($params['sectionsummary'], FORMAT_HTML);
            $update['summaryformat'] = FORMAT_HTML;
        }
        if ($update) {
            course_update_section($course, $record, $update);
        }
        $cmids = [];
        foreach ($params['activities'] as $activity) {
            $cmid = create_course::add_activity($course, $params['section'], $activity);
            if ($cmid) {
                $cmids[] = $cmid;
            }
        }
        $transaction->allow_commit();
        rebuild_course_cache($course->id, true);
        return ['courseid' => (int) $course->id, 'sectionid' => (int) $record->id, 'cmids' => $cmids];
    }

    /**
     * Result structure.
     *
     * @return external_single_structure
     */
    public static function execute_returns(): external_single_structure {
        return new external_single_structure([
            'courseid' => new external_value(PARAM_INT, 'Course id'),
            'sectionid' => new external_value(PARAM_INT, 'Section id'),
            'cmids' => new external_multiple_structure(new external_value(PARAM_INT, 'Course module id'), 'New activities'),
        ]);
    }
}
