"""9.4 节的示意图。

图 9.4.1：算例 9.4.1：5 个超声读数与候选的 μ；似然函数 L(μ)（各读数处密度之积）在样本均值处最大。
图 9.4.2：算例 9.4.2：激光、超声两个测量的密度与融合结果；四种估计方法的标准差。
图 9.4.3：算例 9.4.3：测力传感器标定，各点误差棒（±2σᵢ），普通与加权最小二乘直线及残差。
图 9.4.4：算例 9.4.4：带一个野值的 9 个读数；平均值、中位数、胡伯估计；三种损失函数。
"""
import math

import numpy as np

from _prob import gauss_pdf
from bookout import COLORS as C, T, figure, style

plt = style()


def clean(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


# ---------------------------------------------------------------- 图 9.4.1
zs = np.array([148.0, 155.0, 151.0, 144.0, 157.0])
sg = 10.0
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.0, 5.0), sharex=True, gridspec_kw={"height_ratios": [1.1, 1]})
x = np.linspace(110, 190, 800)
for mu, col, ls in ((135.0, C["muted"], "--"), (zs.mean(), C["z"], "-")):
    ax1.plot(x, gauss_pdf(x, mu, sg), color=col, lw=1.6, ls=ls)
    for zi in zs:
        xo = zi if ls == "-" else zi - 0.8          # 灰竖线稍向左错开，免得被蓝竖线盖住
        ax1.plot([xo, xo], [0, gauss_pdf(zi, mu, sg)], color=col, lw=2.2 if ls == "-" else 2.0, alpha=0.9, zorder=4 if ls != "-" else 3)
ax1.plot(zs, np.zeros_like(zs), "o", color=C["x"], ms=6, clip_on=False, zorder=5)
ax1.text(112, 0.0485, T("候选 μ = 135 mm：各读数处的密度（灰竖线）都小", "candidate μ = 135 mm: small densities at the readings (grey)"), fontsize=9, color=C["muted"])
ax1.text(112, 0.0545, T(f"候选 μ = {zs.mean():.0f} mm（样本均值）：密度之积最大（蓝竖线）", f"candidate μ = {zs.mean():.0f} mm (sample mean): largest product (blue)"), fontsize=9, color=C["z"])
ax1.set_ylim(0, 0.059)
ax1.set_ylabel(T("密度 / mm⁻¹", "density / mm⁻¹"), fontsize=9)
ax1.tick_params(labelsize=8)
clean(ax1)
mus = np.linspace(110, 190, 800)
L = np.array([np.prod(gauss_pdf(zs, m, sg)) for m in mus])
ax2.plot(mus, L / L.max(), color=C["z"], lw=1.8)
ax2.axvline(zs.mean(), color=C["z"], lw=0.8, ls=":")
ax2.plot([135], [np.prod(gauss_pdf(zs, 135, sg)) / L.max()], "o", color=C["muted"], ms=5)
ax2.text(zs.mean() + 2, 0.92, T(r"最大值在 $\bar z$ 处", r"maximum at $\bar z$"), fontsize=9, color=C["z"])
ax2.set_ylabel(T("L(μ)（以最大值为 1）", "L(μ) (max = 1)"), fontsize=9)
ax2.set_xlabel(T("μ / mm", "μ / mm"))
ax2.tick_params(labelsize=8)
clean(ax2)
fig.tight_layout()
figure(fig, "fig9_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 9.4.2
s1, s2, z1, z2 = 3.0, 10.0, 152.0, 143.0
w1 = (1 / s1 ** 2) / (1 / s1 ** 2 + 1 / s2 ** 2)
xh, sh = w1 * z1 + (1 - w1) * z2, 1 / math.sqrt(1 / s1 ** 2 + 1 / s2 ** 2)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.4), gridspec_kw={"width_ratios": [1.4, 1]})
x = np.linspace(115, 180, 800)
ax1.plot(x, gauss_pdf(x, z2, s2), color=C["accent"], lw=1.6, ls=":")
ax1.plot(x, gauss_pdf(x, z1, s1), color=C["muted"], lw=1.6, ls="--")
ax1.plot(x, gauss_pdf(x, xh, sh), color=C["z"], lw=2.2)
ax1.text(117, 0.035, T("超声 143 mm，σ = 10 mm", "ultrasonic 143 mm, σ = 10 mm"), color=C["accent"], fontsize=9)
ax1.text(158, 0.115, T("激光 152 mm，σ = 3 mm", "laser 152 mm, σ = 3 mm"), color=C["muted"], fontsize=9)
ax1.text(117, 0.125, T(f"融合 {xh:.1f} mm，σ = {sh:.2f} mm", f"fused {xh:.1f} mm, σ = {sh:.2f} mm"), color=C["z"], fontsize=9)
ax1.set_xlabel(T("到充电桩的距离 / mm", "distance to the charger / mm"))
ax1.set_ylabel(T("密度 / mm⁻¹", "density / mm⁻¹"), fontsize=9)
clean(ax1)
names = [T("只用超声", "ultrasonic\nonly"), T("简单平均", "plain\naverage"), T("只用激光", "laser\nonly"), T("加权（最大似然）", "weighted\n(ML)")]
vals = [s2, math.sqrt(s1 ** 2 + s2 ** 2) / 2, s1, sh]
cols = [C["accent"], C["x"], C["muted"], C["z"]]
ax2.barh(range(4), vals, color=cols, height=0.6)
for i, v in enumerate(vals):
    ax2.text(v + 0.2, i, f"{v:.2f} mm", va="center", fontsize=9)
ax2.set_yticks(range(4))
ax2.set_yticklabels(names, fontsize=9)
ax2.set_xlim(0, 13)
ax2.set_xlabel(T("估计值的标准差 / mm", "std of the estimate / mm"))
clean(ax2)
fig.tight_layout()
figure(fig, "fig9_4_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 9.4.3（数据与算例 9.4.3 相同）
rng = np.random.default_rng(904)
rng.standard_normal(200000)
rng.standard_normal(200000)                     # 与程序 9.4.1 同样地消耗随机数，得到同一组标定读数
F = np.array([0.0, 20, 40, 60, 80, 100])
sig_i = 0.05 + 0.002 * F
u = 0.3 + 0.2 * F + sig_i * rng.standard_normal(len(F))
Ad = np.column_stack([np.ones_like(F), F])
Wd = np.diag(1 / sig_i ** 2)
ols = np.linalg.solve(Ad.T @ Ad, Ad.T @ u)
wls = np.linalg.solve(Ad.T @ Wd @ Ad, Ad.T @ Wd @ u)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.5))
xx = np.linspace(-5, 105, 10)
ax1.errorbar(F, u, yerr=2 * sig_i, fmt="o", color=C["ink"], ms=4, capsize=3, lw=1)
ax1.plot(xx, ols[0] + ols[1] * xx, color=C["x"], lw=1.2, ls="--", label=T("普通最小二乘", "ordinary LS"))
ax1.plot(xx, wls[0] + wls[1] * xx, color=C["z"], lw=1.6, label=T("加权最小二乘", "weighted LS"))
ax1.legend(fontsize=9, frameon=False, loc="upper left")
ax1.set_xlabel(T("标准力 F / N", "reference force F / N"))
ax1.set_ylabel(T("输出 u / mV", "output u / mV"))
clean(ax1)
for est, col, mk, lab, dx in ((ols, C["x"], "s", T("普通", "ordinary"), -1.2), (wls, C["z"], "o", T("加权", "weighted"), 1.2)):
    ax2.plot(F + dx, u - (est[0] + est[1] * F), mk, color=col, ms=5, label=lab)
ax2.fill_between(F, -2 * sig_i, 2 * sig_i, color=C["muted"], alpha=0.15, lw=0)
ax2.axhline(0, color=C["muted"], lw=0.8)
ax2.text(2, 0.43, T("灰带：±2σᵢ（各点噪声）", "grey band: ±2σᵢ (noise at each point)"), fontsize=9, color=C["muted"])
ax2.legend(fontsize=9, frameon=False, loc="lower left")
ax2.set_ylim(-0.55, 0.55)
ax2.set_xlabel(T("标准力 F / N", "reference force F / N"))
ax2.set_ylabel(T("残差 / mV", "residual / mV"))
clean(ax2)
fig.tight_layout()
figure(fig, "fig9_4_3")
plt.close(fig)

# ---------------------------------------------------------------- 图 9.4.4 野值
zr = np.array([150.0, 148, 153, 151, 149, 152, 147, 150, 236])
c = 1.345 * 2.0
m = float(np.median(zr))
for _ in range(100):
    r = zr - m
    w = np.where(np.abs(r) <= c, 1.0, c / np.maximum(np.abs(r), 1e-12))
    m = float(np.sum(w * zr) / np.sum(w))
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.3), gridspec_kw={"width_ratios": [1.3, 1]})
ax1.plot(range(1, 10), zr, "o", color=C["ink"], ms=6)
ax1.plot([9], [zr[-1]], "o", color=C["x"], ms=9, mfc="none", mew=1.5)
ax1.text(8.6, 228, T("野值（多径回波）", "outlier (multipath echo)"), color=C["x"], fontsize=9, ha="right")
for v, col, ls, lab in ((zr.mean(), C["x"], "--", T(f"平均值 {zr.mean():.1f}", f"mean {zr.mean():.1f}")),
                        (np.median(zr), C["accent"], ":", T(f"中位数 {np.median(zr):.0f}", f"median {np.median(zr):.0f}")),
                        (m, C["z"], "-", T(f"胡伯估计 {m:.1f}", f"Huber {m:.1f}"))):
    ax1.axhline(v, color=col, lw=1.3, ls=ls, label=lab)
ax1.legend(fontsize=9, frameon=False, loc="center left")
ax1.set_xlabel(T("读数序号", "reading number"))
ax1.set_ylabel(T("读数 / mm", "reading / mm"))
ax1.set_xticks(range(1, 10))
clean(ax1)
r = np.linspace(-4, 4, 400)
ax2.plot(r, r ** 2 / 2, color=C["x"], lw=1.6, ls="--", label=T("平方 r²/2（高斯）", "square r²/2 (Gaussian)"))
ax2.plot(r, np.abs(r), color=C["accent"], lw=1.6, ls=":", label=T("绝对值 |r|（拉普拉斯）", "absolute |r| (Laplace)"))
k = 1.345
ax2.plot(r, np.where(np.abs(r) <= k, r ** 2 / 2, k * np.abs(r) - k * k / 2), color=C["z"], lw=2, label=T("胡伯函数", "Huber"))
ax2.set_ylim(0, 5)
ax2.set_xlabel(T("残差 r（以噪声标准差为单位）", "residual r (in noise stds)"))
ax2.set_ylabel(T("损失 ρ(r)", "loss ρ(r)"))
ax2.legend(fontsize=8.5, frameon=False, loc="upper center")
clean(ax2)
fig.tight_layout()
figure(fig, "fig9_4_4")
plt.close(fig)
