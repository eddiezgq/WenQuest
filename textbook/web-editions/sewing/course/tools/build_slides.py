#!/usr/bin/env python3
"""第 24 轮：《缝纫机设计与制造》新版课件。

    python3 course/tools/build_slides.py ch01 --out <目录>                 # 生成 第1讲-…-课件.html（一个文件）
    python3 course/tools/build_slides.py ch01 --out <目录> --preview all   # 另出逐页预览截图，检查版式

内容在 course/slides/chNN.yaml（每页一个版式、最多 3 条、中文在上英文在下）。每页按 1920×1080 的网页版式排好，
用无头浏览器渲染成高清图片铺满整页；动画片段（网页动画、三维样机录屏）作为视频嵌进对应位置，PowerPoint 和
问渠放映器里都在原位播放；实验页放大截图和“打开虚拟实验”按钮（链接 #lab-1-1，问渠放映器里点它，实验在课件旁打开、
可以直接操作）。讲者备注是中英讲稿，放映时只给老师看，录课时当讲稿用。

数字：{{ch01.键:格式}} 由 course/calc/ch01.py 算出（设了 WQ_BOOK_OUT 时用 bookout.out 交出）。
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import html as H
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
COURSE = HERE.parent
BOOK = COURSE.parent
ROOT = BOOK.parents[2]
W, H_ = 1920, 1080
SCALE = 4 / 3                     # 渲染成 2560×1440
PH = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\s*(?::([^}]*))?\}\}")
COURSE_NAME = ["缝纫机设计与制造", "Sewing Machine Design and Manufacturing"]
LAB_URL = "https://learn.wenquestrobotics.com/#lab-{no}"


# ---------------------------------------------------------------- numbers from the course programs
def run_programs(names: list[str]) -> dict:
    out = {}
    for n in names:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        env = dict(os.environ, WQ_BOOK_OUT=path, MPLBACKEND="Agg",
                   PYTHONPATH=os.pathsep.join([str(BOOK.parent.parent / "tools"), os.environ.get("PYTHONPATH", "")]))
        r = subprocess.run([sys.executable, str(COURSE / "calc" / f"{n}.py")], env=env, capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(f"{n}.py failed: {r.stderr[-500:]}")
        out[n] = json.loads(Path(path).read_text(encoding="utf-8") or "{}")
        os.unlink(path)
    return out


def fill(x, values):
    if isinstance(x, str):
        def rep(m):
            v = values[m.group(1)][m.group(2)]
            return format(v, m.group(3)) if m.group(3) else str(v)
        return PH.sub(rep, x)
    if isinstance(x, list):
        return [fill(i, values) for i in x]
    if isinstance(x, dict):
        return {k: fill(v, values) for k, v in x.items()}
    return x


def e(s) -> str:
    return H.escape(str(s))


# ---------------------------------------------------------------- style
CSS = """
@page{size:1920px 1080px;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg0:#08101d;--bg1:#13213a;--ink:#f3f6fa;--en:#8fa3ba;--mut:#5f7189;--amber:#f2b705;--teal:#2ec4b6;--blue:#4c8dff;
  --orange:#ff7a45;--violet:#a78bfa;--card:#101b2e;--line:#22324d;--zh:'Noto Sans CJK SC','Noto Sans SC','Microsoft YaHei',sans-serif;
  --enf:'Inter','DejaVu Sans','Helvetica Neue',Arial,sans-serif}
html,body{width:1920px;height:1080px;background:var(--bg0);overflow:hidden}
.slide{position:relative;width:1920px;height:1080px;color:var(--ink);font-family:var(--zh);
  background:radial-gradient(1400px 900px at 12% -10%,#1b2d4d 0%,rgba(27,45,77,0) 60%),radial-gradient(900px 700px at 110% 120%,#132a3a 0%,rgba(19,42,58,0) 60%),linear-gradient(160deg,var(--bg1),var(--bg0) 70%);}
.grain{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.035) 1px,transparent 1px);background-size:6px 6px;pointer-events:none}
.head{position:absolute;left:110px;right:110px;top:72px}
.head .zh{font-size:64px;font-weight:700;letter-spacing:1px;line-height:1.18}
.head .en{font-family:var(--enf);font-size:30px;color:var(--en);margin-top:12px;font-weight:400}
.seam{height:4px;margin-top:22px;width:220px;background:repeating-linear-gradient(90deg,var(--amber) 0 22px,transparent 22px 36px);border-radius:2px}
.foot{position:absolute;left:110px;right:110px;bottom:38px;display:flex;justify-content:space-between;font-size:20px;color:var(--mut);font-family:var(--enf)}
.foot b{color:#8193ab;font-weight:500;font-family:var(--zh)}
.tag{display:inline-block;font-size:26px;font-weight:700;color:#0b1220;background:var(--amber);padding:6px 18px;border-radius:8px;margin-bottom:22px}
.tag .t-en{font-family:var(--enf);font-weight:600;margin-left:12px;opacity:.75;font-size:22px}
.body{position:absolute;left:110px;right:110px;top:300px;bottom:120px}
.pts{display:flex;flex-direction:column;gap:46px}
.pt{display:flex;gap:28px;align-items:flex-start}
.pt .dot{flex:none;width:18px;height:18px;margin-top:22px;border-radius:50%;background:var(--amber);box-shadow:0 0 0 6px rgba(242,183,5,.15)}
.pt .zh{font-size:46px;line-height:1.32;font-weight:500}
.pt .en{font-family:var(--enf);font-size:26px;line-height:1.35;color:var(--en);margin-top:8px}
.card{background:linear-gradient(180deg,#14223a,#0f1a2d);border:1px solid var(--line);border-radius:28px;box-shadow:0 30px 80px rgba(0,0,0,.45)}
.media{position:relative;border-radius:24px;overflow:hidden;background:#0d1626;border:1px solid var(--line);box-shadow:0 30px 80px rgba(0,0,0,.5)}
.media img{display:block;width:100%;height:100%;object-fit:contain}
.media.white{background:#f6f7f9}
.play{position:absolute;right:22px;bottom:20px;font-family:var(--enf);font-size:22px;color:#0b1220;background:var(--amber);padding:6px 14px;border-radius:999px;font-weight:700}
/* cover */
.cover .bgv{position:absolute;left:30%;top:0;right:0;bottom:0}
.cover .bgv img{width:100%;height:100%;object-fit:cover;filter:saturate(1.05)}
.cover .shade{position:absolute;inset:0;background:linear-gradient(90deg,#08101d 0%,#08101d 30%,rgba(8,16,29,.55) 42%,rgba(8,16,29,0) 58%)}
.cover .txt{position:absolute;left:120px;top:250px;width:980px}
.cover .kick{font-size:34px;color:var(--amber);font-weight:700;letter-spacing:4px}
.cover .kick span{font-family:var(--enf);font-weight:500;color:#c9a94a;margin-left:16px;letter-spacing:1px}
.cover h1{font-size:104px;line-height:1.1;margin-top:26px;font-weight:800}
.cover .h1en{font-family:var(--enf);font-size:40px;color:#b4c3d6;margin-top:22px}
.cover .sub{margin-top:54px;font-size:38px;color:#dbe4ef}
.cover .suben{font-family:var(--enf);font-size:26px;color:var(--en);margin-top:8px}
.cover .brand{position:absolute;left:120px;bottom:70px;font-size:26px;color:#9fb0c6}
.cover .brand b{color:var(--teal);font-weight:700;margin-right:14px}
/* section */
.section .no{position:absolute;left:110px;top:200px;font-family:var(--enf);font-size:300px;font-weight:800;line-height:1;
  background:linear-gradient(180deg,rgba(242,183,5,.95),rgba(242,183,5,.15));-webkit-background-clip:text;color:transparent}
.section .st{position:absolute;left:120px;top:560px;right:120px}
.section .st .zh{font-size:92px;font-weight:800;line-height:1.15}
.section .st .en{font-family:var(--enf);font-size:40px;color:var(--en);margin-top:18px}
.section .bar{position:absolute;left:120px;top:520px;width:300px;height:6px;background:repeating-linear-gradient(90deg,var(--amber) 0 30px,transparent 30px 48px)}
/* question */
.question .q{position:absolute;left:110px;top:150px;right:110px}
.question .q .zh{font-size:100px;font-weight:800;line-height:1.12}
.question .q .en{font-family:var(--enf);font-size:40px;color:var(--en);margin-top:20px}
.question .facts{position:absolute;left:110px;right:110px;top:560px;display:grid;grid-template-columns:repeat(3,1fr);gap:34px}
.question .fact{padding:34px 34px 30px}
.question .fact .zh{font-size:36px;line-height:1.36;font-weight:500}
.question .fact .en{font-family:var(--enf);font-size:22px;color:var(--en);margin-top:12px;line-height:1.35}
.question .fact .n{font-family:var(--enf);color:var(--amber);font-weight:800;font-size:28px;margin-bottom:14px}
/* split */
.split .body{display:grid;grid-template-columns:780px 1fr;gap:70px;top:300px}
.split .vis{position:relative}
/* duo */
.duo .body{display:grid;grid-template-columns:1fr 1fr;gap:56px;top:290px}
.duo .col .media{height:460px}
.duo .col .lab{margin-top:28px}
.duo .col .lab .zh{font-size:40px;font-weight:700}
.duo .col .lab .en{font-family:var(--enf);font-size:24px;color:var(--en);margin-top:6px}
.duo .col .note{margin-top:18px;display:inline-block;padding:10px 20px;border-radius:12px;font-size:28px;background:rgba(255,122,69,.12);color:#ffb38f}
.duo .col.ok .note{background:rgba(46,196,182,.12);color:#7fe3d8}
.duo .col .note span{font-family:var(--enf);font-size:20px;margin-left:12px;opacity:.85}
/* lab */
.lab .body{display:grid;grid-template-columns:1150px 1fr;gap:60px;top:280px}
.lab .media{height:650px}
.lab .tasks .h{font-size:30px;color:var(--amber);font-weight:700;margin-bottom:26px}
.lab .tasks .h span{font-family:var(--enf);font-weight:500;margin-left:10px;font-size:22px}
.lab .task{display:flex;gap:20px;margin-bottom:24px}
.lab .task .k{flex:none;width:52px;height:52px;border-radius:14px;background:rgba(242,183,5,.14);color:var(--amber);font-family:var(--enf);font-weight:800;font-size:28px;display:flex;align-items:center;justify-content:center}
.lab .task .zh{font-size:34px;line-height:1.35}
.lab .task .en{font-family:var(--enf);font-size:21px;color:var(--en);margin-top:6px}
.lab .go{margin-top:10px;white-space:nowrap;display:inline-flex;align-items:center;gap:16px;background:var(--amber);color:#0b1220;font-size:36px;font-weight:800;padding:20px 40px;border-radius:999px;box-shadow:0 14px 40px rgba(242,183,5,.35)}
.lab .go span{font-family:var(--enf);font-size:24px;font-weight:600;opacity:.8}
/* timeline */
.timeline .tl{position:absolute;left:110px;right:110px;top:330px;height:600px}
/* bignum */
.bignum .nums{position:absolute;left:110px;right:110px;top:330px;display:flex;gap:40px}
.bignum .num{flex:1;padding:46px 44px}
.bignum .num .n{white-space:nowrap;font-size:100px;font-weight:800;line-height:1;background:linear-gradient(180deg,#ffd75a,#f2b705);-webkit-background-clip:text;color:transparent}
.bignum .num .ne{font-family:var(--enf);font-size:28px;color:#c9a94a;margin-top:10px;height:34px}
.bignum .num .zh{font-size:36px;margin-top:28px;line-height:1.35}
.bignum .num .en{font-family:var(--enf);font-size:22px;color:var(--en);margin-top:8px}
.footnote{position:absolute;left:110px;right:110px;bottom:110px;padding:24px 34px;border-left:6px solid var(--teal);background:rgba(46,196,182,.07);border-radius:0 18px 18px 0}
.footnote .zh{font-size:32px;line-height:1.4}
.footnote .en{font-family:var(--enf);font-size:22px;color:var(--en);margin-top:6px}
/* stages */
.stages .chart{position:absolute;left:110px;right:110px;top:300px;height:520px}
/* formula */
.formula .eq{position:absolute;left:110px;top:300px;width:700px;font-family:'DejaVu Serif',serif;font-size:96px;font-style:italic;color:#fff}
.formula .eq .sub{display:block;font-family:var(--zh);font-style:normal;font-size:30px;color:var(--en);margin-top:24px;line-height:1.5}
.formula .chart{position:absolute;left:860px;right:110px;top:290px;height:560px}
/* tiles */
.tiles .grid{position:absolute;left:110px;right:110px;top:300px;display:grid;grid-template-columns:repeat(3,1fr);gap:30px}
.tiles .tile{padding:32px 36px;min-height:290px}
.tiles .tile.hot{border-color:var(--amber);box-shadow:0 0 0 2px var(--amber),0 30px 80px rgba(0,0,0,.45)}
.tiles .tile .k{font-family:var(--enf);font-size:70px;font-weight:800;color:var(--amber);line-height:1}
.tiles .tile .nm{font-size:40px;font-weight:700;margin-top:16px}
.tiles .tile .nm span{display:block;font-family:var(--enf);font-size:22px;font-weight:500;color:var(--en);margin-top:4px}
.tiles .tile .use{font-size:28px;color:#c7d3e2;margin-top:18px;line-height:1.4}
.tiles .tile .use span{display:block;font-family:var(--enf);font-size:20px;color:var(--en);margin-top:2px}
.tiles4 .grid{position:absolute;left:110px;right:110px;top:300px;display:grid;grid-template-columns:repeat(4,1fr);gap:30px}
.tiles4 .tile{padding:20px 22px 30px}
.tiles4 .tile svg{display:block;width:100%;height:330px;background:#f4efe3;border-radius:18px}
.tiles4 .tile .zh{font-size:32px;font-weight:700;margin-top:22px;line-height:1.35}
.tiles4 .tile .en{font-family:var(--enf);font-size:20px;color:var(--en);margin-top:6px;line-height:1.35}
/* chain */
.chain .flow{position:absolute;left:70px;right:70px;top:400px;display:flex;align-items:center;gap:4px}
.chain .step{flex:1;height:190px;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:22px;background:#111d31;border:1px solid var(--line);text-align:center;padding:0 8px}
.chain .step .zh{font-size:32px;font-weight:700;white-space:nowrap}
.chain .step .en{font-family:var(--enf);font-size:18px;color:var(--en);margin-top:8px}
.chain .step.hot{background:linear-gradient(180deg,#f2b705,#d99b00);border:none;transform:scale(1.12);box-shadow:0 20px 60px rgba(242,183,5,.35);color:#0b1220}
.chain .step.hot .en{color:#3d2f00}
.chain .arr{flex:none;color:#f2b705;font-size:44px;font-weight:700;opacity:.7}
.chain .brace{position:absolute;top:640px;font-size:30px;color:var(--amber);text-align:center;font-weight:700}
/* answer */
.answer .rows{position:absolute;left:110px;top:330px;width:1100px}
.answer .row{display:flex;justify-content:space-between;align-items:baseline;padding:26px 10px;border-bottom:1px solid var(--line)}
.answer .row .a{font-size:46px}
.answer .row .b{font-family:var(--enf);font-size:64px;font-weight:800}
.answer .row:last-child .b{color:var(--amber)}
.answer .side{position:absolute;left:1300px;right:110px;top:330px;padding:44px}
.answer .side .big{font-family:var(--enf);font-size:150px;font-weight:800;color:var(--orange);line-height:1}
.answer .side .zh{font-size:36px;margin-top:24px;line-height:1.4}
.answer .side .en{font-family:var(--enf);font-size:22px;color:var(--en);margin-top:8px}
/* roadmap */
.roadmap .road{position:absolute;left:110px;right:110px;top:320px;height:600px}
/* summary */
.summary .pts{position:absolute;left:110px;right:110px;top:300px;gap:40px}
.summary .pt .k{flex:none;width:76px;height:76px;border-radius:20px;background:var(--amber);color:#0b1220;font-family:var(--enf);font-weight:800;font-size:40px;display:flex;align-items:center;justify-content:center}
.summary .after{position:absolute;left:110px;right:110px;bottom:110px;padding:28px 36px;border-radius:22px;background:rgba(46,196,182,.1);border:1px solid rgba(46,196,182,.4)}
.summary .after .zh{font-size:32px;color:#bff3ec}
.summary .after .en{font-family:var(--enf);font-size:21px;color:var(--en);margin-top:6px}
.svgbox svg{width:100%;height:100%}
.points .body{top:290px}
.figure .fbody{position:absolute;left:110px;right:110px;top:270px;display:flex;justify-content:center}
.figure .fbody>div{width:100%}
.figure .cap{position:absolute;left:110px;right:110px;bottom:100px;text-align:center}
.figure .cap .zh{font-size:32px;color:#dbe4ef}.figure .cap .en{font-family:var(--enf);font-size:22px;color:var(--en);margin-left:16px}
svg text{font-family:var(--zh)}
svg .en{font-family:var(--enf)}
"""


# ---------------------------------------------------------------- custom visuals (inline SVG, drawn for the slide size)
def vis_needle_idea() -> str:
    return """<svg viewBox="0 0 900 640" width="100%" height="640">
  <defs><linearGradient id="cl" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#e9dcc0"/><stop offset="1" stop-color="#cdbb95"/></linearGradient></defs>
  <rect x="0" y="300" width="900" height="70" rx="6" fill="url(#cl)"/>
  <text x="20" y="290" font-size="26" fill="#8fa3ba">布 · cloth</text>
  <!-- hand needle -->
  <g transform="translate(170,0)">
    <text x="0" y="60" font-size="34" font-weight="700" fill="#ff9c75" text-anchor="middle">手缝针</text>
    <text x="0" y="94" font-size="22" fill="#8fa3ba" text-anchor="middle" class="en">hand needle</text>
    <rect x="-7" y="130" width="14" height="380" rx="7" fill="#c8d2de"/>
    <polygon points="-7,510 7,510 0,560" fill="#c8d2de"/>
    <ellipse cx="0" cy="150" rx="4" ry="12" fill="#08101d"/>
    <path d="M0 150 C 40 140, 70 110, 90 70" stroke="#ff7a45" stroke-width="5" fill="none"/>
    <text x="22" y="190" font-size="24" fill="#ff9c75">针眼在尾部</text>
    <path d="M -60 450 L -60 600" stroke="#ff7a45" stroke-width="4" stroke-dasharray="10 8" marker-end="url(#a1)"/>
    <text x="-70" y="630" font-size="24" fill="#ff9c75" text-anchor="middle">整根穿过</text>
  </g>
  <!-- machine needle -->
  <g transform="translate(600,0)">
    <text x="0" y="60" font-size="34" font-weight="700" fill="#5ee0d2" text-anchor="middle">机针</text>
    <text x="0" y="94" font-size="22" fill="#8fa3ba" text-anchor="middle" class="en">machine needle</text>
    <rect x="-9" y="110" width="18" height="300" rx="5" fill="#c8d2de"/>
    <polygon points="-9,410 9,410 0,452" fill="#c8d2de"/>
    <ellipse cx="0" cy="425" rx="4" ry="10" fill="#08101d"/>
    <path d="M -2 112 L -2 425" stroke="#4c8dff" stroke-width="4"/>
    <path d="M 2 425 C 30 440, 60 470, 70 480 C 90 500, 60 530, 30 520 C 10 512, 4 470, 3 430" stroke="#4c8dff" stroke-width="5" fill="none"/>
    <text x="90" y="430" font-size="24" fill="#5ee0d2">针眼在针尖</text>
    <text x="100" y="525" font-size="24" fill="#8fd0ff">布底留下线环</text>
    <text x="100" y="556" font-size="20" fill="#8fa3ba" class="en">a loop is left below</text>
  </g>
  <defs><marker id="a1" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#ff7a45"/></marker></defs>
</svg>"""


def vis_feed_box() -> str:
    return """<svg viewBox="0 0 900 640" width="100%" height="640">
  <rect x="40" y="380" width="820" height="40" rx="6" fill="#2a3a55"/>
  <text x="50" y="455" font-size="24" fill="#8fa3ba">针板 · throat plate</text>
  <rect x="170" y="160" width="560" height="200" rx="10" fill="none" stroke="#f2b705" stroke-width="5" stroke-dasharray="18 12"/>
  <g font-size="40" font-weight="800" fill="#f2b705">
    <text x="120" y="275" text-anchor="end">① 升</text><text x="450" y="135" text-anchor="middle">② 进 →</text>
    <text x="760" y="275">③ 降</text><text x="450" y="405" text-anchor="middle" fill="#ffd27a">④ 退 ←</text></g>
  <g font-size="22" fill="#c9a94a" class="en"><text x="120" y="305" text-anchor="end" class="en">up</text><text x="560" y="135" class="en">forward</text>
    <text x="760" y="305" class="en">down</text><text x="450" y="440" text-anchor="middle" class="en">back</text></g>
  <g transform="translate(250,170)"><rect width="200" height="40" rx="6" fill="#ff7a45"/>
    <path d="M0 0 l20 -26 l20 26 l20 -26 l20 26 l20 -26 l20 26 l20 -26 l20 26 l20 -26 l20 26" fill="#ff7a45"/></g>
  <text x="460" y="252" font-size="26" fill="#ffb38f">送布牙 · feed dog</text>
  <circle cx="450" cy="560" r="62" fill="none" stroke="#2ec4b6" stroke-width="6"/>
  <path d="M450 498 A62 62 0 0 1 512 560" stroke="#5ee0d2" stroke-width="12" fill="none" stroke-linecap="round"/>
  <text x="540" y="572" font-size="26" fill="#5ee0d2">旋转钩：连续转，不换向</text>
</svg>"""


def vis_encoder_flow() -> str:
    box = lambda x, y, zh, en, c: (f'<g transform="translate({x},{y})"><rect width="380" height="130" rx="22" fill="#111d31" stroke="{c}" stroke-width="3"/>'
                                   f'<text x="190" y="62" font-size="38" font-weight="700" fill="#f3f6fa" text-anchor="middle">{zh}</text>'
                                   f'<text x="190" y="100" font-size="22" fill="#8fa3ba" text-anchor="middle" class="en">{en}</text></g>')
    arr = lambda x1, y1, x2, y2: f'<path d="M{x1} {y1} L{x2} {y2}" stroke="#4b5f7d" stroke-width="6" marker-end="url(#ar)"/>'
    return ('<svg viewBox="0 0 900 640" width="100%" height="640"><defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="#4b5f7d"/></marker></defs>'
            + box(40, 40, "主轴编码器", "shaft encoder", "#2ec4b6") + arr(420, 105, 490, 105)
            + box(500, 40, "读出角度 φ", "angle φ", "#2ec4b6") + arr(690, 170, 690, 250)
            + box(500, 260, "软件按角度", "commands by angle", "#f2b705") + arr(500, 325, 430, 325)
            + box(40, 260, "伺服·电磁铁·气缸", "servo · solenoid · air", "#ff7a45") + arr(230, 390, 230, 470)
            + '<g transform="translate(40,480)"><rect width="840" height="120" rx="22" fill="rgba(255,122,69,.12)"/>'
              '<text x="420" y="58" font-size="36" font-weight="700" fill="#ffb38f" text-anchor="middle">剪线 · 倒缝 · 抬压脚 · 停针定位</text>'
              '<text x="420" y="96" font-size="22" fill="#8fa3ba" text-anchor="middle" class="en">trim · reverse · foot lift · needle positioning</text></g></svg>')


def vis_square_law() -> str:
    pts = " ".join(f"{80 + x * 7.4:.0f},{560 - (x / 100) ** 2 * 460:.0f}" for x in range(0, 101, 4))
    return f"""<svg viewBox="0 0 900 640" width="100%" height="640">
  <path d="M80 560 L860 560 M80 560 L80 60" stroke="#4b5f7d" stroke-width="3"/>
  <polyline points="{pts}" fill="none" stroke="#f2b705" stroke-width="7" stroke-linecap="round"/>
  <path d="M450 560 L450 445 M80 445 L450 445" stroke="#2ec4b6" stroke-width="3" stroke-dasharray="8 8"/>
  <path d="M820 560 L820 100 M80 100 L820 100" stroke="#ff7a45" stroke-width="3" stroke-dasharray="8 8"/>
  <circle cx="450" cy="445" r="12" fill="#2ec4b6"/><circle cx="820" cy="100" r="14" fill="#ff7a45"/>
  <text x="470" y="430" font-size="32" fill="#5ee0d2" font-weight="700">1×</text>
  <text x="760" y="85" font-size="40" fill="#ff9c75" font-weight="800">4×</text>
  <text x="450" y="605" font-size="26" fill="#8fa3ba" text-anchor="middle">速度 v</text>
  <text x="820" y="605" font-size="26" fill="#8fa3ba" text-anchor="middle">2v</text>
  <text x="70" y="50" font-size="26" fill="#8fa3ba">惯性力 F ∝ v²</text>
</svg>"""


def stitch_svg(kind: str) -> str:
    top, bot = [], []
    if kind == "lock":
        for i in range(5):
            x = 30 + i * 70
            top.append(f'<path d="M{x} 110 L{x + 52} 110" stroke="#2c6fd6" stroke-width="9" stroke-linecap="round"/>')
            bot.append(f'<path d="M{x} 240 L{x + 52} 240" stroke="#e0662f" stroke-width="9" stroke-linecap="round"/>')
    elif kind == "chain":
        for i in range(5):
            x = 30 + i * 70
            top.append(f'<path d="M{x} 110 L{x + 52} 110" stroke="#2c6fd6" stroke-width="9" stroke-linecap="round"/>')
            bot.append(f'<ellipse cx="{x + 40}" cy="240" rx="36" ry="17" fill="none" stroke="#2c6fd6" stroke-width="8"/>')
    elif kind == "overedge":
        top.append('<rect x="0" y="80" width="300" height="190" fill="#e6dcc6"/>')
        for i in range(8):
            x = 20 + i * 38
            top.append(f'<path d="M{x} 120 C {x + 40} 60, {x + 60} 60, {x + 30} 250" stroke="#2c6fd6" stroke-width="6" fill="none"/>')
            top.append(f'<path d="M{x + 10} 250 L{x + 40} 120" stroke="#e0662f" stroke-width="5"/>')
    elif kind == "cover":
        for row, y in enumerate((95, 125)):
            top.append(f'<path d="M20 {y} L380 {y}" stroke="#2c6fd6" stroke-width="7" stroke-dasharray="40 14"/>')
        for i in range(9):
            x = 20 + i * 40
            bot.append(f'<path d="M{x} 225 L{x + 20} 255 L{x + 40} 225" stroke="#e0662f" stroke-width="6" fill="none"/>')
        bot.append('<path d="M20 225 L380 225 M20 255 L380 255" stroke="#2c6fd6" stroke-width="5"/>')
    lab = ('<text x="12" y="60" font-size="22" fill="#6b5a3a">正面 face</text><text x="12" y="200" font-size="22" fill="#6b5a3a">反面 back</text>'
           '<path d="M0 170 L400 170" stroke="#d6c7a6" stroke-width="2"/>')
    return f'<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid meet">{lab}{"".join(top)}{"".join(bot)}</svg>'


CUSTOM = {"needle_idea": vis_needle_idea, "feed_box": vis_feed_box, "encoder_flow": vis_encoder_flow, "square_law": vis_square_law}


# ---------------------------------------------------------------- layouts
def foot(no, page, total):
    return (f'<div class="foot"><div><b>{COURSE_NAME[0]}</b> · {COURSE_NAME[1]} · 第 {no} 讲 Lecture {no}</div>'
            f'<div>问渠 WenQuest · {page}/{total}</div></div>')


def head(title, tag=None):
    t = f'<div class="tag">{e(tag[0])}<span class="t-en">{e(tag[1])}</span></div>' if tag else ""
    return f'<div class="head">{t}<div class="zh">{e(title[0])}</div><div class="en">{e(title[1])}</div><div class="seam"></div></div>'


def points(pts, numbered=False):
    out = []
    for k, p in enumerate(pts):
        mark = f'<div class="k">{k + 1}</div>' if numbered else '<div class="dot"></div>'
        out.append(f'<div class="pt">{mark}<div><div class="zh">{e(p[0])}</div><div class="en">{e(p[1])}</div></div></div>')
    return f'<div class="pts">{"".join(out)}</div>'


def media(src: dict, ctx, h=640, white=False) -> str:
    if "video" in src:          # 活的：页面上直接运行动画或三维样机（只显示其中一块，照样能操作）
        return f'<div class="media live" data-live="{src["video"]}" style="height:{h}px"></div>'
    if "html" in src:
        return f'<div style="height:{h}px">{CUSTOM[src["html"]]()}</div>'
    if "fig" in src:            # 教材插图 img/<名>.webp（英文版 img/en/），内联进课件
        return f'<div class="media white" style="height:{h}px"><img src="{fig_uri(src["fig"])}"></div>'
    if "svg" in src:            # 为幻灯片新画的图（SVG 原文写在 yaml 里）
        return f'<div class="svgbox" style="height:{h}px">{src["svg"]}</div>'
    if "img" in src:
        return f'<div class="media{" white" if white else ""}" style="height:{h}px"><img src="{src["img"]}"></div>'
    return ""


def fig_uri(name: str) -> str:
    stem = Path(name).stem
    f = BOOK / "img" / f"{stem}.webp"
    if not f.exists():
        raise SystemExit(f"no figure img/{stem}.webp")
    return "data:image/webp;base64," + base64.b64encode(f.read_bytes()).decode("ascii")


def L_cover(s, ctx):
    return (f'<div class="slide cover"><div class="bgv live" data-live="{s["video"]}"></div><div class="shade"></div>'
            f'<div class="txt"><div class="kick">{e(s["kicker"][0])}<span>{e(s["kicker"][1])}</span></div><h1>{e(s["title"][0])}</h1>'
            f'<div class="h1en">{e(s["title"][1])}</div><div class="sub">{e(s["sub"][0])}</div><div class="suben">{e(s["sub"][1])}</div></div>'
            f'<div class="brand"><b>问渠 WenQuest</b>{COURSE_NAME[0]} · {COURSE_NAME[1]}</div></div>')


def L_section(s, ctx):
    return (f'<div class="slide section"><div class="grain"></div><div class="no">{e(s["num"])}</div><div class="bar"></div>'
            f'<div class="st"><div class="zh">{e(s["title"][0])}</div><div class="en">{e(s["title"][1])}</div></div>{ctx["foot"]}</div>')


def L_question(s, ctx):
    facts = "".join(f'<div class="fact card"><div class="n">0{k + 1}</div><div class="zh">{e(f[0])}</div><div class="en">{e(f[1])}</div></div>'
                    for k, f in enumerate(s["facts"]))
    return (f'<div class="slide question"><div class="grain"></div><div class="q"><div class="tag">{e(s["tag"][0])}<span class="t-en">{e(s["tag"][1])}</span></div>'
            f'<div class="zh">{e(s["title"][0])}</div><div class="en">{e(s["title"][1])}</div></div><div class="facts">{facts}</div>{ctx["foot"]}</div>')


def L_split(s, ctx):
    return (f'<div class="slide split"><div class="grain"></div>{head(s["title"])}<div class="body">{points(s["points"])}'
            f'<div class="vis">{media(s["visual"], ctx, 640)}</div></div>{ctx["foot"]}</div>')


def L_duo(s, ctx):
    def col(c, ok):
        return (f'<div class="col{" ok" if ok else ""}">{media(c, ctx, 460)}<div class="lab"><div class="zh">{e(c["label"][0])}</div>'
                f'<div class="en">{e(c["label"][1])}</div></div><div class="note">{e(c["note"][0])}<span>{e(c["note"][1])}</span></div></div>')
    return f'<div class="slide duo"><div class="grain"></div>{head(s["title"])}<div class="body">{col(s["left"], False)}{col(s["right"], True)}</div>{ctx["foot"]}</div>'


def L_lab(s, ctx):
    tasks = "".join(f'<div class="task"><div class="k">{k + 1}</div><div><div class="zh">{e(t[0])}</div><div class="en">{e(t[1])}</div></div></div>'
                    for k, t in enumerate(s["tasks"]))
    return (f'<div class="slide lab"><div class="grain"></div>{head(s["title"])}<div class="body"><div class="media white live" data-live="lab:{s["shot"]["page"]}" style="height:650px"></div>'
            f'<div class="tasks"><div class="h">任务<span>Tasks</span></div>{tasks}<div class="go" data-act="fulllab" data-page="lab:{s["shot"]["page"]}">全屏做实验 ▶<span>Full-screen lab</span></div></div></div>{ctx["foot"]}</div>')


def L_timeline(s, ctx):
    ev = s["events"]
    y0, y1 = min(x["year"] for x in ev), max(x["year"] for x in ev)
    X = lambda y: 170 + [v["year"] for v in ev].index(y) * (1360 / max(1, len(ev) - 1))     # 等距排开（不按比例），字不会挤在一起
    g = ['<path d="M20 300 L1680 300" stroke="#2c3e5c" stroke-width="6" stroke-linecap="round"/>']
    for k, v in enumerate(ev):
        x, up = X(v["year"]), k % 2 == 0
        y = 70 if up else 400
        g.append('<g class="frag">')
        g.append(f'<path d="M{x:.0f} 300 L{x:.0f} {(y + 150) if up else y}" stroke="#4b5f7d" stroke-width="3" stroke-dasharray="6 6"/>')
        g.append(f'<circle cx="{x:.0f}" cy="300" r="20" fill="#f2b705"/><circle cx="{x:.0f}" cy="300" r="34" fill="none" stroke="rgba(242,183,5,.35)" stroke-width="6"/>')
        g.append(f'<text x="{x:.0f}" y="{y + 10}" font-size="54" font-weight="800" fill="#f2b705" text-anchor="middle" class="en">{v["year"]}</text>')
        g.append(f'<text x="{x:.0f}" y="{y + 62}" font-size="38" font-weight="700" fill="#f3f6fa" text-anchor="middle">{e(v["who"][0])} <tspan class="en" font-size="24" fill="#8fa3ba">{e(v["who"][1])}</tspan></text>')
        g.append(f'<text x="{x:.0f}" y="{y + 108}" font-size="30" fill="#d3deea" text-anchor="middle">{e(v["what"][0])}</text>')
        g.append(f'<text x="{x:.0f}" y="{y + 140}" font-size="21" fill="#8fa3ba" text-anchor="middle" class="en">{e(v["what"][1])}</text></g>')
    return (f'<div class="slide timeline"><div class="grain"></div>{head(s["title"])}<div class="tl"><svg viewBox="0 0 1700 600" width="1700" height="600">{"".join(g)}</svg></div>{ctx["foot"]}</div>')


def L_bignum(s, ctx):
    nums = "".join(f'<div class="num card"><div class="n">{e(n["n"])}</div><div class="ne">{e(n.get("n_en", ""))}</div><div class="zh">{e(n["label"][0])}</div><div class="en">{e(n["label"][1])}</div></div>'
                   for n in s["nums"])
    fn = f'<div class="footnote"><div class="zh">{e(s["foot"][0])}</div><div class="en">{e(s["foot"][1])}</div></div>' if s.get("foot") else ""
    return f'<div class="slide bignum"><div class="grain"></div>{head(s["title"])}<div class="nums">{nums}</div>{fn}{ctx["foot"]}</div>'


def L_stages(s, ctx):
    st = s["stages"]
    y0, y1 = 1840, 2040
    X = lambda y: 260 + (y - y0) / (y1 - y0) * 1400
    cols = ["#7aa5f0", "#4c8dff", "#2ec4b6", "#ff7a45", "#a78bfa"]
    g = []
    for yr in range(1850, 2041, 30):
        g.append(f'<path d="M{X(yr):.0f} 0 L{X(yr):.0f} 470" stroke="#1e2c45" stroke-width="2"/><text x="{X(yr):.0f}" y="505" font-size="24" fill="#5f7189" text-anchor="middle" class="en">{yr}</text>')
    for k, v in enumerate(st):
        y = 10 + k * 92
        g.append(f'<text x="0" y="{y + 50}" font-size="40" font-weight="800" fill="{cols[k]}">{k + 1} {e(v["name"][0])}</text>')
        g.append(f'<rect x="{X(v["from"]):.0f}" y="{y + 8}" width="{X(v["to"]) - X(v["from"]):.0f}" height="58" rx="14" fill="{cols[k]}" opacity=".9"/>')
        wide = X(v["to"]) - X(v["from"]) > 300
        g.append(f'<text x="{X(v["from"]) + 20:.0f}" y="{y + 47}" font-size="27" font-weight="700" fill="#08101d">{e(v["note"][0])}</text>' if wide else
                 f'<text x="{X(v["from"]) - 18:.0f}" y="{y + 47}" font-size="27" font-weight="700" fill="{cols[k]}" text-anchor="end">{e(v["note"][0])}</text>')
    fn = f'<div class="footnote"><div class="zh">{e(s["foot"][0])}</div><div class="en">{e(s["foot"][1])}</div></div>'
    return f'<div class="slide stages"><div class="grain"></div>{head(s["title"])}<div class="chart"><svg viewBox="0 0 1700 520" width="1700" height="520">{"".join(g)}</svg></div>{fn}{ctx["foot"]}</div>'


def L_formula(s, ctx):
    bars = s["bars"]
    fmax = max(float(b["F"]) for b in bars)
    g = []
    for k, b in enumerate(bars):
        x = 40 + k * 230
        hgt = max(6, float(b["F"]) / fmax * 380)
        col = "#ff7a45" if k == len(bars) - 1 else ("#4b5f7d" if k == 0 else "#f2b705")
        g.append(f'<rect x="{x}" y="{430 - hgt:.0f}" width="150" height="{hgt:.0f}" rx="12" fill="{col}"/>')
        g.append(f'<text x="{x + 75}" y="{410 - hgt:.0f}" font-size="44" font-weight="800" fill="#f3f6fa" text-anchor="middle" class="en">{e(b["F"])} N</text>')
        g.append(f'<text x="{x + 75}" y="480" font-size="26" fill="#d3deea" text-anchor="middle">{e(b["label"][0])}</text>')
    return (f'<div class="slide formula"><div class="grain"></div>{head(s["title"])}<div class="eq">{s["formula_html"]}'
            f'<span class="sub">针杆下止点惯性力<br><span style="font-family:var(--enf);font-size:22px">needle-bar inertia force at BDC</span></span></div>'
            f'<div class="chart"><svg viewBox="0 0 950 520" width="950" height="520">{"".join(g)}</svg></div>'
            f'<div class="footnote"><div class="zh">{e(s["foot"][0])}</div><div class="en">{e(s["foot"][1])}</div></div>{ctx["foot"]}</div>')


def L_tiles(s, ctx):
    t = "".join(f'<div class="tile card{" hot" if x.get("hot") else ""}"><div class="k">{e(x["k"])}</div><div class="nm">{e(x["name"][0])}<span>{e(x["name"][1])}</span></div>'
                f'<div class="use">{e(x["use"][0])}<span>{e(x["use"][1])}</span></div></div>' for x in s["tiles"])
    return f'<div class="slide tiles"><div class="grain"></div>{head(s["title"])}<div class="grid">{t}</div>{ctx["foot"]}</div>'


def L_tiles4(s, ctx):
    t = "".join(f'<div class="tile card">{stitch_svg(x["draw"])}<div class="zh">{e(x["name"][0])}</div><div class="en">{e(x["name"][1])}</div></div>' for x in s["tiles"])
    return f'<div class="slide tiles4"><div class="grain"></div>{head(s["title"])}<div class="grid">{t}</div>{ctx["foot"]}</div>'


def L_chain(s, ctx):
    hot = set(s.get("hot", []))
    parts = []
    for k, st in enumerate(s["steps"]):
        if k:
            parts.append('<div class="arr">›</div>')
        parts.append(f'<div class="step{" hot" if k in hot else ""}"><div class="zh">{e(st[0])}</div><div class="en">{e(st[1])}</div></div>')
    fn = f'<div class="footnote"><div class="zh">{e(s["foot"][0])}</div><div class="en">{e(s["foot"][1])}</div></div>'
    return (f'<div class="slide chain"><div class="grain"></div>{head(s["title"])}<div class="flow">{"".join(parts)}</div>'
            + (f'<div class="brace" style="left:{70 + 1780 * min(hot) / len(s["steps"]):.0f}px;width:{1780 * len(hot) / len(s["steps"]):.0f}px">▲ {e(s.get("mark", ["本课程", "this course"])[0])} · {e(s.get("mark", ["本课程", "this course"])[1])}</div>' if hot else "")
            + f'{fn}{ctx["foot"]}</div>')


def L_answer(s, ctx):
    rows = "".join(f'<div class="row"><div class="a">{e(r[0])}</div><div class="b">{e(r[1])}</div></div>' for r in s["rows"])
    return (f'<div class="slide answer"><div class="grain"></div>{head(s["title"], s.get("tag"))}<div class="rows">{rows}</div>'
            + (f'<div class="side card"><div class="big">{e(s["side"]["big"])}</div><div class="zh">{e(s["side"]["text"][0])}</div>'
               f'<div class="en">{e(s["side"]["text"][1])}</div></div>' if s.get("side") else "") +
            f'<div class="footnote"><div class="zh">{e(s["foot"][0])}</div><div class="en">{e(s["foot"][1])}</div></div>{ctx["foot"]}</div>')


def L_roadmap(s, ctx):
    p = s["parts"]
    cols = ["#7aa5f0", "#4c8dff", "#4c8dff", "#2ec4b6", "#2ec4b6", "#ff7a45", "#ff7a45", "#a78bfa"]
    pos = [(110 + k * 211, 400 if k % 2 == 0 else 220) for k in range(len(p))]
    path = "M" + " L".join(f"{x} {y}" for x, y in pos)
    g = [f'<path d="{path}" stroke="#22324d" stroke-width="34" fill="none" stroke-linejoin="round" stroke-linecap="round"/>',
         f'<path d="{path}" stroke="#f2b705" stroke-width="5" fill="none" stroke-dasharray="24 16" stroke-linejoin="round"/>']
    for k, (x, y) in enumerate(pos):
        g.append(f'<g class="frag"><circle cx="{x}" cy="{y}" r="34" fill="{cols[k]}"/><text x="{x}" y="{y + 12}" font-size="32" font-weight="800" fill="#08101d" text-anchor="middle" class="en">{k + 1}</text>')
        ty = y + 100 if k % 2 == 0 else y - 85
        g.append(f'<text x="{x}" y="{ty}" font-size="34" font-weight="700" fill="#f3f6fa" text-anchor="middle">{e(p[k][0])}</text>')
        g.append(f'<text x="{x}" y="{ty + 34}" font-size="20" fill="#8fa3ba" text-anchor="middle" class="en">{e(p[k][1])}</text></g>')
    return f'<div class="slide roadmap"><div class="grain"></div>{head(s["title"])}<div class="road"><svg viewBox="0 0 1700 600" width="1700" height="600">{"".join(g)}</svg></div>{ctx["foot"]}</div>'


def L_points(s, ctx):
    fn = f'<div class="footnote"><div class="zh">{e(s["foot"][0])}</div><div class="en">{e(s["foot"][1])}</div></div>' if s.get("foot") else ""
    return f'<div class="slide points"><div class="grain"></div>{head(s["title"], s.get("tag"))}<div class="body">{points(s["points"])}</div>{fn}{ctx["foot"]}</div>'


def L_figure(s, ctx):
    cap = f'<div class="cap"><span class="zh">{e(s["caption"][0])}</span><span class="en">{e(s["caption"][1])}</span></div>' if s.get("caption") else ""
    return (f'<div class="slide figure"><div class="grain"></div>{head(s["title"])}<div class="fbody">{media(s["visual"], ctx, s.get("h", 640))}</div>'
            f'{cap}{ctx["foot"]}</div>')


def L_summary(s, ctx):
    return (f'<div class="slide summary"><div class="grain"></div>{head(s["title"])}{points(s["points"], numbered=True)}'
            f'<div class="after"><div class="zh">{e(s["after"][0])}</div><div class="en">{e(s["after"][1])}</div></div>{ctx["foot"]}</div>')


LAYOUTS = {k[2:]: v for k, v in globals().items() if k.startswith("L_")}


def formula_html(tex: str) -> str:
    """The few formulas the slides need, as HTML (F = m a ∝ n²)."""
    s = tex.replace("\\,", " ").replace("\\;", " ").replace("\\propto", "∝").replace("^{2}", "²")
    return e(s).replace("∝", '<span style="color:#f2b705;font-style:normal"> ∝ </span>')


# ---------------------------------------------------------------- the deck: one HTML file, pages like PPT, live labs inside
DECK_CSS = """
html,body{margin:0;height:100%;background:#000;overflow:hidden}
#stage{position:fixed;left:50%;top:50%;width:1920px;height:1080px;transform-origin:50% 50%}
#stage>.slide{position:absolute;inset:0;display:none}
#stage>.slide.on{display:block}
.live{overflow:hidden}
.live iframe{position:absolute;left:0;top:0;border:0;transform-origin:0 0;background:#fff}
.cover .bgv.live iframe{background:#0b1220}
.cover .shade{pointer-events:none}
.frag{opacity:0;transform:translateY(18px);transition:opacity .45s ease,transform .45s ease}
.frag.on{opacity:1;transform:none}
svg .frag{transform:none}
body.all .frag{opacity:1!important;transform:none!important;transition:none}
#bar{position:fixed;left:0;bottom:0;height:4px;background:#f2b705;transition:width .3s;z-index:5}
#nav{position:fixed;right:18px;bottom:14px;display:flex;gap:8px;z-index:6;opacity:0;transition:opacity .3s;font:14px system-ui,sans-serif}
body:hover #nav{opacity:.9}
#nav button{background:rgba(20,30,48,.85);color:#dfe7f1;border:1px solid #2a3b57;border-radius:8px;padding:6px 10px;cursor:pointer;font:inherit}
#nav span{color:#9fb0c6;align-self:center;min-width:56px;text-align:center}
#fl{position:fixed;inset:0;z-index:20;background:#fff;display:none}
#fl iframe{width:100%;height:100%;border:0}
#fl button{position:fixed;right:16px;top:12px;z-index:21;font:16px system-ui;padding:8px 14px;border-radius:8px;border:0;background:#0b1220;color:#fff;cursor:pointer}
body.all #nav,body.all #bar{display:none}
"""

DECK_JS = r"""
(function(){
const D=JSON.parse(document.getElementById('deck-data').textContent);
if(new URLSearchParams(location.search).has('presenter')){addEventListener('load',()=>{document.open();document.write(D.presenter);document.close();});return;}
const stage=document.getElementById('stage'),slides=[...stage.children];
const pages={};document.querySelectorAll('script[data-page]').forEach(s=>pages[s.dataset.page]=s.textContent);
const dec=b64=>new TextDecoder().decode(Uint8Array.from(atob(b64),c=>c.charCodeAt(0)));
const qs=new URLSearchParams(location.search);if(qs.has('all'))document.body.classList.add('all');
let cur=0,frag=0;
function fit(){const s=Math.min(innerWidth/1920,innerHeight/1080);stage.style.transform=`translate(-50%,-50%) scale(${s})`;}
addEventListener('resize',fit);fit();
// live frames: the real lab or animation page, zoomed to the part the slide shows; still fully interactive
// 活的页面：在课件里的框中运行实验或动画页。框里的页面和课件之间只靠消息说话（平台把课件放在沙箱里，不能直接伸手进框）
const frames=new Map();
function mount(el){if(el.querySelector('iframe'))return;const id=el.dataset.live,c=D.clips[id]||{};
  const f=document.createElement('iframe');const vw=c.vw||1600,vh=c.vh||900;f.width=vw;f.height=vh;f.setAttribute('allow','fullscreen');
  f.srcdoc=dec(pages[c.page]);el.appendChild(f);frames.set(f,{el,c,vw,vh});
  f.addEventListener('load',()=>{const ask=()=>{try{f.contentWindow.postMessage({wqlive:1,steps:c.steps||[],selector:c.selector||''},'*')}catch(e){}};
    ask();for(let t=400;t<=4000;t+=400)setTimeout(()=>{try{f.contentWindow.postMessage({wqlive:2,selector:c.selector||''},'*')}catch(e){}},t);
    new ResizeObserver(()=>{try{f.contentWindow.postMessage({wqlive:2,selector:c.selector||''},'*')}catch(e){}}).observe(el);});}
addEventListener('message',m=>{const d=m.data;if(!d||!d.wqrect)return;
  for(const [f,o] of frames){if(f.contentWindow!==m.source)continue;const {el,c,vw,vh}=o;const cw=el.clientWidth;
    const r=d.wqrect[2]>0?{x:d.wqrect[0],y:d.wqrect[1],w:d.wqrect[2],h:d.wqrect[3]}:{x:0,y:0,w:vw,h:vh};
    if(!el.dataset.h0)el.dataset.h0=el.clientHeight;const H0=+el.dataset.h0;
    const s=c.cover?Math.max(cw/r.w,H0/r.h):Math.min(cw/r.w,H0/r.h);
    if(c.selector&&!c.cover){const h=Math.round(r.h*s);el.style.height=h+'px';el.style.marginTop=Math.round((H0-h)/2)+'px';}
    const ch2=el.clientHeight;f.style.transform=`translate(${(cw-r.w*s)/2-r.x*s}px,${(ch2-r.h*s)/2-r.y*s}px) scale(${s})`;}});
function unmount(el){const f=el.querySelector('iframe');if(f){frames.delete(f);f.remove();}}
function frags(i){return [...slides[i].querySelectorAll('.frag')];}
function show(i,f,send){i=Math.max(0,Math.min(slides.length-1,i));
  slides.forEach((s,k)=>{s.classList.toggle('on',k===i);if(Math.abs(k-i)>1||D.heavy.includes(k)&&k!==i)s.querySelectorAll('.live').forEach(unmount);});
  slides[i].querySelectorAll('.live').forEach(mount);
  const fs=frags(i);frag=f==null?0:(f<0?fs.length:Math.min(f,fs.length));fs.forEach((x,k)=>x.classList.toggle('on',k<frag));
  cur=i;document.getElementById('bar').style.width=((i+1)/slides.length*100)+'%';
  document.getElementById('pg').textContent=(i+1)+' / '+slides.length;
  if(location.hash!=='#'+(i+1))history.replaceState(null,'','#'+(i+1));
  if(send!==false)bc&&bc.postMessage({i:cur,f:frag});}
function next(){const fs=frags(cur);if(frag<fs.length){fs[frag].classList.add('on');frag++;bc&&bc.postMessage({i:cur,f:frag});}else show(cur+1,0);}
function prev(){if(frag>0&&!document.body.classList.contains('all')){frag--;frags(cur)[frag].classList.remove('on');bc&&bc.postMessage({i:cur,f:frag});}else show(cur-1,-1);}
addEventListener('keydown',e=>{if(e.target.closest&&e.target.closest('iframe'))return;
  const k=e.key;if(['ArrowRight','ArrowDown','PageDown',' ','Enter'].includes(k)){e.preventDefault();next();}
  else if(['ArrowLeft','ArrowUp','PageUp','Backspace'].includes(k)){e.preventDefault();prev();}
  else if(k==='Home')show(0);else if(k==='End')show(slides.length-1,-1);
  else if(k==='f'||k==='F')full();else if(k==='s'||k==='S')presenter();else if(k==='Escape')closeLab();});
// touch: swipe on the page (not inside a live frame)
let tx=null;addEventListener('touchstart',e=>{tx=e.touches[0].clientX},{passive:true});
addEventListener('touchend',e=>{if(tx==null)return;const d=e.changedTouches[0].clientX-tx;if(Math.abs(d)>60)(d<0?next:prev)();tx=null;});
function full(){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();}
// full-screen lab
document.querySelectorAll('[data-act=fulllab]').forEach(b=>{b.style.cursor='pointer';b.onclick=()=>{const fl=document.getElementById('fl');
  fl.querySelector('iframe').srcdoc=dec(pages[D.clips[b.dataset.page].page]);fl.style.display='block';};});
function closeLab(){const fl=document.getElementById('fl');if(fl.style.display==='block'){fl.style.display='none';fl.querySelector('iframe').srcdoc='';}}
document.querySelector('#fl button').onclick=closeLab;
// presenter window: notes (script), next page, timer; both windows stay in step
// 讲者窗口用窗口间消息同步（平台里课件放在沙箱框里，广播频道不可用）
let pw=null;const bc={postMessage:m=>{try{pw&&!pw.closed&&pw.postMessage(Object.assign({wqdeck:D.id},m),'*')}catch(e){}}};
addEventListener('message',m=>{const d=m.data;if(!d||d.wqdeck!==D.id||m.source!==pw)return;if(d.cmd==='next')next();else if(d.cmd==='prev')prev();else if(d.cmd==='hello')bc.postMessage({i:cur,f:frag});});
function presenter(){pw=open(location.href.split('#')[0].split('?')[0]+'?presenter=1','wq-presenter-'+D.id,'width=1100,height=760');}
document.getElementById('bp').onclick=prev;document.getElementById('bn').onclick=next;document.getElementById('bs').onclick=presenter;document.getElementById('bf').onclick=full;
const h=parseInt(location.hash.slice(1));show(isNaN(h)?0:h-1,document.body.classList.contains('all')?-1:0);
addEventListener('hashchange',()=>{const h=parseInt(location.hash.slice(1));if(!isNaN(h)&&h-1!==cur)show(h-1,document.body.classList.contains('all')?-1:0);});
})();
"""

PRESENTER = r"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>讲者视图</title><style>
body{margin:0;font-family:'Noto Sans CJK SC','Microsoft YaHei',system-ui,sans-serif;background:#0b1220;color:#e6edf5}
header{display:flex;gap:14px;align-items:center;padding:12px 18px;background:#111c2e;border-bottom:1px solid #22324d}
header b{font-size:22px}header .t{margin-left:auto;font:600 26px ui-monospace,monospace;color:#f2b705}
button{font:16px inherit;padding:8px 16px;border-radius:8px;border:1px solid #2a3b57;background:#16243b;color:#e6edf5;cursor:pointer}
main{display:grid;grid-template-columns:1fr 320px;gap:18px;padding:18px}
.notes{font-size:26px;line-height:1.7;white-space:pre-wrap}.notes .en{font-size:19px;color:#8fa3ba;margin-top:18px}
aside .lbl{color:#8fa3ba;font-size:14px;margin-bottom:6px}aside .nx{font-size:20px;line-height:1.4;padding:12px;border:1px solid #22324d;border-radius:10px}
.sz{margin-left:8px}
</style></head><body><header><button id="p">◀ 上一步</button><button id="n">下一步 ▶</button><b id="pg"></b><span id="fr" style="color:#8fa3ba"></span>
<span class="sz"><button id="a">A−</button> <button id="b">A+</button></span><span class="t" id="tm">00:00</span><button id="r">计时清零</button></header>
<main><div><div class="notes" id="nz"></div><div class="notes en" id="ne"></div></div><aside><div class="lbl">下一页</div><div class="nx" id="nx"></div></aside></main>
<script>
const D=__DATA__;const bc={postMessage:m=>opener&&opener.postMessage(Object.assign({wqdeck:D.id},m),'*')};let i=0,t0=Date.now(),fs=26;
function draw(f){document.getElementById('pg').textContent=(i+1)+' / '+D.notes.length;document.getElementById('fr').textContent=f!=null?'· 第 '+f+' 步':'';
 document.getElementById('nz').textContent=D.notes[i][0]||'';document.getElementById('ne').textContent=D.notes[i][1]||'';
 document.getElementById('nx').textContent=D.titles[i+1]||'（最后一页）';}
addEventListener('message',m=>{const d=m.data;if(d&&d.wqdeck===D.id&&d.i!=null){i=d.i;draw(d.f);}});bc.postMessage({cmd:'hello'});
document.getElementById('n').onclick=()=>bc.postMessage({cmd:'next'});document.getElementById('p').onclick=()=>bc.postMessage({cmd:'prev'});
addEventListener('keydown',e=>{if(['ArrowRight',' ','PageDown'].includes(e.key)){e.preventDefault();bc.postMessage({cmd:'next'});}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();bc.postMessage({cmd:'prev'});}});
document.getElementById('r').onclick=()=>t0=Date.now();
document.getElementById('a').onclick=()=>{fs=Math.max(16,fs-2);document.getElementById('nz').style.fontSize=fs+'px';};
document.getElementById('b').onclick=()=>{fs=Math.min(48,fs+2);document.getElementById('nz').style.fontSize=fs+'px';};
setInterval(()=>{const s=Math.floor((Date.now()-t0)/1000);document.getElementById('tm').textContent=String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');},500);draw();
</script></body></html>"""


def mark_frags(html: str, layout: str) -> str:
    """Points, cards, rows and timeline events appear one by one (like PPT build animations)."""
    for cls in ('class="pt"', 'class="fact card"', 'class="tile card', 'class="num card"', 'class="row"', 'class="task"', 'class="col', 'class="footnote"', 'class="after"'):
        html = html.replace(cls, cls.replace('class="', 'class="frag '))
    return html


LIVE_AGENT = """<script>(function(){function rect(sel){if(!sel)return[0,0,0,0];var t=document.querySelector(sel);if(!t)return[0,0,0,0];var b=t.getBoundingClientRect();return[b.left,b.top,b.width,b.height];}
addEventListener('message',function(m){var d=m.data;if(!d||!d.wqlive)return;if(d.wqlive===1){(d.steps||[]).forEach(function(st){setTimeout(function(){try{[].concat(st.press||[]).forEach(function(s){var b=document.querySelector(s);b&&b.click();});
Object.keys(st.set||{}).forEach(function(k){var e=document.getElementById(k);if(!e)return;e.value=st.set[k];e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input',{bubbles:true}));});if(st.js)(0,eval)(st.js);}catch(e){console.warn(e);}},(st.at||0)*1000+300);});}
parent.postMessage({wqrect:rect(d.selector)},'*');});})();</script>"""


def page_b64(name: str, lang="zh") -> str:
    sys.path.insert(0, str(BOOK))
    from inline import inline
    src = (BOOK / "src" / lang / "labs" / f"{name}.html").read_text(encoding="utf-8")
    src = inline(src)
    src = re.sub(r'<a href="\.\./index\.html"[^>]*>[^<]*</a>', "", src)
    src = src.replace("</body>", LIVE_AGENT + "</body>", 1)
    return base64.b64encode(src.encode("utf-8")).decode("ascii")


def build_deck(spec, lesson, slides_html, out: Path) -> Path:
    no = spec["lesson"]
    clips = dict(spec.get("clips") or {})
    for lab in (s for s in spec["slides"] if s["layout"] == "lab"):
        clips["lab:" + lab["shot"]["page"]] = {"page": lab["shot"]["page"], "vw": lab["shot"].get("vw", 1400), "vh": lab["shot"].get("vh", 830),
                                               "steps": lab["shot"].get("steps") or [{"press": x["press"]} for x in lab["shot"].get("set", []) if "press" in x]}
    for c in clips.values():
        if c.get("selector") and "#stage" in c["selector"]:
            c["cover"] = True
    heavy = [k for k, s in enumerate(spec["slides"]) if any(clips.get(x, {}).get("page", "").startswith(("proto-lockstitch", "model-"))
                                                            for x in re.findall(r'data-live="([^"]+)"', slides_html[k]))]
    notes = [s.get("notes") or ["", ""] for s in spec["slides"]]
    titles = [(s.get("title") or s.get("kicker") or ["", ""])[0] for s in spec["slides"]]
    data = {"id": f"sewing-{no}", "clips": clips, "heavy": heavy}
    pres = PRESENTER.replace("__DATA__", json.dumps({"id": data["id"], "notes": notes, "titles": titles}, ensure_ascii=False))
    data["presenter"] = pres
    pages = sorted({c["page"] for c in clips.values()})
    scripts = "".join(f'<script type="text/plain" data-page="{p}">{page_b64(p)}</script>' for p in pages)
    body = "".join(slides_html)
    title = f"第 {no} 讲 {lesson['title'][0]} · 课件"
    doc = (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{e(title)}</title><style>{CSS}{DECK_CSS}</style></head><body><div id="stage">{body}</div>'
           f'<div id="bar"></div><div id="nav"><button id="bp" title="上一步 ←">◀</button><span id="pg"></span><button id="bn" title="下一步 → / 空格">▶</button>'
           f'<button id="bs" title="讲者视图（S）">讲者</button><button id="bf" title="全屏（F）">全屏</button></div>'
           f'<div id="fl"><button>返回课件（Esc）</button><iframe></iframe></div>'
           f'<script type="application/json" id="deck-data">{json.dumps(data, ensure_ascii=False).replace("</", "<\\/")}</script>{scripts}'
           f'<script>{DECK_JS}</script></body></html>')
    out.write_text(doc, encoding="utf-8")
    return out


async def preview(deck: Path, n: int, outdir: Path, only: set | None = None):
    """Screenshots of every page with everything shown (?all), for checking; reports anything that overflows the page."""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        page = await b.new_page(viewport={"width": 1920, "height": 1080})
        three = os.environ.get("WQ_THREE")
        if three:
            await page.route("**/three.min.js", lambda r: r.fulfill(path=three, content_type="application/javascript"))
        errors = []
        page.on("pageerror", lambda e_: errors.append(str(e_)))
        for i in range(1, n + 1):
            if only and i not in only:
                continue
            await page.goto(deck.resolve().as_uri() + f"?all=1#{i}")
            await page.wait_for_timeout(3500)
            over = await page.evaluate("""() => [...document.querySelectorAll('.slide.on *')].filter(e => { const r = e.getBoundingClientRect();
                return r.width > 0 && !e.closest('.live') && (r.right > innerWidth + 1 || r.bottom > innerHeight + 1); }).map(e => (e.className.baseVal ?? e.className) || e.tagName).slice(0, 4)""")
            await page.screenshot(path=str(outdir / f"p{i:02d}.jpg"), type="jpeg", quality=88)
            if over:
                print(f"! page {i} overflows: {over}")
        await b.close()
        if errors:
            print("! page errors:", errors[:3])


def make_deck(lesson_id: str, out: Path) -> Path:
    """Build the deck of one lesson into out/ and return its path (used by build_course.py too)."""
    spec = yaml.safe_load((COURSE / "slides" / f"{lesson_id}.yaml").read_text(encoding="utf-8"))
    values = run_programs(spec.get("code") or [])
    spec = fill(spec, values)
    lesson = json.loads((COURSE / "lessons" / f"{lesson_id}.json").read_text(encoding="utf-8"))
    out.mkdir(parents=True, exist_ok=True)
    slides = spec["slides"]
    pages = []
    for k, s in enumerate(slides):
        if s["layout"] == "formula":
            s["formula_html"] = formula_html(s["formula"])
        ctx = {"foot": foot(spec["lesson"], k + 1, len(slides)), "v": values}
        pages.append(mark_frags(LAYOUTS[s["layout"]](s, ctx), s["layout"]))
    no = spec["lesson"]
    return build_deck(spec, lesson, pages, out / f"第{no}讲-{lesson['title'][0]}-课件.html")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lesson")
    ap.add_argument("--out", required=True)
    ap.add_argument("--preview", default="", help="页码（逗号分隔）或 all：出预览截图")
    a = ap.parse_args()
    out = Path(a.out)
    deck = make_deck(a.lesson, out)
    print("deck:", deck, f"{deck.stat().st_size / 1e6:.2f} MB")
    if a.preview:
        n = deck.read_text(encoding="utf-8").count('<div class="slide ')
        only = None if a.preview == "all" else {int(x) for x in a.preview.split(",")}
        asyncio.run(preview(deck, n, out, only))


if __name__ == "__main__":
    main()
