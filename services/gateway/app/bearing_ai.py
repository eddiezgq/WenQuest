"""问渠轴承的 AI 起草（第 64 轮第 7 步，细则第十五节）：网关只负责调模型、认人、限次、留记录。

  POST /api/v1/bearing/ai/draft      一句话 → 应用场景与载荷草稿（场景类型、句子里给了的字段的数；没给的留空）
  POST /api/v1/bearing/ai/explain    校核结果 → 白话解释和修改建议
  POST /api/v1/bearing/ai/describe   项目摘要 + 校核结果 → 计算书里的一段设计说明
  POST /api/v1/bearing/ai/runs/{id}  轴承服务回填这次是否通过代码检查

做法与问渠凸轮的 AI 起草（cam_ai.py）相同，不同的是**只给开通了企业授权的单位用**（Eddie 11-04 定 S2，与云端项目同一份授权，
m.sewing_who_web）。调用方是轴承服务（官网 /bearing/），它转来用户的全站登录 cookie 或 Bearer；字段校验、数字核对、跑校核
都在轴承服务里由代码做，网关不改项目。模型走统一的模型接口 ai.py：美国用 Claude，国内部署（region cn）自动用 DeepSeek。
每人每天上限 WQ_BEARING_AI_DAILY（默认 30，与凸轮分开计）。每次调用记一条：谁、单位、哪个功能、输入摘要（前 200 字）、模型、
耗时、是否通过检查。数据：<data_dir>/bearing_ai.db（SQLite）。
"""

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, Header, Request
from pydantic import BaseModel, Field

from .moodle import EngineError

DRAFT_SYSTEM = """You turn one sentence about where a rolling bearing is used into a draft of the application data for
the WenQuest Bearing software. You pick the application kind from the allowed list and fill the fields of that kind.
Rules — they matter more than anything else:
1. Never invent a number. Every number you write must be stated in the sentence, in the unit the field asks for.
   Do not convert units, do not estimate, do not use typical or handbook values. If the sentence gives a number in
   another unit, or does not give it at all, leave the field null and add a short question asking for it.
2. Choices that are words (which bearing is this one, A or B; the joint axis; inboard or outboard row) may be taken
   from the sentence; if the sentence does not say, leave them null.
3. Only use the field paths listed for the kind you chose. For load cases use paths cases.<i>.<column> (i from 0).
4. Never choose a bearing type, size or catalogue number.
Answer only with the JSON object."""

EXPLAIN_SYSTEM = """You explain the deterministic checks of a rolling bearing design in plain words for an engineer.
Use only the numbers given in the check results, written as given; do not compute new numbers and do not invent
limits, standards, catalogue data or ratings. Say which checks fail or are unknown and why (unknown means data is
missing, never a pass), and suggest in words what the engineer could change (clearance, fits, lubrication, a larger
or different bearing, the limits that still need filling in …). At most six sentences. Answer only with the JSON
object."""

DESCRIBE_SYSTEM = """You write the design description paragraph of a rolling bearing calculation sheet: where the
bearing is used, its type and main sizes, the load cases, and the main check conclusions. Use only the numbers given,
written as given; do not invent numbers, limits, standards, materials, ratings or tolerances. Three to five sentences,
neutral engineering tone. Answer only with the JSON object."""

DRAFT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "kind": {"type": "string"},
        "values": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "properties": {"path": {"type": "string"}, "value": {"type": ["number", "string", "null"]},
                           "quote": {"type": "string"}},
            "required": ["path", "value", "quote"]}},
        "assumptions": {"type": "array", "items": {"type": "string"}},
        "questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["kind", "values", "assumptions", "questions"],
}

TEXT_SCHEMA = {"type": "object", "additionalProperties": False,
               "properties": {"sentences": {"type": "array", "items": {"type": "string"}}},
               "required": ["sentences"]}


class DraftIn(BaseModel):
    sentence: str = Field(min_length=2, max_length=600)
    kinds: dict[str, Any] = Field(default_factory=dict)      # 轴承服务整理好的：每种场景的字段（路径、名称、单位、选项）
    bearing: str = Field(default="", max_length=40)
    lang: str = Field(default="zh", pattern="^(zh|en)$")


class TextIn(BaseModel):
    title: str = Field(default="", max_length=200)
    summary: dict[str, Any] = Field(default_factory=dict)
    checks: list[dict[str, Any]] = Field(default_factory=list, max_length=80)
    lang: str = Field(default="zh", pattern="^(zh|en)$")


class VerdictIn(BaseModel):
    passed: bool
    note: str = Field(default="", max_length=300)


def register(app, m) -> None:
    state = m.state

    def db() -> sqlite3.Connection:
        d = Path(state.settings.data_dir)
        d.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(str(d / "bearing_ai.db"), isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("create table if not exists runs(id integer primary key, ts real, user_id integer, org text, kind text, "
                  "input text, provider text, ms integer, ok integer, passed integer, note text)")
        return c

    def daily() -> int:
        try:
            return int(os.environ.get("WQ_BEARING_AI_DAILY") or 30)
        except ValueError:
            return 30

    async def who(req: Request, authorization: Annotated[str | None, Header()] = None) -> dict:
        """开通了企业授权的人（没登录 401，登录了没开通 403）。"""
        return await m.sewing_who_web(req, authorization)

    def quota(lic: dict) -> int:
        with db() as c:
            n = c.execute("select count(*) from runs where user_id=? and ts>?",
                          (int(lic["user_id"]), time.time() - 86400)).fetchone()[0]
        if n >= daily():
            raise EngineError("quota", f"today's AI drafts are used up ({daily()} a day)", 429)
        return daily() - n

    async def run(lic: dict, kind: str, summary: str, **kw) -> tuple[dict, int, int]:
        """调一次模型；不管成败都记一条。返回 (模型的 JSON, 记录编号, 今天还剩几次)。"""
        if not state.ai.available:
            raise EngineError("ai_unavailable", "no AI model is configured", 503)
        left = quota(lic)
        t0 = time.time()
        ok, out = 0, {}
        try:
            out = await state.ai.json(**kw)
            ok = 1
        finally:
            with db() as c:
                rid = c.execute("insert into runs(ts,user_id,org,kind,input,provider,ms,ok) values(?,?,?,?,?,?,?,?)",
                                (t0, int(lic["user_id"]), lic.get("org") or "", kind, summary[:200], state.ai.provider,
                                 int((time.time() - t0) * 1000), ok)).lastrowid
        return out, rid, left - 1

    @app.post("/api/v1/bearing/ai/draft")
    async def draft(body: DraftIn, lic: Annotated[dict, Depends(who)]):
        prompt = (f"Bearing type (fixed, do not change): {body.bearing}\n"
                  f"Allowed application kinds and their fields (JSON): "
                  f"{json.dumps(body.kinds, ensure_ascii=False)[:9000]}\n"
                  f"Write the assumptions and questions in {'Chinese' if body.lang == 'zh' else 'English'}.\n"
                  f"Sentence:\n{body.sentence}")
        out, rid, left = await run(lic, "draft", body.sentence, system=DRAFT_SYSTEM, prompt=prompt,
                                   schema=DRAFT_SCHEMA, max_tokens=2000,
                                   fake=lambda: {"kind": "generic", "values": [], "assumptions": [],
                                                 "questions": ["(fake model)"]})
        return {"draft": out, "run": rid, "left_today": left, "model": state.ai.provider}

    async def text(kind: str, system: str, body: TextIn, lic: dict) -> dict:
        prompt = (f"Write in {'Chinese' if body.lang == 'zh' else 'English'}.\nBearing: {body.title}\n"
                  f"Design summary (JSON): {json.dumps(body.summary, ensure_ascii=False)[:4000]}\n"
                  f"Check results (JSON): {json.dumps(body.checks, ensure_ascii=False)[:8000]}")
        out, rid, left = await run(lic, kind, body.title or kind, system=system, prompt=prompt, schema=TEXT_SCHEMA,
                                   max_tokens=1500, fake=lambda: {"sentences": ["(fake model)"]})
        return {"sentences": [str(s) for s in out.get("sentences") or []][:8], "run": rid, "left_today": left,
                "model": state.ai.provider}

    @app.post("/api/v1/bearing/ai/explain")
    async def explain(body: TextIn, lic: Annotated[dict, Depends(who)]):
        return await text("explain", EXPLAIN_SYSTEM, body, lic)

    @app.post("/api/v1/bearing/ai/describe")
    async def describe(body: TextIn, lic: Annotated[dict, Depends(who)]):
        return await text("describe", DESCRIBE_SYSTEM, body, lic)

    @app.post("/api/v1/bearing/ai/runs/{rid}")
    async def verdict(rid: int, body: VerdictIn, lic: Annotated[dict, Depends(who)]):
        with db() as c:
            n = c.execute("update runs set passed=?, note=? where id=? and user_id=?",
                          (int(body.passed), body.note[:300], rid, int(lic["user_id"]))).rowcount
        if not n:
            raise EngineError("not_found", "no such run", 404)
        return {"ok": True}
