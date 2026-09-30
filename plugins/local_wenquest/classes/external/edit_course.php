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
use core_external\external_single_structure;
use core_external\external_value;

/**
 * Teachers edit their course in WenQuest: course settings, chapters (sections) and the content in them.
 * One action per call; fields left null are not changed.
 *
 * Actions: course, addsection, section, movesection, deletesection, module, movemodule, deletemodule, content.
 *
 * @package    local_wenquest
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
class edit_course extends external_api {
    /**
     * Parameters.
     *
     * @return external_function_parameters
     */
    public static function execute_parameters(): external_function_parameters {
        $opt = fn($type, $desc) => new external_value($type, $desc, VALUE_DEFAULT, null);
        return new external_function_parameters([
            'courseid' => new external_value(PARAM_INT, 'Course id'),
            'action' => new external_value(PARAM_ALPHA, 'What to do'),
            'sectionid' => $opt(PARAM_INT, 'Section (section, movesection, deletesection; target of movemodule)'),
            'cmid' => $opt(PARAM_INT, 'Course module (module, movemodule, deletemodule, content)'),
            'name' => $opt(PARAM_TEXT, 'New name (course full name, section or activity name)'),
            'summary' => $opt(PARAM_RAW, 'Course or section summary (HTML)'),
            'visible' => $opt(PARAM_INT, '1 visible to students, 0 hidden'),
            'position' => $opt(PARAM_INT, 'addsection: insert at this section number (0 = at the end); movesection: target number'),
            'beforecmid' => $opt(PARAM_INT, 'movemodule: put before this activity (0 = at the end)'),
            'force' => $opt(PARAM_BOOL, 'deletesection: also delete the activities in it'),
            'content' => $opt(PARAM_RAW, 'Page content (HTML)'),
            'url' => $opt(PARAM_URL, 'Link target'),
            'intro' => $opt(PARAM_RAW, 'Activity description / instructions (HTML)'),
            'duedate' => $opt(PARAM_INT, 'Assignment due date (0 = none)'),
            'cutoffdate' => $opt(PARAM_INT, 'Assignment cut-off date (0 = none)'),
            'grade' => $opt(PARAM_FLOAT, 'Assignment maximum grade'),
            'allowtext' => $opt(PARAM_BOOL, 'Assignment accepts online text'),
            'allowfiles' => $opt(PARAM_BOOL, 'Assignment accepts files'),
            'maxfiles' => $opt(PARAM_INT, 'Assignment: most files a student may upload'),
            'draftitemid' => $opt(PARAM_INT, 'replacefile: the uploaded file (draft area) that replaces a file activity\'s file'),
        ]);
    }

    /**
     * Do one edit.
     *
     * @param int $courseid
     * @param string $action
     * @param int|null $sectionid
     * @param int|null $cmid
     * @param string|null $name
     * @param string|null $summary
     * @param int|null $visible
     * @param int|null $position
     * @param int|null $beforecmid
     * @param bool|null $force
     * @param string|null $content
     * @param string|null $url
     * @param string|null $intro
     * @param int|null $duedate
     * @param int|null $cutoffdate
     * @param float|null $grade
     * @param bool|null $allowtext
     * @param bool|null $allowfiles
     * @param int|null $maxfiles
     * @param int|null $draftitemid
     * @return array
     */
    public static function execute(int $courseid, string $action, ?int $sectionid = null, ?int $cmid = null, ?string $name = null,
            ?string $summary = null, ?int $visible = null, ?int $position = null, ?int $beforecmid = null, ?bool $force = null,
            ?string $content = null, ?string $url = null, ?string $intro = null, ?int $duedate = null, ?int $cutoffdate = null,
            ?float $grade = null, ?bool $allowtext = null, ?bool $allowfiles = null, ?int $maxfiles = null,
            ?int $draftitemid = null): array {
        global $CFG, $DB;
        require_once($CFG->dirroot . '/course/lib.php');
        require_once($CFG->dirroot . '/course/modlib.php');
        $p = self::validate_parameters(self::execute_parameters(), compact('courseid', 'action', 'sectionid', 'cmid', 'name',
            'summary', 'visible', 'position', 'beforecmid', 'force', 'content', 'url', 'intro', 'duedate', 'cutoffdate', 'grade',
            'allowtext', 'allowfiles', 'maxfiles', 'draftitemid'));
        $course = get_course($p['courseid']);
        $context = \context_course::instance($course->id);
        self::validate_context($context);
        $has = fn($k) => $p[$k] !== null;
        $html = fn($t) => clean_text((string) $t, FORMAT_HTML);
        $out = ['ok' => true, 'sectionid' => 0, 'cmid' => 0];

        $section = null;
        if ($has('sectionid')) {
            $section = $DB->get_record('course_sections', ['id' => $p['sectionid'], 'course' => $course->id], '*', MUST_EXIST);
        }
        $cm = null;
        if ($has('cmid')) {
            $cm = get_coursemodule_from_id('', $p['cmid'], $course->id, false, MUST_EXIST);
        }
        $need = function(string ...$fields) use ($p) {
            foreach ($fields as $f) {
                if ($p[$f] === null) {
                    throw new \invalid_parameter_exception("$f is required for {$p['action']}");
                }
            }
        };

        switch ($p['action']) {
            case 'course':
                require_capability('moodle/course:update', $context);
                $data = (object) ['id' => $course->id];
                if ($has('name') && trim($p['name']) !== '') {
                    $data->fullname = trim($p['name']);
                }
                if ($has('summary')) {
                    $data->summary = $html($p['summary']);
                    $data->summaryformat = FORMAT_HTML;
                }
                if ($has('visible')) {
                    require_capability('moodle/course:visibility', $context);
                    $data->visible = $p['visible'] ? 1 : 0;
                }
                update_course($data);
                break;

            case 'addsection':
                require_capability('moodle/course:update', $context);
                $new = course_create_section($course, $p['position'] ?? 0);
                $update = [];
                if ($has('name')) {
                    $update['name'] = trim($p['name']);
                }
                if ($has('summary')) {
                    $update['summary'] = $html($p['summary']);
                    $update['summaryformat'] = FORMAT_HTML;
                }
                if ($update) {
                    course_update_section($course, $new, $update);
                }
                $out['sectionid'] = (int) $new->id;
                break;

            case 'section':
                require_capability('moodle/course:update', $context);
                $need('sectionid');
                $update = [];
                if ($has('name')) {
                    $update['name'] = trim($p['name']);
                }
                if ($has('summary')) {
                    $update['summary'] = $html($p['summary']);
                    $update['summaryformat'] = FORMAT_HTML;
                }
                if ($has('visible')) {
                    require_capability('moodle/course:sectionvisibility', $context);
                    $update['visible'] = $p['visible'] ? 1 : 0;
                }
                if ($update) {
                    course_update_section($course, $section, $update);
                }
                $out['sectionid'] = (int) $section->id;
                break;

            case 'movesection':
                require_capability('moodle/course:movesections', $context);
                $need('sectionid', 'position');
                if ((int) $section->section === 0 || $p['position'] < 1) {
                    throw new \invalid_parameter_exception('the general section stays first');
                }
                if (!move_section_to($course, $section->section, $p['position'])) {
                    throw new \moodle_exception('cannotmovesection', 'error');
                }
                break;

            case 'deletesection':
                require_capability('moodle/course:update', $context);
                $need('sectionid');
                if ((int) $section->section === 0) {
                    throw new \invalid_parameter_exception('the general section cannot be deleted');
                }
                if (!course_delete_section($course, $section, (bool) $p['force'])) {
                    throw new \moodle_exception('sectionnotempty', 'local_wenquest');
                }
                break;

            case 'module':
                $need('cmid');
                require_capability('moodle/course:manageactivities', \context_module::instance($cm->id));
                if ($has('name') && trim($p['name']) !== '') {
                    set_coursemodule_name($cm->id, trim($p['name']));
                }
                if ($has('visible')) {
                    require_capability('moodle/course:activityvisibility', \context_module::instance($cm->id));
                    set_coursemodule_visible($cm->id, $p['visible'] ? 1 : 0);
                    \core\event\course_module_updated::create_from_cm($cm)->trigger();
                }
                $out['cmid'] = (int) $cm->id;
                break;

            case 'movemodule':
                $need('cmid', 'sectionid');
                require_capability('moodle/course:manageactivities', $context);
                $before = null;
                if (!empty($p['beforecmid'])) {
                    $before = get_coursemodule_from_id('', $p['beforecmid'], $course->id, false, MUST_EXIST);
                    if ((int) $before->section !== (int) $section->id) {
                        throw new \invalid_parameter_exception('beforecmid is in another section');
                    }
                }
                moveto_module($cm, $section, $before);
                $out['cmid'] = (int) $cm->id;
                break;

            case 'deletemodule':
                $need('cmid');
                require_capability('moodle/course:manageactivities', \context_module::instance($cm->id));
                course_delete_module($cm->id);
                break;

            case 'content':
                $need('cmid');
                $modcontext = \context_module::instance($cm->id);
                require_capability('moodle/course:manageactivities', $modcontext);
                $table = $cm->modname;
                $rec = $DB->get_record($table, ['id' => $cm->instance], '*', MUST_EXIST);
                $update = ['id' => $rec->id, 'timemodified' => time()];
                if ($has('intro') && property_exists($rec, 'intro')) {
                    $update['intro'] = $html($p['intro']);
                    $update['introformat'] = FORMAT_HTML;
                }
                if ($table === 'page' && $has('content')) {
                    $update['content'] = $html($p['content']);
                    $update['contentformat'] = FORMAT_HTML;
                    $update['revision'] = (int) $rec->revision + 1;
                }
                if ($table === 'url' && $has('url') && $p['url'] !== '') {
                    $update['externalurl'] = $p['url'];
                }
                if ($table === 'assign') {
                    foreach (['duedate', 'cutoffdate'] as $f) {
                        if ($has($f)) {
                            $update[$f] = max(0, $p[$f]);
                        }
                    }
                    if ($has('grade')) {
                        $update['grade'] = max(1, $p['grade']);
                    }
                }
                if ($has('name') && trim($p['name']) !== '') {
                    $update['name'] = trim($p['name']);
                }
                $DB->update_record($table, (object) $update);
                if ($table === 'assign') {
                    require_once($CFG->dirroot . '/mod/assign/locallib.php');
                    $assign = new \assign($modcontext, $cm, $course);
                    foreach (['onlinetext' => 'allowtext', 'file' => 'allowfiles'] as $type => $field) {
                        if ($has($field)) {
                            $plugin = $assign->get_submission_plugin_by_type($type);
                            $p[$field] ? $plugin->enable() : $plugin->disable();
                        }
                    }
                    if ($has('maxfiles')) {
                        $assign->get_submission_plugin_by_type('file')->set_config('maxfilesubmissions', max(1, min(20, $p['maxfiles'])));
                    }
                    $instance = $DB->get_record('assign', ['id' => $rec->id], '*', MUST_EXIST);
                    $instance->cmidnumber = $cm->idnumber;
                    assign_grade_item_update($instance);
                    $assign = new \assign($modcontext, $cm, $course);
                    $assign->update_calendar($cm->id);
                }
                \core\event\course_module_updated::create_from_cm($cm)->trigger();
                $out['cmid'] = (int) $cm->id;
                break;

            case 'replacefile':
                // Replace the file of a file activity (e.g. the chapter's virtual lab page) and keep the activity.
                $need('cmid', 'draftitemid');
                if ($cm->modname !== 'resource') {
                    throw new \invalid_parameter_exception('replacefile works on file activities only');
                }
                $modcontext = \context_module::instance($cm->id);
                require_capability('moodle/course:manageactivities', $modcontext);
                file_save_draft_area_files($p['draftitemid'], $modcontext->id, 'mod_resource', 'content', 0,
                    ['subdirs' => 0, 'maxfiles' => 1]);
                $fs = get_file_storage();
                $files = $fs->get_area_files($modcontext->id, 'mod_resource', 'content', 0, 'sortorder DESC, id ASC', false);
                if (!$files) {
                    throw new \invalid_parameter_exception('no file was uploaded');
                }
                $main = reset($files);
                file_set_sortorder($modcontext->id, 'mod_resource', 'content', 0, $main->get_filepath(), $main->get_filename(), 1);
                $rev = (int) $DB->get_field('resource', 'revision', ['id' => $cm->instance]);
                $DB->update_record('resource', (object) ['id' => $cm->instance, 'revision' => $rev + 1, 'timemodified' => time()]);
                \core\event\course_module_updated::create_from_cm($cm)->trigger();
                $out['cmid'] = (int) $cm->id;
                break;

            default:
                throw new \invalid_parameter_exception('unknown action');
        }
        rebuild_course_cache($course->id, true);
        return $out;
    }

    /**
     * Result structure.
     *
     * @return external_single_structure
     */
    public static function execute_returns(): external_single_structure {
        return new external_single_structure([
            'ok' => new external_value(PARAM_BOOL, 'Done'),
            'sectionid' => new external_value(PARAM_INT, 'New or changed section'),
            'cmid' => new external_value(PARAM_INT, 'Changed activity'),
        ]);
    }
}
