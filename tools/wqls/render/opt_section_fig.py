"""画 G4.8 针板下面的剖面（opt_section.py 导出的 opt_section.json）。

    python3 tools/wqls/render/opt_section_fig.py <零件目录> <输出 PNG>
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
INK, MUTED = "#1f2328", "#6b7280"
STYLE = {"casting": ("#d9dce1", "///"), "feed_bar": ("#6f9fd4", None), "hook": ("#8fa3b8", None), "bobbin_case": ("#b8c2cc", None),
         "fixed_knife": ("#4b5563", None), "moving_knife": ("#d98a2b", None), "knife_shaft": ("#d98a2b", None), "trim_base": ("#8fa3b8", None)}
TITLE = {"120": "动刀在最后（φ 120°，平时缝纫也停在这里）", "0": "动刀在最前（φ 340°–20° 钩住线）"}
LAB = [("moving_knife", "动刀"), ("feed_bar", "送布牙排")]

d = Path(sys.argv[1])
sec = json.loads((d / "opt_section.json").read_text())
fig, axs = plt.subplots(1, 2, figsize=(13, 6.4), dpi=150)
for ax, key in zip(axs, ("120", "0")):
    R = sec["cuts"][key]
    for k in ["casting", "hook", "bobbin_case", "feed_bar", "trim_base", "fixed_knife", "knife_shaft", "moving_knife"]:
        rings = R.get(k)
        if not rings:
            continue
        verts, codes = [], []
        for i, r in enumerate(rings):
            depth = sum(1 for j, o in enumerate(rings) if j != i and MPath(o).contains_point(r[0]))
            area = sum(r[q][0] * r[q - 1][1] - r[q - 1][0] * r[q][1] for q in range(len(r)))
            if (area < 0) != (depth % 2 == 1):
                r = r[::-1]
            verts += r + [r[0]]
            codes += [MPath.MOVETO] + [MPath.LINETO] * (len(r) - 1) + [MPath.CLOSEPOLY]
        fc, hatch = STYLE[k]
        if k in ("hook", "bobbin_case", "fixed_knife"):        # 不在刀片平面上：画轮廓（旋梭在下面、定刀在上面）
            ax.add_patch(PathPatch(MPath(verts, codes), facecolor="none", edgecolor=fc if k != "fixed_knife" else "#111827",
                                   lw=1.4, ls=(0, (4, 2)), zorder=5))
            continue
        ax.add_patch(PathPatch(MPath(verts, codes), facecolor=fc, edgecolor="#374151", lw=0.5, hatch=hatch, alpha=0.95))
    ax.plot([0], [0], marker="+", ms=14, color="#9b1c1c", mew=1.2)
    ax.annotate("针", (0, 0), (2.5, -3.5), color="#9b1c1c", fontsize=9)
    ax.set_aspect("equal")
    ax.set_xlim(-30, 30)
    ax.set_ylim(-22, 48)
    ax.set_title(TITLE[key], loc="left", fontsize=10, color=INK)
    ax.set_xlabel("x（mm）", color=MUTED, fontsize=8.5)
    ax.set_ylabel("y（mm，往后为正）", color=MUTED, fontsize=8.5)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=7.5)
handles = [plt.Rectangle((0, 0), 1, 1, fc=STYLE[k][0], ec="#374151") for k, _ in LAB] + [plt.Rectangle((0, 0), 1, 1, fc="#d9dce1", hatch="///", ec="#374151"),
           plt.Line2D([], [], color="#111827", ls=(0, (4, 2)), lw=1.4), plt.Line2D([], [], color=STYLE["hook"][0], ls=(0, (4, 2)), lw=1.4)]
fig.legend(handles, [t for _, t in LAB] + ["机座（剖面）", "定刀（针板底面，在刀片上面）", "旋梭（在刀片下面）"], loc="lower center", ncol=5, frameon=False, fontsize=9)
fig.suptitle(f"WQ-LS 自动剪线：针板下面的剖面（z {sec['z']}，刀片平面），从上往下看", x=0.01, ha="left", fontsize=11, color=INK)
fig.tight_layout(rect=(0, 0.06, 1, 0.95))
fig.savefig(sys.argv[2])
print("ok", sys.argv[2])
