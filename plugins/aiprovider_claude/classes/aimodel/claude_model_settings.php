<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

namespace aiprovider_claude\aimodel;

use MoodleQuickForm;

/**
 * Settings shared by all Claude text models.
 *
 * @package    aiprovider_claude
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
trait claude_model_settings {
    #[\Override]
    public function get_model_settings(): array {
        $settings = [];
        foreach (['temperature' => PARAM_FLOAT, 'max_tokens' => PARAM_INT] as $key => $type) {
            $settings[$key] = [
                'elementtype' => 'text',
                'label' => ['identifier' => 'settings_' . $key, 'component' => 'aiprovider_claude'],
                'type' => $type,
                'help' => ['identifier' => 'settings_' . $key, 'component' => 'aiprovider_claude'],
            ];
        }
        return $settings;
    }

    #[\Override]
    public function add_model_settings(MoodleQuickForm $mform): void {
        foreach ($this->get_model_settings() as $key => $setting) {
            $mform->addElement(
                $setting['elementtype'],
                $key,
                get_string($setting['label']['identifier'], $setting['label']['component']),
            );
            $mform->setType($key, $setting['type']);
            $mform->addHelpButton($key, $setting['help']['identifier'], $setting['help']['component']);
        }
    }

    #[\Override]
    public function model_type(): int {
        return self::MODEL_TYPE_TEXT;
    }
}
