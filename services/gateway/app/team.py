"""The AI professor team (round 3, D30): roles, instructions and output formats.

Each role is one model call with its own job description and a strict JSON output, so the
orchestrator (studio.py) can check every answer before anything reaches the teacher.

  课程负责人 lead       talks with the teacher: questions, replies, records decisions
  资料馆员   librarian  says what every file is (main textbook, slides, answers ...) and reads the textbook's contents
  课程设计师 designer   outline and teaching calendar from the textbook contents and the teacher's hours
  主讲教授   author     writes one lesson to the course standard, from the textbook pages, citing them
  习题与测评 assessor   practice questions and an answer key for the lesson
  审稿人     reviewer   checks the lesson against the sources; sends it back when it is wrong
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

DESIGNER = COMMON + (
    " Role: 课程设计师 (course designer). Design the course outline and teaching calendar: chapters follow the "
    "main textbook's contents (use its chapter titles), each lesson is one class session with one clear goal, "
    "and every lesson names the textbook sections it teaches. Fit the teacher's weeks and sessions; leave "
    "room for review and exams when the calendar asks for it. Chapter and lesson titles are real topic names "
    "(e.g. '1.2 Units and Standards' or '1.2 单位与标准'), never numbers, formulas or answers."
)


def outline_schema(lang_keys: list[str]) -> dict:
    t = _obj({k: STR for k in lang_keys})
    lesson = _obj({"title": t, "goal": t, "week": INT, "sections": STRS}, ["title", "goal", "week", "sections"])
    chapter = _obj({"no": INT, "title": t, "summary": t, "lessons": {"type": "array", "items": lesson}},
                   ["no", "title", "summary", "lessons"])
    return _obj({"title": t, "summary": t, "chapters": {"type": "array", "items": chapter}, "calendar_note": STR},
                ["title", "summary", "chapters"])


def outline_prompt(project_summary: str, toc_text: str, extra: str, feedback: str = "") -> str:
    parts = [
        "Design the outline. `sections` lists the textbook section numbers each lesson teaches (e.g. ['1.2','1.3']). "
        "`week` is the teaching week of the lesson. Keep 2-6 lessons per chapter.",
        project_summary,
        "Main textbook contents:\n" + (toc_text or "(no single textbook; use the chapter materials below)"),
    ]
    if extra:
        parts.append(extra)
    if feedback:
        parts.append("Your previous outline was rejected by the quality check for these reasons; fix them:\n" + feedback)
    return "\n\n".join(parts)


# --- 主讲教授 author, 习题与测评 assessor, 审稿人 reviewer ------------------------------------------

STANDARD = (
    "Course standard for every science/engineering lesson (WenQuest): "
    "1) a real problem to open with — mainly from robotics, plus one everyday-life example; "
    "2) the concepts, built from intuition to formalism, with worked examples; "
    "3) an animation moment (describe what the animation shows, in 3Blue1Brown style; if the course has an "
    "animation video for this topic, point to it by name); "
    "4) a virtual-lab moment (what to try in the chapter's virtual lab, if there is one); "
    "5) modelling and solving the opening problem, and where the model fails; "
    "then a short summary and 2-3 check-your-understanding questions."
)

AUTHOR = COMMON + (
    " Role: 主讲教授 (lecturer). Write one lesson for students. Teach FROM the given source pages: keep their "
    "notation, definitions and numbers; explain and reorganise rather than invent. After each paragraph, "
    "example or formula taken from a source, cite it inline like （参考：University Physics Vol 1，第12页） or "
    "(Source: University Physics Vol 1, p. 12). Only cite pages you were given. " + STANDARD
)

HTML_RULES = ("HTML using only h3, h4, p, ul, ol, li, strong, em, code, pre, blockquote, table, tr, th, td. "
              "No h1/h2, no inline styles, no scripts, no images. Formulas as LaTeX between \\( \\) or \\[ \\].")


def lesson_schema(lang_keys: list[str]) -> dict:
    return _obj({"content": _obj({k: STR for k in lang_keys}), "summary": STR})


def lesson_prompt(ctx: str, sources: str, notes: str) -> str:
    return (f"{ctx}\n\nFormat: {HTML_RULES}\nLength: about 1200-2000 words (or 2000-3500 Chinese characters) per language.\n"
            + (f"\nThe teacher / reviewer asked for these changes — follow them:\n{notes}\n" if notes else "")
            + f"\nSources:\n{sources}")


ASSESSOR = COMMON + (
    " Role: 习题与测评 (assessment). Write 4-6 practice questions for the lesson (mix of concept checks and "
    "calculations, at least one about the opening robotics problem), in the style of the textbook's exercises, "
    "and a separate answer key with worked solutions. Base them on the lesson and its sources only."
)


def exercises_schema(lang_keys: list[str]) -> dict:
    return _obj({"questions": _obj({k: STR for k in lang_keys}), "answers": _obj({k: STR for k in lang_keys})})


REVIEWER = COMMON + (
    " Role: 审稿人 (reviewer), independent of the author. Check the lesson against the sources given: facts, "
    "formulas, numbers and units must agree with the sources; every citation must point to a page that was "
    "given and says that; nothing may be invented; the lesson must teach its stated goal and follow the "
    "course standard. Verdict 'revise' only for real problems (wrong physics, wrong numbers, invented "
    "citations, missing core content); list each problem concretely so the author can fix it."
)


def review_schema() -> dict:
    issue = _obj({"severity": {"type": "string", "enum": ["high", "low"]}, "text": STR})
    return _obj({"verdict": {"type": "string", "enum": ["pass", "revise"]}, "issues": {"type": "array", "items": issue},
                 "summary": STR})


def review_prompt(ctx: str, lesson_html: str, exercises: str, sources: str) -> str:
    return (f"{ctx}\n\nLesson to check:\n<<<\n{lesson_html}\n>>>\n\nPractice questions and answers:\n<<<\n{exercises}\n>>>\n"
            f"\nSources the author was given:\n{sources}")
