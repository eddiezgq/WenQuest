"""讲稿（第 22 轮）：读 docs/课程视频/<课>/<节>/讲稿.yaml，填入程序输出的数字，拆成配音句与字幕句，检查结构。

讲稿格式见 tools/video/README.md。要点：
  - shots: 一个镜头一种画面（title / slide / anim / code / lab / clip / homework / outro）；
  - say.zh / say.en: 每行一句配音、一条字幕；行首 “>” = 说这句之前画面进入下一步；两种语言 “>” 个数相同；
  - “[字幕|读法]”：字幕显示前者，配音读后者；
  - {{程序.键:格式}}：运行教材 code/ 里的程序得到，不手写数字。
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
TEXTBOOK = ROOT / "textbook"
# 网页版教材（第 23 轮）：一讲 = 课程包一讲（一章），section 写讲号（如 "2"）；程序在 course/calc/chNN.py，
# 插图在 img/（英文 img/en/），实验与动画页在 src/<语言>/labs/，作业取课程包 assignment
WEB = {p.name: p for p in sorted((TEXTBOOK / "web-editions").iterdir()) if (p / "course").is_dir()}   # 第 29 轮起：有课程包的网页版教材都可以
KINDS = {"title", "slide", "anim", "code", "lab", "clip", "homework", "outro", "deck"}
LANGS = ("zh", "en")
PH = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\s*(?::([^}]*))?\}\}")
DUAL = re.compile(r"\[([^\[\]|]+)\|([^\[\]]+)\]")


class ScriptError(Exception):
    pass


@dataclass
class Line:
    shown: str          # 字幕
    spoken: str         # 配音
    step: bool          # 说之前画面进入下一步


@dataclass
class Shot:
    id: str
    kind: str
    data: dict
    lines: dict = field(default_factory=dict)   # lang -> [Line]

    def steps(self, lang: str) -> int:
        return sum(1 for ln in self.lines[lang] if ln.step)


@dataclass
class Lecture:
    dir: Path
    book: str
    section: str
    chapter_no: int
    data: dict
    shots: list
    values: dict

    def t(self, pair, lang):
        """[zh, en] → text in lang."""
        if isinstance(pair, (list, tuple)):
            return pair[0] if lang == "zh" else (pair[1] if len(pair) > 1 else pair[0])
        return str(pair)

    @property
    def web(self) -> Path | None:
        return WEB.get(self.book)

    @property
    def code_dir(self) -> Path:
        if self.book in WEB:
            return WEB[self.book] / "course" / "calc"
        return TEXTBOOK / self.book / f"ch{self.chapter_no:02d}" / "code"

    @property
    def ch_dir(self) -> Path:
        return TEXTBOOK / self.book / f"ch{self.chapter_no:02d}"


def run_programs(book: str, ch: int, names: list[str]) -> dict:
    """Run the textbook programs that the script quotes; {name: {key: value}} (same values the book prints)."""
    code = WEB[book] / "course" / "calc" if book in WEB else TEXTBOOK / book / f"ch{ch:02d}" / "code"
    out = {}
    for n in names:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        env = dict(os.environ, WQ_BOOK_OUT=path, MPLBACKEND="Agg",
                   PYTHONPATH=os.pathsep.join([str(TEXTBOOK / "tools"), str(code), os.environ.get("PYTHONPATH", "")]))
        r = subprocess.run([sys.executable, f"{n}.py"], cwd=code, env=env, capture_output=True, text=True, timeout=600)
        if r.returncode:
            raise ScriptError(f"程序 {n}.py 运行失败：{r.stderr.strip()[-600:]}")
        out[n] = json.loads(Path(path).read_text(encoding="utf-8") or "{}")
        os.unlink(path)
    return out


def fill(text: str, values: dict, where: str) -> str:
    def rep(m):
        prog, key, fmt = m.group(1), m.group(2), m.group(3)
        if prog not in values or key not in values[prog]:
            raise ScriptError(f"{where}：{{{{{prog}.{key}}}}} 没有对应的程序输出")
        v = values[prog][key]
        if fmt:
            try:
                return format(v, fmt)
            except (TypeError, ValueError) as e:
                raise ScriptError(f"{where}：{{{{{prog}.{key}:{fmt}}}}} 格式不对：{e}") from e
        return str(v)
    return PH.sub(rep, text)


def split_line(raw: str) -> Line:
    s = raw.strip()
    step = s.startswith(">")
    if step:
        s = s[1:].strip()
    shown = DUAL.sub(lambda m: m.group(1), s)
    spoken = DUAL.sub(lambda m: m.group(2), s)
    return Line(shown=shown, spoken=spoken, step=step)


def fill_tree(x, values, where):
    if isinstance(x, str):
        return fill(x, values, where)
    if isinstance(x, list):
        return [fill_tree(i, values, where) for i in x]
    if isinstance(x, dict):
        return {k: fill_tree(v, values, where) for k, v in x.items()}
    return x


def load(lecture_dir: str | Path) -> Lecture:
    d = Path(lecture_dir)
    p = d / "讲稿.yaml"
    if not p.exists():
        raise ScriptError(f"没有 {p}")
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    for k in ("book", "section", "title") + (() if raw.get("deck") else ("shots",)):
        if k not in raw:
            raise ScriptError(f"讲稿缺少 {k}")
    book, sec = raw["book"], str(raw["section"])
    ch = int(sec.split(".")[0]) if sec.split(".")[0].isdigit() else 0     # 演讲稿（第 44 轮）的 section 不是讲号
    langs = tuple(raw.get("langs") or LANGS)                                # 只出中文：langs: [zh]
    if raw.get("deck"):
        raw = from_deck(raw)
    values = run_programs(book, ch, raw.get("code") or [])
    data = fill_tree({k: v for k, v in raw.items() if k != "shots"}, values, "讲稿头部")
    shots, seen = [], set()
    for i, s in enumerate(raw["shots"]):
        sid = s.get("id") or f"shot{i + 1}"
        if sid in seen:
            raise ScriptError(f"镜头 id 重复：{sid}")
        seen.add(sid)
        kind = s.get("kind")
        if kind not in KINDS:
            raise ScriptError(f"镜头 {sid}：kind 应为 {sorted(KINDS)} 之一")
        body = fill_tree({k: v for k, v in s.items() if k != "say"}, values, f"镜头 {sid}")
        say = s.get("say") or {}
        lines = {lang: [] for lang in LANGS}
        for lang in langs:
            if not say.get(lang):
                raise ScriptError(f"镜头 {sid}：缺少 say.{lang}")
            lines[lang] = [split_line(fill(str(x), values, f"镜头 {sid} say.{lang}")) for x in say[lang]]
        shot = Shot(id=sid, kind=kind, data=body, lines=lines)
        nz, ne = shot.steps("zh"), shot.steps("en")
        if nz != ne and len(langs) > 1:
            raise ScriptError(f"镜头 {sid}：中文 {nz} 个“>”，英文 {ne} 个，应相同")
        need = {"slide": len(body.get("items") or []), "homework": len(body.get("items") or []),
                "outro": len(body.get("points") or []), "lab": len(body.get("steps") or [])}.get(kind)
        if need is not None and nz > need:
            raise ScriptError(f"镜头 {sid}：“>” 有 {nz} 个，多于可显示的 {need} 项")
        for lang in langs:
            for ln in lines[lang]:
                if "[" in ln.shown and "|" in ln.shown:
                    raise ScriptError(f"镜头 {sid}：“[字幕|读法]” 写法不完整：{ln.shown[:40]}")
                if PH.search(ln.shown):
                    raise ScriptError(f"镜头 {sid}：占位符没有填上：{ln.shown[:40]}")
        shots.append(shot)
    return Lecture(dir=d, book=book, section=sec, chapter_no=ch, data=data, shots=shots, values=values)


ZH_END = re.compile(r"(?<=[。！？])")
EN_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9“\"'(])")


def sentences(text: str, lang: str) -> list[str]:
    text = re.sub(r"\s+", " " if lang == "en" else "", str(text)).strip()
    parts = ZH_END.split(text) if lang == "zh" else EN_END.split(text)
    return [x.strip() for x in parts if x.strip()]


def from_deck(raw: dict) -> dict:
    """第 25 轮起的标准：视频画面就是这一讲的网页互动课件（course/slides/chNN.yaml），配音是每页讲稿。
    讲稿.yaml 只写：deck、intro（封面上说的）、after（课程讲完、小结之前的镜头：虚拟实验、数字工厂录屏，
    或追加的课件页 {slide: {...}}，如作业、测验）、outro（小结之后的结尾）。每页的句子依次让该页要点逐条出现。"""
    deck_id = raw["deck"]
    dy = WEB[raw["book"]] / "course" / "slides" / f"{deck_id}.yaml"
    deck = yaml.safe_load(dy.read_text(encoding="utf-8"))
    code = list(dict.fromkeys(list(raw.get("code") or []) + list(deck.get("code") or [])))
    slides = deck["slides"]
    if deck.get("only_zh"):              # 只写中文的演示稿（第 44 轮）：讲稿、标题补成 [中文, ""]
        slides = [{k: ([v, ""] if k in ("notes", "title") and isinstance(v, str) else v) for k, v in sl.items()} for sl in slides]
    extra = [a["slide"] for a in raw.get("after") or [] if "slide" in a]
    tools = TEXTBOOK / "tools" / "webcourse" / "wc_slides.py"       # 公用课件引擎（第 29 轮）
    import hashlib
    stamp = hashlib.sha1((dy.read_text(encoding="utf-8") + tools.read_text(encoding="utf-8")
                          + json.dumps(extra, ensure_ascii=False)).encode()).hexdigest()[:12]

    def say_of(notes, zh_extra=(), en_extra=()):
        zh = sentences(notes[0], "zh") + list(zh_extra) if notes else list(zh_extra)
        en = sentences(notes[1], "en") + list(en_extra) if notes else list(en_extra)
        k = min(len(zh), len(en)) if en else len(zh)        # 只有中文（第 44 轮）：每句都让下一个要点出现
        return {"zh": [(">" if i < k else "") + x for i, x in enumerate(zh)],
                "en": [(">" if i < k else "") + x for i, x in enumerate(en)]}

    shots, part, summary = [], ["", ""], None
    for n, sl in enumerate(slides, 1):
        lay = sl["layout"]
        if lay == "section":
            part = sl["title"]
        if lay == "lab":
            continue                     # 学生自己操作的整页实验：视频里放到课后部分，用实验录屏
        if n in (raw.get("skip") or []):
            continue                     # 控制长度：课程部分约 10 分钟，次要的页留给课件和教材
        if lay == "summary":
            summary = (n, sl)
            continue
        if lay == "cover":
            say = {"zh": raw["intro"]["zh"], "en": raw["intro"].get("en") or []}
        elif lay == "section":
            say = {"zh": [sl["title"][0] + "。"], "en": [sl["title"][1] + "."]}
        else:
            say = say_of(sl.get("notes"))
        if n in (raw.get("say") or {}):          # 短版（第 44 轮）：这一页换一段更短的话
            say = say_of([raw["say"][n], ""])
        if not say["zh"]:
            continue
        shots.append({"id": f"p{n:02d}", "kind": "deck", "slide": n, "stamp": stamp,
                      "part": part if lay != "cover" else ["开场", "Opening"], "say": say})
    k = len(slides)
    for a in raw.get("after") or []:
        if "slide" in a:
            k += 1
            sl = a["slide"]
            shots.append({"id": a.get("id") or f"x{k:02d}", "kind": "deck", "slide": k, "stamp": stamp,
                          "part": a.get("part") or sl.get("title") or ["", ""], "say": a.get("say") or say_of(sl.get("notes"))})
        else:
            shots.append(a)
    if summary:
        n, sl = summary
        out = raw.get("outro") or {"zh": [], "en": []}
        notes = [raw["say"][n], ""] if n in (raw.get("say") or {}) else sl.get("notes")
        shots.append({"id": "summary", "kind": "deck", "slide": n, "stamp": stamp, "part": ["小结", "Summary"],
                      "say": say_of(notes, out["zh"], out.get("en") or [])})
    new = {k_: v for k_, v in raw.items() if k_ not in ("intro", "after", "outro", "skip", "say")}
    if deck.get("talk"):
        new["talk"] = deck["talk"]
    new.update(code=code, shots=shots, deck_extra=extra)
    return new


def lesson(lec: Lecture) -> dict:
    """The course-pack lesson of a web-edition book (course/lessons/chNN.json)."""
    return json.loads((lec.web / "course" / "lessons" / f"ch{lec.chapter_no:02d}.json").read_text(encoding="utf-8"))


def assignment(lec: Lecture, ids: list, lang: str) -> dict:
    """Web-edition books: homework items are 1-based task numbers of the lesson's assignment → {n: (kind, text)}."""
    tasks = lesson(lec)["assignment"]["tasks"]
    i = 0 if lang == "zh" else 1
    out = {}
    for n in ids:
        if not 1 <= int(n) <= len(tasks):
            raise ScriptError(f"作业里没有第 {n} 题")
        txt = tasks[int(n) - 1][i]
        m = re.match(r"^[（(]?([^）)。.：:]{1,16})[）)]?[。.：:]?\s*(.+)$", txt, re.S)
        kind, body = (m.group(1), m.group(2)) if m and len(m.group(1)) <= 16 and txt[:1] in "（(" else ("", txt)
        if not kind:
            m2 = re.match(r"^([^。.]{1,28})[。.]\s*(.+)$", txt, re.S)
            kind, body = (m2.group(1), m2.group(2)) if m2 else ("", txt)
        out[str(n)] = (kind, body.strip())
    return out


def exercises(lec: Lecture, ids: list[str]) -> dict:
    """{'14.2.1': ('计算', 'text with $math$')} from the section's markdown (the book is the single source)."""
    md = (lec.ch_dir / f"{lec.chapter_no:02d}-{lec.section.split('.')[1]}.md").read_text(encoding="utf-8")
    out = {}
    for i in ids:
        m = re.search(r"^" + re.escape(i) + r"\s+（([^）]+)）\s*(.+)$", md, re.M)
        if not m:
            raise ScriptError(f"教材里找不到习题 {i}")
        out[i] = (m.group(1), m.group(2).strip())
    return out


def exercises_en(lec: Lecture, ids: list[str]) -> dict:
    p = lec.ch_dir / f"{lec.chapter_no:02d}-{lec.section.split('.')[1]}.en.md"
    if not p.exists():
        return {}
    md = p.read_text(encoding="utf-8")
    out = {}
    for i in ids:
        m = re.search(r"^" + re.escape(i) + r"\s+\(([^)]+)\)\s*(.+)$", md, re.M)
        if m:
            out[i] = (m.group(1), m.group(2).strip())
    return out


if __name__ == "__main__":
    lec = load(sys.argv[1])
    for s in lec.shots:
        for lang in LANGS:
            n = sum(len(x.spoken) for x in s.lines[lang])
            print(s.id, lang, len(s.lines[lang]), "句", n, "字符")
