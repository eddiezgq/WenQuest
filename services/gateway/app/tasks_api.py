"""Engineering task sheets in a course (round 11, 2.7 (4)(5)): the teacher picks a task sheet from the textbooks, issues it
to a class factory, follows each student's progress and writes the grades into the course gradebook.

The work itself (deliverables, AI design reviewer, comments, approval, rubric grades) lives in the digital factory hub;
the gateway keeps only which course issued which task sheet to which factory and under which Moodle assignment, and
talks to the hub server-to-server with the task-sheet key (WQ_FACTORY_TASK_KEY). Grades are written with the teacher's
own Moodle session (mod_assign_save_grade); the student's id is the same on both sides (one sign-on).
"""

import html
import json
import re
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import urlparse

from fastapi import Depends, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .moodle import EngineError
from .session import Session

BOOK = re.compile(r"^[a-z][a-z0-9_-]{0,40}$")
NO = re.compile(r"^\d{1,3}\.\d{1,3}$")
CODE = re.compile(r"^TS-\d{1,3}-\d{1,3}$")


class IssueIn(BaseModel):
    book: str = Field(max_length=40)
    no: str = Field(max_length=10)                       # 33.1
    factory: str = Field(default="", max_length=20)      # class factory id; "" = the public factory
    due: int = Field(default=0, ge=0)                    # unix time, 0 = none
    section: int = Field(default=0, ge=0, le=200)


class PushIn(BaseModel):
    again: bool = False                                  # also rewrite grades already written


class Store:
    def __init__(self, folder: str):
        Path(folder).mkdir(parents=True, exist_ok=True)
        self.path = str(Path(folder) / "tasks.db")
        self.lock = threading.Lock()
        self._db()

    def _db(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        with c:                               # every time: the file may have been replaced (restore, cleanup)
            c.execute("create table if not exists course_task (course_id integer not null, code text not null, factory text not null,"
                      " tid text not null, cmid integer, book text, no text, title_zh text, title_en text, due integer,"
                      " issued_by integer, issued_at integer, primary key (course_id, code))")
        return c

    def put(self, **row: Any) -> None:
        with self.lock, self._db() as c:
            c.execute("insert into course_task (course_id, code, factory, tid, cmid, book, no, title_zh, title_en, due, issued_by, issued_at)"
                      " values (:course_id, :code, :factory, :tid, :cmid, :book, :no, :title_zh, :title_en, :due, :issued_by, :issued_at)"
                      " on conflict (course_id, code) do update set factory=excluded.factory, tid=excluded.tid, cmid=excluded.cmid,"
                      " due=excluded.due", row)

    def of_course(self, course_id: int) -> list[dict]:
        with self._db() as c:
            return [dict(r) for r in c.execute("select * from course_task where course_id=? order by issued_at", (course_id,))]

    def one(self, course_id: int, code: str) -> dict | None:
        with self._db() as c:
            r = c.execute("select * from course_task where course_id=? and code=?", (course_id, code)).fetchone()
            return dict(r) if r else None


def classes(raw: str) -> list[dict]:
    """WQ_FACTORY_CLASSES = "pilot:试点班,g2:二班" → [{id, name}]"""
    out = []
    for part in (raw or "").split(","):
        if ":" in part:
            i, n = part.split(":", 1)
            if re.fullmatch(r"[a-z][a-z0-9]{1,19}", i.strip()):
                out.append({"id": i.strip(), "name": n.strip() or i.strip()})
    return out


def factory_base(public: str, cid: str) -> str:
    """https://factory.<domain> → the class factory https://<cid>.factory.<domain>"""
    public = (public or "").rstrip("/")
    if not cid:
        return public
    u = urlparse(public)
    return f"{u.scheme}://{cid}.{u.netloc}"


def register(app, m) -> None:
    current = m.current
    state = m.state
    _store: dict[str, Store] = {}

    def store() -> Store:
        k = state.settings.data_dir
        if k not in _store:
            _store[k] = Store(str(Path(k) / "tasks"))
        return _store[k]

    def root() -> Path:
        return Path(state.settings.textbook_dir)

    def ready() -> None:
        if not (state.settings.factory_url and state.settings.factory_task_key):
            raise EngineError("factory_unavailable", "the digital factory is not connected", 503)

    def known(cid: str) -> bool:
        return cid == "" or any(c["id"] == cid for c in classes(state.settings.factory_classes))

    async def factory(method: str, cid: str, path: str, **kw: Any) -> Any:
        ready()
        url = factory_base(state.settings.factory_url, cid) + path
        try:
            r = await state.http.request(method, url, headers={"Authorization": f"Bearer {state.settings.factory_task_key}"},
                                         timeout=30, **kw)
        except Exception as e:  # noqa: BLE001
            raise EngineError("factory_unavailable", f"digital factory unreachable: {type(e).__name__}", 503) from e
        if r.status_code >= 400:
            try:
                detail = r.json().get("detail")
            except ValueError:
                detail = r.text[:200]
            raise EngineError("factory_error", str(detail), 502 if r.status_code >= 500 else 400)
        return r.json()

    async def is_teacher(sess: Session, courseid: int) -> bool:
        try:
            return await state.moodle.can_edit_course(sess.moodle_token, courseid)
        except EngineError:
            return False

    async def need_teacher(sess: Session, courseid: int) -> None:
        if not await is_teacher(sess, courseid):
            raise EngineError("forbidden", "only the course's teachers can do this", 403)

    def spec_of(book: str, no: str) -> dict:
        if not (BOOK.match(book) and NO.match(no)):
            raise EngineError("not_found", "no such task sheet", 404)
        p = root() / book / "task" / f"ts{no.replace('.', '_')}.json"
        if not p.exists():
            raise EngineError("not_found", "no such task sheet", 404)
        return json.loads(p.read_text(encoding="utf-8"))

    def catalog() -> list[dict]:
        out = []
        if not root().is_dir():
            return out
        for d in sorted(root().iterdir()):
            if not (BOOK.match(d.name) and (d / "task").is_dir()):
                continue
            title = d.name
            idx = d / "web" / "index.json"
            if idx.exists():
                title = json.loads(idx.read_text(encoding="utf-8")).get("title", d.name)
            for p in sorted((d / "task").glob("ts*.json")):
                t = json.loads(p.read_text(encoding="utf-8"))
                out.append({"book": d.name, "book_title": title, "no": t.get("no"), "code": t.get("编号"), "title": t.get("标题"),
                            "role": t.get("角色"), "hours": t.get("学时"), "stations": t.get("工位"), "section": t.get("section")})
        return out

    @app.get("/api/v1/task-docs/{book}/{no}/{kind}")
    async def task_docs(book: str, no: str, kind: str, req: Request):
        """The task sheet, rubric or blank calculation sheet (Word) for the factory's “我的任务” page: signed in with the
        site-wide cookie (the factory is another sub-domain of the same site) or the app's bearer token."""
        from .accounts import COOKIE
        tok = req.cookies.get(COOKIE, "")
        auth = req.headers.get("authorization", "")
        sess = state.codec.read(tok) if tok else (state.codec.read(auth[7:]) if auth.lower().startswith("bearer ") else None)
        if not sess:
            raise EngineError("not_logged_in", "sign in first", 401)
        if not (BOOK.match(book) and NO.match(no) and kind in ("task", "rubric", "calc")):
            raise EngineError("not_found", "no such file", 404)
        p = root() / book / "task" / f"ts{no.replace('.', '_')}-{kind}.docx"
        if not p.exists():
            raise EngineError("not_found", "no such file", 404)
        what = {"task": "工程任务单", "rubric": "评分量规", "calc": "空白计算书"}[kind]
        return FileResponse(p, filename=f"任务{no}-{what}.docx",
                            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    @app.get("/api/v1/task-catalog")
    async def task_catalog(sess: Annotated[Session, Depends(current)]):
        """Every engineering task sheet in the built textbooks, for the teacher's “issue a task sheet” dialog."""
        if not await m.can_create(sess.moodle_token):
            raise EngineError("forbidden", "teachers only", 403)
        return {"tasks": catalog(), "factories": [{"id": "", "name": "公共工厂"}] + classes(state.settings.factory_classes),
                "connected": bool(state.settings.factory_url and state.settings.factory_task_key)}

    @app.get("/api/v1/courses/{courseid}/tasks")
    async def course_tasks(courseid: int, sess: Annotated[Session, Depends(current)]):
        """Teacher: every issued task sheet with each student's progress. Student: the issued ones and his own status."""
        teacher = await is_teacher(sess, courseid)
        rows = store().of_course(courseid)
        progress: dict[str, dict] = {}
        error = None
        for fid in sorted({r["factory"] for r in rows}):
            try:
                for t in await factory("GET", fid, f"/api/tasks/course/{courseid}"):
                    progress[t["code"]] = t
            except EngineError as e:
                error = e.message
        names = {c["id"]: c["name"] for c in classes(state.settings.factory_classes)}
        out = []
        for r in rows:
            p = progress.get(r["code"]) or {}
            subs = p.get("submissions") or []
            base = factory_base(state.settings.factory_url, r["factory"])
            item = {"code": r["code"], "book": r["book"], "no": r["no"], "title": {"zh": r["title_zh"], "en": r["title_en"]},
                    "factory": r["factory"], "factory_name": names.get(r["factory"], "公共工厂" if not r["factory"] else r["factory"]),
                    "due": r["due"], "cmid": r["cmid"], "url": f"{base}/tasks/{r['tid']}"}
            if teacher:
                item["submissions"] = [{k: s.get(k) for k in ("id", "author_uid", "name", "status", "status_zh", "rounds", "open_errors",
                                                              "open_warnings", "suggested", "total", "pushed_at")} | {
                    "review_url": f"{base}/tasks/review/{s['id']}"} for s in subs]
                item["counts"] = {k: sum(1 for s in subs if s["status"] == k) for k in ("draft", "submitted", "returned", "approved", "graded")}
                item["to_push"] = sum(1 for s in subs if s.get("total") is not None and not s.get("pushed_at"))
            else:
                mine = next((s for s in subs if str(s.get("author_uid")) == str(sess.user_id)), None)
                item["mine"] = {k: mine.get(k) for k in ("status", "status_zh", "total", "open_errors")} if mine else None
            out.append(item)
        return {"teacher": teacher, "tasks": out, "factory_error": error}

    @app.post("/api/v1/courses/{courseid}/tasks")
    async def issue(courseid: int, body: IssueIn, sess: Annotated[Session, Depends(current)]):
        """Issue (or re-issue with a new due date) a task sheet: a Moodle assignment for the gradebook + the task in the factory."""
        await need_teacher(sess, courseid)
        if not known(body.factory):
            raise EngineError("not_found", "no such class factory", 404)
        ready()
        spec = spec_of(body.book, body.no)
        code = spec.get("编号", "")
        if not CODE.match(code):
            raise EngineError("bad_task", "the task sheet has no valid code", 400)
        old = store().one(courseid, code)
        title = spec.get("标题") or [code, code]
        tok = sess.moodle_token
        course = await state.moodle.course(tok, courseid, None) or {}
        base = factory_base(state.settings.factory_url, body.factory)
        if old and old["factory"] != body.factory:
            raise EngineError("already_issued", "this task sheet was issued to another factory in this course", 409)
        cmid = old["cmid"] if old else None
        if cmid is None:                      # the gradebook item first, so the factory knows where grades go
            intro = (f"<p>{html.escape((spec.get('背景') or ['', ''])[0])}</p>"
                     f"<p>在数字工厂完成：<a href='{base}/tasks' target='_blank'>{html.escape(base)}/tasks</a>（我的任务）。"
                     "交付物、AI 评审意见、批准和评分都在那里，分数由老师写回本作业。</p>")
            a = await state.moodle.call(tok, "local_wenquest_add_activities", None, courseid=courseid, section=body.section, activities=[{
                "type": "assign", "name": f"工程任务单 {code} {title[0]}"[:250], "visible": 1, "intro": intro, "content": "",
                "duedate": body.due, "grade": 100}])
            cmid = (a.get("cmids") or [0])[0] or None
        elif body.due != (old or {}).get("due"):
            await state.moodle.call(tok, "local_wenquest_edit_course", None, courseid=courseid, action="content", cmid=cmid, duedate=body.due)
        due_iso = datetime.fromtimestamp(body.due, timezone.utc).isoformat() if body.due else None
        r = await factory("POST", body.factory, "/api/tasks/course/issue", json={
            "spec": spec, "course_id": courseid, "course_name": course.get("fullname", ""), "cmid": cmid, "due": due_iso,
            "issued_by": str(sess.user_id)})
        tid = r["id"]
        store().put(course_id=courseid, code=code, factory=body.factory, tid=tid, cmid=cmid, book=body.book, no=body.no,
                    title_zh=title[0], title_en=title[1] if len(title) > 1 else title[0], due=body.due, issued_by=sess.user_id,
                    issued_at=int(time.time()))
        return {"code": code, "tid": tid, "cmid": cmid, "url": f"{base}/tasks/{tid}"}

    @app.post("/api/v1/courses/{courseid}/tasks/{code}/push")
    async def push(courseid: int, code: str, body: PushIn, sess: Annotated[Session, Depends(current)]):
        """Write the graded submissions into the course gradebook (the task sheet's Moodle assignment)."""
        await need_teacher(sess, courseid)
        row = store().one(courseid, code)
        if not row or not row["cmid"]:
            raise EngineError("not_found", "this task sheet was not issued in this course", 404)
        prog = next((t for t in await factory("GET", row["factory"], f"/api/tasks/course/{courseid}") if t["code"] == code), None)
        if not prog:
            raise EngineError("not_found", "the factory has no such task sheet", 404)
        tok = sess.moodle_token
        a = next((x for x in await state.moodle.assignments(tok, courseid, None) if int(x.get("cmid", 0)) == int(row["cmid"])), None)
        if not a:
            raise EngineError("not_found", "the task sheet's assignment is gone from the course", 404)
        spec = spec_of(row["book"], row["no"])
        rubric = spec.get("评分") or []
        done, failed = [], []
        for s in prog.get("submissions") or []:
            if s.get("total") is None or (s.get("pushed_at") and not body.again):
                continue
            items = (s.get("score_items") or [])
            lines = "".join(f"<li>{html.escape(x['项'][0])}：{v:g} / {x['分']:g}</li>" for x, v in zip(rubric, items))
            fb = (f"<p>工程任务单 {html.escape(code)}：{s['total']:g} 分</p>" + (f"<ul>{lines}</ul>" if lines else "")
                  + (f"<p>{html.escape(s.get('score_note') or '')}</p>" if s.get("score_note") else ""))
            try:
                await state.moodle.call(tok, "mod_assign_save_grade", None, assignmentid=a["id"], userid=int(s["author_uid"]),
                                        grade=float(s["total"]), attemptnumber=-1, addattempt=0, workflowstate="", applytoall=1,
                                        plugindata={"assignfeedbackcomments_editor": {"text": fb, "format": 1}})
                done.append(s["id"])
            except EngineError as e:
                failed.append({"name": s.get("name"), "error": e.message})
        if done:
            await factory("POST", row["factory"], f"/api/tasks/course/{courseid}/pushed", json={"submissions": done})
        return {"pushed": len(done), "failed": failed}
