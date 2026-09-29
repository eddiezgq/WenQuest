"""Teachers edit their course in WenQuest (round 3, D32 / step B3): course settings, chapters, content,
assignments and quizzes (including AI-written quiz questions). Registered by main.create_app().

Bilingual text (Moodle multilang markup) is edited as {zh, en}; single-language text as {text}.
"""

import html as htmllib
import json
import re
from typing import Annotated, Any

from fastapi import Depends, File, Form, UploadFile
from pydantic import BaseModel, Field

from . import course_builder as cb
from . import materials as mt
from .moodle import EngineError
from .session import Session

MAX_FILE = 190 * 1024 * 1024


class Bi(BaseModel):
    """Text as edited: one language (`text`) or both (`zh`, `en`)."""
    text: str | None = Field(default=None, max_length=200000)
    zh: str | None = Field(default=None, max_length=200000)
    en: str | None = Field(default=None, max_length=200000)


class SettingsIn(BaseModel):
    name: Bi | None = None
    summary: Bi | None = None
    visible: bool | None = None


class SectionIn(BaseModel):
    name: Bi | None = None
    summary: Bi | None = None
    visible: bool | None = None
    position: int | None = Field(default=None, ge=0, le=200)


class ModuleIn(BaseModel):
    name: Bi | None = None
    visible: bool | None = None


class MoveIn(BaseModel):
    section: int | None = None      # target section id (modules)
    before: int = 0                 # put before this activity (0 = at the end)
    position: int | None = None     # target section number (sections)


class ContentIn(BaseModel):
    name: Bi | None = None
    content: Bi | None = None
    intro: Bi | None = None
    url: str | None = Field(default=None, max_length=2000)
    duedate: int | None = Field(default=None, ge=0)
    cutoffdate: int | None = Field(default=None, ge=0)
    grade: float | None = Field(default=None, gt=0, le=10000)
    allowtext: bool | None = None
    allowfiles: bool | None = None
    maxfiles: int | None = Field(default=None, ge=1, le=20)


class NewActivity(ContentIn):
    type: str = Field(pattern="^(page|url|assign|forum)$")
    visible: bool = True


class QAnswer(BaseModel):
    text: str = Field(max_length=5000)
    fraction: float = 0
    feedback: str = Field(default="", max_length=5000)
    tolerance: float = 0


class QuestionIn(BaseModel):
    type: str = Field(pattern="^(single|multiple|truefalse|shortanswer|numerical)$")
    name: str = Field(default="", max_length=255)
    text: str = Field(min_length=1, max_length=20000)
    answers: list[QAnswer] = Field(default_factory=list, max_length=20)
    correct: bool = True
    feedback: str = Field(default="", max_length=20000)
    mark: float = Field(default=1, gt=0, le=100)


class QuizIn(BaseModel):
    cmid: int = 0
    section: int = Field(default=0, ge=0, le=200)
    name: str = Field(min_length=1, max_length=255)
    intro: str = Field(default="", max_length=20000)
    timeopen: int = 0
    timeclose: int = 0
    timelimit: int = Field(default=0, ge=0, le=86400)
    attempts: int = Field(default=1, ge=0, le=100)
    grade: float = Field(default=100, gt=0, le=10000)
    showanswers: str = Field(default="immediately", pattern="^(immediately|afterclose|never)$")
    visible: bool = True
    questions: list[QuestionIn] = Field(default_factory=list, max_length=200)
    keep_questions: bool = False    # update settings only


class AiAssignIn(BaseModel):
    section: int = Field(ge=0, le=200)
    note: str = Field(default="", max_length=1000)


class AiQuizIn(BaseModel):
    section: int = Field(ge=0, le=200)
    count: int = Field(default=8, ge=1, le=30)
    types: list[str] = Field(default_factory=lambda: ["single", "multiple", "truefalse", "shortanswer", "numerical"])
    note: str = Field(default="", max_length=1000)


QUIZ_WRITER = (
    "You are the assessment writer of a WenQuest university course. Write quiz questions for the given lesson "
    "material: test understanding and problem solving (concepts, reasoning, calculations with units), not "
    "trivia. Include at least one question about a robotics application when the material has one. Every "
    "question needs a short explanation. Types: single (exactly one correct option, 4 options), multiple (2-3 "
    "correct of 4-5), truefalse (set correct), shortanswer (1-3 accepted answers, a word or short phrase; put "
    "the blank in the text as ______), numerical (one numeric answer with a sensible tolerance; state units and "
    "g in the text). Options must be plausible. Formulas in LaTeX within \\( \\). Write in Chinese unless the "
    "material is in English; keep the teacher's notation."
)


ASSIGN_WRITER = (
    "You are the lead lecturer of a WenQuest university course. Set one homework assignment for the given chapter, "
    "the way a strong professor would: 3-6 problems that go from checking the concepts to real problem solving, "
    "at least one based on a robotics application (AGV, robot arm, drone, conveyor ...) and, when it fits, one "
    "everyday-life problem. Give all data and units needed; ask for derivations, not just answers. Then the "
    "submission requirements and a grading rubric (criteria with points adding up to the maximum grade). Also "
    "write a complete answer key with worked solutions for the teacher. HTML (p, ol, li, strong, table); formulas "
    "in LaTeX within \\( \\) or \\[ \\]. Write in Chinese unless the material is in English; keep the "
    "teacher's notation. Follow the teacher's request when given."
)


def assign_schema() -> dict:
    return {"type": "object", "additionalProperties": False,
            "required": ["name", "problems", "requirements", "rubric", "answers", "grade", "days"],
            "properties": {"name": {"type": "string"}, "problems": {"type": "string"}, "requirements": {"type": "string"},
                           "rubric": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                      "required": ["criterion", "points"],
                                      "properties": {"criterion": {"type": "string"}, "points": {"type": "number"}}}},
                           "answers": {"type": "string"}, "grade": {"type": "number"}, "days": {"type": "integer"}}}


def fake_assignment(title: str) -> dict:
    return {"name": f"{title} 作业", "grade": 100, "days": 7,
            "problems": "<ol><li><p>AGV 以 1.5 m/s 行驶，0.5 s 内匀减速停下。求减速度；货箱与车板间静摩擦因数 0.3，判断货箱是否滑动。</p></li>"
                        "<li><p>质量 2.0 kg 的木块放在倾角 30° 的斜面上，动摩擦因数 0.20，求下滑加速度（g 取 9.8 m/s²）。</p></li>"
                        "<li><p>生活中的例子：公交车急刹时乘客为什么向前倾？用牛顿第一定律解释。</p></li></ol>",
            "requirements": "<p>写出所用的物理规律和推导步骤，结果带单位；手写拍照或 Word 均可。</p>",
            "rubric": [{"criterion": "物理规律与受力分析正确", "points": 40}, {"criterion": "推导与计算正确、单位规范", "points": 40},
                       {"criterion": "应用题建模合理、结论清楚", "points": 20}],
            "answers": "<ol><li><p>\\(a=1.5/0.5=3.0\\) m/s² &gt; \\(\\mu g=2.94\\) m/s²，会滑动。</p></li>"
                       "<li><p>\\(a=g(\\sin30^\\circ-0.2\\cos30^\\circ)\\approx 3.2\\) m/s²。</p></li><li><p>惯性。</p></li></ol>"}


def quiz_schema() -> dict:
    ans = {"type": "object", "additionalProperties": False, "required": ["text", "fraction", "feedback", "tolerance"],
           "properties": {"text": {"type": "string"}, "fraction": {"type": "number"}, "feedback": {"type": "string"},
                          "tolerance": {"type": "number"}}}
    q = {"type": "object", "additionalProperties": False,
         "required": ["type", "text", "answers", "correct", "feedback", "mark"],
         "properties": {"type": {"type": "string", "enum": ["single", "multiple", "truefalse", "shortanswer", "numerical"]},
                        "text": {"type": "string"}, "answers": {"type": "array", "items": ans}, "correct": {"type": "boolean"},
                        "feedback": {"type": "string"}, "mark": {"type": "number"}}}
    return {"type": "object", "additionalProperties": False, "required": ["questions"],
            "properties": {"questions": {"type": "array", "items": q}}}


def fake_questions(title: str, n: int) -> list[dict]:
    base = [
        {"type": "single", "text": f"<p>关于“{title}”，下列说法正确的是：</p>", "correct": True, "mark": 1,
         "feedback": "回到本节的核心概念。", "answers": [{"text": "在惯性系中，合力为零时物体保持匀速直线运动或静止", "fraction": 1, "feedback": "", "tolerance": 0},
                                                         {"text": "运动需要力来维持", "fraction": 0, "feedback": "这是亚里士多德的观点", "tolerance": 0},
                                                         {"text": "质量越大的物体惯性越小", "fraction": 0, "feedback": "", "tolerance": 0},
                                                         {"text": "加速的车厢是惯性系", "fraction": 0, "feedback": "", "tolerance": 0}]},
        {"type": "truefalse", "text": "<p>刹车时货箱向前滑，是因为受到了向前的力。</p>", "correct": False, "mark": 1,
         "feedback": "货箱保持原来的运动（惯性），并没有向前的力。", "answers": []},
        {"type": "numerical", "text": "<p>AGV 在 0.5 s 内从 1.5 m/s 匀减速到停下，减速度大小是多少 m/s²？</p>", "correct": True, "mark": 2,
         "feedback": "\\(a=\\Delta v/\\Delta t=1.5/0.5=3.0\\) m/s²", "answers": [{"text": "3", "fraction": 1, "feedback": "", "tolerance": 0.05}]},
        {"type": "shortanswer", "text": "<p>物体保持原有运动状态的性质叫做 ______。</p>", "correct": True, "mark": 1,
         "feedback": "惯性。", "answers": [{"text": "惯性", "fraction": 1, "feedback": "", "tolerance": 0}]},
        {"type": "multiple", "text": "<p>下列参考系中，可以近似看作惯性系的是：</p>", "correct": True, "mark": 1, "feedback": "匀速或静止（相对地面）的参考系。",
         "answers": [{"text": "静止的实验室", "fraction": 1, "feedback": "", "tolerance": 0}, {"text": "匀速直线行驶的列车", "fraction": 1, "feedback": "", "tolerance": 0},
                     {"text": "正在刹车的汽车", "fraction": 0, "feedback": "", "tolerance": 0}, {"text": "转弯中的 AGV", "fraction": 0, "feedback": "", "tolerance": 0}]},
    ]
    return [base[i % len(base)] for i in range(n)]


def check_questions(qs: list[dict]) -> list[dict]:
    """Keep only questions that can be saved: choices need 2+ options and a right one; fill-ins an answer."""
    out = []
    for q in qs:
        t = q.get("type")
        answers = [a for a in q.get("answers") or [] if str(a.get("text") or "").strip()]
        if t in ("single", "multiple"):
            right = [a for a in answers if (a.get("fraction") or 0) > 0]
            if len(answers) < 2 or not right or (t == "single" and len(right) != 1):
                continue
        elif t in ("shortanswer", "numerical"):
            if not answers:
                continue
            if t == "numerical":
                try:
                    float(str(answers[0]["text"]).replace(",", "."))
                except ValueError:
                    continue
        elif t != "truefalse":
            continue
        q["answers"] = answers
        q["mark"] = max(0.5, min(10.0, float(q.get("mark") or 1)))
        out.append(q)
    return out


def register(app, m) -> None:
    current = m.current
    state = m.state

    async def call(sess: Session, fn: str, lang: str | None = None, **params: Any) -> Any:
        return await state.moodle.call(sess.moodle_token, fn, lang, **params)

    async def need_teacher(sess: Session, courseid: int) -> None:
        if not await state.moodle.can_edit_course(sess.moodle_token, courseid):
            raise EngineError("forbidden", "only the course's teachers edit it", 403)

    def split(raw: str | None, html: bool = False) -> dict:
        raw = raw or ""
        if "multilang" in raw or "{mlang" in raw:
            zh, en = m.resolve(raw, "zh"), m.resolve(raw, "en")
            if zh != en:
                return {"zh": zh, "en": en}
        return {"text": raw}

    def join(b: Bi | None, html: bool = False) -> str | None:
        if b is None:
            return None
        if b.zh is not None or b.en is not None:
            zh, en = (b.zh or "").strip(), (b.en or "").strip()
            if zh and en:
                return cb.ml(cb.Text(zh=zh, en=en), "both", html)
            return zh or en
        return (b.text or "").strip()

    async def edit(sess: Session, courseid: int, action: str, **params: Any) -> dict:
        clean = {k: (1 if v is True else 0 if v is False else v) for k, v in params.items() if v is not None}
        return await call(sess, "local_wenquest_edit_course", None, courseid=courseid, action=action, **clean)

    # --- structure ----------------------------------------------------------------------------------

    @app.get("/api/v1/courses/{courseid}/structure")
    async def structure(courseid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        await need_teacher(sess, courseid)
        lg = m.lang_of(lang, sess)
        c = await state.moodle.course(sess.moodle_token, courseid, None)
        secs = await state.moodle.course_contents(sess.moodle_token, courseid, None)
        sections = []
        for s in secs:
            mods = []
            for mod in s.get("modules") or []:
                if mod.get("modname") == "label":
                    continue
                f = next((x for x in mod.get("contents") or [] if x.get("type") == "file"), None)
                mods.append({"cmid": mod["id"], "type": mod.get("modname"), "name": split(mod.get("name")),
                             "title": m.plain(mod.get("name"), lg), "visible": bool(mod.get("visible", 1)),
                             "file": {"name": f.get("filename"), "kind": m.content.file_kind(f.get("filename"), f.get("mimetype"))} if f else None})
            sections.append({"id": s["id"], "number": s.get("section"), "name": split(s.get("name")),
                             "title": m.plain(s.get("name"), lg) or (f"#{s.get('section')}"),
                             "summary": split(s.get("summary"), True), "visible": bool(s.get("visible", 1)), "modules": mods})
        return {"course": {"id": courseid, "name": split((c or {}).get("fullname")), "summary": split((c or {}).get("summary"), True),
                           "visible": bool((c or {}).get("visible", 1))}, "sections": sections}

    @app.put("/api/v1/courses/{courseid}/settings")
    async def settings(courseid: int, body: SettingsIn, sess: Annotated[Session, Depends(current)]):
        await edit(sess, courseid, "course", name=join(body.name), summary=join(body.summary, True), visible=body.visible)
        return {"ok": True}

    @app.post("/api/v1/courses/{courseid}/sections")
    async def add_section(courseid: int, body: SectionIn, sess: Annotated[Session, Depends(current)]):
        r = await edit(sess, courseid, "addsection", name=join(body.name), summary=join(body.summary, True), position=body.position or 0)
        return {"id": r.get("sectionid")}

    @app.put("/api/v1/courses/{courseid}/sections/{sid}")
    async def edit_section(courseid: int, sid: int, body: SectionIn, sess: Annotated[Session, Depends(current)]):
        await edit(sess, courseid, "section", sectionid=sid, name=join(body.name), summary=join(body.summary, True), visible=body.visible)
        return {"ok": True}

    @app.post("/api/v1/courses/{courseid}/sections/{sid}/move")
    async def move_section(courseid: int, sid: int, body: MoveIn, sess: Annotated[Session, Depends(current)]):
        if not body.position:
            raise EngineError("bad_position", "a target position is required", 400)
        await edit(sess, courseid, "movesection", sectionid=sid, position=body.position)
        return {"ok": True}

    @app.delete("/api/v1/courses/{courseid}/sections/{sid}")
    async def delete_section(courseid: int, sid: int, sess: Annotated[Session, Depends(current)], force: bool = False):
        await edit(sess, courseid, "deletesection", sectionid=sid, force=force)
        return {"ok": True}

    @app.put("/api/v1/courses/{courseid}/modules/{cmid}")
    async def edit_module(courseid: int, cmid: int, body: ModuleIn, sess: Annotated[Session, Depends(current)]):
        await edit(sess, courseid, "module", cmid=cmid, name=join(body.name), visible=body.visible)
        return {"ok": True}

    @app.post("/api/v1/courses/{courseid}/modules/{cmid}/move")
    async def move_module(courseid: int, cmid: int, body: MoveIn, sess: Annotated[Session, Depends(current)]):
        if not body.section:
            raise EngineError("bad_position", "a target section is required", 400)
        await edit(sess, courseid, "movemodule", cmid=cmid, sectionid=body.section, beforecmid=body.before or 0)
        return {"ok": True}

    @app.delete("/api/v1/courses/{courseid}/modules/{cmid}")
    async def delete_module(courseid: int, cmid: int, sess: Annotated[Session, Depends(current)]):
        await edit(sess, courseid, "deletemodule", cmid=cmid)
        return {"ok": True}

    # --- content of one activity --------------------------------------------------------------------

    @app.get("/api/v1/courses/{courseid}/modules/{cmid}/content")
    async def content(courseid: int, cmid: int, sess: Annotated[Session, Depends(current)]):
        await need_teacher(sess, courseid)
        tok = sess.moodle_token
        cm = await state.moodle.course_module(tok, cmid)
        kind, inst = cm["modname"], int(cm["instance"])
        out: dict[str, Any] = {"cmid": cmid, "type": kind, "name": split(cm.get("name")), "visible": bool(cm.get("visible", 1))}
        if kind == "page":
            p = next((x for x in await state.moodle.pages(tok, courseid, None) if x["id"] == inst), {})
            out["content"] = split(p.get("content"), True)
        elif kind == "url":
            u = next((x for x in await state.moodle.urls(tok, courseid, None) if x["id"] == inst), {})
            out.update(url=u.get("externalurl") or "", intro=split(u.get("intro"), True))
        elif kind == "assign":
            a = next((x for x in await state.moodle.assignments(tok, courseid, None) if x["cmid"] == cmid), {})
            cfg = {(c.get("plugin"), c.get("name")): c.get("value") for c in a.get("configs") or [] if c.get("subtype") == "assignsubmission"}
            out.update(intro=split(a.get("intro"), True), duedate=a.get("duedate") or 0, cutoffdate=a.get("cutoffdate") or 0,
                       grade=a.get("grade") or 100, allowtext=cfg.get(("onlinetext", "enabled")) == "1",
                       allowfiles=cfg.get(("file", "enabled")) == "1", maxfiles=int(cfg.get(("file", "maxfilesubmissions")) or 5))
        elif kind == "forum":
            f = next((x for x in await call(sess, "mod_forum_get_forums_by_courses", None, courseids=[courseid]) if x.get("cmid") == cmid), {})
            out["intro"] = split(f.get("intro"), True)
        elif kind == "quiz":
            out["quiz"] = await call(sess, "local_wenquest_get_quiz", None, cmid=cmid)
        return out

    @app.put("/api/v1/courses/{courseid}/modules/{cmid}/content")
    async def save_content(courseid: int, cmid: int, body: ContentIn, sess: Annotated[Session, Depends(current)]):
        url = body.url.strip() if body.url else None
        if url is not None and url and not re.match(r"^https?://", url):
            url = "https://" + url
        await edit(sess, courseid, "content", cmid=cmid, name=join(body.name), content=join(body.content, True),
                   intro=join(body.intro, True), url=url, duedate=body.duedate, cutoffdate=body.cutoffdate, grade=body.grade,
                   allowtext=body.allowtext, allowfiles=body.allowfiles, maxfiles=body.maxfiles)
        return {"ok": True}

    @app.post("/api/v1/courses/{courseid}/sections/{number}/activities")
    async def add_activity(courseid: int, number: int, body: NewActivity, sess: Annotated[Session, Depends(current)]):
        name = join(body.name) or ""
        if not name:
            raise EngineError("name_required", "a name is required", 400)
        act: dict[str, Any] = {"type": body.type, "name": name, "visible": 1 if body.visible else 0,
                               "intro": join(body.intro, True) or "", "content": join(body.content, True) or ""}
        if body.type == "url":
            u = (body.url or "").strip()
            if not u:
                raise EngineError("url_required", "a link is required", 400)
            act["url"] = u if re.match(r"^https?://", u) else "https://" + u
        if body.type == "assign":
            act["duedate"] = body.duedate or 0
            act["grade"] = body.grade or 100
        r = await call(sess, "local_wenquest_add_activities", None, courseid=courseid, section=number, activities=[act])
        cmid = (r.get("cmids") or [0])[0]
        if body.type == "assign" and cmid and (body.allowtext is not None or body.allowfiles is not None or body.maxfiles):
            await edit(sess, courseid, "content", cmid=cmid, allowtext=body.allowtext, allowfiles=body.allowfiles,
                       maxfiles=body.maxfiles, cutoffdate=body.cutoffdate)
        return {"cmid": cmid}

    @app.post("/api/v1/courses/{courseid}/sections/{number}/files")
    async def add_file(courseid: int, number: int, sess: Annotated[Session, Depends(current)],
                       file: Annotated[UploadFile, File()], name: Annotated[str, Form()] = "", visible: Annotated[bool, Form()] = True):
        data = await file.read()
        if len(data) > MAX_FILE:
            raise EngineError("file_too_large", file.filename or "file", 413)
        fname = mt.fix_name(file.filename or "file")
        draft = await state.moodle.upload(sess.moodle_token, fname, data)
        title = name.strip() or fname.rsplit(".", 1)[0]
        r = await call(sess, "local_wenquest_add_activities", None, courseid=courseid, section=number,
                       activities=[{"type": "resource", "name": title, "draftitemid": draft, "visible": 1 if visible else 0}])
        return {"cmid": (r.get("cmids") or [0])[0]}

    # --- quizzes ------------------------------------------------------------------------------------

    @app.post("/api/v1/courses/{courseid}/quizzes")
    async def save_quiz(courseid: int, body: QuizIn, sess: Annotated[Session, Depends(current)]):
        qs = [] if body.keep_questions else [q.model_dump() for q in body.questions]
        for i, q in enumerate(qs):
            if q["type"] in ("single", "multiple"):
                right = [a for a in q["answers"] if a["fraction"] > 0 and a["text"].strip()]
                if len([a for a in q["answers"] if a["text"].strip()]) < 2 or not right or (q["type"] == "single" and len(right) != 1):
                    raise EngineError("question_invalid", str(i + 1), 400)
            elif q["type"] in ("shortanswer", "numerical") and not any(a["text"].strip() for a in q["answers"]):
                raise EngineError("question_invalid", str(i + 1), 400)
        if not body.cmid and not qs:
            raise EngineError("no_questions", "a quiz needs questions", 400)
        r = await call(sess, "local_wenquest_create_quiz", None, courseid=courseid, cmid=body.cmid, section=body.section,
                       name=body.name.strip(), intro=body.intro,
                       timeopen=body.timeopen, timeclose=body.timeclose, timelimit=body.timelimit, attempts=body.attempts,
                       grade=body.grade, showanswers=body.showanswers, visible=1 if body.visible else 0, questions=qs)
        return r

    async def chapter_material(sess: Session, courseid: int, section: int, lg: str) -> tuple[str, list[str]]:
        tok = sess.moodle_token
        secs = await state.moodle.course_contents(tok, courseid, None)
        sec = next((s for s in secs if s.get("section") == section), None)
        if not sec:
            raise EngineError("not_found", "section", 404)
        pages = {p["coursemodule"]: p for p in await state.moodle.pages(tok, courseid, None)}
        parts = []
        for mod in sec.get("modules") or []:
            p = pages.get(mod["id"])
            if p and mod.get("visible", 1):   # lessons students can see, not answer keys or plans
                parts.append(f"## {m.plain(p.get('name'), lg)}\n{m.plain(p.get('content'), lg)[:12000]}")
        return m.plain(sec.get("name"), lg), parts

    @app.post("/api/v1/courses/{courseid}/assignments/ai")
    async def ai_assignment(courseid: int, body: AiAssignIn, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        """A draft assignment (problems, requirements, rubric) and its answer key; nothing is saved here."""
        await need_teacher(sess, courseid)
        lg = m.lang_of(lang, sess)
        title, parts = await chapter_material(sess, courseid, body.section, lg)
        prompt = (f"Chapter: {title}\n" + (f"Teacher's request: {body.note}\n" if body.note else "")
                  + ("\nLesson material:\n" + "\n\n".join(parts)[:60000] if parts
                     else "\n(No lesson pages yet: set the assignment from your own knowledge of this chapter.)"))
        out = await state.ai.json(system=ASSIGN_WRITER, prompt=prompt, schema=assign_schema(), max_tokens=12000,
                                  fake=lambda: fake_assignment(title))
        out = out or {}
        grade = max(1.0, min(1000.0, float(out.get("grade") or 100)))
        rubric = [r for r in out.get("rubric") or [] if isinstance(r, dict) and r.get("criterion")]
        table = ""
        if rubric:
            rows = "".join(f"<tr><td>{htmllib.escape(str(r['criterion']))}</td><td>{float(r.get('points') or 0):g}</td></tr>" for r in rubric)
            table = f"<h4>评分标准</h4><table><tr><th>项目</th><th>分值</th></tr>{rows}</table>"
        intro = (str(out.get("problems") or "") + ("<h4>提交要求</h4>" + str(out.get("requirements")) if out.get("requirements") else "")
                 + table)
        if not intro.strip():
            raise EngineError("ai_bad_output", "empty assignment", 502)
        return {"name": str(out.get("name") or f"{title} 作业")[:200], "intro": intro, "answers": str(out.get("answers") or ""),
                "grade": grade, "days": max(1, min(60, int(out.get("days") or 7))), "chapter": title}

    @app.post("/api/v1/courses/{courseid}/quizzes/ai")
    async def ai_quiz(courseid: int, body: AiQuizIn, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        """Draft questions from a chapter's lessons; nothing is saved until the teacher saves the quiz."""
        await need_teacher(sess, courseid)
        lg = m.lang_of(lang, sess)
        tok = sess.moodle_token
        secs = await state.moodle.course_contents(tok, courseid, None)
        sec = next((s for s in secs if s.get("section") == body.section), None)
        if not sec:
            raise EngineError("not_found", "section", 404)
        pages = {p["coursemodule"]: p for p in await state.moodle.pages(tok, courseid, None)}
        parts = []
        for mod in sec.get("modules") or []:
            p = pages.get(mod["id"])
            if p:
                parts.append(f"## {m.plain(p.get('name'), lg)}\n{m.plain(p.get('content'), lg)[:12000]}")
        title = m.plain(sec.get("name"), lg)
        if not parts:
            raise EngineError("no_material", "this chapter has no lesson pages to write questions from", 400)
        types = [t for t in body.types if t in ("single", "multiple", "truefalse", "shortanswer", "numerical")] or ["single"]
        prompt = (f"Chapter: {title}\nWrite {body.count} questions. Allowed types: {', '.join(types)}; mix them.\n"
                  + (f"Teacher's request: {body.note}\n" if body.note else "") + "\nLesson material:\n" + "\n\n".join(parts)[:60000])
        out = await state.ai.json(system=QUIZ_WRITER, prompt=prompt, schema=quiz_schema(), max_tokens=12000,
                                  fake=lambda: {"questions": fake_questions(title, body.count)})
        qs = [q for q in check_questions((out or {}).get("questions") or []) if q.get("type") in types][: body.count]
        if not qs:
            raise EngineError("ai_bad_output", "no usable questions", 502)
        return {"questions": qs, "title": title}
