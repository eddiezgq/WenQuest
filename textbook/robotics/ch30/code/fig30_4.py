"""30.4 节的示意图。

图 30.4.1：(a) 零件库里机械臂的负载与臂展（厂商参数，对数坐标）：协作机器人、工业机器人；阴影是部件装配工位的要求
          （负载 ≥ 5 kg、臂展 ≥ 0.76 m），虚线是搬第二级大齿轮 GR-302 所需的负载；
          (b) 机器人厂清单里一台 WQ-CR5 的材料费构成（逐层加起来）。
"""
import numpy as np

from _ch30 import COBOTS, GRIPPER_KG, bom_rollup, library_arms
from bookout import COLORS as C, T, figure, style

plt = style()
arms = [a for a in library_arms() if a["payload_kg"] and a["reach_mm"]]
fig, axs = plt.subplots(1, 2, figsize=(11.8, 4.4), gridspec_kw={"width_ratios": [1.25, 1]})
ax = axs[0]
ax.fill_between([759, 1500], 5, 30, color=C["y"], alpha=0.1)
ax.axhline(11.0 + GRIPPER_KG, color=C["x"], lw=0.9, ls="--")
ax.text(370, 12.6, T("搬 GR-302 要 ≈12 kg", "GR-302 needs ≈12 kg"), fontsize=8, color=C["x"])
for a in arms:
    co = a["id"] in COBOTS
    me = a["id"] == "B-ARM-WQCR5"
    ax.plot(a["reach_mm"], a["payload_kg"], "*" if me else ("o" if co else "s"), ms=12 if me else 6,
            color=C["accent"] if me else (C["z"] if co else C["muted"]), alpha=0.9)
    off = {"B-ARM-WQCR5": (-50, -14), "B-ARM-UR10E": (5, 4), "B-ARM-IRB1200": (-70, 6), "B-ARM-FR3": (6, -10)}
    if a["id"] in off:
        ax.annotate(a["model"], (a["reach_mm"], a["payload_kg"]), xytext=off[a["id"]], textcoords="offset points", fontsize=7.5)
ax.plot([], [], "o", color=C["z"], label=T("协作机器人", "collaborative robots"))
ax.plot([], [], "s", color=C["muted"], label=T("工业机器人（要围栏）", "industrial robots (need guarding)"))
ax.plot([], [], "*", color=C["accent"], ms=10, label="WQ-CR5")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(300, 4000)
ax.set_ylim(0.4, 1000)
ax.set_xlabel(T("臂展 / mm", "reach / mm"))
ax.set_ylabel(T("额定负载 / kg", "rated payload / kg"))
ax.legend(fontsize=8, frameon=False, loc="upper left")
ax.set_title(T("(a) 零件库里的机械臂与工位的要求", "(a) the library's arms and the station's needs"), fontsize=11)

ax = axs[1]
parts, total = bom_rollup("WQ-CR5")
lab = {"WQJ-L": T("大关节模组 ×2", "large joint modules ×2"), "WQJ-M": T("中关节模组", "medium joint module"),
       "WQJ-S": T("小关节模组 ×3", "small joint modules ×3"), "CTRL-CAB": T("控制柜", "controller cabinet"),
       "ARM-UP": T("大臂", "upper arm"), "ARM-FO": T("小臂", "forearm"), "BASE-CR5": T("底座", "base"),
       "CABLE-ARM": T("线束", "cable harness"), "SCR-M5x16": T("螺钉", "screws")}
items = sorted(parts.items(), key=lambda kv: kv[1])
ax.barh(range(len(items)), [v for _, v in items], color=C["z"], alpha=0.8)
for i, (k, v) in enumerate(items):
    ax.text(v + 60, i, f"{v:,.0f}（{v / total * 100:.0f}%）" if T("中", "") else f"{v:,.0f} ({v / total * 100:.0f}%)", va="center", fontsize=8)
ax.set_yticks(range(len(items)), [lab[k] for k, _ in items])
ax.set_xlim(0, max(parts.values()) * 1.45)
ax.set_xlabel(T("材料费 / 美元（示例）", "material cost / USD (example)"))
ax.set_title(T("(b) 一台 WQ-CR5 的材料费", "(b) material cost of one WQ-CR5"), fontsize=11)
fig.tight_layout()
figure(fig, "fig30_4_1")
