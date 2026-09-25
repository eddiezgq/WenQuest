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

use GuzzleHttp\Psr7\Request;
use Psr\Http\Message\RequestInterface;
use Psr\Http\Message\ResponseInterface;

/**
 * Class process text generation.
 *
 * @package    aiprovider_claude
 * @copyright  2025 Matt Porritt <matt.porritt@moodle.com>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
class process_generate_text extends abstract_processor {
    #[\Override]
    protected function get_system_instruction(): string {
        return $this->provider->actionconfig[$this->action::class]['settings']['systeminstruction']
            ?? $this->action::get_system_instruction();
    }

    #[\Override]
    protected function create_request_object(string $userid): RequestInterface {
        // Anthropic Messages API: the system prompt is a top-level field, not a message.
        $userobj = new \stdClass();
        $userobj->role = 'user';
        $userobj->content = $this->action->get_configuration('prompttext');

        $requestobj = new \stdClass();
        $requestobj->model = $this->get_model();
        $requestobj->max_tokens = helper::DEFAULT_MAX_TOKENS;
        $requestobj->messages = [$userobj];

        $systeminstruction = $this->get_system_instruction();
        if (!empty($systeminstruction)) {
            $requestobj->system = $systeminstruction;
        }

        // Anonymised user id, so Anthropic can detect abuse without receiving personal data.
        $requestobj->metadata = (object) ['user_id' => $userid];

        // Append the extra model settings (temperature, max_tokens, ...).
        foreach ($this->get_model_settings() as $setting => $value) {
            if ($value === '' || $value === null) {
                continue;
            }
            if ($setting === 'max_tokens') {
                $value = (int) $value;
            } else if (is_numeric($value)) {
                $value = (float) $value;
            }
            $requestobj->$setting = $value;
        }

        return new Request(
            method: 'POST',
            uri: '',
            headers: [
                'Content-Type' => 'application/json',
            ],
            body: json_encode($requestobj),
        );
    }

    /**
     * Handle a successful response from the external AI api.
     *
     * @param ResponseInterface $response The response object.
     * @return array The response.
     */
    protected function handle_api_success(ResponseInterface $response): array {
        $bodyobj = json_decode($response->getBody()->getContents());

        // A response can hold several content blocks; join the text ones.
        $text = '';
        foreach ($bodyobj->content ?? [] as $block) {
            if (($block->type ?? '') === 'text') {
                $text .= $block->text;
            }
        }

        return [
            'success' => true,
            'id' => $bodyobj->id,
            'fingerprint' => $bodyobj->id,
            'generatedcontent' => $text,
            'finishreason' => $bodyobj->stop_reason ?? '',
            'prompttokens' => $bodyobj->usage->input_tokens ?? 0,
            'completiontokens' => $bodyobj->usage->output_tokens ?? 0,
            'model' => $bodyobj->model ?? $this->get_model(),
        ];
    }
}
