"""本单位零件库第一期（第 49 轮，细则第七节 2）：一个单位一个库，同单位成员共享，别的单位看不见。

  GET    /api/v1/sewing/parts/cats             类别、字段、接进设计的方式（谁都能看）
  GET    /api/v1/sewing/parts                  查找（q 编号 / 名称 / 物料号，cat 类别，status ok / review）
  POST   /api/v1/sewing/parts                  手填一个零件（有造型程序的类别自动生成三维）
  GET    /api/v1/sewing/parts/{id}             详情（含这件能接进当前机型的哪些参数：?machine=）
  PUT    /api/v1/sewing/parts/{id}             改；confirm = true 把“待复核”变成“可用”（复核过）
  DELETE /api/v1/sewing/parts/{id}
  POST   /api/v1/sewing/parts/{id}/step        上传这件的 STEP（30 MB 以内）
  GET    /api/v1/sewing/parts/{id}/step        下载 STEP
  GET    /api/v1/sewing/parts/{id}/mesh        三维预览用的三角网格（网页看图）
  GET    /api/v1/sewing/parts/template.xlsx    某类别的 Excel 模板（?cat=）
  POST   /api/v1/sewing/parts/import           表格批量：commit = false 只预览检查，true 才入库
  POST   /api/v1/sewing/parts/extract          AI 整理样本：PDF → 参数表（每个数附原文出处，程序核对能在 PDF 里找到）→ 全部“待复核”
  GET    /api/v1/sewing/parts/erp.xlsx         ERPNext 物料导入表（可用的零件）
  GET    /api/v1/sewing/parts/for              当前机型能用的零件和它们接进哪些参数（设计页“从本单位零件库选”）

谁能用：已开通的企业（网页登录凭证或 FreeCAD 钥匙）。数据：<data_dir>/sewing.db 的 parts 表，文件在 <data_dir>/sewing_parts/。
上限：每单位 5 000 件，STEP 30 MB，AI 整理每单位每天 20 份。待复核的零件不进设计和选型。
"""

import hashlib
import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import quote

from fastapi import Depends, File, Form, Response, UploadFile
from pydantic import BaseModel, Field

from .moodle import EngineError
from .sewcore import aicheck
from .sewcore import partlib as PL

MAX_PARTS = 5000
MAX_STEP = 30 * 1024 * 1024
MAX_PDF = 30 * 1024 * 1024
EXTRACT_DAILY = 20

EXTRACT_SYSTEM = """You read a component catalogue or drawing (the text of a PDF) and fill a parts table for a sewing-machine
company's own parts library. One row per distinct model / size in the document that belongs to the category asked for.
Rules — they matter more than anything else:
1. Never invent a value. Every number must be written in the document. If a field is not in the document, use null.
2. Convert units only by plain arithmetic and only when the document gives the value in another unit; then say so in
   the quote (e.g. "0.637 N·m" stays 0.637; "6.37 kgf·cm" is not converted — leave it null and ask in notes).
3. For every non-null field give `quote`: the short exact text from the document the value comes from (≤ 80 chars).
4. code = the model number as written in the document; name = a short Chinese name.
Answer only with the JSON object."""


class PartIn(BaseModel):
    cat: str = Field(pattern="^(" + "|".join(PL.ORDER) + ")$")
    code: str = Field(min_length=1, max_length=60)
    name: str = Field(min_length=1, max_length=80)
    erp: str = Field(default="", max_length=60)
    fields: dict[str, Any] = Field(default_factory=dict)
    confirm: bool = False


def extract_schema(cat: str) -> dict:
    props, q = {}, {}
    for k, _zh, _u, *_ in PL.CATS[cat]["fields"]:
        props[k] = {"type": ["string", "null"]} if k in PL.TEXT_FIELDS else {"type": ["number", "null"]}
        q[k] = {"type": ["string", "null"]}
    row = {"type": "object", "additionalProperties": False,
           "properties": {"code": {"type": "string"}, "name": {"type": "string"},
                          "fields": {"type": "object", "additionalProperties": False, "properties": props, "required": list(props)},
                          "quotes": {"type": "object", "additionalProperties": False, "properties": q, "required": list(q)}},
           "required": ["code", "name", "fields", "quotes"]}
    return {"type": "object", "additionalProperties": False,
            "properties": {"rows": {"type": "array", "items": row}, "notes": {"type": "array", "items": {"type": "string"}}},
            "required": ["rows", "notes"]}


def pdf_text(data: bytes, max_pages: int = 60, max_chars: int = 60000) -> str:
    from pypdf import PdfReader
    import io
    rd = PdfReader(io.BytesIO(data))
    out = []
    for i, pg in enumerate(rd.pages[:max_pages]):
        t = pg.extract_text() or ""
        if t.strip():
            out.append(f"[第 {i + 1} 页]\n{t}")
        if sum(len(x) for x in out) > max_chars:
            break
    return "\n".join(out)[:max_chars]


def evidence(cat: str, fields: dict, quotes: dict, text: str) -> dict:
    """每个数：原文出处，以及程序有没有在 PDF 文字里找到这个数（允许四舍五入）"""
    bag = {v for v, _ in aicheck.numbers_in(text)}
    flat = re.sub(r"\s+", "", text)
    ev = {}
    for k, v in fields.items():
        qt = str((quotes or {}).get(k) or "")[:120]
        if k in PL.TEXT_FIELDS:
            ok = bool(v) and re.sub(r"\s+", "", str(v)) in flat
        else:
            dec = len(str(v).split(".")[1]) if "." in str(v) else 0
            ok = aicheck.found(float(v), dec, bag)
        ev[k] = {"quote": qt, "found": ok}
    return ev


def register(app, m) -> None:
    state = m.state
    who = m.sewing_who

    def db() -> sqlite3.Connection:
        c = m.sewing_db()
        c.execute("""create table if not exists parts(id integer primary key, org text, code text, name text, cat text, fields text,
                     erp text, source text, status text, evidence text, step text, step_name text, created_by integer,
                     created integer, updated integer)""")
        c.execute("create unique index if not exists parts_code on parts(org, code)")
        c.execute("create table if not exists part_extracts(id integer primary key, org text, user_id integer, ts real, file text, rows integer)")
        return c

    def store() -> Path:
        d = Path(state.settings.data_dir) / "sewing_parts"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def row(r) -> dict:
        d = dict(r)
        d["fields"] = json.loads(d["fields"] or "{}")
        d["evidence"] = json.loads(d["evidence"] or "{}")
        d["has_step"] = bool(d.pop("step"))
        return d

    def own(c, pid: int, lic: dict):
        r = c.execute("select * from parts where id=? and org=?", (pid, lic["org"])).fetchone()
        if not r:
            raise EngineError("not_found", "no such part", 404)
        return r

    def save_step(data: bytes) -> str:
        h = hashlib.sha256(data).hexdigest()
        p = store() / f"{h}.step"
        if not p.exists():
            p.write_bytes(data)
        return h

    def free_code(c, org: str, code: str) -> str:
        base, n = code, 2
        while c.execute("select 1 from parts where org=? and code=?", (org, code)).fetchone():
            code = f"{base}-{n}"
            n += 1
        return code

    def insert(c, lic, cat, code, name, erp, fields, source, status, ev=None) -> int:
        if c.execute("select count(*) from parts where org=?", (lic["org"],)).fetchone()[0] >= MAX_PARTS:
            raise EngineError("too_many", f"at most {MAX_PARTS} parts per company", 400)
        step = None
        if PL.can_shape(cat, fields):
            data = PL.to_step(cat, fields, code)
            step = save_step(data) if data else None
        now = int(time.time())
        return c.execute("""insert into parts(org,code,name,cat,fields,erp,source,status,evidence,step,step_name,created_by,created,updated)
                            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                         (lic["org"], code, name, cat, json.dumps(fields, ensure_ascii=False), erp, source, status,
                          json.dumps(ev or {}, ensure_ascii=False), step, f"{code}.step" if step else "", lic["user_id"], now, now)).lastrowid

    @app.get("/api/v1/sewing/parts/cats")
    async def cats():
        return {"cats": PL.cats_public()}

    @app.get("/api/v1/sewing/parts")
    async def search(lic: Annotated[dict, Depends(who)], q: str = "", cat: str = "", status: str = ""):
        sql, args = "select * from parts where org=?", [lic["org"]]
        if cat:
            sql += " and cat=?"
            args.append(cat)
        if status in ("ok", "review"):
            sql += " and status=?"
            args.append(status)
        if q.strip():
            sql += " and (code like ? or name like ? or erp like ?)"
            args += [f"%{q.strip()}%"] * 3
        with db() as c:
            rs = [row(r) for r in c.execute(sql + " order by updated desc limit 500", args)]
            n = c.execute("select count(*) from parts where org=?", (lic["org"],)).fetchone()[0]
            nr = c.execute("select count(*) from parts where org=? and status='review'", (lic["org"],)).fetchone()[0]
        return {"org": lic["org"], "parts": rs, "total": n, "review": nr}

    @app.post("/api/v1/sewing/parts")
    async def create(body: PartIn, lic: Annotated[dict, Depends(who)]):
        fields, errs = PL.check_fields(body.cat, body.fields)
        if errs:
            raise EngineError("bad_fields", "；".join(errs), 400)
        with db() as c:
            if c.execute("select 1 from parts where org=? and code=?", (lic["org"], body.code.strip())).fetchone():
                raise EngineError("duplicate", "this code is already in your library", 409)
            pid = insert(c, lic, body.cat, body.code.strip(), body.name.strip(), body.erp.strip(), fields, "manual", "ok")
            return row(c.execute("select * from parts where id=?", (pid,)).fetchone())

    @app.get("/api/v1/sewing/parts/for")
    async def usable(lic: Annotated[dict, Depends(who)], machine: str = "lockstitch"):
        out = []
        with db() as c:
            for r in c.execute("select * from parts where org=? and status='ok' order by code", (lic["org"],)):
                p = row(r)
                for u in PL.param_values(p["cat"], p["fields"], machine):
                    out.append({"id": p["id"], "code": p["code"], "name": p["name"], "cat": p["cat"], "label": u["label"], "params": u["params"]})
        return {"items": out}

    @app.get("/api/v1/sewing/parts/template.xlsx")
    async def template(cat: str, lic: Annotated[dict, Depends(who)]):
        if cat not in PL.CATS:
            raise EngineError("not_found", "no such category", 404)
        name = f"零件库模板-{PL.CATS[cat]['zh'].replace(' / ', '、')}.xlsx"
        return Response(PL.template_xlsx(cat), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(name)}"})

    @app.post("/api/v1/sewing/parts/import")
    async def import_xlsx(lic: Annotated[dict, Depends(who)], file: UploadFile = File(...), cat: str = Form(...),
                          commit: bool = Form(False)):
        if cat not in PL.CATS:
            raise EngineError("not_found", "no such category", 404)
        data = await file.read()
        if not data or len(data) > 10 * 1024 * 1024:
            raise EngineError("bad_file", "the table is empty or larger than 10 MB", 400)
        try:
            rows = PL.read_xlsx(cat, data)
        except ValueError as e:
            raise EngineError("bad_table", str(e), 400) from e
        except Exception as e:  # noqa: BLE001
            raise EngineError("bad_table", "cannot read this file; save it as .xlsx from the template", 400) from e
        with db() as c:
            for x in rows:
                if x["code"] and c.execute("select 1 from parts where org=? and code=?", (lic["org"], x["code"])).fetchone():
                    x["errors"].append("编号库里已经有了")
            bad = sum(1 for x in rows if x["errors"])
            if not commit or bad or not rows:
                return {"rows": rows, "bad": bad, "imported": 0}
            for x in rows:
                insert(c, lic, cat, x["code"], x["name"], x["erp"], x["fields"], "table", "ok")
        return {"rows": rows, "bad": 0, "imported": len(rows)}

    @app.post("/api/v1/sewing/parts/extract")
    async def extract(lic: Annotated[dict, Depends(who)], file: UploadFile = File(...), cat: str = Form(...)):
        if cat not in PL.CATS:
            raise EngineError("not_found", "no such category", 404)
        if not state.ai.available:
            raise EngineError("ai_unavailable", "no AI model is configured on this server", 503)
        data = await file.read()
        if not data or len(data) > MAX_PDF or not data.startswith(b"%PDF"):
            raise EngineError("bad_file", "upload a PDF under 30 MB", 400)
        try:
            text = pdf_text(data)
        except Exception as e:  # noqa: BLE001
            raise EngineError("bad_file", "cannot read this PDF", 400) from e
        if len(text.strip()) < 40:
            raise EngineError("no_text", "this PDF has no text layer (a scan); scanned catalogues are not supported yet", 400)
        with db() as c:
            n = c.execute("select count(*) from part_extracts where org=? and ts>?", (lic["org"], time.time() - 86400)).fetchone()[0]
        if n >= EXTRACT_DAILY:
            raise EngineError("quota", f"today's catalogue reads are used up ({EXTRACT_DAILY} a day per company)", 429)
        c0 = PL.CATS[cat]
        fl = "\n".join(f"{k}\t{zh}\t{u}" for k, zh, u, *_ in c0["fields"])
        out = await state.ai.json(system=EXTRACT_SYSTEM, schema=extract_schema(cat), max_tokens=8000,
                                  prompt=f"Category: {c0['zh']}\nFields (key, name, unit):\n{fl}\n\nDocument text:\n{text}",
                                  fake=lambda: {"rows": [], "notes": []})
        made = []
        with db() as c:
            c.execute("insert into part_extracts(org,user_id,ts,file,rows) values(?,?,?,?,?)",
                      (lic["org"], lic["user_id"], time.time(), (file.filename or "")[:80], len(out.get("rows") or [])))
            for r in (out.get("rows") or [])[:200]:
                raw = {k: v for k, v in (r.get("fields") or {}).items() if v is not None}
                fields, errs = PL.check_fields(cat, raw)
                # 必填没找到也照样进“待复核”，复核时补
                fields.update({k: v for k, v in raw.items() if k not in fields and k in PL.TEXT_FIELDS})
                ev = evidence(cat, fields, r.get("quotes") or {}, text)
                code = free_code(c, lic["org"], (str(r.get("code") or "").strip() or f"AI-{int(time.time())}")[:60])
                pid = insert(c, lic, cat, code, (str(r.get("name") or "") or c0["zh"])[:80], "", fields, "ai", "review",
                             dict(ev, _file=(file.filename or "")[:80], _errors=errs))
                made.append(row(c.execute("select * from parts where id=?", (pid,)).fetchone()))
        return {"parts": made, "notes": [str(x) for x in (out.get("notes") or [])][:6], "model": state.ai.provider}

    @app.get("/api/v1/sewing/parts/erp.xlsx")
    async def erp(lic: Annotated[dict, Depends(who)]):
        with db() as c:
            ps = [row(r) for r in c.execute("select * from parts where org=? and status='ok' order by code", (lic["org"],))]
        return Response(PL.erp_xlsx(ps), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote('本单位零件-ERPNext物料导入表.xlsx')}"})

    @app.get("/api/v1/sewing/parts/{pid}")
    async def get_part(pid: int, lic: Annotated[dict, Depends(who)], machine: str = ""):
        with db() as c:
            p = row(own(c, pid, lic))
        if machine:
            p["uses"] = PL.param_values(p["cat"], p["fields"], machine)
        return p

    @app.put("/api/v1/sewing/parts/{pid}")
    async def update(pid: int, body: PartIn, lic: Annotated[dict, Depends(who)]):
        fields, errs = PL.check_fields(body.cat, body.fields)
        with db() as c:
            old = row(own(c, pid, lic))
            if errs and (old["status"] == "ok" or body.confirm):
                raise EngineError("bad_fields", "；".join(errs), 400)
            if c.execute("select 1 from parts where org=? and code=? and id<>?", (lic["org"], body.code.strip(), pid)).fetchone():
                raise EngineError("duplicate", "this code is already in your library", 409)
            status = "ok" if (old["status"] == "ok" or body.confirm) else "review"
            step = c.execute("select step, step_name from parts where id=?", (pid,)).fetchone()
            sh, sn = step[0], step[1]
            if PL.can_shape(body.cat, fields) and (fields != old["fields"] or not sh) and old["source"] != "upload":
                data = PL.to_step(body.cat, fields, body.code.strip())
                if data:
                    sh, sn = save_step(data), f"{body.code.strip()}.step"
            c.execute("update parts set code=?, name=?, cat=?, fields=?, erp=?, status=?, step=?, step_name=?, updated=? where id=?",
                      (body.code.strip(), body.name.strip(), body.cat, json.dumps(fields, ensure_ascii=False), body.erp.strip(), status,
                       sh, sn, int(time.time()), pid))
            return row(c.execute("select * from parts where id=?", (pid,)).fetchone())

    @app.delete("/api/v1/sewing/parts/{pid}")
    async def remove(pid: int, lic: Annotated[dict, Depends(who)]):
        with db() as c:
            own(c, pid, lic)
            c.execute("delete from parts where id=?", (pid,))
        return {"ok": True}

    @app.post("/api/v1/sewing/parts/{pid}/step")
    async def upload_step(pid: int, lic: Annotated[dict, Depends(who)], file: UploadFile = File(...)):
        data = await file.read()
        if not data or len(data) > MAX_STEP or b"ISO-10303-21" not in data[:200]:
            raise EngineError("bad_file", "upload a STEP file (.step / .stp) under 30 MB", 400)
        with db() as c:
            own(c, pid, lic)
            c.execute("update parts set step=?, step_name=?, source=case when source='manual' then 'upload' else source end, updated=? where id=?",
                      (save_step(data), (file.filename or "part.step")[:80], int(time.time()), pid))
            return row(c.execute("select * from parts where id=?", (pid,)).fetchone())

    def step_bytes(pid: int, lic: dict) -> tuple[bytes, str]:
        with db() as c:
            r = own(c, pid, lic)
        if not r["step"]:
            raise EngineError("not_found", "this part has no 3D model", 404)
        p = store() / f"{r['step']}.step"
        if not p.exists():
            raise EngineError("not_found", "the 3D file is missing on the server", 404)
        return p.read_bytes(), r["step_name"] or f"{r['code']}.step"

    @app.get("/api/v1/sewing/parts/{pid}/step")
    async def download_step(pid: int, lic: Annotated[dict, Depends(who)]):
        data, name = step_bytes(pid, lic)
        return Response(data, media_type="model/step", headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(name)}"})

    @app.get("/api/v1/sewing/parts/{pid}/mesh")
    async def mesh(pid: int, lic: Annotated[dict, Depends(who)]):
        data, _ = step_bytes(pid, lic)
        h = hashlib.sha256(data).hexdigest()
        cache = store() / f"{h}.mesh.json"
        if cache.exists():
            return Response(cache.read_bytes(), media_type="application/json")
        try:
            out = step_mesh(data)
        except Exception as e:  # noqa: BLE001
            raise EngineError("unavailable", "3D preview is not available on this server", 503) from e
        cache.write_text(json.dumps(out))
        return out

    # CAE（sewing_cae.py）用：本单位可用的电机、库里机壳的 STEP
    def org_motors(org: str) -> list[dict]:
        with db() as c:
            return [PL.cae_motor(row(r)) for r in c.execute("select * from parts where org=? and cat='motor' and status='ok'", (org,))]

    m.sewing_org_motors = org_motors
    m.sewing_part_step = step_bytes


def step_mesh(data: bytes, tol: float = 0.2) -> dict:
    """STEP → 三角网格（顶点、三角形），网页 three.js 显示用"""
    import os
    import tempfile

    import build123d as bd
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "p.step")
        with open(p, "wb") as f:
            f.write(data)
        shape = bd.import_step(p)
    bb = shape.bounding_box()
    size = max(bb.size.X, bb.size.Y, bb.size.Z, 1e-3)
    verts, tris = shape.tessellate(max(tol, size / 400))
    return {"v": [round(c, 3) for v in verts for c in (v.X, v.Y, v.Z)], "f": [i for t in tris for i in t],
            "size": [round(bb.size.X, 2), round(bb.size.Y, 2), round(bb.size.Z, 2)]}
