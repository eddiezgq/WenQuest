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
 * Online class sessions (Tencent Meeting / Zoom): list, save, delete. Each session also appears in
 * the course calendar.
 *
 * @package    local_wenquest
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
class meetings extends external_api {
    /** Providers WenQuest knows how to label. */
    const PROVIDERS = ['tencent', 'zoom', 'other'];

    /**
     * Parameters for listing.
     *
     * @return external_function_parameters
     */
    public static function get_parameters(): external_function_parameters {
        return new external_function_parameters(['courseid' => new external_value(PARAM_INT, 'Course id')]);
    }

    /**
     * The course's sessions, newest start last.
     *
     * @param int $courseid
     * @return array
     */
    public static function get(int $courseid): array {
        global $DB;
        $p = self::validate_parameters(self::get_parameters(), ['courseid' => $courseid]);
        $context = \context_course::instance($p['courseid']);
        self::validate_context($context);
        $rows = $DB->get_records('local_wenquest_meeting', ['courseid' => $p['courseid']], 'timestart ASC');
        return ['meetings' => array_values(array_map([self::class, 'export'], $rows)),
                'canmanage' => has_capability('moodle/course:update', $context)];
    }

    /**
     * Listing result.
     *
     * @return external_single_structure
     */
    public static function get_returns(): external_single_structure {
        return new external_single_structure([
            'meetings' => new external_multiple_structure(self::structure()),
            'canmanage' => new external_value(PARAM_BOOL, 'Current user may add and change sessions'),
        ]);
    }

    /**
     * Parameters for saving.
     *
     * @return external_function_parameters
     */
    public static function save_parameters(): external_function_parameters {
        return new external_function_parameters([
            'courseid' => new external_value(PARAM_INT, 'Course id'),
            'id' => new external_value(PARAM_INT, '0 = new session', VALUE_DEFAULT, 0),
            'name' => new external_value(PARAM_TEXT, 'Topic'),
            'provider' => new external_value(PARAM_ALPHA, 'tencent, zoom or other', VALUE_DEFAULT, 'tencent'),
            'url' => new external_value(PARAM_URL, 'Join link', VALUE_DEFAULT, ''),
            'meetingcode' => new external_value(PARAM_TEXT, 'Meeting number', VALUE_DEFAULT, ''),
            'passcode' => new external_value(PARAM_TEXT, 'Password', VALUE_DEFAULT, ''),
            'notes' => new external_value(PARAM_TEXT, 'Notes for students', VALUE_DEFAULT, ''),
            'timestart' => new external_value(PARAM_INT, 'Start (Unix time)'),
            'duration' => new external_value(PARAM_INT, 'Minutes', VALUE_DEFAULT, 90),
        ]);
    }

    /**
     * Create or update a session and its calendar event.
     *
     * @param int $courseid
     * @param int $id
     * @param string $name
     * @param string $provider
     * @param string $url
     * @param string $meetingcode
     * @param string $passcode
     * @param string $notes
     * @param int $timestart
     * @param int $duration
     * @return array
     */
    public static function save(int $courseid, int $id, string $name, string $provider, string $url, string $meetingcode,
            string $passcode, string $notes, int $timestart, int $duration): array {
        global $CFG, $DB;
        require_once($CFG->dirroot . '/calendar/lib.php');
        $p = self::validate_parameters(self::save_parameters(), [
            'courseid' => $courseid, 'id' => $id, 'name' => $name, 'provider' => $provider, 'url' => $url,
            'meetingcode' => $meetingcode, 'passcode' => $passcode, 'notes' => $notes,
            'timestart' => $timestart, 'duration' => $duration,
        ]);
        $context = \context_course::instance($p['courseid']);
        self::validate_context($context);
        require_capability('moodle/course:update', $context);
        if (trim($p['name']) === '' || $p['timestart'] <= 0) {
            throw new \invalid_parameter_exception('topic and start time are required');
        }
        if ($p['url'] === '' && trim($p['meetingcode']) === '') {
            throw new \invalid_parameter_exception('a join link or a meeting number is required');
        }
        $rec = $p['id'] ? $DB->get_record('local_wenquest_meeting', ['id' => $p['id'], 'courseid' => $p['courseid']], '*', MUST_EXIST)
            : (object) ['courseid' => $p['courseid'], 'eventid' => 0];
        $rec->name = \core_text::substr(trim($p['name']), 0, 255);
        $rec->provider = in_array($p['provider'], self::PROVIDERS, true) ? $p['provider'] : 'other';
        $rec->url = $p['url'];
        $rec->meetingcode = \core_text::substr(trim($p['meetingcode']), 0, 64);
        $rec->passcode = \core_text::substr(trim($p['passcode']), 0, 64);
        $rec->notes = $p['notes'];
        $rec->timestart = $p['timestart'];
        $rec->duration = max(5, min(600, $p['duration']));
        $rec->timemodified = time();

        // The calendar shows the session with its join details.
        $label = ['tencent' => '腾讯会议', 'zoom' => 'Zoom', 'other' => '在线课堂'][$rec->provider];
        $desc = '<p>' . s($label) . ($rec->meetingcode ? ' · ' . s($rec->meetingcode) : '')
            . ($rec->passcode ? ' · ' . s($rec->passcode) : '') . '</p>'
            . ($rec->url ? '<p><a href="' . s($rec->url) . '">' . s($rec->url) . '</a></p>' : '')
            . ($rec->notes ? '<p>' . s($rec->notes) . '</p>' : '');
        $data = (object) [
            'name' => $label . '：' . $rec->name, 'description' => $desc, 'format' => FORMAT_HTML,
            'courseid' => $rec->courseid, 'groupid' => 0, 'userid' => 0, 'modulename' => '', 'instance' => 0,
            'eventtype' => 'course', 'timestart' => $rec->timestart, 'timeduration' => $rec->duration * 60, 'visible' => 1,
        ];
        $event = $rec->eventid ? \calendar_event::load($rec->eventid) : null;
        if ($event) {
            $event->update($data, false);
        } else {
            $event = \calendar_event::create($data, false);
            $rec->eventid = $event ? (int) $event->id : 0;
        }
        if (!empty($rec->id)) {
            $DB->update_record('local_wenquest_meeting', $rec);
        } else {
            $rec->id = $DB->insert_record('local_wenquest_meeting', $rec);
        }
        return self::export($DB->get_record('local_wenquest_meeting', ['id' => $rec->id]));
    }

    /**
     * Saving result.
     *
     * @return external_single_structure
     */
    public static function save_returns(): external_single_structure {
        return self::structure();
    }

    /**
     * Parameters for deleting.
     *
     * @return external_function_parameters
     */
    public static function delete_parameters(): external_function_parameters {
        return new external_function_parameters([
            'courseid' => new external_value(PARAM_INT, 'Course id'),
            'id' => new external_value(PARAM_INT, 'Session'),
        ]);
    }

    /**
     * Delete a session and its calendar event.
     *
     * @param int $courseid
     * @param int $id
     * @return array
     */
    public static function delete(int $courseid, int $id): array {
        global $CFG, $DB;
        require_once($CFG->dirroot . '/calendar/lib.php');
        $p = self::validate_parameters(self::delete_parameters(), ['courseid' => $courseid, 'id' => $id]);
        $context = \context_course::instance($p['courseid']);
        self::validate_context($context);
        require_capability('moodle/course:update', $context);
        $rec = $DB->get_record('local_wenquest_meeting', ['id' => $p['id'], 'courseid' => $p['courseid']], '*', MUST_EXIST);
        if ($rec->eventid && $DB->record_exists('event', ['id' => $rec->eventid])) {
            \calendar_event::load($rec->eventid)->delete();
        }
        $DB->delete_records('local_wenquest_meeting', ['id' => $rec->id]);
        return ['deleted' => true];
    }

    /**
     * Deleting result.
     *
     * @return external_single_structure
     */
    public static function delete_returns(): external_single_structure {
        return new external_single_structure(['deleted' => new external_value(PARAM_BOOL, 'Deleted')]);
    }

    /**
     * One session for the web service.
     *
     * @param \stdClass $r
     * @return array
     */
    public static function export(\stdClass $r): array {
        return [
            'id' => (int) $r->id, 'courseid' => (int) $r->courseid, 'name' => $r->name, 'provider' => $r->provider,
            'url' => (string) $r->url, 'meetingcode' => (string) $r->meetingcode, 'passcode' => (string) $r->passcode,
            'notes' => (string) $r->notes, 'timestart' => (int) $r->timestart, 'duration' => (int) $r->duration,
        ];
    }

    /**
     * Structure of one session.
     *
     * @return external_single_structure
     */
    private static function structure(): external_single_structure {
        return new external_single_structure([
            'id' => new external_value(PARAM_INT, 'Id'),
            'courseid' => new external_value(PARAM_INT, 'Course'),
            'name' => new external_value(PARAM_TEXT, 'Topic'),
            'provider' => new external_value(PARAM_ALPHA, 'tencent, zoom or other'),
            'url' => new external_value(PARAM_RAW, 'Join link'),
            'meetingcode' => new external_value(PARAM_TEXT, 'Meeting number'),
            'passcode' => new external_value(PARAM_TEXT, 'Password'),
            'notes' => new external_value(PARAM_TEXT, 'Notes'),
            'timestart' => new external_value(PARAM_INT, 'Start'),
            'duration' => new external_value(PARAM_INT, 'Minutes'),
        ]);
    }
}
