"""图 24.1.1：纯克隆对带纠正的（DAgger 玩具版）。

（a）离专家轨迹的偏差随步数怎么走——两条都是**先涨后饱和**，要紧的是饱和在哪里
    （2 cm 判据那条横线是生死线）；（b）同样 120 回合的专家标注，成功率差一个数量级。
"""
import numpy as np

from _ch24 import (DEGREE, GRASP_TOL, SIM, collect, deviation_curve, evaluate, expert,
                   fit_ls, make_policy, poly_features, sample_starts, sample_targets)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_EPISODES, ROUNDS, N_TEST, STEPS_CURVE = 120, 4, 80, 60

test_poses = sample_targets(N_TEST, seed=11)
test_starts = sample_starts(N_TEST, seed=11, spread=0.30)

demo_poses = sample_targets(N_EPISODES, seed=2)
demo_starts = sample_starts(N_EPISODES, seed=2, spread=0.05)
O_bc, A_bc = collect(lambda p, w: expert(p, w), demo_poses, demo_starts, SIM, seed=0)
W_bc = fit_ls(poly_features(O_bc, DEGREE), A_bc)

per = N_EPISODES // ROUNDS
Os, As = [], []
O0, A0 = collect(lambda p, w: expert(p, w), demo_poses[:per], demo_starts[:per], SIM, seed=0)
Os.append(O0)
As.append(A0)
W_dg = fit_ls(poly_features(O0, DEGREE), A0)
rounds_succ = [evaluate(lambda p, w: make_policy(W_dg, DEGREE), test_poses, test_starts,
                        SIM, seed=7)["success_pct"]]
for rnd in range(ROUNDS - 1):
    pp = sample_targets(per, seed=30 + rnd)
    ss = sample_starts(per, seed=30 + rnd, spread=0.30)
    cur = W_dg.copy()
    O2, A2 = collect(lambda p, w, Wc=cur: make_policy(Wc, DEGREE), pp, ss, SIM, seed=rnd)
    Os.append(O2)
    As.append(A2)
    W_dg = fit_ls(poly_features(np.vstack(Os), DEGREE), np.vstack(As))
    rounds_succ.append(evaluate(lambda p, w: make_policy(W_dg, DEGREE), test_poses,
                                test_starts, SIM, seed=7)["success_pct"])

succ_bc = evaluate(lambda p, w: make_policy(W_bc, DEGREE), test_poses, test_starts,
                   SIM, seed=7)["success_pct"]
dev_bc = deviation_curve(lambda p, w: make_policy(W_bc, DEGREE), test_poses[:40],
                         test_starts[:40], SIM, seed=7, steps=STEPS_CURVE)
dev_dg = deviation_curve(lambda p, w: make_policy(W_dg, DEGREE), test_poses[:40],
                         test_starts[:40], SIM, seed=7, steps=STEPS_CURVE)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 偏差随步数
t = np.arange(STEPS_CURVE + 1)
a.plot(t, dev_bc * 100, color=C["x"], lw=2.2, label=T("纯克隆（120 条演示）", "pure cloning (120 demos)"))
a.plot(t, dev_dg * 100, color=C["z"], lw=2.2, label=T("带纠正的（30 条 + 3 轮纠正）",
                                                      "with corrections (30 + 3 rounds)"))
a.axhline(GRASP_TOL["pos_m"] * 100, color=C["accent"], lw=1.4, ls="--")
a.annotate(T("2 cm 判据：饱和在这条线上面的，几乎每次都抓空",
             "2 cm criterion: plateau above this line means missing almost every time"),
           xy=(STEPS_CURVE * 0.97, GRASP_TOL["pos_m"] * 100), xytext=(0, 6),
           textcoords="offset points", ha="right", fontsize=8.5, color=C["accent"])
a.annotate(T(f"纯克隆饱和在 {dev_bc[-1] * 100:.1f} cm", f"cloning plateaus at {dev_bc[-1] * 100:.1f} cm"),
           xy=(STEPS_CURVE, dev_bc[-1] * 100), xytext=(-18, 14), textcoords="offset points",
           ha="right", fontsize=9, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.1))
a.annotate(T(f"带纠正的 {dev_dg[-1] * 100:.1f} cm", f"with corrections {dev_dg[-1] * 100:.1f} cm"),
           xy=(STEPS_CURVE, dev_dg[-1] * 100), xytext=(-18, -26), textcoords="offset points",
           ha="right", fontsize=9, color=C["z"],
           arrowprops=dict(arrowstyle="->", color=C["z"], lw=1.1))
a.set_xlabel(T("步数（0.05 s 一步）", "step (0.05 s each)"))
a.set_ylabel(T("离专家轨迹的偏差（cm）", "deviation from the expert path (cm)"))
a.set_title(T("(a) 偏差先涨后饱和，不是一路超线性涨上去",
              "(a) deviation grows, then saturates — it is not superlinear all the way"),
            fontsize=10)
a.set_ylim(0, max(dev_bc.max(), dev_dg.max()) * 100 * 1.45)
a.legend(fontsize=8.5, loc="upper left", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 成功率
xs = np.arange(ROUNDS)
b.plot(xs, rounds_succ, "o-", color=C["z"], lw=2.2, ms=7,
       label=T("带纠正的（每轮重拟合）", "with corrections (refit each round)"))
b.axhline(succ_bc, color=C["x"], lw=2.2, ls="--",
          label=T("纯克隆（同样 120 回合标注）", "pure cloning (same 120 labelled episodes)"))
for i, s in enumerate(rounds_succ):
    b.annotate(f"{s:.1f}%", xy=(i, s), xytext=(10 if i == 0 else 0, 8),
               textcoords="offset points", ha="center", fontsize=8.5, color=C["z"])
b.annotate(T(f"纯克隆 {succ_bc:.1f}%", f"cloning {succ_bc:.1f}%"),
           xy=(2.95, succ_bc), xytext=(0, 7), textcoords="offset points",
           ha="right", fontsize=9, color=C["x"])
b.set_xticks(xs)
b.set_xticklabels([T("只有演示", "demos only")] +
                  [T(f"第 {i} 轮纠正", f"correction {i}") for i in range(1, ROUNDS)], fontsize=9)
b.set_ylabel(T("任务成功率（%，试 80 次）", "task success rate (%, 80 trials)"))
b.set_ylim(-6, max(rounds_succ) * 1.35 + 6)
b.set_title(T("(b) 差别不在算法，在数据采在谁走出来的状态上",
              "(b) the difference is whose states the data comes from"), fontsize=10)
b.annotate(T("专家标注预算完全相同：120 回合", "identical labelling budget: 120 episodes"),
           xy=(0.40, 0.03), xycoords="axes fraction", ha="center", fontsize=8.5, color=C["accent"])
b.legend(fontsize=8.5, loc="upper left", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5, axis="y")

fig.tight_layout()
figure(fig, "fig24_1_1")
