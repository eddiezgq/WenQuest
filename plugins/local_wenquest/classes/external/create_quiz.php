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
 * Create a quiz with its questions in one call (single / multiple choice, true-false, fill-in, numerical),
 * so teachers (and the AI question writer) build quizzes in WenQuest. With cmid set, the quiz's settings
 * are updated and its questions replaced (only while nobody has attempted it).
 *
 * @package    local_wenquest
 * @copyright  2026 Guoqing Zhang
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
class create_quiz extends external_api {
    /**
     * Parameters.
     *
     * @return external_function_parameters
     */
    public static function execute_parameters(): external_function_parameters {
        $answer = new external_single_structure([
            'text' => new external_value(PARAM_RAW, 'Answer (HTML for choices, plain for fill-in / numbers)'),
            'fraction' => new external_value(PARAM_FLOAT, 'Credit 0..1 (choices: 1 = correct)', VALUE_DEFAULT, 0),
            'feedback' => new external_value(PARAM_RAW, 'Feedback for this answer', VALUE_DEFAULT, ''),
            'tolerance' => new external_value(PARAM_FLOAT, 'Numerical: accepted error', VALUE_DEFAULT, 0),
        ]);
        $question = new external_single_structure([
            'type' => new external_value(PARAM_ALPHA, 'single, multiple, truefalse, shortanswer or numerical'),
            'name' => new external_value(PARAM_TEXT, 'Short name', VALUE_DEFAULT, ''),
            'text' => new external_value(PARAM_RAW, 'Question text (HTML, LaTeX allowed)'),
            'answers' => new external_multiple_structure($answer, 'Answers', VALUE_DEFAULT, []),
            'correct' => new external_value(PARAM_BOOL, 'True/false: the right answer', VALUE_DEFAULT, true),
            'feedback' => new external_value(PARAM_RAW, 'Explanation shown after answering', VALUE_DEFAULT, ''),
            'mark' => new external_value(PARAM_FLOAT, 'Marks for this question', VALUE_DEFAULT, 1),
        ]);
        return new external_function_parameters([
            'courseid' => new external_value(PARAM_INT, 'Course id'),
            'cmid' => new external_value(PARAM_INT, '0 = new quiz; otherwise the quiz to update', VALUE_DEFAULT, 0),
            'section' => new external_value(PARAM_INT, 'Section number for a new quiz', VALUE_DEFAULT, 0),
            'name' => new external_value(PARAM_TEXT, 'Quiz name'),
            'intro' => new external_value(PARAM_RAW, 'Instructions (HTML)', VALUE_DEFAULT, ''),
            'timeopen' => new external_value(PARAM_INT, 'Opens (0 = now)', VALUE_DEFAULT, 0),
            'timeclose' => new external_value(PARAM_INT, 'Closes (0 = never)', VALUE_DEFAULT, 0),
            'timelimit' => new external_value(PARAM_INT, 'Time limit in seconds (0 = none)', VALUE_DEFAULT, 0),
            'attempts' => new external_value(PARAM_INT, 'Attempts allowed (0 = unlimited)', VALUE_DEFAULT, 1),
            'grade' => new external_value(PARAM_FLOAT, 'Maximum grade', VALUE_DEFAULT, 100),
            'showanswers' => new external_value(PARAM_ALPHA, 'immediately, afterclose or never', VALUE_DEFAULT, 'immediately'),
            'visible' => new external_value(PARAM_INT, '1 = students see it', VALUE_DEFAULT, 1),
            'questions' => new external_multiple_structure($question, 'Questions', VALUE_DEFAULT, []),
        ]);
    }

    /**
     * Create or update the quiz.
     *
     * @param int $courseid
     * @param int $cmid
     * @param int $section
     * @param string $name
     * @param string $intro
     * @param int $timeopen
     * @param int $timeclose
     * @param int $timelimit
     * @param int $attempts
     * @param float $grade
     * @param string $showanswers
     * @param int $visible
     * @param array $questions
     * @return array
     */
    public static function execute(int $courseid, int $cmid, int $section, string $name, string $intro, int $timeopen,
            int $timeclose, int $timelimit, int $attempts, float $grade, string $showanswers, int $visible, array $questions): array {
        global $CFG, $DB;
        require_once($CFG->dirroot . '/course/lib.php');
        require_once($CFG->dirroot . '/course/modlib.php');
        require_once($CFG->dirroot . '/mod/quiz/lib.php');
        require_once($CFG->dirroot . '/mod/quiz/locallib.php');
        require_once($CFG->libdir . '/questionlib.php');

        $p = self::validate_parameters(self::execute_parameters(), [
            'courseid' => $courseid, 'cmid' => $cmid, 'section' => $section, 'name' => $name, 'intro' => $intro,
            'timeopen' => $timeopen, 'timeclose' => $timeclose, 'timelimit' => $timelimit, 'attempts' => $attempts,
            'grade' => $grade, 'showanswers' => $showanswers, 'visible' => $visible, 'questions' => $questions,
        ]);
        $course = get_course($p['courseid']);
        $context = \context_course::instance($course->id);
        self::validate_context($context);
        require_capability('moodle/course:manageactivities', $context);
        if (trim($p['name']) === '') {
            throw new \invalid_parameter_exception('quiz name is empty');
        }
        if (count($p['questions']) > 200) {
            throw new \invalid_parameter_exception('at most 200 questions');
        }

        $settings = self::settings($p);
        $transaction = $DB->start_delegated_transaction();
        if ($p['cmid']) {
            $cm = get_coursemodule_from_id('quiz', $p['cmid'], $course->id, false, MUST_EXIST);
            $quiz = $DB->get_record('quiz', ['id' => $cm->instance], '*', MUST_EXIST);
            $replacequestions = !empty($p['questions']);
            if ($replacequestions && $DB->record_exists('quiz_attempts', ['quiz' => $quiz->id, 'preview' => 0])) {
                throw new \moodle_exception('cannoteditafterattempts', 'quiz');
            }
            $data = (object) ($settings + [
                'coursemodule' => $cm->id, 'instance' => $quiz->id, 'modulename' => 'quiz', 'course' => $course->id,
                'section' => $cm->sectionnum, 'visible' => $p['visible'] ? 1 : 0, 'cmidnumber' => $cm->idnumber,
                'groupmode' => $cm->groupmode, 'groupingid' => $cm->groupingid,
            ]);
            update_module($data);
            if ($replacequestions) {
                $structure = \mod_quiz\quiz_settings::create($quiz->id)->get_structure();
                foreach ($structure->get_slots() as $slot) {
                    $structure->remove_slot($slot->slot);
                }
            }
        } else {
            course_create_sections_if_missing($course, [$p['section']]);
            $info = (object) ($settings + [
                'modulename' => 'quiz', 'course' => $course->id, 'section' => $p['section'],
                'visible' => $p['visible'] ? 1 : 0, 'visibleoncoursepage' => 1, 'cmidnumber' => '',
                'groupmode' => 0, 'groupingid' => 0, 'availability' => null, 'showdescription' => 0,
                'completion' => COMPLETION_TRACKING_AUTOMATIC, 'completionusegrade' => 1,
            ]);
            $created = create_module($info);
            $cm = get_coursemodule_from_id('quiz', $created->coursemodule, $course->id, false, MUST_EXIST);
            $quiz = $DB->get_record('quiz', ['id' => $cm->instance], '*', MUST_EXIST);
            $replacequestions = true;
        }

        $added = 0;
        if ($replacequestions) {
            $modcontext = \context_module::instance($cm->id);
            $category = question_get_default_category($modcontext->id, true);
            foreach ($p['questions'] as $i => $q) {
                $qid = self::save_question($q, $category, $i + 1);
                quiz_add_quiz_question($qid, $quiz, 0, max(0.1, (float) $q['mark']));
                $added++;
            }
            $settingsobj = \mod_quiz\quiz_settings::create($quiz->id);
            $settingsobj->get_grade_calculator()->recompute_quiz_sumgrades();
            quiz_repaginate_questions($quiz->id, 1);
        }
        $transaction->allow_commit();
        rebuild_course_cache($course->id, true);
        return ['cmid' => (int) $cm->id, 'quizid' => (int) $quiz->id, 'questions' => $added];
    }

    /**
     * Quiz settings in the form Moodle's quiz module expects.
     *
     * @param array $p
     * @return array
     */
    private static function settings(array $p): array {
        $show = $p['showanswers'];
        $s = [
            'name' => \core_text::substr(trim($p['name']), 0, 255),
            'introeditor' => ['text' => clean_text($p['intro'], FORMAT_HTML), 'format' => FORMAT_HTML, 'itemid' => 0],
            'timeopen' => max(0, $p['timeopen']), 'timeclose' => max(0, $p['timeclose']), 'timelimit' => max(0, $p['timelimit']),
            'overduehandling' => 'autosubmit', 'graceperiod' => 0, 'preferredbehaviour' => 'deferredfeedback',
            'canredoquestions' => 0, 'attempts' => max(0, $p['attempts']), 'attemptonlast' => 0,
            'grademethod' => QUIZ_GRADEHIGHEST, 'decimalpoints' => 2, 'questiondecimalpoints' => -1,
            'questionsperpage' => 1, 'navmethod' => QUIZ_NAVMETHOD_FREE, 'shuffleanswers' => 1,
            'grade' => max(1, $p['grade']), 'sumgrades' => 0, 'quizpassword' => '', 'subnet' => '', 'browsersecurity' => '-',
            'delay1' => 0, 'delay2' => 0, 'showuserpicture' => 0, 'showblocks' => 0, 'completionminattempts' => 0,
        ];
        // Scores are always shown after the attempt; answers and explanations as the teacher chose.
        $answers = ['immediately' => [1, 1, 1], 'afterclose' => [0, 0, 1], 'never' => [0, 0, 0]][$show] ?? [1, 1, 1];
        foreach (['immediately' => $answers[0], 'open' => $answers[1], 'closed' => $answers[2]] as $when => $on) {
            foreach (['attempt', 'marks', 'maxmarks', 'overallfeedback'] as $what) {
                $s[$what . $when] = 1;
            }
            foreach (['correctness', 'specificfeedback', 'generalfeedback', 'rightanswer'] as $what) {
                $s[$what . $when] = $on;
            }
        }
        foreach (['attempt', 'correctness', 'marks', 'maxmarks', 'specificfeedback', 'generalfeedback', 'rightanswer',
                  'overallfeedback'] as $what) {
            $s[$what . 'during'] = 0;
        }
        return $s;
    }

    /**
     * Save one question in the quiz's own question bank.
     *
     * @param array $q
     * @param \stdClass $category
     * @param int $no
     * @return int question id
     */
    private static function save_question(array $q, \stdClass $category, int $no): int {
        global $USER;
        $html = fn($t) => ['text' => clean_text((string) $t, FORMAT_HTML), 'format' => FORMAT_HTML];
        $type = $q['type'];
        $qtype = ['single' => 'multichoice', 'multiple' => 'multichoice', 'truefalse' => 'truefalse',
            'shortanswer' => 'shortanswer', 'numerical' => 'numerical'][$type] ?? null;
        if (!$qtype) {
            throw new \invalid_parameter_exception("question $no: unknown type $type");
        }
        $question = (object) ['category' => $category->id, 'qtype' => $qtype, 'createdby' => $USER->id, 'modifiedby' => $USER->id];
        $name = trim($q['name']) !== '' ? $q['name'] : \core_text::substr(trim(strip_tags($q['text'])), 0, 60);
        $form = (object) [
            'category' => $category->id . ',' . $category->contextid,
            'name' => $name !== '' ? $name : "Q$no",
            'questiontext' => $html($q['text']),
            'generalfeedback' => $html($q['feedback']),
            'defaultmark' => max(0.1, (float) $q['mark']),
            'penalty' => 0,
            'status' => \core_question\local\bank\question_version_status::QUESTION_STATUS_READY,
            'idnumber' => null,
        ];
        $answers = array_values(array_filter($q['answers'], fn($a) => trim((string) $a['text']) !== ''));
        switch ($type) {
            case 'single':
            case 'multiple':
                if (count($answers) < 2) {
                    throw new \invalid_parameter_exception("question $no: a choice question needs at least two options");
                }
                $right = array_values(array_filter($answers, fn($a) => $a['fraction'] > 0));
                if (!$right) {
                    throw new \invalid_parameter_exception("question $no: mark at least one option as correct");
                }
                $single = $type === 'single';
                $form->single = $single ? '1' : '0';
                $form->shuffleanswers = 1;
                $form->answernumbering = 'ABCD';
                $form->showstandardinstruction = 0;
                $form->shownumcorrect = 1;
                foreach (['correctfeedback', 'partiallycorrectfeedback', 'incorrectfeedback'] as $f) {
                    $form->$f = $html('');
                }
                $form->answer = $form->fraction = $form->feedback = [];
                foreach ($answers as $a) {
                    $form->answer[] = $html($a['text']);
                    if ($single) {
                        $form->fraction[] = $a['fraction'] > 0 ? '1.0' : '0.0';
                    } else {
                        $form->fraction[] = $a['fraction'] > 0 ? (string) round(1 / count($right), 7) : (string) round(-1 / count($right), 7);
                    }
                    $form->feedback[] = $html($a['feedback']);
                }
                break;
            case 'truefalse':
                $form->correctanswer = $q['correct'] ? '1' : '0';
                $form->feedbacktrue = $html('');
                $form->feedbackfalse = $html('');
                $form->showstandardinstruction = 0;
                $form->penalty = 1;
                break;
            case 'shortanswer':
                if (!$answers) {
                    throw new \invalid_parameter_exception("question $no: give at least one accepted answer");
                }
                $form->usecase = 0;
                $form->answer = $form->fraction = $form->feedback = [];
                foreach ($answers as $a) {
                    $form->answer[] = trim(strip_tags($a['text']));
                    $form->fraction[] = (string) ($a['fraction'] > 0 ? min(1, $a['fraction']) : 1);
                    $form->feedback[] = $html($a['feedback']);
                }
                break;
            case 'numerical':
                if (!$answers) {
                    throw new \invalid_parameter_exception("question $no: give the numerical answer");
                }
                $form->answer = $form->fraction = $form->feedback = $form->tolerance = [];
                foreach ($answers as $a) {
                    $form->answer[] = trim(strip_tags($a['text']));
                    $form->tolerance[] = abs((float) $a['tolerance']);
                    $form->fraction[] = (string) ($a['fraction'] > 0 ? min(1, $a['fraction']) : 1);
                    $form->feedback[] = $html($a['feedback']);
                }
                $form->unitrole = '3';
                $form->unitpenalty = 0;
                $form->unitgradingtypes = '1';
                $form->unitsleft = '0';
                $form->nounits = 1;
                $form->multiplier = ['1.0'];
                break;
        }
        $saved = \question_bank::get_qtype($qtype)->save_question($question, $form);
        return (int) $saved->id;
    }

    /**
     * Result structure.
     *
     * @return external_single_structure
     */
    public static function execute_returns(): external_single_structure {
        return new external_single_structure([
            'cmid' => new external_value(PARAM_INT, 'Course module id'),
            'quizid' => new external_value(PARAM_INT, 'Quiz id'),
            'questions' => new external_value(PARAM_INT, 'Questions added'),
        ]);
    }
}
