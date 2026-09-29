"""Course work in WenQuest's own UI (round 3, D32 / step B2): assignments (submit, grade, AI grading
suggestion), quizzes (answer, review), grades, calendar and inbox. Registered by main.create_app().

All calls use the signed-in user's own Moodle token; Moodle decides what each person may do.
"""

import asyncio
import json
import random
import re
import time
from typing import Annotated, Any

from fastapi import Depends, File, Form, UploadFile
from pydantic import BaseModel, Field

from . import materials as mt
from . import quiz_parse as qp
from .course_api import text_html
from .moodle import EngineError
from .session import Session

MAX_UPLOAD = 50 * 1024 * 1024


class AnswersIn(BaseModel):
    answers: dict[str, Any] = Field(default_factory=dict)
    finish: bool = False
    timeup: bool = False


class GradeIn(BaseModel):
    grade: float | None = None
    feedback: str = Field(default="", max_length=20000)


class EventIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    timestart: int = Field(gt=0)
    duration: int = Field(default=0, ge=0, le=60 * 24 * 14)   # minutes
    description: str = Field(default="", max_length=4000)


class MessageIn(BaseModel):
    text: str = Field(min_length=1, max_length=8000)


class NewMessageIn(BaseModel):
    to: list[int] = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=8000)


AI_GRADER = (
    "You are the teaching assistant of a university course on WenQuest. Suggest a grade for one student's "
    "submission against the assignment's requirements and rubric (if the assignment gives one; otherwise judge "
    "correctness, completeness, reasoning and presentation). Be fair and specific: quote or point to the parts "
    "of the work that earn or lose marks. The teacher will review your suggestion before anything is saved. "
    "Write the comment to the student, in Chinese unless the assignment is in English: what is good, what is "
    "wrong or missing, and how to improve. Never exceed the maximum grade."
)


def register(app, m) -> None:
    current = m.current
    state = m.state

    def clean(h: str | None, lg: str | None, tok: str) -> str:
        return m.content.clean(m.resolve(h, lg), state.settings.moodle_url, m.sign_file(tok))

    async def call(sess: Session, fn: str, lang: str | None = None, **params: Any) -> Any:
        return await state.moodle.call(sess.moodle_token, fn, lang, **params)

    async def is_teacher(sess: Session, courseid: int) -> bool:
        try:
            return await state.moodle.can_edit_course(sess.moodle_token, courseid)
        except EngineError:
            return False

    async def cm_of(sess: Session, cmid: int, kind: str) -> dict:
        cm = await state.moodle.course_module(sess.moodle_token, cmid)
        if cm.get("modname") != kind:
            raise EngineError("not_found", kind, 404)
        return cm

    def files_of(plugins: list[dict] | None, kind: str, tok: str) -> list[dict]:
        out = []
        for p in plugins or []:
            if p.get("type") != kind:
                continue
            for area in p.get("fileareas") or []:
                for f in area.get("files") or []:
                    if f.get("fileurl"):
                        out.append({"name": f.get("filename"), "size": f.get("filesize"), "mimetype": f.get("mimetype"),
                                    "url": m.sign_file(tok)(f["fileurl"]), "_raw": f["fileurl"]})
        return out

    def text_of(plugins: list[dict] | None, kind: str) -> str:
        for p in plugins or []:
            if p.get("type") == kind:
                for e in p.get("editorfields") or []:
                    return e.get("text") or ""
        return ""

    # ============================================================================ assignments

    async def assignment(sess: Session, cmid: int, lg: str | None) -> tuple[dict, dict]:
        cm = await cm_of(sess, cmid, "assign")
        a = next((x for x in await state.moodle.assignments(sess.moodle_token, int(cm["course"]), lg) if x["cmid"] == cmid), None)
        if not a:
            raise EngineError("not_found", "assign", 404)
        return cm, a

    def assign_config(a: dict) -> dict:
        cfg = {(c.get("plugin"), c.get("subtype"), c.get("name")): c.get("value") for c in a.get("configs") or []}
        get = lambda plugin, name, d="0": cfg.get((plugin, "assignsubmission", name), d)  # noqa: E731
        return {
            "text": get("onlinetext", "enabled") == "1",
            "files": get("file", "enabled") == "1",
            "maxfiles": int(get("file", "maxfilesubmissions", "0") or 0),
            "maxbytes": int(get("file", "maxsubmissionsizebytes", "0") or 0),
            "filetypes": get("file", "filetypeslist", ""),
            "wordlimit": int(get("onlinetext", "wordlimit", "0") or 0),
            "drafts": bool(a.get("submissiondrafts")),   # with drafts, saving and handing in are separate steps
        }

    def submission_view(st: dict, tok: str, lg: str | None) -> dict:
        last = st.get("lastattempt") or {}
        sub = last.get("submission") or (last.get("teamsubmission") or {})
        fb = st.get("feedback") or {}
        return {
            "status": sub.get("status") or "new",               # new, draft, submitted, reopened
            "modified": sub.get("timemodified") or 0,
            "text": clean(text_of(sub.get("plugins"), "onlinetext"), lg, tok),
            "files": [{k: v for k, v in f.items() if k != "_raw"} for f in files_of(sub.get("plugins"), "file", tok)],
            "can_edit": bool(last.get("canedit")),
            "can_submit": bool(last.get("cansubmit")),
            "grading": last.get("gradingstatus") or "",
            "locked": bool(last.get("locked")),
            "extension": last.get("extensionduedate") or 0,
            "graded": bool(fb.get("grade")),
            "grade": fb.get("gradefordisplay") or "",
            "grade_raw": (fb.get("grade") or {}).get("grade"),
            "feedback": clean(text_of(fb.get("plugins"), "comments"), lg, tok),
            "feedback_files": [{k: v for k, v in f.items() if k != "_raw"} for f in files_of(fb.get("plugins"), "file", tok)],
            "graded_at": fb.get("gradeddate") or 0,
        }

    @app.get("/api/v1/assignments/{cmid}")
    async def assignment_page(cmid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = m.lang_of(lang, sess)
        tok = sess.moodle_token
        cm, a = await assignment(sess, cmid, lg)
        courseid = int(cm["course"])
        teacher = await is_teacher(sess, courseid)
        out = {
            "id": a["id"], "cmid": cmid, "course_id": courseid, "name": m.plain(a.get("name"), lg),
            "intro": clean(a.get("intro"), lg, tok),
            "attachments": [{"name": f.get("filename"), "url": m.sign_file(tok)(f["fileurl"])}
                            for f in a.get("introattachments") or [] if f.get("fileurl")],
            "due": a.get("duedate") or 0, "cutoff": a.get("cutoffdate") or 0, "opens": a.get("allowsubmissionsfromdate") or 0,
            "max_grade": a.get("grade"), "config": assign_config(a), "teacher": teacher,
        }
        st = await call(sess, "mod_assign_get_submission_status", lg, assignid=a["id"])
        if teacher:
            g = st.get("gradingsummary") or {}
            out["summary"] = {"participants": g.get("participantcount", 0), "submitted": g.get("submissionssubmittedcount", 0),
                              "drafts": g.get("submissiondraftscount", 0), "needs_grading": g.get("submissionsneedgradingcount", 0)}
        else:
            out["submission"] = submission_view(st, tok, lg)
        try:
            await call(sess, "mod_assign_view_assign", None, assignid=a["id"])
        except EngineError:
            pass
        return out

    async def build_draft(sess: Session, keep: list[dict], new: list[tuple[str, bytes]]) -> int:
        """One draft area holding the files the student keeps plus the new ones."""
        itemid = 0
        for f in keep:
            r = await state.moodle.fetch_file(sess.moodle_token, f["_raw"])
            itemid = await state.moodle.upload(sess.moodle_token, f["name"], r.content, itemid)
        for name, data in new:
            itemid = await state.moodle.upload(sess.moodle_token, name, data, itemid)
        return itemid or random.randint(10_000_000, 999_999_999)   # an empty area removes every file

    @app.post("/api/v1/assignments/{cmid}/submission")
    async def submit(cmid: int, sess: Annotated[Session, Depends(current)],
                     text: Annotated[str | None, Form()] = None, keep: Annotated[str, Form()] = "[]",
                     submit: Annotated[bool, Form()] = False, files: Annotated[list[UploadFile] | None, File()] = None):
        """Save the student's work (text and/or files); `submit` also hands it in for grading."""
        cm, a = await assignment(sess, cmid, None)
        cfg = assign_config(a)
        st = await call(sess, "mod_assign_get_submission_status", None, assignid=a["id"])
        cur = submission_view(st, sess.moodle_token, None)
        if not cur["can_edit"] and (text is not None or files):
            raise EngineError("submission_closed", "this assignment no longer accepts changes", 409)
        plugindata: dict[str, Any] = {}
        if text is not None and cfg["text"]:
            plugindata["onlinetext_editor"] = {"text": text_html(text) if text.strip() else "", "format": 1, "itemid": 0}
        new = []
        for f in files or []:
            data = await f.read()
            if len(data) > MAX_UPLOAD or (cfg["maxbytes"] and len(data) > cfg["maxbytes"]):
                raise EngineError("file_too_large", f.filename or "file", 413)
            new.append((mt.fix_name(f.filename or "file"), data))
        try:
            keep_names = set(json.loads(keep or "[]"))
        except ValueError:
            keep_names = set()
        existing = files_of(((st.get("lastattempt") or {}).get("submission") or {}).get("plugins"), "file", sess.moodle_token)
        kept = [f for f in existing if f["name"] in keep_names]
        if cfg["files"] and (new or len(kept) != len(existing)):
            if cfg["maxfiles"] and len(kept) + len(new) > cfg["maxfiles"]:
                raise EngineError("too_many_files", str(cfg["maxfiles"]), 400)
            plugindata["files_filemanager"] = await build_draft(sess, kept, new)
        if plugindata:
            r = await call(sess, "mod_assign_save_submission", None, assignmentid=a["id"], plugindata=plugindata)
            if r:  # warnings mean Moodle refused the change
                w = r[0] if isinstance(r, list) else r
                raise EngineError("submission_refused", str(w.get("item") or w.get("message") or w)[:200], 409)
        if submit and cfg["drafts"]:
            r = await call(sess, "mod_assign_submit_for_grading", None, assignmentid=a["id"], acceptsubmissionstatement=1)
            if r:
                w = r[0] if isinstance(r, list) else r
                raise EngineError("submission_refused", str(w.get("message") or w.get("item") or w)[:200], 409)
        st = await call(sess, "mod_assign_get_submission_status", m.lang_of(None, sess), assignid=a["id"])
        return submission_view(st, sess.moodle_token, m.lang_of(None, sess))

    @app.get("/api/v1/assignments/{cmid}/submissions")
    async def submissions(cmid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = m.lang_of(lang, sess)
        cm, a = await assignment(sess, cmid, lg)
        people = await call(sess, "mod_assign_list_participants", lg, assignid=a["id"], groupid=0, filter="",
                            skip=0, limit=0, onlyids=0, includeenrolments=0, tablesort=0)
        subs = await call(sess, "mod_assign_get_submissions", None, assignmentids=[a["id"]])
        grades = await call(sess, "mod_assign_get_grades", None, assignmentids=[a["id"]])
        by_user = {s["userid"]: s for x in subs.get("assignments") or [] for s in x.get("submissions") or []}
        grade_of = {g["userid"]: g for x in grades.get("assignments") or [] for g in x.get("grades") or []}
        rows = []
        for p in people:
            s = by_user.get(p["id"]) or {}
            g = grade_of.get(p["id"])
            graw = float(g["grade"]) if g and g.get("grade") not in (None, "") and float(g["grade"]) >= 0 else None
            rows.append({"id": p["id"], "fullname": p.get("fullname") or "", "groups": [x.get("name") for x in p.get("groups") or []],
                         "status": s.get("status") or ("submitted" if p.get("submitted") else "new"),
                         "modified": s.get("timemodified") or 0, "needs_grading": bool(p.get("requiregrading")),
                         "grade": graw, "late": bool(a.get("duedate") and s.get("status") == "submitted"
                                                      and (s.get("timemodified") or 0) > a["duedate"])})
        order = {"submitted": 0, "draft": 1, "reopened": 2, "new": 3}
        rows.sort(key=lambda r: (not r["needs_grading"], order.get(r["status"], 4), r["fullname"]))
        return {"assignment": {"id": a["id"], "name": m.plain(a.get("name"), lg), "max_grade": a.get("grade"),
                               "due": a.get("duedate") or 0}, "rows": rows}

    async def student_work(sess: Session, a: dict, userid: int, lg: str | None) -> tuple[dict, dict]:
        st = await call(sess, "mod_assign_get_submission_status", lg, assignid=a["id"], userid=userid)
        return st, submission_view(st, sess.moodle_token, lg)

    @app.get("/api/v1/assignments/{cmid}/submissions/{userid}")
    async def submission_detail(cmid: int, userid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = m.lang_of(lang, sess)
        cm, a = await assignment(sess, cmid, lg)
        _, view = await student_work(sess, a, userid, lg)
        return {**view, "userid": userid, "max_grade": a.get("grade")}

    @app.put("/api/v1/assignments/{cmid}/grades/{userid}")
    async def save_grade(cmid: int, userid: int, body: GradeIn, sess: Annotated[Session, Depends(current)]):
        cm, a = await assignment(sess, cmid, None)
        mx = float(a.get("grade") or 100)
        if body.grade is not None and not (0 <= body.grade <= mx):
            raise EngineError("grade_out_of_range", str(mx), 400)
        await call(sess, "mod_assign_save_grade", None, assignmentid=a["id"], userid=userid,
                   grade=-1 if body.grade is None else body.grade, attemptnumber=-1, addattempt=0, workflowstate="",
                   applytoall=1, plugindata={"assignfeedbackcomments_editor": {"text": text_html(body.feedback) if body.feedback.strip() else "",
                                                                                 "format": 1}})
        return {"ok": True}

    @app.post("/api/v1/assignments/{cmid}/submissions/{userid}/ai")
    async def ai_grade(cmid: int, userid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        """A suggested grade and comment; nothing is saved until the teacher saves it."""
        lg = m.lang_of(lang, sess)
        cm, a = await assignment(sess, cmid, lg)
        if not await is_teacher(sess, int(cm["course"])):
            raise EngineError("forbidden", "only teachers grade", 403)
        st, view = await student_work(sess, a, userid, lg)
        sub = (st.get("lastattempt") or {}).get("submission") or {}
        parts = []
        if view["text"]:
            parts.append("Online text:\n" + m.plain(view["text"], lg)[:30000])
        for f in files_of(sub.get("plugins"), "file", sess.moodle_token)[:5]:
            try:
                data = (await state.moodle.fetch_file(sess.moodle_token, f["_raw"])).content
                txt, _ = await asyncio.to_thread(mt.extract, f["name"], data)
                parts.append(f"File {f['name']}:\n{mt.clean(txt)[:30000]}")
            except Exception as e:  # noqa: BLE001 - an unreadable file is reported, not fatal
                parts.append(f"File {f['name']}: (could not be read: {type(e).__name__})")
        if not parts:
            raise EngineError("nothing_submitted", "this student has not submitted anything yet", 400)
        mx = float(a.get("grade") or 100)
        schema = {"type": "object", "additionalProperties": False, "required": ["grade", "comment", "criteria"],
                  "properties": {"grade": {"type": "number"}, "comment": {"type": "string"},
                                 "criteria": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                              "required": ["name", "score", "max", "note"],
                                              "properties": {"name": {"type": "string"}, "score": {"type": "number"},
                                                             "max": {"type": "number"}, "note": {"type": "string"}}}}}}
        prompt = (f"Assignment: {m.plain(a.get('name'), lg)}\nMaximum grade: {mx:g}\n"
                  f"Requirements and rubric:\n{m.plain(a.get('intro'), lg)[:12000]}\n\nThe student's work:\n"
                  + "\n\n".join(parts)[:60000])
        out = await state.ai.json(system=AI_GRADER, prompt=prompt, schema=schema, max_tokens=4000,
                                  fake=lambda: {"grade": round(mx * 0.8, 1), "criteria": [],
                                                "comment": "整体完成较好：思路清楚，计算基本正确。请补充误差分析，并注明各物理量的单位。"})
        grade = max(0.0, min(mx, float((out or {}).get("grade") or 0)))
        return {"grade": round(grade, 1), "max_grade": mx, "comment": str((out or {}).get("comment") or "")[:4000],
                "criteria": (out or {}).get("criteria") or []}

    # ============================================================================ quizzes

    async def quiz(sess: Session, cmid: int, lg: str | None) -> tuple[dict, dict]:
        cm = await cm_of(sess, cmid, "quiz")
        rows = (await call(sess, "mod_quiz_get_quizzes_by_courses", lg, courseids=[int(cm["course"])])).get("quizzes") or []
        q = next((x for x in rows if x.get("coursemodule") == cmid), None)
        if not q:
            raise EngineError("not_found", "quiz", 404)
        return cm, q

    def scaled(sumgrades: Any, q: dict) -> float | None:
        if sumgrades in (None, "") or not q.get("sumgrades"):
            return None
        return round(float(sumgrades) / float(q["sumgrades"]) * float(q.get("grade") or 0), 2)

    @app.get("/api/v1/quizzes/{cmid}")
    async def quiz_page(cmid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = m.lang_of(lang, sess)
        cm, q = await quiz(sess, cmid, lg)
        access = await call(sess, "mod_quiz_get_quiz_access_information", lg, quizid=q["id"])
        attempts = (await call(sess, "mod_quiz_get_user_attempts", None, quizid=q["id"], status="all", includepreviews=0)).get("attempts") or []
        new = await call(sess, "mod_quiz_get_attempt_access_information", lg, quizid=q["id"], attemptid=0)
        best = await call(sess, "mod_quiz_get_user_best_grade", None, quizid=q["id"])
        teacher = await is_teacher(sess, int(cm["course"]))
        return {
            "id": q["id"], "cmid": cmid, "course_id": int(cm["course"]), "name": m.plain(q.get("name"), lg),
            "intro": clean(q.get("intro"), lg, sess.moodle_token), "opens": q.get("timeopen") or 0, "closes": q.get("timeclose") or 0,
            "timelimit": q.get("timelimit") or 0, "attempts_allowed": q.get("attempts") or 0, "max_grade": q.get("grade"),
            "questions": bool(q.get("sumgrades")), "teacher": teacher,
            "can_attempt": bool(access.get("canattempt")) and not new.get("preventnewattemptreasons"),
            "blocked": [m.plain(x, lg) for x in (new.get("preventnewattemptreasons") or []) + (access.get("preventaccessreasons") or [])],
            "rules": [m.plain(x, lg) for x in access.get("accessrules") or []],
            "attempts": [{"id": x["id"], "number": x.get("attempt"), "state": x.get("state"), "start": x.get("timestart"),
                          "finish": x.get("timefinish"), "grade": scaled(x.get("sumgrades"), q)} for x in attempts],
            "best": float(best["grade"]) if best.get("hasgrade") else None,
        }

    @app.post("/api/v1/quizzes/{cmid}/attempt")
    async def start_attempt(cmid: int, sess: Annotated[Session, Depends(current)]):
        cm, q = await quiz(sess, cmid, None)
        open_ = (await call(sess, "mod_quiz_get_user_attempts", None, quizid=q["id"], status="unfinished", includepreviews=1)).get("attempts") or []
        if open_:
            return {"attempt": open_[0]["id"]}
        r = await call(sess, "mod_quiz_start_attempt", None, quizid=q["id"], forcenew=0)
        return {"attempt": r["attempt"]["id"]}

    async def attempt_pages(sess: Session, aid: int, lg: str | None) -> tuple[dict, list[dict]]:
        first = await call(sess, "mod_quiz_get_attempt_data", lg, attemptid=aid, page=0)
        att = first["attempt"]
        layout = [x for x in str(att.get("layout") or "").split(",") if x != ""]
        pages = max(1, layout.count("0"))
        datas = [first] + list(await asyncio.gather(*[call(sess, "mod_quiz_get_attempt_data", lg, attemptid=aid, page=p)
                                                      for p in range(1, pages)]))
        tok = sess.moodle_token
        questions = [qp.parse_question(q, lambda h: clean(h, lg, tok)) for d in datas for q in d.get("questions") or []]
        for q in questions:
            q.setdefault("page", 0)
        return att, questions

    @app.get("/api/v1/quiz-attempts/{aid}")
    async def attempt(aid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = m.lang_of(lang, sess)
        att, questions = await attempt_pages(sess, aid, lg)
        quizrow = None
        if att.get("quiz"):
            cm = await call(sess, "core_course_get_course_module_by_instance", None, module="quiz", instance=att["quiz"])
            _, quizrow = await quiz(sess, int(cm["cm"]["id"]), lg)
        deadline = att.get("timecheckstate") or 0
        if quizrow and quizrow.get("timelimit"):
            deadline = min(x for x in (deadline or 10**12, att["timestart"] + quizrow["timelimit"]) if x)
        if quizrow and quizrow.get("timeclose"):
            deadline = min(x for x in (deadline or 10**12, quizrow["timeclose"]) if x)
        return {"id": aid, "state": att.get("state"), "start": att.get("timestart"), "deadline": deadline or 0,
                "now": int(time.time()), "quiz": {"name": m.plain(quizrow.get("name"), lg) if quizrow else "",
                                                  "cmid": quizrow.get("coursemodule") if quizrow else None,
                                                  "course_id": quizrow.get("course") if quizrow else None},
                "questions": questions}

    @app.post("/api/v1/quiz-attempts/{aid}")
    async def save_attempt(aid: int, body: AnswersIn, sess: Annotated[Session, Depends(current)]):
        """Save answers; `finish` hands the attempt in (also when time is up)."""
        att, questions = await attempt_pages(sess, aid, None)
        if att.get("state") != "inprogress":
            raise EngineError("attempt_closed", "this attempt is already finished", 409)
        data = qp.form_data(questions, body.answers)
        r = await call(sess, "mod_quiz_process_attempt", None, attemptid=aid, data=data,
                       finishattempt=1 if body.finish else 0, timeup=1 if body.timeup else 0)
        return {"state": r.get("state")}

    @app.get("/api/v1/quiz-attempts/{aid}/review")
    async def review(aid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = m.lang_of(lang, sess)
        tok = sess.moodle_token
        try:
            r = await call(sess, "mod_quiz_get_attempt_review", lg, attemptid=aid, page=-1)
        except EngineError as e:
            if e.status in (401, 403) or e.code in ("forbidden", "noreviewattempt", "noreview"):
                return {"available": False}
            raise
        att = r.get("attempt") or {}
        cm = await call(sess, "core_course_get_course_module_by_instance", None, module="quiz", instance=att.get("quiz"))
        _, q = await quiz(sess, int(cm["cm"]["id"]), lg)
        return {"available": True, "grade": round(float(r["grade"]), 2) if r.get("grade") not in (None, "") else None,
                "max_grade": q.get("grade"), "state": att.get("state"), "start": att.get("timestart"), "finish": att.get("timefinish"),
                "quiz": {"name": m.plain(q.get("name"), lg), "cmid": q.get("coursemodule"), "course_id": q.get("course")},
                "questions": [qp.parse_question(x, lambda h: clean(h, lg, tok)) for x in r.get("questions") or []]}

    # ============================================================================ grades

    @app.get("/api/v1/courses/{courseid}/grades")
    async def grades(courseid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = m.lang_of(lang, sess)
        teacher = await is_teacher(sess, courseid)
        r = await call(sess, "gradereport_user_get_grade_items", lg, courseid=courseid, userid=0 if teacher else sess.user_id)
        users = r.get("usergrades") or []

        def item_of(i: dict) -> dict:
            return {"id": i["id"], "name": m.plain(i.get("itemname"), lg) or ("课程总评" if i.get("itemtype") == "course" else ""),
                    "type": i.get("itemtype"), "module": i.get("itemmodule"), "cmid": i.get("cmid"), "max": i.get("grademax")}

        def cell(i: dict) -> dict:
            return {"raw": i.get("graderaw"), "text": i.get("gradeformatted") or "", "percent": i.get("percentageformatted") or "",
                    "feedback": clean(i.get("feedback"), lg, sess.moodle_token), "hidden": bool(i.get("gradehiddenbydate") or i.get("hidden")),
                    "graded_at": i.get("gradedategraded") or 0}

        items = [item_of(i) for i in (users[0].get("gradeitems") if users else [])]
        if teacher:
            rows = [{"id": u["userid"], "fullname": u.get("userfullname") or "",
                     "cells": {str(i["id"]): cell(i) for i in u.get("gradeitems") or []}} for u in users]
            return {"teacher": True, "items": items, "rows": rows}
        mine = users[0] if users else {}
        return {"teacher": False, "items": items, "cells": {str(i["id"]): cell(i) for i in mine.get("gradeitems") or []}}

    # ============================================================================ calendar

    async def my_courses(sess: Session, lg: str | None) -> list[dict]:
        rows = await state.moodle.user_courses(sess.moodle_token, sess.user_id, lg)
        return [{"id": c["id"], "name": m.plain(c.get("fullname"), lg)} for c in rows if c.get("visible", 1)]

    @app.get("/api/v1/calendar")
    async def calendar(sess: Annotated[Session, Depends(current)], start: int, end: int, course: int = 0, lang: str | None = None):
        lg = m.lang_of(lang, sess)
        if end <= start or end - start > 100 * 86400:
            raise EngineError("bad_range", "at most 100 days", 400)
        courses = await my_courses(sess, lg)
        ids = [course] if course else [c["id"] for c in courses]
        names = {c["id"]: c["name"] for c in courses}
        r = await call(sess, "core_calendar_get_calendar_events", lg, events={"courseids": ids},
                       options={"userevents": 1, "siteevents": 1, "timestart": start, "timeend": end, "ignorehidden": 1})
        events = r.get("events") or []
        # Activity events open the activity in WenQuest: find their course modules.
        cms: dict[tuple[str, int], int] = {}
        need = {int(e["courseid"]) for e in events if e.get("modulename") and e.get("courseid")}
        contents = await asyncio.gather(*[state.moodle.course_contents(sess.moodle_token, cid, None) for cid in need],
                                        return_exceptions=True)
        for secs in contents:
            if isinstance(secs, Exception):
                continue
            for s in secs:
                for mod in s.get("modules") or []:
                    cms[(mod.get("modname"), int(mod.get("instance") or 0))] = mod["id"]
        teacher_of = {}
        if course:
            teacher_of[course] = await is_teacher(sess, course)
        out = []
        for e in events:
            cid = int(e.get("courseid") or 0)
            out.append({"id": e["id"], "name": m.plain(e.get("name"), lg), "description": clean(e.get("description"), lg, sess.moodle_token),
                        "start": e.get("timestart"), "duration": e.get("timeduration") or 0, "type": e.get("eventtype"),
                        "course_id": cid, "course": names.get(cid, ""), "module": e.get("modulename") or "",
                        "cmid": cms.get((e.get("modulename"), int(e.get("instance") or 0))),
                        "can_delete": e.get("eventtype") in ("course", "user") and (e.get("eventtype") == "user" or teacher_of.get(cid, False))})
        out.sort(key=lambda x: x["start"] or 0)
        return {"events": out, "courses": courses, "can_add": bool(course and teacher_of.get(course))}

    @app.post("/api/v1/courses/{courseid}/events")
    async def add_event(courseid: int, body: EventIn, sess: Annotated[Session, Depends(current)]):
        r = await call(sess, "core_calendar_create_calendar_events", None, events=[{
            "name": body.name.strip(), "courseid": courseid, "eventtype": "course", "timestart": body.timestart,
            "timeduration": body.duration * 60, "description": text_html(body.description) if body.description.strip() else "",
            "format": 1}])
        if r.get("warnings"):
            raise EngineError("forbidden", str(r["warnings"][0].get("message"))[:200], 403)
        return {"ok": True}

    @app.delete("/api/v1/events/{eventid}")
    async def delete_event(eventid: int, sess: Annotated[Session, Depends(current)]):
        await call(sess, "core_calendar_delete_calendar_events", None, events=[{"eventid": eventid, "repeat": 0}])
        return {"ok": True}

    # ============================================================================ inbox

    def conv_view(c: dict, me: int, tok: str) -> dict:
        others = [u for u in c.get("members") or [] if u.get("id") != me]
        last = (c.get("messages") or [None])[0]
        return {"id": c["id"], "name": c.get("name") or "、".join(u.get("fullname", "") for u in others[:3]),
                "group": c.get("type") == 2, "members": len(c.get("members") or []) if c.get("type") == 2 else len(others) + 1,
                "unread": c.get("unreadcount") or 0, "last": m.plain(last.get("text"), None)[:120] if last else "",
                "time": last.get("timecreated") if last else 0, "from_me": bool(last and last.get("useridfrom") == me)}

    @app.get("/api/v1/inbox")
    async def inbox(sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = m.lang_of(lang, sess)
        r = await call(sess, "core_message_get_conversations", lg, userid=sess.user_id, limitfrom=0, limitnum=100, mergeself=1)
        convs = [conv_view(c, sess.user_id, sess.moodle_token) for c in r.get("conversations") or []
                 if c.get("type") != 3 or c.get("messages")]   # the empty "notes to self" conversation
        n = await call(sess, "core_message_get_messages", lg, useridto=sess.user_id, useridfrom=0, type="notifications",
                       read=2, newestfirst=1, limitfrom=0, limitnum=50)
        notes = [{"id": x["id"], "subject": m.plain(x.get("subject"), lg), "text": m.plain(x.get("smallmessage") or x.get("fullmessage"), lg)[:300],
                  "time": x.get("timecreated"), "read": bool(x.get("timeread"))} for x in n.get("messages") or []]
        return {"conversations": convs, "notifications": notes}

    @app.get("/api/v1/inbox/unread")
    async def unread(sess: Annotated[Session, Depends(current)]):
        c = await call(sess, "core_message_get_unread_conversations_count", None, useridto=sess.user_id)
        n = await call(sess, "core_message_get_unread_notification_count", None, useridto=sess.user_id)
        return {"messages": int(c or 0), "notifications": int(n or 0)}

    @app.get("/api/v1/inbox/{convid}")
    async def conversation(convid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = m.lang_of(lang, sess)
        r = await call(sess, "core_message_get_conversation_messages", lg, currentuserid=sess.user_id, convid=convid,
                       limitfrom=0, limitnum=200, newest=1)
        names = {u["id"]: u.get("fullname", "") for u in r.get("members") or []}
        msgs = [{"id": x["id"], "from": x.get("useridfrom"), "author": names.get(x.get("useridfrom"), ""),
                 "text": clean(x.get("text"), lg, sess.moodle_token), "time": x.get("timecreated"),
                 "mine": x.get("useridfrom") == sess.user_id} for x in r.get("messages") or []]
        msgs.sort(key=lambda x: (x["time"] or 0, x["id"]))
        try:
            await call(sess, "core_message_mark_all_conversation_messages_as_read", None, userid=sess.user_id, conversationid=convid)
        except EngineError:
            pass
        others = [n for uid, n in names.items() if uid != sess.user_id]
        return {"id": convid, "name": "、".join(others[:4]), "messages": msgs}

    @app.post("/api/v1/inbox/{convid}")
    async def send(convid: int, body: MessageIn, sess: Annotated[Session, Depends(current)]):
        await call(sess, "core_message_send_messages_to_conversation", None, conversationid=convid,
                   messages=[{"text": text_html(body.text), "textformat": 1}])
        return {"ok": True}

    @app.post("/api/v1/inbox")
    async def new_message(body: NewMessageIn, sess: Annotated[Session, Depends(current)]):
        msgs = [{"touserid": uid, "text": text_html(body.text), "textformat": 1} for uid in dict.fromkeys(body.to) if uid != sess.user_id]
        r = await call(sess, "core_message_send_instant_messages", None, messages=msgs)
        failed = [x for x in r if x.get("msgid", -1) == -1]
        convs = {x.get("conversationid") for x in r if x.get("conversationid")}
        return {"sent": len(r) - len(failed), "failed": [x.get("errormessage") for x in failed],
                "conversation": convs.pop() if len(convs) == 1 else None}

    @app.get("/api/v1/inbox-contacts")
    async def contacts(sess: Annotated[Session, Depends(current)], lang: str | None = None):
        """People the user can write to: everyone in their courses, by course and group."""
        lg = m.lang_of(lang, sess)
        courses = (await my_courses(sess, lg))[:30]
        lists = await asyncio.gather(*[call(sess, "core_enrol_get_enrolled_users", lg, courseid=c["id"], options=[
            {"name": "userfields", "value": "id,fullname,roles,groups"}]) for c in courses], return_exceptions=True)
        out = []
        for c, users in zip(courses, lists):
            if isinstance(users, Exception):
                continue
            people = [{"id": u["id"], "fullname": u.get("fullname", ""),
                       "teacher": bool({"editingteacher", "teacher", "manager"} & {r.get("shortname") for r in u.get("roles") or []}),
                       "groups": [g.get("name") for g in u.get("groups") or []]} for u in users if u["id"] != sess.user_id]
            out.append({"id": c["id"], "name": c["name"], "people": people})
        return {"courses": out}
