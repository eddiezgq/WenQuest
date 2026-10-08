"""M3.2 节的示意图。

图 M3.2.1：（a）大数定律：抽检的样本比例随件数增多收敛到真实的 2%，波动按 1/√n 缩小；
（b）中心极限定理：返工工时的分布八成是 0（极偏），但 n 个的平均值的分布随 n 增大越来越像正态。
"""
import numpy as np

from _chM3 import P_BAD, rng
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
g = rng(11)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.0, 4.0))
ns = np.arange(1, 5001)
for k, col in enumerate((C["z"], C["y"], C["accent"])):
    draws = (g.random(5000) < P_BAD).astype(float)
    a.plot(ns, np.cumsum(draws) / ns, color=col, lw=1.0, alpha=0.9)
a.axhline(P_BAD, color=C["ink"], lw=1.4, ls="--", label=T("真实不合格率 2%", "true rate 2%"))
band = 1.96 * np.sqrt(P_BAD * (1 - P_BAD) / ns)
a.fill_between(ns, P_BAD - band, P_BAD + band, color=C["muted"], alpha=0.18,
               label=T("±1.96 个标准差（按 $1/\\sqrt{n}$ 收窄）", "±1.96 sd (shrinks as $1/\\sqrt{n}$)"))
a.set_xscale("log")
a.set_ylim(0, 0.08)
a.set_xlabel(T("已检件数 $n$（对数坐标）", "inspected $n$ (log)"))
a.set_ylabel(T("样本比例", "sample proportion"))
a.set_title(T("(a) 大数定律：三次抽检的轨迹", "(a) Law of large numbers: three runs"), fontsize=10)
a.legend(fontsize=8)
a.grid(alpha=0.25, lw=0.5, which="both")


def rework(size):
    hit = g.random(size) < 0.2
    return np.where(hit, g.uniform(0.5, 3.0, size), 0.0)


one = rework(200000)
mu, sd = one.mean(), one.std()
for n, col in ((1, C["x"]), (5, C["accent"]), (30, C["y"]), (200, C["z"])):
    m = rework((60000, n)).mean(axis=1)
    z = (m - mu) / (sd / np.sqrt(n))
    b.hist(z, bins=np.linspace(-4, 4, 80), density=True, histtype="step", lw=1.6, color=col,
           label=T(f"$n = {n}$", f"$n = {n}$"))
xs = np.linspace(-4, 4, 200)
b.plot(xs, np.exp(-xs ** 2 / 2) / np.sqrt(2 * np.pi), color=C["ink"], lw=1.4, ls="--",
       label=T("标准正态", "standard normal"))
b.set_ylim(0, 0.55)                                # n = 1、5 时在"工时为零"处有个很高的尖峰，截掉以便看清其余
b.text(-3.9, 0.5, T("（$n=1$、$5$ 的尖峰超出画面：八成的零件返工工时是 0）",
                    "(the spikes at zero for $n=1,5$ run off the top)"), fontsize=8, color=C["muted"])
b.set_xlabel(T("标准化后的样本均值", "standardised sample mean"))
b.set_ylabel(T("密度", "density"))
b.set_title(T("(b) 中心极限定理：$n$ 越大越像正态", "(b) CLT: the larger $n$, the more normal"), fontsize=10)
b.legend(fontsize=8)
b.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
figure(fig, "figM3_2_1")
