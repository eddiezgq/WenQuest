"""30.3 节的示意图。

图 30.3.1：(a) 臂展不变（a2 + a3 = 0.76 m），大臂长 a2 从 0.30 m 到 0.50 m：J2、J3 的最大重力矩（带 5 kg 负载）与肩部死区 |a2 − a3|，
          灰线是 J1 模组的半径；(b) 按 design() 选出的关节模组：每个关节峰值、连续需求占模组能力的比例（含 1.2 倍安全系数）。
"""
import numpy as np

from _ch30 import wqcr5
from bookout import COLORS as C, T, figure, style

plt = style()
W = wqcr5()
S = abs(W.DH[1]["a"]) + abs(W.DH[2]["a"])
a2s = np.round(np.arange(0.30, 0.501, 0.01), 3)
g2, g3 = [], []
for a2 in a2s:
    with W.geometry(a2, S - a2):
        g, _ = W.worst_case(W.PAYLOAD_KG, step_deg=45.0)
    g2.append(g[1])
    g3.append(g[2])
fig, axs = plt.subplots(1, 2, figsize=(11.8, 4.2))
ax = axs[0]
ax.plot(a2s, g2, color=C["x"], lw=1.6, label=T("J2 最大重力矩", "J2 largest gravity torque"))
ax.plot(a2s, g3, color=C["z"], lw=1.6, label=T("J3 最大重力矩", "J3 largest gravity torque"))
ax.set_xlabel(T("大臂长 a2 / m（小臂 a3 = 0.76 − a2）", "upper arm a2 / m (forearm a3 = 0.76 − a2)"))
ax.set_ylabel(T("力矩 / (N·m)", "torque / (N·m)"))
ax.set_ylim(0, 110)
ax2 = ax.twinx()
ax2.plot(a2s, np.abs(2 * a2s - S) * 100, color=C["accent"], lw=1.2, ls="--", label=T("肩部死区 |a2 − a3|", "shoulder hole |a2 − a3|"))
ax2.axhline(W.MODULES["L"]["r"] * 100, color=C["muted"], lw=0.8)
ax2.text(0.305, W.MODULES["L"]["r"] * 100 + 0.4, T("J1 模组半径 5.5 cm", "J1 module radius 5.5 cm"), fontsize=8, color=C["muted"])
ax2.set_ylabel(T("死区半径 / cm", "hole radius / cm"))
ax2.set_ylim(0, 25)
ax.axvline(0.40, color=C["ink"], lw=0.8, ls=":")
ax.text(0.402, 104, "WQ-CR5", fontsize=8)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, fontsize=8, frameon=False, loc="lower right")
ax.set_title(T("(a) 大臂、小臂怎样分", "(a) splitting the reach"), fontsize=11)

ax = axs[1]
d = W.design()
J = d["joints"]
x = np.arange(6)
ax.bar(x - 0.18, [j["use_peak"] * 100 for j in J], 0.36, color=C["x"], alpha=0.8, label=T("峰值需求 / 模组峰值能力", "peak need / module peak"))
ax.bar(x + 0.18, [j["use_rms"] * 100 for j in J], 0.36, color=C["z"], alpha=0.8, label=T("连续需求 / 模组额定能力", "continuous need / module rating"))
ax.axhline(100, color=C["muted"], lw=0.8)
ax.set_xticks(x, [j["joint"] + "\n" + j["module"] for j in J])
ax.set_ylim(0, 125)
ax.set_ylabel(T("利用率 / %（含 1.2 倍安全系数）", "utilisation / % (safety factor 1.2)"))
ax.legend(fontsize=8, frameon=False, loc="upper right")
ax.set_title(T("(b) 每个关节选的模组", "(b) the module chosen for each joint"), fontsize=11)
fig.tight_layout()
figure(fig, "fig30_3_1")
