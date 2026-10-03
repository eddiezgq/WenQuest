"""图 1.1.1：左，负载力矩对负载的比例与叠加；右，力矩对关节角不成比例（抬到 60° 的减少量不是抬到 30° 的两倍）。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
import ex1_1_data as d

fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.8))
names = [T("1 kg", "1 kg"), T("2 kg", "2 kg"), T("1 kg + 2 kg", "1 kg + 2 kg")]
a1.bar([0, 1], [d.t1, d.t2], color=[BLUE, GREEN], width=0.6)
a1.bar([2], [d.t1], color=BLUE, width=0.6)
a1.bar([2], [d.t2], bottom=[d.t1], color=GREEN, width=0.6)
a1.set_xticks([0, 1, 2], names)
a1.set_ylabel(T("肩关节力矩 / (N·m)", "shoulder torque / (N·m)"))
a1.set_title(T("对负载：成比例，可叠加", "In the load: proportional and additive"), fontsize=12)
th = np.linspace(0, 90, 181)
a2.plot(th, [2 * 9.80665 * d.L * math.cos(math.radians(x)) for x in th], color=RED)
tau = lambda x: 2 * 9.80665 * d.L * math.cos(math.radians(x))
a2.scatter([0, 30, 60], [tau(0), tau(30), tau(60)], color=INK, zorder=3)
guess = tau(0) - 2 * (tau(0) - tau(30))
a2.plot([45, 75], [guess, guess], color=MUTED, ls="--", lw=1.2)
a2.annotate(T("若成比例，60° 时应在此", "if proportional, 60° would be here"), (75, guess), (52, guess + 2.2), fontsize=9, color=MUTED)
a2.set_ylim(0, 18)
a2.set_xlabel(T("手臂与水平面的夹角 θ / °", "arm angle above horizontal θ / °"))
a2.set_ylabel(T("2 kg 负载的力矩 / (N·m)", "torque of 2 kg / (N·m)"))
a2.set_title(T("对关节角：不成比例", "In the angle: not proportional"), fontsize=12)
for ax in (a1, a2):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig1_1_1")
