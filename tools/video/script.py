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
KINDS = {"title", "slide", "anim", "code", "lab", "clip", "homework", "outro"}
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
    def code_dir(self) -> Path:
        return TEXTBOOK / self.book / f"ch{self.chapter_no:02d}" / "code"

    @property
    def ch_dir(self) -> Path:
        return TEXTBOOK / self.book / f"ch{self.chapter_no:02d}"


def run_programs(book: str, ch: int, names: list[str]) -> dict:
    """Run the textbook programs that the script quotes; {name: {key: value}} (same values the book prints)."""
    code = TEXTBOOK / book / f"ch{ch:02d}" / "code"
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
    for k in ("book", "section", "title", "shots"):
        if k not in raw:
            raise ScriptError(f"讲稿缺少 {k}")
    book, sec = raw["book"], str(raw["section"])
    ch = int(sec.split(".")[0])
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
        lines = {}
        for lang in LANGS:
            if not say.get(lang):
                raise ScriptError(f"镜头 {sid}：缺少 say.{lang}")
            lines[lang] = [split_line(fill(str(x), values, f"镜头 {sid} say.{lang}")) for x in say[lang]]
        shot = Shot(id=sid, kind=kind, data=body, lines=lines)
        nz, ne = shot.steps("zh"), shot.steps("en")
        if nz != ne:
            raise ScriptError(f"镜头 {sid}：中文 {nz} 个“>”，英文 {ne} 个，应相同")
        need = {"slide": len(body.get("items") or []), "homework": len(body.get("items") or []),
                "outro": len(body.get("points") or []), "lab": len(body.get("steps") or [])}.get(kind)
        if need is not None and nz > need:
            raise ScriptError(f"镜头 {sid}：“>” 有 {nz} 个，多于可显示的 {need} 项")
        for lang in LANGS:
            for ln in lines[lang]:
                if "[" in ln.shown and "|" in ln.shown:
                    raise ScriptError(f"镜头 {sid}：“[字幕|读法]” 写法不完整：{ln.shown[:40]}")
                if PH.search(ln.shown):
                    raise ScriptError(f"镜头 {sid}：占位符没有填上：{ln.shown[:40]}")
        shots.append(shot)
    return Lecture(dir=d, book=book, section=sec, chapter_no=ch, data=data, shots=shots, values=values)


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
