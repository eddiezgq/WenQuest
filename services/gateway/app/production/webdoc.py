"""问渠网页文档（第 122 轮）：一份文档 = 有结构的内容块，同一份数据出网页、Word 和作业正文。

文档 {"v": 1, "kind": "labreport", "title": [中文, English], "blocks": [...]}，块的种类 t：
  title   {zh, en}                        大标题
  fields  {items: [{k, label, v}]}         表头栏（姓名、学号……），每行三对，可填
  note    {text}                           小字说明
  h       {zh, en}                         中英对照的小节标题
  p       {zh, en}                         中英对照的固定段落
  strong  {text}                           加粗的一行（实际问题的题目）
  label   {text}                           普通的一行提示
  prompt  {zh, en}                         题目或提示（思考题、五步）
  text    {id, lines, v}                   学生写的区域；空的时候 Word 里画 lines 条横线；$…$ 写公式
  table   {id, title: [zh, en], head, head_en, rows, grow?, records?}
          rows 里模板给的非空格子只读，空格子和 {{名}} 格子可填；grow 可加行；records 是“记入报告”的实验记录表
  check   {id, options: [[zh, en]], v: [下标], other}   勾选（AI 使用声明），other 是“其他”后面写的字
  figure  {id, png, caption, src?}         图：学生由表格画的或上传的，png 是 base64；src 记作图用的表和列
  rubric  {head, rows}                     评分量规，只读

学生能改的只有：fields 的 v、text 的 v、table 可填的格子和 grow 加的行、check 的 v / other、figure（加、删、改）。
`merge(template, student)` 只取这些，别的一律以模板为准，所以学生的数据改不了栏目、题目和量规。
"""
from __future__ import annotations

import base64
import binascii
import io
import re
from copy import deepcopy
from typing import Any

PLACEHOLDER = re.compile(r"\{\{\s*([^{}\s]+)\s*\}\}")
MAX_FIGURES = 8
MAX_PNG = 600_000          # 一张图的 PNG 最大字节数
MAX_TEXT = 20_000          # 一个写作区最多字数
MAX_ROWS = 200             # 一张表最多行数（含加的行）
MAX_CELL = 200


class DocError(ValueError):
    pass


def editable_cell(tpl: str) -> bool:
    """A template cell the student fills in: empty, or a {{name}} the lab can fill."""
    return tpl.strip() == "" or bool(PLACEHOLDER.fullmatch(tpl.strip()))


def placeholders(doc: dict) -> dict[str, tuple[str, int, int]]:
    """{{name}} → (table id, row, column) for every placeholder cell of the template."""
    out = {}
    for b in doc["blocks"]:
        if b["t"] == "table":
            for i, r in enumerate(b["rows"]):
                for j, c in enumerate(r):
                    mt = PLACEHOLDER.fullmatch(str(c).strip())
                    if mt:
                        out[mt.group(1)] = (b["id"], i, j)
    return out


def blank(doc: dict, gpu: bool = False) -> dict:
    """The template as a student starts it: placeholder cells empty (a GPU lab keeps them for the returned numbers)."""
    d = deepcopy(doc)
    if not gpu:
        for b in d["blocks"]:
            if b["t"] == "table":
                b["rows"] = [[("" if PLACEHOLDER.fullmatch(str(c).strip()) else c) for c in r] for r in b["rows"]]
    return d


def _s(x: Any, n: int) -> str:
    return str(x if x is not None else "")[:n]


def _png(s: Any) -> str:
    s = str(s or "")
    if s.startswith("data:image/png;base64,"):
        s = s.split(",", 1)[1]
    try:
        raw = base64.b64decode(s, validate=True)
    except (binascii.Error, ValueError):
        raise DocError("图片不是有效的 PNG")
    if not raw.startswith(b"\x89PNG") or len(raw) > MAX_PNG:
        raise DocError("图片不是 PNG，或超过 600 KB")
    try:
        from PIL import Image
        with Image.open(io.BytesIO(raw)) as im:
            im.verify()
    except Exception:  # noqa: BLE001 - any decoding problem means Word could not show it either
        raise DocError("图片打不开")
    return base64.b64encode(raw).decode()


def merge(template: dict, student: dict) -> dict:
    """The template with only the student's answers taken from `student` (anything else there is ignored)."""
    out = deepcopy(template)
    got = {b.get("id") or f"_{b['t']}": b for b in (student or {}).get("blocks") or [] if isinstance(b, dict) and "t" in b}
    figures = [b for b in (student or {}).get("blocks") or [] if isinstance(b, dict) and b.get("t") == "figure"]
    for b in out["blocks"]:
        s = got.get(b.get("id") or f"_{b['t']}")
        if not s or s.get("t") != b["t"]:
            continue
        if b["t"] == "fields":
            vals = {x.get("k"): x.get("v") for x in s.get("items") or [] if isinstance(x, dict)}
            for it in b["items"]:
                if it.get("fixed"):
                    continue
                it["v"] = _s(vals.get(it["k"], it.get("v", "")), 80)
        elif b["t"] == "text":
            b["v"] = _s(s.get("v"), MAX_TEXT)
        elif b["t"] == "check":
            n = len(b["options"])
            b["v"] = sorted({int(i) for i in s.get("v") or [] if isinstance(i, int) and 0 <= i < n})
            b["other"] = _s(s.get("other"), 400)
        elif b["t"] == "table":
            ncol = len(b["head"])
            srows = [r for r in s.get("rows") or [] if isinstance(r, list)]
            rows = []
            for i, tr in enumerate(b["rows"]):
                sr = srows[i] if i < len(srows) else []
                rows.append([(_s(sr[j] if j < len(sr) else "", MAX_CELL) if editable_cell(str(c)) else c)
                             for j, c in enumerate(tr)])
            if b.get("grow"):
                for sr in srows[len(b["rows"]):MAX_ROWS]:
                    rows.append([_s(sr[j] if j < len(sr) else "", MAX_CELL) for j in range(ncol)])
            b["rows"] = rows
    figs = []
    for f in figures[:MAX_FIGURES]:
        src = f.get("src") if isinstance(f.get("src"), dict) else None
        figs.append({"t": "figure", "id": _s(f.get("id") or f"fig{len(figs) + 1}", 40), "png": _png(f.get("png")),
                     "caption": _s(f.get("caption"), 200), **({"src": {k: _s(v, 40) for k, v in src.items()}} if src else {})})
    if figs:      # figures go right after the data tables (part four), where the template asks for a graph
        at = next((i + 1 for i, b in enumerate(out["blocks"]) if b.get("id") == "process"), len(out["blocks"]))
        out["blocks"][at:at] = figs
    return out


def fill(doc: dict, template: dict, values: dict[str, Any]) -> dict:
    """Put numbers the lab reported into the {{name}} cells of a student's document (positions from the template)."""
    pos = placeholders(template)
    for name, v in values.items():
        if name in pos:
            tid, i, j = pos[name]
            for b in doc["blocks"]:
                if b["t"] == "table" and b["id"] == tid and i < len(b["rows"]) and j < len(b["rows"][i]):
                    b["rows"][i][j] = _s(v, MAX_CELL)
    return doc


# ----------------------------------------------------------------------------- Word

def to_docx(doc: dict, path: str | None = None, *, template: bool = False) -> bytes:
    """Word in the platform's course layout. A template (nothing written yet) draws ruled lines in the empty areas."""
    from . import docgen
    d = docgen.Doc()
    for b in doc["blocks"]:
        t = b["t"]
        if t == "title":
            d.title(b["zh"], b.get("en"))
        elif t == "fields":
            items = b["items"]
            rows = [[x for it in items[i:i + 3] for x in (it["label"], it.get("v", ""))] for i in range(0, len(items), 3)]
            d.table(rows[0], rows[1:], widths=[2.4, 3.2, 2.2, 2.8, 2.2, 3.2], font_size=10)
        elif t == "note":
            d.en(b["text"], size=9)
        elif t == "h":
            d.bh(b["zh"], b["en"])
        elif t == "p":
            d.bp(b["zh"], b["en"])
        elif t == "strong":
            d.p(b["text"], indent=False).runs[0].bold = True
        elif t == "label":
            d.p(b["text"], indent=False)
        elif t == "prompt":
            d.p(b["zh"], indent=False)
            d.en(b["en"])
        elif t == "text":
            v = (b.get("v") or "").strip()
            if v:
                for line in v.splitlines():
                    d.p(line, indent=False)
            elif b.get("lines"):
                d.lines(b["lines"])
        elif t == "table":
            title = b.get("title") or ["", ""]
            if title[0]:
                d.p(f"{title[0]}  {title[1]}".strip(), indent=False)
            n = len(b["head"])
            rows = b["rows"] or ([[""] * n] if b.get("records") else [])
            if template and b.get("records"):
                rows = [[""] * n] * 3
            widths = [2.0, 3.0, 6.0, 5.0] if b.get("records") and n == 4 else [round(16.0 / n, 2)] * n
            d.table([str(h) for h in b["head"]], [[str(c) for c in r] for r in rows], widths=widths, font_size=9.5)
        elif t == "check":
            boxes = "　　".join(("☑ " if i in (b.get("v") or []) else "□ ") + o[0] for i, o in enumerate(b["options"]))
            other = b.get("other") or ""
            d.p(f"{boxes}　　□ 其他：{other or '____________'}" if not other else f"{boxes}　　☑ 其他：{other}", indent=False)
            d.en("   ".join("□ " + o[1] for o in b["options"]) + "   □ Other: ____________")
        elif t == "figure":
            raw = base64.b64decode(b["png"])
            d.d.add_picture(io.BytesIO(raw), width=docgen.Cm(13))
            d.d.paragraphs[-1].alignment = docgen.WD_ALIGN_PARAGRAPH.CENTER
            if b.get("caption"):
                d.en(b["caption"], size=9.5)
        elif t == "rubric":
            d.table(b["head"], b["rows"], widths=[4.0, 2.2, 9.8], font_size=9.5)
    buf = io.BytesIO()
    d.d.save(buf)
    data = buf.getvalue()
    if path:
        with open(path, "wb") as f:
            f.write(data)
    return data


# ----------------------------------------------------------------------------- 作业正文（HTML）

def _e(s: Any) -> str:
    import html
    return html.escape(str(s or ""))


def to_html(doc: dict) -> str:
    """The report as the assignment's online text: what the teacher and the AI grading suggestion read."""
    out = []
    for b in doc["blocks"]:
        t = b["t"]
        if t == "title":
            out.append(f"<h2>{_e(b['zh'])}<br><small>{_e(b.get('en'))}</small></h2>")
        elif t == "fields":
            out.append("<p>" + "；".join(f"{_e(it['label'])}：{_e(it.get('v'))}" for it in b["items"] if it.get("v")) + "</p>")
        elif t == "h":
            out.append(f"<h3>{_e(b['zh'])}　<small>{_e(b['en'])}</small></h3>")
        elif t in ("prompt", "p"):
            out.append(f"<p><em>{_e(b['zh'])}</em></p>")
        elif t == "label":
            out.append(f"<p><em>{_e(b['text'])}</em></p>")
        elif t == "strong":
            out.append(f"<p><strong>{_e(b['text'])}</strong></p>")
        elif t == "text":
            v = (b.get("v") or "").strip()
            out.append("".join(f"<p>{_e(x)}</p>" for x in v.splitlines()) if v else "<p>（未填写）</p>")
        elif t == "table":
            if not b["rows"]:
                continue
            title = (b.get("title") or [""])[0]
            head = "".join(f"<th>{_e(h)}</th>" for h in b["head"])
            body = "".join("<tr>" + "".join(f"<td>{_e(c)}</td>" for c in r) + "</tr>" for r in b["rows"])
            out.append(f"<p><strong>{_e(title)}</strong></p><table border='1'><tr>{head}</tr>{body}</table>")
        elif t == "check":
            sel = [b["options"][i][0] for i in b.get("v") or []] + ([f"其他：{b['other']}"] if b.get("other") else [])
            out.append(f"<p>{'；'.join(_e(x) for x in sel) or '（未勾选）'}</p>")
        elif t == "figure":
            out.append(f"<p>［图：{_e(b.get('caption') or '学生作图')}］</p>")
    return "\n".join(out)


def plain_words(doc: dict) -> int:
    """How much the student has written (characters in text areas and filled cells)."""
    n = 0
    for b in doc["blocks"]:
        if b["t"] == "text":
            n += len((b.get("v") or "").strip())
    return n
