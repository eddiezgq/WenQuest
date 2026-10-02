"""44.5 节的计算：

算例 44.5.1  电子（E = 1 eV）射向高 2 eV 的矩形势垒，宽 0.5 nm 与 1.0 nm：精确透射系数与近似式 16E(V₀−E)/V₀² e^{−2κa}。
算例 44.5.2  MOS 晶体管的栅氧化层（SiO₂）：势垒高约 3.1 eV，取氧化层中电子的有效质量 0.5 mₑ、电子能量 0.1 eV，
             比较 1.2 nm、2 nm、8 nm 厚的透射系数；厚度每增加 0.1 nm，透射系数缩小多少倍。
图 44.5.3    高斯波包穿越势垒（克兰克–尼科尔森法，_qm.cn_step）：透过的概率与按波包的波数分布平均的 T(E) 核对。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d
import _qm


def trans(E, V0, a, mr=1.0):
    """矩形势垒的精确透射系数（E ≠ V0）。"""
    cc = _qm.C / mr
    E = np.asarray(E, float)
    out_ = np.empty_like(E)
    lo = E < V0
    kap = np.sqrt((V0 - E[lo]) / cc)
    out_[lo] = 1 / (1 + V0 ** 2 * np.sinh(kap * a) ** 2 / (4 * E[lo] * (V0 - E[lo])))
    kk = np.sqrt((E[~lo] - V0) / cc)
    out_[~lo] = 1 / (1 + V0 ** 2 * np.sin(kk * a) ** 2 / (4 * E[~lo] * (E[~lo] - V0)))
    return out_


def approx(E, V0, a, mr=1.0):
    kap = math.sqrt((V0 - E) / (_qm.C / mr))
    return 16 * E * (V0 - E) / V0 ** 2 * math.exp(-2 * kap * a)


# ---- 算例 44.5.1
E1, V1 = 1.0, 2.0
kap1 = math.sqrt((V1 - E1) / _qm.C)
T05, T10 = trans([E1], V1, 0.5)[0], trans([E1], V1, 1.0)[0]
A05, A10 = approx(E1, V1, 0.5), approx(E1, V1, 1.0)

# ---- 算例 44.5.2：栅氧化层
Vox, mox, Eox = 3.1, 0.5, 0.1
kox = math.sqrt((Vox - Eox) / (_qm.C / mox))
Tox = {t: trans([Eox], Vox, t, mox)[0] for t in (1.2, 2.0, 8.0)}
per01 = math.exp(2 * kox * 0.1)

# ---- 波包穿越势垒
Lb, N = 200.0, 4000
dx = Lb / (N + 1)
x = (np.arange(N) + 1) * dx
Vb, wb, x_b = 0.3, 1.0, 100.0
V = np.where((x >= x_b) & (x < x_b + wb), Vb, 0.0)
E0, sig, x0 = 0.2, 6.0, 60.0
k0 = _qm.k_of(E0)
psi = _qm.packet(x, x0, sig, k0)
snaps, dt = [], 0.5
vg = 2 * _qm.C * k0 / _qm.HBAR_EVFS              # 群速度 ħk/m，nm/fs
t_end = 2 * (x_b - x0) / vg
steps = int(t_end / dt)
for s in range(steps + 1):
    if s in (0, steps // 2, steps):
        snaps.append((s * dt, np.abs(psi) ** 2))
    psi = _qm.cn_step(psi, V, dx, dt)
norm_end = np.sum(np.abs(psi) ** 2) * dx
T_packet = np.sum(np.abs(psi[x > x_b + wb]) ** 2) * dx
# 按波包的波数分布 |φ(k)|²（高斯，宽 1/(2σ)）平均平面波的透射系数
ks = np.linspace(k0 - 6 / (2 * sig), k0 + 6 / (2 * sig), 2001)
wk = np.exp(-((ks - k0) * 2 * sig) ** 2 / 2)
T_avg = np.sum(wk * trans(_qm.C * ks ** 2, Vb, wb)) / np.sum(wk)
T_E0 = trans([E0], Vb, wb)[0]
assert abs(norm_end - 1) < 1e-6
assert abs(T_packet - T_avg) < 2e-3

out(E1=E1, V1=V1, kap1=kap1, T05=T05, T10=T10, A05=A05, A10=A10, ratio_T=T05 / T10,
    Vox=Vox, mox=mox, Eox=Eox, kox=kox, Tox12=Tox[1.2], Tox20=Tox[2.0], Tox80=Tox[8.0], per01=per01,
    Vb=Vb, wb=wb, E0=E0, sig=sig, vg=vg, t_end=t_end, T_packet=T_packet, T_avg=T_avg, T_E0=T_E0)

plt = style()
# ---- 图 44.5.2：透射系数随能量的变化
fig, ax = plt.subplots(figsize=(5.2, 3.0))
Es = np.linspace(0.01, 6, 1200)
for a_, col in ((0.5, d.PSI), (1.0, d.LEVEL)):
    ax.semilogy(Es / V1, trans(Es, V1, a_), color=col, lw=2, label=T(f"$a$ = {a_:g} nm", f"$a$ = {a_:g} nm"))
ax.axvline(1, color=d.MUTED, ls=":", lw=1)
ax.set_xlabel(T("$E/V_0$", "$E/V_0$")); ax.set_ylabel(T("透射系数 $T$", "transmission $T$"))
ax.set_ylim(1e-4, 1.5); ax.legend(frameon=False, fontsize=9); d.spines(ax)
figure(fig, "fig44_5_2")

# ---- 图 44.5.1：势垒内外的波函数（E < V0）
fig, ax = plt.subplots(figsize=(5.6, 2.6))
a_ = 0.5
k = math.sqrt(E1 / _qm.C)
# 解边界条件：左边 e^{ikx} + r e^{−ikx}，势垒内 A e^{−κx} + B e^{κx}，右边 t e^{ikx}
M = np.array([[1, -1, -1, 0], [-1j * k, -(-kap1), -kap1, 0],
              [0, np.exp(-kap1 * a_), np.exp(kap1 * a_), -np.exp(1j * k * a_)],
              [0, -kap1 * np.exp(-kap1 * a_), kap1 * np.exp(kap1 * a_), -1j * k * np.exp(1j * k * a_)]], complex)
rhs = np.array([-1, -1j * k, 0, 0], complex)      # 未知数 r, A, B, t：x = 0 与 x = a 处 ψ、ψ′ 连续
r_, A_, B_, t_ = np.linalg.solve(M, rhs)
assert abs(abs(t_) ** 2 - T05) < 1e-9
xl, xm, xr = np.linspace(-1.5, 0, 300), np.linspace(0, a_, 100), np.linspace(a_, 2.0, 300)
ax.axvspan(0, a_, color=d.POT, alpha=0.2)
ax.plot(xl, (np.exp(1j * k * xl) + r_ * np.exp(-1j * k * xl)).real, color=d.PSI, lw=1.8)
ax.plot(xm, (A_ * np.exp(-kap1 * xm) + B_ * np.exp(kap1 * xm)).real, color=d.PSI, lw=1.8)
ax.plot(xr, (t_ * np.exp(1j * k * xr)).real, color=d.PSI, lw=1.8)
ax.text(a_ / 2, -1.2, T("势垒", "barrier"), ha="center", fontsize=9, color=d.POT)
ax.set_xlabel(T("$x$ / nm", "$x$ / nm")); ax.set_ylabel(T("$\\mathrm{Re}\\,\\psi$", "$\\mathrm{Re}\\,\\psi$")); d.spines(ax)
figure(fig, "fig44_5_1")

# ---- 图 44.5.3：波包穿越势垒的三个时刻
fig, axs = plt.subplots(3, 1, figsize=(5.6, 4.2), sharex=True)
for ax, (t, p) in zip(axs, snaps):
    ax.fill_between(x, p, color=d.PROB, alpha=0.35); ax.plot(x, p, color=d.PROB, lw=1.2)
    ax.axvspan(x_b, x_b + wb, color=d.POT, alpha=0.5)
    ax.text(5, 0.8 * p.max(), f"$t$ = {t:.0f} fs", fontsize=9)
    ax.set_yticks([]); d.spines(ax)
axs[-1].set_xlabel(T("$x$ / nm", "$x$ / nm")); axs[-1].set_xlim(0, 200)
axs[1].set_ylabel(T("$|\\Psi|^2$", "$|\\Psi|^2$"))
fig.tight_layout()
figure(fig, "fig44_5_3")
