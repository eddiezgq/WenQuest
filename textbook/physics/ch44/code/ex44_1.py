"""44.1 节的计算：

算例 44.1.1  归一化 ψ(x) = A e^{−|x|/a}，求 A 和粒子落在 |x| < a 内的概率；数值积分核对。
算例 44.1.2  宽 L 的盒子中，n = 1、2 两个定态在中间三分之一内的概率，与经典的 1/3 比较。
图 44.1.1    按 |ψ|² 随机抽取粒子位置，看探测结果怎样一个一个积累成概率密度（n = 2 的定态）。
"""
import math

import numpy as np
from scipy.integrate import quad

from bookout import T, figure, out, style
import _draw as d

# ---- 算例 44.1.1
a = 0.1                                          # nm
A = 1 / math.sqrt(a)                             # ∫A² e^{−2|x|/a} dx = A² a = 1
norm = quad(lambda x: A ** 2 * math.exp(-2 * abs(x) / a), -np.inf, np.inf)[0]
assert abs(norm - 1) < 1e-9
P_in = quad(lambda x: A ** 2 * math.exp(-2 * abs(x) / a), -a, a)[0]
assert abs(P_in - (1 - math.exp(-2))) < 1e-12

# ---- 算例 44.1.2
L = 1.0


def p_mid(n):
    return quad(lambda x: 2 / L * math.sin(n * math.pi * x / L) ** 2, L / 3, 2 * L / 3)[0]


P1, P2 = p_mid(1), p_mid(2)
assert abs(P1 - (1 / 3 + math.sqrt(3) / (2 * math.pi))) < 1e-12
assert abs(P2 - (1 / 3 - math.sqrt(3) / (4 * math.pi))) < 1e-12

out(a=a, A=A, P_in=P_in, P1=P1, P2=P2, A_nm=A)

# ---- 图 44.1.1：探测结果一个一个积累
rng = np.random.default_rng(44)
xs = np.linspace(0, L, 400)
dens = 2 / L * np.sin(2 * np.pi * xs / L) ** 2


def sample(n):
    out_ = []
    while len(out_) < n:                          # 舍选法：均匀撒点，按 |ψ|²/max 接受
        x = rng.uniform(0, L, 4 * n)
        y = rng.uniform(0, 2 / L, 4 * n)
        out_.extend(x[y < 2 / L * np.sin(2 * np.pi * x / L) ** 2])
    return np.array(out_[:n])


plt = style()
fig, axs = plt.subplots(1, 3, figsize=(7.6, 2.4), sharey=True)
for ax, n in zip(axs, (20, 200, 5000)):
    ax.hist(sample(n), bins=40, range=(0, L), density=True, color=d.PSI, alpha=0.55)
    ax.plot(xs, dens, color=d.PROB, lw=2)
    ax.set_title(T(f"{n} 个粒子", f"{n} particles"), fontsize=10)
    ax.set_xlabel(T("$x/L$", "$x/L$")); d.spines(ax)
axs[0].set_ylabel(T("$L\\,|\\psi|^2$", "$L\\,|\\psi|^2$"))
axs[0].set_ylim(0, 3.2)
fig.tight_layout()
figure(fig, "fig44_1_1")

# ---- 图 44.1.2：算例 44.1.1 的概率密度与 |x| < a 的面积
fig, ax = plt.subplots(figsize=(5.0, 2.6))
x = np.linspace(-0.4, 0.4, 801)
p = A ** 2 * np.exp(-2 * np.abs(x) / a)
ax.plot(x, p, color=d.PROB, lw=2)
m = np.abs(x) < a
ax.fill_between(x[m], p[m], color=d.PROB, alpha=0.25)
ax.text(0, 4, T(f"面积 = {P_in:.3f}", f"area = {P_in:.3f}"), ha="center", fontsize=10, color=d.INK)
ax.set_xlabel(T("$x$ / nm", "$x$ / nm")); ax.set_ylabel(T("$|\\psi|^2$ / nm$^{-1}$", "$|\\psi|^2$ / nm$^{-1}$"))
d.spines(ax)
figure(fig, "fig44_1_2")
