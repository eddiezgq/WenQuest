"""17.1 节的示意图。

图 17.1.1：（a）同一个模型，pass@1、pass@10、pass@100 随采样温度各走各的——最优温度随 k 上升；
（b）两种常见的错写法各错多少：难度一不均，拿"平均 pass@1"往上外推就高估几十个百分点。
"""
import numpy as np

from _ch17 import best_temperature, pass_at_k, pass_curve, problem_logits
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

logits, right = problem_logits()
temps = np.round(np.arange(0.0, 2.01, 0.05), 2)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

for k, col, mk in ((1, C["z"], "o-"), (10, C["y"], "s-"), (100, C["x"], "^-")):
    ys = [pass_curve(logits, right, float(t), (k,))[k] for t in temps]
    a.plot(temps, ys, mk, color=col, lw=1.8, ms=3, markevery=4, label=f"pass@{k}")
    bt, bv = best_temperature(logits, right, k)
    a.plot([bt], [bv], "*", color=col, ms=15)
    a.annotate(T(f"最优 T = {bt:.2f}", f"best T = {bt:.2f}"), xy=(bt, bv),
               xytext=(bt + 0.12, bv + 0.03), fontsize=8, color=col)
a.set_xlabel(T("采样温度 T", "sampling temperature"))
a.set_ylabel(T("通过率", "pass rate"))
a.set_ylim(0, 1.05)
a.set_title(T("(a) k 越大，最优温度越高", "(a) Larger k wants a higher temperature"), fontsize=10)
a.legend(fontsize=9)
a.grid(alpha=0.25, lw=0.5)

# （b）两种错写法
g = np.random.default_rng(0)
N = 200
ks = [1, 2, 5, 10, 20, 50, 100]
ps = np.concatenate([np.full(200, 0.02), np.full(200, 0.60)])
cs = np.array([g.binomial(N, p) for p in ps])
true = [float(np.mean([1 - (1 - p) ** k for p in ps])) for k in ks]
unb = [float(np.mean([pass_at_k(N, int(c), k) for c in cs])) for k in ks]
pbar = float(np.mean(cs / N))
extrap = [1 - (1 - pbar) ** k for k in ks]

b.semilogx(ks, true, "-", color=C["ink"], lw=2.4, label=T("真值", "true value"))
b.semilogx(ks, unb, "o", color=C["z"], ms=7, label=T("无偏估计量", "unbiased estimator"))
b.semilogx(ks, extrap, "s--", color=C["x"], lw=1.8, ms=5,
           label=T("拿平均 pass@1 往上外推", "extrapolating from the mean pass@1"))
b.fill_between(ks, true, extrap, color=C["x"], alpha=0.12)
b.annotate(T(f"k = 10 时高估 {((extrap[3] - true[3]) * 100):.0f} 个百分点",
             f"{((extrap[3] - true[3]) * 100):.0f} points too high at k = 10"),
           xy=(10, (true[3] + extrap[3]) / 2), xytext=(1.6, 0.42), fontsize=9,
           arrowprops=dict(arrowstyle="->", color=C["muted"], lw=1.0))
b.set_xlabel(T("k（采几个样本）", "k (number of samples)"))
b.set_ylabel(T("pass@k", "pass@k"))
b.set_ylim(0, 1.05)
b.set_title(T("(b) 题目难易不均时，外推错得离谱",
              "(b) With uneven difficulty, extrapolation is badly wrong"), fontsize=10)
b.legend(fontsize=8, loc="lower right")
b.grid(alpha=0.25, lw=0.5, which="both")

fig.tight_layout()
figure(fig, "fig17_1_1")
