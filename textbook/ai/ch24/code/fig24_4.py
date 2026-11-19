"""图 24.4.1：奖励塑形的副作用——累计奖励与真实成功率两条**背离**的线。

横轴是塑形项的权重。左轴是“搜出来的最优策略”的累计奖励（一路上升），
右轴是同一个策略的真实任务成功率（过了临界权重掉到 0）。
阴影区里最优行为是**贴着工件来回转、永不闭合夹爪**——这就是刷奖励。
"""
import numpy as np

from _ch24 import SIM, rollout, sample_starts, sample_targets, servo_policy
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
D0, TASK_BONUS = 0.03, 20.0
WEIGHTS = (0.0, 0.1, 0.2, 0.4, 0.8, 1.0, 1.2, 1.6, 2.4)
CLOSE_AT = (0.0, 0.006, 0.012, 0.020)
HOVER = (0.0, 0.4, 0.9)
N_EP = 40

poses = sample_targets(N_EP, seed=21)
starts = sample_starts(N_EP, seed=21, spread=0.25)


def run(close_at, hover, w):
    rew, suc = [], []
    for k, (pose, q0) in enumerate(zip(poses, starts)):
        r = rollout(servo_policy(gain=3.5, close_at=close_at, hover=hover),
                    pose, q0, SIM, seed=k + 5)
        n = r["n_steps"]
        d = np.linalg.norm(r["tip"][1:n + 1, :2] - pose[:2], axis=1)
        rew.append(w * float(np.exp(-d / D0).sum()) + (TASK_BONUS if r["success"] else 0.0))
        suc.append(r["success"])
    return float(np.mean(rew)), float(np.mean(suc)) * 100


best_rew, best_succ, farm = [], [], []
for w in WEIGHTS:
    cand = [(*run(c, h, w), c) for c in CLOSE_AT for h in HOVER]
    cand.sort(key=lambda z: -z[0])
    best_rew.append(cand[0][0])
    best_succ.append(cand[0][1])
    farm.append(cand[0][2] == 0.0)
best_rew = np.array(best_rew)
best_succ = np.array(best_succ)
xs = np.array(WEIGHTS)
i_farm = int(np.argmax(farm))

fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.plot(xs, best_rew, "o-", color=C["y"], lw=2.4, ms=7,
        label=T("累计奖励（搜出来的最优策略）", "cumulative reward (best policy found)"))
ax.set_xlabel(T("塑形项权重 w（每步奖励 w·e^(−d/3 cm)）",
                "shaping weight w (per-step reward w·e^(−d/3 cm))"))
ax.set_ylabel(T("平均累计奖励", "mean cumulative reward"), color=C["y"])
ax.tick_params(axis="y", labelcolor=C["y"])
ax.axvspan(xs[i_farm] - 0.1, xs[-1] + 0.1, color=C["x"], alpha=0.07)

ax2 = ax.twinx()
ax2.plot(xs, best_succ, "s--", color=C["x"], lw=2.4, ms=7,
         label=T("真实任务成功率（试 40 次）", "true task success rate (40 trials)"))
ax2.set_ylabel(T("真实任务成功率（%）", "true task success rate (%)"), color=C["x"])
ax2.tick_params(axis="y", labelcolor=C["x"])
ax2.set_ylim(-6, 108)

ax2.annotate(T(f"w ≥ {xs[i_farm]:.1f}：最优行为变成\n“贴着工件转、永不闭合夹爪”\n"
               f"——奖励 {best_rew[i_farm]:.0f}，成功率 {best_succ[i_farm]:.0f}%",
               f"w ≥ {xs[i_farm]:.1f}: the best policy now hovers\nand never closes the gripper\n"
               f"— reward {best_rew[i_farm]:.0f}, success {best_succ[i_farm]:.0f}%"),
             xy=(xs[i_farm], best_succ[i_farm]), xytext=(-112, 128), textcoords="offset points",
             ha="center", fontsize=9, color=C["x"],
             arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.3))
ax.annotate(T(f"不加塑形：奖励 {best_rew[0]:.1f}，成功率 {best_succ[0]:.0f}%",
              f"no shaping: reward {best_rew[0]:.1f}, success {best_succ[0]:.0f}%"),
            xy=(xs[0], best_rew[0]), xytext=(250, 26), textcoords="offset points",
            ha="center", fontsize=9, color=C["y"],
            arrowprops=dict(arrowstyle="->", color=C["y"], lw=1.2))
ax.set_title(T("塑形权重一过临界值，两条线就分道扬镳",
                "past a critical weight the two curves part ways"), fontsize=10.5)
lines = ax.get_lines()[:1] + ax2.get_lines()[:1]
ax.legend(lines, [ln.get_label() for ln in lines], fontsize=8.5, loc="upper left",
          framealpha=0.92)
ax.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
figure(fig, "fig24_4_1")
