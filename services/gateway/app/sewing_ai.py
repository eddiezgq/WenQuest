"""缝纫机设计软件的 AI 助手（第 49 轮，细则第七节 1）：AI 起草，计算核心把关，人拍板。

  POST /api/v1/sewing/ai/draft      一句话要求 → 改哪几个参数、改成多少、为什么；网关用计算核心重算，红灯变多就让 AI 再改一次，
                                    还不行就退回（status = rejected）。只给对照，不改项目——人点“采用”才回填
  POST /api/v1/sewing/ai/explain    当前红黄灯 → 白话原因和改法；每条改法用计算核心试算，标出能不能消掉这盏灯
  POST /api/v1/sewing/ai/describe   计算书的“设计说明”；句子里的每个数都要在这组设计的参数、结果、校核里找得到，找不到的句子删掉

谁能用：已开通的企业（网页登录凭证或 FreeCAD 钥匙）。每人每天 WQ_SEWING_AI_DAILY 次（默认 30），每次记一条
（谁、功能、输入前 200 字、模型、耗时、是否通过程序把关）。模型走 ai.py：国内部署 DeepSeek，美国 Claude；
没配模型时用规则版（起草认“参数名 + 数字”，解释用校核自带的改法，设计说明用模板句），照样能用。
数据：<data_dir>/sewing_ai.db（SQLite）。
"""

import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends
from pydantic import BaseModel, Field

from . import sewcore
from .moodle import EngineError
from .sewcore import aicheck

MACHINE_RE = "^(lockstitch|overlock|cover|pattern|embroid)$"
SKIP = {"pts"}                      # 花样机上传的针位表：不让 AI 改

DRAFT_SYSTEM = """You help an engineer change a sewing-machine design in the WenQuest design software.
You get the current parameters (key, name, unit, allowed range, current value), the current check results, and one
requirement sentence. Answer with the parameter changes that meet the requirement.
Rules — they matter more than anything else:
1. Change only keys from the list, and as few as you can. Keep every value inside its allowed range.
2. A number the sentence states (a speed, a stitch length …) must be used exactly as stated.
3. Other values are your engineering proposal: say in one short line why (which check it protects or fixes).
4. The software recomputes every check after your answer; it rejects drafts that add failing checks. If you are told
   which checks failed after your last draft, fix them without dropping what the sentence asked for.
5. If the sentence asks for something the parameters cannot express, say so in questions instead of guessing.
Write `why`, assumptions and questions in Chinese. Answer only with the JSON object."""

EXPLAIN_SYSTEM = """You explain failing or warning checks of a sewing-machine design in plain Chinese for an engineer.
For each check given: why it fails (use only the numbers given, written as given; do not invent limits or standards),
and one to three fixes, each a single parameter change (key from the list, value inside its range) with one short line.
The software tries every fix and tells the engineer whether it clears the check. Answer only with the JSON object."""

DESCRIBE_SYSTEM = """You write the "design description" paragraph of a sewing-machine calculation sheet in Chinese:
what machine this is, the main design choices, and the check conclusions. Use only numbers that appear in the data
given, written as given (rounding is allowed); do not invent numbers, limits, standards, materials or tolerances.
Every sentence with a number that is not in the data is deleted by the software. Three to six sentences, neutral
engineering tone. Answer only with the JSON object."""

TEXT_SCHEMA = {"type": "object", "additionalProperties": False,
               "properties": {"sentences": {"type": "array", "items": {"type": "string"}}},
               "required": ["sentences"]}


def draft_schema(keys: list[str]) -> dict:
    ch = {"type": "object", "additionalProperties": False,
          "properties": {"key": {"type": "string", "enum": keys}, "value": {"type": ["number", "string"]}, "why": {"type": "string"}},
          "required": ["key", "value", "why"]}
    return {"type": "object", "additionalProperties": False,
            "properties": {"changes": {"type": "array", "items": ch},
                           "assumptions": {"type": "array", "items": {"type": "string"}},
                           "questions": {"type": "array", "items": {"type": "string"}}},
            "required": ["changes", "assumptions", "questions"]}


def explain_schema(checks: list[str], keys: list[str]) -> dict:
    fix = {"type": "object", "additionalProperties": False,
           "properties": {"key": {"type": "string", "enum": keys}, "value": {"type": ["number", "string"]}, "how": {"type": "string"}},
           "required": ["key", "value", "how"]}
    it = {"type": "object", "additionalProperties": False,
          "properties": {"check": {"type": "string", "enum": checks}, "why": {"type": "string"}, "fixes": {"type": "array", "items": fix}},
          "required": ["check", "why", "fixes"]}
    return {"type": "object", "additionalProperties": False, "properties": {"items": {"type": "array", "items": it}}, "required": ["items"]}


class AiIn(BaseModel):
    machine: str = Field(default="lockstitch", pattern=MACHINE_RE)
    params: dict[str, Any] = Field(default_factory=dict)
    sentence: str = Field(default="", max_length=600)


# ---------- 计算核心把关（纯函数，单元测试直接调） ----------

def spec_of(M) -> dict:
    """key → (中文名, 单位, 最小, 最大, 选项键列表)"""
    out = {}
    for _g, _gzh, _gen, items in M.GROUPS:
        for k, zh, _en, unit, _d, lo, hi, _st in items:
            if k in SKIP:
                continue
            out[k] = (zh, unit, lo, hi, [c[0] for c in M.CHOICES.get(k, [])])
    return out


def counts(R) -> dict:
    cs = R["checks"]
    return {"ok": sum(c["state"] == "ok" for c in cs), "warn": sum(c["state"] == "warn" for c in cs),
            "bad": sum(c["state"] == "bad" for c in cs), "all": len(cs)}


def bad_keys(R) -> set:
    return {c["key"] for c in R["checks"] if c["state"] == "bad"}


def check_brief(R, states=("bad", "warn")) -> list[dict]:
    return [{"key": c["key"], "name": c["name"]["zh"], "state": c["state"], "value": c["value"]["zh"], "limit": c["limit"]["zh"],
             "advice": c["advice"]["zh"]} for c in R["checks"] if c["state"] in states]


def apply_changes(M, base: dict, changes: list[dict]) -> tuple[dict, list[dict]]:
    """把改动夹进范围后用到参数上。返回 (新参数, 对照行)。不认识的键、选项外的值丢掉并说明。"""
    sp = spec_of(M)
    p = dict(base)
    rows = []
    for ch in changes or []:
        k = str(ch.get("key", ""))
        if k not in sp:
            continue
        zh, unit, lo, hi, opts = sp[k]
        v, note = ch.get("value"), ""
        if opts:
            if v not in opts:
                rows.append({"key": k, "name": zh, "unit": unit, "old": base.get(k), "new": base.get(k), "why": ch.get("why") or ch.get("how") or "",
                             "note": "不是可选的值，没改"})
                continue
        else:
            try:
                v = float(v)
            except (TypeError, ValueError):
                continue
            if lo is not None and (v < lo or v > hi):
                note = f"超出范围 {lo}–{hi}，已夹到边上"
                v = min(hi, max(lo, v))
            v = round(v, 6)
            if v == int(v):
                v = int(v)
        p[k] = v
        rows.append({"key": k, "name": zh, "unit": unit, "old": base.get(k), "new": v, "why": ch.get("why") or ch.get("how") or "", "note": note})
    return M.clean(p), rows


def judge(R0, R1) -> tuple[bool, list[dict]]:
    """通过 = 没有新增红灯（原来就红的可以还红）。返回 (是否通过, 新增的红灯)"""
    new = bad_keys(R1) - bad_keys(R0)
    return not new, [c for c in check_brief(R1, ("bad",)) if c["key"] in new]


_ALIAS = {"lockstitch": {"转速": "n", "针距": "s", "曲柄": "r", "连杆": "l", "平衡率": "k", "底线张力": "Tb", "夹线器张力": "Td", "张力": "Td",
                         "针杆质量": "mr", "梭尖间隙": "g", "机针直径": "d", "固有频率": "fn"},
          "overlock": {"转速": "n", "针距": "s", "差动比": "D", "曲柄": "r", "连杆": "l", "布厚": "t"},
          "cover": {"转速": "n", "针密": "spc", "针距": "g", "件数": "Q", "缝长": "Lcm", "损耗": "W"},
          "pattern": {"转速": "n", "针距": "s", "机头最高转速": "n_head"},
          "embroid": {"头数": "H", "转速": "n", "针长": "s", "缎纹宽": "s"}}


def rule_draft(M, sentence: str) -> list[dict]:
    """没配模型时的起草：句子里“参数名（或常用叫法）+ 数字”。"""
    sp = spec_of(M)
    names = {}
    for k, (zh, *_rest) in sp.items():
        names[re.sub(r"[（(].*?[)）]", "", zh).strip()] = k
    names.update(_ALIAS.get(M.MACHINE, {}))
    out, seen = [], set()
    for name in sorted(names, key=len, reverse=True):
        for mt in re.finditer(re.escape(name) + r"[^0-9\-，。；,;]{0,8}?(-?\d+(?:\.\d+)?)", sentence):
            k = names[name]
            if k in seen or sp[k][4]:
                continue
            seen.add(k)
            out.append({"key": k, "value": float(mt.group(1)), "why": f"句子里写的“{name} {mt.group(1)}”"})
    return out


def rule_describe(M, R) -> list[str]:
    c = counts(R)
    p = R["params"]
    s = [f"本设计为{M.NAME[0]}" + (f"，设计转速 {p['n']} r/min。" if "n" in p else "。")]
    if c["bad"] == 0 and c["warn"] == 0:
        s.append(f"全部 {c['all']} 项校核合格。")
    else:
        s.append(f"{c['all']} 项校核中，合格 {c['ok']} 项、需注意 {c['warn']} 项、不合格 {c['bad']} 项。")
        bad = [x["name"] for x in check_brief(R, ("bad",))]
        if bad:
            s.append("不合格的是：" + "、".join(bad) + "。")
    return s


def register(app, m) -> None:
    state = m.state

    def db() -> sqlite3.Connection:
        d = Path(state.settings.data_dir)
        d.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(str(d / "sewing_ai.db"), isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("create table if not exists runs(id integer primary key, ts real, user_id integer, org text, kind text, "
                  "input text, provider text, ms integer, ok integer, passed integer)")
        return c

    def daily() -> int:
        return int(getattr(state.settings, "sewing_ai_daily", 30) or 30)

    def quota(lic: dict) -> int:
        with db() as c:
            n = c.execute("select count(*) from runs where user_id=? and ts>?", (lic["user_id"], time.time() - 86400)).fetchone()[0]
        if n >= daily():
            raise EngineError("quota", f"today's AI uses are used up ({daily()} a day)", 429)
        return daily() - n

    def log(lic, kind, text, provider, t0, ok, passed) -> int:
        with db() as c:
            return c.execute("insert into runs(ts,user_id,org,kind,input,provider,ms,ok,passed) values(?,?,?,?,?,?,?,?,?)",
                             (t0, lic["user_id"], lic["org"], kind, text[:200], provider, int((time.time() - t0) * 1000), int(ok),
                              None if passed is None else int(passed))).lastrowid

    async def model(**kw) -> dict | None:
        """有模型就调；没配模型返回 None（走规则版）。"""
        if not state.ai.available:
            return None
        return await state.ai.json(**kw)

    def provider() -> str:
        return state.ai.provider if state.ai.available else "rules"

    def table(M, p) -> str:
        sp = spec_of(M)
        rows = []
        for k, (zh, unit, lo, hi, opts) in sp.items():
            rng = "/".join(opts) if opts else f"{lo}–{hi}"
            rows.append(f"{k}\t{zh}\t{unit}\t{rng}\t{p.get(k)}")
        return "key\tname\tunit\trange\tcurrent\n" + "\n".join(rows)

    # ---------- 起草 ----------
    @app.post("/api/v1/sewing/ai/draft")
    async def draft(body: AiIn, lic: Annotated[dict, Depends(m.sewing_who)]):
        if len(body.sentence.strip()) < 2:
            raise EngineError("empty", "write what you want first", 400)
        left = quota(lic)
        M = sewcore.get(body.machine)
        p0 = M.clean(body.params)
        R0 = M.analyze(p0)
        keys = list(spec_of(M))
        t0 = time.time()
        rounds, out, ok = 0, {}, False
        R1, rows = R0, []
        changes, assumptions, questions = [], [], []
        feedback = ""
        try:
            for rounds in (1, 2):
                prompt = (f"Machine: {M.NAME[0]} ({M.MACHINE}).\nParameters:\n{table(M, p0)}\n"
                          f"Current checks that fail or warn (JSON): {json.dumps(check_brief(R0), ensure_ascii=False)[:6000]}\n"
                          f"Requirement sentence:\n{body.sentence}\n{feedback}")
                out = await model(system=DRAFT_SYSTEM, prompt=prompt, schema=draft_schema(keys), max_tokens=2500,
                                  fake=lambda: {"changes": rule_draft(M, body.sentence), "assumptions": [], "questions": []})
                if out is None:                         # 规则版
                    out = {"changes": rule_draft(M, body.sentence), "assumptions": [], "questions": [] if rule_draft(M, body.sentence)
                           else ["没认出参数名和数字。没配大模型时，请写成“转速 6000”“针距 4”这样。"]}
                changes = out.get("changes") or []
                assumptions, questions = out.get("assumptions") or [], out.get("questions") or []
                p1, rows = apply_changes(M, p0, changes)
                R1 = M.analyze(p1)
                ok, new_bad = judge(R0, R1)
                if ok or provider() == "rules":
                    break
                feedback = ("Your last draft was rejected: these checks failed that did not fail before (JSON): "
                            f"{json.dumps(new_bad, ensure_ascii=False)}. Your last changes: {json.dumps(changes, ensure_ascii=False)}. "
                            "Give a corrected full list of changes.")
        except EngineError:
            log(lic, "draft", body.sentence, provider(), t0, False, None)
            raise
        rid = log(lic, "draft", body.sentence, provider(), t0, True, ok)
        new_bad = judge(R0, R1)[1]
        return {"status": "ok" if ok else "rejected", "rounds": rounds, "changes": rows, "params": p1 if ok else None,
                "before": counts(R0), "after": counts(R1), "new_bad": new_bad, "after_bad": check_brief(R1, ("bad",)),
                "assumptions": [str(x) for x in assumptions][:6], "questions": [str(x) for x in questions][:6],
                "run": rid, "left_today": left - 1, "model": provider()}

    # ---------- 解释红黄灯 ----------
    @app.post("/api/v1/sewing/ai/explain")
    async def explain(body: AiIn, lic: Annotated[dict, Depends(m.sewing_who)]):
        M = sewcore.get(body.machine)
        p0 = M.clean(body.params)
        R0 = M.analyze(p0)
        bw = check_brief(R0)
        if not bw:
            return {"items": [], "all_ok": True, "model": "", "left_today": None}
        left = quota(lic)
        keys = list(spec_of(M))
        t0 = time.time()
        try:
            out = await model(system=EXPLAIN_SYSTEM, schema=explain_schema([c["key"] for c in bw], keys), max_tokens=3000,
                              prompt=f"Machine: {M.NAME[0]}.\nParameters:\n{table(M, p0)}\nChecks to explain (JSON): {json.dumps(bw, ensure_ascii=False)}",
                              fake=lambda: {"items": [{"check": c["key"], "why": c["advice"], "fixes": []} for c in bw]})
        except EngineError:
            log(lic, "explain", "", provider(), t0, False, None)
            raise
        if out is None:
            out = {"items": [{"check": c["key"], "why": c["advice"] or "按判据调整对应参数。", "fixes": []} for c in bw]}
        items = []
        names = {c["key"]: c for c in bw}
        for it in out.get("items") or []:
            c = names.get(it.get("check"))
            if not c:
                continue
            fixes = []
            for fx in (it.get("fixes") or [])[:3]:
                p1, rows = apply_changes(M, p0, [fx])
                if not rows:
                    continue
                R1 = M.analyze(p1)
                st = next((x["state"] for x in R1["checks"] if x["key"] == c["key"]), "ok")
                ok, new_bad = judge(R0, R1)
                fixes.append({**rows[0], "how": fx.get("how", ""), "clears": st == "ok", "becomes": st, "new_bad": [x["name"] for x in new_bad],
                              "params": p1 if ok else None})
            items.append({"check": c["key"], "name": c["name"], "state": c["state"], "value": c["value"], "limit": c["limit"],
                          "why": str(it.get("why") or ""), "fixes": fixes})
        rid = log(lic, "explain", ",".join(c["key"] for c in bw), provider(), t0, True, None)
        return {"items": items, "all_ok": False, "run": rid, "left_today": left - 1, "model": provider()}

    # ---------- 设计说明 ----------
    @app.post("/api/v1/sewing/ai/describe")
    async def describe(body: AiIn, lic: Annotated[dict, Depends(m.sewing_who)]):
        left = quota(lic)
        M = sewcore.get(body.machine)
        p0 = M.clean(body.params)
        R0 = M.analyze(p0)
        data = {"machine": M.NAME[0], "params": {spec_of(M).get(k, (k,))[0]: v for k, v in p0.items() if k not in SKIP},
                "results": [{"name": r["zh"], "value": r["value"], "unit": r["unit"]} for r in R0["results"]],
                "checks": [{"name": c["name"]["zh"], "state": c["state"], "value": c["value"]["zh"], "limit": c["limit"]["zh"]} for c in R0["checks"]],
                "counts": counts(R0)}
        t0 = time.time()
        try:
            out = await model(system=DESCRIBE_SYSTEM, schema=TEXT_SCHEMA, max_tokens=1500,
                              prompt=f"Design data (JSON): {json.dumps(data, ensure_ascii=False)[:12000]}",
                              fake=lambda: {"sentences": rule_describe(M, R0)})
        except EngineError:
            log(lic, "describe", "", provider(), t0, False, None)
            raise
        sent = (out or {}).get("sentences") if out is not None else rule_describe(M, R0)
        keep, drop = aicheck.verify([str(x) for x in (sent or [])][:8], R0, M.NAME[0])
        rid = log(lic, "describe", M.MACHINE, provider(), t0, True, not drop)
        return {"sentences": keep, "dropped": drop, "run": rid, "left_today": left - 1, "model": provider()}
