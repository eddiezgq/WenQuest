"""画 G4.5 旋梭组剖视图（hook_section.py 导出的 section.json）。

    python3 tools/wqls/render/hook_section_fig.py <零件目录> <输出 PNG>
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
STYLE = {   # 名字: (填充色, 剖面线, 图上的名称)
    "casting": ("#d9dce1", "///", None),
    "lower_shaft": ("#8fa3b8", None, "下轴 Ø12"),
    "hook_shaft": ("#8fa3b8", None, "旋梭轴 Ø10"),
    "bearings_lower": ("#5b6b7d", None, "6201 ×2"),
    "gear_hook": ("#c28b3c", None, "斜齿轮 z 20"),
    "gear_lower": ("#c28b3c", None, "斜齿轮 z 40"),
    "bushes_hook": ("#b8863b", None, "铜套 ×2"),
    "hook": ("#4b5563", None, "旋梭"),
    "bobbin_case": ("#9ca3af", None, "梭芯套"),
    "pulley_lower": ("#6b8fb3", None, "下带轮 32 齿"),
    "belt": ("#222222", None, "同步带 570-3M-15"),
}

d = Path(sys.argv[1])
sec = json.loads((d / "section.json").read_text())
R, vL = sec["rings"], sec["axis_v"]["lower"]
fig, ax = plt.subplots(figsize=(15, 5.2), dpi=150)
for k in ["casting"] + [k for k in STYLE if k != "casting"]:
    rings = R.get(k) or []
    if not rings:
        continue
    verts, codes = [], []
    for r in rings:
        verts += r + [r[0]]
        codes += [MPath.MOVETO] + [MPath.LINETO] * (len(r) - 1) + [MPath.CLOSEPOLY]
    fc, hatch, _ = STYLE[k]
    ax.add_patch(PathPatch(MPath(verts, codes), facecolor=fc, edgecolor="#374151", lw=0.5, hatch=hatch, zorder=1 if k == "casting" else 3))
for v, name in ((0.0, "旋梭轴轴线"), (vL, "下轴轴线")):
    ax.plot([-20, 400], [v, v], color="#9b1c1c", lw=0.6, ls=(0, (12, 3, 2, 3)), zorder=4)
LAB = [("hook", -8, -30), ("bobbin_case", 18, -30), ("bushes_hook", 42, -30), ("hook_shaft", 66, -30), ("gear_hook", 96, -30),
       ("gear_lower", 62, 66), ("bearings_lower", 118, 66), ("lower_shaft", 200, 60), ("pulley_lower", 330, 66),
       ("belt", 335, -12)]
anchor = {"hook": (3, -12), "bobbin_case": (12, -2), "bushes_hook": (40, -8), "hook_shaft": (66, 0), "gear_hook": (78, -6),
          "gear_lower": (76, vL + 18), "bearings_lower": (97, vL + 14), "lower_shaft": (200, vL), "pulley_lower": (350, vL + 14),
          "belt": (348, vL - 18)}
for k, x, y in LAB:
    ax.annotate(STYLE[k][2], anchor[k], (x, y), fontsize=8.5, color=INK, ha="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6), zorder=5)
ax.annotate("机座（下件）HT250；x 300 横筋上 Ø34 孔让下轴穿过", (303, vL + 40), (220, vL + 50), fontsize=8.5, color=INK, ha="center",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
ax.set_aspect("equal")
ax.set_xlim(-30, 420)
ax.set_ylim(-40, vL + 70)
ax.invert_yaxis()
ax.set_xlabel("x（mm，向右为手轮一侧）", color=MUTED, fontsize=9)
ax.set_ylabel("剖面内距旋梭轴（mm）", color=MUTED, fontsize=9)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.tick_params(colors=MUTED, labelsize=8)
fig.suptitle("WQ-LS 旋梭组剖视：剖面过旋梭轴、下轴两条轴线（φ = 0），机座剖面打斜线", color=INK, fontsize=11, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(sys.argv[2])
print("ok", sys.argv[2])
