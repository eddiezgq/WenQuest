"""画 G4.7 压脚与操纵件剖视图（ctrl_section.py 导出的 ctrl_section.json）。

    python3 tools/wqls/render/ctrl_section_fig.py <零件目录> <输出 PNG>
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402

plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
INK, MUTED = "#1f2328", "#6b7280"
STEEL, MOVE, BRASS, DARK, SPRING = "#8fa3b8", "#2f6fb3", "#c28b3c", "#4b5563", "#7c3aed"
STYLE = {
    "casting": ("#d9dce1", "///"),
    "presser_bushes": (BRASS, None), "presser_bar": (MOVE, None), "presser_foot": (MOVE, None), "presser_collar": (MOVE, None),
    "presser_spring": (SPRING, None), "presser_screw": (STEEL, None), "lift_bracket": (MOVE, None), "hand_lifter": (BRASS, None),
    "knee_c2": (STEEL, None), "knee_link": (STEEL, None), "release_shaft": (STEEL, None), "stitch_dial": (BRASS, None),
    "pull_rod": (MOVE, None), "reverse_lever": (STEEL, None), "reverse_spring": (SPRING, None), "regulator": (BRASS, None),
    "reg_slider": (MOVE, None), "needle_bar": (STEEL, None), "needle_clamp": (DARK, None), "needle": (DARK, None),
    "shaft": (STEEL, None), "lower_shaft": (STEEL, None), "feed_bar": (MOVE, None),
}
# 剖面键, 标题, u 范围, v 范围, u 轴名
PANELS = [("x-16", "x −16：压脚杆、压脚弹簧、调压螺钉（从机头一侧往右看）", (-45, 70), (-8, 275), "y（mm，往后为正）"),
          ("y18", "y 18：手抬偏心凸轮、抬压脚块凸轮臂（从前往后看）", (-75, 15), (60, 200), "x（mm，往右为正）"),
          ("y-47", "y −47：针距旋钮槽轮、拉杆上端的销", (292, 388), (128, 212), "x（mm）"),
          ("y-20", "y −20：针距拉杆、调节器臂", (290, 370), (-70, 160), "x（mm）")]
LABELS = {
    "x-16": [("presser_screw", (6, 262), (40, 262), "调压螺钉 M18×1.5"), ("presser_spring", (6, 215), (40, 225), "压脚弹簧"),
             ("presser_bar", (6, 100), (40, 100), "压脚杆 Ø8（空心）"), ("lift_bracket", (30, 144), (45, 165), "抬压脚块"),
             ("presser_bushes", (2, 44), (40, 55), "下导套"), ("presser_foot", (0, 3), (35, 18), "压脚"),
             ("release_shaft", (-20, 176), (-30, 200), "松线轴")],
    "y18": [("hand_lifter", (-40, 128), (-62, 100), "手抬偏心凸轮"), ("lift_bracket", (-34, 144), (-55, 175), "抬压脚块凸轮臂")],
    "y-47": [("stitch_dial", (340, 192), (372, 206), "槽轮"), ("pull_rod", (325, 150), (305, 140), "拉杆上端的销")],
    "y-20": [("pull_rod", (324, 60), (348, 70), "针距拉杆"), ("regulator", (312, -50), (345, -40), "调节器（臂端销）")],
}

d = Path(sys.argv[1])
sec = json.loads((d / "ctrl_section.json").read_text())
fig = plt.figure(figsize=(14, 10), dpi=150)
gs = fig.add_gridspec(2, 3, width_ratios=[0.8, 0.75, 0.75], height_ratios=[1, 1])
axs = [fig.add_subplot(gs[:, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 2]), fig.add_subplot(gs[1, 1:])]
for ax, (key, title, xl, yl, ulab) in zip(axs, PANELS):
    R = sec["cuts"].get(key, {})
    for k in ["casting"] + [k for k in STYLE if k != "casting"]:
        rings = R.get(k) or []
        if not rings:
            continue
        verts, codes = [], []
        for r in rings:
            verts += r + [r[0]]
            codes += [MPath.MOVETO] + [MPath.LINETO] * (len(r) - 1) + [MPath.CLOSEPOLY]
        fc, hatch = STYLE[k]
        ax.add_patch(PathPatch(MPath(verts, codes), facecolor=fc, edgecolor="#374151", lw=0.5, hatch=hatch,
                               zorder=1 if k == "casting" else 3))
    for k, xy, txt_xy, txt in LABELS[key]:
        if R.get(k):
            ax.annotate(txt, xy, txt_xy, fontsize=8.5, color=INK, zorder=6, ha="center",
                        bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.85),
                        arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.axhline(0, color="#9b1c1c", lw=0.6, ls=(0, (12, 3, 2, 3)), zorder=4)
    ax.set_aspect("equal")
    ax.set_xlim(*xl)
    ax.set_ylim(*yl)
    ax.set_title(title, loc="left", fontsize=9.5, color=INK)
    ax.set_xlabel(ulab, color=MUTED, fontsize=8.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=7.5)
axs[0].set_ylabel("z（mm，针板面为 0，点划线）", color=MUTED, fontsize=8.5)
fig.suptitle(f"WQ-LS 压脚与操纵件剖视（压脚放下、针距 3 mm 正缝，上轴 φ = {sec['phi']}°），机壳剖面打斜线",
             color=INK, fontsize=11, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(sys.argv[2])
print("ok", sys.argv[2])
