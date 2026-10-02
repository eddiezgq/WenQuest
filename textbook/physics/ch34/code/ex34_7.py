"""34.7 节的计算：

算例 34.7.1  AGV 无线充电：两个相同的线圈（L = 24 μH，内阻 0.1 Ω），串联电容补偿，在 85 kHz 谐振；
             负载 10 Ω。按电路的相量方程（第 36 章）计算传输效率与输出电压随耦合系数 k 的变化（图 34.7.1），
             并与“不补偿”的情形比较。相量解与解析式核对。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

L1 = L2 = 24e-6
R1 = R2 = 0.1
RL = 10.0
f = 85e3
w = 2 * math.pi * f
C = 1 / (w ** 2 * L1)            # 谐振电容
V1 = 10.0                        # 一次侧电压幅值，V


def solve(kc, comp=True):
    """相量方程：Z1 I1 − jωM I2 = V1，−jωM I1 + Z2 I2 = 0（I2 的方向取使负载电压为 RL I2）。"""
    M = kc * math.sqrt(L1 * L2)
    Z1 = R1 + 1j * w * L1 + (1 / (1j * w * C) if comp else 0)
    Z2 = R2 + RL + 1j * w * L2 + (1 / (1j * w * C) if comp else 0)
    A = np.array([[Z1, -1j * w * M], [-1j * w * M, Z2]])
    I1, I2 = np.linalg.solve(A, [V1, 0])
    P_in = 0.5 * (V1 * np.conj(I1)).real
    P_L = 0.5 * abs(I2) ** 2 * RL
    return P_L / P_in, abs(I2) * RL, P_L, abs(I1)


def eta_res(kc):
    """谐振时效率的解析式：η = ω²M²RL / [(R2 + RL)(R1(R2 + RL) + ω²M²)]。"""
    M = kc * math.sqrt(L1 * L2)
    return (w * M) ** 2 * RL / ((R2 + RL) * (R1 * (R2 + RL) + (w * M) ** 2))


for kc in (0.05, 0.1, 0.3, 0.6):
    assert abs(solve(kc)[0] - eta_res(kc)) < 1e-9

eta3, V3, P3, I13 = solve(0.3)
eta3n, V3n, P3n, _ = solve(0.3, comp=False)
eta05, V05, P05, _ = solve(0.05)
out(L_uH=L1 * 1e6, f_kHz=f / 1000, C_nF=C * 1e9, RL=RL, V1=V1, eta3=100 * eta3, V3=V3, P3=P3, I13=I13,
    eta3n=100 * eta3n, P3n=P3n, eta05=100 * eta05, P05=P05, wM3=w * 0.3 * L1)

plt = style()
kk = np.linspace(0.01, 0.8, 300)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.4, 3.1))
ax1.plot(kk, [100 * solve(x)[0] for x in kk], color=d.FIELD, lw=2, label=T("谐振补偿", "resonant"))
ax1.plot(kk, [100 * solve(x, False)[0] for x in kk], color=d.MUTED, lw=2, ls="--", label=T("不补偿", "uncompensated"))
ax1.set_xlabel(T("耦合系数 $k$", "coupling coefficient $k$")); ax1.set_ylabel(T("效率 $\\eta$ / %", "efficiency $\\eta$ / %"))
ax1.set_ylim(0, 100); ax1.legend(frameon=False, loc="lower right")
ax2.plot(kk, [solve(x)[2] for x in kk], color=d.FIELD, lw=2)
ax2.plot(kk, [solve(x, False)[2] for x in kk], color=d.MUTED, lw=2, ls="--")
ax2.set_xlabel(T("耦合系数 $k$", "coupling coefficient $k$")); ax2.set_ylabel(T("负载功率 $P$ / W", "load power $P$ / W"))
for ax in (ax1, ax2):
    d.spines(ax)
fig.tight_layout()
figure(fig, "fig34_7_1")
