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
    "WenQuest course standard (the benchmark is 大学物理 Chapter 1): each lesson runs "
    "real problem (a concrete ROBOTICS problem with real numbers that the lesson's model can solve, plus one "
    "everyday-life example) → concept → animation (3Blue1Brown style; you write its question and a storyboard "
    "of 5-8 beats, each beat one bilingual caption) → virtual lab (an interactive web lab with one robot scene and "
    "one everyday scene, adjustable parameters and 3 auto-checked tasks) → modelling in five steps: problem, "
    "model (assumptions), solution (numbers), check with the lab, where the model fails and how to improve it. "
    "All student-facing text is Chinese–English (课件中英对照): every text is a pair [中文, English], each "
    "written natively. Numbers, units and formulas must be correct; the answer to the robot problem must "
    "follow from the given data."
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
        "Design the outline. `problem` is the lesson's robotics problem in a few words (e.g. 'AGV emergency stop: "
        "will the cargo slide?'). `sections` lists textbook section numbers the lesson teaches (e.g. ['1.2','1.3'], "
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
    " Role: 主讲教授 (lecturer). Write ONE lesson as a lesson spec (JSON), to the level of the benchmark example "
    "you are given. The notes are the lecture text students read: 3-6 sections of real teaching (intuition, "
    "definitions, derivations, a worked example), HTML using p, ul, ol, li, strong, em, table, formulas as LaTeX in "
    "\\( \\) or \\[ \\]. When you use the teacher's sources, keep their notation and cite them inline like "
    "（参考：文件名 第12页）; never cite pages you were not given. " + STANDARD
)


def lesson_prompt(ctx: str, sources: str, notes: str, exemplar: str) -> str:
    return (f"{ctx}\n\nThe benchmark lesson (1.1 of 大学物理 Chapter 1) — match its structure, depth and quality, "
            f"but write about THIS lesson:\n{exemplar}\n"
            + (f"\nThe teacher / reviewer asked for these changes — follow them:\n{notes}\n" if notes else "")
            + f"\nTeacher's materials for this lesson (hints, may be empty):\n{sources}")


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
    " Role: 审稿人 (reviewer), independent of the author. Check the lesson spec against the WenQuest standard "
    "and against physics: (1) all five steps present and consistent — the stated answer must follow from the "
    "given data (recompute the numbers); (2) the robotics problem is realistic and solvable with this lesson's "
    "model; (3) formulas, units and numbers correct; (4) Chinese and English say the same thing; (5) the "
    "animation storyboard teaches the concept visually; (6) the lab tasks can be done and checked with the "
    "stated parameters; (7) citations only point to pages given. Verdict 'revise' only for real problems; "
    "list each concretely so the author can fix it. " + STANDARD
)


def review_schema() -> dict:
    issue = _obj({"severity": {"type": "string", "enum": ["high", "low"]}, "text": STR})
    return _obj({"verdict": {"type": "string", "enum": ["pass", "revise"]}, "issues": {"type": "array", "items": issue},
                 "summary": STR})


def review_prompt(ctx: str, spec_json: str, exercises: str, sources: str, missing: list[str]) -> str:
    return (f"{ctx}\n\nLesson spec to check:\n<<<\n{spec_json}\n>>>\n\nPractice questions and answers:\n<<<\n{exercises}\n>>>\n"
            + (f"\nThe automatic check already found: {'; '.join(missing)}\n" if missing else "")
            + f"\nTeacher's materials the author was given:\n{sources}")


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
  vec(start, end, color=C_V, label=r"\vec v", label_dir=UP)   vector arrow with LaTeX label
  readout(name, value_str, unit, color, size)                   MathTex like "v = 1.50 m/s"
Colours: C_V velocity (orange), C_A acceleration (red), C_F force, C_X / C_Y components, STEEL, YELLOW, GREY_B.
Math: MathTex(r"...") (LaTeX); Chinese only through zh()/caption(), never inside MathTex.
Motion: ValueTracker + always_redraw, TracedPath, MoveAlongPath, Axes(...).plot(...), GrowArrow, Transform.
"""

ANIMATOR = COMMON + (
    " Role: 动画师 (animator). Turn the lesson's animation storyboard into ONE Manim scene in the style of "
    "3Blue1Brown and of the WenQuest benchmark: every beat of the storyboard becomes a caption (Chinese and "
    "English, as given) plus real motion that shows the physics — computed from the actual formulas with "
    "ValueTracker/always_redraw, correct numbers and units, never just text on screen. Show the robot scene of the "
    "lesson (AGV, arm, conveyor, drone ...) and end with self.card(...) holding the key formulas. 40-90 seconds, "
    "at most about 25 self.play calls; simple shapes render fast. Return JSON {\"code\": \"...python...\"}.\n\n" + ANIM_API
)


def animation_schema() -> dict:
    return _obj({"code": STR})


def animation_prompt(no: str, spec_json: str, example: str, error: str = "", previous: str = "") -> str:
    out = (f"Lesson {no}. The lesson spec (use its animation title, question and beats, its concept and robot problem):\n"
           f"{spec_json}\n\nA complete example scene for lesson 2.1 in the house style — follow its structure:\n{example}\n")
    if error:
        out += (f"\nYour previous code failed. Fix it and return the whole corrected scene.\nError:\n{error}\n"
                f"\nPrevious code:\n{previous}\n")
    return out
