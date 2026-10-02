"""44.4 节的计算：

算例 44.4.1  GaAs/Al₀.₃Ga₀.₇As 量子阱，阱宽 8 nm：导带阶 ΔE_c = 0.243 eV，电子有效质量 0.067 mₑ；
             解超越方程求束缚态能级，数一数束缚态个数，并用数值解核对；求第一能级的透入深度 1/κ。
算例 44.4.2  同一量子阱中重空穴（ΔE_v = 0.131 eV，0.50 mₑ）的第一能级；导带与价带第一能级之间的跃迁
             放出的光子能量和波长（GaAs 室温禁带宽度 1.424 eV）。阱内外有效质量取相同值（简化）。
"""
import math

import numpy as np
from scipy.optimize import brentq

from bookout import T, figure, out, style
from constants import h, c, e
import _draw as d
import _qm

a = 8.0                                   # 阱宽，nm
dEc, me_ = 0.243, 0.067
dEv, mh_ = 0.131, 0.50
Eg = 1.424


def bound_states(V0, a, mr):
    """有限深势阱（阱底为 0、阱外为 V0）的束缚态能级。z = k a/2，z0 = (a/2)√(V0/c)。"""
    cc = _qm.C / mr
    z0 = a / 2 * math.sqrt(V0 / cc)
    out_ = []
    n = 0
    while True:
        lo, hi = n * math.pi / 2 + 1e-12, min((n + 1) * math.pi / 2, z0) - 1e-12
        if lo >= z0:
            break
        f = (lambda z: math.tan(z) - math.sqrt(z0 ** 2 / z ** 2 - 1)) if n % 2 == 0 else \
            (lambda z: -1 / math.tan(z) - math.sqrt(z0 ** 2 / z ** 2 - 1))
        if f(lo) * f(hi) < 0:
            z = brentq(f, lo, hi, xtol=1e-14)
            out_.append(cc * (2 * z / a) ** 2)
        n += 1
    return z0, out_


z0e, Ee = bound_states(dEc, a, me_)
z0h, Eh = bound_states(dEv, a, mh_)
n_e = len(Ee)
assert n_e == math.ceil(2 * z0e / math.pi)             # 束缚态个数 = ⌈z0/(π/2)⌉
kappa1 = math.sqrt((dEc - Ee[0]) / (_qm.C / me_))      # 1/nm
pen = 1 / kappa1
E_inf1 = _qm.C / me_ * (math.pi / a) ** 2              # 同宽无限深势阱的第一能级（对照）

# 数值解核对：在 60 nm 宽的盒子里放一个 8 nm 的阱
Lbox, N = 60.0, 3000
dx = Lbox / (N + 1)
x = (np.arange(N) + 1) * dx - Lbox / 2
V = np.where(np.abs(x) < a / 2, 0.0, dEc)
En, psi = _qm.levels(V, dx, n_e, me_)
assert np.allclose(En, Ee, rtol=2e-3)

E_photon = Eg + Ee[0] + Eh[0]
lam = h * c / (E_photon * e) * 1e9
lam_bulk = h * c / (Eg * e) * 1e9

out(a=a, dEc=dEc, me=me_, z0e=z0e, n_e=n_e, Ee1_meV=Ee[0] * 1000, Ee2_meV=Ee[1] * 1000,
    Ee3_meV=Ee[2] * 1000 if n_e > 2 else 0, E_inf1_meV=E_inf1 * 1000, pen=pen, kappa1=kappa1,
    dEv=dEv, mh=mh_, Eh1_meV=Eh[0] * 1000, Eg=Eg, E_photon=E_photon, lam=lam, lam_bulk=lam_bulk)

plt = style()
# ---- 图 44.4.2：有限深势阱中的束缚态
fig, ax = plt.subplots(figsize=(5.6, 3.4))
xs = x
ax.plot(xs, 1000 * V, color=d.POT, lw=2.5)
for k_ in range(n_e):
    ax.plot([xs[0], xs[-1]], [1000 * En[k_]] * 2, color=d.LEVEL, lw=0.8, ls="--")
    ax.plot(xs, 1000 * En[k_] + 55 * psi[k_] / np.abs(psi[k_]).max(), color=d.PSI, lw=1.8)
ax.axvspan(a / 2, a / 2 + pen, color=d.PROB, alpha=0.15)
ax.text(a / 2 + pen / 2, 270, "$1/\\kappa$", ha="center", fontsize=9, color=d.PROB)
ax.set_xlim(-14, 14); ax.set_ylim(-10, 300)
ax.set_xlabel(T("$x$ / nm", "$x$ / nm")); ax.set_ylabel(T("能量 / meV", "energy / meV")); d.spines(ax)
figure(fig, "fig44_4_2")

# ---- 图 44.4.1：超越方程的图解
fig, ax = plt.subplots(figsize=(5.0, 3.0))
z = np.linspace(0.01, z0e, 600)
rhs = np.sqrt(z0e ** 2 / z ** 2 - 1)
ax.plot(z, rhs, color=d.INK, lw=2, label=T("$\\sqrt{z_0^2/z^2-1}$", "$\\sqrt{z_0^2/z^2-1}$"))
for n in range(n_e + 1):
    zz = np.linspace(n * np.pi / 2 + 0.02, (n + 1) * np.pi / 2 - 0.02, 200)
    zz = zz[zz < z0e + 0.5]
    yy = np.tan(zz) if n % 2 == 0 else -1 / np.tan(zz)
    ax.plot(zz, yy, color=d.PSI if n % 2 == 0 else d.LEVEL, lw=1.5,
            label=(T("$\\tan z$（偶宇称）", "$\\tan z$ (even)") if n == 0 else T("$-\\cot z$（奇宇称）", "$-\\cot z$ (odd)") if n == 1 else None))
for k_, E_ in enumerate(Ee):
    zk = a / 2 * math.sqrt(E_ / (_qm.C / me_))
    ax.plot([zk], [math.sqrt(z0e ** 2 / zk ** 2 - 1)], "o", color=d.CLASS)
ax.axvline(z0e, color=d.MUTED, lw=1, ls=":"); ax.text(z0e, 5.3, "$z_0$", ha="center", fontsize=10)
ax.set_xlim(0, z0e + 0.4); ax.set_ylim(0, 5)
ax.set_xlabel("$z = ka/2$"); ax.legend(frameon=False, fontsize=8, loc="upper right"); d.spines(ax)
figure(fig, "fig44_4_1")
