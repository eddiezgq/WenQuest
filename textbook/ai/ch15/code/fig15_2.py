"""15.2 节的示意图。

图 15.2.1：（a）Baird 的七状态反例：离策略 + 自举 + 函数逼近三件事凑在一起，权重飞到十万；
冻住自举的那一份（目标网络）或改成同策略取样，就不飞了。
（b）表格 Q 学习：试得越多越接近价值迭代算出来的答案，但停在一个噪声底上。
"""
import numpy as np

from _ch15 import baird, q_learning, shop_mdp, value_iteration
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

fig, (a, b) = plt.subplots(1, 2, figsize=(11.2, 4.0))

for name, kw, col in ((T("三件事齐了", "all three ingredients"), {}, C["x"]),
                      (T("冻住自举的那一份（目标网络）", "frozen bootstrap (target network)"), {"target_every": 200}, C["z"]),
                      (T("改成同策略取样", "on-policy sampling"), {"on_policy": True}, C["y"])):
    h, _ = baird(steps=3000, **kw)
    a.semilogy(h, color=col, lw=1.8, label=name)
a.set_xlabel(T("更新次数", "updates"))
a.set_ylabel(T("权重的范数（真实价值全是 0）", "norm of the weights (true value is 0)"))
a.set_title(T("(a) 价值不是估不准，是飞了", "(a) Not inaccurate — divergent"), fontsize=10)
a.legend(fontsize=8)
a.grid(alpha=0.25, lw=0.5, which="both")

P, R, idx, g, start, goal = shop_mdp()
V, pi, _, _ = value_iteration(P, R, 0.95)
for alpha, col in ((0.5, C["x"]), (0.2, C["z"]), (0.05, C["y"])):
    curves = []
    for sd in range(3):                                   # 三个随机种子取平均，曲线才看得出趋势
        _, curve = q_learning(P, R, 0.95, alpha=alpha, steps=400_000, goal=idx[goal], seed=sd, every=2000)
        curves.append(np.sqrt(((curve - V) ** 2).mean(1)))      # 均方根误差：比最大差平稳得多
    err = np.mean(curves, axis=0)
    xs = (np.arange(len(err)) + 1) * 2000
    b.loglog(xs, err, color=col, lw=1.8, label=T(f"步长 α = {alpha}", f"step size α = {alpha}"))
b.set_xlabel(T("试了多少步", "environment steps"))
b.set_ylabel(T("与最优价值的均方根差", "RMS error vs the optimal value"))
b.set_title(T("(b) 步长越小，停得越低，也走得越慢", "(b) A smaller step size settles lower and slower"), fontsize=10)
b.legend(fontsize=8)
b.grid(alpha=0.25, lw=0.5, which="both")

fig.tight_layout()
figure(fig, "fig15_2_1")
