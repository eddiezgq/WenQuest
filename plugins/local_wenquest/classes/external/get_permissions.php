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
 * What the current user may do in WenQuest.
 *
 * @package    local_wenquest
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
class get_permissions extends external_api {
    /**
     * No parameters.
     *
     * @return external_function_parameters
     */
    public static function execute_parameters(): external_function_parameters {
        return new external_function_parameters([]);
    }

    /**
     * Report the permissions.
     *
     * @return array
     */
    public static function execute(): array {
        $context = \context_system::instance();
        self::validate_context($context);
        $category = \core_course_category::get_default();
        $catcontext = \context_coursecat::instance($category->id);
        return [
            'cancreatecourses' => has_capability('moodle/course:create', $catcontext),
            'issiteadmin' => is_siteadmin(),
        ];
    }

    /**
     * Result structure.
     *
     * @return external_single_structure
     */
    public static function execute_returns(): external_single_structure {
        return new external_single_structure([
            'cancreatecourses' => new external_value(PARAM_BOOL, 'May create courses'),
            'issiteadmin' => new external_value(PARAM_BOOL, 'Is a site administrator'),
        ]);
    }
}
