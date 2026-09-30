"""The AI professor team (round 3, D30): roles, instructions and output formats.

Each role is one model call with its own job description and a strict JSON output, so the
orchestrator (studio.py) can check every answer before anything reaches the teacher.

  课程负责人 lead       talks with the teacher: questions, replies, records decisions
  资料馆员   librarian  says what every file is (main textbook, slides, answers ...) and reads the textbook's contents
  课程设计师 designer   outline and teaching calendar from the textbook contents and the teacher's hours
  主讲教授   author     writes one lesson to the course standard, from the textbook pages, citing them
  习题与测评 assessor   practice questions and an answer key for the lesson
  审稿人     reviewer   checks the lesson against the sources; sends it back when it is wrong
  动画师     animator   turns the lesson's storyboard into a Manim scene (3Blue1Brown style), rendered on the server
"""
from __future__ import annotations

ROLES = {
    "main_textbook": "主教材",
    "aux_textbook": "辅助教材",
    "reference": "参考资料",
    "syllabus": "教学大纲",
    "calendar": "教学日历",
    "slides": "课件",
    "lesson_plan": "教案",
    "notes": "讲义",
    "homework": "习题/作业",
    "answer_key": "答案/题解",
    "exam": "试卷/测验",
    "lab": "实验",
    "rubric": "评分标准",
    "media": "视频/图片素材",
    "other": "无关/其他",
}
# Teacher-only when published (students never see them).
TEACHER_ONLY_ROLES = {"lesson_plan", "answer_key", "exam"}
# Attached to the chapter in the course (the textbooks themselves are not: size and copyright).
ATTACH_ROLES = {"slides", "notes", "homework", "lab", "media", "lesson_plan", "answer_key"}
# Course-information section.
INFO_ROLES = {"syllabus", "calendar", "rubric"}

COMMON = (
    "You are part of WenQuest's AI professor team, which builds university courses together with a real "
    "teacher. Be precise and honest: never invent facts, page numbers, sources or quotes; when something is "
    "unclear, say so or ask. The teacher decides; you propose. Write Chinese text in Simplified Chinese."
)

LANG_NAME = {"zh": "Simplified Chinese", "en": "English", "both": "both Simplified Chinese and English"}


def _obj(props: dict, required: list[str] | None = None) -> dict:
    return {"type": "object", "properties": props, "required": required if required is not None else list(props)}


STR = {"type": "string"}
INT = {"type": "integer"}
STRS = {"type": "array", "items": STR}
INTS = {"type": "array", "items": INT}
PAIR = {"type": "array", "items": STR, "minItems": 2, "maxItems": 2, "description": "[中文, English]"}
QUESTIONS = {"type": "array", "items": _obj({"text": STR, "options": STRS}, ["text"])}


# --- 资料馆员 librarian ------------------------------------------------------------------------

LIBRARIAN = COMMON + (
    " Role: 资料馆员 (librarian). You receive the teacher's course files: path, type, size, page count and the "
    "first text of each. Decide what each file IS for this course: main_textbook (the book the course follows; "
    "usually one, large, with a table of contents), aux_textbook (another textbook used alongside), reference "
    "(background reading), syllabus, calendar, rubric (grading standards), slides, lesson_plan, notes (lecture notes), homework "
    "(problem sets), answer_key (solutions, answers), exam (tests, quizzes), lab (lab guides, virtual labs, "
    "report templates), media (videos, pictures), other (unrelated). Also give the chapter numbers a file "
    "covers (empty for whole-course files), the document's own title, and its language. Mark confidence "
    "'low' when you are guessing. Ask the teacher only about what you really cannot tell from the files "
    "(at most 3 questions, with short answer options). Judge by content, not only by file name. "
    "Watch for two things and report them in the summary: (1) files that belong to DIFFERENT courses, levels "
    "or textbooks (e.g. university slides next to high-school slides): say which files form which set and ask "
    "which course to build; (2) a main textbook that the files refer to but that is not included (e.g. a "
    "download link): name the book and ask the teacher to upload it, or to confirm teaching from the slides "
    "and notes alone. Chapter numbers come from the content ('Chapter 7', 'Unit 05'), never from long numbers "
    "in file names."
)


def librarian_schema() -> dict:
    f = _obj({"id": STR, "role": {"type": "string", "enum": list(ROLES)}, "chapters": INTS, "title": STR,
              "language": {"type": "string", "enum": ["zh", "en", "mixed", "none"]},
              "confidence": {"type": "string", "enum": ["high", "low"]}, "note": STR},
             ["id", "role", "chapters", "title", "language", "confidence"])
    return _obj({
        "course": _obj({"title": STR, "subject": STR, "language": STR}),
        "main_textbook": STR,
        "files": {"type": "array", "items": f},
        "summary": STR,
        "questions": QUESTIONS,
    }, ["course", "main_textbook", "files", "summary", "questions"])


def librarian_prompt(files: list[dict], description: str) -> str:
    lines = [f"The teacher's description: {description or '(none)'}", "", "Files:"]
    for f in files:
        lines.append(f"\n### id={f['id']} | {f['path']} | {f['ext']} | {f['size'] // 1024} KB | "
                     f"{f['pages'] or '-'} pages{' | could not read: ' + f['error'] if f['error'] else ''}")
        if f.get("excerpt"):
            lines.append(f["excerpt"][:1200])
    lines.append("\nReturn main_textbook as the id of the main textbook, or an empty string if there is none.")
    return "\n".join(lines)


LIBRARIAN_UPDATE = COMMON + (
    " Role: 资料馆员 (librarian). The teacher has answered the team's questions. Update the materials list so "
    "it matches the answers: files that are not used for the course the teacher chose become 'other' (or "
    "'reference' when the teacher wants to keep them as background); a newly named main textbook becomes "
    "'main_textbook'; fix chapter numbers the answers make clear. Return only the files that change."
)


def update_schema() -> dict:
    f = _obj({"id": STR, "role": {"type": "string", "enum": list(ROLES)}, "chapters": INTS, "why": STR}, ["id", "role", "chapters"])
    return _obj({"files": {"type": "array", "items": f}, "note": STR}, ["files", "note"])


TOC = COMMON + (
    " Role: 资料馆员 reading a textbook's table of contents. From the contents pages given, list the chapters "
    "and their numbered sections exactly as printed (number, title, printed page). Skip front matter, "
    "appendices, answers and index. Do not invent sections that are not printed."
)


def toc_schema() -> dict:
    sec = _obj({"no": STR, "title": STR, "page": INT}, ["no", "title"])
    ch = _obj({"no": INT, "title": STR, "page": INT, "sections": {"type": "array", "items": sec}}, ["no", "title", "sections"])
    return _obj({"book_title": STR, "chapters": {"type": "array", "items": ch}})


# --- 课程负责人 lead ---------------------------------------------------------------------------

LEAD = COMMON + (
    " Role: 课程负责人 (course lead). You are the only team member who talks to the teacher. Speak like a "
    "respectful, efficient colleague: short, concrete, no flattery. Reply in the teacher's language."
)


def questions_schema() -> dict:
    req = _obj({"course_title": STR, "audience": STR, "weeks": INT, "sessions_per_week": INT,
                "minutes_per_session": INT, "language": STR}, [])
    return _obj({"message": STR, "questions": QUESTIONS, "known": req}, ["message", "questions", "known"])


def questions_prompt(project_summary: str, librarian_questions: list[dict]) -> str:
    return (
        "The librarian has just gone through the teacher's materials. Write the first report to the teacher:\n"
        "- message: 3-6 sentences: what the materials are (name the main textbook and what else there is), "
        "anything that could not be read and what to do about it, and what happens next.\n"
        "- questions: at most 5, only what the team needs and cannot find in the materials or the teacher's "
        "description. Typical: course title if unclear, students and level, number of weeks and class "
        "sessions per week (and minutes per session), teaching language (Chinese / English / bilingual), "
        "which chapters to cover, and the librarian's own open questions below. Give answer options where "
        "possible. Never ask what the syllabus or calendar already says.\n"
        "- known: requirements you found in the materials (e.g. from the syllabus/calendar); omit unknowns.\n\n"
        f"Librarian's open questions: {librarian_questions}\n\n{project_summary}"
    )


ACTIONS = {
    "answer_question": "{id, answer}: the teacher answered an open question",
    "set_requirement": "{key, value}: key is one of course_title, audience, level, language (zh|en|both), weeks, "
                       "sessions_per_week, minutes_per_session, scope, notes",
    "set_role": "{file_id, role}: the teacher says a file is something else",
    "set_textbook": "{file_id}: the teacher names the main textbook",
    "revise_lesson": "{lesson_id, note}: the teacher wants a lesson rewritten, note says how",
    "write_next": "{}: the teacher asks to write the next lesson now",
    "set_pace": "{mode: manual|daily, hour}: how lessons are written",
    "proceed": "{}: the teacher approves the current stage and wants to move on",
}


def chat_schema() -> dict:
    act = _obj({"type": {"type": "string", "enum": list(ACTIONS)}, "id": STR, "answer": STR, "key": STR,
                "value": STR, "file_id": STR, "role": STR, "lesson_id": STR, "note": STR, "mode": STR,
                "hour": INT}, ["type"])
    return _obj({"reply": STR, "actions": {"type": "array", "items": act}})


def chat_prompt(project_summary: str, history: list[dict], text: str) -> str:
    acts = "\n".join(f"- {k} {v}" for k, v in ACTIONS.items())
    hist = "\n".join(f"{m['role']}: {m['text'][:600]}" for m in history[-12:])
    return (
        "The teacher wrote to you. Answer in `reply` (short). When the teacher decides or tells you something the "
        "team must remember, also return actions (only these types):\n" + acts + "\n"
        "Do not claim that something has been done unless an action does it. If the teacher asks about the "
        "course, answer from the project state below.\n\n"
        f"{project_summary}\n\nRecent conversation:\n{hist}\n\nTeacher: {text}"
    )


# --- 课程设计师 designer -----------------------------------------------------------------------

# The WenQuest course standard (D31): every lesson is built like 大学物理 Chapter 1, the benchmark.
AI_FIRST = (
    " Use your full expert knowledge to design the BEST lesson, as a master teacher would; do not merely "
    "summarise the teacher's files. The teacher's materials (if any) tell you their textbook, order, notation "
    "and favourite examples: follow those, fix their mistakes, fill their gaps. With no materials you still "
    "build a complete lesson."
)
STANDARD = (
    "WenQuest course standard: each lesson runs "
    "real problem (a concrete ROBOTICS problem with real numbers that the lesson's model can solve, plus one "
    "everyday-life example) → concept → animation (3Blue1Brown style; you write its question and a storyboard "
    "of 5-8 beats, each beat one bilingual caption) → virtual lab (an interactive web lab with one robot scene and "
    "one everyday scene, adjustable parameters and 3 auto-checked tasks) → modelling in five steps: problem, "
    "model (assumptions), solution (numbers), check with the lab, where the model fails and how to improve it. "
    "All student-facing text is Chinese–English (课件中英对照): every text is a pair [中文, English], each "
    "written natively. Numbers, units and formulas must be correct; the answer to the robot problem must "
    "follow from the given data. Everything is about THIS course's subject and follows the course design book "
    "(its robot platform, notation and the chapter's animation and lab means); never borrow the topic, robot, "
    "scene or numbers of another course or of an example."
)

DESIGNER = COMMON + AI_FIRST + (
    " Role: 课程设计师 (course designer). Design the course outline and teaching calendar: chapters in a sound "
    "teaching order (follow the main textbook's contents when there is one), each lesson one class session with "
    "one clear goal and its own ROBOTICS problem, and every lesson names the textbook sections it teaches (if "
    "any). Fit the teacher's weeks and sessions; leave room for review and exams when the calendar asks for it. "
    "Chapter and lesson titles are real topic names, never numbers, formulas or answers. " + STANDARD
)


def outline_schema(lang_keys: list[str]) -> dict:
    t = _obj({k: STR for k in lang_keys})
    lesson = _obj({"title": t, "goal": t, "problem": t, "week": INT, "sections": STRS}, ["title", "goal", "problem", "week", "sections"])
    chapter = _obj({"no": INT, "title": t, "summary": t, "lessons": {"type": "array", "items": lesson}},
                   ["no", "title", "summary", "lessons"])
    return _obj({"title": t, "summary": t, "chapters": {"type": "array", "items": chapter}, "calendar_note": STR},
                ["title", "summary", "chapters"])


def outline_prompt(project_summary: str, toc_text: str, extra: str, feedback: str = "") -> str:
    parts = [
        "Design the outline. `problem` is the lesson's robotics problem in a few words, taken from THIS course's "
        "subject (for a robotics course e.g. 'where must joint 2 turn so the gripper reaches the part?'). `sections` lists textbook section numbers the lesson teaches (e.g. ['1.2','1.3'], "
        "empty if there is no textbook). `week` is the teaching week. Keep 2-6 lessons per chapter.",
        project_summary,
        "Main textbook contents:\n" + (toc_text or "(no single textbook: design the chapters yourself, using the materials below as hints)"),
    ]
    if extra:
        parts.append(extra)
    if feedback:
        parts.append("Your previous outline was rejected by the quality check for these reasons; fix them:\n" + feedback)
    return "\n\n".join(parts)


# --- 主讲教授 author, 课程设计师 guide & plan, 习题与测评 assessor, 审稿人 reviewer --------------------

AUTHOR = COMMON + AI_FIRST + (
    " Role: 主讲教授 (lecturer). Write ONE lesson as a lesson spec (JSON), to the depth the structure guide asks "
    "for, about THIS course's subject and following its design book. The notes are the lecture text students read: 3-6 sections of real teaching (intuition, "
    "definitions, derivations, a worked example), HTML using p, ul, ol, li, strong, em, table, formulas as LaTeX in "
    "\\( \\) or \\[ \\]. When you use the teacher's sources, keep their notation and cite them inline like "
    "（参考：文件名 第12页）; never cite pages you were not given. " + STANDARD
)


def lesson_prompt(ctx: str, sources: str, notes: str, guide: str, previous: str = "") -> str:
    return (f"{ctx}\n\nWhat each part of the lesson spec must contain (structure and depth only — the content is yours, "
            f"about THIS lesson):\n{guide}\n"
            + (f"\nThe previous lesson of this course, for continuity of notation, robot platform and level "
               f"(do not repeat its problem or examples):\n{previous}\n" if previous else "")
            + (f"\nThe teacher / reviewer asked for these changes — follow them:\n{notes}\n" if notes else "")
            + f"\nTeacher's materials for this lesson (hints, may be empty):\n{sources}")


# --- 课程设计书 course design book ----------------------------------------------------------------------

DESIGN_BOOK = COMMON + (
    " Role: 课程设计师 (course designer). Before any lesson is written, write the course design book that every "
    "member of the team follows, so the whole course is about its own subject and hangs together: the subject "
    "and level; the main textbook and how it is used; ONE robot platform (or two) that runs through the whole "
    "course and fits the subject (e.g. for a robotics course a 6-axis arm and a differential-drive mobile robot; "
    "for circuits the robot's motor drive board), described concretely with its key parameters; notation and "
    "terms consistent with the textbook; the visual style of the animations for this subject; and for every "
    "chapter the means its animations and virtual labs will use (what is drawn, what the student adjusts, what "
    "is measured) and the theme of its robot problems. List what the team must avoid (e.g. examples from other "
    "subjects). The teacher's requirements are binding. Chinese, concise. From the 问渠零件与机器人库 listing "
    "you are given, choose the entries the course will use throughout (its robot platform first, then typical "
    "parts and mechanisms) — `library`: their ids exactly as listed and the role of each; describe the platform "
    "with those entries' real parameters. Never invent ids."
)


def design_book_schema() -> dict:
    ch = _obj({"no": INT, "animation": STR, "lab": STR, "problems": STR})
    lib = _obj({"id": STR, "role": STR})
    return _obj({"subject": STR, "audience": STR, "textbook": STR, "platform": STR, "notation": STR,
                 "visual_style": STR, "chapters": {"type": "array", "items": ch}, "avoid": STRS,
                 "library": {"type": "array", "items": lib}})


def design_book_prompt(project_summary: str, outline: str, requirements: str, catalog: str = "") -> str:
    return (f"{project_summary}\n\nThe teacher's requirements (binding):\n{requirements}\n\n"
            f"The approved outline:\n{outline}\n\n"
            + (f"问渠零件与机器人库 (id | name | category | tags | principle):\n{catalog}\n\n" if catalog else "")
            + "Write the course design book.")


def design_book_text(b: dict | None) -> str:
    """The design book as the team reads it in every prompt."""
    if not b:
        return ""
    lines = [f"Subject and level: {b.get('subject', '')}; students: {b.get('audience', '')}",
             f"Textbook: {b.get('textbook', '')}", f"Robot platform used throughout: {b.get('platform', '')}",
             f"Notation: {b.get('notation', '')}", f"Animation style: {b.get('visual_style', '')}"]
    for c in b.get("chapters") or []:
        lines.append(f"Chapter {c.get('no')}: animations — {c.get('animation', '')}; labs — {c.get('lab', '')}; "
                     f"robot problems — {c.get('problems', '')}")
    if b.get("library"):
        lines.append("Library entries used throughout (问渠零件与机器人库): "
                     + "; ".join(f"{x['id']} ({x.get('role', '')})" for x in b["library"]))
    if b.get("avoid"):
        lines.append("Avoid: " + "; ".join(b["avoid"]))
    return "\n".join(x for x in lines if x.split(":", 1)[-1].strip(" ;—"))


GUIDE_PLAN = COMMON + (
    " Role: 课程设计师 (course designer). From the lesson spec, write (1) the lab guide for its virtual lab, in the "
    "benchmark's layout: objectives, principles (formulas), the lab's parameters and ranges, numbered steps that "
    "use the lab's robot scene and everyday scene, 1-2 data tables students fill in (headers and first column "
    "given, measured cells empty), cautions, 2 thinking questions, and the robot problem as a 3-part question; "
    "(2) the lesson plan (教案, Chinese): three objectives, key and difficult points, the class process in timed "
    "phases (导入/新课/动画/实验/建模/小结, about 90 minutes), board layout and homework. Bilingual pairs are "
    "[中文, English]."
)

ASSESSOR = COMMON + (
    " Role: 习题与测评 (assessment). Write 4-6 practice questions for the lesson (concept checks and "
    "calculations, at least one about the lesson's robotics problem with new numbers), and a separate answer key "
    "with worked solutions. Chinese and English, as HTML (ol/li, p; formulas in \\( \\))."
)


def exercises_schema(lang_keys: list[str]) -> dict:
    return _obj({"questions": _obj({k: STR for k in lang_keys}), "answers": _obj({k: STR for k in lang_keys})})


REVIEWER = COMMON + (
    " Role: 审稿人 (reviewer), independent of the author. Check the lesson spec against the WenQuest standard, "
    "the course design book and the subject: (0) it is about THIS course and lesson — a topic, robot or example "
    "taken from another subject is a 'high' issue; (1) all five steps present and consistent — the stated answer must follow from the "
    "given data (recompute the numbers); (2) the robotics problem is realistic and solvable with this lesson's "
    "model; (3) formulas, units and numbers correct; (4) Chinese and English say the same thing; (5) the "
    "animation storyboard teaches the concept visually; (6) the lab tasks can be done and checked with the "
    "stated parameters; (7) citations only point to pages given. Verdict 'revise' only for real problems; "
    "list each concretely so the author can fix it. " + STANDARD
)


def review_schema() -> dict:
    issue = _obj({"severity": {"type": "string", "enum": ["high", "low"]}, "text": STR})
    item = _obj({"ok": {"type": "boolean"}, "note": STR})
    checks = _obj({"textbook": item, "problem": item, "numbers": item, "bilingual": item})
    return _obj({"verdict": {"type": "string", "enum": ["pass", "revise"]}, "issues": {"type": "array", "items": issue},
                 "summary": STR, "checks": checks})


REVIEW_CHECKS = ("\n\nAlso fill `checks`, one line each, true only when you verified it: textbook — the lesson follows "
                 "the textbook pages it was given (false when none were given or it ignores them); problem — the robot "
                 "problem is THIS lesson's and uses the course's robot/platform; numbers — every number, unit and final "
                 "answer is recomputed and right; bilingual — Chinese and English say the same thing.")


def review_prompt(ctx: str, spec_json: str, exercises: str, sources: str, missing: list[str]) -> str:
    return REVIEW_CHECKS.strip() + "\n\n" + (f"{ctx}\n\nLesson spec to check:\n<<<\n{spec_json}\n>>>\n\nPractice questions and answers:\n<<<\n{exercises}\n>>>\n"
            + (f"\nThe automatic check already found: {'; '.join(missing)}\n" if missing else "")
            + f"\nTeacher's materials the author was given:\n{sources}")


# --- 切题检查 relevance check (team rebuild R3) --------------------------------------------------------

RELEVANCE = COMMON + (
    " Role: 审稿人 (reviewer), relevance check. You see what the student will see of one lesson's animation or "
    "virtual lab: its key pictures (when given), its titles, captions and task texts. Decide whether it teaches THIS "
    "lesson: its concept and its robot problem, on the robot or platform the course design book names, in THIS "
    "course's subject. It is off topic when it shows another subject or course (e.g. a physics AGV/crate example in "
    "a robotics kinematics lesson), another lesson's content, placeholder text, or pictures that do not match the "
    "captions. Small style issues do not matter. Return JSON {\"on_topic\": true/false, \"reason\": \"one sentence\", "
    "\"fix\": \"what to change (when off topic)\"}."
)


def relevance_schema() -> dict:
    return _obj({"on_topic": {"type": "boolean"}, "reason": STR, "fix": STR})


def relevance_prompt(what: str, course: str, lesson: str, texts: list[str]) -> str:
    return (f"{course}\n\nThis lesson:\n{lesson}\n\nThe {what} to check — its texts:\n"
            + "\n".join(f"- {t}" for t in texts[:40]) + "\n\nIs it on topic for THIS lesson?")


# --- 插图师 illustrator (round 4) --------------------------------------------------------------------------

ILLUSTRATOR = COMMON + (
    " Role: 插图师 (illustrator). Draw ONE figure for THIS lesson exactly as the lecturer asked (`purpose`), for "
    "lecture notes and slides: clear, uncluttered, textbook quality, every label correct and in the course's language "
    "setting. Use the course's robot platform from the design book. Never invent statistics or data: a chart uses only "
    "the numbers given in `data` or values you compute from the lesson's own formulas. Return JSON as asked."
)

FIG_GRAPH = r"""Return {"graph": {...}} for a block diagram / flow / classification tree / course map:
{"direction": "LR" | "TB",
 "nodes": [{"id": "a", "label": ["中文", "English"], "shape": "round|box|diamond|circle|note|cylinder",
            "group": "optional group id", "group_label": ["组名", "Group name"], "emphasis": false, "color": 0}],
 "edges": [{"from": "a", "to": "b", "label": ["可选", "optional"], "dashed": false}]}
4-18 nodes; short labels (≤ 12 Chinese characters); emphasis marks 1-2 key nodes; groups put related nodes in a frame."""

FIG_CHART = r"""Return {"chart": {...}} for a plot of real numbers:
{"type": "line" | "bar" | "scatter", "x_label": ["中文（单位）", "English (unit)"], "y_label": [..],
 "series": [{"name": ["中文", "English"], "x": [numbers], "y": [numbers]}],
 "categories": [["类别", "category"], ...] (bar charts only), "lines": [{"y": number, "label": ["限值", "limit"]}]}
Compute the numbers from the lesson's formulas or take them from `data`; 10-200 points for curves."""

FIG_SCENE = r"""Return {"code": "...python..."}: ONE still picture drawn with the WenQuest Manim parts (the same API as the
animations, listed below). `class Lesson(Base):` with `def construct(self):` that only ADDS mobjects (self.add(...);
no self.play, no waiting, no self.title/self.caption/self.card — the caption is under the figure). Fill the frame
(x in [-6.8, 6.8], y in [-3.6, 3.6]); dark background; labels with zh()/en()/bi() or MathTex; label sizes 22-30.
"""


def figure_schema(kind: str) -> dict:
    if kind == "graph":
        node = _obj({"id": STR, "label": PAIR, "shape": STR, "group": STR, "group_label": PAIR, "emphasis": {"type": "boolean"},
                     "color": INT}, ["id", "label"])
        edge = _obj({"from": STR, "to": STR, "label": PAIR, "dashed": {"type": "boolean"}}, ["from", "to"])
        return _obj({"graph": _obj({"direction": STR, "nodes": {"type": "array", "items": node},
                                    "edges": {"type": "array", "items": edge}}, ["nodes", "edges"])})
    if kind == "chart":
        num = {"type": "array", "items": {"type": "number"}}
        ser = _obj({"name": PAIR, "x": num, "y": num}, ["y"])
        return _obj({"chart": _obj({"type": STR, "x_label": PAIR, "y_label": PAIR, "series": {"type": "array", "items": ser},
                                    "categories": {"type": "array", "items": PAIR},
                                    "lines": {"type": "array", "items": _obj({"y": {"type": "number"}, "label": PAIR}, ["y"])}},
                                   ["type", "series"])})
    return _obj({"code": STR})


def figure_prompt(no: str, fig: dict, spec_json: str, lang: str, course: str, error: str = "", previous: str = "") -> str:
    how = {"graph": FIG_GRAPH, "chart": FIG_CHART, "scene": FIG_SCENE + "\n" + ANIM_API}[fig["kind"]]
    lang_rule = {"zh": "Chinese only", "en": "English only", "both": "Chinese and English (labels as [中文, English] pairs)"}.get(lang, "Chinese and English")
    out = (f"{course}\n\nLesson {no}. Figure: {fig['title'][0]} / {fig['title'][1]}\nPurpose (what it must show): "
           f"{fig['purpose'][0]} / {fig['purpose'][1]}\n" + (f"Data: {fig['data']}\n" if fig.get("data") else "")
           + f"Labels: {lang_rule}.\n\nThe lesson spec:\n{spec_json}\n\n{how}")
    if error:
        out += f"\n\nYour previous figure was not accepted. Fix it.\nProblem:\n{error}\n" + (f"\nPrevious:\n{previous}\n" if previous else "")
    return out


# --- 动画师 animator ----------------------------------------------------------------------------------

ANIM_API = r"""Write Python for Manim Community v0.19+ with the WenQuest parts. Start with `from wq_anim import *`
(it brings in everything from manim, plus numpy as np). Define exactly one scene: `class Lesson(Base):` with
`def construct(self):`. Allowed imports: wq_anim, manim, numpy, math, random. No files, images, SVGs, sounds,
os/sys, getattr/eval/exec, or names/attributes starting with an underscore (the code is checked and rejected).

Frame: 14.2 x 8 units, centre (0,0); the title takes the top-left corner (y > 2.6), captions the bottom (y < -2.6).
Keep drawings inside x in [-6.8, 6.8], y in [-2.5, 2.5]. Background is dark (#0f1419); use light colours.

Parts from wq_anim:
  self.title(no, zh, en)                 title at the top-left (call once, first)
  self.caption(zh, en, wait=1.5)         bilingual caption at the bottom; replaces the previous one
  self.clear_stage()                     fade out everything except title and caption
  self.card(lines, wait=2.5)             closing summary card; lines: [zh, en] pairs or MathTex objects
  zh(text, size=30, color=WHITE, weight=NORMAL), en(text, size=20), bi([zh, en], size=28)   text
  fit(mobject, width=12.5)               shrink if too wide
  ground(y=-2.2, x0=-7, x1=7)            floor with hatching
  agv(width=2.6, height=0.7, label="")   warehouse AGV (bottom at its own y=0; place with .move_to(p, aligned_edge=DOWN))
  cargo(size=0.8, label="")              a box
  conveyor(length=6)                     belt conveyor
  arm(base, a1, a2, l1=2.2, l2=1.6)      two-link robot arm, angles in degrees; arm_tip(...) gives the gripper point
  drone(width=1.8)                       quadcopter, side view
  (robotics) rot_x(deg), rot_y(deg), rot_z(deg)  3x3 rotation matrices (numpy; combine with @)
  proj3(p, origin=ORIGIN, scale=1.0)     a 3D point on screen (oblique view, z up)
  frame2(origin, angle=0, length=1.2, labels=("x","y"), name=r"\{A\}")   2D coordinate frame
  frame3(origin, R, length=1.2, scale=1.0, name=r"\{B\}")   3D frame for rotation matrix R (x red, y green, z blue)
  planar_fk(base, angles, lengths)       joint points of a planar n-link arm (relative angles, degrees)
  planar_arm(base, angles, lengths, joint_labels=[r"\theta_1", ...])   planar n-link arm drawing
  mobile_robot(pos, heading=0, size=0.9) differential-drive robot seen from above
  lidar(center, angles_deg, ranges)      laser rays with hit points
  matrix_tex(M, digits=2)                numeric matrix as LaTeX
  vec(start, end, color=C_V, label=r"\vec v", label_dir=UP)   vector arrow with LaTeX label
  readout(name, value_str, unit, color, size)                   MathTex like "v = 1.50 m/s"
Colours: C_V velocity (orange), C_A acceleration (red), C_F force, C_X / C_Y components, STEEL, YELLOW, GREY_B.
Math: MathTex(r"...") (LaTeX); Chinese only through zh()/caption(), never inside MathTex.
Motion: ValueTracker + always_redraw, TracedPath, MoveAlongPath, Axes(...).plot(...), GrowArrow, Transform.
"""

ANIMATOR = COMMON + (
    " Role: 动画师 (animator). Turn the lesson's animation storyboard into ONE Manim scene in the style of "
    "3Blue1Brown and of the WenQuest benchmark: every beat of the storyboard becomes a caption (Chinese and "
    "English, as given) plus real motion that shows THIS lesson's idea — computed from the lesson's actual formulas "
    "with ValueTracker/always_redraw, correct numbers and units, never just text on screen. Draw the robot or "
    "platform the course design book names for this course (use the parts that fit it; never pick a robot the course "
    "does not use) and end with self.card(...) holding the key formulas. The example you are given shows technique "
    "only: its content is a placeholder and must never appear in your scene. 40-90 seconds, "
    "at most about 25 self.play calls; simple shapes render fast. Return JSON {\"code\": \"...python...\"}.\n\n" + ANIM_API
)


def animation_schema() -> dict:
    return _obj({"code": STR})


def animation_prompt(no: str, spec_json: str, example: str, error: str = "", previous: str = "", course: str = "") -> str:
    out = (f"{course}\n\n" if course else "") + (
        f"Lesson {no}. The lesson spec (use its animation title, question and beats, its concept and robot problem):\n"
        f"{spec_json}\n\nTECHNIQUE example (house style: structure, ValueTracker, readouts, captions, closing card). "
        f"Its content is a placeholder — copy the technique, never its shapes, numbers or text:\n{example}\n")
    if error:
        out += (f"\nYour previous code failed. Fix it and return the whole corrected scene.\nError:\n{error}\n"
                f"\nPrevious code:\n{previous}\n")
    return out


# --- 实验师 lab engineer (A3) --------------------------------------------------------------------------

LAB_API = r"""Write ONE virtual lab as plain JavaScript that calls WQ.lab({...}) exactly once. The WenQuest lab kit
already draws the page (tabs, EN/中文, scene buttons, sliders, measurement panel, task list, progress, canvas
and animation loop); you only give the physics and the pictures. Every text is a pair ["中文", "English"].

WQ.lab({
  title: [zh, en],                       // short, e.g. ["惯性与急停", "Inertia and emergency stops"]
  goal: [zh, en],                        // one sentence: what the student should see
  scenes: [                              // exactly two: the robot scene first, then the everyday scene
    { id: "robot", robot: true, name: [zh, en], problem: { title: [zh, en], text: [zh, en] } },
    { id: "life", name: [zh, en], problem: {...}, hide: ["paramId"], params: { paramId: { min, max, step, value } } },
  ],                                     // hide/params: per-scene slider changes (optional)
  params: [ { id, name: [zh, en], min, max, step, value, unit: "m/s", digits: 1 } ],   // 2-5 sliders
  buttons: [ { id: "start", name: [zh, en], primary: true }, { id: "reset", name: [zh, en] } ],  // optional;
                                         // "start" and "reset" are built in; other ids call action(id, api, state)
  legend: [ { color: "var(--orange)", name: [zh, en] } ],                              // optional
  tasks: [                               // 3 tasks; each ticked by your code with api.done(id)
    { id: "slide", robot: true, text: [zh, en],
      demo: { scene: "robot", set: { paramId: value, ... }, press: ["start"], wait: 3 } },
  ],                                     // demo = how to complete it; the checker does exactly this and
                                         // waits `wait` seconds of lab time, then the task MUST be ticked
  think: [zh, en],                       // a question to think about (optional)
  reset(api, state) { ... },             // set up `state` (a plain object) from api.p; called on load,
                                         // scene change, slider change while stopped, and "reset"
  start(api, state) { ... },             // optional, after "start" (the kit calls reset first, then sets running)
  update(dt, api, state) { ... },        // physics step, called only while api.running; dt in seconds
  readouts(api, state) { return [[ [zh, en], "1.50 m/s" ], ...]; },   // measurement rows
  draw(api, state) { ... },              // draw the current picture (the canvas is cleared for you)
});

api: api.w, api.h (canvas size in px, 16:10), api.ctx (CanvasRenderingContext2D), api.p (slider values by id),
api.scene (scene id), api.t (seconds since start), api.running, api.stop() (end the run; call it when the motion
is over), api.done(taskId), api.T(zh, en) and api.P([zh, en]) (text in the current language), api.fmt(x, digits),
api.css("--ink") colours: --ink --muted --accent --amber --blue --green --red --orange --violet --ground --grid
--water --water-line --panel. Drawing helpers: api.line(x1,y1,x2,y2,color,width,dash), api.arrow(x1,y1,x2,y2,color,
width), api.label(text,x,y,color,size,align), api.rect(x,y,w,h,fill,stroke,radius), api.circle(x,y,r,fill,stroke),
api.ground(y, width, scroll, step), api.grid(w, h, step), api.agv(x, yBottom, width, color), api.box(x, yBottom, size, color).
Robotics helpers (angles in degrees, counter-clockwise on screen): api.rot2(deg) (2x2 matrix), api.fk(x, y, angles, lengths)
(joint points of a planar arm, angles relative), api.arm(x, y, angles, lengths, color, width) (draws it, returns the points),
api.frame(x, y, deg, len, ["x","y"], "{B}") (coordinate frame), api.robot(x, y, headingDeg, size, color) (mobile robot from
above), api.lidar(x, y, anglesDeg, rangesPx, color), api.plot(x, y, w, h, [{pts: [[x, y], ...], color}], {xmin, xmax, ymin,
ymax, xlabel, ylabel}) (a small chart; returns {X, Y} to map values to pixels).
Scale with api.w/api.h (never fixed pixel sizes); y grows downwards; keep a margin of 12 px.

Rules (checked automatically; the lab is rejected otherwise): no fetch/XMLHttpRequest/WebSocket, no import,
no eval/Function, no localStorage/cookies, no location/window.open/parent/top/postMessage, no innerHTML or
document.write, no web addresses, no setTimeout/setInterval/requestAnimationFrame (the kit runs the loop), and
never call other WQ functions. Put helper functions and constants above or below the WQ.lab call.
"""

LAB_ENGINEER = COMMON + (
    " Role: 实验师 (lab engineer). Build the lesson's virtual lab from the lesson spec: its robot scene and everyday "
    "scene, its adjustable parameters and its tasks. The model must be real and correct (compute it from THIS "
    "lesson's formulas with correct units), the picture must show what the student has to notice (vectors, frames, "
    "readings, paths, curves), and each task must be checkable by your code and reachable with its demo. The robot "
    "scene shows the robot or platform the course design book names for this course. The example you are given "
    "shows technique only: its content is a placeholder and must never appear in your lab. Return JSON {\"code\": \"...javascript...\"}.\n\n" + LAB_API
)


def lab_schema() -> dict:
    return _obj({"code": STR})


def lab_prompt(no: str, spec_json: str, example: str, problems: list[str] | None = None, previous: str = "",
               course: str = "") -> str:
    out = (f"{course}\n\n" if course else "") + (
        f"Lesson {no}. The lesson spec (use its lab title, scenes, params and tasks, its concept, formulas and robot problem):\n"
        f"{spec_json}\n\nTECHNIQUE example (structure only; its content is a placeholder — never copy its topic, "
        f"texts or numbers):\n{example}\n")
    if problems:
        out += ("\nYour previous lab failed the automatic check. Fix every problem and return the whole corrected code.\n"
                "Problems:\n" + "\n".join(f"- {p}" for p in problems[:15]) + f"\n\nPrevious code:\n{previous}\n")
    return out
