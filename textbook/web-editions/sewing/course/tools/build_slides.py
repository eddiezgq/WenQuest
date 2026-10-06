#!/usr/bin/env python3
"""第 24 轮：《缝纫机设计与制造》新版课件。

    python3 course/tools/build_slides.py ch01 --out <目录>        # 生成 第1讲-…-课件.pptx 和逐页预览 png
    python3 course/tools/build_slides.py ch01 --out <目录> --only 3,4   # 只出这几页的预览（不出 pptx），改版式时用

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
.cover .bgv{position:absolute;inset:0}
.cover .bgv img{width:100%;height:100%;object-fit:cover;filter:saturate(1.05)}
.cover .shade{position:absolute;inset:0;background:linear-gradient(90deg,rgba(6,12,22,.96) 0%,rgba(6,12,22,.82) 38%,rgba(6,12,22,.15) 72%,rgba(6,12,22,0) 100%)}
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
.lab .task{display:flex;gap:20px;margin-bottom:30px}
.lab .task .k{flex:none;width:52px;height:52px;border-radius:14px;background:rgba(242,183,5,.14);color:var(--amber);font-family:var(--enf);font-weight:800;font-size:28px;display:flex;align-items:center;justify-content:center}
.lab .task .zh{font-size:34px;line-height:1.35}
.lab .task .en{font-family:var(--enf);font-size:21px;color:var(--en);margin-top:6px}
.lab .go{margin-top:30px;display:inline-flex;align-items:center;gap:16px;background:var(--amber);color:#0b1220;font-size:36px;font-weight:800;padding:20px 40px;border-radius:999px;box-shadow:0 14px 40px rgba(242,183,5,.35)}
.lab .go span{font-family:var(--enf);font-size:24px;font-weight:600;opacity:.8}
/* timeline */
.timeline .tl{position:absolute;left:110px;right:110px;top:330px;height:600px}
/* bignum */
.bignum .nums{position:absolute;left:110px;right:110px;top:330px;display:flex;gap:40px}
.bignum .num{flex:1;padding:46px 44px}
.bignum .num .n{font-size:120px;font-weight:800;line-height:1;background:linear-gradient(180deg,#ffd75a,#f2b705);-webkit-background-clip:text;color:transparent}
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
.chain .flow{position:absolute;left:90px;right:90px;top:400px;display:flex;align-items:center;gap:10px}
.chain .step{flex:1;height:190px;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:22px;background:#111d31;border:1px solid var(--line);text-align:center;padding:0 8px}
.chain .step .zh{font-size:34px;font-weight:700}
.chain .step .en{font-family:var(--enf);font-size:18px;color:var(--en);margin-top:8px}
.chain .step.hot{background:linear-gradient(180deg,#f2b705,#d99b00);border:none;transform:scale(1.12);box-shadow:0 20px 60px rgba(242,183,5,.35);color:#0b1220}
.chain .step.hot .en{color:#3d2f00}
.chain .arr{flex:none;color:#4b5f7d;font-size:34px}
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
  <g font-size="22" fill="#c9a94a" class="en"><text x="120" y="305" text-anchor="end" class="en">up</text><text x="450" y="100" text-anchor="middle" class="en">forward</text>
    <text x="760" y="305" class="en">down</text><text x="450" y="440" text-anchor="middle" class="en">back</text></g>
  <g transform="translate(250,170)"><rect width="200" height="40" rx="6" fill="#ff7a45"/>
    <path d="M0 0 l20 -26 l20 26 l20 -26 l20 26 l20 -26 l20 26 l20 -26 l20 26 l20 -26 l20 26" fill="#ff7a45"/></g>
  <text x="560" y="230" font-size="26" fill="#ffb38f">送布牙 · feed dog</text>
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
    if "video" in src:
        poster = ctx["posters"][src["video"]]
        return (f'<div class="media" data-video="{src["video"]}" style="height:{h}px"><img src="{poster}"></div>')
    if "html" in src:
        return f'<div style="height:{h}px">{CUSTOM[src["html"]]()}</div>'
    if "img" in src:
        return f'<div class="media{" white" if white else ""}" style="height:{h}px"><img src="{src["img"]}"></div>'
    return ""


def L_cover(s, ctx):
    return (f'<div class="slide cover"><div class="bgv" data-video="{s["video"]}" data-full="1"><img src="{ctx["posters"][s["video"]]}"></div><div class="shade"></div>'
            f'<div class="txt"><div class="kick">{e(s["kicker"][0])}<span>{e(s["kicker"][1])}</span></div><h1>{e(s["title"][0])}</h1>'
            f'<div class="h1en">{e(s["title"][1])}</div><div class="sub">{e(s["sub"][0])}</div><div class="suben">{e(s["sub"][1])}</div></div>'
            f'<div class="brand"><b>问渠 WenQuest</b>{COURSE_NAME[0]} · {COURSE_NAME[1]}</div></div>')


def L_section(s, ctx):
    return (f'<div class="slide section"><div class="grain"></div><div class="no">{e(s["no"])}</div><div class="bar"></div>'
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
    return (f'<div class="slide lab"><div class="grain"></div>{head(s["title"])}<div class="body"><div class="media white" style="height:650px"><img src="{ctx["labshot"]}"></div>'
            f'<div class="tasks"><div class="h">任务<span>Tasks</span></div>{tasks}<div class="go" data-link="lab">打开虚拟实验 ▶<span>Open the lab</span></div></div></div>{ctx["foot"]}</div>')


def L_timeline(s, ctx):
    ev = s["events"]
    y0, y1 = min(x["year"] for x in ev), max(x["year"] for x in ev)
    X = lambda y: 60 + (y - y0) / (y1 - y0) * 1580
    g = ['<path d="M20 300 L1680 300" stroke="#2c3e5c" stroke-width="6" stroke-linecap="round"/>']
    for k, v in enumerate(ev):
        x, up = X(v["year"]), k % 2 == 0
        y = 70 if up else 400
        g.append(f'<path d="M{x:.0f} 300 L{x:.0f} {(y + 150) if up else y}" stroke="#4b5f7d" stroke-width="3" stroke-dasharray="6 6"/>')
        g.append(f'<circle cx="{x:.0f}" cy="300" r="20" fill="#f2b705"/><circle cx="{x:.0f}" cy="300" r="34" fill="none" stroke="rgba(242,183,5,.35)" stroke-width="6"/>')
        g.append(f'<text x="{x:.0f}" y="{y + 10}" font-size="54" font-weight="800" fill="#f2b705" text-anchor="middle" class="en">{v["year"]}</text>')
        g.append(f'<text x="{x:.0f}" y="{y + 62}" font-size="38" font-weight="700" fill="#f3f6fa" text-anchor="middle">{e(v["who"][0])} <tspan class="en" font-size="24" fill="#8fa3ba">{e(v["who"][1])}</tspan></text>')
        g.append(f'<text x="{x:.0f}" y="{y + 108}" font-size="30" fill="#d3deea" text-anchor="middle">{e(v["what"][0])}</text>')
        g.append(f'<text x="{x:.0f}" y="{y + 140}" font-size="21" fill="#8fa3ba" text-anchor="middle" class="en">{e(v["what"][1])}</text>')
    return (f'<div class="slide timeline"><div class="grain"></div>{head(s["title"])}<div class="tl"><svg viewBox="0 0 1700 600" width="1700" height="600">{"".join(g)}</svg></div>{ctx["foot"]}</div>')


def L_bignum(s, ctx):
    nums = "".join(f'<div class="num card"><div class="n">{e(n["n"])}</div><div class="ne">{e(n.get("n_en", ""))}</div><div class="zh">{e(n["label"][0])}</div><div class="en">{e(n["label"][1])}</div></div>'
                   for n in s["nums"])
    fn = f'<div class="footnote"><div class="zh">{e(s["foot"][0])}</div><div class="en">{e(s["foot"][1])}</div></div>' if s.get("foot") else ""
    return f'<div class="slide bignum"><div class="grain"></div>{head(s["title"])}<div class="nums">{nums}</div>{fn}{ctx["foot"]}</div>'


def L_stages(s, ctx):
    st = s["stages"]
    y0, y1 = 1840, 2030
    X = lambda y: 260 + (y - y0) / (y1 - y0) * 1420
    cols = ["#7aa5f0", "#4c8dff", "#2ec4b6", "#ff7a45", "#a78bfa"]
    g = []
    for yr in range(1850, 2031, 30):
        g.append(f'<path d="M{X(yr):.0f} 0 L{X(yr):.0f} 470" stroke="#1e2c45" stroke-width="2"/><text x="{X(yr):.0f}" y="505" font-size="24" fill="#5f7189" text-anchor="middle" class="en">{yr}</text>')
    for k, v in enumerate(st):
        y = 10 + k * 92
        g.append(f'<text x="0" y="{y + 50}" font-size="40" font-weight="800" fill="{cols[k]}">{k + 1} {e(v["name"][0])}</text>')
        g.append(f'<rect x="{X(v["from"]):.0f}" y="{y + 8}" width="{X(v["to"]) - X(v["from"]):.0f}" height="58" rx="14" fill="{cols[k]}" opacity=".9"/>')
        g.append(f'<text x="{X(v["from"]) + 20:.0f}" y="{y + 47}" font-size="27" font-weight="700" fill="#08101d">{e(v["note"][0])}</text>')
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
            f'<div class="brace" style="left:{90 + 1740 * 5.3 / 9:.0f}px;width:{1740 * 2 / 9 + 40:.0f}px">▲ 本课程 · this course</div>{fn}{ctx["foot"]}</div>')


def L_answer(s, ctx):
    rows = "".join(f'<div class="row"><div class="a">{e(r[0])}</div><div class="b">{e(r[1])}</div></div>' for r in s["rows"])
    return (f'<div class="slide answer"><div class="grain"></div>{head(s["title"], s.get("tag"))}<div class="rows">{rows}</div>'
            f'<div class="side card"><div class="big">×{ctx["v"]["ch01"]["F6000"] / ctx["v"]["ch01"]["F5000"]:.2f}</div><div class="zh">5000 → 6000 针/分<br>转速 ×1.2，惯性力 ×1.2²</div>'
            f'<div class="en">speed ×1.2, force ×1.2²</div></div>'
            f'<div class="footnote"><div class="zh">{e(s["foot"][0])}</div><div class="en">{e(s["foot"][1])}</div></div>{ctx["foot"]}</div>')


def L_roadmap(s, ctx):
    p = s["parts"]
    g = []
    cols = ["#7aa5f0", "#4c8dff", "#4c8dff", "#2ec4b6", "#2ec4b6", "#ff7a45", "#ff7a45", "#a78bfa"]
    path = "M60 420 C 300 420, 300 140, 560 140 S 820 420, 1080 420 S 1340 140, 1640 140"
    g.append(f'<path d="{path}" stroke="#22324d" stroke-width="40" fill="none" stroke-linecap="round"/>')
    g.append(f'<path d="{path}" stroke="#f2b705" stroke-width="5" fill="none" stroke-dasharray="26 18"/>')
    pos = [(60, 420), (300, 290), (560, 140), (820, 280), (1080, 420), (1340, 280), (1500, 170), (1640, 140)]
    for k, (x, y) in enumerate(pos):
        g.append(f'<circle cx="{x}" cy="{y}" r="30" fill="{cols[k]}"/><text x="{x}" y="{y + 11}" font-size="30" font-weight="800" fill="#08101d" text-anchor="middle" class="en">{k + 1}</text>')
        ty = y + 90 if y < 300 else y - 70
        g.append(f'<text x="{x}" y="{ty}" font-size="36" font-weight="700" fill="#f3f6fa" text-anchor="middle">{e(p[k][0])}</text>')
        g.append(f'<text x="{x}" y="{ty + 34}" font-size="21" fill="#8fa3ba" text-anchor="middle" class="en">{e(p[k][1])}</text>')
    return f'<div class="slide roadmap"><div class="grain"></div>{head(s["title"])}<div class="road"><svg viewBox="0 0 1700 600" width="1700" height="600">{"".join(g)}</svg></div>{ctx["foot"]}</div>'


def L_summary(s, ctx):
    return (f'<div class="slide summary"><div class="grain"></div>{head(s["title"])}{points(s["points"], numbered=True)}'
            f'<div class="after"><div class="zh">{e(s["after"][0])}</div><div class="en">{e(s["after"][1])}</div></div>{ctx["foot"]}</div>')


LAYOUTS = {k[2:]: v for k, v in globals().items() if k.startswith("L_")}


def formula_html(tex: str) -> str:
    """The few formulas the slides need, as HTML (F = m a ∝ n²)."""
    s = tex.replace("\\,", " ").replace("\\;", " ").replace("\\propto", "∝").replace("^{2}", "²")
    return e(s).replace("∝", '<span style="color:#f2b705;font-style:normal"> ∝ </span>')


# ---------------------------------------------------------------- recording clips (animation pages, 3D prototype)
async def record_clip(page_name: str, selector: str, steps: list, dur: float, out_mp4: Path, poster: Path, lang="zh", fps=30):
    from playwright.async_api import async_playwright
    src = BOOK / "src" / lang / "labs" / f"{page_name}.html"
    manual = "manual:on=>" in src.read_text(encoding="utf-8")
    fps = 15 if manual else fps
    frames = out_mp4.with_suffix("")
    shutil.rmtree(frames, ignore_errors=True)
    frames.mkdir(parents=True)
    async with async_playwright() as p:
        args = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] if manual else []
        b = await p.chromium.launch(args=args)
        ctx = await b.new_context(viewport={"width": 1600, "height": 900}, device_scale_factor=1.5)
        page = await ctx.new_page()
        three = os.environ.get("WQ_THREE")
        if three:
            await page.route("**/three.min.js", lambda r: r.fulfill(path=three, content_type="application/javascript"))
        if not manual:
            await page.clock.install()
        await page.goto(src.resolve().as_uri())
        if manual:
            for _ in range(240):
                if await page.evaluate("!!(window.__api && window.__api.step)"):
                    break
                await asyncio.sleep(0.5)
            await page.evaluate("__api.manual(true)")
        else:
            await page.clock.run_for(800)
        box = await page.evaluate(f"(() => {{ const r = document.querySelector({json.dumps(selector)}).getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }})()")
        cdp = await ctx.new_cdp_session(page)
        n = int(dur * fps)
        done = set()
        for fr in range(n):
            t = fr / fps
            for k, st in enumerate(steps):
                if k in done or t < st.get("at", 0):
                    continue
                done.add(k)
                for sel in ([st["press"]] if isinstance(st.get("press"), str) else st.get("press") or []):
                    await page.click(sel)
                for pid, v in (st.get("set") or {}).items():
                    await page.evaluate("""([pid, v]) => { const e = document.getElementById(pid); e.value = v;
                        e.dispatchEvent(new Event(e.tagName === 'SELECT' ? 'change' : 'input', {bubbles: true})); }""", [pid, v])
                if st.get("js"):
                    await page.evaluate(st["js"])
            if manual:
                await page.evaluate(f"__api.step({1 / fps})")
            else:
                await page.clock.run_for(int(1000 / fps))
            r = await cdp.send("Page.captureScreenshot", {"format": "jpeg", "quality": 92,
                                                           "clip": {"x": box[0], "y": box[1], "width": box[2], "height": box[3], "scale": 1.5}})
            (frames / f"{fr:05d}.jpg").write_bytes(base64.b64decode(r["data"]))
        await b.close()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(frames / "%05d.jpg"),
                    "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2,fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                    "-movflags", "+faststart", str(out_mp4)], check=True)
    mid = sorted(frames.glob("*.jpg"))[int(n * 0.7)]
    shutil.copy(mid, poster)
    shutil.rmtree(frames)


async def lab_shot(page_name: str, presses: list, out: Path, lang="zh"):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await b.new_page(viewport={"width": 1280, "height": 760}, device_scale_factor=2)
        await page.goto((BOOK / "src" / lang / "labs" / f"{page_name}.html").resolve().as_uri())
        await page.wait_for_timeout(600)
        for sel in presses:
            await page.click(sel)
        await page.wait_for_timeout(4000)
        await page.screenshot(path=str(out), type="jpeg", quality=92)
        await b.close()


# ---------------------------------------------------------------- render slides and measure where videos / links go
async def render(html_pages: list[str], outdir: Path) -> list[dict]:
    from playwright.async_api import async_playwright
    res = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await b.new_page(viewport={"width": W, "height": H_}, device_scale_factor=SCALE)
        for k, doc in enumerate(html_pages):
            f = outdir / f"slide{k + 1:02d}.html"
            f.write_text(doc, encoding="utf-8")
            await page.goto(f.resolve().as_uri())
            await page.wait_for_timeout(250)
            boxes = await page.evaluate("""() => [...document.querySelectorAll('[data-video],[data-link]')].map(e => {
                const r = e.getBoundingClientRect(); return {video: e.dataset.video || null, link: e.dataset.link || null, x: r.x, y: r.y, w: r.width, h: r.height}; })""")
            over = await page.evaluate("""() => [...document.querySelectorAll('.slide *')].filter(e => {
                const r = e.getBoundingClientRect(); return r.width > 0 && (r.right > 1921 || r.bottom > 1081); }).map(e => e.className || e.tagName).slice(0, 5)""")
            img = outdir / f"slide{k + 1:02d}.jpg"
            await page.screenshot(path=str(img), type="jpeg", quality=93)
            res.append({"img": img, "boxes": boxes, "overflow": over})
        await b.close()
    return res


def build_pptx(slides, rendered, clips, notes, lab_no, out: Path):
    from pptx import Presentation
    from pptx.util import Emu
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)          # 13.333 × 7.5 in
    px = 12192000 / W
    blank = prs.slide_layouts[6]
    for s, r, nt in zip(slides, rendered, notes):
        sl = prs.slides.add_slide(blank)
        sl.shapes.add_picture(str(r["img"]), 0, 0, prs.slide_width, prs.slide_height)
        for bx in r["boxes"]:
            x, y, w, h = (Emu(int(v * px)) for v in (bx["x"], bx["y"], bx["w"], bx["h"]))
            if bx["video"]:
                c = clips[bx["video"]]
                mv = sl.shapes.add_movie(str(c["mp4"]), x, y, w, h, poster_frame_image=str(c["poster"]), mime_type="video/mp4")
                mv.name = f"video {bx['video']}"
            if bx["link"] == "lab":
                from pptx.enum.shapes import MSO_SHAPE
                shp = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
                shp.fill.background()
                shp.line.fill.background()
                shp.click_action.hyperlink.address = LAB_URL.format(no=lab_no)
                shp.name = f"lab {lab_no}"
                tf = shp.text_frame          # 平台放映器按页面文字认实验；字是透明的，不影响画面
                tf.text = f"虚拟实验 {lab_no} Lab {lab_no}"
                for para in tf.paragraphs:
                    for run in para.runs:
                        run.font.size = Emu(12700 * 2)
                        run.font.color.rgb = __import__("pptx.dml.color", fromlist=["RGBColor"]).RGBColor(0xF2, 0xB7, 0x05)
        sl.notes_slide.notes_text_frame.text = "\n\n".join(x for x in nt if x)
    prs.save(str(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lesson")
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    spec = yaml.safe_load((COURSE / "slides" / f"{a.lesson}.yaml").read_text(encoding="utf-8"))
    values = run_programs(spec.get("code") or [])
    spec = fill(spec, values)
    lesson = json.loads((COURSE / "lessons" / f"{a.lesson}.json").read_text(encoding="utf-8"))
    out = Path(a.out)
    work = out / "work"
    work.mkdir(parents=True, exist_ok=True)
    # clips (cached by their spec)
    clips, posters = {}, {}
    for cid, c in (spec.get("clips") or {}).items():
        key = hashlib.sha1(json.dumps(c, sort_keys=True).encode() + (BOOK / "src" / "zh" / "labs" / f"{c['page']}.html").read_bytes()).hexdigest()[:10]
        mp4, poster = work / f"clip_{cid}_{key}.mp4", work / f"clip_{cid}_{key}.jpg"
        if not mp4.exists():
            print("recording", cid, flush=True)
            asyncio.run(record_clip(c["page"], c["selector"], c.get("steps") or [], float(c["dur"]), mp4, poster))
        clips[cid] = {"mp4": mp4, "poster": poster}
        posters[cid] = poster.resolve().as_uri()
    labshot = work / "labshot.jpg"
    lab_slide = next((s for s in spec["slides"] if s["layout"] == "lab"), None)
    if lab_slide and not labshot.exists():
        asyncio.run(lab_shot(lab_slide["shot"]["page"], [x["press"] for x in lab_slide["shot"].get("set", []) if "press" in x], labshot))
    slides = spec["slides"]
    total = len(slides)
    pages = []
    for k, s in enumerate(slides):
        if s["layout"] == "formula":
            s["formula_html"] = formula_html(s["formula"])
        ctx = {"posters": posters, "labshot": labshot.resolve().as_uri(), "foot": foot(spec["lesson"], k + 1, total), "v": values}
        body = LAYOUTS[s["layout"]](s, ctx)
        pages.append(f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>')
    only = {int(x) for x in a.only.split(",") if x}
    if only:
        idx = sorted(only)
        rendered = asyncio.run(render([pages[i - 1] for i in idx], work))
        for i, r in zip(idx, rendered):
            dst = out / f"p{i:02d}.jpg"
            shutil.copy(r["img"], dst)
            print(dst, "overflow:" if r["overflow"] else "", r["overflow"] or "")
        return
    rendered = asyncio.run(render(pages, work))
    for i, r in enumerate(rendered, 1):
        shutil.copy(r["img"], out / f"p{i:02d}.jpg")
        if r["overflow"]:
            print(f"! page {i} overflows: {r['overflow']}")
    notes = [s.get("notes") or ["", ""] for s in slides]
    no = spec["lesson"]
    name = f"第{no}讲-{lesson['title'][0]}-课件（中英对照）.pptx"
    build_pptx(slides, rendered, clips, notes, spec["lab"]["no"] if spec.get("lab") else "", out / name)
    print("pptx:", out / name, f"{(out / name).stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
