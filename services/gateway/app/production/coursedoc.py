"""老师用的网页文档（第 126 轮）：教案、实验指导书、通知等，老师自由编排的内容块。

文档 {"v": 1, "kind": "coursedoc", "template": "blank|plan|guide|notice", "title": [中文, English],
      "sub": "副标题（可空）", "blocks": [...]}，块的种类 t：
  h        {level: 1-3, text, en}            小节标题；en 可空（中英对照时写英文）
  para     {text, en}                        段落；$…$ 写公式；en 可空
  list     {ordered, items: [{text, en}]}    列表
  table    {id, caption, head: [...], rows: [[...]]}   表格（老师可增删行列）
  image    {img, caption}                    图片：img 是图片库里的编号（上传的照片或由表格作的图）
  callout  {text}                            提示框
  hr       {}                                分隔线

和第 122 轮实验报告（webdoc.py）不同，这里所有内容老师都能改，所以没有“模板合并”，只做 `clean()`：
只留认得的块和字段，限制长度。同一份数据出 Word（docgen 版式）和课程页面的正文（HTML）。
"""
from __future__ import annotations

import html
import io
import re
from typing import Any, Callable

TEMPLATES = ("blank", "plan", "guide", "notice")
MAX_BLOCKS = 400
MAX_TEXT = 20_000
MAX_ROWS = 300
MAX_COLS = 12
MAX_CELL = 2000
MAX_ITEMS = 100
IMG = re.compile(r"^[0-9a-f]{32}$")


class DocError(ValueError):
    pass


def _s(x: Any, n: int) -> str:
    return str(x if x is not None else "")[:n]


def clean(doc: Any) -> dict:
    """Only known blocks and fields, within limits; anything else is dropped."""
    if not isinstance(doc, dict):
        raise DocError("不是文档")
    title = doc.get("title") if isinstance(doc.get("title"), list) else [doc.get("title") or "", ""]
    out = {"v": 1, "kind": "coursedoc", "template": doc.get("template") if doc.get("template") in TEMPLATES else "blank",
           "title": [_s(title[0] if title else "", 200), _s(title[1] if len(title) > 1 else "", 200)],
           "sub": _s(doc.get("sub"), 300), "blocks": []}
    blocks = [b for b in doc.get("blocks") or [] if isinstance(b, dict)]
    if len(blocks) > MAX_BLOCKS:
        raise DocError(f"内容块太多（最多 {MAX_BLOCKS} 块）")
    n = 0
    for b in blocks:
        t = b.get("t")
        if t == "h":
            lv = b.get("level") if b.get("level") in (1, 2, 3) else 1
            out["blocks"].append({"t": "h", "level": lv, "text": _s(b.get("text"), 300), "en": _s(b.get("en"), 300)})
        elif t == "para":
            out["blocks"].append({"t": "para", "text": _s(b.get("text"), MAX_TEXT), "en": _s(b.get("en"), MAX_TEXT)})
        elif t == "list":
            items = []
            for it in (b.get("items") or [])[:MAX_ITEMS]:
                it = it if isinstance(it, dict) else {"text": it}
                items.append({"text": _s(it.get("text"), 2000), "en": _s(it.get("en"), 2000)})
            out["blocks"].append({"t": "list", "ordered": bool(b.get("ordered")), "items": items or [{"text": "", "en": ""}]})
        elif t == "table":
            head = [_s(h, 200) for h in (b.get("head") or [])[:MAX_COLS]] or ["", ""]
            nc = len(head)
            rows = []
            for r in (b.get("rows") or [])[:MAX_ROWS]:
                r = r if isinstance(r, list) else []
                rows.append([_s(r[j] if j < len(r) else "", MAX_CELL) for j in range(nc)])
            n += 1
            out["blocks"].append({"t": "table", "id": _s(b.get("id") or f"t{n}", 40), "caption": _s(b.get("caption"), 300),
                                  "head": head, "rows": rows})
        elif t == "image":
            img = str(b.get("img") or "")
            if IMG.match(img):
                out["blocks"].append({"t": "image", "img": img, "caption": _s(b.get("caption"), 300)})
        elif t == "callout":
            out["blocks"].append({"t": "callout", "text": _s(b.get("text"), MAX_TEXT)})
        elif t == "hr":
            out["blocks"].append({"t": "hr"})
    return out


def images_of(doc: dict) -> list[str]:
    return [b["img"] for b in doc["blocks"] if b["t"] == "image"]


def words(doc: dict) -> int:
    n = 0
    for b in doc["blocks"]:
        if b["t"] in ("para", "callout", "h"):
            n += len(b.get("text", "").strip())
        elif b["t"] == "list":
            n += sum(len(it["text"].strip()) for it in b["items"])
        elif b["t"] == "table":
            n += sum(len(c.strip()) for r in b["rows"] for c in r)
    return n


def headings(doc: dict) -> list[str]:
    return [b["text"] for b in doc["blocks"] if b["t"] == "h"]


# ----------------------------------------------------------------------------- 模板

def H(text: str, en: str = "", level: int = 1) -> dict:
    return {"t": "h", "level": level, "text": text, "en": en}


def P(text: str = "", en: str = "") -> dict:
    return {"t": "para", "text": text, "en": en}


def L(items: list, ordered: bool = False) -> dict:
    return {"t": "list", "ordered": ordered,
            "items": [{"text": x[0], "en": x[1]} if isinstance(x, (list, tuple)) else {"text": x, "en": ""} for x in items]}


def T(head: list[str], rows: list[list[str]], caption: str = "", tid: str = "") -> dict:
    return {"t": "table", "id": tid, "caption": caption, "head": head, "rows": rows}


# 教案：栏目与 production/docs.py 的 plan() 一致（测试比对）
PLAN_HEADINGS = ["一、教学目标", "二、教学重点与难点", "三、教学方法", "四、教学过程", "五、板书设计", "六、课后作业", "七、教学反思"]
PLAN_PROCESS_HEAD = ["环节", "时间", "教学内容", "师生活动"]
# 实验指导书：栏目与 docs.py 的 guide() 一致
GUIDE_HEADINGS = [("一、实验目的", "1  Objectives"), ("二、实验原理", "2  Principles"), ("三、实验环境", "3  The virtual lab"),
                  ("四、实验步骤", "4  Procedure"), ("五、数据记录", "5  Data record"), ("六、注意事项", "6  Notes"),
                  ("七、思考题", "7  Questions"), ("八、与实际问题的联系", "8  Connection to a real problem")]


def template(kind: str, title: str = "", course: str = "", teacher: str = "") -> dict:
    """A new document of this kind: the headings and tables of the course's Word layout, to be filled in (or by AI)."""
    title = title.strip()
    if kind == "plan":
        blocks = [T(["课题", "授课对象", "学时", "授课方式"], [[title, "", "2 学时", "讲授 + 动画 + 虚拟实验 + 课堂练习"]], tid="info"),
                  H(PLAN_HEADINGS[0]), L([("知识目标：", ""), ("能力目标：", ""), ("素养目标：", "")]),
                  H(PLAN_HEADINGS[1]), P("重点："), P("难点："),
                  H(PLAN_HEADINGS[2]), P(),
                  H(PLAN_HEADINGS[3]), T(PLAN_PROCESS_HEAD, [["导入", "10 min", "", ""], ["新课", "40 min", "", ""],
                                                            ["小结", "10 min", "", ""]], tid="process"),
                  H(PLAN_HEADINGS[4]), P(), H(PLAN_HEADINGS[5]), P(), H(PLAN_HEADINGS[6]), P("（课后填写）")]
        doc = {"template": "plan", "title": [f"{course}教案" if course else "教案", ""],
               "sub": title + (f"  ·  授课教师：{teacher}" if teacher else ""), "blocks": blocks}
    elif kind == "guide":
        blocks = []
        for zh, en in GUIDE_HEADINGS:
            blocks.append(H(zh, en))
            if zh.startswith("四") or zh.startswith("七"):
                blocks.append(L([("", "")], ordered=True))
            elif zh.startswith("五"):
                blocks.append(T(["", ""], [["", ""]], caption="表 1", tid="t1"))
            else:
                blocks.append(P())
        doc = {"template": "guide", "title": [title or "实验指导书", ""], "sub": "", "blocks": blocks}
    elif kind == "notice":
        doc = {"template": "notice", "title": [title or "通知", ""], "sub": "",
               "blocks": [P(), H("时间与地点", "Time and place"), T(["事项", "时间", "地点"], [["", "", ""]], tid="when"),
                          H("要求", "What to do"), L([("", "")], ordered=True), callout("如有问题，请在课程讨论区留言。")]}
    else:
        doc = {"template": "blank", "title": [title or "未命名文档", ""], "sub": "", "blocks": [P()]}
    return clean(doc)


def callout(text: str) -> dict:
    return {"t": "callout", "text": text}


def from_plan(spec: dict, gp: dict, no: str, course: str, chapter: str, teacher: str = "") -> dict:
    """教案 from the AI course workshop's lesson design: the same content as docs.plan() writes into Word."""
    pl, s = gp["plan"], spec
    o = pl["objectives"]
    rows = [[x["phase"], f"{x['minutes']} min" if x["minutes"] else "", x["content"], x["activity"]] for x in pl["process"]]
    if not rows:
        rows = [["导入", "10 min", s["problem"]["text"][0], "提出机器人问题，学生讨论"],
                ["新课", "40 min", "；".join(p[0] for p in s["concept"]["points"]), "讲授 + 板书"],
                ["动画", "10 min", s["animation"]["question"][0], "播放并暂停提问"],
                ["实验", "15 min", "；".join(t[0] for t in s["lab"]["tasks"]), "课堂演示"],
                ["建模", "15 min", s["model"]["solve"][0], "师生共同完成五步"],
                ["小结", "10 min", "；".join(x[0] for x in s["summary"]), "布置练习和实验报告"]]
    blocks = [T(["课题", "授课对象", "学时", "授课方式"],
                [[f"{no} {s['title'][0]}", pl["audience"] or "—", pl["hours"] or "2 学时", pl["method"] or "讲授 + 动画 + 虚拟实验 + 课堂练习"]],
                tid="info"),
              H(PLAN_HEADINGS[0]),
              L([("知识目标：" + (o["knowledge"] or s["goal"][0]), ""), ("能力目标：" + (o["ability"] or "能针对实际问题建立模型并求解。"), ""),
                 ("素养目标：" + (o["literacy"] or "体会“建立模型—求解—检验—修正”的科学方法。"), "")]),
              H(PLAN_HEADINGS[1]),
              P("重点：" + (pl["key"] or "；".join(p[0] for p in s["concept"]["points"][:2]))), P("难点：" + (pl["difficult"] or "—")),
              H(PLAN_HEADINGS[2]),
              P("以机器人实际问题驱动：先提出问题，再讲概念，用动画建立直观，用虚拟实验验证，最后回到问题按五步建模求解。"),
              H(PLAN_HEADINGS[3]), T(PLAN_PROCESS_HEAD, rows, tid="process"),
              H(PLAN_HEADINGS[4]), P(pl["board"] or "—"),
              H(PLAN_HEADINGS[5]), P(pl["homework"] or "完成本节练习；完成虚拟实验任务并按实验指导书写实验报告。"),
              H(PLAN_HEADINGS[6]), P(pl["reflection"] or "（课后填写）")]
    return clean({"template": "plan", "title": [f"{course}教案", ""],
                  "sub": f"{chapter}  ·  {no} {s['title'][0]}" + (f"  ·  授课教师：{teacher}" if teacher else ""), "blocks": blocks})


def from_guide(spec: dict, gp: dict, no: str) -> dict:
    """实验指导书 from the lesson design: the same content as docs.guide() writes into Word."""
    from .docs import LINK
    g, s = gp["guide"], spec
    blocks: list[dict] = [H(*GUIDE_HEADINGS[0]), L([tuple(x) for x in (g["goal"] or [s["goal"]])], ordered=True),
                          H(*GUIDE_HEADINGS[1])]
    blocks += [P(zh, en) for zh, en in g["theory"]]
    blocks += [H(*GUIDE_HEADINGS[2]), P(f"打开方式：{LINK}"),
               P(f"场景：{s['lab']['robot_scene'][0]}；{s['lab']['life_scene'][0]}", f"Scenes: {s['lab']['robot_scene'][1]}; {s['lab']['life_scene'][1]}")]
    if g["env"]:
        both = lambda x: x[0] if x[0] == x[1] or not x[1] else f"{x[0]}\n{x[1]}"  # noqa: E731
        blocks.append(T(["项目 Item", "范围 Range"], [[f"{e['item'][0]} {e['item'][1]}", both(e["range"])] for e in g["env"]], tid="env"))
    blocks += [H(*GUIDE_HEADINGS[3]), L([tuple(x) for x in g["steps"]], ordered=True), H(*GUIDE_HEADINGS[4]),
               P("以下表格同时出现在实验报告模板中，请在报告里填写。", "The same tables appear in the report template; fill them in there.")]
    for i, t in enumerate(g["tables"], 1):
        blocks.append(T(t["headers"], t["rows"], caption=f"{t['caption'][0]}  {t['caption'][1]}", tid=f"t{i}"))
    blocks += [H(*GUIDE_HEADINGS[5]), L([tuple(x) for x in g["cautions"]]), H(*GUIDE_HEADINGS[6]), L([tuple(x) for x in g["questions"]], ordered=True),
               H(*GUIDE_HEADINGS[7])]
    p = s["problem"]
    q = g["problem_question"] if g["problem_question"][0] else p["text"]
    blocks += [P(f"机器人问题：{p['title'][0]}", f"Robot problem: {p['title'][1]}"), P(q[0], q[1]),
               P("请在实验报告“实际问题的建模与求解”一栏中按五步完成：① 实际问题 ② 建立模型（写出简化假设）③ 求解 ④ 用虚拟实验检验 ⑤ 指出模型在哪里失效、怎样修正。",
                 "In the report section “Modelling a real problem”, work through five steps: ① the problem ② the model (state your assumptions) "
                 "③ the solution ④ a check with the virtual lab ⑤ where the model fails and how to improve it."),
               P("生活中的例子：" + s["everyday"]["text"][0], "Everyday example: " + s["everyday"]["text"][1])]
    return clean({"template": "guide", "title": [f"实验 {no}  {s['lab']['title'][0]}", f"Lab {no}  {s['lab']['title'][1]}"],
                  "sub": "", "blocks": blocks})


# ----------------------------------------------------------------------------- Word

def _widths(n: int) -> list[float]:
    return [round(16.0 / n, 2)] * n


def to_docx(doc: dict, image: Callable[[str], bytes | None] = lambda _k: None) -> bytes:
    from . import docgen
    d = docgen.Doc()
    t0, t1 = doc["title"][0], doc["title"][1]
    d.title(t0, doc.get("sub") or t1 or None)
    if doc.get("sub") and t1:
        d.en(t1)
    for b in doc["blocks"]:
        t = b["t"]
        if t == "h":
            if b.get("en"):
                d.bh(b["text"], b["en"], level=b["level"])
            else:
                d.h(b["text"], b["level"])
        elif t == "para":
            for line in (b["text"] or "").splitlines() or [""]:
                if line.strip():
                    d.p(line)
            if b.get("en"):
                d.en(b["en"], indent=True)
        elif t == "list":
            for i, it in enumerate(b["items"], 1):
                para = d.d.add_paragraph() if b["ordered"] else d.d.add_paragraph(style="List Bullet")
                if b["ordered"]:
                    para.paragraph_format.left_indent = docgen.Pt(22)
                    para.paragraph_format.first_line_indent = docgen.Pt(-16)
                docgen._font(para.add_run((f"{i}. " if b["ordered"] else "") + it["text"]))
                if it.get("en"):
                    para.add_run().add_break()
                    r = para.add_run(it["en"])
                    r.font.size = docgen.Pt(9.5)
                    r.font.color.rgb = docgen.RGBColor.from_string("5B6B75")
        elif t == "table":
            if b.get("caption"):
                d.p(b["caption"], indent=False)
            d.table(b["head"], b["rows"], widths=_widths(len(b["head"])), font_size=9.5)
        elif t == "image":
            raw = image(b["img"])
            if raw:
                d.d.add_picture(io.BytesIO(raw), width=docgen.Cm(14))
                d.d.paragraphs[-1].alignment = docgen.WD_ALIGN_PARAGRAPH.CENTER
                if b.get("caption"):
                    d.en(b["caption"], size=9.5)
        elif t == "callout":
            para = d.p(b["text"], indent=False)
            para.paragraph_format.left_indent = docgen.Pt(12)
            for r in para.runs:
                r.font.color.rgb = docgen.RGBColor.from_string("1F6F8B")
        elif t == "hr":
            d.lines(1)
    buf = io.BytesIO()
    d.d.save(buf)
    return buf.getvalue()


# ----------------------------------------------------------------------------- 课程页面正文（HTML）

def _math(s: str) -> str:
    """Escape, and write $…$ / $$…$$ the way the course pages typeset formulas (\\( \\) and \\[ \\])."""
    e = html.escape(s or "")
    e = re.sub(r"\$\$([^$]+)\$\$", r"\\[\1\\]", e)
    return re.sub(r"\$([^$\n]+)\$", r"\\(\1\\)", e)


def to_html(doc: dict, img_url: Callable[[str], str] = lambda k: k) -> str:
    """The document as the Moodle page's content: what students (and the classic view) see once it is published."""
    out = []
    if doc.get("sub"):
        out.append(f"<p style=\"text-align:center;color:#555\">{html.escape(doc['sub'])}</p>")
    for b in doc["blocks"]:
        t = b["t"]
        if t == "h":
            lv = b["level"] + 1
            en = f" <small style=\"color:#5b6b75;font-weight:normal\">{html.escape(b['en'])}</small>" if b.get("en") else ""
            out.append(f"<h{lv}>{html.escape(b['text'])}{en}</h{lv}>")
        elif t == "para":
            for line in (b["text"] or "").splitlines():
                if line.strip():
                    out.append(f"<p>{_math(line)}</p>")
            if b.get("en"):
                out.append(f"<p style=\"color:#5b6b75\">{_math(b['en'])}</p>")
        elif t == "list":
            tag = "ol" if b["ordered"] else "ul"
            lis = "".join(f"<li>{_math(it['text'])}" + (f"<br><span style=\"color:#5b6b75\">{_math(it['en'])}</span>" if it.get("en") else "")
                          + "</li>" for it in b["items"])
            out.append(f"<{tag}>{lis}</{tag}>")
        elif t == "table":
            cap = f"<p><strong>{html.escape(b['caption'])}</strong></p>" if b.get("caption") else ""
            head = "".join(f"<th>{html.escape(h)}</th>" for h in b["head"])
            body = "".join("<tr>" + "".join(f"<td>{_math(c).replace(chr(10), '<br>')}</td>" for c in r) + "</tr>" for r in b["rows"])
            out.append(f"{cap}<table border=\"1\" style=\"border-collapse:collapse\"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>")
        elif t == "image":
            cap = f"<p style=\"text-align:center;color:#555\">{html.escape(b['caption'])}</p>" if b.get("caption") else ""
            out.append(f"<p style=\"text-align:center\"><img src=\"{html.escape(img_url(b['img']))}\" alt=\"{html.escape(b.get('caption') or '')}\" "
                       f"style=\"max-width:100%\"></p>{cap}")
        elif t == "callout":
            out.append(f"<blockquote>{_math(b['text']).replace(chr(10), '<br>')}</blockquote>")
        elif t == "hr":
            out.append("<hr>")
    return "\n".join(out) or "<p>&nbsp;</p>"


def plain(doc: dict) -> str:
    """The document as plain text (for AI context)."""
    out = [doc["title"][0]]
    for b in doc["blocks"]:
        t = b["t"]
        if t == "h":
            out.append("\n## " + b["text"])
        elif t in ("para", "callout"):
            out.append(b["text"])
        elif t == "list":
            out += [f"- {it['text']}" for it in b["items"]]
        elif t == "table":
            out.append(" | ".join(b["head"]))
            out += [" | ".join(r) for r in b["rows"]]
    return "\n".join(out)
