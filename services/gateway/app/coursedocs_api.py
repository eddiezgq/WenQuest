"""老师用的网页文档（第 126 轮）：教案、实验指导书、通知……在问渠里写、AI 起草、发布进课程、导出 Word / PDF。

每份文档 = 课程里的一个 Moodle“页面”（经典界面、手机、备份、权限照常）+ 网关里的源内容（内容块，见 production/coursedoc.py）。
存储：<data_dir>/webdocs.db（和第 122 轮实验报告同一个库）
  cdocs     一份文档一行：课程、页面 cmid、模板、草稿 body、可见范围、发布到第几版
  cversions 每次“发布”存一份只读快照；学生看到的是最近发布的那一版（页面正文）
  cimages   文档里的图片（按内容的哈希存，课程页面经 /api/v1/webdoc-img/<哈希> 取）
“仅老师” = 页面对学生隐藏；“学生可见” = 页面显示。只有本课程的老师（能编辑课程的人）能看、能改源内容。
AI（第 121 轮 D-9：老师的文档 AI 写初稿，人改）：整份初稿、改某一块；结果先给老师看，老师点“采用”才进文档。
"""

import asyncio
import base64
import binascii
import hashlib
import io
import json
import sqlite3
import threading
import time
import zipfile
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends
from fastapi.responses import Response
from pydantic import BaseModel, Field

from . import materials as mt
from .moodle import EngineError
from .production import coursedoc
from .session import Session

DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MAX_IMAGE = 3_000_000
AUDIENCES = ("teachers", "students")


class Store:
    def __init__(self, folder: str):
        Path(folder).mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(Path(folder) / "webdocs.db"), check_same_thread=False, isolation_level=None)
        self.lock = threading.Lock()
        with self.lock:
            self.db.executescript("""
                CREATE TABLE IF NOT EXISTS cdocs (id INTEGER PRIMARY KEY AUTOINCREMENT, course INTEGER, cmid INTEGER, template TEXT,
                    body TEXT, audience TEXT, published INTEGER, created REAL, updated REAL, by INTEGER);
                CREATE INDEX IF NOT EXISTS cdocs_course ON cdocs (course);
                CREATE INDEX IF NOT EXISTS cdocs_cmid ON cdocs (cmid);
                CREATE TABLE IF NOT EXISTS cversions (doc INTEGER, ver INTEGER, at REAL, by INTEGER, audience TEXT, body TEXT,
                    PRIMARY KEY (doc, ver));
                CREATE TABLE IF NOT EXISTS cimages (hash TEXT PRIMARY KEY, mime TEXT, data BLOB, at REAL);
            """)

    @staticmethod
    def _row(r) -> dict | None:
        if not r:
            return None
        return {"id": r[0], "course": r[1], "cmid": r[2], "template": r[3], "body": json.loads(r[4]), "audience": r[5],
                "published": r[6], "created": r[7], "updated": r[8], "by": r[9]}

    def create(self, course: int, template: str, body: dict, by: int) -> int:
        now = time.time()
        with self.lock:
            cur = self.db.execute("INSERT INTO cdocs (course, cmid, template, body, audience, published, created, updated, by) "
                                  "VALUES (?,?,?,?,?,?,?,?,?)",
                                  (course, 0, template, json.dumps(body, ensure_ascii=False), "teachers", 0, now, now, by))
            return int(cur.lastrowid)

    def get(self, doc: int) -> dict | None:
        with self.lock:
            return self._row(self.db.execute("SELECT * FROM cdocs WHERE id=?", (doc,)).fetchone())

    def by_cmid(self, cmid: int) -> dict | None:
        with self.lock:
            return self._row(self.db.execute("SELECT * FROM cdocs WHERE cmid=? ORDER BY id DESC LIMIT 1", (cmid,)).fetchone())

    def of_course(self, course: int) -> list[dict]:
        with self.lock:
            return [self._row(r) for r in self.db.execute("SELECT * FROM cdocs WHERE course=? ORDER BY id", (course,)).fetchall()]

    def set(self, doc: int, **f: Any) -> None:
        if "body" in f:
            f["body"] = json.dumps(f["body"], ensure_ascii=False)
        cols = ", ".join(f"{k}=?" for k in f)
        with self.lock:
            self.db.execute(f"UPDATE cdocs SET {cols} WHERE id=?", (*f.values(), doc))

    def save(self, doc: int, body: dict, by: int) -> float:
        now = time.time()
        self.set(doc, body=body, updated=now, by=by)
        return now

    def forget_cmid(self, cmid: int) -> None:
        with self.lock:
            self.db.execute("UPDATE cdocs SET cmid=0 WHERE cmid=?", (cmid,))

    def snapshot(self, doc: int, body: dict, by: int, audience: str) -> int:
        with self.lock:
            n = self.db.execute("SELECT COALESCE(MAX(ver), 0) FROM cversions WHERE doc=?", (doc,)).fetchone()[0] + 1
            self.db.execute("INSERT INTO cversions VALUES (?,?,?,?,?,?)",
                            (doc, n, time.time(), by, audience, json.dumps(body, ensure_ascii=False)))
        return n

    def versions(self, doc: int) -> list[dict]:
        with self.lock:
            rows = self.db.execute("SELECT ver, at, by, audience FROM cversions WHERE doc=? ORDER BY ver", (doc,)).fetchall()
        return [{"ver": r[0], "at": r[1], "by": r[2], "audience": r[3]} for r in rows]

    def version(self, doc: int, ver: int) -> dict | None:
        with self.lock:
            r = self.db.execute("SELECT body, at, audience FROM cversions WHERE doc=? AND ver=?", (doc, ver)).fetchone()
        return {"body": json.loads(r[0]), "at": r[1], "audience": r[2]} if r else None

    def put_image(self, data: bytes, mime: str) -> str:
        h = hashlib.sha256(data).hexdigest()[:32]
        with self.lock:
            self.db.execute("INSERT OR IGNORE INTO cimages VALUES (?,?,?,?)", (h, mime, data, time.time()))
        return h

    def image(self, h: str) -> tuple[str, bytes] | None:
        with self.lock:
            r = self.db.execute("SELECT mime, data FROM cimages WHERE hash=?", (h,)).fetchone()
        return (r[0], bytes(r[1])) if r else None


def image_in(raw: bytes) -> tuple[bytes, str]:
    """A PNG or JPEG the teacher added: checked, and made at most 1600 px wide (Word and the page stay small)."""
    from PIL import Image
    try:
        im = Image.open(io.BytesIO(raw))
        im.load()
    except Exception:  # noqa: BLE001 - anything PIL cannot open is not a picture we can show
        raise EngineError("bad_image", "this is not a picture (PNG or JPEG)", 400)
    if im.format not in ("PNG", "JPEG"):
        raise EngineError("bad_image", "pictures must be PNG or JPEG", 400)
    if im.width <= 1600 and len(raw) <= 1_200_000:
        return raw, "image/png" if im.format == "PNG" else "image/jpeg"
    im.thumbnail((1600, 1600 * 4))
    out = io.BytesIO()
    if im.format == "PNG" and im.mode in ("RGBA", "LA", "P"):
        im.save(out, "PNG", optimize=True)
        return out.getvalue(), "image/png"
    im.convert("RGB").save(out, "JPEG", quality=85)
    return out.getvalue(), "image/jpeg"


class NewDoc(BaseModel):
    section: int = Field(ge=0, le=500)
    template: str = "blank"
    title: str = Field(min_length=1, max_length=200)


class DocIn(BaseModel):
    doc: dict
    base: float | None = None


class PublishIn(BaseModel):
    audience: str = "teachers"


class RestoreIn(BaseModel):
    ver: int


class ImageIn(BaseModel):
    data: str = Field(max_length=MAX_IMAGE * 4 // 3 + 100)       # base64 (a data: URL is fine)


class DraftIn(BaseModel):
    prompt: str = Field(min_length=2, max_length=4000)
    sources: list[int] = Field(default_factory=list, max_length=6)    # cmids of course items the AI should draw on


class BlockIn(BaseModel):
    index: int = Field(ge=0)
    action: str
    block: dict
    note: str = Field(default="", max_length=1000)


AI_WRITER = """你是大学老师的教学文件助手，替老师写教学文件的初稿，老师会再改。
- 用中文写；模板里小节标题带英文的（中英对照），段落和列表也给出对应的英文（en 字段），否则 en 留空。
- 严格按给定模板的小节顺序和标题写，不增删小节；表格保留表头，行可以增减。
- 内容具体、可直接用于课堂：写清教学内容、时间分配、学生活动；理工科课程优先用机器人的实际问题举例，再配一个生活中的例子。
- 公式写在 $ $ 之间（LaTeX）。
- 只依据老师的要求和给出的资料，不编造法规条款号、标准编号或具体统计数字；不确定的地方写“（请老师补充）”。
- 每个块用 t 表示种类：h 标题（level 1-3）、para 段落、list 列表（items）、table 表格（head、rows）、callout 提示框。"""

AI_EDITOR = """你是大学老师的教学文件助手。老师选了文档里的一块，要你按要求改写。
- 只返回改好的这一块，种类（t）不变；表格保留列数；公式写在 $ $ 之间。
- 不编造法规条款号、标准编号或具体统计数字。
- “译成中英对照”：中文放 text，英文放 en（列表每项各自给 en；表格把每格写成“中文 / English”）。"""

ACTIONS = {"rewrite": "改写得更清楚、更规范，意思不变", "expand": "扩写：补充细节、例子或步骤，长度约为原来的两倍",
           "shorten": "缩写：保留要点，长度约为原来的一半", "bilingual": "译成中英对照"}

BLOCK_SCHEMA = {"type": "object", "required": ["t"], "properties": {
    "t": {"type": "string", "enum": ["h", "para", "list", "table", "callout"]},
    "level": {"type": "integer"}, "text": {"type": "string"}, "en": {"type": "string"}, "ordered": {"type": "boolean"},
    "items": {"type": "array", "items": {"type": "object", "properties": {"text": {"type": "string"}, "en": {"type": "string"}}}},
    "caption": {"type": "string"}, "head": {"type": "array", "items": {"type": "string"}},
    "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}}}


def register(app, m) -> None:
    state = m.state

    def store() -> Store:
        if not getattr(state, "coursedocs", None):
            state.coursedocs = Store(state.settings.data_dir)
        return state.coursedocs

    def of_cmid(cmid: int) -> int | None:
        d = store().by_cmid(cmid) if cmid else None
        return d["id"] if d else None

    m.coursedoc_of_cmid = of_cmid            # edit_api / activity 页用：这个页面是不是网页文档
    m.coursedoc_store = store

    async def call(sess: Session, fn: str, **params: Any) -> Any:
        return await state.moodle.call(sess.moodle_token, fn, None, **params)

    async def need_teacher(sess: Session, course: int) -> None:
        if not await m.assign_tools.is_teacher(sess, course):
            raise EngineError("forbidden", "only the course's teachers", 403)

    async def doc_for(sess: Session, doc_id: int) -> dict:
        d = store().get(doc_id)
        if not d:
            raise EngineError("not_found", "no such document", 404)
        await need_teacher(sess, d["course"])
        return d

    def img_url(h: str) -> str:
        return f"{state.settings.public_url.rstrip('/')}/api/v1/webdoc-img/{h}"

    def image_bytes(h: str) -> bytes | None:
        x = store().image(h)
        return x[1] if x else None

    def name_of(doc: dict) -> str:
        """The page's (and file's) name. Every lesson plan is titled “<课程>教案”, so a plan is named by its 课题 instead."""
        if doc.get("template") == "plan":
            info = next((b for b in doc["blocks"] if b["t"] == "table" and b["head"][:1] == ["课题"] and b["rows"]), None)
            if info and info["rows"][0][0].strip():
                return f"{info['rows'][0][0].strip()} 教案"[:200]
        return (doc["title"][0] or doc["title"][1] or "文档").strip()[:200]

    def file_name(doc: dict) -> str:
        return name_of(doc).replace("/", "-").replace(" ", "")

    async def section_of(sess: Session, course: int) -> dict[int, int]:
        """cmid → section number, as the course is now (teachers move things)."""
        out = {}
        for s in await state.moodle.course_contents(sess.moodle_token, course, None):
            for mod in s.get("modules") or []:
                out[int(mod["id"])] = int(s.get("section") or 0)
        return out

    def state_of(d: dict) -> dict:
        return {"id": d["id"], "course": d["course"], "cmid": d["cmid"], "template": d["template"], "doc": d["body"],
                "audience": d["audience"], "published": d["published"], "updated": d["updated"],
                "versions": store().versions(d["id"]), "pdf": bool(state.settings.docs_url and state.settings.docs_jwt_secret)}

    # ---------------------------------------------------------------- create, read, save

    @app.post("/api/v1/courses/{courseid}/webdocs")
    async def create_doc(courseid: int, body: NewDoc, sess: Annotated[Session, Depends(m.current)]):
        """A new document in a chapter: the Moodle page (hidden from students until published) and its source."""
        await need_teacher(sess, courseid)
        if body.template not in coursedoc.TEMPLATES:
            raise EngineError("bad_template", "unknown template", 400)
        course = await state.moodle.course(sess.moodle_token, courseid, None)
        try:
            info = await state.moodle.site_info(sess.moodle_token)
            teacher = info.get("fullname") or ""
        except EngineError:
            teacher = ""
        doc = coursedoc.template(body.template, body.title, m.plain((course or {}).get("fullname"), "zh"), teacher)
        did = store().create(courseid, body.template, doc, sess.user_id)
        r = await call(sess, "local_wenquest_add_activities", courseid=courseid, section=body.section,
                       activities=[{"type": "page", "name": name_of(doc), "visible": 0, "intro": "",
                                    "content": coursedoc.to_html(doc, img_url)}])
        cmid = (r.get("cmids") or [0])[0]
        if not cmid:
            raise EngineError("create_failed", "the course page could not be made", 502)
        store().set(did, cmid=cmid)
        return state_of(store().get(did))

    @app.get("/api/v1/webdocs/{doc_id}")
    async def get_doc(doc_id: int, sess: Annotated[Session, Depends(m.current)]):
        return state_of(await doc_for(sess, doc_id))

    @app.get("/api/v1/webdocs/by-cmid/{cmid}")
    async def doc_by_cmid(cmid: int, sess: Annotated[Session, Depends(m.current)]):
        d = store().by_cmid(cmid)
        if not d:
            raise EngineError("not_found", "not a web document", 404)
        await need_teacher(sess, d["course"])
        return {"id": d["id"]}

    @app.put("/api/v1/webdocs/{doc_id}")
    async def save_doc(doc_id: int, body: DocIn, sess: Annotated[Session, Depends(m.current)]):
        d = await doc_for(sess, doc_id)
        if body.base is not None and d["updated"] > body.base + 0.001:
            raise EngineError("doc_changed", "this document was changed elsewhere; reload it first", 409)
        try:
            doc = coursedoc.clean(body.doc)
        except coursedoc.DocError as e:
            raise EngineError("bad_doc", str(e), 400)
        doc["template"] = d["template"]
        return {"updated": store().save(doc_id, doc, sess.user_id)}

    @app.post("/api/v1/webdocs/{doc_id}/images")
    async def add_image(doc_id: int, body: ImageIn, sess: Annotated[Session, Depends(m.current)]):
        await doc_for(sess, doc_id)
        s = body.data.split(",", 1)[1] if body.data.startswith("data:") else body.data
        try:
            raw = base64.b64decode(s, validate=True)
        except (binascii.Error, ValueError):
            raise EngineError("bad_image", "not a picture", 400)
        if len(raw) > MAX_IMAGE:
            raise EngineError("bad_image", "pictures are at most 3 MB", 400)
        data, mime = await asyncio.to_thread(image_in, raw)
        h = store().put_image(data, mime)
        return {"img": h, "url": img_url(h)}

    @app.get("/api/v1/webdoc-img/{h}")
    async def get_image(h: str):
        x = store().image(h) if coursedoc.IMG.match(h) else None
        if not x:
            raise EngineError("not_found", "no such picture", 404)
        return Response(x[1], media_type=x[0], headers={"Cache-Control": "public, max-age=31536000, immutable"})

    # ---------------------------------------------------------------- publish, versions

    @app.post("/api/v1/webdocs/{doc_id}/publish")
    async def publish(doc_id: int, body: PublishIn, sess: Annotated[Session, Depends(m.current)]):
        """The draft becomes the course page's content (a new read-only version); `audience` shows or hides it for students."""
        d = await doc_for(sess, doc_id)
        if body.audience not in AUDIENCES:
            raise EngineError("bad_audience", "teachers or students", 400)
        if not d["cmid"]:
            raise EngineError("page_gone", "the course page of this document was deleted", 409)
        doc = d["body"]
        try:
            await call(sess, "local_wenquest_edit_course", courseid=d["course"], action="content", cmid=d["cmid"],
                       name=name_of(doc), content=coursedoc.to_html(doc, img_url))
            await call(sess, "local_wenquest_edit_course", courseid=d["course"], action="module", cmid=d["cmid"],
                       visible=1 if body.audience == "students" else 0)
        except EngineError as e:
            if e.code in ("not_found", "invalid_input", "invalidrecord"):
                store().forget_cmid(d["cmid"])
                raise EngineError("page_gone", "the course page of this document was deleted", 409)
            raise
        ver = store().snapshot(doc_id, doc, sess.user_id, body.audience)
        store().set(doc_id, published=ver, audience=body.audience)
        return state_of(store().get(doc_id))

    @app.get("/api/v1/webdocs/{doc_id}/versions/{ver}")
    async def get_version(doc_id: int, ver: int, sess: Annotated[Session, Depends(m.current)]):
        await doc_for(sess, doc_id)
        v = store().version(doc_id, ver)
        if not v:
            raise EngineError("not_found", "no such version", 404)
        return {"ver": ver, "at": v["at"], "audience": v["audience"], "doc": v["body"]}

    @app.post("/api/v1/webdocs/{doc_id}/restore")
    async def restore(doc_id: int, body: RestoreIn, sess: Annotated[Session, Depends(m.current)]):
        """Make an earlier version the draft again (the course page changes when it is published)."""
        await doc_for(sess, doc_id)
        v = store().version(doc_id, body.ver)
        if not v:
            raise EngineError("not_found", "no such version", 404)
        store().save(doc_id, v["body"], sess.user_id)
        return state_of(store().get(doc_id))

    # ---------------------------------------------------------------- export

    def disposition(name: str) -> dict:
        from urllib.parse import quote
        return {"Content-Disposition": f"attachment; filename=\"doc.{name.rsplit('.', 1)[-1]}\"; filename*=UTF-8''{quote(name)}",
                "Cache-Control": "no-store"}

    async def render(doc: dict, fmt: str) -> tuple[bytes, str]:
        data = await asyncio.to_thread(coursedoc.to_docx, doc, image_bytes)
        if fmt == "pdf":
            return await m.webdocs_pdf(data, file_name(doc)), "pdf"
        return data, "docx"

    @app.get("/api/v1/webdocs/{doc_id}/export")
    async def export(doc_id: int, sess: Annotated[Session, Depends(m.current)], fmt: str = "docx", ver: int = 0):
        d = await doc_for(sess, doc_id)
        doc = d["body"]
        if ver:
            v = store().version(doc_id, ver)
            if not v:
                raise EngineError("not_found", "no such version", 404)
            doc = v["body"]
        data, ext = await render(doc, "pdf" if fmt == "pdf" else "docx")
        return Response(data, media_type="application/pdf" if ext == "pdf" else DOCX, headers=disposition(f"{file_name(doc)}.{ext}"))

    @app.get("/api/v1/courses/{courseid}/webdocs")
    async def list_docs(courseid: int, sess: Annotated[Session, Depends(m.current)], section: int = -1, template: str = ""):
        """The course's documents (with their chapter as the course is now); deleted pages left out."""
        await need_teacher(sess, courseid)
        where = await section_of(sess, courseid)
        out = []
        for d in store().of_course(courseid):
            if d["cmid"] not in where:
                continue
            if (section >= 0 and where[d["cmid"]] != section) or (template and d["template"] != template):
                continue
            out.append({"id": d["id"], "cmid": d["cmid"], "section": where[d["cmid"]], "template": d["template"],
                        "title": d["body"]["title"], "audience": d["audience"], "published": d["published"], "updated": d["updated"]})
        return {"docs": out}

    @app.get("/api/v1/courses/{courseid}/webdocs.zip")
    async def export_many(courseid: int, sess: Annotated[Session, Depends(m.current)], section: int = -1, template: str = "",
                          fmt: str = "docx"):
        """Several documents at once (e.g. a chapter's lesson plans), each as it is now, in a zip."""
        listed = (await list_docs(courseid, sess, section, template))["docs"]
        if not listed:
            raise EngineError("not_found", "no documents here", 404)
        buf = io.BytesIO()
        seen: set[str] = set()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for x in listed[:80]:
                doc = store().get(x["id"])["body"]
                data, ext = await render(doc, "pdf" if fmt == "pdf" else "docx")
                name = file_name(doc)
                while f"{name}.{ext}" in seen:
                    name += "-2"
                seen.add(f"{name}.{ext}")
                z.writestr(f"{name}.{ext}", data)
        label = {"plan": "教案", "guide": "实验指导书", "notice": "通知"}.get(template, "文档")
        return Response(buf.getvalue(), media_type="application/zip", headers=disposition(f"{label}{'-第' + str(section) + '章' if section >= 0 else ''}.zip"))

    # ---------------------------------------------------------------- AI

    async def sources(sess: Session, course: int) -> list[dict]:
        """What in the course the AI may draw on: pages and files with text (教材、大纲、讲义……)."""
        out = []
        for s in await state.moodle.course_contents(sess.moodle_token, course, None):
            for mod in s.get("modules") or []:
                if mod.get("modname") == "page" or (mod.get("modname") == "resource" and any(
                        str(f.get("filename", "")).lower().rsplit(".", 1)[-1] in ("docx", "doc", "pdf", "pptx", "txt", "md", "wps")
                        for f in mod.get("contents") or [])):
                    out.append({"cmid": int(mod["id"]), "name": m.plain(mod.get("name"), sess.lang),
                                "section": m.plain(s.get("name"), sess.lang), "type": mod["modname"]})
        return out

    @app.get("/api/v1/courses/{courseid}/ai-sources")
    async def ai_sources(courseid: int, sess: Annotated[Session, Depends(m.current)]):
        await need_teacher(sess, courseid)
        return {"sources": (await sources(sess, courseid))[:200]}

    async def source_text(sess: Session, course: int, cmids: list[int]) -> str:
        if not cmids:
            return ""
        want = set(cmids)
        parts = []
        pages = None
        for s in await state.moodle.course_contents(sess.moodle_token, course, None):
            for mod in s.get("modules") or []:
                if int(mod["id"]) not in want:
                    continue
                name = m.plain(mod.get("name"), "zh")
                try:
                    if mod.get("modname") == "page":
                        pages = pages if pages is not None else await state.moodle.pages(sess.moodle_token, course, None)
                        p = next((x for x in pages if x.get("coursemodule") == mod["id"]), None)
                        txt = m.plain((p or {}).get("content"), "zh")
                    else:
                        f = next(x for x in mod.get("contents") or [] if x.get("type") == "file")
                        data = (await state.moodle.fetch_file(sess.moodle_token, f["fileurl"])).content
                        txt, _ = await asyncio.to_thread(mt.extract, f["filename"], data)
                        txt = mt.clean(txt)
                except Exception as e:  # noqa: BLE001 - an unreadable source is skipped, the draft still comes
                    txt = f"（读不出：{type(e).__name__}）"
                parts.append(f"【{name}】\n{txt[:20000]}")
        return "\n\n".join(parts)[:60000]

    @app.post("/api/v1/webdocs/{doc_id}/ai-draft")
    async def ai_draft(doc_id: int, body: DraftIn, sess: Annotated[Session, Depends(m.current)]):
        """A whole first draft in the document's template; returned to the teacher, not saved until they take it."""
        d = await doc_for(sess, doc_id)
        cur = d["body"]
        course = await state.moodle.course(sess.moodle_token, d["course"], None)
        skeleton = cur          # the document as it is now (the template's sections, or the teacher's own) is the structure to fill
        src = await source_text(sess, d["course"], body.sources)
        prompt = (f"课程：{m.plain((course or {}).get('fullname'), 'zh')}\n文档：{cur['title'][0]}"
                  + (f"（{cur['sub']}）" if cur.get("sub") else "") + f"（模板：{d['template']}）\n"
                  f"老师的要求：{body.prompt}\n\n模板（按这个结构写，JSON）：\n"
                  f"{json.dumps(skeleton['blocks'], ensure_ascii=False)}\n\n"
                  + (f"可依据的课程资料：\n{src}\n" if src else "（没有选资料，按要求和学科常识写。）\n"))
        schema = {"type": "object", "required": ["blocks"], "properties": {
            "title": {"type": "string"}, "sub": {"type": "string"}, "blocks": {"type": "array", "items": BLOCK_SCHEMA}}}

        def fake() -> dict:
            out = json.loads(json.dumps(skeleton))
            for b in out["blocks"]:
                if b["t"] == "para" and not b["text"]:
                    b["text"] = f"（AI 初稿）{body.prompt[:40]}"
                if b["t"] == "list":
                    for it in b["items"]:
                        it["text"] = (it["text"] or "") + "（AI 初稿）"
            return out
        out = await state.ai.json(system=AI_WRITER, prompt=prompt, schema=schema, max_tokens=12000, fake=fake)
        try:
            doc = coursedoc.clean({"template": d["template"], "title": [str(out.get("title") or cur["title"][0]), cur["title"][1]],
                                   "sub": out.get("sub") if isinstance(out.get("sub"), str) and out.get("sub") else cur.get("sub", ""),
                                   "blocks": out.get("blocks") or []})
        except coursedoc.DocError:
            raise EngineError("ai_failed", "the AI's draft could not be used; try again", 502)
        if not doc["blocks"]:
            raise EngineError("ai_failed", "the AI returned an empty draft; try again", 502)
        return {"doc": doc}

    @app.post("/api/v1/webdocs/{doc_id}/ai-block")
    async def ai_block(doc_id: int, body: BlockIn, sess: Annotated[Session, Depends(m.current)]):
        """One block rewritten / expanded / shortened / made bilingual; the teacher takes it or not."""
        d = await doc_for(sess, doc_id)
        if body.action not in ACTIONS:
            raise EngineError("bad_action", "unknown action", 400)
        try:
            blk = coursedoc.clean({"blocks": [body.block]})["blocks"]
        except coursedoc.DocError:
            blk = []
        if not blk or blk[0]["t"] not in ("h", "para", "list", "table", "callout"):
            raise EngineError("bad_block", "this kind of block cannot be rewritten", 400)
        blk = blk[0]
        context = coursedoc.plain(d["body"])[:12000]
        prompt = (f"要求：{ACTIONS[body.action]}" + (f"；老师补充：{body.note}" if body.note else "")
                  + f"\n\n要改的块（JSON）：\n{json.dumps(blk, ensure_ascii=False)}\n\n整份文档（供参考）：\n{context}")

        def fake() -> dict:
            x = json.loads(json.dumps(blk))
            if x["t"] in ("para", "callout", "h"):
                x["text"] = f"{x.get('text', '')}（{body.action}）"
                if body.action == "bilingual":
                    x["en"] = "(English) " + x.get("text", "")
            elif x["t"] == "list":
                for it in x["items"]:
                    it["text"] += f"（{body.action}）"
            return x
        out = await state.ai.json(system=AI_EDITOR, prompt=prompt, schema=BLOCK_SCHEMA, max_tokens=6000, fake=fake)
        try:
            new = coursedoc.clean({"blocks": [{**(out or {}), "t": blk["t"]}]})["blocks"]
        except coursedoc.DocError:
            new = []
        if not new:
            raise EngineError("ai_failed", "the AI's answer could not be used; try again", 502)
        new = new[0]
        if blk["t"] == "table":
            new["id"] = blk["id"]
        if blk["t"] == "h":
            new["level"] = blk["level"]
        return {"block": new}

    # ---------------------------------------------------------------- the AI course workshop (studio)

    def adopt(course: int, cmid: int, doc: dict, audience: str, by: int) -> int:
        """A document the workshop already put into the course as a page: keep its source so teachers edit it here."""
        doc = coursedoc.clean(doc)
        did = store().create(course, doc["template"], doc, by)
        ver = store().snapshot(did, doc, by, audience)
        store().set(did, cmid=cmid, audience=audience, published=ver)
        return did

    m.coursedoc_adopt = adopt
    m.coursedoc_html = lambda doc: coursedoc.to_html(coursedoc.clean(doc), img_url)
