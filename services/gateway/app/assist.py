"""问渠客服（第 87 轮）：每一页右下角“问问问渠”的接口。

知识库 app/assist_kb.json 由 tools/assistant/build_kb.py 从帮助文件、首页清单、国内版官网文字稿生成。
两档：
  检索档（免费，两站都有）：按问题找出最相关的几段，返回摘要和出处链接，不调用大模型。
  AI 档：检索后由模型只依据这几段组织回答、附出处。美国站（region us）直接开；国内站（region cn）只有在
         .env 填了 WQ_AI_REG（网信办登记编号）后才开，并且只用 DeepSeek。每天调用次数有上限
         （WQ_ASSIST_AI_DAILY，默认 300），超了自动退回检索档。
国内站只用标了 cn 的段落（不含国内版官网禁用词），出处不给链接（帮助网页不上国内站）。

  POST /api/v1/public/assist       不用登录；每个网络地址每小时 20 问
  GET  /api/v1/admin/assist-log    管理员：最近的提问，?missed=1 只看没答上的（用来补帮助文件）

记录只存时间、问题、页面、档位、有没有答上，不存网络地址。
"""

import json
import math
import os
import re
import time
from collections import Counter, deque
from pathlib import Path
from typing import Annotated

from fastapi import Depends, Request
from pydantic import BaseModel, Field

from .moodle import EngineError
from .session import Session

KB_FILE = Path(__file__).with_name("assist_kb.json")
IP_HOURLY = 20
TOP = 4
WORD = re.compile(r"[a-z0-9]+(?:[.+#-][a-z0-9]+)*")
HAN = re.compile(r"[一-鿿]+")
# 同义词：问法和资料里的写法不一样时，把问法补上资料里的词
SYN = {
    "ppt": "课件", "slides": "课件", "lecture": "课件 讲解视频", "courseware": "课件", "textbook": "教材", "book": "教材",
    "factory": "数字工厂", "erp": "ERP 经营 质量", "plc": "PLC", "cam": "数控编程 CAM", "g-code": "数控编程 G代码",
    "gcode": "数控编程 G代码", "g代码": "数控编程 G代码", "cae": "仿真 有限元", "fea": "有限元", "cfd": "流体", "whiteboard": "白板课", "video": "视频",
    "sewing": "缝纫机", "cam-design": "凸轮", "bearing": "轴承", "login": "登录 账号", "account": "账号", "price": "预约演示 联系",
    "cost": "预约演示 联系", "contact": "联系 预约演示", "demo": "演示", "course": "课程", "ai": "AI", "quiz": "测验",
    "exam": "考试", "homework": "作业", "assignment": "作业", "student": "学生", "teacher": "老师 教师", "robot": "机器人",
    "evaluation": "评价", "accreditation": "认证 评估", "digital twin": "数字孪生", "parts": "零件库", "library": "库",
    "多少钱": "预约演示 联系", "价格": "预约演示 联系", "收费": "预约演示 联系", "报价": "预约演示 联系",
    "ppt课件": "网页互动课件", "放映": "课件演示", "能耗": "能源", "零件库": "零件与机器人库", "试用": "体验 开通", "注册": "账号 登录 开通", "开通": "开通 账号",
}
STOP = set("的 了 是 在 我 你 他 怎么 什么 如何 吗 呢 啊 吧 有 和 与 及 a an the to of in on for is are do does how what can i my "
           "you your it with and or be this that which where".split())

STOP |= set("怎 么 什 如 何 吗 呢 吧 啊 哪 里 个 要 能 可 以 会 这 那 些 们 吗 么 请 问 想 用".split())
STOP1 = set("怎么什如何吗呢吧啊哪里个要能可以会这那些们请问想用的了是在我你有和与及".replace(" ", ""))

SYSTEM = {
    "zh": ("你是问渠（WenQuest）的客服。只依据下面给出的资料段落回答用户的问题，用中文，简短、直接、分点不超过 5 条。"
           "资料里没有的内容不要编：把 unsure 设为 true，并建议用户通过“联系我们 / 预约演示”咨询。"
           "不报价格（价格一律请预约演示）、不承诺资料里没写的功能、不索要身份证号等个人信息。"
           "used 填你实际依据的段落编号。"),
    "en": ("You are the customer assistant for WenQuest (问渠). Answer ONLY from the passages below, in English, briefly and "
           "directly (at most 5 points). Passages may be in Chinese; translate what you use. If the passages do not contain the "
           "answer, do not make it up: set unsure to true and suggest contacting us / booking a demo. Never quote prices "
           "(prices: book a demo), never promise features the passages do not state, never ask for ID numbers or other personal "
           "data. Put the numbers of the passages you actually used in used."),
}
SCHEMA = {"type": "object", "properties": {"answer": {"type": "string"}, "used": {"type": "array", "items": {"type": "integer"}},
                                           "unsure": {"type": "boolean"}}, "required": ["answer", "used", "unsure"]}


def tokens(text: str) -> list[str]:
    """中文按单字 + 相邻两字，英文按词；问题和资料用同一套切法"""
    t = text.lower()
    out = [w for w in WORD.findall(t) if w not in STOP]
    for run in HAN.findall(t):
        out += [c for c in run if c not in STOP]
        out += [b for b in (run[i:i + 2] for i in range(len(run) - 1)) if b not in STOP and not (b[0] in STOP1 and b[1] in STOP1)]
    return out


def expand(q: str) -> str:
    low = q.lower()
    extra = [v for k, v in SYN.items() if k in low]
    return q + " " + " ".join(extra)


class Index:
    """BM25；标题、小节名算两遍（权重更高）"""

    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.docs = [Counter(tokens((c["title"] + " " + c.get("section", "")) * 2 + " " + c["text"])) for c in chunks]
        self.titles = [(c["title"] + " " + c.get("section", "")).lower() for c in chunks]
        self.len = [sum(d.values()) for d in self.docs]
        self.avg = (sum(self.len) / len(self.len)) if self.len else 1
        df: Counter = Counter()
        for d in self.docs:
            df.update(d.keys())
        n = len(self.docs)
        self.idf = {w: math.log(1 + (n - f + 0.5) / (f + 0.5)) for w, f in df.items()}

    def search(self, q: str, k: int = TOP, page: str = "") -> list[tuple[float, dict]]:
        qt = Counter(tokens(expand(q)))
        if not qt:
            return []
        scored = []
        for i, d in enumerate(self.docs):
            s = 0.0
            for w, qn in qt.items():
                f = d.get(w)
                if f:
                    s += self.idf[w] * f * 2.2 / (f + 1.2 * (0.25 + 0.75 * self.len[i] / self.avg)) * (1 + 0.3 * (qn - 1))
            if s:                                      # 问题里的词出现在资料标题里：多半就是这篇
                tt = self.titles[i]
                s *= 1 + 0.6 * sum(1 for w in qt if len(w) >= 2 and w in tt)
            if s and page and self.chunks[i].get("url") and page.startswith(self.chunks[i]["url"].rstrip("/") or "#"):
                s *= 1.25                              # 用户所在的页面就是这段资料的出处：先按这一块答
            if s:
                scored.append((s, self.chunks[i]))
        scored.sort(key=lambda x: -x[0])
        # 同一篇资料最多两段，免得前几条都是一篇
        out, per = [], Counter()
        for s, c in scored:
            if per[c["doc"]] >= 2:
                continue
            per[c["doc"]] += 1
            out.append((s, c))
            if len(out) >= k:
                break
        return out


def load_index(region: str) -> Index:
    chunks = json.loads(KB_FILE.read_text(encoding="utf-8"))["chunks"] if KB_FILE.exists() else []
    if region == "cn":
        chunks = [{**c, **{k: c[k + "_cn"] for k in ("text", "title", "section") if k + "_cn" in c}} for c in chunks if c.get("cn")]
    else:
        chunks = [c for c in chunks if c.get("us", True)]
    return Index(chunks)


def snippet(text: str, q: str, n: int = 160) -> str:
    """摘出资料里和问题最沾边的一小段"""
    qt = set(tokens(q))
    best, at = -1, 0
    for i in range(0, max(1, len(text) - n), 40):
        part = text[i:i + n]
        hit = len(qt & set(tokens(part)))
        if hit > best:
            best, at = hit, i
    s = text[at:at + n].strip()
    return ("…" if at else "") + s + ("…" if at + n < len(text) else "")


class AskIn(BaseModel):
    q: str = Field(min_length=1, max_length=300)
    page: str = Field(default="", max_length=300)
    lang: str = Field(default="", max_length=10)
    ai: bool = True                                    # 用户可以只要检索结果


def register(app, m) -> None:
    state = m.state
    hits: dict[str, deque] = {}
    day = {"d": "", "n": 0}
    cache: dict[str, Index] = {}

    def region() -> str:
        return (state.settings.region or "us").strip().lower()

    def index() -> Index:
        r = region()
        if r not in cache:
            cache[r] = load_index(r)
        return cache[r]

    def ai_allowed() -> bool:
        if not state.ai.available:
            return False
        if region() == "cn" and not (state.settings.ai_reg or "").strip():
            return False                               # 网信办登记之前，国内站只用检索档
        cap = int(os.environ.get("WQ_ASSIST_AI_DAILY", "300") or 0)
        today = time.strftime("%Y-%m-%d")
        if day["d"] != today:
            day.update(d=today, n=0)
        return day["n"] < cap

    def log(row: dict) -> None:
        try:
            d = Path(state.settings.data_dir)
            d.mkdir(parents=True, exist_ok=True)
            with open(d / "assist-log.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        except OSError:
            pass

    def ip(req: Request) -> str:
        fwd = req.headers.get("x-forwarded-for", "")
        return (fwd.split(",")[0].strip() if fwd else (req.client.host if req.client else "")) or "?"

    @app.post("/api/v1/public/assist")
    async def ask(body: AskIn, req: Request):
        lang = "zh" if (body.lang or "zh").lower().startswith("zh") else "en"
        now = time.time()
        h = hits.setdefault(ip(req), deque())
        while h and now - h[0] > 3600:
            h.popleft()
        if len(h) >= IP_HOURLY:
            raise EngineError("rate_limited", "问得太快了，请过一会儿再问" if lang == "zh" else
                              "Too many questions — please try again later", 429)
        h.append(now)
        q = body.q.strip()
        cn = region() == "cn"
        found = index().search(q, page=body.page)
        sources = [{"title": c["title"] + (f" · {c['section']}" if c.get("section") else ""),
                    "url": None if cn else c.get("url"), "snippet": snippet(c["text"], q)} for _, c in found]
        out = {"mode": "search", "answer": "", "sources": sources, "unsure": not found, "ai_label": False,
               "region": "cn" if cn else "us", "contact": "/contact/" if cn else "/#contact"}
        if found and body.ai and ai_allowed():
            day["n"] += 1
            passages = "\n\n".join(f"[{i + 1}] {c['title']} {c.get('section', '')}\n{c['text']}" for i, (_, c) in enumerate(found))
            fake = {"answer": ("（演示）" if lang == "zh" else "(demo) ") + found[0][1]["text"][:200], "used": [1], "unsure": False}
            try:
                r = await state.ai.json(system=SYSTEM[lang], prompt=f"资料段落：\n{passages}\n\n用户问题（在页面 {body.page or '未知'}）：{q}",
                                        schema=SCHEMA, max_tokens=900, fake=fake)
                used = [i - 1 for i in r.get("used") or [] if isinstance(i, int) and 1 <= i <= len(sources)]
                out.update(mode="ai", answer=str(r.get("answer", ""))[:2000], unsure=bool(r.get("unsure")), ai_label=True,
                           sources=[sources[i] for i in used] or sources[:2])
            except Exception:                          # 模型出错：退回检索档，照样有答案
                pass
        log({"ts": int(now), "q": q, "page": body.page[:200], "lang": lang, "mode": out["mode"], "answered": not out["unsure"],
             "top": found[0][1]["doc"] if found else ""})
        return out

    @app.get("/api/v1/admin/assist-log")
    async def assist_log(sess: Annotated[Session, Depends(m.current)], missed: int = 0, limit: int = 200):
        await m.accounts_require_admin(sess)
        f = Path(state.settings.data_dir) / "assist-log.jsonl"
        rows = []
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines()[-5000:]:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if r.get("ts", 0) < time.time() - 30 * 86400:  # 记录只看 30 天
                    continue
                if missed and r.get("answered"):
                    continue
                rows.append(r)
        rows = rows[::-1][:max(1, min(limit, 1000))]
        return {"count": len(rows), "rows": rows}
