"""问渠凸轮的 AI 起草（第 39 轮第 6 步，细则第十一节）：网关只负责调模型、认人、限次、留记录。

  POST /api/v1/cam/ai/draft      一句话要求 → 运动程序草稿（各段：升 / 停 / 回、转角、行程、规律、理由；没给的数留空）
  POST /api/v1/cam/ai/explain    校核结果 → 白话解释和修改建议
  POST /api/v1/cam/ai/describe   项目摘要 + 校核结果 → 计算书里的一段设计说明
  POST /api/v1/cam/ai/runs/{id}  凸轮服务回填这次草稿是否通过代码校验

调用方是凸轮服务（官网 /cam/），它转来用户的全站登录 cookie 或 Bearer；判定、校验、核对数字都在凸轮服务里由代码做，
网关不改项目。模型走统一的模型接口 ai.py：美国用 Claude，国内部署（region cn）自动用 DeepSeek。
每人每天上限 WQ_CAM_AI_DAILY（默认 30）。每次调用记一条：谁、哪个功能、输入摘要（前 200 字）、模型、耗时、是否通过校验。
数据：<data_dir>/cam_ai.db（SQLite）。
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

KINDS = ("draft", "explain", "describe")

DRAFT_SYSTEM = """You turn one requirement sentence for a cam into a draft motion program for the WenQuest Cam software.
The program is a list of segments over one camshaft turn (360°): rise, dwell, return. For an indexing cam (a turret
that advances and does not come back) the rises need not be cancelled by returns; the net advance per turn is given.
Rules — they matter more than anything else:
1. Never invent a number. Every angle, lift and advance you write must be stated in the sentence, or follow from it by
   plain arithmetic the sentence implies (e.g. "the rest of the turn" = 360 minus the angles given). Anything the
   sentence does not give, leave null and add a short question asking for it.
2. Motion laws are a design choice you may propose: pick from the allowed list and say why in one short line
   (speed, smoothness, impact). If the sentence names a law, use it.
3. Units: lifts in mm for a translating follower; angles of swing or index in degrees for an oscillating follower or
   an indexing turret (field h is then in degrees).
4. Keep the segments in the order of the camshaft turn, starting at 0°.
Answer only with the JSON object."""

EXPLAIN_SYSTEM = """You explain the deterministic checks of a cam design in plain words for an engineer.
Use only the numbers given in the check results, written as given; do not compute new numbers and do not invent
limits or standards. Say which checks fail or are unknown and why (unknown means data is missing, never a pass),
and suggest what the engineer could change (base radius, roller size, motion law, speed, eccentricity …) in words.
Keep it short: at most six sentences. Answer only with the JSON object."""

DESCRIBE_SYSTEM = """You write the design description paragraph of a cam calculation sheet: what the cam does, the motion
program and laws used, and the main check conclusions. Use only the numbers given, written as given; do not invent
numbers, limits, standards, materials or tolerances. Three to five sentences, neutral engineering tone.
Answer only with the JSON object."""


def draft_schema(laws: list[str]) -> dict:
    seg = {"type": "object", "additionalProperties": False,
           "properties": {"kind": {"type": "string", "enum": ["rise", "dwell", "return"]},
                          "deg": {"type": ["number", "null"]},
                          "h": {"type": ["number", "null"]},
                          "law": {"type": ["string", "null"], "enum": [*laws, None]},
                          "why": {"type": "string"}},
           "required": ["kind", "deg", "h", "law", "why"]}
    return {"type": "object", "additionalProperties": False,
            "properties": {"segments": {"type": "array", "items": seg},
                           "advance_deg": {"type": ["number", "null"]},
                           "assumptions": {"type": "array", "items": {"type": "string"}},
                           "questions": {"type": "array", "items": {"type": "string"}}},
            "required": ["segments", "advance_deg", "assumptions", "questions"]}


TEXT_SCHEMA = {"type": "object", "additionalProperties": False,
               "properties": {"sentences": {"type": "array", "items": {"type": "string"}}},
               "required": ["sentences"]}


class DraftIn(BaseModel):
    sentence: str = Field(min_length=2, max_length=600)
    follower: str = Field(default="translating", pattern="^(translating|oscillating|indexing)$")
    laws: list[str] = Field(default_factory=list, max_length=20)
    lang: str = Field(default="zh", pattern="^(zh|en)$")


class TextIn(BaseModel):
    title: str = Field(default="", max_length=200)
    summary: dict[str, Any] = Field(default_factory=dict)       # 程序、机构、转速（凸轮服务整理好的）
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
        c = sqlite3.connect(str(d / "cam_ai.db"), isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("create table if not exists runs(id integer primary key, ts real, user_id integer, kind text, "
                  "input text, provider text, ms integer, ok integer, passed integer, note text)")
        return c

    def daily() -> int:
        return int(getattr(state.settings, "cam_ai_daily", 30) or 30)

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

    async def run(sess: Session, kind: str, summary: str, **kw) -> tuple[dict, int, int]:
        """调一次模型；不管成败都记一条。返回 (模型的 JSON, 记录编号, 今天还剩几次)。"""
        if not state.ai.available:
            raise EngineError("ai_unavailable", "no AI model is configured", 503)
        left = quota(sess)
        t0 = time.time()
        ok, out = 0, {}
        try:
            out = await state.ai.json(**kw)
            ok = 1
        finally:
            with db() as c:
                rid = c.execute("insert into runs(ts,user_id,kind,input,provider,ms,ok) values(?,?,?,?,?,?,?)",
                                (t0, sess.user_id, kind, summary[:200], state.ai.provider,
                                 int((time.time() - t0) * 1000), ok)).lastrowid
        return out, rid, left - 1

    @app.post("/api/v1/cam/ai/draft")
    async def draft(body: DraftIn, sess: Annotated[Session, Depends(who)]):
        laws = body.laws or ["cycloidal", "mod_sine", "mod_trapezoid", "poly345", "poly4567"]
        unit = "mm" if body.follower == "translating" else "deg"
        prompt = (f"Follower: {body.follower} (lifts in {unit}). Allowed motion laws: {', '.join(laws)}.\n"
                  f"Write the assumptions and questions in {'Chinese' if body.lang == 'zh' else 'English'}.\n"
                  f"Requirement sentence:\n{body.sentence}")
        out, rid, left = await run(sess, "draft", body.sentence, system=DRAFT_SYSTEM, prompt=prompt,
                                   schema=draft_schema(laws), max_tokens=2000,
                                   fake=lambda: {"segments": [], "advance_deg": None, "assumptions": [],
                                                 "questions": ["(fake model)"]})
        return {"draft": out, "run": rid, "left_today": left, "model": state.ai.provider}

    async def text(kind: str, system: str, body: TextIn, sess: Session) -> dict:
        prompt = (f"Write in {'Chinese' if body.lang == 'zh' else 'English'}.\nCam: {body.title}\n"
                  f"Design summary (JSON): {json.dumps(body.summary, ensure_ascii=False)[:4000]}\n"
                  f"Check results (JSON): {json.dumps(body.checks, ensure_ascii=False)[:8000]}")
        out, rid, left = await run(sess, kind, body.title or kind, system=system, prompt=prompt, schema=TEXT_SCHEMA,
                                   max_tokens=1500, fake=lambda: {"sentences": ["(fake model)"]})
        return {"sentences": [str(s) for s in out.get("sentences") or []][:8], "run": rid, "left_today": left,
                "model": state.ai.provider}

    @app.post("/api/v1/cam/ai/explain")
    async def explain(body: TextIn, sess: Annotated[Session, Depends(who)]):
        return await text("explain", EXPLAIN_SYSTEM, body, sess)

    @app.post("/api/v1/cam/ai/describe")
    async def describe(body: TextIn, sess: Annotated[Session, Depends(who)]):
        return await text("describe", DESCRIBE_SYSTEM, body, sess)

    @app.post("/api/v1/cam/ai/runs/{rid}")
    async def verdict(rid: int, body: VerdictIn, sess: Annotated[Session, Depends(who)]):
        with db() as c:
            n = c.execute("update runs set passed=?, note=? where id=? and user_id=?",
                          (int(body.passed), body.note[:300], rid, sess.user_id)).rowcount
        if not n:
            raise EngineError("not_found", "no such run", 404)
        return {"ok": True}
