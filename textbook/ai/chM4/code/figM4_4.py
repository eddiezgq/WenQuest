"""M4.4 节的示意图。

图 M4.4.1：（a）相邻两个可表示的浮点数之间的间隔随数值大小跳变（单精度）：数越大，间隔越大，
所以"大数吃小数"；（b）求和误差随项数增长：顺序求和接近线性，成对求和慢得多，补偿求和几乎不涨。
"""
import numpy as np

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

fig, (a, b) = plt.subplots(1, 2, figsize=(11.0, 4.0))
xs = np.logspace(-6, 8, 400)
gap32 = np.array([float(np.spacing(np.float32(x))) for x in xs])
gap16 = np.array([float(np.spacing(np.float16(x))) if x < 65504 else np.nan for x in xs])
a.loglog(xs, gap32, color=C["z"], lw=1.8, label="FP32")
a.loglog(xs, gap16, color=C["x"], lw=1.8, label="FP16")
a.loglog(xs, xs * float(np.finfo(np.float32).eps), color=C["muted"], lw=1.0, ls="--",
         label=T("$x\\cdot\\varepsilon$（相对间隔不变）", "$x\\cdot\\varepsilon$ (constant relative gap)"))
a.set_xlabel(T("数值 $x$", "value $x$"))
a.set_ylabel(T("与下一个可表示数的间隔", "gap to the next representable number"))
a.set_title(T("(a) 浮点数的间隔随大小跳变", "(a) The gap grows with the value"), fontsize=10)
a.legend(fontsize=8)
a.grid(alpha=0.25, lw=0.5, which="both")

g = np.random.default_rng(44)
ns = np.unique(np.logspace(2, 5.6, 22).astype(int))
x = g.uniform(0.5, 1.5, int(ns[-1])).astype(np.float32)
seq_e, pair_e, kah_e = [], [], []
for n in ns:
    xx = x[:n]
    exact = float(np.sum(xx.astype(np.float64)))
    seq_e.append(abs(float(np.cumsum(xx)[-1]) - exact) / exact)
    pair_e.append(abs(float(np.sum(xx)) - exact) / exact)
    c = np.float32(0.0)
    s_ = np.float32(0.0)
    for val in xx:
        y_ = val - c
        t_ = s_ + y_
        c = (t_ - s_) - y_
        s_ = t_
    kah_e.append(abs(float(s_) - exact) / exact)
eps = float(np.finfo(np.float32).eps)
b.loglog(ns, np.maximum(seq_e, 1e-12), "o-", color=C["x"], lw=1.6, ms=4, label=T("顺序求和", "sequential"))
b.loglog(ns, np.maximum(pair_e, 1e-12), "s-", color=C["z"], lw=1.6, ms=4, label=T("成对求和（NumPy 默认）", "pairwise"))
b.loglog(ns, np.maximum(kah_e, 1e-12), "^-", color=C["y"], lw=1.6, ms=4, label=T("补偿求和（卡亨）", "compensated (Kahan)"))
b.loglog(ns, ns * eps, color=C["muted"], lw=1.0, ls="--", label=T("最坏情况 $n\\varepsilon$", "worst case $n\\varepsilon$"))
b.loglog(ns, np.sqrt(ns) * eps, color=C["muted"], lw=1.0, ls=":", label=T("随机误差 $\\sqrt{n}\\varepsilon$", "random $\\sqrt{n}\\varepsilon$"))
b.set_xlabel(T("项数 $n$", "number of terms $n$"))
b.set_ylabel(T("相对误差", "relative error"))
b.set_title(T("(b) 求和的误差随项数怎样涨", "(b) How summation error grows"), fontsize=10)
b.legend(fontsize=8)
b.grid(alpha=0.25, lw=0.5, which="both")
fig.tight_layout()
figure(fig, "figM4_4_1")
