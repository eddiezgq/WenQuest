"""画 G4.6 送布组剖视图（feed_section.py 导出的 feed_section.json）：三个垂直于 x 的剖面并排，从左往右看（y 向右为往后、送布方向）。

    python3 tools/wqls/render/feed_section_fig.py <零件目录> <输出 PNG>
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
STEEL, MOVE, BRASS, DARK = "#8fa3b8", "#2f6fb3", "#c28b3c", "#4b5563"
STYLE = {   # 名字: (填充色, 剖面线, 图上的名称)
    "casting": ("#d9dce1", "///", None),
    "feed_bar": (MOVE, None, "牙架、送布牙"),
    "feed_rock": (MOVE, None, "送布摆轴"),
    "lift_rock": (MOVE, None, "抬牙摆轴"),
    "hook": (DARK, None, "旋梭"),
    "bobbin_case": ("#9ca3af", None, "梭芯套"),
    "hook_shaft": (STEEL, None, "旋梭轴"),
    "feed_ecc": (BRASS, None, "送布偏心 Ø26"),
    "feed_rod": (MOVE, None, "送布连杆"),
    "regulator": (BRASS, None, "调节器"),
    "reg_slider": (MOVE, None, "滑块"),
    "feed_link": (MOVE, None, "水平连杆 L2"),
    "shaft": (STEEL, None, "上轴"),
    "lower_shaft": (STEEL, None, "下轴"),
    "pulley_upper": ("#6b8fb3", None, "上带轮"),
    "pulley_lower": ("#6b8fb3", None, "下带轮"),
    "belt": ("#222222", None, "同步带"),
    "oil_ecc": (BRASS, None, "油泵偏心"),
    "oil_plunger": (MOVE, None, "柱塞"),
    "oil_pump": ("#7c8794", None, "油泵"),
    "lift_link": (MOVE, None, "抬牙连杆"),
    "lift_ecc": (BRASS, None, "抬牙偏心"),
}
PANELS = [("25.5", "x 25.5：牙架、送布牙从旋梭右边过去", (-60, 90), (-50, 14)),
          ("316.0", "x 316：调节器、送布摆轴曲柄", (-60, 90), (-78, 14)),
          ("331.0", "x 331：送布偏心、送布连杆（立柱里）", (-60, 90), (-75, 228))]
# 标注：剖面 → [(名字, 引线起点 (y, z), 文字位置 (y, z), 文字)]
LABELS = {
    "25.5": [("feed_bar", (40, -12.5), (48, -27), "牙架（送布牙在针 y 0 处，见三维）"), ("lift_rock", (-45, -28), (-28, -44), "抬牙摆轴（机座凸台里）"),
             ("hook_shaft", (0, -21.5), (12, -40), "旋梭轴"), ("feed_rock", (76, -40), (52, -47), "送布摆轴"),
             ("casting", (55, -3), (58, 9), "机座顶板（剖面打斜线）")],
    "316.0": [("regulator", (-6, -62), (-45, -74), "调节器"), ("reg_slider", (0, -47), (25, -64), "滑块"),
              ("lower_shaft", (28, -35), (44, -18), "下轴"), ("feed_rock", (76, -46), (50, -72), "送布摆轴曲柄")],
    "331.0": [("feed_ecc", (12, 208), (35, 222), "送布偏心 Ø26"), ("shaft", (0, 200), (-40, 172), "上轴"),
              ("feed_rod", (2, 110), (30, 128), "送布连杆（ADC12）"), ("reg_slider", (0, -50), (-40, -66), "滑块销 P"),
              ("lower_shaft", (28, -35), (50, -18), "下轴")],
}

d = Path(sys.argv[1])
sec = json.loads((d / "feed_section.json").read_text())
fig = plt.figure(figsize=(14, 9.6), dpi=150)
gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 0.62])
axs = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[:, 1])]
for ax, (key, title, xl, yl) in zip(axs, PANELS):
    R = sec["cuts"].get(key, {})
    for k in ["casting"] + [k for k in STYLE if k != "casting"]:
        rings = R.get(k) or []
        if not rings:
            continue
        verts, codes = [], []
        for r in rings:
            verts += r + [r[0]]
            codes += [MPath.MOVETO] + [MPath.LINETO] * (len(r) - 1) + [MPath.CLOSEPOLY]
        fc, hatch, name = STYLE[k]
        ax.add_patch(PathPatch(MPath(verts, codes), facecolor=fc, edgecolor="#374151", lw=0.5, hatch=hatch,
                               zorder=1 if k == "casting" else 3, alpha=1.0))
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
    ax.set_xlabel("y（mm，往后为正 = 送布方向）", color=MUTED, fontsize=8.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=7.5)
axs[0].set_ylabel("z（mm，针板面为 0，点划线）", color=MUTED, fontsize=8.5)
fig.suptitle(f"WQ-LS 送布组剖视：垂直于上轴的三个剖面，从机头一侧往右看（上轴 φ = {sec['phi']}°，送布牙在最高处附近），机座剖面打斜线",
             color=INK, fontsize=11, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(sys.argv[2])
print("ok", sys.argv[2])
