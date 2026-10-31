"""15.3 节的示意图。

图 15.3.1：（a）取木棍游戏上，蒙特卡洛树搜索的选对率随模拟次数上升——这个游戏有必胜策略，
所以"对不对"是能核对的；（b）一次搜索把模拟花在哪：三个候选里，它把大半压在最好的那一支上。
"""
import numpy as np

from _ch15 import TAKE, sticks_best, uct
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

fig, (a, b) = plt.subplots(1, 2, figsize=(11.2, 4.0))

sims_list = [5, 10, 20, 30, 50, 100, 200, 400, 1000]
acc = []
for sims in sims_list:
    ok = n = 0
    for k in range(5, 26):
        if k % 4 == 0:
            continue
        move, _, _, _ = uct(k, sims, g=np.random.default_rng(100 + k))
        ok += int(move == sticks_best(k))
        n += 1
    acc.append(ok / n * 100)
a.semilogx(sims_list, acc, "o-", color=C["z"], lw=1.8, ms=5)
a.axhline(100, color=C["muted"], ls="--", lw=1.0, label=T("必胜策略（解析解）", "the provably winning move"))
a.axhline(100 / 3, color=C["x"], ls=":", lw=1.0, label=T("瞎猜（三个候选）", "guessing among three"))
a.set_xlabel(T("每步跑多少次模拟", "simulations per move"))
a.set_ylabel(T("选对的比例（%）", "share of correct moves (%)"))
a.set_ylim(0, 108)
a.set_title(T("(a) 模拟次数一多，就搜得对了", "(a) More simulations, better moves"), fontsize=10)
a.legend(fontsize=8, loc="lower right")
a.grid(alpha=0.25, lw=0.5, which="both")

N0 = 13
move, acts, visits, wins = uct(N0, 1000, g=np.random.default_rng(7))
cols = [C["z"] if t == sticks_best(N0) else C["muted"] for t in acts]
b.bar([str(t) for t in acts], visits, color=cols)
for i, t in enumerate(acts):
    rate = wins[i] / max(visits[i], 1) * 100
    b.text(i, visits[i] + 12, T(f"胜率 {rate:.0f}%", f"{rate:.0f}% wins"), ha="center", fontsize=9)
b.set_xlabel(T(f"从 {N0} 根里取几根", f"sticks taken from {N0}"))
b.set_ylabel(T("这一支被访问了多少次", "visits"))
b.set_title(T("(b) 搜索不平均用力", "(b) Search does not spread its effort evenly"), fontsize=10)
b.grid(alpha=0.25, lw=0.5, axis="y")

fig.tight_layout()
figure(fig, "fig15_3_1")
