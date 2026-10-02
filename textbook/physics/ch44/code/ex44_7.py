"""44.7 节的计算：

算例 44.7.1  扫描隧道显微镜：逸出功（功函数） φ = 4.5 eV 时的衰减常数 κ = √(2mφ)/ħ；针尖与样品的间隙每变化 0.1 nm，
             隧穿电流变化多少倍；电流读数有 2% 的噪声时，恒流模式对应的高度分辨率。
算例 44.7.2  逼近曲线：间隙 0.40～0.70 nm 每隔 0.03 nm 记一次电流（约 2 nA 到 3 pA）（读数含 3% 的随机误差，种子固定），
             用最小二乘拟合 ln I = ln I₀ − 2κd，求 κ 和逸出功 φ 及其标准不确定度。
图 44.7.1    恒流模式扫描：针尖在反馈控制下跟随表面的原子起伏和一个原子台阶（石墨，晶格 0.246 nm、层间距 0.335 nm）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d
import _qm

# ---- 算例 44.7.1
phi = 4.5
kappa = math.sqrt(phi / _qm.C)                  # 1/nm
per01 = math.exp(2 * kappa * 0.1)
dz_res_pm = 0.02 / (2 * kappa) * 1000           # δI/I = 2κ δd

# ---- 算例 44.7.2：逼近曲线与拟合
rng = np.random.default_rng(447)
I0 = 1.0e4                                      # nA（只影响截距）
dgap = np.arange(0.40, 0.7001, 0.03)
I = I0 * np.exp(-2 * kappa * dgap) * (1 + 0.03 * rng.standard_normal(dgap.size))
y = np.log(I)
A = np.vstack([np.ones_like(dgap), dgap]).T
coef, res, *_ = np.linalg.lstsq(A, y, rcond=None)
b = coef[1]
s2 = np.sum((y - A @ coef) ** 2) / (dgap.size - 2)
cov = s2 * np.linalg.inv(A.T @ A)
ub = math.sqrt(cov[1, 1])
kfit = -b / 2
ukfit = ub / 2
phifit = _qm.C * kfit ** 2
uphi = 2 * phifit * ukfit / kfit

U_phi = 2 * uphi                                 # 扩展不确定度，k = 2（符号约定第十节）
out(U_phi=U_phi, phi=phi, kappa=kappa, per01=per01, dz_res_pm=dz_res_pm, npts=dgap.size, kfit=kfit, ukfit=ukfit,
    phifit=phifit, uphi=uphi, Imax=I.max(), Imin_pA=I.min() * 1000)

plt = style()
fig, ax = plt.subplots(figsize=(5.0, 3.0))
ax.semilogy(dgap, I, "o", color=d.PSI, label=T("读数", "readings"))
dd = np.linspace(0.38, 0.72, 100)
ax.semilogy(dd, np.exp(coef[0] + b * dd), color=d.CLASS, lw=1.5, label=T("拟合", "fit"))
ax.set_xlabel(T("间隙 $d$ / nm", "gap $d$ / nm")); ax.set_ylabel(T("隧穿电流 $I$ / nA", "tunnelling current $I$ / nA"))
ax.legend(frameon=False, fontsize=9); d.spines(ax)
figure(fig, "fig44_7_2")

# ---- 图 44.7.1：恒流扫描
xs = np.linspace(0, 3.0, 1500)
a_lat = 0.246
surf = 0.02 * np.cos(2 * np.pi * xs / a_lat) + np.where(xs > 1.6, 0.335, 0.0)
d0 = 0.6                                         # 设定电流对应的间隙
z = np.empty_like(xs)
zc = surf[0] + d0
I_set = math.exp(-2 * kappa * d0)
for i, s in enumerate(surf):                     # 积分反馈：按 ln(I/I_set) 调整针尖高度
    for _ in range(3):
        Ii = math.exp(-2 * kappa * (zc - s))
        zc += 0.35 * math.log(Ii / I_set) / (2 * kappa)
    z[i] = zc
fig, ax = plt.subplots(figsize=(5.6, 2.8))
ax.fill_between(xs, -0.3, surf, color=d.POT, alpha=0.35)
ax.plot(xs, surf, color=d.POT, lw=1)
ax.plot(xs, z, color=d.CLASS, lw=1.6, label=T("针尖高度（恒流）", "tip height (constant current)"))
ax.set_xlabel(T("扫描位置 $x$ / nm", "scan position $x$ / nm")); ax.set_ylabel(T("高度 / nm", "height / nm"))
ax.set_ylim(-0.3, 1.25); ax.legend(frameon=False, fontsize=9, loc="upper left"); d.spines(ax)
figure(fig, "fig44_7_1")
