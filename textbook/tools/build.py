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

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[1]
KINDS = ("程序", "动画", "实验", "图", "表")
REF_KINDS = ("式", "定义", "定理", "引理", "推论", "算例", "程序", "图", "表", "动画", "实验", "习题")


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
    defines: set = field(default_factory=set)


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
    for path in sorted(book["root"].glob("ch[0-9][0-9]/[0-9][0-9]-*.md"), key=lambda p: [int(x) for x in re.findall(r"\d+", p.name)]):
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


def glossary(book: dict) -> set[str]:
    p = book["root"] / "conventions" / "术语表.csv"
    with p.open(encoding="utf-8") as f:
        return {row["中文"].strip() for row in csv.DictReader(f)}


# ---------------------------------------------------------------- programs and placeholders

def run_programs(book: dict, chapters: set[int], rep: Report) -> dict[str, dict]:
    values: dict[str, dict] = {}
    cache = book["root"].parent / "build" / book["book"] / "values"
    cache.mkdir(parents=True, exist_ok=True)
    for ch in sorted(chapters):
        for prog in sorted((book["root"] / f"ch{ch:02d}" / "code").glob("*.py")):
            where = str(prog.relative_to(book["root"].parent))
            digest = hashlib.sha256(prog.read_bytes() + (TOOLS / "bookout.py").read_bytes()).hexdigest()[:16]
            hit = cache / f"{prog.stem}.{digest}.json"
            if hit.exists():
                values[prog.stem] = json.loads(hit.read_text(encoding="utf-8"))
                continue
            outp = cache / f"{prog.stem}.out.json"
            outp.unlink(missing_ok=True)
            figs = cache.parent / "figs"
            figs.mkdir(exist_ok=True)
            env = {**os.environ, "WQ_BOOK_OUT": str(outp), "WQ_BOOK_FIGDIR": str(figs), "PYTHONPATH": str(TOOLS), "MPLBACKEND": "Agg"}
            try:
                r = subprocess.run([sys.executable, prog.name], cwd=prog.parent, env=env, capture_output=True, text=True, timeout=300)
            except subprocess.TimeoutExpired:
                rep.add("error", "程序", where, "运行超过 5 分钟")
                continue
            if r.returncode != 0:
                rep.add("error", "程序", where, "运行出错：" + (r.stderr.strip().splitlines() or ["?"])[-1])
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
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            try:
                return format(v, fmt.strip()) if fmt else (str(v) if isinstance(v, int) else sig(v))
            except ValueError:
                rep.add("error", "占位符", sec.id, f"{m.group(0)}：格式 {fmt} 不对")
                return m.group(0)
        return str(v)
    return PLACE.sub(one, sec.source)


# ---------------------------------------------------------------- formulas, directives, markdown

DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.S)
INLINE = re.compile(r"(?<![\\$])\$(?!\$)([^$\n]+?)\$")
FENCE = re.compile(r"^```.*?^```", re.S | re.M)
DIRECTIVE = re.compile(r"^:::[ \t]*(" + "|".join(KINDS) + r")[ \t]+([\d.]+)[ \t]*\n(.*?)^:::[ \t]*$", re.S | re.M)
TAG = re.compile(r"\\tag\{([^}]+)\}")


def protect(text: str, store: list, pattern: re.Pattern, make) -> str:
    def one(m):
        store.append(make(m))
        return f"WQTOKEN{len(store) - 1}Z"
    return pattern.sub(one, text)


def directive_html(sec: Section, kind: str, num: str, body: str, values: dict, rep: Report) -> str:
    meta, rest = {}, []
    for line in body.splitlines():
        m = re.match(r"^(src|说明|模板|模型|caption|图)\s*[:：]\s*(.*)$", line.strip())
        if m and not rest:
            meta[m.group(1)] = m.group(2).strip()
        else:
            rest.append(line)
    note = "\n".join(rest).strip()
    label = f"{kind} {num}"
    sec.defines.add(label)
    cap = html.escape(meta.get("说明", "") or meta.get("caption", ""))
    if kind == "程序":
        src = meta.get("src", "")
        p = sec.path.parent / src
        if not src or not p.exists():
            rep.add("error", "程序", sec.id, f"{label}：找不到 {src or '（未写 src）'}")
            code = ""
        else:
            code = p.read_text(encoding="utf-8")
        result = values.get(Path(src).stem)
        res = ""
        if result:
            res = "<div class='wq-prog-out'><b>运行结果</b><pre>" + html.escape(
                "\n".join(f"{k} = {format(v, '.6g') if isinstance(v, float) else v}" for k, v in result.items() if not k.startswith("_"))) + "</pre></div>"
        return (f"<figure class='wq-prog' id='{kind}-{num}'><figcaption>{label}　{cap}</figcaption>"
                f"<details><summary>程序 {html.escape(src)}</summary><pre class='wq-code'><code>{html.escape(code)}</code></pre></details>"
                f"{res}{('<p>' + html.escape(note) + '</p>') if note else ''}</figure>")
    if kind == "图":
        src = meta.get("src", "")
        p = sec.figdir / f"{src}.svg" if src else None
        if not p or not p.exists():
            rep.add("error", "图", sec.id, f"{label}：没有找到示意图 {src or '（未写 src）'}（由 code/ 里的程序用 bookout.figure 生成）")
            return f"<figure class='wq-fig' id='{kind}-{num}'><div class='wq-media-box'>【{label}】</div></figure>"
        import base64
        data = base64.b64encode(p.read_bytes()).decode()
        return (f"<figure class='wq-fig' id='{kind}-{num}'><img class='wq-figimg' alt='{label}' src='data:image/svg+xml;base64,{data}'/>"
                f"<figcaption>{label}　{cap}</figcaption>{('<p>' + html.escape(note) + '</p>') if note else ''}</figure>")
    if kind == "动画":
        fig = meta.get("图", "")
        sec.anim_figs.append((label, fig))
    cls = {"动画": "wq-anim", "实验": "wq-lab", "表": "wq-tab"}[kind]
    src = html.escape(meta.get("src", ""))
    # media are produced in later steps (animator, labkit); until then a placeholder box shows what will be there
    return (f"<figure class='{cls}' id='{kind}-{num}' data-src='{src}'><div class='wq-media-box'>【{label}】{cap}</div>"
            f"<figcaption>{label}　{cap}</figcaption>{('<p>' + html.escape(note) + '</p>') if note else ''}</figure>")


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
    for kind in ("定义", "定理", "引理", "推论", "算例"):
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
    text = text.split("**本节参考文献**")[0].split("## 参考文献")[0]
    for line_no, line in enumerate(text.splitlines(), 1):
        for m in NUMBER.finditer(line):
            digits = m.group(1).replace(".", "").lstrip("0")
            if len(digits) >= 4:
                rep.add("error", "手写数字", sec.id, f"“{m.group(1)}” 应由程序给出（写成 {{{{程序.名称}}}}）：{line.strip()[:60]}")


TERM = re.compile(r"\*\*([\u4e00-\u9fff][\u4e00-\u9fff·\-–]{1,11})\*\*")


LABELS = {"工程师笔记", "习题", "证明", "参考文献", "本节参考文献", "本章参考文献", "章首提要", "本章小结", "注意", "提示", "历史注记"}


def check_terms(sec: Section, terms: set[str], rep: Report) -> None:
    for t in dict.fromkeys(TERM.findall(sec.source)):
        if t not in terms and t not in LABELS:
            rep.add("error", "术语", sec.id, f"“{t}” 不在术语表里（conventions/术语表.csv）")


# ---------------------------------------------------------------- output

CSS = (TOOLS / "book.css")


def page(title: str, body: str) -> str:
    return (f"<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
            f"<meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS.read_text(encoding='utf-8')}</style>"
            f"</head><body><main class='wq-book'>{body}</main></body></html>")


def build(book_name: str, pdf: bool = False, only: set | None = None, out_dir: Path | None = None,
          root: Path | None = None) -> Report:
    """root: a book folder elsewhere (tests); its book.yaml is then not compared with the outline."""
    rep = Report()
    book = load_book(book_name, root)
    if root is None:
        outline_in_sync(book_name, rep)
    sections = load_sections(book, rep, only)
    terms = glossary(book)
    values = run_programs(book, {s.chapter for s in sections}, rep)
    formulas: list = []
    figdir = book["root"].parent / "build" / book_name / "figs"
    for sec in sections:
        sec.figdir = figdir
        check_tags(sec, rep)
        check_numbers(sec, rep)
        check_terms(sec, terms, rep)
        sec.html = render_section(sec, fill(sec, values, rep), values, rep, formulas)
    check_refs(sections, book, rep)
    for sec in sections:      # 动画代替不了示意图 (Eddie 2026-10-01): every animation has its static figure
        for label, fig in sec.anim_figs:
            if not fig:
                rep.add("error", "图", sec.id, f"{label} 没有配示意图（在动画里写“图: x.y.z”，并在正文放这张图）")
            elif f"图 {fig}" not in sec.defines:
                rep.add("error", "图", sec.id, f"{label} 配的图 {fig} 不在本节")
    svgs, imgs = typeset(formulas, rep)
    for sec in sections:
        sec.html_mp = re.sub(r"WQMATH(\d+)Z", lambda m: imgs[int(m.group(1))], sec.html)
        sec.html = re.sub(r"WQMATH(\d+)Z", lambda m: svgs[int(m.group(1))], sec.html)

    out = out_dir or (book["root"].parent / "build" / book_name)
    web = out / "web"
    web.mkdir(parents=True, exist_ok=True)
    titles = {c["no"]: c["title"] for c in book["chapters"]}
    index = {"book": book_name, "title": book["title"], "parts": book["parts"],
             "chapters": [{"no": c["no"], "title": c["title"], "level": c["level"], "part": c["part"],
                           "sections": [{"id": s["id"], "title": s["title"], "written": s["id"] in {x.id for x in sections}}
                                        for s in c["sections"]]} for c in book["chapters"]],
             "errors": len(rep.errors)}
    for sec in sections:
        frag = f"<section class='wq-sec' id='sec-{sec.id}'><h2>{sec.id}　{html.escape(sec.title)}</h2>{sec.html}</section>"
        (web / f"{sec.id}.html").write_text(frag, encoding="utf-8")
        (web / f"{sec.id}.mp.html").write_text(
            f"<section class='wq-sec'><h2>{sec.id}　{html.escape(sec.title)}</h2>{sec.html_mp}</section>", encoding="utf-8")
    (web / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    by_ch: dict[int, list[Section]] = {}
    for sec in sections:
        by_ch.setdefault(sec.chapter, []).append(sec)
    index["pdf"] = sorted(by_ch) if pdf and not rep.errors else []
    (web / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    for ch, secs in by_ch.items():
        body = (f"<h1>第 {ch} 章　{html.escape(titles[ch])}</h1>"
                + "".join(f"<section class='wq-sec'><h2>{s.id}　{html.escape(s.title)}</h2>{s.html}</section>" for s in secs))
        (out / f"ch{ch:02d}.html").write_text(page(f"第 {ch} 章 {titles[ch]}", body), encoding="utf-8")
    if pdf and not rep.errors:
        make_pdfs(out, sorted(by_ch), rep)
    (out / "report.txt").write_text("\n".join(map(str, rep.problems)) or "全部检查通过", encoding="utf-8")
    return rep


def make_pdfs(out: Path, chapters: list[int], rep: Report) -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        exe = os.environ.get("WQ_CHROMIUM")
        b = p.chromium.launch(**({"executable_path": exe} if exe else {}))
        pg = b.new_page()
        for ch in chapters:
            pg.goto((out / f"ch{ch:02d}.html").as_uri())
            pg.pdf(path=str(out / f"ch{ch:02d}.pdf"), format="A4", print_background=True,
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
    a = ap.parse_args()
    rep = build(a.book, a.pdf, set(a.only.split(",")) if a.only else None)
    for p in rep.problems:
        print(p)
    n_err, n_warn = len(rep.errors), len(rep.problems) - len(rep.errors)
    print(f"\n{'未通过' if n_err else '通过'}：{n_err} 个错误，{n_warn} 个提醒。输出在 textbook/build/{a.book}/")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
