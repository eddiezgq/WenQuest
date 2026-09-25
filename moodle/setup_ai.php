<?php
// This file is part of the WenQuest deployment package.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Configure AI providers, placements, language and timezone from environment variables.
 *
 * Safe to run on every container start: existing provider instances are updated, not duplicated.
 *
 * Environment:
 *   ANTHROPIC_API_KEY   Claude API key (optional)
 *   CLAUDE_MODEL        default claude-sonnet-5
 *   CLAUDE_ENDPOINT     default https://api.anthropic.com/v1/messages
 *   DEEPSEEK_API_KEY    DeepSeek API key (optional, for deployments in mainland China)
 *   MOODLE_LANG         default zh_cn (used only if the language pack is installed)
 *   MOODLE_TIMEZONE     default Asia/Shanghai
 *
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

define('CLI_SCRIPT', true);
require(__DIR__ . '/config.php');

$manager = \core\di::get(\core_ai\manager::class);
$textactions = [
    \core_ai\aiactions\generate_text::class,
    \core_ai\aiactions\summarise_text::class,
    \core_ai\aiactions\explain_text::class,
];

/**
 * Create or update one provider instance.
 *
 * @param \core_ai\manager $manager
 * @param string $classname Provider class, e.g. aiprovider_claude\provider
 * @param string $name Instance name
 * @param string $apikey API key
 * @param array $settings Per-action settings
 * @param array $actions Action classes to enable
 */
function wenquest_upsert_provider(\core_ai\manager $manager, string $classname, string $name, string $apikey,
        array $settings, array $actions): void {
    $actionconfig = [];
    foreach ($actions as $action) {
        $actionconfig[$action] = [
            'enabled' => true,
            'settings' => $settings + ['systeminstruction' => $action::get_system_instruction()],
        ];
    }
    $existing = $manager->get_provider_instances(['provider' => $classname]);
    if ($existing) {
        $provider = reset($existing);
        $config = $provider->config;
        $config['apikey'] = $apikey;
        $manager->update_provider_instance($provider, $config, $actionconfig);
        $manager->enable_provider_instance($manager->get_provider_instances(['id' => $provider->id])[$provider->id]);
        mtrace("Updated AI provider: {$name}");
    } else {
        $manager->create_provider_instance(classname: '\\' . $classname, name: $name, enabled: true,
            config: ['apikey' => $apikey], actionconfig: $actionconfig);
        mtrace("Created AI provider: {$name}");
    }
}

$configured = false;
if ($key = getenv('ANTHROPIC_API_KEY')) {
    wenquest_upsert_provider($manager, 'aiprovider_claude\provider', 'Claude', $key, [
        'model' => getenv('CLAUDE_MODEL') ?: 'claude-sonnet-5',
        'endpoint' => getenv('CLAUDE_ENDPOINT') ?: 'https://api.anthropic.com/v1/messages',
        'max_tokens' => 4096,
    ], $textactions);
    $configured = true;
}
if ($key = getenv('DEEPSEEK_API_KEY')) {
    wenquest_upsert_provider($manager, 'aiprovider_deepseek\provider', 'DeepSeek', $key, [
        'model' => 'deepseek-chat',
        'endpoint' => 'https://api.deepseek.com/chat/completions',
    ], $textactions);
    $configured = true;
}
if ($configured) {
    foreach (['courseassist', 'editor'] as $placement) {
        \core\plugininfo\aiplacement::enable_plugin($placement, 1);
    }
    mtrace('Enabled AI placements: course assistant, text editor');
} else {
    mtrace('No AI API key set; skipping AI provider setup.');
}

$lang = getenv('MOODLE_LANG') ?: 'zh_cn';
if (get_string_manager()->translation_exists($lang, false)) {
    set_config('lang', $lang);
    mtrace("Default language: {$lang}");
}
set_config('timezone', getenv('MOODLE_TIMEZONE') ?: 'Asia/Shanghai');
purge_caches();
