"""Word → 网页文档的内容块（第 128 轮）：把平台自己生成的 Word（计算书、调机卡……）按原顺序拆成标题、段落、表格、图片。

这样网页文档和 Word 导出出自同一份计算结果，数字一致；拆出来的块都标 lock（计算出来的，网页上不能改）。
只认平台 docgen 版式里用到的东西：标题样式（Heading 1–3）、普通段落、表格（第一行当表头）、段落里的图片。
"""
from __future__ import annotations

import io
from typing import Callable

from docx import Document
from docx.oxml.ns import qn


def blocks_of(data: bytes, put_image: Callable[[bytes, str], str] | None = None) -> tuple[str, str, list[dict]]:
    """(大标题, 副标题, 块)。put_image(图片字节, 类型) → 图片编号；不给就丢掉图片。"""
    d = Document(io.BytesIO(data))
    body = d.element.body
    title, sub = "", ""
    out: list[dict] = []
    n_tab = 0
    paras = {p._p: p for p in d.paragraphs}
    tables = {t._tbl: t for t in d.tables}
    first = True
    for el in body.iterchildren():
        if el.tag == qn("w:p"):
            p = paras.get(el)
            if p is None:
                continue
            for blip in el.iter(qn("a:blip")):
                rid = blip.get(qn("r:embed"))
                part = d.part.related_parts.get(rid) if rid else None
                if part is not None and put_image:
                    mime = getattr(part, "content_type", "image/png")
                    if mime in ("image/png", "image/jpeg"):
                        out.append({"t": "image", "img": put_image(part.blob, mime), "caption": "", "lock": True})
            text = p.text.strip()
            if not text:
                continue
            style = (p.style.name if p.style is not None else "") or ""
            centered = p.alignment is not None and int(p.alignment) == 1
            if first and centered:                 # docgen.title(): a centred title, then a centred subtitle
                title = text
                first = False
                continue
            first = False
            if centered and not sub and not out:
                sub = text
                continue
            if style.startswith("Heading"):
                lv = style.rsplit(" ", 1)[-1]
                out.append({"t": "h", "level": min(3, max(1, int(lv) if lv.isdigit() else 1)), "text": text, "en": "", "lock": True})
            elif centered and out and out[-1]["t"] == "image" and not out[-1]["caption"]:
                out[-1]["caption"] = text          # a figure's caption
            else:
                out.append({"t": "para", "text": text, "en": "", "lock": True})
        elif el.tag == qn("w:tbl"):
            t = tables.get(el)
            if t is None:
                continue
            rows = []
            for r in t.rows:
                cells, seen = [], set()
                for c in r.cells:              # merged cells repeat: keep each once
                    if id(c._tc) in seen:
                        continue
                    seen.add(id(c._tc))
                    cells.append(c.text.strip())
                rows.append(cells)
            if not rows:
                continue
            w = max(len(r) for r in rows)
            rows = [r + [""] * (w - len(r)) for r in rows]
            n_tab += 1
            caption = ""
            if out and out[-1]["t"] == "para" and len(out[-1]["text"]) <= 60 and out[-1]["text"].startswith(("表", "Table")):
                caption = out.pop()["text"]
            out.append({"t": "table", "id": f"c{n_tab}", "caption": caption, "head": rows[0], "rows": rows[1:], "lock": True})
    return title, sub, out
