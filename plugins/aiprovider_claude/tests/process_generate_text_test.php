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

use core_ai\aiactions\base;
use core_ai\provider;
use GuzzleHttp\Psr7\Response;

defined('MOODLE_INTERNAL') || die();
require_once(__DIR__ . '/testcase_helper_trait.php');

/**
 * Tests for the Claude text processors.
 *
 * @package    aiprovider_claude
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 *
 * @covers     \aiprovider_claude\provider
 * @covers     \aiprovider_claude\process_generate_text
 * @covers     \aiprovider_claude\process_summarise_text
 * @covers     \aiprovider_claude\process_explain_text
 * @covers     \aiprovider_claude\abstract_processor
 */
final class process_generate_text_test extends \advanced_testcase {
    use testcase_helper_trait;

    /** @var string A successful response in JSON format. */
    protected string $responsebodyjson;

    /** @var provider The provider that will process the action. */
    protected provider $provider;

    /** @var base The action to process. */
    protected base $action;

    #[\Override]
    protected function setUp(): void {
        parent::setUp();
        $this->resetAfterTest();
        $this->responsebodyjson = file_get_contents(self::get_fixture_path('aiprovider_claude', 'text_request_success.json'));
        $this->provider = $this->create_provider(
            actionclass: \core_ai\aiactions\generate_text::class,
            actionconfig: ['systeminstruction' => 'You are a helpful teaching assistant.'],
        );
        $this->action = new \core_ai\aiactions\generate_text(contextid: 1, userid: 1, prompttext: 'What is a stack?');
    }

    /**
     * Build the request body for a processor.
     *
     * @param process_generate_text $processor
     * @return \stdClass
     */
    private function request_body(process_generate_text $processor): \stdClass {
        $method = new \ReflectionMethod($processor, 'create_request_object');
        $request = $method->invoke($processor, 'anon-user');
        return json_decode($request->getBody()->getContents());
    }

    public function test_create_request_object_uses_messages_api_shape(): void {
        $body = $this->request_body(new process_generate_text($this->provider, $this->action));

        $this->assertEquals('claude-sonnet-5', $body->model);
        $this->assertEquals('You are a helpful teaching assistant.', $body->system);
        $this->assertCount(1, $body->messages);
        $this->assertEquals('user', $body->messages[0]->role);
        $this->assertEquals('What is a stack?', $body->messages[0]->content);
        $this->assertEquals(helper::DEFAULT_MAX_TOKENS, $body->max_tokens);
        $this->assertEquals('anon-user', $body->metadata->user_id);
        $this->assertObjectNotHasProperty('user', $body);
    }

    public function test_create_request_object_with_model_settings(): void {
        $provider = $this->create_provider(
            actionclass: \core_ai\aiactions\generate_text::class,
            actionconfig: ['temperature' => '0.2', 'max_tokens' => '800'],
        );
        $body = $this->request_body(new process_generate_text($provider, $this->action));
        $this->assertSame(0.2, $body->temperature);
        $this->assertSame(800, $body->max_tokens);

        $provider = $this->create_provider(
            actionclass: \core_ai\aiactions\generate_text::class,
            actionconfig: ['model' => 'claude-custom', 'modelextraparams' => '{"temperature": 0.5, "max_tokens": 100}'],
        );
        $body = $this->request_body(new process_generate_text($provider, $this->action));
        $this->assertEquals('claude-custom', $body->model);
        $this->assertSame(0.5, $body->temperature);
        $this->assertSame(100, $body->max_tokens);
    }

    public function test_authentication_headers(): void {
        $request = new \GuzzleHttp\Psr7\Request('POST', '');
        $request = $this->provider->add_authentication_headers($request);
        $this->assertEquals('123', $request->getHeaderLine('x-api-key'));
        $this->assertEquals(helper::API_VERSION, $request->getHeaderLine('anthropic-version'));
        $this->assertFalse($request->hasHeader('Authorization'));
    }

    public function test_handle_api_success(): void {
        $processor = new process_generate_text($this->provider, $this->action);
        $method = new \ReflectionMethod($processor, 'handle_api_success');
        $result = $method->invoke($processor, new Response(200, ['Content-Type' => 'application/json'], $this->responsebodyjson));

        $this->assertTrue($result['success']);
        $this->assertEquals('msg_01XFDUDYJgAACzvnptvVoYEL', $result['id']);
        $this->assertStringContainsString('后进先出', $result['generatedcontent']);
        $this->assertEquals('end_turn', $result['finishreason']);
        $this->assertEquals(23, $result['prompttokens']);
        $this->assertEquals(41, $result['completiontokens']);
        $this->assertEquals('claude-sonnet-5', $result['model']);
    }

    public function test_handle_api_success_joins_text_blocks(): void {
        $json = json_encode([
            'id' => 'msg_2', 'model' => 'claude-sonnet-5', 'stop_reason' => 'max_tokens',
            'content' => [['type' => 'text', 'text' => 'Part one. '], ['type' => 'text', 'text' => 'Part two.']],
            'usage' => ['input_tokens' => 5, 'output_tokens' => 6],
        ]);
        $processor = new process_generate_text($this->provider, $this->action);
        $method = new \ReflectionMethod($processor, 'handle_api_success');
        $result = $method->invoke($processor, new Response(200, [], $json));
        $this->assertEquals('Part one. Part two.', $result['generatedcontent']);
        $this->assertEquals('max_tokens', $result['finishreason']);
    }

    public function test_handle_api_error(): void {
        $processor = new process_generate_text($this->provider, $this->action);
        $method = new \ReflectionMethod($processor, 'handle_api_error');

        $result = $method->invoke($processor, new Response(401, [],
            '{"type":"error","error":{"type":"authentication_error","message":"invalid x-api-key"}}'));
        $this->assertEquals(401, $result['errorcode']);
        $this->assertStringContainsString('invalid x-api-key', $result['errormessage']);

        $result = $method->invoke($processor, new Response(529));
        $this->assertEquals(529, $result['errorcode']);
    }

    public function test_process_success_and_error(): void {
        $this->provider = $this->create_provider(
            actionclass: \core_ai\aiactions\generate_text::class,
            ratelimited: false,
        );
        $this->setUser($this->getDataGenerator()->create_user());
        ['mock' => $mock] = $this->get_mocked_http_client();

        $mock->append(new Response(200, ['Content-Type' => 'application/json'], $this->responsebodyjson));
        $result = (new process_generate_text($this->provider, $this->action))->process();
        $this->assertTrue($result->get_success());
        $this->assertStringContainsString('后进先出', $result->get_response_data()['generatedcontent']);

        $this->setUser($this->getDataGenerator()->create_user());
        $mock->append(new Response(401, [], '{"type":"error","error":{"type":"authentication_error","message":"invalid x-api-key"}}'));
        $result = (new process_generate_text($this->provider, $this->action))->process();
        $this->assertFalse($result->get_success());
        $this->assertEquals(401, $result->get_errorcode());
    }

    public function test_summarise_and_explain_process(): void {
        $this->setUser($this->getDataGenerator()->create_user());
        ['mock' => $mock] = $this->get_mocked_http_client();

        $provider = $this->create_provider(actionclass: \core_ai\aiactions\summarise_text::class, ratelimited: false);
        $action = new \core_ai\aiactions\summarise_text(contextid: 1, userid: 1, prompttext: 'Long course text');
        $mock->append(new Response(200, [], $this->responsebodyjson));
        $result = (new process_summarise_text($provider, $action))->process();
        $this->assertTrue($result->get_success());
        $this->assertEquals('summarise_text', $result->get_actionname());

        $this->setUser($this->getDataGenerator()->create_user());
        $provider = $this->create_provider(actionclass: \core_ai\aiactions\explain_text::class, ratelimited: false);
        $action = new \core_ai\aiactions\explain_text(contextid: 1, userid: 1, prompttext: 'Recursion');
        $mock->append(new Response(200, [], $this->responsebodyjson));
        $result = (new process_explain_text($provider, $action))->process();
        $this->assertTrue($result->get_success());
        $this->assertEquals('explain_text', $result->get_actionname());
    }

    public function test_model_classes(): void {
        $names = array_map(fn($c) => (new $c())->get_model_name(), helper::get_model_classes());
        sort($names);
        $this->assertEquals(['claude-haiku-4-5-20251001', 'claude-opus-5-5', 'claude-sonnet-5'], $names);
        $this->assertNotNull(helper::get_model_class(helper::DEFAULT_MODEL));
    }
}
