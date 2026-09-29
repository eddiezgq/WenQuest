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
use mod_quiz\question\display_options;

/**
 * A quiz's settings and questions in the same shape create_quiz takes, so teachers can edit it in WenQuest.
 *
 * @package    local_wenquest
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
class get_quiz extends external_api {
    /**
     * Parameters.
     *
     * @return external_function_parameters
     */
    public static function execute_parameters(): external_function_parameters {
        return new external_function_parameters(['cmid' => new external_value(PARAM_INT, 'Quiz course module')]);
    }

    /**
     * Read the quiz.
     *
     * @param int $cmid
     * @return array
     */
    public static function execute(int $cmid): array {
        global $CFG, $DB;
        require_once($CFG->libdir . '/questionlib.php');
        $p = self::validate_parameters(self::execute_parameters(), ['cmid' => $cmid]);
        $cm = get_coursemodule_from_id('quiz', $p['cmid'], 0, false, MUST_EXIST);
        $context = \context_module::instance($cm->id);
        self::validate_context($context);
        require_capability('mod/quiz:manage', $context);
        $quiz = $DB->get_record('quiz', ['id' => $cm->instance], '*', MUST_EXIST);

        $right = (int) $quiz->reviewrightanswer;
        $show = ($right & display_options::IMMEDIATELY_AFTER) ? 'immediately' : (($right & display_options::AFTER_CLOSE) ? 'afterclose' : 'never');
        $questions = [];
        $unsupported = 0;
        foreach (\mod_quiz\question\bank\qbank_helper::get_question_structure($quiz->id, $context) as $slot) {
            if (empty($slot->questionid)) {
                $unsupported++;
                continue;
            }
            $q = \question_bank::load_question_data($slot->questionid);
            $item = ['type' => '', 'name' => $q->name, 'text' => $q->questiontext, 'answers' => [], 'correct' => true,
                'feedback' => (string) $q->generalfeedback, 'mark' => (float) $slot->maxmark];
            $answers = array_values((array) ($q->options->answers ?? []));
            switch ($q->qtype) {
                case 'multichoice':
                    $item['type'] = $q->options->single ? 'single' : 'multiple';
                    foreach ($answers as $a) {
                        $item['answers'][] = ['text' => $a->answer, 'fraction' => $a->fraction > 0 ? 1 : 0,
                            'feedback' => (string) $a->feedback, 'tolerance' => 0];
                    }
                    break;
                case 'truefalse':
                    $item['type'] = 'truefalse';
                    $true = $q->options->answers[$q->options->trueanswer] ?? null;
                    $item['correct'] = $true && $true->fraction > 0.5;
                    break;
                case 'shortanswer':
                case 'numerical':
                    $item['type'] = $q->qtype;
                    foreach ($answers as $a) {
                        if ($a->answer === '*') {
                            continue;
                        }
                        $item['answers'][] = ['text' => $a->answer, 'fraction' => (float) $a->fraction,
                            'feedback' => (string) $a->feedback, 'tolerance' => (float) ($a->tolerance ?? 0)];
                    }
                    break;
                default:
                    $unsupported++;
                    continue 2;
            }
            $questions[] = $item;
        }
        return [
            'cmid' => (int) $cm->id, 'section' => (int) $DB->get_field('course_sections', 'section', ['id' => $cm->section]),
            'name' => $quiz->name, 'intro' => (string) $quiz->intro, 'timeopen' => (int) $quiz->timeopen,
            'timeclose' => (int) $quiz->timeclose, 'timelimit' => (int) $quiz->timelimit, 'attempts' => (int) $quiz->attempts,
            'grade' => (float) $quiz->grade, 'showanswers' => $show, 'visible' => (int) $cm->visible,
            'hasattempts' => $DB->record_exists('quiz_attempts', ['quiz' => $quiz->id, 'preview' => 0]),
            'unsupported' => $unsupported, 'questions' => $questions,
        ];
    }

    /**
     * Result structure.
     *
     * @return external_single_structure
     */
    public static function execute_returns(): external_single_structure {
        $answer = new external_single_structure([
            'text' => new external_value(PARAM_RAW, 'Answer'),
            'fraction' => new external_value(PARAM_FLOAT, 'Credit'),
            'feedback' => new external_value(PARAM_RAW, 'Feedback'),
            'tolerance' => new external_value(PARAM_FLOAT, 'Numerical tolerance'),
        ]);
        return new external_single_structure([
            'cmid' => new external_value(PARAM_INT, 'Course module'),
            'section' => new external_value(PARAM_INT, 'Section number'),
            'name' => new external_value(PARAM_TEXT, 'Name'),
            'intro' => new external_value(PARAM_RAW, 'Instructions'),
            'timeopen' => new external_value(PARAM_INT, 'Opens'),
            'timeclose' => new external_value(PARAM_INT, 'Closes'),
            'timelimit' => new external_value(PARAM_INT, 'Seconds'),
            'attempts' => new external_value(PARAM_INT, 'Attempts allowed'),
            'grade' => new external_value(PARAM_FLOAT, 'Maximum grade'),
            'showanswers' => new external_value(PARAM_ALPHA, 'immediately, afterclose or never'),
            'visible' => new external_value(PARAM_INT, 'Visible to students'),
            'hasattempts' => new external_value(PARAM_BOOL, 'Students have attempted it (questions locked)'),
            'unsupported' => new external_value(PARAM_INT, 'Questions of types WenQuest does not edit'),
            'questions' => new external_multiple_structure(new external_single_structure([
                'type' => new external_value(PARAM_ALPHA, 'single, multiple, truefalse, shortanswer or numerical'),
                'name' => new external_value(PARAM_TEXT, 'Name'),
                'text' => new external_value(PARAM_RAW, 'Question text'),
                'answers' => new external_multiple_structure($answer),
                'correct' => new external_value(PARAM_BOOL, 'True/false answer'),
                'feedback' => new external_value(PARAM_RAW, 'Explanation'),
                'mark' => new external_value(PARAM_FLOAT, 'Marks'),
            ])),
        ]);
    }
}
