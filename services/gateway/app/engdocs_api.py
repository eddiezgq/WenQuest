"""工程师的网页文档（第 128 轮，阶段 C1）：缝纫机设计软件的计算书、调机卡“存为网页文档”；数字工厂工艺卡的 PDF。

- 计算书 / 调机卡：由设计计算生成 Word（和“导出”的同一份），拆成内容块（production/docx_blocks.py），这些块标 lock：
  网页上只读，保存时以生成的为准（数字不能手改，第 128 轮 Q3）；工程师自己加的块（说明、照片、表格）随便改。
  记下生成时的设计参数指纹；关联的机型项目改过后提示“重新生成”，重新生成时换掉计算的块、保留自己加的块。
  存 <data_dir>/webdocs.db 的 edocs 表，按单位（开通记录的 org）共享；图片用第 126 轮的图片库。
- 内部接口 POST /api/v1/internal/docx-to-pdf：数字工厂枢纽（同在 factory-edge 网络）把工艺卡的 Word 交来转成 PDF，
  用课程接口钥匙（WQ_FACTORY_READ_KEY）认证；转换走本服务器的 OnlyOffice（第 122 轮）。
"""

import asyncio
import hashlib
import hmac
import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, Header, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from . import sewcore
from .moodle import EngineError
from .production import coursedoc, docx_blocks
from .session import Session

DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
KINDS = {"report": "计算书", "card": "调机卡"}
MAX_PDF_IN = 20_000_000


class EStore:
    def __init__(self, folder: str):
        Path(folder).mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(Path(folder) / "webdocs.db"), check_same_thread=False, isolation_level=None)
        self.lock = threading.Lock()
        with self.lock:
            self.db.executescript("""
                CREATE TABLE IF NOT EXISTS edocs (id INTEGER PRIMARY KEY AUTOINCREMENT, org TEXT, kind TEXT, machine TEXT, pid INTEGER,
                    project TEXT, fingerprint TEXT, source TEXT, body TEXT, created REAL, updated REAL, by INTEGER, by_name TEXT);
                CREATE INDEX IF NOT EXISTS edocs_org ON edocs (org, updated);
            """)

    @staticmethod
    def _row(r) -> dict | None:
        if not r:
            return None
        keys = ("id", "org", "kind", "machine", "pid", "project", "fingerprint", "source", "body", "created", "updated", "by", "by_name")
        d = dict(zip(keys, r))
        d["body"] = json.loads(d["body"])
        d["source"] = json.loads(d["source"])
        return d

    def create(self, org: str, kind: str, machine: str, pid: int, project: str, fp: str, source: dict, body: dict,
               by: int, by_name: str) -> int:
        now = time.time()
        with self.lock:
            cur = self.db.execute("INSERT INTO edocs (org, kind, machine, pid, project, fingerprint, source, body, created, updated, by, by_name) "
                                  "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                                  (org, kind, machine, pid, project, fp, json.dumps(source, ensure_ascii=False),
                                   json.dumps(body, ensure_ascii=False), now, now, by, by_name))
            return int(cur.lastrowid)

    def get(self, i: int) -> dict | None:
        with self.lock:
            return self._row(self.db.execute("SELECT * FROM edocs WHERE id=?", (i,)).fetchone())

    def of_org(self, org: str) -> list[dict]:
        with self.lock:
            return [self._row(r) for r in self.db.execute("SELECT * FROM edocs WHERE org=? ORDER BY updated DESC LIMIT 300", (org,))]

    def update(self, i: int, **f: Any) -> float:
        f["updated"] = time.time()
        for k in ("body", "source"):
            if k in f:
                f[k] = json.dumps(f[k], ensure_ascii=False)
        with self.lock:
            self.db.execute(f"UPDATE edocs SET {', '.join(k + '=?' for k in f)} WHERE id=?", (*f.values(), i))
        return f["updated"]

    def delete(self, i: int) -> None:
        with self.lock:
            self.db.execute("DELETE FROM edocs WHERE id=?", (i,))


class NewEngDoc(BaseModel):
    kind: str = Field(pattern="^(report|card)$")
    machine: str = Field(default="lockstitch", pattern="^(lockstitch|overlock|cover|pattern|embroid|flatknit)$")
    params: dict[str, Any] = Field(default_factory=dict)
    pid: int = 0                                         # 机型项目（有就能提示“设计改了”）
    project: str = Field(default="", max_length=80)
    lang: str = "zh"
    desc: list[str] = Field(default_factory=list, max_length=8)
    ebox: dict[str, Any] | None = None


class DocIn(BaseModel):
    doc: dict
    base: float | None = None


class ImageIn(BaseModel):
    data: str = Field(max_length=4_100_000)


def _norm(x: Any) -> Any:
    """Numbers as floats (5000 and 5000.0 are the same design), the rest as JSON has it."""
    if isinstance(x, bool) or x is None or isinstance(x, str):
        return x
    if isinstance(x, (int, float)):
        return round(float(x), 9)
    if isinstance(x, dict):
        return {str(k): _norm(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_norm(v) for v in x]
    return str(x)


def fingerprint(machine: str, params: dict, ebox: dict | None) -> str:
    return hashlib.sha256(json.dumps([machine, _norm(params), _norm(ebox or None)], sort_keys=True,
                                     ensure_ascii=False).encode()).hexdigest()[:24]


def keep_locked(old: dict, new: dict) -> dict:
    """The engineer's save: their own blocks as sent, the computed (locked) ones exactly as generated, in the engineer's order;
    a computed block missing from the save, or changed in it, is put back after the computed block it followed."""
    key = lambda b: json.dumps(b, sort_keys=True, ensure_ascii=False)  # noqa: E731
    locked = [b for b in old["blocks"] if b.get("lock")]
    free: dict[str, list[int]] = {}
    for i, b in enumerate(locked):
        free.setdefault(key(b), []).append(i)
    out: list[dict] = []
    placed: set[int] = set()
    for b in new["blocks"]:
        if not b.get("lock"):
            out.append(b)
            continue
        slots = free.get(key(b))
        if slots:                                      # an unchanged computed block (the next unused copy of it)
            i = slots.pop(0)
            out.append(locked[i])
            placed.add(i)
        # a changed or invented "computed" block is dropped
    for i, b in enumerate(locked):
        if i in placed:
            continue
        at = 0
        if i > 0:
            prev = locked[i - 1]
            at = next((j + 1 for j in range(len(out) - 1, -1, -1) if out[j] is prev), len(out))
        out.insert(at, b)
        placed.add(i)
    return {**new, "title": old["title"], "sub": old["sub"], "blocks": out}


def regenerate(old: dict, fresh: dict) -> dict:
    """New computed blocks; the engineer's own blocks stay at the end of the section (computed heading) they were in,
    those at the very start stay first and those after everything computed stay last."""
    start, last, by_section = [], [], {}
    for i, b in enumerate(old["blocks"]):
        if b.get("lock"):
            continue
        before = [x for x in old["blocks"][:i] if x.get("lock")]
        after = [x for x in old["blocks"][i + 1:] if x.get("lock")]
        if not before:
            start.append(b)
        elif not after:
            last.append(b)
        else:
            head = next((x["text"] for x in reversed(before) if x["t"] == "h"), "")
            by_section.setdefault(head, []).append(b)
    out = list(start)
    section = ""
    for b in fresh["blocks"]:
        if b["t"] == "h":
            out += by_section.pop(section, [])
            section = b["text"]
        out.append(b)
    out += by_section.pop(section, [])
    for rest in by_section.values():           # a section that is no longer there: keep the text at the end
        out += rest
    out += last
    return {**fresh, "blocks": out}


def register(app, m) -> None:
    state = m.state

    def store() -> EStore:
        if not getattr(state, "engdocs", None):
            state.engdocs = EStore(state.settings.data_dir)
        return state.engdocs

    def images():
        return m.coursedoc_store()

    def image_bytes(h: str) -> bytes | None:
        x = images().image(h)
        return x[1] if x else None

    def img_url(h: str) -> str:
        return f"{state.settings.public_url.rstrip('/')}/api/v1/webdoc-img/{h}"

    async def build(body: NewEngDoc, org: str) -> tuple[dict, dict]:
        """The Word file exactly as “导出” makes it, split into locked blocks."""
        from .sewcore import report
        lang = "en" if body.lang.startswith("en") else "zh"
        M = sewcore.get(body.machine)
        p = M.clean(body.params)
        if body.kind == "report":
            cae = m.sewing_cae_results(org, M.MACHINE, p, body.ebox) if hasattr(m, "sewing_cae_results") else []
            data = await asyncio.to_thread(report.calc_report, p, lang, body.project, org, machine=M.MACHINE, cae=cae,
                                           desc=[x[:400] for x in body.desc], ebox=body.ebox)
        else:
            data = await asyncio.to_thread(report.card_docx, p, lang, body.project, machine=M.MACHINE)
        title, sub, blocks = await asyncio.to_thread(docx_blocks.blocks_of, data, images().put_image)
        stem = body.project.strip() or M.NAME[0]
        doc = coursedoc.clean({"template": "blank", "title": [title or f"{stem}{KINDS[body.kind]}", ""], "sub": sub,
                               "blocks": blocks})
        source = {"machine": M.MACHINE, "params": p, "project": body.project, "lang": lang, "desc": body.desc[:8], "ebox": body.ebox}
        return doc, source

    def project_params(org: str, pid: int) -> tuple[str, dict] | None:
        if not pid:
            return None
        with m.sewing_db() as c:
            r = c.execute("select machine, params from projects where id=? and org=?", (pid, org)).fetchone()
        return (r[0], json.loads(r[1] or "{}")) if r else None

    def state_of(d: dict) -> dict:
        cur = project_params(d["org"], d["pid"])
        stale = bool(cur) and fingerprint(cur[0], sewcore.get(cur[0]).clean(cur[1]), d["source"].get("ebox")) != d["fingerprint"]
        return {"id": d["id"], "kind": d["kind"], "machine": d["machine"], "pid": d["pid"], "project": d["project"], "doc": d["body"],
                "updated": d["updated"], "by_name": d["by_name"], "stale": stale, "project_gone": bool(d["pid"]) and cur is None,
                "pdf": bool(state.settings.docs_url and state.settings.docs_jwt_secret)}

    async def mine(sess: Session, i: int) -> tuple[dict, dict]:
        lic = await m.sewing_need_license(sess)
        d = store().get(i)
        if not d or d["org"] != lic["org"]:
            raise EngineError("not_found", "no such document", 404)
        return d, lic

    @app.post("/api/v1/sewing/webdocs")
    async def create(body: NewEngDoc, sess: Annotated[Session, Depends(m.current)]):
        """“存为网页文档”：计算书或调机卡，数字照这次计算。"""
        lic = await m.sewing_need_license(sess)
        if len(store().of_org(lic["org"])) >= 300:
            raise EngineError("too_many", "at most 300 documents per company; delete old ones first", 400)
        if body.pid and not project_params(lic["org"], body.pid):
            raise EngineError("not_found", "no such project", 404)
        doc, source = await build(body, lic["org"])
        fp = fingerprint(source["machine"], source["params"], body.ebox)
        i = store().create(lic["org"], body.kind, source["machine"], body.pid, body.project, fp, source, doc, sess.user_id,
                           lic.get("name") or "")
        return state_of(store().get(i))

    @app.get("/api/v1/sewing/webdocs")
    async def listing(sess: Annotated[Session, Depends(m.current)]):
        lic = await m.sewing_need_license(sess)
        return {"docs": [{"id": d["id"], "kind": d["kind"], "machine": d["machine"], "project": d["project"], "title": d["body"]["title"],
                          "updated": d["updated"], "by_name": d["by_name"]} for d in store().of_org(lic["org"])]}

    @app.get("/api/v1/engdocs/{i}")
    async def get_doc(i: int, sess: Annotated[Session, Depends(m.current)]):
        d, _ = await mine(sess, i)
        return state_of(d)

    @app.put("/api/v1/engdocs/{i}")
    async def save_doc(i: int, body: DocIn, sess: Annotated[Session, Depends(m.current)]):
        d, _ = await mine(sess, i)
        if body.base is not None and d["updated"] > body.base + 0.001:
            raise EngineError("doc_changed", "this document was changed elsewhere; reload it first", 409)
        try:
            doc = keep_locked(d["body"], coursedoc.clean(body.doc))
        except coursedoc.DocError as e:
            raise EngineError("bad_doc", str(e), 400)
        return {"updated": store().update(i, body=doc, by=sess.user_id)}

    @app.post("/api/v1/engdocs/{i}/regenerate")
    async def regen(i: int, sess: Annotated[Session, Depends(m.current)]):
        """The project's design changed: compute again from it; the engineer's own blocks stay."""
        d, lic = await mine(sess, i)
        cur = project_params(lic["org"], d["pid"])
        if not cur:
            raise EngineError("project_gone", "the design project of this document was deleted", 409)
        src = d["source"]
        nb = NewEngDoc(kind=d["kind"], machine=cur[0], params=cur[1], pid=d["pid"], project=d["project"], lang=src.get("lang", "zh"),
                       desc=src.get("desc") or [], ebox=src.get("ebox"))
        fresh, source = await build(nb, lic["org"])
        doc = regenerate(d["body"], fresh)
        store().update(i, body=doc, source=source, fingerprint=fingerprint(source["machine"], source["params"], nb.ebox), machine=cur[0])
        return state_of(store().get(i))

    @app.delete("/api/v1/engdocs/{i}")
    async def delete_doc(i: int, sess: Annotated[Session, Depends(m.current)]):
        await mine(sess, i)
        store().delete(i)
        return {"ok": True}

    @app.post("/api/v1/engdocs/{i}/images")
    async def add_image(i: int, body: ImageIn, sess: Annotated[Session, Depends(m.current)]):
        await mine(sess, i)
        import base64
        import binascii
        from .coursedocs_api import MAX_IMAGE, image_in
        s = body.data.split(",", 1)[1] if body.data.startswith("data:") else body.data
        try:
            raw = base64.b64decode(s, validate=True)
        except (binascii.Error, ValueError):
            raise EngineError("bad_image", "not a picture", 400)
        if len(raw) > MAX_IMAGE:
            raise EngineError("bad_image", "pictures are at most 3 MB", 400)
        data, mime = await asyncio.to_thread(image_in, raw)
        h = images().put_image(data, mime)
        return {"img": h, "url": img_url(h)}

    @app.get("/api/v1/engdocs/{i}/export")
    async def export(i: int, sess: Annotated[Session, Depends(m.current)], fmt: str = "docx"):
        d, _ = await mine(sess, i)
        data = await asyncio.to_thread(coursedoc.to_docx, d["body"], image_bytes)
        name = (d["body"]["title"][0] or KINDS[d["kind"]]).replace("/", "-").replace(" ", "")
        ext = "docx"
        if fmt == "pdf":
            data, ext = await m.webdocs_pdf(data, name), "pdf"
        from urllib.parse import quote
        return Response(data, media_type="application/pdf" if ext == "pdf" else DOCX,
                        headers={"Content-Disposition": f"attachment; filename=\"doc.{ext}\"; filename*=UTF-8''{quote(name + '.' + ext)}",
                                 "Cache-Control": "no-store"})

    # ---------------------------------------------------------------- 数字工厂枢纽转 PDF（工艺卡）

    @app.post("/api/v1/internal/docx-to-pdf")
    async def docx_to_pdf(req: Request, authorization: Annotated[str | None, Header()] = None):
        key = state.settings.factory_read_key
        got = (authorization or "").split(" ", 1)[-1].strip()
        if not key or not got or not hmac.compare_digest(got, key):
            raise EngineError("forbidden", "server-to-server only", 403)
        data = await req.body()
        if not data or len(data) > MAX_PDF_IN or not data.startswith(b"PK"):
            raise EngineError("bad_file", "send a Word (docx) file of at most 20 MB", 400)
        pdf = await m.webdocs_pdf(data, "cards")
        return Response(pdf, media_type="application/pdf", headers={"Cache-Control": "no-store"})

    m.engdoc_html = lambda doc: coursedoc.to_html(doc, img_url)
