"""图 24.2.1：域随机化范围的倒 U 形——**仿真与真机两条线**。

横轴是随机化范围（0 = 只在标称仿真里训），两条线分别是在标称仿真参数上的成功率
与在真机参数上的成功率。范围 0 那一端最要紧：仿真里八成多，真机上是零。
"""
import numpy as np

from _ch24 import (DEGREE, REAL, SIM, evaluate, make_policy, randomized_world,
                   sample_starts, sample_targets, train_policy)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
SCALES = (0.0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0, 1.3)
N_EPISODES, N_TEST = 160, 80

test_poses = sample_targets(N_TEST, seed=11)
test_starts = sample_starts(N_TEST, seed=11, spread=0.25)

sim_s, real_s = [], []
for scale in SCALES:
    def world_of(i, g, s=scale):
        return SIM if s == 0.0 else randomized_world(SIM, s, g)

    W = train_policy(N_EPISODES, rounds=4, world_of=world_of, seed=0)
    pol = (lambda p, w: make_policy(W, DEGREE))
    sim_s.append(evaluate(pol, test_poses, test_starts, SIM, seed=7)["success_pct"])
    real_s.append(evaluate(pol, test_poses, test_starts, REAL, seed=7)["success_pct"])
sim_s = np.array(sim_s)
real_s = np.array(real_s)
xs = np.array(SCALES)
i_best = int(np.argmax(real_s))

fig, ax = plt.subplots(figsize=(7.2, 4.6))
ax.plot(xs, sim_s, "s--", color=C["z"], lw=2.0, ms=6,
        label=T("仿真成功率（标称参数，80 次）", "success in simulation (nominal, 80 trials)"))
ax.plot(xs, real_s, "o-", color=C["x"], lw=2.4, ms=7,
        label=T("真机成功率（真机参数，80 次）", "success on the “real” robot (80 trials)"))
ax.plot(xs[i_best], real_s[i_best], "o", color=C["x"], ms=13, mfc="none", mew=2)

ax.annotate(T(f"不随机化：仿真 {sim_s[0]:.0f}%、真机 {real_s[0]:.0f}%",
              f"no randomization: sim {sim_s[0]:.0f}%, real {real_s[0]:.0f}%"),
            xy=(xs[0], real_s[0]), xytext=(34, 30), textcoords="offset points",
            fontsize=9, color=C["x"],
            arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.2))
ax.annotate(T(f"最好的范围 {xs[i_best]:.2f}：真机 {real_s[i_best]:.0f}%",
              f"best range {xs[i_best]:.2f}: real {real_s[i_best]:.0f}%"),
            xy=(xs[i_best], real_s[i_best]), xytext=(46, -78), textcoords="offset points",
            fontsize=9, color=C["x"],
            arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.2))
ax.annotate(T(f"范围太宽：两列一起掉（仿真 {sim_s[-1]:.0f}%、真机 {real_s[-1]:.0f}%）",
              f"too wide: both columns fall (sim {sim_s[-1]:.0f}%, real {real_s[-1]:.0f}%)"),
            xy=(xs[-1], sim_s[-1]), xytext=(-8, -40), textcoords="offset points",
            ha="right", fontsize=9, color=C["muted"],
            arrowprops=dict(arrowstyle="->", color=C["muted"], lw=1.2))
ax.axvspan(xs[max(i_best - 1, 0)], xs[min(i_best + 2, len(xs) - 1)], color=C["accent"], alpha=0.10)
ax.set_xlabel(T("域随机化范围（0 = 只在标称仿真里训）",
                "domain-randomization range (0 = nominal simulation only)"))
ax.set_ylabel(T("任务成功率（%）", "task success rate (%)"))
ax.set_ylim(-6, 108)
ax.set_title(T("域随机化：太窄盖不住真机，太宽两列一起掉",
                "domain randomization: too narrow misses the robot, too wide hurts both"),
             fontsize=10.5)
ax.legend(fontsize=8.5, loc="lower center", framealpha=0.92)
ax.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
figure(fig, "fig24_2_1")
