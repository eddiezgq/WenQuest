"""问渠电子的 AI 起草（第 105 轮 P3）：网关只负责调模型、认人、限次、留记录。

  POST /api/v1/eda/ai/draft      需求 + 起草目录 → 规格与功能块参数的草稿（每个数带来源；没给的关键数留空并提问）
  POST /api/v1/eda/ai/runs/{id}  问渠电子服务回填这次草稿是否通过代码校验
  POST /api/v1/eda/ai/issues     第 112 轮：工厂端检查结果 → 给客户的工程问题单草稿（每条引用检查结果编号）。
                                 只收检查结果，不收客户的文件；记录里只记工厂名和结果条数

调用方是问渠电子服务（官网 /eda/），它转来用户的全站登录 cookie 或 Bearer；目录由它按功能块库生成，这里只把目录当数据
放进提示，网关不判定、不改设计。模型走统一的模型接口 ai.py：美国用 Claude，国内部署（region cn）自动用 DeepSeek。
每人每天上限 WQ_EDA_AI_DAILY（默认 30）。每次调用记一条：谁、输入摘要（前 200 字）、模型、耗时、是否通过校验。
数据：<data_dir>/eda_ai.db（SQLite）。
"""

import json
import sqlite3
import time
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, Header, Request
from pydantic import BaseModel, Field

from .moodle import EngineError
from .session import Session

DRAFT_SYSTEM = """You draft the first two layers of a printed-circuit-board design for the WenQuest Electronics platform:
the specification (spec) and the parameters of the functional blocks (units). A catalog lists the only spec fields,
unit types, parameters, allowed ranges and choices you may use; the board topology is fixed by the catalog.
Rules — they matter more than anything else:
1. Never invent a number. Every value carries a source:
   - "requirement": the number is written in the requirement; put the exact words you took it from in "quote".
   - "rule": the number follows from numbers in the requirement by a plain rule (e.g. current = power / voltage);
     write the rule and the numbers you used in "why".
   - "assumption": a design choice you propose that the requirement does not settle; write it in "why" as a short
     question the engineer must answer. Required spec fields may never be assumptions.
2. If a required spec field is neither written nor derivable, set its value to null and ask for it in "questions".
3. Use only spec keys, unit types and parameter keys from the catalog, with values inside the allowed range or list.
   Parameters you do not mention keep the catalog default; only list the ones the requirement or a rule changes,
   or the ones you deliberately propose.
4. Anything the requirement asks for that the catalog cannot do (another interface, another board type, another
   device) goes into "unsupported" in one short line each; do not approximate it.
5. If "feedback" lists failed checks from the previous draft, change only what is needed to fix them, with sources.
Answer only with the JSON object."""


ISSUES_SYSTEM = """You draft an engineering query (problem list) that a PCB assembly factory sends to its customer, for the
WenQuest PCBA platform. You get only the factory's check results; each has an id (R1, R2, ...), a check key, a status
(fail / unknown / pending), the measured value, the factory's limit, the reference designators and a note.
Rules:
1. Every issue cites one or more result ids from the list. Never mention a problem that is not in the results, and never
   invent numbers, part numbers or designators: write about what the results say.
2. Ask a clear question the customer can answer, and give two to four concrete options (e.g. fix the design, accept a
   deviation, provide a missing file). For "unknown" results caused by missing files, ask for those files.
3. Group results that the customer would answer together; skip nothing that failed.
4. Be short and polite, the way an experienced process engineer writes.
Answer only with the JSON object."""


def issues_schema(ids: list[str]) -> dict:
    item = {"type": "object", "additionalProperties": False,
            "properties": {"cites": {"type": "array", "items": {"type": "string", "enum": ids}},
                           "question": {"type": "string"},
                           "options": {"type": "array", "items": {"type": "string"}},
                           "reply_required": {"type": "boolean"}},
            "required": ["cites", "question", "options", "reply_required"]}
    return {"type": "object", "additionalProperties": False,
            "properties": {"issues": {"type": "array", "items": item}}, "required": ["issues"]}


def _value_schema() -> dict:
    return {"type": ["number", "string", "null"]}


def _entry_schema() -> dict:
    return {"type": "object", "additionalProperties": False,
            "properties": {"key": {"type": "string"}, "value": _value_schema(),
                           "source": {"type": "string", "enum": ["requirement", "rule", "assumption"]},
                           "quote": {"type": "string"}, "why": {"type": "string"}},
            "required": ["key", "value", "source", "quote", "why"]}


def draft_schema(unit_types: list[str]) -> dict:
    unit = {"type": "object", "additionalProperties": False,
            "properties": {"type": {"type": "string", "enum": unit_types},
                           "params": {"type": "array", "items": _entry_schema()}},
            "required": ["type", "params"]}
    return {"type": "object", "additionalProperties": False,
            "properties": {"spec": {"type": "array", "items": _entry_schema()},
                           "units": {"type": "array", "items": unit},
                           "questions": {"type": "array", "items": {"type": "string"}},
                           "unsupported": {"type": "array", "items": {"type": "string"}}},
            "required": ["spec", "units", "questions", "unsupported"]}


class DraftIn(BaseModel):
    requirement: str = Field(min_length=4, max_length=3000)
    catalog: dict[str, Any]
    feedback: dict[str, Any] | None = None
    lang: str = Field(default="zh", pattern="^(zh|en)$")


class IssuesIn(BaseModel):
    results: list[dict[str, Any]] = Field(min_length=1, max_length=80)
    factory: str = Field(default="", max_length=120)
    lang: str = Field(default="zh", pattern="^(zh|en)$")


RESULT_KEYS = ("id", "key", "name", "status", "value", "limit", "unit", "detail", "refs")


class VerdictIn(BaseModel):
    passed: bool
    note: str = Field(default="", max_length=300)


def register(app, m) -> None:
    state = m.state

    def db() -> sqlite3.Connection:
        d = Path(state.settings.data_dir)
        d.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(str(d / "eda_ai.db"), isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("create table if not exists runs(id integer primary key, ts real, user_id integer, kind text, "
                  "input text, provider text, ms integer, ok integer, passed integer, note text)")
        return c

    def daily() -> int:
        return int(getattr(state.settings, "eda_ai_daily", 30) or 30)

    async def who(req: Request, authorization: Annotated[str | None, Header()] = None) -> Session:
        sess = None
        if authorization and authorization.lower().startswith("bearer "):
            sess = state.codec.read(authorization.split(" ", 1)[1].strip())
        if not sess:
            tok = req.cookies.get("wq_sso", "")
            sess = state.codec.read(tok) if tok else None
        if not sess:
            raise EngineError("not_logged_in", "sign in to use AI drafting", 401)
        return sess

    def quota(sess: Session) -> int:
        with db() as c:
            n = c.execute("select count(*) from runs where user_id=? and ts>?",
                          (sess.user_id, time.time() - 86400)).fetchone()[0]
        if n >= daily():
            raise EngineError("quota", f"today's AI drafts are used up ({daily()} a day)", 429)
        return daily() - n

    @app.post("/api/v1/eda/ai/draft")
    async def draft(body: DraftIn, sess: Annotated[Session, Depends(who)]):
        cat = json.dumps(body.catalog, ensure_ascii=False)
        if len(cat) > 20000:
            raise EngineError("bad_request", "catalog too large", 400)
        types = [str(u.get("type")) for u in body.catalog.get("units") or []] + \
                [str(u.get("type")) for u in body.catalog.get("fixed_units") or []]
        if not types:
            raise EngineError("bad_request", "catalog has no unit types", 400)
        if not state.ai.available:
            raise EngineError("ai_unavailable", "no AI model is configured", 503)
        left = quota(sess)
        prompt = (f"Write questions, unsupported items and why-texts in {'Chinese' if body.lang == 'zh' else 'English'}.\n"
                  f"Catalog (JSON):\n{cat}\n"
                  + (f"Feedback (JSON):\n{json.dumps(body.feedback, ensure_ascii=False)[:6000]}\n" if body.feedback else "")
                  + f"Requirement:\n{body.requirement}")
        t0 = time.time()
        ok, out = 0, {}
        try:
            out = await state.ai.json(system=DRAFT_SYSTEM, prompt=prompt, schema=draft_schema(types), max_tokens=3000,
                                      fake=lambda: {"spec": [], "units": [], "questions": ["(fake model)"],
                                                    "unsupported": []})
            ok = 1
        finally:
            with db() as c:
                rid = c.execute("insert into runs(ts,user_id,kind,input,provider,ms,ok) values(?,?,?,?,?,?,?)",
                                (t0, sess.user_id, "draft" if not body.feedback else "revise",
                                 body.requirement[:200], state.ai.provider, int((time.time() - t0) * 1000),
                                 ok)).lastrowid
        return {"draft": out, "run": rid, "left_today": left - 1, "model": state.ai.provider}

    @app.post("/api/v1/eda/ai/issues")
    async def issues(body: IssuesIn, sess: Annotated[Session, Depends(who)]):
        res = [{k: r.get(k) for k in RESULT_KEYS} for r in body.results if r.get("status") in ("fail", "unknown", "pending")]
        ids = [str(r["id"]) for r in res if r.get("id")]
        if not ids:
            raise EngineError("bad_request", "no open check results to write about", 400)
        data = json.dumps(res, ensure_ascii=False)
        if len(data) > 30000:
            raise EngineError("bad_request", "results too large", 400)
        if not state.ai.available:
            raise EngineError("ai_unavailable", "no AI model is configured", 503)
        left = quota(sess)
        prompt = (f"Write in {'Chinese' if body.lang == 'zh' else 'English'}.\nFactory: {body.factory}\n"
                  f"Check results (JSON):\n{data}")
        t0 = time.time()
        ok, out = 0, {}
        try:
            out = await state.ai.json(system=ISSUES_SYSTEM, prompt=prompt, schema=issues_schema(ids), max_tokens=3000,
                                      fake=lambda: {"issues": [{"cites": ids[:1], "question": "(fake model)",
                                                                "options": [], "reply_required": True}]})
            ok = 1
        finally:
            with db() as c:
                rid = c.execute("insert into runs(ts,user_id,kind,input,provider,ms,ok) values(?,?,?,?,?,?,?)",
                                (t0, sess.user_id, "issues", f"{body.factory[:80]}；{len(ids)} 条结果",
                                 state.ai.provider, int((time.time() - t0) * 1000), ok)).lastrowid
        return {"draft": out, "run": rid, "left_today": left - 1, "model": state.ai.provider}

    @app.post("/api/v1/eda/ai/runs/{rid}")
    async def verdict(rid: int, body: VerdictIn, sess: Annotated[Session, Depends(who)]):
        with db() as c:
            n = c.execute("update runs set passed=?, note=? where id=? and user_id=?",
                          (int(body.passed), body.note[:300], rid, sess.user_id)).rowcount
        if not n:
            raise EngineError("not_found", "no such run", 404)
        return {"ok": True}
