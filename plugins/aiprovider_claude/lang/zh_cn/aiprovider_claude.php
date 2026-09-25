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
 * Strings for component aiprovider_claude, language 'zh_cn'.
 *
 * @package    aiprovider_claude
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

$string['action:explain_text:endpoint'] = 'API 地址';
$string['action:explain_text:model'] = '文本解释模型';
$string['action:explain_text:model_help'] = '用于解释所选文本的 Claude 模型。';
$string['action:explain_text:systeminstruction'] = '系统指令';
$string['action:explain_text:systeminstruction_help'] = '该指令会与用户的提示一起发送给 Claude。除非确有需要，不建议修改。';
$string['action:generate_text:endpoint'] = 'API 地址';
$string['action:generate_text:model'] = 'AI 模型';
$string['action:generate_text:model_help'] = '用于生成文本的 Claude 模型。';
$string['action:generate_text:systeminstruction'] = '系统指令';
$string['action:generate_text:systeminstruction_help'] = '该指令会与用户的提示一起发送给 Claude。除非确有需要，不建议修改。';
$string['action:summarise_text:endpoint'] = 'API 地址';
$string['action:summarise_text:model'] = 'AI 模型';
$string['action:summarise_text:model_help'] = '用于生成摘要的 Claude 模型。';
$string['action:summarise_text:systeminstruction'] = '系统指令';
$string['action:summarise_text:systeminstruction_help'] = '该指令会与用户的提示一起发送给 Claude。除非确有需要，不建议修改。';
$string['apikey'] = 'Anthropic API 密钥';
$string['apikey_help'] = '在 <a href="https://console.anthropic.com/settings/keys" target="_blank">Anthropic Console</a> 创建密钥。claude.ai 的订阅不包含 API 使用权限。';
$string['custom_model_name'] = '自定义模型名称';
$string['extraparams'] = '额外参数';
$string['extraparams_help'] = 'JSON 格式的 Messages API 额外参数，例如：
<pre>
{
    "temperature": 0.5,
    "max_tokens": 1024
}
</pre>';
$string['invalidjson'] = 'JSON 格式无效';
$string['pluginname'] = 'Anthropic Claude API 提供方';
$string['privacy:metadata'] = 'Anthropic Claude API 提供方插件不存储任何个人数据。';
$string['privacy:metadata:aiprovider_claude:externalpurpose'] = '这些信息会发送到 Anthropic API 以生成回复。Anthropic 如何保存这些数据取决于你的 Anthropic 账户设置。本插件不会向 Anthropic 明确发送用户数据，也不在 Moodle 中存储这些数据。';
$string['privacy:metadata:aiprovider_claude:model'] = '生成回复所用的模型。';
$string['privacy:metadata:aiprovider_claude:prompttext'] = '用户输入的提示文本。';
$string['settings'] = '设置';
$string['settings_help'] = '调整以下设置，自定义发送给 Claude 的请求。';
$string['settings_max_tokens'] = 'max_tokens（最大输出长度）';
$string['settings_max_tokens_help'] = 'Claude 最多可生成的 token 数。Messages API 要求提供此值；留空时使用 4096。';
$string['settings_temperature'] = 'temperature（随机度）';
$string['settings_temperature_help'] = '随机程度，取值 0.0–1.0。批改和分析建议接近 0，创作类任务可适当调高。留空则使用模型默认值。';
