"""Builds a WenQuest textbook from its sources and checks it (第 7 轮 2.3).

    python3 textbook/tools/build.py robotics            # check and build the web version
    python3 textbook/tools/build.py robotics --pdf      # also a PDF per chapter (headless Chromium)

Sources: textbook/<book>/book.yaml (generated from the agreed outline) and chNN/NN-M.md, one file per section, with
a front matter (id, title). In the text:

- ``{{ex4_1_1.x_p}}`` — a number from the program chNN/code/ex4_1_1.py (``bookout.out``); ``{{ex4_1_1.x_p:.2f}}``
  gives a format; the default is 5 significant digits.
- ``$...$`` and ``$$...$$`` — formulas (LaTeX), typeset to SVG on the server; display formulas are numbered with
  ``\\tag{4.1.3}``.
- ``::: 程序 4.1.1`` / ``::: 动画 4.1.1`` / ``::: 实验 4.1`` / ``::: 图 4.1.1`` … ``:::`` — a program (listed with its
  output), an animation, a virtual lab, a figure. Lines ``key: value`` first (src, 说明), then free text.
- ``**定义 4.1.1（名称）**`` and the like define numbered items; ``**术语**`` marks a term, which must be in the
  glossary (conventions/术语表.csv).

Checks (any error stops the build):
  程序     every program runs;
  占位符   every placeholder has a value;
  公式     every formula typesets;
  编号     equation tags are unique, belong to their section and run in order;
  引用     references to 式/定义/定理/算例/程序/图/表/动画/实验, sections (4.8 节) and chapters exist;
  手写数字 a decimal with 4 or more significant digits must come from a program, not be typed by hand;
  术语     bold terms are in the glossary.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from markdown_it import MarkdownIt

import english
import labdocs
import tasksheet

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[1]
WQ_ANIM = ROOT / "services" / "animator" / "wq_anim.py"
_ANIM_CHECK = None


_LABKIT = None


def labkit():
    """The platform's lab kit (services/gateway/app/production/labs.py): static check and the lab page."""
    global _LABKIT
    if _LABKIT is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("wq_labs", ROOT / "services" / "gateway" / "app" / "production" / "labs.py")
        _LABKIT = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_LABKIT)
    return _LABKIT


_MODELS: dict = {}


def book_models(book: dict) -> dict:
    """The library models copied into the book (textbook/<book>/models/<id>/entry.json + default.glb), in the form the
    lab kit embeds for 3D labs: {id: {entry (normalised like the platform does), glb (base64), motion}}."""
    key = str(book["root"])
    if key not in _MODELS:
        import base64
        import importlib.util
        spec = importlib.util.spec_from_file_location("wq_library", ROOT / "services" / "gateway" / "app" / "library.py")
        lib = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lib)
        out = {}
        for d in sorted((book["root"] / "models").glob("*/entry.json")):
            entry = lib.normalize_entry(json.loads(d.read_text(encoding="utf-8")))
            out[d.parent.name] = {"entry": entry, "glb": base64.b64encode((d.parent / "default.glb").read_bytes()).decode(), "motion": []}
        _MODELS[key] = out
    return _MODELS[key]


def trial_labs(page_html: str, ids: list[str], rep: "Report", where: str) -> None:
    """Run every lab's tasks in headless Chromium with the lab checker's own code (services/labcheck)."""
    import asyncio
    import importlib.util
    spec = importlib.util.spec_from_file_location("wq_labcheck", ROOT / "services" / "labcheck" / "app.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for lab in ids:
        res = asyncio.run(mod.run(page_html, lab))
        for p in res.get("problems") or []:
            rep.add("error", "实验", where, f"实验 {lab.replace('-', '.')}：{p}")


def anim_check(code: str) -> str:
    """The animation service's own safety check (services/animator/app.py: check), without importing the service."""
    global _ANIM_CHECK
    if _ANIM_CHECK is None:
        import ast
        tree = ast.parse((ROOT / "services" / "animator" / "app.py").read_text(encoding="utf-8"))
        names = {"ALLOWED_IMPORTS", "FORBIDDEN_NAMES", "FORBIDDEN_ATTRS", "MAX_CODE"}
        keep = [n for n in tree.body if (isinstance(n, ast.FunctionDef) and n.name == "check")
                or (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in n.targets))]
        ns: dict = {"ast": ast}
        exec(compile(ast.Module(body=keep, type_ignores=[]), "animator-check", "exec"), ns)
        _ANIM_CHECK = ns["check"]
    return _ANIM_CHECK(code)
KINDS = ("程序", "动画", "实验", "图", "表", "任务")          # 任务: engineering task sheets (第 11、13 轮)
REF_KINDS = ("式", "定义", "定律", "定理", "引理", "推论", "准则", "算例", "程序", "图", "表", "动画", "实验", "任务", "习题")


@dataclass
class Problem:
    level: str          # error | warning
    kind: str           # 程序 / 占位符 / 公式 / 编号 / 引用 / 手写数字 / 术语 / 结构
    where: str
    text: str

    def __str__(self) -> str:
        return f"{'✗' if self.level == 'error' else '!'} [{self.kind}] {self.where}：{self.text}"


@dataclass
class Section:
    id: str
    title: str
    chapter: int
    path: Path
    source: str
    html: str = ""
    html_mp: str = ""
    figdir: Path = Path(".")
    anim_figs: list = field(default_factory=list)
    anims: list = field(default_factory=list)
    labs: list = field(default_factory=list)
    labdocs: list = field(default_factory=list)
    tasks: list = field(default_factory=list)       # (number, yaml path, task data): 工程任务单 (第 13 轮)
    media: list = field(default_factory=list)       # (kind, number, caption) of animations and labs: the 互动资源 lists (第 9 轮 2.5)
    defines: set = field(default_factory=set)
    lang: str = "zh"                 # "en": the English edition of the section (NN-M.en.md, 第 8 轮)


@dataclass
class Report:
    problems: list = field(default_factory=list)

    def add(self, level, kind, where, text):
        p = Problem(level, kind, where, text)
        if not any(vars(p) == vars(q) for q in self.problems):
            self.problems.append(p)

    @property
    def errors(self):
        return [p for p in self.problems if p.level == "error"]


# ---------------------------------------------------------------- loading

def load_book(book: str, root: Path | None = None) -> dict:
    root = root or ROOT / "textbook" / book
    data = yaml.safe_load((root / "book.yaml").read_text(encoding="utf-8"))
    data["root"] = root
    return data


def outline_in_sync(book: str, rep: Report) -> None:
    sys.path.insert(0, str(TOOLS))
    import outline  # noqa: E402
    if outline.generate(book)["chapters"] != {k: v for k, v in load_book(book).items()}["chapters"]:
        rep.add("error", "结构", "book.yaml", "与提纲不一致：提纲改过后请运行 python3 textbook/tools/outline.py " + book)


FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def load_sections(book: dict, rep: Report, only: set | None = None) -> list[Section]:
    out = []
    known = {s["id"]: (c["no"], s["title"]) for c in book["chapters"] for s in c["sections"]}
    for c in book["chapters"]:      # 章首提要 NN-0.md (id "N.0") and 章末小结 NN-99.md (id "N.end")
        known[f"{c['no']}.0"] = (c["no"], "本章提要")
        known[f"{c['no']}.end"] = (c["no"], "本章小结")
    for path in sorted(book["root"].glob("ch[0-9][0-9]/[0-9][0-9]-*.md"), key=lambda p: [int(x) for x in re.findall(r"\d+", p.name)]):
        if path.name.endswith(".en.md"):
            continue
        text = path.read_text(encoding="utf-8")
        m = FRONT.match(text)
        where = str(path.relative_to(book["root"].parent))
        if not m:
            rep.add("error", "结构", where, "缺少开头的 --- id/title --- 信息")
            continue
        meta = yaml.safe_load(m.group(1)) or {}
        sid = str(meta.get("id", ""))
        if only and sid not in only:
            continue
        if sid not in known:
            rep.add("error", "结构", where, f"节号 {sid} 不在提纲里")
            continue
        ch = int(sid.split(".")[0])
        if path.parent.name != f"ch{ch:02d}":
            rep.add("error", "结构", where, f"{sid} 应放在 ch{ch:02d}/")
        out.append(Section(sid, str(meta.get("title") or known[sid][1]), ch, path, text[m.end():]))
    return out


def load_sections_en(book: dict, zh: list[Section], rep: Report) -> list[Section]:
    """The English edition: NN-M.en.md next to each Chinese section that has been translated."""
    out = []
    by_id = {s.id: s for s in zh}
    for s in zh:
        path = s.path.with_name(s.path.stem + ".en.md")
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        m = FRONT.match(text)
        where = str(path.relative_to(book["root"].parent))
        meta = (yaml.safe_load(m.group(1)) or {}) if m else {}
        if not m or str(meta.get("id", "")) != s.id or not meta.get("title"):
            rep.add("error", "结构", where, f"开头要有 --- id: \"{s.id}\" 和英文 title ---")
            continue
        out.append(Section(s.id, str(meta["title"]), s.chapter, path, text[m.end():], lang="en"))
    for path in book["root"].glob("ch[0-9][0-9]/[0-9][0-9]-*.en.md"):
        zh_path = path.with_name(path.name[:-6] + ".md")
        if not zh_path.exists():
            rep.add("error", "结构", str(path.relative_to(book["root"].parent)), "没有对应的中文节（英文版只能翻译已有的中文）")
    del by_id
    return out


def progress(book: dict) -> dict:
    """progress.yaml: each chapter's status (第 8 轮 2.1) and the English titles of parts and chapters."""
    p = book["root"] / "progress.yaml"
    data = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
    return data or {}


STATUS = ("draft", "ai", "first", "team", "final")     # 草稿、AI 审稿、初审、团队审阅、定稿


def glossary_en(book: dict) -> dict[str, str]:
    p = book["root"] / "conventions" / "术语表.csv"
    with p.open(encoding="utf-8") as f:
        return {row["中文"].strip(): (row.get("English") or "").strip() for row in csv.DictReader(f)}


def glossary(book: dict) -> set[str]:
    p = book["root"] / "conventions" / "术语表.csv"
    with p.open(encoding="utf-8") as f:
        return {row["中文"].strip() for row in csv.DictReader(f)}


def _names(en: str) -> set[str]:
    """The English names of a glossary entry ("a; b (c)" → {"a", "b"}): alternatives, without notes in brackets."""
    out = set()
    for x in en.split(";"):
        while re.search(r"\([^()]*\)", x):           # brackets may nest: "(SO(3))"
            x = re.sub(r"\s*\([^()]*\)", "", x)
        x = re.sub(r"[–—]", "-", x).replace("’", "'").replace("'s ", " ").replace("' ", " ")   # hand–eye = hand-eye, Farkas' = Farkas
        if x.strip():
            out.add(x.strip().lower())
    return out


def check_std_tables(book: dict, rep: Report) -> None:
    """Every digitized standard table of the book (std/*.yaml, 第 11、13 轮) is well formed: sources with addresses,
    each row's source listed, columns declared, at least 10 spot checks (stdtab.check)."""
    import stdtab
    import yaml as _yaml
    for p in sorted((book["root"] / "std").glob("*.yaml")):
        try:
            d = _yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except _yaml.YAMLError as e:
            rep.add("error", "标准表", f"std/{p.name}", f"YAML 格式错误：{e}")
            continue
        # a table without sources is in the compact format (《机械设计》第 11 轮: rows as lists, "status: 待核对"); it is
        # reported as a 提醒 so one book's table format never stops another book's build
        kind = "error" if "sources" in d else "warning"
        for why in (stdtab.check(p) if kind == "error" else ["没有逐行出处（sources），待按零件库格式补出处并抽查核对"]):
            rep.add(kind, "标准表", f"std/{p.name}", why)


def check_other_books(book: dict, rep: Report) -> None:
    """The same Chinese term should have the same English name in every book (第 9 轮 2.3): two entries agree when
    they share at least one English name (brackets, dashes and apostrophes ignored). A difference is a 提醒, not an
    error, so one book never stops another book's build; a term that really means something else in a book (e.g.
    线性代数's 位移 = shift) says so in its 备注 column ("含义不同") and is skipped."""
    mine = glossary_en(book)
    with (book["root"] / "conventions" / "术语表.csv").open(encoding="utf-8") as f:
        mine_note = {row["中文"].strip(): row.get("备注") or "" for row in csv.DictReader(f)}
    for other in sorted(book["root"].parent.glob("*/conventions/术语表.csv")):
        if other.parents[1] == book["root"]:
            continue
        with other.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        theirs = {row["中文"].strip(): (row.get("English") or "").strip() for row in rows}
        their_note = {row["中文"].strip(): row.get("备注") or "" for row in rows}
        name = other.parents[1].name
        for zh, en in mine.items():
            if "含义不同" in mine_note.get(zh, "") + their_note.get(zh, ""):
                continue
            if zh in theirs and en and theirs[zh] and not (_names(en) & _names(theirs[zh])):
                rep.add("warning", "术语", "conventions/术语表.csv",
                        f"“{zh}”的英文名与《{name}》不一致：本书 {en}，{name} 为 {theirs[zh]}")


# ---------------------------------------------------------------- programs and placeholders

def run_programs(book: dict, chapters: set[int], rep: Report, lang: str = "zh") -> dict[str, dict]:
    """Runs every program of these chapters; lang "en" runs them for the English edition (English figure labels and
    text values, figures in figs/en/)."""
    values: dict[str, dict] = {}
    cache = book["root"].parent / "build" / book["book"] / ("values" if lang == "zh" else "values-en")
    cache.mkdir(parents=True, exist_ok=True)
    for ch in sorted(chapters):
        code = book["root"] / f"ch{ch:02d}" / "code"
        shared = b"".join(p.read_bytes() for p in sorted(code.glob("_*.py")))   # helper modules (not run themselves)
        shared += b"".join(p.read_bytes() for p in sorted((book["root"] / "models").glob("*/*")))   # library models the programs read
        shared += b"".join(p.read_bytes() for p in sorted((book["root"] / "conventions").glob("*.py")))   # the book's constants (constants.py)
        shared += b"".join(p.read_bytes() for p in sorted((book["root"] / "std").glob("*.yaml")))   # standard tables (机械设计, 第 11 轮)
        shared += (TOOLS / "stdtab.py").read_bytes()                     # table reader and the shared calculation sheet (第 13 轮)
        shared += (ROOT / "textbook" / "mechdesign" / "conventions" / "calcsheet.py").read_bytes() if (ROOT / "textbook" / "mechdesign" / "conventions" / "calcsheet.py").exists() else b""
        meta_p = book["root"] / "meta.yaml"
        if meta_p.exists():          # files outside the book the programs read (e.g. the digital factory's process plans, 第 13 轮)
            for pat in (yaml.safe_load(meta_p.read_text(encoding="utf-8")) or {}).get("program_deps") or []:
                shared += b"".join(p.read_bytes() for p in sorted(ROOT.glob(pat)) if p.is_file())
        if (book["root"] / "conventions" / "mdstd.py").exists():       # its materials come from the digital factory's library
            shared += (ROOT / "factory" / "digital" / "cae" / "materials.py").read_bytes()
            for rel in ("cae/solve.py", "cae/fatigue.py", "cae/geometry.py", "sim/engine.py"):   # 有限元、疲劳、试验台记录（第 33 章起）
                p = ROOT / "factory" / "digital" / rel
                shared += p.read_bytes() if p.exists() else b""
        for prog in sorted(p for p in code.glob("*.py") if not p.name.startswith("_")):
            where = str(prog.relative_to(book["root"].parent))
            digest = hashlib.sha256(prog.read_bytes() + shared + (TOOLS / "bookout.py").read_bytes() + lang.encode()).hexdigest()[:16]
            hit = cache / f"{prog.stem}.{digest}.json"
            if hit.exists():
                values[prog.stem] = json.loads(hit.read_text(encoding="utf-8"))
                continue
            outp = cache / f"{prog.stem}.out.json"
            outp.unlink(missing_ok=True)
            figs = cache.parent / "figs" / ("" if lang == "zh" else "en")
            figs.mkdir(parents=True, exist_ok=True)
            env = {**os.environ, "WQ_BOOK_OUT": str(outp), "WQ_BOOK_FIGDIR": str(figs), "PYTHONPATH": os.pathsep.join([str(TOOLS), str(book["root"] / "conventions")]), "MPLBACKEND": "Agg",
                   "WQ_LANG": lang}
            try:
                r = subprocess.run([sys.executable, prog.name], cwd=prog.parent, env=env, capture_output=True, text=True, timeout=300)
            except subprocess.TimeoutExpired:
                rep.add("error", "程序", where, "运行超过 5 分钟")
                continue
            if r.returncode != 0:
                rep.add("error", "程序", where + ("（英文版运行）" if lang == "en" else ""), "运行出错：" + (r.stderr.strip().splitlines() or ["?"])[-1])
                continue
            if not outp.exists():
                rep.add("error", "程序", where, "没有用 bookout.out(...) 交出结果")
                continue
            v = json.loads(outp.read_text(encoding="utf-8"))
            for old in cache.glob(f"{prog.stem}.*.json"):
                old.unlink()
            hit.write_text(json.dumps(v, ensure_ascii=False), encoding="utf-8")
            values[prog.stem] = v
    return values


PLACE = re.compile(r"\{\{\s*(\w+)\.(\w+)\s*(?::([^}]+))?\}\}")


def sig(x: float, n: int = 5) -> str:
    """n significant digits, keeping trailing zeros (0.18660, not 0.1866)."""
    if x == 0:
        return "0"
    from decimal import Decimal
    d = Decimal(repr(float(x)))
    exp = d.adjusted()
    q = Decimal(1).scaleb(exp - n + 1)
    s = format(d.quantize(q), "f")
    return s


def fill(sec: Section, values: dict, rep: Report) -> str:
    def one(m):
        prog, name, fmt = m.group(1), m.group(2), m.group(3)
        if prog not in values:
            rep.add("error", "占位符", sec.id, f"{{{{{prog}.{name}}}}}：没有程序 {prog}.py 或它没有运行成功")
            return m.group(0)
        if name not in values[prog]:
            rep.add("error", "占位符", sec.id, f"{{{{{prog}.{name}}}}}：程序 {prog}.py 没有交出 {name}")
            return m.group(0)
        v = values[prog][name]
        if isinstance(v, (int, float)) and not isinstance(v, bool) and fmt and fmt.strip().startswith("sci"):
            # {{p.x:sci1}} → 7.2\times 10^{-13} (inside a formula)
            digits = int(fmt.strip()[3:] or 1)
            m_, e_ = f"{v:.{digits}e}".split("e")
            return f"{m_}\\times 10^{{{int(e_)}}}"
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            try:
                return format(v, fmt.strip()) if fmt else (str(v) if isinstance(v, int) else sig(v))
            except ValueError:
                rep.add("error", "占位符", sec.id, f"{m.group(0)}：格式 {fmt} 不对")
                return m.group(0)
        if sec.lang == "en" and english.CJK.search(str(v)):
            rep.add("error", "占位符", sec.id + "（英文版）", f"{m.group(0)} 的值是中文：程序里写成 T(中文, English)")
        return str(v)
    return PLACE.sub(one, sec.source)


# ---------------------------------------------------------------- formulas, directives, markdown

DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.S)
INLINE = re.compile(r"(?<![\\$])\$(?!\$)([^$\n]+?)\$")
FENCE = re.compile(r"^```.*?^```", re.S | re.M)
DIRECTIVE = re.compile(r"^:::[ \t]*(" + "|".join(KINDS + tuple(english.KINDS)) + r")[ \t]+([\d.]+)[ \t]*\n(.*?)^:::[ \t]*$", re.S | re.M)
TAG = re.compile(r"\\tag\{([^}]+)\}")


def protect(text: str, store: list, pattern: re.Pattern, make) -> str:
    def one(m):
        store.append(make(m))
        return f"WQTOKEN{len(store) - 1}Z"
    return pattern.sub(one, text)


def directive_html(sec: Section, kind: str, num: str, body: str, values: dict, rep: Report) -> str:
    kind = english.KINDS.get(kind, kind)          # English directives (::: Figure 4.1.1) mean the same things
    en = sec.lang == "en"
    meta, rest = {}, []
    for line in body.splitlines():
        m = re.match(r"^(src|说明|模板|模型|caption|图|figure)\s*[:：]\s*(.*)$", line.strip())
        if m and not rest:
            meta[{"figure": "图"}.get(m.group(1), m.group(1))] = m.group(2).strip()
        else:
            rest.append(line)
    note = "\n".join(rest).strip()
    label = f"{english.LABEL[kind]} {num}" if en else f"{kind} {num}"
    sec.defines.add(f"{kind} {num}")
    cap = html.escape(meta.get("说明", "") or meta.get("caption", ""))
    box = f"[{label}] " if en else f"【{label}】"          # what shows until the media is there
    gap = ". " if en else "　"
    if kind == "程序":
        src = meta.get("src", "")
        p = sec.path.parent / src
        if not src or not p.exists():
            rep.add("error", "程序", sec.id, f"{label}：找不到 {src or '（未写 src）'}")
            code = ""
        else:
            if en:                # the English edition lists the copy with English comments (same code, checked)
                why = english.same_code(p, p.parent / "en" / p.name)
                if why:
                    rep.add("error", "程序", sec.id + "（英文版）", f"{label}：{why}")
                else:
                    p = p.parent / "en" / p.name
            code = p.read_text(encoding="utf-8")
        result = values.get(Path(src).stem)
        res = ""
        if result:
            res = f"<div class='wq-prog-out'><b>{'Output' if en else '运行结果'}</b><pre>" + html.escape(
                "\n".join(f"{k} = {format(v, '.6g') if isinstance(v, float) else v}" for k, v in result.items() if not k.startswith("_"))) + "</pre></div>"
        return (f"<figure class='wq-prog' id='{kind}-{num}'><figcaption>{label}{gap}{cap}</figcaption>"
                f"<details><summary>{'Program' if en else '程序'} {html.escape(src)}</summary><pre class='wq-code'><code>{html.escape(code)}</code></pre></details>"
                f"{res}{('<p>' + html.escape(note) + '</p>') if note else ''}</figure>")
    if kind == "图":
        src = meta.get("src", "")
        p = (sec.figdir / "en" if en else sec.figdir) / f"{src}.svg" if src else None
        if not p or not p.exists():
            rep.add("error", "图", sec.id, f"{label}：没有找到示意图 {src or '（未写 src）'}（由 code/ 里的程序用 bookout.figure 生成）")
            return f"<figure class='wq-fig' id='{kind}-{num}'><div class='wq-media-box'>{box}</div></figure>"
        import base64
        data = base64.b64encode(p.read_bytes()).decode()
        return (f"<figure class='wq-fig' id='{kind}-{num}'><img class='wq-figimg' alt='{label}' src='data:image/svg+xml;base64,{data}'/>"
                f"<figcaption>{label}{gap}{cap}</figcaption>{('<p>' + html.escape(note) + '</p>') if note else ''}</figure>")
    if kind == "表":     # the table itself follows in Markdown; here only its numbered caption
        return f"<div class='wq-tabcap' id='{kind}-{num}'>{label}{gap}{cap}</div>"
    if kind == "动画":
        fig = meta.get("图", "")
        sec.anim_figs.append((label, fig))
        sec.media.append(("anim", num, meta.get("说明", "") or meta.get("caption", "")))
        name = meta.get("src", "")
        script = sec.path.parent / "anim" / f"{name}.py" if name else None
        if not script or not script.exists():
            rep.add("error", "动画", sec.id, f"{label}：没有场景程序（写 src: 名称，放在 anim/名称.py）")
        else:
            code = script.read_text(encoding="utf-8")
            why = anim_check(code)
            if why:
                rep.add("error", "动画", sec.id, f"{label}：场景程序不能通过渲染服务的检查：{why}")
            h = hashlib.sha256(code.encode() + WQ_ANIM.read_bytes()).hexdigest()[:12]
            sec.anims.append((name, h, code))
            # the gateway puts the rendered video here once it is ready; until then this box shows
            return (f"<figure class='wq-anim' id='{kind}-{num}'><div class='wq-media-box' data-anim='{name}' data-hash='{h}'>"
                    f"{box}{cap}</div><figcaption>{label}{gap}{cap}</figcaption>"
                    f"{('<p>' + html.escape(note) + '</p>') if note else ''}</figure>")
    if kind == "实验":
        sec.media.append(("lab", num, meta.get("说明", "") or meta.get("caption", "")))
        name = meta.get("src", "")
        script = sec.path.parent / "lab" / f"{name}.js" if name else None
        if not script or not script.exists():
            rep.add("error", "实验", sec.id, f"{label}：没有实验程序（写 src: 名称，放在 lab/名称.js）")
        else:
            code = script.read_text(encoding="utf-8")
            for why in labkit().static_problems(code):
                rep.add("error", "实验", sec.id, f"{label}：{why}")
            if not en:
                sec.labs.append((num, code))
            g, bad = labdocs.load(script.with_suffix(".yaml"))
            for why in bad:
                rep.add("error", "实验", sec.id, f"{label}：{why}")
            if g is not None and not bad:
                sec.labdocs.append((num, script, g))
            return (f"<figure class='wq-lab' id='{kind}-{num}'><div class='wq-media-box wq-labbox' data-lab='{num.replace('.', '-')}'>"
                    f"{box}{cap}</div>{('<p>' + html.escape(note) + '</p>') if note else ''}</figure>")
    if kind == "任务":       # 工程任务单 (第 11 轮 2.7（3）5a、第 13 轮): task/NAME.yaml → task sheet, rubric, blank calculation sheet
        name = meta.get("src", "")
        path = sec.path.parent / "task" / f"{name}.yaml" if name else None
        if not path:
            rep.add("error", "任务", sec.id, f"{label}：没写 src（任务单说明文件 task/名称.yaml）")
            return ""
        t, bad = tasksheet.load(path)
        for why in bad:
            rep.add("error", "任务", sec.id, f"{label}：{why}")
        if t is None or bad:
            return f"<figure class='wq-task' id='{kind}-{num}'><div class='wq-media-box'>{box}{cap}</div></figure>"
        if not en:
            sec.tasks.append((num, path, t))
        i = 1 if en else 0
        st = "".join(f"<span class='wq-station'>〔{x}〕{html.escape((tasksheet.STATION_EN if en else tasksheet.STATION_ZH)[x])}</span>" for x in t["工位"])
        dl = "".join(f"<li>{html.escape(x['名称'][i])}</li>" for x in t["交付物"])
        head = ("Engineering task" if en else "工程任务单")
        return (f"<figure class='wq-task' id='{kind}-{num}'><div class='wq-taskbox' data-task='{num.replace('.', '-')}'>"
                f"<div class='wq-task-head'><b>{label}　{head} {html.escape(t['编号'])}</b>{gap}{html.escape(t['标题'][i])}</div>"
                f"<div class='wq-task-role'>{'Role' if en else '角色'}：{html.escape(t['角色'][i])}　{'Hours' if en else '建议学时'}：{t['学时']}</div>"
                f"<div class='wq-task-stations'>{st}</div><p>{html.escape(t['背景'][i])}</p>"
                f"<div class='wq-task-dl'><b>{'Deliverables' if en else '交付物'}</b><ul>{dl}</ul></div></div>"
                f"{('<p>' + html.escape(note) + '</p>') if note else ''}</figure>")
    cls = {"动画": "wq-anim", "实验": "wq-lab", "表": "wq-tab"}[kind]
    src = html.escape(meta.get("src", ""))
    # media are produced in later steps (animator, labkit); until then a placeholder box shows what will be there
    return (f"<figure class='{cls}' id='{kind}-{num}' data-src='{src}'><div class='wq-media-box'>{box}{cap}</div>"
            f"<figcaption>{label}{gap}{cap}</figcaption>{('<p>' + html.escape(note) + '</p>') if note else ''}</figure>")


def render_section(sec: Section, text: str, values: dict, rep: Report, formulas: list) -> str:
    store: list = []
    text = protect(text, store, FENCE, lambda m: ("raw", None, m.group(0)))
    text = protect(text, store, DIRECTIVE, lambda m: ("directive", (m.group(1), m.group(2), m.group(3)), None))
    text = protect(text, store, DISPLAY, lambda m: ("math", True, m.group(1).strip()))
    text = protect(text, store, INLINE, lambda m: ("math", False, m.group(1).strip()))
    md = MarkdownIt("commonmark", {"html": False, "typographer": False}).enable("table")
    # raw fences go back before markdown so they render as code blocks
    def unraw(t):
        return re.sub(r"WQTOKEN(\d+)Z", lambda m: store[int(m.group(1))][2] if store[int(m.group(1))][0] == "raw" else m.group(0), t)
    out = md.render(unraw(text))

    def back(m):
        i = int(m.group(1))
        kind, a, b = store[i]
        if kind == "directive":
            return directive_html(sec, a[0], a[1], a[2], values, rep)
        if kind == "math":
            formulas.append((sec.id, b, a))
            return f"WQMATH{len(formulas) - 1}Z"
        return m.group(0)
    out = re.sub(r"WQTOKEN(\d+)Z", back, out)
    # a display formula alone in a paragraph becomes a block
    out = re.sub(r"<p>(WQMATH\d+Z)</p>", r"<div class='wq-eq'>\1</div>", out)
    return out


def _mathjax(items: list[dict], rep: Report) -> list[dict] | None:
    r = subprocess.run(["node", str(TOOLS / "tex2svg.mjs")], input=json.dumps(items), capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        rep.add("error", "公式", "排版", "MathJax 运行失败：" + r.stderr[-300:] + "（先在 textbook/tools 运行 npm ci）")
        return None
    return json.loads(r.stdout)


def as_img(svg: str, cls: str) -> str:
    """An SVG formula as an <img> (the mini program's rich-text cannot show inline SVG): size kept in ex units."""
    import base64
    style = []
    for attr in ("width", "height"):
        m = re.search(attr + r'="([\d.]+ex)"', svg)
        if m:
            style.append(f"{attr}:{m.group(1)}")
    m = re.search(r'vertical-align:\s*(-?[\d.]+ex)', svg)
    if m:
        style.append(f"vertical-align:{m.group(1)}")
    data = base64.b64encode(svg.encode()).decode()
    return f"<img class='{cls}' style='{';'.join(style)}' src='data:image/svg+xml;base64,{data}'/>"


def typeset(formulas: list, rep: Report) -> tuple[list[str], list[str]]:
    """(web, mini program) renderings of every formula. Numbered display formulas are typeset a second time without
    \\tag for the mini program, where the number is written beside the image."""
    if not formulas:
        return [], []
    res = _mathjax([{"tex": f[1], "display": f[2]} for f in formulas], rep)
    if res is None:
        return ["" for _ in formulas], ["" for _ in formulas]
    tagged = [i for i, f in enumerate(formulas) if f[2] and TAG.search(f[1])]
    plain = _mathjax([{"tex": TAG.sub("", formulas[i][1]), "display": True} for i in tagged], rep) or []
    plain_of = dict(zip(tagged, plain))
    web, mp = [], []
    for i, ((sid, tex, disp), x) in enumerate(zip(formulas, res)):
        if "error" in x:
            rep.add("error", "公式", sid, f"{x['error']}：{tex[:80]}")
            web.append(f"<code>{html.escape(tex)}</code>")
            mp.append(f"<code>{html.escape(tex)}</code>")
            continue
        cls = "wq-md" if disp else "wq-mi"
        web.append(f"<span class='{cls}'>{x['svg']}</span>")
        if i in plain_of and "svg" in plain_of[i]:
            tag = TAG.search(tex).group(1)
            mp.append(f"{as_img(plain_of[i]['svg'], cls)}<span class='wq-tagno'>({tag})</span>")
        else:
            mp.append(as_img(x["svg"], cls))
    return web, mp


# ---------------------------------------------------------------- checks

def check_tags(sec: Section, rep: Report) -> None:
    tags = TAG.findall(sec.source)
    seen = []
    for t in tags:
        if not re.fullmatch(re.escape(sec.id) + r"\.\d+", t):
            rep.add("error", "编号", sec.id, f"式 ({t}) 应编为 ({sec.id}.n)")
            continue
        if t in seen:
            rep.add("error", "编号", sec.id, f"式 ({t}) 重复")
        seen.append(t)
        sec.defines.add(f"式 {t}")
    nums = [int(t.rsplit(".", 1)[1]) for t in seen]
    if nums and nums != list(range(1, len(nums) + 1)):
        rep.add("error", "编号", sec.id, f"公式编号应从 1 起连续：{nums}")
    for kind in ("定义", "定律", "定理", "引理", "推论", "准则", "算例"):     # 定律: laws of physics (第 9 轮); 准则: design and process criteria (第 11、13 轮)
        found = re.findall(r"\*\*" + kind + r" (" + re.escape(sec.id) + r"\.\d+)", sec.source)
        for n in found:
            sec.defines.add(f"{kind} {n}")
        nums = [int(n.rsplit(".", 1)[1]) for n in found]
        if nums and nums != list(range(1, len(nums) + 1)):
            rep.add("error", "编号", sec.id, f"{kind}编号应从 1 起连续：{nums}")
    for n in re.findall(r"(?m)^(\d+\.\d+\.\d+)\s", sec.source):     # exercises "4.1.1 …" at line start
        sec.defines.add(f"习题 {n}")
    heads = re.findall(r"(?m)^#{3,4}\s+(\d+\.\d+\.\d+)\s", sec.source)  # subsections "### 4.1.6 …"
    for n in heads:
        if not n.startswith(sec.id + "."):
            rep.add("error", "编号", sec.id, f"小节 {n} 不属于 {sec.id} 节")
        sec.defines.add(f"节 {n}")


REF = re.compile(r"(" + "|".join(REF_KINDS) + r")\s*\(?(\d+\.\d+(?:\.\d+)?)\)?")
EQ_LIST = re.compile(r"式\s*\((\d+\.\d+\.\d+)\)(?:\s*(?:和|与|、|至|到|–|-)\s*\((\d+\.\d+\.\d+)\))?")
SEC_REF = re.compile(r"(?<![\d.])(\d+\.\d+)\s*节")
SUB_REF = re.compile(r"(?<![\d.])(\d+\.\d+\.\d+)\s*节")
CH_REF = re.compile(r"第\s*(\d+)\s*章")


def check_refs(sections: list[Section], book: dict, rep: Report) -> None:
    defined = set().union(*(s.defines for s in sections)) if sections else set()
    written = {s.id for s in sections}
    known = {s["id"] for c in book["chapters"] for s in c["sections"]}
    nchap = len(book["chapters"])
    for sec in sections:
        text = FENCE.sub("", sec.source)
        refs = set()
        for m in EQ_LIST.finditer(text):
            refs.update(f"式 {x}" for x in m.groups() if x)
        for m in REF.finditer(text):
            if m.group(1) != "式":
                refs.add(f"{m.group(1)} {m.group(2)}")
        for r in sorted(refs):
            if r in defined:
                continue
            target = ".".join(r.split(" ")[1].split(".")[:2])
            if target in known and target not in written:
                rep.add("warning", "引用", sec.id, f"{r} 所在的 {target} 节尚未写出")
            else:
                rep.add("error", "引用", sec.id, f"{r} 不存在")
        for m in SEC_REF.finditer(text):
            sid = m.group(1)
            if sid not in known:
                rep.add("error", "引用", sec.id, f"{sid} 节不在提纲里")
            elif sid not in written:
                rep.add("warning", "引用", sec.id, f"{sid} 节尚未写出")
        for m in SUB_REF.finditer(text):
            sid = m.group(1)
            if f"节 {sid}" in defined:
                continue
            parent = sid.rsplit(".", 1)[0]
            if parent in known and parent not in written:
                rep.add("warning", "引用", sec.id, f"{sid} 节所在的 {parent} 节尚未写出")
            else:
                rep.add("error", "引用", sec.id, f"{sid} 节不存在")
        for m in CH_REF.finditer(text):
            if not 1 <= int(m.group(1)) <= nchap:
                rep.add("error", "引用", sec.id, f"第 {m.group(1)} 章不存在（全书 {nchap} 章）")


NUMBER = re.compile(r"(?<![\w.{])(\d+\.\d+)(?![\w.]|\d)")


def check_numbers(sec: Section, rep: Report) -> None:
    """A decimal with 4+ significant digits must come from a program ({{…}}), not be typed by hand."""
    text = FENCE.sub("", sec.source)
    text = PLACE.sub("", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\b(?:JJF|JJG|GB(?:/T)?|JB(?:/T)?|ISO|IEC|IEEE|DIN|VDI|EN|ASTM|ASME|AWS|SAE)\s*[A-Z]?[\d.]+", "", text)     # standard numbers, e.g. JJF 1059.1, JB/T 9165.2
    text = re.split(r"\*\*本节参考文献\*\*|#+\s*(?:本章)?参考文献|\*\*Section references\*\*|#+\s*(?:Chapter )?References", text, flags=re.I)[0]
    for line_no, line in enumerate(text.splitlines(), 1):
        for m in NUMBER.finditer(line):
            digits = m.group(1).replace(".", "").lstrip("0")
            if len(digits) >= 4:
                rep.add("error", "手写数字", sec.id, f"“{m.group(1)}” 应由程序给出（写成 {{{{程序.名称}}}}）：{line.strip()[:60]}")


TERM = re.compile(r"\*\*([\u4e00-\u9fff][\u4e00-\u9fff·\-–]{1,11})\*\*(?![：:])")   # "**小标题**：" is a lead-in, not a term


LABELS = {"工程师笔记", "生活中的例子", "机器人的例子", "习题", "证明", "参考文献", "本节参考文献", "本章参考文献", "章首提要", "本章小结", "注意", "提示", "历史注记", "估一估"}


def _norm_term(t: str) -> str:
    return re.sub(r"[-–—]", "-", t)


def check_terms(sec: Section, terms: set[str], rep: Report) -> None:
    known = {_norm_term(x) for x in terms}
    for t in dict.fromkeys(TERM.findall(sec.source)):
        if _norm_term(t) not in known and t not in LABELS:
            rep.add("error", "术语", sec.id, f"“{t}” 不在术语表里（conventions/术语表.csv）")


# ---------------------------------------------------------------- output

CSS = (TOOLS / "book.css")


def page(title: str, body: str, lang: str = "zh") -> str:
    return (f"<!doctype html><html lang='{'en' if lang == 'en' else 'zh-CN'}'><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
            f"<meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS.read_text(encoding='utf-8')}</style>"
            f"</head><body><main class='wq-book'>{body}</main></body></html>")


def _toc_sections(c: dict, sections: list, sections_en: list = ()) -> list[dict]:
    have = {x.id: x for x in sections}
    en = {x.id: x for x in sections_en}
    out = [{"id": s["id"], "title": s["title"], "written": s["id"] in have} for s in c["sections"]]
    for sid, at in ((f"{c['no']}.0", 0), (f"{c['no']}.end", None)):
        if sid in have:
            item = {"id": sid, "title": have[sid].title, "written": True, "kind": "intro" if at == 0 else "summary"}
            out.insert(0, item) if at == 0 else out.append(item)
    for item in out:
        if item["id"] in en:
            item["en"] = True
            item["title_en"] = en[item["id"]].title
    return out


def check_refs_en(sections_en: list[Section], defined: set, written: set, book: dict, rep: Report) -> None:
    known = {s["id"] for c in book["chapters"] for s in c["sections"]}
    nchap = len(book["chapters"])
    for sec in sections_en:
        where = sec.id + "（英文版）"
        items, secs, chs = english.refs(sec.source)
        for r in sorted(items):
            if r in defined:
                continue
            target = ".".join(r.split(" ")[1].split(".")[:2])
            if target in known and target not in written:
                rep.add("warning", "引用", where, f"{r} 所在的 {target} 节尚未写出")
            else:
                rep.add("error", "引用", where, f"{r} 不存在")
        for sid in secs:
            if sid.count(".") == 2:
                if f"节 {sid}" in defined:
                    continue
                parent = sid.rsplit(".", 1)[0]
                if parent in known and parent not in written:
                    rep.add("warning", "引用", where, f"Section {sid} 所在的 {parent} 节尚未写出")
                else:
                    rep.add("error", "引用", where, f"Section {sid} 不存在")
            elif sid not in known:
                rep.add("error", "引用", where, f"Section {sid} 不在提纲里")
            elif sid not in written:
                rep.add("warning", "引用", where, f"Section {sid} 尚未写出")
        for n in chs:
            if not 1 <= n <= nchap:
                rep.add("error", "引用", where, f"Chapter {n} 不存在（全书 {nchap} 章）")


def build(book_name: str, pdf: bool = False, only: set | None = None, out_dir: Path | None = None,
          root: Path | None = None, labs: bool = False) -> Report:
    """root: a book folder elsewhere (tests); its book.yaml is then not compared with the outline."""
    rep = Report()
    book = load_book(book_name, root)
    if root is None:
        outline_in_sync(book_name, rep)
    sections = load_sections(book, rep, only)
    sections_en = load_sections_en(book, sections, rep)
    prog_meta = progress(book)
    terms = glossary(book)
    check_other_books(book, rep)
    check_std_tables(book, rep)
    values = run_programs(book, {s.chapter for s in sections}, rep)
    en_chapters = {s.chapter for s in sections_en}
    values_en = run_programs(book, en_chapters, rep, "en") if en_chapters else {}
    for prog, v in values_en.items():
        for why in english.same_values(values.get(prog, {}), v, prog):
            rep.add("error", "程序", "英文版", why)
    formulas: list = []
    figdir = book["root"].parent / "build" / book_name / "figs"
    for sec in sections:
        sec.figdir = figdir
        check_tags(sec, rep)
        check_numbers(sec, rep)
        check_terms(sec, terms, rep)
        sec.html = render_section(sec, fill(sec, values, rep), values, rep, formulas)
    check_refs(sections, book, rep)
    zh_of = {s.id: s for s in sections}
    gl_en = glossary_en(book)
    for sec in sections_en:      # 英文版 (第 8 轮): same structure as the Chinese section, English terms, own references
        zh = zh_of[sec.id]
        sec.figdir = figdir
        where = sec.id + "（英文版）"
        for why in english.parity(zh.source, sec.source):
            rep.add("error", "英文版", where, why)
        sec.defines = set(zh.defines)
        left = sorted(set(re.findall(r"[\u4e00-\u9fff]+", FENCE.sub("", sec.source))))
        if left:
            rep.add("error", "英文版", where, "正文里还有中文：" + "、".join(left[:8]))
        check_numbers(sec, rep)
        for why in english.check_terms(zh.source, sec.source, gl_en):
            rep.add("error", "术语", where, why)
        sec.html = render_section(sec, fill(sec, values_en, rep), values_en, rep, formulas)
    check_refs_en(sections_en, set().union(*(s.defines for s in sections)) if sections else set(), {s.id for s in sections}, book, rep)
    for sec in [*sections, *sections_en]:      # 动画代替不了示意图 (Eddie 2026-10-01): every animation has its static figure
        for label, fig in sec.anim_figs:
            if not fig:
                rep.add("error", "图", sec.id, f"{label} 没有配示意图（在动画里写“图: x.y.z”，并在正文放这张图）")
            elif f"图 {fig}" not in sec.defines:
                rep.add("error", "图", sec.id, f"{label} 配的图 {fig} 不在本节")
    svgs, imgs = typeset(formulas, rep)
    for sec in [*sections, *sections_en]:
        sec.html_mp = re.sub(r"WQMATH(\d+)Z", lambda m: imgs[int(m.group(1))], sec.html)
        sec.html = re.sub(r"WQMATH(\d+)Z", lambda m: svgs[int(m.group(1))], sec.html)

    out = out_dir or (book["root"].parent / "build" / book_name)
    web = out / "web"
    web.mkdir(parents=True, exist_ok=True)
    titles = {c["no"]: c["title"] for c in book["chapters"]}
    meta_ch = {int(k): v or {} for k, v in (prog_meta.get("chapters") or {}).items()}
    for no, v in meta_ch.items():
        if v.get("status") and v["status"] not in STATUS:
            rep.add("error", "结构", "progress.yaml", f"第 {no} 章的状态 {v['status']} 应为 {'、'.join(STATUS)} 之一")
    for no in en_chapters:
        if not meta_ch.get(no, {}).get("title_en"):
            rep.add("error", "英文版", "progress.yaml", f"第 {no} 章有英文版，请写出英文章名 title_en")
    parts_en = prog_meta.get("parts_en") or {}
    index = {"book": book_name, "title": book["title"], "title_en": book.get("title_en", ""), "parts": book["parts"],
             "parts_en": parts_en,
             "chapters": [{"no": c["no"], "title": c["title"], "level": c["level"], "part": c["part"],
                           "title_en": meta_ch.get(c["no"], {}).get("title_en", ""), "status": meta_ch.get(c["no"], {}).get("status", ""),
                           "sections": _toc_sections(c, sections, sections_en)} for c in book["chapters"]],
             "errors": len(rep.errors)}
    # 互动资源 (第 9 轮 2.5): every chapter's animations and labs, in reading order, for the reader's lists
    en_cap = {(s.id, k, n): c for s in sections_en for k, n, c in s.media}
    index["resources"] = {}
    for sec in sections:
        for k, n, c in sec.media:
            index["resources"].setdefault(str(sec.chapter), []).append(
                {"kind": k, "num": n, "title": c, "title_en": en_cap.get((sec.id, k, n), ""), "sec": sec.id})
    for sec in sections:
        head = html.escape(sec.title) if sec.id.endswith((".0", ".end")) else f"{sec.id}　{html.escape(sec.title)}"
        frag = f"<section class='wq-sec' id='sec-{sec.id}'><h2>{head}</h2>{sec.html}</section>"
        (web / f"{sec.id}.html").write_text(frag, encoding="utf-8")
        (web / f"{sec.id}.mp.html").write_text(
            f"<section class='wq-sec'><h2>{head}</h2>{sec.html_mp}</section>", encoding="utf-8")
    (web / "en").mkdir(exist_ok=True)
    for sec in sections_en:
        head = html.escape(sec.title) if sec.id.endswith((".0", ".end")) else f"{sec.id}&nbsp; {html.escape(sec.title)}"
        (web / "en" / f"{sec.id}.html").write_text(f"<section class='wq-sec' id='sec-{sec.id}' lang='en'><h2>{head}</h2>{sec.html}</section>", encoding="utf-8")
        (web / "en" / f"{sec.id}.mp.html").write_text(f"<section class='wq-sec' lang='en'><h2>{head}</h2>{sec.html_mp}</section>", encoding="utf-8")
    (web / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    by_ch: dict[int, list[Section]] = {}
    for sec in sections:
        by_ch.setdefault(sec.chapter, []).append(sec)
    index["pdf"] = sorted(by_ch) if pdf and not rep.errors else []
    by_ch_en: dict[int, list[Section]] = {}
    for sec in sections_en:
        by_ch_en.setdefault(sec.chapter, []).append(sec)
    index["pdf_en"] = sorted(by_ch_en) if pdf and not rep.errors else []
    anim_dir = out / "anim"
    anim_dir.mkdir(exist_ok=True)
    index["anims"] = {}
    for sec in sections:
        for name, h, code in sec.anims:
            (anim_dir / f"{name}.py").write_text(code, encoding="utf-8")
            index["anims"][name] = h
    (web / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    lab_dir = out / "lab"
    lab_dir.mkdir(exist_ok=True)
    index["labs"] = {}
    for ch, secs in sorted(by_ch.items()):
        items = [x for sec in secs for x in sec.labs]
        if not items:
            continue
        page_html = labkit().page(items, course=[book["title"], book.get("title_en", "")], chapter=[f"第{ch}章", f"Chapter {ch}"],
                                  key=f"wq-book-{book_name}", models=book_models(book))
        (lab_dir / f"ch{ch:02d}.html").write_text(page_html, encoding="utf-8")
        index["labs"][str(ch)] = [no for no, _ in items]
        for sec in secs:      # 实验指导书与报告模板 (第 7 轮第 4 步补充)
            for no, script, g in sec.labdocs:
                try:
                    m = labdocs.meta(script)
                except ValueError as e:
                    rep.add("error", "实验", sec.id, f"实验 {no}：{e}")
                    continue
                where = (f"《{book['title']}》{sec.id} 节", f"{book.get('title_en') or book['title']}, Section {sec.id}")
                stem = f"lab{no.replace('.', '_')}"
                labdocs.guide(m, g, lab_dir / f"{stem}-guide.docx", no, where)
                labdocs.report(m, g, lab_dir / f"{stem}-report.docx", no, where)
        for sec in by_ch_en.get(ch, []):      # the English edition's lab documents (English only)
            for no, script, g in sec.labdocs:
                bad = labdocs.english_problems(g)
                for why in bad:
                    rep.add("error", "实验", sec.id + "（英文版）", f"Lab {no}：{why}")
                if bad:
                    continue
                try:
                    m = labdocs.meta(script)
                except ValueError as e:
                    rep.add("error", "实验", sec.id + "（英文版）", f"Lab {no}：{e}")
                    continue
                where = (f"{book.get('title_en') or book['title']}, Section {sec.id}",) * 2
                stem = f"lab{no.replace('.', '_')}"
                labdocs.guide_en(m, g, lab_dir / f"{stem}-guide.en.docx", no, where[0])
                labdocs.report_en(m, g, lab_dir / f"{stem}-report.en.docx", no, where[0])
        if labs:
            trial_labs(page_html, [no.replace(".", "-") for no, _ in items], rep, f"第 {ch} 章实验页")
    index["tasks"] = {}           # 工程任务单 (第 13 轮): task sheet, rubric and blank calculation sheet in Word
    task_dir = out / "task"
    for ch, secs in sorted(by_ch.items()):
        for sec in secs:
            for no, path, t in sec.tasks:
                where = ((f"《{book['title']}》第 {ch} 章", f"{book.get('title_en') or book['title']}, Chapter {ch}")
                         if sec.id.endswith((".0", ".end")) else      # 章首、章末小结不是“节”
                         (f"《{book['title']}》{sec.id} 节", f"{book.get('title_en') or book['title']}, Section {sec.id}"))
                stem = f"ts{no.replace('.', '_')}"
                try:
                    tasksheet.task_doc(t, task_dir / f"{stem}-task.docx", no, where)
                    tasksheet.rubric_doc(t, task_dir / f"{stem}-rubric.docx", no, where)
                    tasksheet.blank_calc(t, path.parent.parent, task_dir / f"{stem}-calc.docx", book["root"] / "conventions")
                except Exception as e:  # noqa: BLE001 — a broken task sheet is reported, not a crash
                    rep.add("error", "任务", sec.id, f"任务 {no}：生成 Word 失败：{e}")
                    continue
                spec = dict(t, book=book["book"], no=no, section=sec.id, where=list(where),
                            docs=[k for k in ("task", "rubric", "calc") if (task_dir / f"{stem}-{k}.docx").exists()])
                (task_dir / f"{stem}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")   # 下达时发给数字工厂（第 11 轮 2.7（5））
                index["tasks"].setdefault(str(ch), []).append({"no": no, "id": t["编号"], "title": t["标题"], "section": sec.id})
    (web / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    for ch, secs in by_ch.items():
        body = (f"<h1>第 {ch} 章　{html.escape(titles[ch])}</h1>"
                + "".join(f"<section class='wq-sec'><h2>{html.escape(s.title) if s.id.endswith(('.0', '.end')) else s.id + '　' + html.escape(s.title)}</h2>{s.html}</section>" for s in secs))
        (out / f"ch{ch:02d}.html").write_text(page(f"第 {ch} 章 {titles[ch]}", body), encoding="utf-8")
    for ch, secs in by_ch_en.items():
        t_en = meta_ch.get(ch, {}).get("title_en", "")
        body = (f"<h1>Chapter {ch}&nbsp; {html.escape(t_en)}</h1>"
                + "".join(f"<section class='wq-sec' lang='en'><h2>{html.escape(s.title) if s.id.endswith(('.0', '.end')) else s.id + '&nbsp; ' + html.escape(s.title)}</h2>{s.html}</section>" for s in secs))
        (out / f"ch{ch:02d}.en.html").write_text(page(f"Chapter {ch} {t_en}", body, "en"), encoding="utf-8")
    if pdf and not rep.errors:
        make_pdfs(out, sorted(by_ch), rep)
        make_pdfs(out, sorted(by_ch_en), rep, ".en")
    (out / "report.txt").write_text("\n".join(map(str, rep.problems)) or "全部检查通过", encoding="utf-8")
    return rep


def make_pdfs(out: Path, chapters: list[int], rep: Report, suffix: str = "") -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        exe = os.environ.get("WQ_CHROMIUM")
        b = p.chromium.launch(**({"executable_path": exe} if exe else {}))
        pg = b.new_page()
        for ch in chapters:
            pg.goto((out / f"ch{ch:02d}{suffix}.html").as_uri())
            pg.pdf(path=str(out / f"ch{ch:02d}{suffix}.pdf"), format="A4", print_background=True,
                   margin={"top": "22mm", "bottom": "22mm", "left": "20mm", "right": "20mm"},
                   display_header_footer=True, header_template="<span></span>",
                   footer_template="<div style='font-size:8px;width:100%;text-align:center;color:#666'>"
                                   "<span class='pageNumber'></span></div>")
        b.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="教材构建与检查")
    ap.add_argument("book", nargs="?", default="robotics")
    ap.add_argument("--pdf", action="store_true", help="同时生成每章 PDF")
    ap.add_argument("--only", help="只构建这些节，逗号分隔，如 4.1,4.2")
    ap.add_argument("--labs", action="store_true", help="在无头浏览器里试做每个虚拟实验的全部任务")
    a = ap.parse_args()
    rep = build(a.book, a.pdf, set(a.only.split(",")) if a.only else None, labs=a.labs)
    for p in rep.problems:
        print(p)
    n_err, n_warn = len(rep.errors), len(rep.problems) - len(rep.errors)
    print(f"\n{'未通过' if n_err else '通过'}：{n_err} 个错误，{n_warn} 个提醒。输出在 textbook/build/{a.book}/")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
