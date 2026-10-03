"""1.6 节的计算：

算例 1.6.1  单摆测 g：6 个摆长（卷尺量到摆球顶端），每个摆长用秒表测 20 个周期的总时间（人的反应使每次计时有约 0.1 s
            的随机误差）。数据由程序按固定种子生成（真实 g 取 9.80 m/s²，摆球半径 1.5 cm 未计入量得的摆长）。
            作 T² 对 L 的图并做最小二乘拟合：斜率 4π²/g、截距、它们的标准不确定度，求 g 及其扩展不确定度；
            截距不为零说明摆长有系统偏差（摆球半径），而斜率不受影响。再在双对数坐标上拟合 T ∝ L^n，检验 n = 1/2。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

rng = np.random.default_rng(16)
g_true, r_bob = 9.80, 0.015
L = np.array([0.20, 0.35, 0.50, 0.65, 0.80, 0.95])              # 量得的摆长（到摆球顶端），m
t20 = 20 * 2 * np.pi * np.sqrt((L + r_bob) / g_true) + 0.1 * rng.standard_normal(L.size)
t20 = np.round(t20, 2)                                         # 秒表读到 0.01 s
Tp = t20 / 20
y = Tp ** 2


def linfit(x, y):
    """最小二乘直线 y = a + b x：系数、标准不确定度、残差的标准差。"""
    n = x.size
    Sxx = np.sum((x - x.mean()) ** 2)
    b = np.sum((x - x.mean()) * (y - y.mean())) / Sxx
    a = y.mean() - b * x.mean()
    res = y - (a + b * x)
    s = math.sqrt(np.sum(res ** 2) / (n - 2))
    ub = s / math.sqrt(Sxx)
    ua = s * math.sqrt(1 / n + x.mean() ** 2 / Sxx)
    return a, b, ua, ub, s, res


a, b, ua, ub, s, res = linfit(L, y)
assert np.allclose(np.polyfit(L, y, 1), [b, a])
g_fit = 4 * math.pi ** 2 / b
u_g = g_fit * ub / b
r_est = a / b                                                  # 截距/斜率 = 摆长的系统偏差
# 双对数拟合
an, n_exp, uan, un, _, _ = linfit(np.log(L + r_bob), np.log(Tp))

# B 类：卷尺（Ⅱ级，最大允许误差约 ±(0.3 + 0.2 L/m) mm）的刻度误差使斜率有相对误差约 0.05%；秒表走时误差约 10⁻⁵，都可忽略
rel_tape = (0.3 + 0.2 * 1.0) / 1000 / 1.0 / math.sqrt(3)
rel_A = ub / b
assert rel_tape < rel_A / 10
out(rel_tape_pct=100 * rel_tape, rel_A_pct=100 * rel_A, rows=len(L), g_true=g_true, b=b, ub=ub, a=a, ua=ua, s=s, g_fit=g_fit, u_g=u_g, U_g=2 * u_g, r_est_cm=100 * r_est,
    n_exp=n_exp, un=un, t20_first=t20[0], T_first=Tp[0])
out_table = [(f"{L[i]:.2f}", f"{t20[i]:.2f}", f"{Tp[i]:.4f}", f"{y[i]:.4f}") for i in range(L.size)]
out(table="；".join(f"{p[0]} m：{p[1]} s" for p in out_table))

plt = style()
# ---- 图 1.6.1：最小二乘的意思——三条过重心的直线与它们的残差平方和
xb, yb = L.mean(), y.mean()
fig, (b1, b2) = plt.subplots(1, 2, figsize=(7.2, 2.8))
for bb, col, ls in ((3.0, d.MUTED, "--"), (b, d.FIT, "-"), (5.0, d.MUTED, ":")):
    b1.plot([0, 1.05], [yb + bb * (0 - xb), yb + bb * (1.05 - xb)], color=col, ls=ls, lw=1.5)
b1.plot(L, y, "o", color=d.DATA)
for xi, yi in zip(L, y):
    b1.plot([xi, xi], [yi, yb + 5.0 * (xi - xb)], color=d.MUTED, lw=0.8)
b1.set_xlabel(T("摆长 $L$ / m", "length $L$ / m")); b1.set_ylabel("$T^2$ / s$^2$"); b1.set_xlim(0, 1.05); b1.set_ylim(0, 4.6); d.spines(b1)
b1.set_title(T("过重心、斜率不同的三条直线（细竖线为点线的残差）", "three lines through the centroid (thin: residuals of the dotted line)"), fontsize=9)
bs = np.linspace(2.5, 5.5, 200)
Sb = [np.sum((y - (yb + bb * (L - xb))) ** 2) for bb in bs]
b2.plot(bs, Sb, color=d.INK, lw=1.8)
b2.plot([b], [np.sum((y - (yb + b * (L - xb))) ** 2)], "o", color=d.FIT)
b2.annotate(T("最小二乘斜率", "least-squares slope"), (b, 0.02), xytext=(b + 0.3, 0.8), fontsize=9, arrowprops=dict(arrowstyle="->", color=d.MUTED))
b2.set_xlabel(T("斜率 $b$ / (s$^2$/m)", "slope $b$ / (s$^2$/m)")); b2.set_ylabel(T("残差平方和 $S$ / s$^4$", "sum of squares $S$ / s$^4$")); d.spines(b2)
fig.tight_layout()
figure(fig, "fig1_6_1")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
a1.plot(L, Tp, "o", color=d.DATA)
Ls = np.linspace(0, 1.05, 100)
Ld = np.linspace(L.min(), L.max(), 100)
a1.plot(Ld, np.sqrt(a + b * Ld), color=d.FIT, lw=1.5)
a1.set_xlabel(T("摆长 $L$ / m", "length $L$ / m")); a1.set_ylabel(T("周期 $T$ / s", "period $T$ / s")); a1.set_xlim(0, 1.05); a1.set_ylim(0, 2.2); d.spines(a1)
a1.set_title(T("$T$–$L$：曲线", "$T$ vs $L$: curved"), fontsize=10)
a2.plot(L, y, "o", color=d.DATA)
a2.plot(Ls, a + b * Ls, color=d.FIT, lw=1.5)
a2.set_xlabel(T("摆长 $L$ / m", "length $L$ / m")); a2.set_ylabel("$T^2$ / s$^2$"); a2.set_xlim(0, 1.05); a2.set_ylim(0, 4.4); d.spines(a2)
a2.set_title(T("$T^2$–$L$：直线", "$T^2$ vs $L$: straight"), fontsize=10)
a2.text(0.05, 3.7, f"$T^2 = {a:.3f} + {b:.3f}\\,L$", fontsize=9)
fig.tight_layout()
figure(fig, "fig1_6_2")

fig, ax = plt.subplots(figsize=(5.0, 2.2))
ax.axhline(0, color=d.MUTED, lw=1)
ax.plot(L, 1000 * res, "o", color=d.DATA)
ax.set_xlabel(T("摆长 $L$ / m", "length $L$ / m")); ax.set_ylabel(T("残差 / (10$^{-3}$ s$^2$)", "residual / (10$^{-3}$ s$^2$)")); d.spines(ax)
figure(fig, "fig1_6_3")
