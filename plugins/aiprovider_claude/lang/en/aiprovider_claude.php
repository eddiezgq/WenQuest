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
/**
 * Strings for component aiprovider_claude, language 'en'.
 *
 * @package    aiprovider_claude
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

$string['action:explain_text:endpoint'] = 'API endpoint';
$string['action:explain_text:model'] = 'Text explanation model';
$string['action:explain_text:model_help'] = 'The Claude model used to explain the provided text.';
$string['action:explain_text:systeminstruction'] = 'System instruction';
$string['action:explain_text:systeminstruction_help'] = 'This instruction is sent to Claude along with the user\'s prompt. Editing this instruction is not recommended unless absolutely required.';
$string['action:generate_text:endpoint'] = 'API endpoint';
$string['action:generate_text:model'] = 'AI model';
$string['action:generate_text:model_help'] = 'The Claude model used to generate the text response.';
$string['action:generate_text:systeminstruction'] = 'System instruction';
$string['action:generate_text:systeminstruction_help'] = 'This instruction is sent to Claude along with the user\'s prompt. Editing this instruction is not recommended unless absolutely required.';
$string['action:summarise_text:endpoint'] = 'API endpoint';
$string['action:summarise_text:model'] = 'AI model';
$string['action:summarise_text:model_help'] = 'The Claude model used to summarise the provided text.';
$string['action:summarise_text:systeminstruction'] = 'System instruction';
$string['action:summarise_text:systeminstruction_help'] = 'This instruction is sent to Claude along with the user\'s prompt. Editing this instruction is not recommended unless absolutely required.';
$string['apikey'] = 'Anthropic API key';
$string['apikey_help'] = 'Create a key in the <a href="https://console.anthropic.com/settings/keys" target="_blank">Anthropic Console</a>. A claude.ai subscription does not include API access.';
$string['custom_model_name'] = 'Custom model name';
$string['extraparams'] = 'Extra parameters';
$string['extraparams_help'] = 'Extra Messages API parameters in JSON format. For example:
<pre>
{
    "temperature": 0.5,
    "max_tokens": 1024
}
</pre>';
$string['invalidjson'] = 'Invalid JSON string';
$string['pluginname'] = 'Anthropic Claude API provider';
$string['privacy:metadata'] = 'The Anthropic Claude API provider plugin does not store any personal data.';
$string['privacy:metadata:aiprovider_claude:externalpurpose'] = 'This information is sent to the Anthropic API in order for a response to be generated. Your Anthropic account settings may change how Anthropic stores and retains this data. No user data is explicitly sent to Anthropic or stored in Moodle LMS by this plugin.';
$string['privacy:metadata:aiprovider_claude:model'] = 'The model used to generate the response.';
$string['privacy:metadata:aiprovider_claude:prompttext'] = 'The user entered text prompt used to generate the response.';
$string['settings'] = 'Settings';
$string['settings_help'] = 'Adjust the settings below to customise how requests are sent to Claude.';
$string['settings_max_tokens'] = 'max_tokens';
$string['settings_max_tokens_help'] = 'The maximum number of tokens Claude may generate. The Messages API requires this value; if left empty, 4096 is used.';
$string['settings_temperature'] = 'temperature';
$string['settings_temperature_help'] = 'Amount of randomness, from 0.0 to 1.0. Use values near 0 for grading and analysis, and higher values for creative tasks. Leave empty to use the model default.';
