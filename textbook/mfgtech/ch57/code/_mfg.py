"""第 50–56 章共用：读数字工厂的数据（工厂数据、SH-301 工艺规程）、调用工艺文件生成器，把卡片做成书里的图。

书里的卡片与数字工厂提交、审批、执行的是同一份数据（factory/digital/std/SH-301_process.yaml），
由同一个程序生成（factory/digital/hub/cards.py）。卡片在书里是图：用浏览器把卡片排好版、截成图片，包在 SVG 里。
"""
import base64
import copy
import os
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory", REPO / "factory" / "digital"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from factory import data as F  # noqa: E402
from hub import cards  # noqa: E402

PLAN_FILE = REPO / "factory" / "digital" / "std" / "SH-301_process.yaml"
INK = "#1d2327"
MUTED = "#7a868d"
ACCENT = "#3a7dc9"
WARM = "#d98c3a"
RED = "#b5443b"
GREEN = "#2f8f5b"


def plan():
    return yaml.safe_load(PLAN_FILE.read_text(encoding="utf-8"))


def op(p, seq):
    return next(o for o in p["operations"] if o["seq"] == seq)


def setups(o):
    """一道工序的安装次数：工步里每“调头”一次多一次安装。"""
    if not o.get("steps"):
        return 1
    return 1 + sum("调头" in s["content"] for s in o["steps"])


def passes(o):
    return sum(cards.step_values(s)["passes"] or 0 for s in o.get("steps") or [] if s.get("op") in ("turn", "face", "keyway"))


def card_figure(section_html: str, name: str, width=1060, scale=1.6):
    """把一张卡片（cards.py 生成的 <section class='card'>）排版成图片，存为书里的图 <name>.svg。"""
    from playwright.sync_api import sync_playwright
    import bookout
    page_html = ("<!doctype html><html><head><meta charset='utf-8'><style>" + cards.CSS +
                 "body{margin:0;padding:6px;background:#fff}.card{margin:0}</style></head><body>" + section_html + "</body></html>")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": 900}, device_scale_factor=scale)
        pg.set_content(page_html)
        el = pg.query_selector("section.card")
        box = el.bounding_box()
        png = el.screenshot(type="png")
        b.close()
    w, h = box["width"], box["height"]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w:.0f} {h:.0f}" '
           f'width="{w:.0f}" height="{h:.0f}"><image width="{w:.0f}" height="{h:.0f}" '
           f'href="data:image/png;base64,{base64.b64encode(png).decode()}"/></svg>')
    folder = os.environ.get("WQ_BOOK_FIGDIR")
    path = os.path.join(folder, f"{name}.svg") if folder else f"{name}.svg"
    Path(path).write_text(svg, encoding="utf-8")
    bookout._values.setdefault("_figures", []).append(name)
    bookout.out()


def deep(p):
    return copy.deepcopy(p)


def tol():
    from hub import tolerance
    return tolerance


def fx():
    from hub import fixture
    return fixture


def fe():
    from hub import fe2d
    return fe2d


def fixture_data(fid="JJ-301-50"):
    return fx().load_fixture(fid)


def chains_data():
    """WQR-105 中还没有完整工艺规程的零件的尺寸链数据（std/WQR-105_chains.yaml）。"""
    return yaml.safe_load((REPO / "factory" / "digital" / "std" / "WQR-105_chains.yaml").read_text(encoding="utf-8"))


def link(name, nominal, es=0.0, ei=0.0, sense=1):
    return tol().Link(name, nominal, es, ei, sense)


# ---------------------------------------------------------------- 三维图（第 13 轮 8.3）：数字工厂的三维模型 + render3d
def m3d():
    """返回 (core, workpiece, jj30150, elements, typical, machines, shapes) 七个模块。"""
    from models3d import core, workpiece, jj30150, elements, typical, machines, shapes
    return core, workpiece, jj30150, elements, typical, machines, shapes


def r3d():
    import render3d
    return render3d


def loc():
    from models3d import locating
    return locating


ISO = [0.9, -1.25, 0.95]          # 书中三维图的常用视向（从右前上方看）


# ---------------------------------------------------------------- 第 54 章：加工精度库、仿真车间的误差模型、误差放大的工件形状
def acc():
    from hub import accuracy
    return accuracy


def errs():
    from sim import errors
    return errors


def spc():
    from hub import spc as _spc
    return _spc


def x3d():
    from models3d import errors3d
    return errors3d


def shift(problem="tailstock_offset", n_ok=30, n_bad=30, seeds=(541, 542), dress_every=10, magnitude=None):
    """仿真车间的一个班次（与 textbook/tools/factory_shots.py 灌进数字工厂的数据同一个模型）：先正常磨 n_ok 件，
    再在问题情景 problem 下磨 n_bad 件；砂轮每 dress_every 件修整一次。返回各特性的测得值、修整后第一件的序号（resets）、问题开始的序号。"""
    ER = errs()
    a = ER.simulate(n_ok, None, seed=seeds[0], dress_every=dress_every)
    b = ER.simulate(n_bad, problem, magnitude=magnitude, seed=seeds[1], dress_every=dress_every) if n_bad else {"values": {c[0]: [] for c in ER.CHARS}, "dress_after": []}
    vals = {c[0]: a["values"][c[0]] + b["values"][c[0]] for c in ER.CHARS}
    resets = [i + 1 for i in a["dress_after"] if i + 1 < n_ok] + [n_ok] + [n_ok + i + 1 for i in b["dress_after"] if i + 1 < n_bad]
    return {"values": vals, "resets": sorted(set(r for r in resets if 0 < r < n_ok + n_bad)), "start": n_ok, "chars": ER.CHARS}


# ---------------------------------------------------------------- 第 55 章：表面完整性库、表面强化的三维模型
def surf():
    from hub import surface
    return surface


def s3d():
    from models3d import surface3d
    return surface3d


def mats():
    from cae import materials
    return materials


# ---------------------------------------------------------------- 第 56 章：工艺路线（SH-101）
def route():
    from hub import route as _r
    return _r


def proc():
    from hub import process
    return process


def part101():
    return yaml.safe_load((REPO / "factory" / "digital" / "std" / "SH-101_part.yaml").read_text(encoding="utf-8"))


def route101():
    return yaml.safe_load((REPO / "factory" / "digital" / "std" / "SH-101_route.yaml").read_text(encoding="utf-8"))


def r101():
    from models3d import route3d
    return route3d


def review(p):
    """AI 工艺评审员对一份工艺规程的意见（与数字工厂“AI 预检”同一个函数）。"""
    return proc().review(copy.deepcopy(p))


def wrap(text, n):
    """按字数折行（中文一个字算 1，英文字母、数字算 0.55）。"""
    out, line, w = [], "", 0.0
    for ch in str(text):
        cw = 0.55 if ord(ch) < 128 else 1.0
        if w + cw > n and line:
            out.append(line)
            line, w = "", 0.0
        line += ch
        w += cw
    out.append(line)
    return "\n".join(out)


def table_fig(plt, header, rows, widths, name, colors=None, fontsize=7.0, width_in=7.0):
    """书中的表格图：表头、各行（自动折行，行高随内容），widths 为各列宽占比；colors：{(行, 列): 颜色}。"""
    from bookout import figure
    chars_per_unit = width_in * 72 / (fontsize * 1.05)          # 整个表宽能放多少个汉字
    wr = [[wrap(c, max(2, widths[j] * chars_per_unit - 1.2)) for j, c in enumerate(r)] for r in [header] + rows]
    nlines = [max(c.count("\n") + 1 for c in r) for r in wr]
    lh = fontsize * 1.45 / 72
    heights = [n * lh + 0.07 for n in nlines]
    H = sum(heights)
    fig = plt.figure(figsize=(width_in, H + 0.04))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(H, 0)
    y = 0.0
    xs = [0]
    for w in widths:
        xs.append(xs[-1] + w)
    for i, r in enumerate(wr):
        h = heights[i]
        if i == 0:
            ax.add_patch(plt.Rectangle((0, 0), 1, h, fc="#eef1f3", ec="none"))
        for j, c in enumerate(r):
            col = (colors or {}).get((i - 1, j), INK)
            ax.text(xs[j] + 0.008, y + 0.035, c, fontsize=fontsize, va="top", ha="left", color=col,
                    fontweight="bold" if i == 0 else "normal", linespacing=1.3)
        ax.plot([0, 1], [y + h, y + h], color="#c9cfd3", lw=0.6)
        y += h
    for x in xs:
        ax.plot([x, x], [0, H], color="#c9cfd3", lw=0.6)
    ax.plot([0, 1], [0, 0], color="#c9cfd3", lw=0.6)
    figure(fig, name)


def plan101():
    """SH-101 的全套工艺规程（第 57 章主线，std/SH-101_process.yaml）。"""
    return yaml.safe_load((REPO / "factory" / "digital" / "std" / "SH-101_process.yaml").read_text(encoding="utf-8"))


def cards():
    from hub import cards as _c
    return _c


# 一年的有效工作时间（min）：250 天、两班、每班 480 min、设备综合效率 0.85（第 56.8 节，hub/process.py FE_MIN）
FE_MIN = 250 * 2 * 480 * 0.85
