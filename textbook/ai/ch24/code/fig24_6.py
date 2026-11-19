"""图 24.6.1：并行环境数买到了什么。

左轴：达标所需的**迭代轮数**（环境数越多，轮数越少）；
右轴：达标所需的**总环境步数**（环境数越多，步数越多）。
两条线一降一升，就是并行仿真的全部账：**买的是等待的轮数，付的是算力**。
**墙钟时间与吞吐一个字不编**——要换算时间得有四样齐全的公开值（见算例 24.6 的引用）。
"""
import numpy as np

from _ch24 import SIM, evaluate, rollout, sample_starts, sample_targets, servo_policy
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_ENVS = (1, 2, 4, 8, 16, 32)
SEEDS, TARGET, MAX_ITER, N_HOLDOUT = 6, 60.0, 60, 40
P0 = np.array([0.25, 0.25, 1.0])
STEP_SIGMA = np.array([0.05, 0.05, 0.8])

ho_poses = sample_targets(N_HOLDOUT, seed=11)
ho_starts = sample_starts(N_HOLDOUT, seed=11, spread=0.25)


def holdout(p):
    return evaluate(lambda ps, w: servo_policy(gain=p[2], l1_hat=p[0], l2_hat=p[1]),
                    ho_poses, ho_starts, SIM, seed=7)["success_pct"]


def train(n_envs, seed):
    g = np.random.default_rng(seed + 7)
    p = P0.copy()
    steps = 0

    def est(par, it):
        nonlocal steps
        poses = sample_targets(n_envs, seed=1000 + it * 13)
        starts = sample_starts(n_envs, seed=1000 + it * 13, spread=0.25)
        s = 0
        for k in range(n_envs):
            r = rollout(servo_policy(gain=par[2], l1_hat=par[0], l2_hat=par[1]),
                        poses[k], starts[k], SIM, seed=k + it * 31)
            steps += r["n_steps"]
            s += r["success"]
        return s / n_envs * 100

    cur = est(p, 0)
    for it in range(1, MAX_ITER + 1):
        cand = p + STEP_SIGMA * g.normal(0, 1, 3)
        cand[2] = abs(cand[2])
        cand[:2] = np.clip(cand[:2], 0.05, 0.8)
        sc = est(cand, it)
        if sc >= cur:
            p, cur = cand, sc
        if holdout(p) >= TARGET:
            return it, steps
    return MAX_ITER, steps


iters, steps_all = [], []
for n in N_ENVS:
    r = [train(n, seed=sd * 17) for sd in range(SEEDS)]
    iters.append(float(np.median([x[0] for x in r])))
    steps_all.append(float(np.median([x[1] for x in r])))
iters = np.array(iters)
steps_all = np.array(steps_all)
xs = np.array(N_ENVS, dtype=float)

fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.semilogx(xs, iters, "o-", color=C["z"], lw=2.4, ms=7, base=2,
            label=T("达标所需的迭代轮数", "policy updates needed"))
ax.set_xlabel(T("并行环境数（每轮用多少个回合估成绩）",
                "parallel environments (episodes per update)"))
ax.set_ylabel(T("迭代轮数（6 个种子的中位数）", "updates (median of 6 seeds)"), color=C["z"])
ax.tick_params(axis="y", labelcolor=C["z"])
ax.set_xticks(xs)
ax.set_xticklabels([str(int(x)) for x in xs], fontsize=9)
ax.set_ylim(0, max(iters) * 1.35)

ax2 = ax.twinx()
ax2.semilogy(xs, steps_all, "s--", color=C["x"], lw=2.4, ms=7, base=2,
             label=T("达标所需的总环境步数", "total environment steps needed"))
ax2.set_ylabel(T("总环境步数（对数轴）", "total environment steps (log axis)"), color=C["x"])
ax2.tick_params(axis="y", labelcolor=C["x"])

ax.annotate(T(f"1 个环境：{iters[0]:.0f} 轮、{steps_all[0]:,.0f} 步",
              f"1 env: {iters[0]:.0f} updates, {steps_all[0]:,.0f} steps"),
            xy=(xs[0], iters[0]), xytext=(18, 16), textcoords="offset points",
            fontsize=9, color=C["z"],
            arrowprops=dict(arrowstyle="->", color=C["z"], lw=1.2))
ax.annotate(T(f"{int(xs[-1])} 个环境：轮数少 {iters[0] / iters[-1]:.1f} 倍，"
              f"步数多 {steps_all[-1] / steps_all[0]:.0f} 倍",
              f"{int(xs[-1])} envs: {iters[0] / iters[-1]:.1f}× fewer updates, "
              f"{steps_all[-1] / steps_all[0]:.0f}× more steps"),
            xy=(xs[-1], iters[-1]), xytext=(-10, -56), textcoords="offset points",
            ha="right", fontsize=9, color=C["accent"],
            arrowprops=dict(arrowstyle="->", color=C["accent"], lw=1.2))
ax.set_title(T("并行环境买的是等待的轮数，付的是算力——收益递减",
                "parallel envs buy waiting time and pay in compute — with diminishing returns"),
             fontsize=10.5)
lines = ax.get_lines()[:1] + ax2.get_lines()[:1]
ax.legend(lines, [ln.get_label() for ln in lines], fontsize=8.5, loc="lower left",
          framealpha=0.92)
ax.grid(alpha=0.25, lw=0.5, which="both")
fig.tight_layout()
figure(fig, "fig24_6_1")
