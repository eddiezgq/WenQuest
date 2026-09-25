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

namespace aiprovider_claude;

/**
 * Trait for test cases.
 *
 * @package    aiprovider_claude
 * @copyright  2025 Yusuf Wibisono <yusuf.wibisono@moodle.com>, 2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
trait testcase_helper_trait {
    /**
     * Create the provider object.
     *
     * @param string $actionclass The action class to use.
     * @param array $actionconfig The action configuration to use.
     * @param bool $ratelimited Whether to apply the strict test rate limits.
     */
    public function create_provider(
        string $actionclass,
        array $actionconfig = [],
        bool $ratelimited = true,
    ): \core_ai\provider {
        $manager = \core\di::get(\core_ai\manager::class);
        $config = [
            'enableuserratelimit' => true,
            'userratelimit' => 1,
            'enableglobalratelimit' => true,
            'globalratelimit' => 1,
            'apikey' => '123',
        ];
        if (!$ratelimited) {
            $config['enableuserratelimit'] = false;
            $config['enableglobalratelimit'] = false;
        }
        $defaultactionconfig = [
            $actionclass => [
                'settings' => [
                    'model' => 'claude-sonnet-5',
                    'endpoint' => "https://api.anthropic.com/v1/messages",
                ],
            ],
        ];
        foreach ($actionconfig as $key => $value) {
            $defaultactionconfig[$actionclass]['settings'][$key] = $value;
        }
        $provider = $manager->create_provider_instance(
            classname: '\aiprovider_claude\provider',
            name: 'dummy',
            config: $config,
            actionconfig: $defaultactionconfig,
        );

        return $provider;
    }
}
