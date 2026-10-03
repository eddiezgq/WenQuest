"""第 50 章共用：读数字工厂的数据（工厂数据、SH-301 工艺规程）、调用工艺文件生成器，把卡片做成书里的图。

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
