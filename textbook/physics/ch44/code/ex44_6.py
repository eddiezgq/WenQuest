"""44.6 节的计算：

算例 44.6.1  CO 分子的振动：吸收谱线的波数 2143 cm⁻¹，求振动量子 ħω、零点能和化学键的“劲度系数” k = μω²；
             用数值解（_qm.levels，约化质量 μ）核对能级等间距 (n + 1/2)ħω。
算例 44.6.2  巡检机器人的非色散红外（NDIR）CO₂ 传感器：CO₂ 反对称伸缩振动 2349 cm⁻¹，求吸收波长和 ħω；
             室温下处于 n = 1 的分子所占比例（玻尔兹曼因子）。
图 44.6.2    n = 10 的概率密度与经典谐振子的概率密度比较（对应原理）。
"""
import math

import numpy as np
from numpy.polynomial.hermite import hermval

from bookout import T, figure, out, style
from constants import h, c, e, hbar, u, m_e, k as kB
import _draw as d
import _qm

# ---- 算例 44.6.1：CO
nu_CO = 2143e2                                  # 波数，1/m
w_CO = 2 * math.pi * c * nu_CO                  # rad/s
hw_CO = hbar * w_CO / e                         # eV
mu = 12.000 * 15.995 / (12.000 + 15.995) * u    # 约化质量（¹²C¹⁶O）
k_CO = mu * w_CO ** 2                           # N/m
E0_CO = hw_CO / 2
# 数值核对：x 用 nm，质量 μ = mr·mₑ
mr = mu / m_e
k_eVnm2 = k_CO / e * 1e-18                      # N/m → eV/nm²
N, xmax = 1500, 0.04
dx = 2 * xmax / (N + 1)
x = -xmax + (np.arange(N) + 1) * dx
En, psi = _qm.levels(0.5 * k_eVnm2 * x ** 2, dx, 4, mr)
assert np.allclose(np.diff(En), hw_CO, rtol=1e-3) and abs(En[0] - E0_CO) < 1e-3 * E0_CO
x0_pm = math.sqrt(hbar / (mu * w_CO)) * 1e12     # 振动的特征长度，pm

# ---- 算例 44.6.2：CO₂
nu_CO2 = 2349e2
lam_CO2 = 1 / nu_CO2 * 1e6                      # μm
hw_CO2 = h * c * nu_CO2 / e
boltz = math.exp(-hw_CO2 / (kB * 300 / e))

out(nu_CO=2143, hw_CO=hw_CO, E0_CO=E0_CO, mu_u=mu / u, k_CO=k_CO, x0_pm=x0_pm,
    nu_CO2=2349, lam_CO2=lam_CO2, hw_CO2=hw_CO2, boltz=boltz, kT_eV=kB * 300 / e)

plt = style()


def phi(n, q):
    """无量纲谐振子本征函数，q = x/x₀。"""
    cn = np.zeros(n + 1); cn[n] = 1
    return hermval(q, cn) * np.exp(-q ** 2 / 2) / math.sqrt(2 ** n * math.factorial(n) * math.sqrt(math.pi))


# ---- 图 44.6.1：能级与波函数（以 ħω 和 x₀ 为单位）
fig, ax = plt.subplots(figsize=(5.4, 3.6))
q = np.linspace(-4.5, 4.5, 600)
ax.plot(q, q ** 2 / 2, color=d.POT, lw=2)
for n in range(5):
    En_ = n + 0.5
    A = math.sqrt(2 * En_)
    ax.plot([-A, A], [En_, En_], color=d.LEVEL, lw=1, ls="--")
    ax.plot(q, En_ + 0.42 * phi(n, q), color=d.PSI, lw=1.6)
    ax.text(4.6, En_, f"$n={n}$", va="center", fontsize=9)
ax.set_ylim(0, 5.8); ax.set_xlim(-4.5, 5.3)
ax.set_xlabel(T("$x/x_0$", "$x/x_0$")); ax.set_ylabel(T("$E/(\\hbar\\omega)$", "$E/(\\hbar\\omega)$")); d.spines(ax)
figure(fig, "fig44_6_1")

# ---- 图 44.6.2：n = 10 与经典概率密度
fig, ax = plt.subplots(figsize=(5.4, 2.8))
n = 10
A = math.sqrt(2 * n + 1)
q = np.linspace(-5.5, 5.5, 1200)
ax.plot(q, phi(n, q) ** 2, color=d.PROB, lw=1.6, label=T("量子 $n=10$", "quantum $n=10$"))
qc = np.linspace(-A + 1e-3, A - 1e-3, 600)
ax.plot(qc, 1 / (math.pi * np.sqrt(A ** 2 - qc ** 2)), color=d.CLASS, lw=1.8, ls="--", label=T("经典", "classical"))
ax.axvline(-A, color=d.MUTED, lw=0.8, ls=":"); ax.axvline(A, color=d.MUTED, lw=0.8, ls=":")
ax.set_ylim(0, 0.45); ax.set_xlabel(T("$x/x_0$", "$x/x_0$")); ax.set_ylabel(T("概率密度", "probability density"))
ax.legend(frameon=False, fontsize=9, loc="upper center"); d.spines(ax)
figure(fig, "fig44_6_2")
