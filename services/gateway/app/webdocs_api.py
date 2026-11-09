"""网页实验报告（第 122 轮）：学生在问渠页面上写实验报告，提交时交进老师关联的 Moodle 作业。

模板：教材构建时和 Word 模板一起生成的 <教材>/lab/labN_M-report.json（GPU 实验在 gpulab/）。
存储：<data_dir>/webdocs.db
  reports  一个学生一个实验一份：草稿 body（只存学生能改的部分，见 webdoc.merge）、状态、当前版本号
  versions 每次提交存一份只读快照（版本号、时间、交到哪个作业）
  links    老师把作业关联到某本教材的某个实验
提交 = 生成 Word 交进作业（作业开了在线文本的同时放一份正文），再调 Moodle 的“提交批改”。
老师“重新开放”或“退回草稿”后，学生下次打开时报告回到草稿，在新版本上改；旧版本留着可看。
"""

import asyncio
import base64
import hashlib
import hmac
import io
import json
import re
import sqlite3
import threading
import time
import zipfile
from pathlib import Path
from typing import Annotated, Any

from cryptography.fernet import InvalidToken
from fastapi import Depends
from fastapi.responses import Response
from pydantic import BaseModel, Field

from .moodle import EngineError
from .production import webdoc
from .session import Session

BOOK = re.compile(r"^[a-z][a-z0-9_-]{0,40}$")
LAB = re.compile(r"^(\d{1,3})_(\d{1,3})$")
DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
TMP_TTL = 300


class Store:
    def __init__(self, folder: str):
        Path(folder).mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(Path(folder) / "webdocs.db"), check_same_thread=False, isolation_level=None)
        self.lock = threading.Lock()
        with self.lock:
            self.db.executescript("""
                CREATE TABLE IF NOT EXISTS reports (user INTEGER, book TEXT, lab TEXT, status TEXT, version INTEGER,
                    cmid INTEGER, body TEXT, updated REAL, PRIMARY KEY (user, book, lab));
                CREATE TABLE IF NOT EXISTS versions (user INTEGER, book TEXT, lab TEXT, ver INTEGER, at REAL, cmid INTEGER,
                    body TEXT, PRIMARY KEY (user, book, lab, ver));
                CREATE TABLE IF NOT EXISTS links (cmid INTEGER PRIMARY KEY, course INTEGER, book TEXT, lab TEXT, by INTEGER, at REAL);
                CREATE INDEX IF NOT EXISTS links_lab ON links (book, lab);
            """)

    def get(self, user: int, book: str, lab: str) -> dict | None:
        with self.lock:
            r = self.db.execute("SELECT status, version, cmid, body, updated FROM reports WHERE user=? AND book=? AND lab=?",
                                (user, book, lab)).fetchone()
        if not r:
            return None
        return {"status": r[0], "version": r[1], "cmid": r[2], "body": json.loads(r[3]), "updated": r[4]}

    def save(self, user: int, book: str, lab: str, body: dict, status: str = "draft", version: int | None = None,
             cmid: int | None = None) -> float:
        now = time.time()
        cur = self.get(user, book, lab)
        ver = version if version is not None else (cur["version"] if cur else 0)
        cm = cmid if cmid is not None else (cur["cmid"] if cur else None)
        with self.lock:
            self.db.execute("INSERT OR REPLACE INTO reports VALUES (?,?,?,?,?,?,?,?)",
                            (user, book, lab, status, ver, cm, json.dumps(body, ensure_ascii=False), now))
        return now

    def set_status(self, user: int, book: str, lab: str, status: str) -> None:
        with self.lock:
            self.db.execute("UPDATE reports SET status=? WHERE user=? AND book=? AND lab=?", (status, user, book, lab))

    def snapshot(self, user: int, book: str, lab: str, body: dict, cmid: int) -> int:
        with self.lock:
            n = self.db.execute("SELECT COALESCE(MAX(ver), 0) FROM versions WHERE user=? AND book=? AND lab=?",
                                (user, book, lab)).fetchone()[0] + 1
            self.db.execute("INSERT INTO versions VALUES (?,?,?,?,?,?,?)",
                            (user, book, lab, n, time.time(), cmid, json.dumps(body, ensure_ascii=False)))
        return n

    def versions(self, user: int, book: str, lab: str) -> list[dict]:
        with self.lock:
            rows = self.db.execute("SELECT ver, at, cmid FROM versions WHERE user=? AND book=? AND lab=? ORDER BY ver",
                                   (user, book, lab)).fetchall()
        return [{"ver": r[0], "at": r[1], "cmid": r[2]} for r in rows]

    def version(self, user: int, book: str, lab: str, ver: int) -> dict | None:
        with self.lock:
            r = self.db.execute("SELECT body, at, cmid FROM versions WHERE user=? AND book=? AND lab=? AND ver=?",
                                (user, book, lab, ver)).fetchone()
        return {"body": json.loads(r[0]), "at": r[1], "cmid": r[2]} if r else None

    def latest_for(self, cmid: int, user: int) -> dict | None:
        """The last version a student handed in to this assignment."""
        with self.lock:
            r = self.db.execute("SELECT book, lab, ver, at, body FROM versions WHERE cmid=? AND user=? ORDER BY at DESC LIMIT 1",
                                (cmid, user)).fetchone()
        return {"book": r[0], "lab": r[1], "ver": r[2], "at": r[3], "body": json.loads(r[4])} if r else None

    def link(self, cmid: int, course: int, book: str, lab: str, by: int) -> None:
        with self.lock:
            self.db.execute("INSERT OR REPLACE INTO links VALUES (?,?,?,?,?,?)", (cmid, course, book, lab, by, time.time()))

    def unlink(self, cmid: int) -> None:
        with self.lock:
            self.db.execute("DELETE FROM links WHERE cmid=?", (cmid,))

    def link_of(self, cmid: int) -> dict | None:
        with self.lock:
            r = self.db.execute("SELECT course, book, lab FROM links WHERE cmid=?", (cmid,)).fetchone()
        return {"course": r[0], "book": r[1], "lab": r[2]} if r else None

    def links_for(self, book: str, lab: str) -> list[int]:
        with self.lock:
            return [r[0] for r in self.db.execute("SELECT cmid FROM links WHERE book=? AND lab=?", (book, lab)).fetchall()]


class DocIn(BaseModel):
    doc: dict
    base: float | None = None      # the `updated` the page started from: a newer save elsewhere is not overwritten


class SubmitIn(BaseModel):
    cmid: int


class LinkIn(BaseModel):
    book: str = Field(max_length=41)
    lab: str = Field(max_length=9)


def jwt_hs256(payload: dict, secret: str) -> str:
    """A JSON Web Token signed with HS256 (all OnlyOffice needs; no extra library)."""
    def b64(b: bytes) -> str:
        return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
    head = b64(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    body = b64(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(secret.encode(), f"{head}.{body}".encode(), hashlib.sha256).digest()
    return f"{head}.{body}.{b64(sig)}"


def register(app, m) -> None:
    state = m.state
    tmp: dict[str, tuple[float, bytes]] = {}      # Word files waiting for OnlyOffice to fetch them (PDF export)

    def store() -> Store:
        if not getattr(state, "webdocs", None):
            state.webdocs = Store(state.settings.data_dir)
        return state.webdocs

    def tools():
        return m.assign_tools

    def root() -> Path:
        return Path(state.settings.textbook_dir)

    def template(book: str, lab: str) -> dict:
        if not (BOOK.match(book) and LAB.match(lab)):
            raise EngineError("not_found", "no such lab", 404)
        for sub in ("lab", "gpulab"):
            p = root() / book / sub / f"lab{lab}-report.json"
            if p.exists():
                return json.loads(p.read_text(encoding="utf-8"))
        raise EngineError("not_found", "this lab has no online report yet", 404)

    def lab_url(book: str, lab: str, tpl: dict, lang: str) -> str | None:
        ch, k = LAB.match(lab).groups()
        if tpl.get("gpu") or not (root() / book / "lab" / f"ch{int(ch):02d}.html").exists():
            return None
        tok = state.codec.fernet.encrypt(json.dumps({"b": book, "c": str(int(ch))}).encode()).decode()
        return f"{state.settings.public_url.rstrip('/')}/api/v1/textbook-lab/{tok}#lab-{int(ch)}-{int(k)}-{'en' if lang == 'en' else 'zh'}"

    async def fresh_doc(sess: Session, book: str, lab: str, tpl: dict) -> dict:
        d = webdoc.blank(tpl)      # {{名}} cells start empty; a GPU lab's are filled from the student's returned results below
        try:
            info = await state.moodle.site_info(sess.moodle_token)
            name = info.get("fullname") or ""
        except EngineError:
            name = ""
        for b in d["blocks"]:
            if b["t"] == "fields":
                for it in b["items"]:
                    if it["k"] == "name":
                        it["v"] = name
                    elif it["k"] == "date":
                        it["v"] = time.strftime("%Y-%m-%d")
        if tpl.get("gpu"):
            res = m.gpulab_store().results(sess.user_id, book, lab.replace("_", ".")) if hasattr(m, "gpulab_store") else []
            if res:
                webdoc.fill(d, tpl, res[-1]["vals"])
        return d

    async def assignments_for(sess: Session, book: str, lab: str) -> list[dict]:
        out = []
        for cmid in store().links_for(book, lab):
            try:
                cm, a = await tools().assignment(sess, cmid, sess.lang)
            except EngineError:
                continue      # not in this course, or the assignment is gone
            out.append({"cmid": cmid, "name": m.plain(a.get("name"), sess.lang), "course": int(cm["course"]),
                        "due": a.get("duedate") or 0})
        return out

    async def sync_status(sess: Session, book: str, lab: str, cur: dict) -> dict:
        """A submitted report goes back to draft when the teacher reopened the assignment or reverted it to draft."""
        if cur["status"] != "submitted" or not cur.get("cmid"):
            return cur
        try:
            cm, a = await tools().assignment(sess, cur["cmid"], None)
            st = await tools().call(sess, "mod_assign_get_submission_status", None, assignid=a["id"])
        except EngineError:
            return cur
        view = tools().submission_view(st, sess.moodle_token, None)
        if view["can_edit"] and view["status"] in ("reopened", "draft", "new"):
            store().set_status(sess.user_id, book, lab, "draft")
            cur["status"] = "draft"
        return cur

    def doc_of(tpl: dict, body: dict) -> dict:
        return webdoc.merge(tpl, body)

    @app.get("/api/v1/reports/{book}/{lab}")
    async def get_report(book: str, lab: str, sess: Annotated[Session, Depends(m.current)]):
        """The student's report (a fresh one from the template the first time), where it can be handed in, its versions."""
        tpl = template(book, lab)
        cur = store().get(sess.user_id, book, lab)
        if cur:
            cur = await sync_status(sess, book, lab, cur)
            doc = doc_of(tpl, cur["body"])
        else:
            doc = await fresh_doc(sess, book, lab, tpl)
        return {"book": book, "lab": lab, "doc": doc, "status": cur["status"] if cur else "new",
                "updated": cur["updated"] if cur else 0, "cmid": cur["cmid"] if cur else None,
                "versions": store().versions(sess.user_id, book, lab),
                "assignments": await assignments_for(sess, book, lab),
                "lab_url": lab_url(book, lab, tpl, sess.lang), "slots": webdoc.placeholders(tpl),
                "editable": {b["id"]: [[webdoc.editable_cell(str(c)) for c in r] for r in b["rows"]]
                             for b in tpl["blocks"] if b["t"] == "table"},
                "pdf": bool(state.settings.docs_url and state.settings.docs_jwt_secret)}

    @app.put("/api/v1/reports/{book}/{lab}")
    async def save_report(book: str, lab: str, body: DocIn, sess: Annotated[Session, Depends(m.current)]):
        tpl = template(book, lab)
        cur = store().get(sess.user_id, book, lab)
        if cur and cur["status"] == "submitted":
            raise EngineError("report_submitted", "this report has been handed in; it can be changed after the teacher reopens it", 409)
        if cur and body.base is not None and cur["updated"] > body.base + 0.001:
            raise EngineError("report_changed", "this report was changed in another window; reload it first", 409)
        try:
            doc = doc_of(tpl, body.doc)
        except webdoc.DocError as e:
            raise EngineError("bad_report", str(e), 400)
        return {"updated": store().save(sess.user_id, book, lab, doc), "status": "draft"}

    @app.get("/api/v1/reports/{book}/{lab}/versions/{ver}")
    async def report_version(book: str, lab: str, ver: int, sess: Annotated[Session, Depends(m.current)]):
        v = store().version(sess.user_id, book, lab, ver)
        if not v:
            raise EngineError("not_found", "no such version", 404)
        return {"ver": ver, "at": v["at"], "cmid": v["cmid"], "doc": v["body"]}

    def file_name(doc: dict, who: str = "") -> str:
        t0 = (doc.get("title") or [""])[0]
        if not t0.startswith("实验"):
            t0 = f"实验{doc.get('lab', '')}-{t0}"
        return f"{t0}-实验报告{('-' + who) if who else ''}".replace("/", "-").replace(" ", "")

    async def to_pdf(data: bytes, name: str) -> bytes:
        """Word → PDF by the online documents service (第 121 轮), which fetches the file from this gateway."""
        s = state.settings
        if not (s.docs_url and s.docs_jwt_secret):
            raise EngineError("pdf_unavailable", "PDF export is not set up on this server", 503)
        now = time.time()
        for k in [k for k, (t, _) in tmp.items() if t < now - TMP_TTL]:
            tmp.pop(k, None)
        key = hashlib.sha256(data).hexdigest()[:32]
        tmp[key] = (now, data)
        tok = state.codec.fernet.encrypt(key.encode()).decode()
        payload = {"async": False, "filetype": "docx", "outputtype": "pdf", "key": key, "title": f"{key}.docx",
                   "url": f"{s.internal_url.rstrip('/')}/api/v1/webdocs-tmp/{tok}"}
        payload["token"] = jwt_hs256(payload, s.docs_jwt_secret)
        base = s.docs_url.rstrip("/")
        try:
            r = await state.http.post(f"{base}/converter", json=payload, timeout=120,
                                      headers={"Accept": "application/json",
                                               "Authorization": "Bearer " + jwt_hs256({"payload": payload}, s.docs_jwt_secret)})
            out = r.json() if r.status_code == 200 else {}
            if not out.get("endConvert") or not out.get("fileUrl"):
                raise EngineError("pdf_failed", f"conversion error {out.get('error', r.status_code)}", 502)
            url = out["fileUrl"]
            if not url.startswith(base + "/"):       # named by its public address (learn.<域名>/docs/…): fetch it inside
                url = base + re.sub(r"^/docs(?=/)", "", re.sub(r"^https?://[^/]+", "", url))
            f = await state.http.get(url, timeout=60)
            if f.status_code != 200 or not f.content.startswith(b"%PDF"):
                raise EngineError("pdf_failed", f"could not fetch the PDF ({f.status_code})", 502)
            return f.content
        finally:
            tmp.pop(key, None)

    @app.get("/api/v1/webdocs-tmp/{signed}")
    async def tmp_file(signed: str):
        try:
            key = state.codec.fernet.decrypt(signed.encode(), ttl=TMP_TTL).decode()
        except (InvalidToken, ValueError):
            raise EngineError("link_expired", "link expired", 410)
        hit = tmp.get(key)
        if not hit:
            raise EngineError("not_found", "no such file", 404)
        return Response(hit[1], media_type=DOCX)

    async def export(doc: dict, fmt: str, name: str) -> Response:
        data = await asyncio.to_thread(webdoc.to_docx, doc)
        if fmt == "pdf":
            data = await to_pdf(data, name)
            return Response(data, media_type="application/pdf", headers=disposition(name + ".pdf"))
        return Response(data, media_type=DOCX, headers=disposition(name + ".docx"))

    def disposition(name: str) -> dict:
        from urllib.parse import quote
        return {"Content-Disposition": f"attachment; filename=\"report.{name.rsplit('.', 1)[-1]}\"; filename*=UTF-8''{quote(name)}",
                "Cache-Control": "no-store"}

    @app.get("/api/v1/reports/{book}/{lab}/export")
    async def export_report(book: str, lab: str, sess: Annotated[Session, Depends(m.current)], fmt: str = "docx", ver: int = 0):
        tpl = template(book, lab)
        if ver:
            v = store().version(sess.user_id, book, lab, ver)
            if not v:
                raise EngineError("not_found", "no such version", 404)
            doc = v["body"]
        else:
            cur = store().get(sess.user_id, book, lab)
            doc = doc_of(tpl, cur["body"]) if cur else await fresh_doc(sess, book, lab, tpl)
        return await export(doc, "pdf" if fmt == "pdf" else "docx", file_name(doc))

    @app.post("/api/v1/reports/{book}/{lab}/submit")
    async def submit_report(book: str, lab: str, body: SubmitIn, sess: Annotated[Session, Depends(m.current)]):
        """Hand the report in to a linked assignment: the Word file (and the text, if the assignment takes text)."""
        tpl = template(book, lab)
        link = store().link_of(body.cmid)
        if not link or (link["book"], link["lab"]) != (book, lab):
            raise EngineError("not_linked", "this assignment is not for this lab", 400)
        cur = store().get(sess.user_id, book, lab)
        if not cur:
            raise EngineError("report_empty", "write the report first", 400)
        cur = await sync_status(sess, book, lab, cur)
        if cur["status"] == "submitted":
            raise EngineError("report_submitted", "already handed in", 409)
        doc = doc_of(tpl, cur["body"])
        if webdoc.plain_words(doc) < 20:
            raise EngineError("report_empty", "the report is almost empty", 400)
        T = tools()
        cm, a = await T.assignment(sess, body.cmid, None)
        cfg = T.assign_config(a)
        st = await T.call(sess, "mod_assign_get_submission_status", None, assignid=a["id"])
        if not T.submission_view(st, sess.moodle_token, None)["can_edit"]:
            raise EngineError("submission_closed", "this assignment no longer accepts changes", 409)
        if not (cfg["files"] or cfg["text"]):
            raise EngineError("submission_refused", "this assignment takes neither files nor text", 409)
        plugindata: dict[str, Any] = {}
        if cfg["files"]:
            data = await asyncio.to_thread(webdoc.to_docx, doc)
            plugindata["files_filemanager"] = await T.build_draft(sess, [], [(file_name(doc) + ".docx", data)])
        if cfg["text"]:
            plugindata["onlinetext_editor"] = {"text": webdoc.to_html(doc), "format": 1, "itemid": 0}
        r = await T.call(sess, "mod_assign_save_submission", None, assignmentid=a["id"], plugindata=plugindata)
        if r:
            w = r[0] if isinstance(r, list) else r
            raise EngineError("submission_refused", str(w.get("item") or w.get("message") or w)[:200], 409)
        if cfg["drafts"]:
            r = await T.call(sess, "mod_assign_submit_for_grading", None, assignmentid=a["id"], acceptsubmissionstatement=1)
            if r:
                w = r[0] if isinstance(r, list) else r
                raise EngineError("submission_refused", str(w.get("message") or w.get("item") or w)[:200], 409)
        ver = store().snapshot(sess.user_id, book, lab, doc, body.cmid)
        store().save(sess.user_id, book, lab, doc, status="submitted", version=ver, cmid=body.cmid)
        return {"status": "submitted", "version": ver, "versions": store().versions(sess.user_id, book, lab)}

    # ---------------------------------------------------------------- teachers

    async def teacher_of(sess: Session, cmid: int) -> tuple[dict, dict]:
        cm, a = await tools().assignment(sess, cmid, sess.lang)
        if not await tools().is_teacher(sess, int(cm["course"])):
            raise EngineError("forbidden", "only the course's teachers", 403)
        return cm, a

    @app.get("/api/v1/report-labs")
    async def report_labs(sess: Annotated[Session, Depends(m.current)]):
        """Every lab with an online report, by textbook (the teacher picks one when linking an assignment)."""
        out = []
        if root().is_dir():
            for d in sorted(root().iterdir()):
                idx = d / "web" / "index.json"
                if not (BOOK.match(d.name) and idx.exists()):
                    continue
                labs = []
                for sub in ("lab", "gpulab"):
                    for p in (d / sub).glob("lab*-report.json") if (d / sub).is_dir() else []:
                        try:
                            t = json.loads(p.read_text(encoding="utf-8"))
                        except ValueError:
                            continue
                        labs.append({"lab": p.name[3:-len("-report.json")], "no": t.get("lab", ""), "title": t.get("title")})
                labs.sort(key=lambda x: [int(n) for n in x["lab"].split("_")])
                if labs:
                    out.append({"book": d.name, "title": json.loads(idx.read_text(encoding="utf-8")).get("title", d.name), "labs": labs})
        return {"books": out}

    @app.get("/api/v1/assignments/{cmid}/lab-link")
    async def get_link(cmid: int, sess: Annotated[Session, Depends(m.current)]):
        link = store().link_of(cmid)
        if not link:
            return {"linked": False}
        try:
            title = template(link["book"], link["lab"]).get("title")
        except EngineError:
            title = None
        return {"linked": True, "book": link["book"], "lab": link["lab"], "title": title}

    @app.put("/api/v1/assignments/{cmid}/lab-link")
    async def put_link(cmid: int, body: LinkIn, sess: Annotated[Session, Depends(m.current)]):
        cm, _ = await teacher_of(sess, cmid)
        template(body.book, body.lab)      # must exist
        store().link(cmid, int(cm["course"]), body.book, body.lab, sess.user_id)
        return await get_link(cmid, sess)

    @app.delete("/api/v1/assignments/{cmid}/lab-link")
    async def delete_link(cmid: int, sess: Annotated[Session, Depends(m.current)]):
        await teacher_of(sess, cmid)
        store().unlink(cmid)
        return {"linked": False}

    @app.get("/api/v1/assignments/{cmid}/reports/{userid}")
    async def student_report(cmid: int, userid: int, sess: Annotated[Session, Depends(m.current)], ver: int = 0):
        """The online report a student handed in to this assignment (the teacher's view); `ver` an earlier version of it."""
        await teacher_of(sess, cmid)
        v = store().latest_for(cmid, userid)
        if not v:
            raise EngineError("not_found", "no online report", 404)
        if ver and ver != v["ver"]:
            old = store().version(userid, v["book"], v["lab"], ver)
            if not old or old["cmid"] != cmid:
                raise EngineError("not_found", "no such version", 404)
            v = {**v, "ver": ver, "at": old["at"], "body": old["body"]}
        return {"ver": v["ver"], "at": v["at"], "doc": v["body"],
                "versions": [x for x in store().versions(userid, v["book"], v["lab"]) if x["cmid"] == cmid]}

    @app.get("/api/v1/assignments/{cmid}/reports.zip")
    async def class_reports(cmid: int, sess: Annotated[Session, Depends(m.current)], fmt: str = "docx"):
        """Every student's last online report for this assignment, one file each, in a zip."""
        _, a = await teacher_of(sess, cmid)
        people = await tools().call(sess, "mod_assign_list_participants", None, assignid=a["id"], groupid=0, filter="",
                                    skip=0, limit=0, onlyids=0, includeenrolments=0, tablesort=0)
        buf = io.BytesIO()
        n = 0
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for p in people:
                v = store().latest_for(cmid, int(p["id"]))
                if not v:
                    continue
                who = (p.get("fullname") or str(p["id"])).replace("/", "-")
                data = await asyncio.to_thread(webdoc.to_docx, v["body"])
                ext = "docx"
                if fmt == "pdf":
                    data, ext = await to_pdf(data, who), "pdf"
                z.writestr(f"{who}-{file_name(v['body'])}.{ext}", data)
                n += 1
        if not n:
            raise EngineError("not_found", "no online reports have been handed in yet", 404)
        return Response(buf.getvalue(), media_type="application/zip",
                        headers=disposition(f"{m.plain(a.get('name'), sess.lang)}-实验报告.zip"))
