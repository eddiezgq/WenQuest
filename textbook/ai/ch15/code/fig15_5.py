"""15.5 节的示意图。

图 15.5.1：（a）Kuhn 扑克上，反事实遗憾最小化的可利用度按 1/√T 往下掉，与理论界同一条斜率；
（b）学出来的策略：拿最小牌虚张的概率落在 [0, 1/3] 里，拿最大牌下注的概率正好是它的三倍，
拿中间那张牌几乎从不先下注。
"""
import numpy as np

from _ch15 import CFR, KUHN_VALUE
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

fig, (a, b) = plt.subplots(1, 2, figsize=(11.2, 4.0))

iters = [30, 100, 300, 1000, 3000, 10_000, 30_000]
expl, alphas, vals = [], [], []
for it in iters:
    cf = CFR()
    avg, val = cf.run(it, seed=0)
    expl.append(cf.exploitability(avg))
    alphas.append(float(avg["J"][1]))
    vals.append(float(val))
a.loglog(iters, expl, "o-", color=C["z"], lw=1.8, ms=5, label=T("可利用度（算出来的）", "exploitability (measured)"))
ref = expl[0] * np.sqrt(iters[0]) / np.sqrt(np.array(iters, float))
a.loglog(iters, ref, color=C["muted"], ls="--", lw=1.2, label=T("$1/\\sqrt{T}$（理论界的斜率）", "$1/\\sqrt{T}$ (the bound's slope)"))
a.set_xlabel(T("自我对弈了多少轮", "self-play iterations"))
a.set_ylabel(T("可利用度（每局）", "exploitability per hand"))
a.set_title(T("(a) 离均衡还有多远", "(a) How far from equilibrium"), fontsize=10)
a.legend(fontsize=8)
a.grid(alpha=0.25, lw=0.5, which="both")

cf = CFR()
avg, val = cf.run(50_000, seed=0)
names = [T("拿 J 先下注（虚张）", "bet with J (bluff)"), T("拿 Q 先下注", "bet with Q"),
         T("拿 K 先下注", "bet with K"), T("拿 Q 跟注", "call with Q")]
vals_b = [float(avg["J"][1]), float(avg["Q"][1]), float(avg["K"][1]), float(avg["Qb"][1])]
b.barh(names, vals_b, color=[C["x"], C["muted"], C["z"], C["y"]])
b.axvline(1 / 3, color=C["ink"], ls="--", lw=1.0)
b.text(1 / 3 + 0.01, 3.3, T("均衡族的上界 α = 1/3", "upper end of the equilibrium family"), fontsize=8)
for i, x in enumerate(vals_b):
    b.text(x + 0.01, i, f"{x:.3f}", va="center", fontsize=9)
b.set_xlim(0, 1.0)
b.set_xlabel(T("概率", "probability"))
b.set_title(T(f"(b) 学出来的策略（博弈值 {val:.3f}，理论 {KUHN_VALUE:.3f}）",
              f"(b) The learned strategy (value {val:.3f}, theory {KUHN_VALUE:.3f})"), fontsize=10)
b.grid(alpha=0.25, lw=0.5, axis="x")

fig.tight_layout()
figure(fig, "fig15_5_1")
