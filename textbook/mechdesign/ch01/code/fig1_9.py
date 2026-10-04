"""图 1.9.1 本书路线图：52 章按篇着色；八种课程各用哪些章（提纲第四节“课程路线表”，选用的章画浅色）。"""
import re
from pathlib import Path

import yaml

import _ch1 as H
from bookout import T, figure, out, style

ROOT = H.ROOT
book = yaml.safe_load((Path(__file__).resolve().parents[2] / "book.yaml").read_text(encoding="utf-8"))
parts = [p["title"] for p in book["parts"]]
part_of = {c["no"]: parts.index(c["part"]) for c in book["chapters"]}
n_ch = len(book["chapters"])

outline = (ROOT / book["source"]).read_text(encoding="utf-8")
tab = outline[outline.index("## 四、课程路线表"):]
routes = []
for line in tab.splitlines():
    m = re.match(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
    if not m or m.group(1) in ("课程", "---"):
        continue
    name, hours, used = m.groups()
    used = re.sub(r"（[^）]*）", "", used)                     # 括号里是节号，不计
    core, opt = (used.split("选") + [""])[:2]
    def chs(s):
        out_ = set()
        for a, b in re.findall(r"(\d+)(?:\s*[–-]\s*(\d+))?", s):
            out_ |= set(range(int(a), int(b or a) + 1))
        return out_
    routes.append((name, hours, chs(core), chs(opt) - chs(core)))

EN = {"机械原理": "Theory of Machines", "机械设计": "Machine Design", "机械设计基础": "Fundamentals of Machine Design",
      "互换性与测量技术": "Tolerancing and Metrology", "机械设计课程设计": "Machine Design Project", "现代设计方法": "Modern Design Methods",
      "机器人机械设计": "Mechanical Design of Robots", "CAD/CAE/CAM 与数字化制造": "CAD/CAE/CAM and Digital Manufacturing"}
COL = ["#7a868d", "#2c6fbb", "#c0392b", "#2ca02c", "#8e44ad", "#b8860b", "#17becf", "#e377c2", "#1f77b4", "#ff7f0e"]
plt = style()
fig, ax = plt.subplots(figsize=(6.9, 3.6))
for c in range(1, n_ch + 1):
    ax.add_patch(H.Rect((c - 0.5, len(routes) + 0.2), 1, 0.6, COL[part_of[c] % len(COL)]) if hasattr(H, "Rect") else
                 __import__("matplotlib.patches", fromlist=["Rectangle"]).Rectangle((c - 0.5, len(routes) + 0.2), 1, 0.6,
                                                                                     fc=COL[part_of[c] % len(COL)], ec="white", lw=0.5))
ZH_NUM = "一二三四五六七八九"
for p in range(len(parts)):
    cs_ = [c for c in part_of if part_of[c] == p]
    lab = T("导论", "Intro") if p == 0 else T(ZH_NUM[p - 1], "P{}".format(p))
    ax.text((min(cs_) + max(cs_)) / 2, len(routes) + 1.0, lab, ha="center", va="bottom", fontsize=6.5)
for k, (name, hours, core, opt) in enumerate(routes):
    y = len(routes) - 1 - k
    short = re.sub(r"（.*?）", "", name)
    ax.text(0.2, y, T(short, EN.get(short, short)), ha="right", va="center", fontsize=7)
    for c in core:
        ax.plot(c, y, "s", color=COL[part_of[c] % len(COL)], ms=5)
    for c in opt:
        ax.plot(c, y, "s", color=COL[part_of[c] % len(COL)], ms=5, alpha=0.3)
ax.set_xlim(-9.5, n_ch + 0.6)
ax.set_ylim(-0.8, len(routes) + 1.5)
ax.set_xticks([1, 10, 20, 30, 40, 50])
ax.tick_params(axis="x", labelsize=7)
ax.set_xlabel(T("章", "chapter"), fontsize=8)
ax.set_yticks([])
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig1_9_1")
out(n_ch=n_ch, n_parts=len(parts) - 1, n_routes=len(routes))
