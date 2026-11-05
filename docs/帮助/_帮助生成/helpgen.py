# -*- coding: utf-8 -*-
"""网页互动帮助的共用生成程序（第 90 轮从第 49 轮缝纫机帮助抽出）：缝纫机、轴承、凸轮三款软件共用。

每款软件自己的 build.py 只管：章节顺序（EDITIONS）、文中的数（{{键}}，由计算核心算）、动画与小计算器（anim.js）、
“试一试”按钮打开软件的地址（try_url）。这里管：Markdown + 指令 → 网页、目录、版式（template.html）、离线包。

指令（单独一行）：
  ::anim{id=…}            动画（anim.js 里的 A.…）
  ::calc{id=…}            小计算器（anim.js 里的 CALC.…）
  ::video{src=… title="…"}  录像（mp4 + 封面 jpg + 中文字幕 vtt）
  ::img{src=… caption="…"}  截图
  ::try{label="…" …}      “试一试”：带参数打开软件（地址由各软件的 try_url 给）
  ::only{web} … ::end      只在某一份里出现
"""
from __future__ import annotations

import base64
import html
import json
import re
import shutil
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "template.html"
ONLINE = "https://learn.wenquestrobotics.com"

ATTR = re.compile(r'(\w+)=(?:"([^"]*)"|\'([^\']*)\'|(\S+))')
DIR = re.compile(r"^::(\w+)\{(.*)\}\s*$", re.M)
ONLY = re.compile(r"^::only\{(\w+)\}\s*\n(.*?)^::end\s*$", re.M | re.S)


def attrs(s):
    return {m.group(1): m.group(2) if m.group(2) is not None else m.group(3) if m.group(3) is not None else m.group(4) for m in ATTR.finditer(s)}


def lookup(vals, path):
    x = vals
    for k in path.split("."):
        x = x[int(k)] if isinstance(x, list) else x[k]
    return x


def directive(name, a, ed, media_prefix, try_url):
    e = html.escape
    if name == "anim":
        return f'<div class="anim" data-anim="{e(a["id"])}"></div>'
    if name == "calc":
        return f'<div class="calc" data-calc="{e(a["id"])}"></div>'
    if name == "video":
        v = a["src"]
        cap = a.get("title", "")
        return (f'<figure class="vid"><video controls preload="none" playsinline poster="{media_prefix}{v}.jpg">'
                f'<source src="{media_prefix}{v}.mp4" type="video/mp4"><track kind="subtitles" srclang="zh" label="中文" default src="{media_prefix}{v}.vtt">'
                f'</video><figcaption>▶ {e(cap)}</figcaption></figure>')
    if name == "img":
        return f'<figure class="shot"><img loading="lazy" src="{media_prefix}{e(a["src"])}" alt="{e(a.get("caption", ""))}"><figcaption>{e(a.get("caption", ""))}</figcaption></figure>'
    if name == "try":
        return f'<a class="try" href="{e(try_url(a, ed))}" target="_blank" rel="noopener">▶ 试一试：{e(a["label"])}</a>'
    raise ValueError("unknown directive " + name)


def render(md, ed, vals, media_prefix, try_url):
    md = ONLY.sub(lambda m: m.group(2) if m.group(1) == ed else "", md)
    md = re.sub(r"\{\{([\w.]+)\}\}", lambda m: str(lookup(vals, m.group(1))), md)
    blocks = {}

    def keep(m):
        k = f"@@D{len(blocks)}@@"
        blocks[k] = directive(m.group(1), attrs(m.group(2)), ed, media_prefix, try_url)
        return "\n" + k + "\n"
    md = DIR.sub(keep, md)
    h = markdown.markdown(md, extensions=["tables", "fenced_code", "attr_list", "md_in_html"])
    for k, v in blocks.items():
        h = h.replace(f"<p>{k}</p>", v).replace(k, v)
    return h


def sections(src_dir, files, ed, vals, media_prefix, try_url):
    out, nav = [], []
    for i, f in enumerate(files):
        md = (src_dir / "sections" / (f + ".md")).read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---\n", md, re.S)
        meta = dict(x.split(":", 1) for x in m.group(1).splitlines()) if m else {}
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        body = md[m.end():] if m else md
        sid = meta["id"]
        h = render(body, ed, vals, media_prefix, try_url)
        subs = []

        def h3(mm):
            hid = mm.group(1) or f"{sid}-{len(subs) + 1}"
            t = re.sub("<[^>]+>", "", mm.group(2))
            subs.append((hid, t))
            return f'<h3 id="{hid}">{mm.group(2)}</h3>'
        h = re.sub(r'<h3(?: id="([^"]*)")?>(.*?)</h3>', h3, h)
        num = f"{i:02d}"
        out.append(f'<section id="{sid}"><h2><span class="n">{num}</span>{html.escape(meta["title"])}</h2>'
                   f'<p class="lead">{meta.get("lead", "")}</p>{h}</section>')
        nav.append((sid, num, meta["title"], subs))
    return "\n".join(out), nav


def nav_html(nav):
    s = []
    for sid, num, title, subs in nav:
        s.append(f'<a href="#{sid}" data-s="{sid}"><span class="n">{num}</span>{html.escape(title)}</a>')
        for k, t in subs:
            s.append(f'<a class="sub" href="#{k}" data-s="{sid}">{html.escape(t)}</a>')
    return "\n".join(s)


def build(src_dir, brand, E, ed, vals, data, out_dir, media_prefix, try_url, anim_js):
    """One edition of one help: E = {title, short, other: (name, url), files}."""
    body, nav = sections(src_dir, E["files"], ed, vals, media_prefix, try_url)
    t = TEMPLATE.read_text(encoding="utf-8")
    page = (t.replace("{{BRAND}}", brand).replace("{{TITLE}}", E["title"]).replace("{{SHORT}}", E["short"]).replace("{{NAV}}", nav_html(nav))
             .replace("{{BODY}}", body).replace("{{OTHER_NAME}}", E["other"][0]).replace("{{OTHER_URL}}", E["other"][1])
             .replace("{{EDITION}}", ed).replace("{{API}}", "" if ed == "web" else ONLINE)
             .replace("{{DATA}}", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
             .replace("{{ANIM_JS}}", anim_js))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8")
    return page


def offline(page_builder, media_dir, out_dir, online_media):
    """The FreeCAD offline copy: only the FreeCAD videos (fc-*) and pictures travel; subtitles inlined (file:// pages
    do not read the files beside them); the web videos and downloads point online."""
    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / "media").mkdir(parents=True)
    for f in media_dir.glob("*"):
        if f.is_file() and (f.name.startswith("fc-") or f.suffix in (".png", ".webp", ".jpg") and not f.name.startswith("web-")):
            shutil.copy2(f, out_dir / "media" / f.name)
    page = page_builder(out_dir, "media/")

    def inline_vtt(m):
        p = out_dir / "media" / m.group(1)
        return f'src="data:text/vtt;base64,{base64.b64encode(p.read_bytes()).decode()}"' if p.exists() else m.group(0)
    page = re.sub(r'src="media/([^"]+\.vtt)"', inline_vtt, page)
    page = page.replace('href="../media/', f'href="{online_media}')
    page = re.sub(r'(src|poster)="media/(web-[^"]+)"', lambda m: f'{m.group(1)}="{online_media}{m.group(2)}"', page)
    (out_dir / "index.html").write_text(page, encoding="utf-8")
    return page
