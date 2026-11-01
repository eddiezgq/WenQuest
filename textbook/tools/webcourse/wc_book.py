#!/usr/bin/env python3
"""普通教材（textbook/<书>/，用 build.py 构建）的网页互动课件（《机械制造技术》第 13 轮十起）。

课件引擎 wc_slides.py 原样不动：它读一个“书目录”（course/、img/*.webp、src/zh/labs/<页>.html）。这里先从这本书的构建产物
（textbook/build/<书>/）搭一个临时书目录，再调用引擎——与网关 AI 建课的做法相同（services/gateway/app/production/webdeck.py）。

    python3 textbook/<书>/course/tools/build_slides.py ch54 --out <目录> [--preview all] [--media <Manim 视频目录>]

先跑 `python3 textbook/tools/build.py <书>`（课件用它的插图、实验页、三维动画和算例程序）。

slides/chNN.yaml 在引擎格式之外多三样：
- `code: [ex54_4, …]`：本章 code/ 里的算例程序，课件里写 {{ex54_4.键:格式}}，与正文同一个程序、同一个数；
- 图：`{fig: fig54_4_2}` 直接用本章构建出的插图（svg 转 webp）；
- 公式：`{tex: "…"}` 或 `{tex: ["…", "…"]}`，与正文同一个 MathJax 排版，浅色排在深色舞台上；
- 活页面 `clips.<名>.page`：`lab54_3`（本章的实验，单独选中这一个）、`v54_3_1`（三维动画）、`a54_1_1`（Manim 动画）。
  Manim 动画只在服务器上渲染：课件里先放占位（WQANIM:名:散列），平台打开或下载课件时由网关填进视频
  （textbook_api.fill_slides）；本地预览用 --media 指向本地渲染的视频目录。
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import html as H
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
TB = HERE.parents[1]                      # textbook/
ROOT = TB.parent
ANIM_MARK = "WQANIM:{name}:{h}.{ext}"      # 网关按这个占位填 Manim 视频和静帧（与 services/gateway/app/textbook_api.py 一致）
ANIM_RE = re.compile(r"WQANIM:([A-Za-z0-9_]+):([0-9a-f]+)\.(mp4|png)")


def chapter_title(book: str, no: int) -> list[str]:
    bk = yaml.safe_load((TB / book / "book.yaml").read_text(encoding="utf-8"))
    zh = next((c["title"] for c in _walk(bk) if str(c.get("no")) == str(no) and "title" in c), f"第 {no} 章")
    prog = yaml.safe_load((TB / book / "progress.yaml").read_text(encoding="utf-8")) or {}
    en = ((prog.get("chapters") or {}).get(no) or {}).get("title_en", "")
    return [zh, en]


def _walk(x):
    if isinstance(x, dict):
        if "no" in x:
            yield x
        for v in x.values():
            yield from _walk(v)
    elif isinstance(x, list):
        for v in x:
            yield from _walk(v)


# ---------------------------------------------------------------- staging the "book folder" the engine reads
def tex_svgs(items: list[str]) -> list[str]:
    r = subprocess.run(["node", str(TB / "tools" / "tex2svg.mjs")], input=json.dumps([{"tex": t, "display": True} for t in items]),
                       capture_output=True, text=True, timeout=300, cwd=TB / "tools")
    if r.returncode:
        raise SystemExit("MathJax 失败：" + r.stderr[-300:])
    out = []
    for t, x in zip(items, json.loads(r.stdout)):
        if "error" in x:
            raise SystemExit(f"公式有错：{x['error']}：{t}")
        out.append(x["svg"])
    return out


def tex_block(svgs: list[str]) -> str:
    """Formulas for the dark stage: light ink, each line scaled to fit, centred."""
    rows = []
    for s in svgs:
        w = float(re.search(r'width="([\d.]+)ex"', s).group(1))
        h = float(re.search(r'height="([\d.]+)ex"', s).group(1))
        s = re.sub(r'^<svg ', f'<svg style="width:min(100%,{w * 0.5:.2f}em);height:auto;max-height:{h * 0.5:.2f}em;overflow:visible" ', s, count=1)
        rows.append(f'<div style="display:flex;justify-content:center;margin:26px 0">{s}</div>')
    return (f'<div style="display:flex;flex-direction:column;justify-content:center;height:100%;color:#f3f6fa;font-size:110px">'
            f'{"".join(rows)}</div>')


def svg_to_webp(src: Path, dst: Path, width: int = 1800) -> None:
    import cairosvg
    from PIL import Image
    png = dst.with_suffix(".png")
    cairosvg.svg2png(url=str(src), write_to=str(png), output_width=width, background_color="white")
    Image.open(png).convert("RGB").save(dst, "WEBP", quality=88)
    png.unlink()


def lab_page(book: str, no: str, lab: str) -> str:
    """The chapter's lab page with one lab chosen (the page also takes {type:'wq-lab', lab} from its parent)."""
    src = (TB / "build" / book / "lab" / f"ch{no}.html").read_text(encoding="utf-8")
    lid = re.sub(r"^lab", "", lab).replace("_", "-")
    pick = f"<script>postMessage({{type:'wq-lab',lab:'{lid}'}},'*');</script>"
    return src.replace("</body>", pick + "</body>", 1) if "</body>" in src else src + pick + "</body>"


def video_page(src: str, poster: str = "") -> str:
    return ("<!doctype html><html><head><meta charset='utf-8'><style>html,body{margin:0;height:100%;background:#000;overflow:hidden}"
            "video,.wait{width:100%;height:100%;object-fit:contain}.wait{display:flex;align-items:center;justify-content:center;color:#8fa3ba;"
            "font:28px system-ui,sans-serif}</style></head><body>"
            f"<video autoplay loop muted playsinline{f' poster={chr(39)}{poster}{chr(39)}' if poster else ''} src='{src}'></video></body></html>")


def b64(p: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode("ascii")


def stage(book: str, lesson: str, spec: dict, tmp: Path, media: Path | None) -> Path:
    no = int(re.sub(r"\D", "", lesson))
    bk = tmp / "a" / "b" / "c" / book
    course = bk / "course"
    (course / "slides").mkdir(parents=True)
    (course / "lessons").mkdir()
    (bk / "img").mkdir()
    labs = bk / "src" / "zh" / "labs"
    labs.mkdir(parents=True)
    src_course = TB / book / "course"
    shutil.copy(src_course / "course.yaml", course / "course.yaml")
    (course / "lessons" / f"{lesson}.json").write_text(json.dumps({"title": chapter_title(book, no)}, ensure_ascii=False), encoding="utf-8")
    build = TB / "build" / book
    anims = json.loads((build / "web" / "index.json").read_text(encoding="utf-8")).get("anims", {})

    # formulas → inline SVG; figures → img/<名>.webp
    texs = []

    def walk(x):
        if isinstance(x, dict):
            if "tex" in x and isinstance(x["tex"], (str, list)) and "svg" not in x:
                texs.append(x)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(spec["slides"])
    for x in texs:
        items = x.pop("tex")
        items = [items] if isinstance(items, str) else items
        x["svg"] = tex_block(tex_svgs(items))
    figs = set(re.findall(r"'fig': '([A-Za-z0-9_]+)'", repr(spec["slides"])))
    for f in sorted(figs):
        s = build / "figs" / f"{f}.svg"
        if not s.exists():
            raise SystemExit(f"没有插图 {s.relative_to(ROOT)}（先构建这本书）")
        svg_to_webp(s, bk / "img" / f"{f}.webp")

    # live pages
    pages = {c["page"] for c in (spec.get("clips") or {}).values()} | {s["shot"]["page"] for s in spec["slides"] if s["layout"] == "lab"}
    for p in sorted(pages):
        if p.startswith("lab"):
            html_ = lab_page(book, str(no), p)
        elif p in anims and p.startswith("v"):
            h = anims[p]
            html_ = video_page(b64(build / "anim3d" / f"{p}-{h}.mp4", "video/mp4"), b64(build / "anim3d" / f"{p}-{h}.png", "image/png"))
        elif p in anims:
            h = anims[p]
            mp4 = media and next(iter(sorted(media.glob(f"{p}-{h}.mp4")) + sorted(media.glob(f"**/{p}.mp4"))), None)
            if mp4:                     # 本地预览：直接放进本地渲染的视频，静帧取 70% 处
                png = tmp / f"{p}.png"
                dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
                                           capture_output=True, text=True).stdout or 1)
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur * 0.7:.2f}", "-i", str(mp4), "-frames:v", "1", str(png)], check=True)
                html_ = video_page(b64(mp4, "video/mp4"), b64(png, "image/png"))
            else:
                html_ = video_page(ANIM_MARK.format(name=p, h=h, ext="mp4"), ANIM_MARK.format(name=p, h=h, ext="png"))
        else:
            raise SystemExit(f"活页面 {p} 不认识：应是本章的实验（lab54_3）或动画（a54_1_1、v54_3_1）")
        (labs / f"{p}.html").write_text(html_, encoding="utf-8")
    (course / "slides" / f"{lesson}.yaml").write_text(yaml.safe_dump(spec, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return course


def run_book_programs(book: str, names: list[str]) -> dict:
    """The chapter's own worked-example programs (same numbers as the text)."""
    out = {}
    for n in names:
        ch = re.match(r"[a-z]+(\d+)_", n).group(1)
        prog = TB / book / f"ch{ch}" / "code" / f"{n}.py"
        with tempfile.TemporaryDirectory() as d:
            env = {**os.environ, "WQ_BOOK_OUT": str(Path(d) / "o.json"), "WQ_BOOK_FIGDIR": d, "MPLBACKEND": "Agg", "WQ_LANG": "zh",
                   "PYTHONPATH": os.pathsep.join([str(TB / "tools"), str(TB / book / "conventions")]), "WQ_REPO_ROOT": str(ROOT)}
            r = subprocess.run([sys.executable, prog.name], cwd=prog.parent, env=env, capture_output=True, text=True, timeout=600)
            if r.returncode:
                raise SystemExit(f"{n}.py 出错：{r.stderr[-500:]}")
            out[n] = json.loads((Path(d) / "o.json").read_text(encoding="utf-8"))
    return out


def make(book: str, lesson: str, out: Path, media: Path | None = None, keep: Path | None = None, plain: bool = False) -> Path:
    src = TB / book / "course" / "slides" / f"{lesson}.yaml"
    spec = yaml.safe_load(src.read_text(encoding="utf-8"))
    tmp = Path(tempfile.mkdtemp(prefix="wqslides-"))
    try:
        course = stage(book, lesson, spec, tmp, media)
        os.environ["WQ_COURSE_DIR"] = str(course)
        sys.path.insert(0, str(HERE))
        import wc_slides as W           # noqa: E402  （导入时读 WQ_COURSE_DIR）
        W.run_programs = lambda names: run_book_programs(book, names)
        no = int(re.sub(r"\D", "", lesson))
        title = chapter_title(book, no)
        name = f"{lesson}.html" if plain else f"第{no}章-{title[0]}-课件.html"     # plain：平台用（<书>/slides/chNN.html）
        deck = W.make_deck(lesson, out, name=name)
        s = deck.read_text(encoding="utf-8")
        s = s.replace(f"第 {no} 讲 Lecture {no}", f"第 {no} 章 Chapter {no}").replace(f"<title>第 {no} 讲 ", f"<title>第 {no} 章 ")
        deck.write_text(s, encoding="utf-8")
        if keep:
            shutil.copytree(tmp, keep, dirs_exist_ok=True)
        return deck
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(book: str):
    ap = argparse.ArgumentParser()
    ap.add_argument("lesson", nargs="*", help="ch54 …")
    ap.add_argument("--out", required=True)
    ap.add_argument("--preview", default="", help="页码（逗号分隔）或 all：出预览截图")
    ap.add_argument("--media", default="", help="本地预览：Manim 视频所在目录（服务器上由网关填）")
    ap.add_argument("--plain", action="store_true", help="文件名用 chNN.html（部署时放 textbook/build/<书>/slides/）")
    ap.add_argument("--all", action="store_true", help="course.yaml 里列出的、已有 slides/chNN.yaml 的各章")
    a = ap.parse_args()
    out = Path(a.out)
    lessons = list(a.lesson)
    if a.all:
        cfg = yaml.safe_load((TB / book / "course" / "course.yaml").read_text(encoding="utf-8"))
        lessons += [f"ch{n}" for n in cfg.get("lessons", []) if (TB / book / "course" / "slides" / f"ch{n}.yaml").exists()]
    if not lessons:
        raise SystemExit("没有要做的课件")
    for les in lessons:
        deck = make(book, les, out, Path(a.media) if a.media else None, plain=a.plain)
        print("deck:", deck, f"{deck.stat().st_size / 1e6:.2f} MB", "Manim 占位", len(set(ANIM_RE.findall(_pages_text(deck)))))
        if a.preview:
            import wc_slides as W
            n = deck.read_text(encoding="utf-8").count('<div class="slide ')
            only = None if a.preview == "all" else {int(x) for x in a.preview.split(",")}
            pv = out / f"preview-{les}"
            pv.mkdir(parents=True, exist_ok=True)
            asyncio.run(W.preview(deck, n, pv, only))


def _pages_text(deck: Path) -> str:
    s = deck.read_text(encoding="utf-8")
    return "".join(base64.b64decode(m).decode("utf-8", "replace") for m in re.findall(r'<script type="text/plain" data-page="[^"]+">([^<]+)</script>', s))
