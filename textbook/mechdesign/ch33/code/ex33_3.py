"""33.3 节：按扭转强度初估直径。

算例 33.3.1  WQR-105 输出轴：由功率和转速估算最小直径；把系数 A₀ 从许用切应力推出来，而不是查表；
算例 33.3.2  键槽的放大量、与联轴器孔径和轴承内径的协调；
图 33.3.1    最小直径随许用切应力 [τ] 的变化，标出 A 版、B 版外伸段的直径。
"""
import math

import numpy as np

import _draw as D
import _shaft as S
from bookout import T, figure, out, style

T_nmm = S.T_RATED
n = S.N_OUT
P = T_nmm / 1e3 * n / 9550                      # kW：T（N·m）= 9550 P / n
tau_lo, tau_hi = 25.0, 45.0                     # 许用扭转切应力 [τ]，MPa：已把弯曲、应力集中的影响“打进”这个偏低的值里
A0 = lambda tau: (9550e3 * 16 / (math.pi * tau)) ** (1 / 3)      # d = A0 (P/n)^(1/3)，d 以 mm，P 以 kW，n 以 r/min
A0_hi, A0_lo = A0(tau_lo), A0(tau_hi)
d_hi = A0_hi * (P / n) ** (1 / 3)
d_lo = A0_lo * (P / n) ** (1 / 3)
key_add = 1.05                                  # 有一个键槽，直径加大 5%（两个键槽加 10%）
d_lo_k, d_hi_k = d_lo * key_add, d_hi * key_add
tau_30 = T_nmm / S.WT_solid(30)                 # Ø30 外伸段的名义扭转切应力
# 同一个转矩，不同许用应力下的最小直径
plt = style()
fig, ax = plt.subplots(figsize=(6.4, 3.4))
tau = np.linspace(15, 70, 200)
d = (16 * T_nmm / (math.pi * tau)) ** (1 / 3)
ax.plot(tau, d, color=D.TORQUE, lw=1.8)
ax.axvspan(tau_lo, tau_hi, color=D.TORQUE, alpha=0.12, lw=0)
ax.text((tau_lo + tau_hi) / 2, 46.5, T("初估常用的 [τ]", "usual [τ] for estimates"), ha="center", fontsize=9, color=D.TORQUE)
for dd, name in ((30, T("外伸段 Ø30（A、B 版）", "extension Ø30 (A, B)")), (35, T("轴承位 Ø35", "bearing seat Ø35")), (40, T("齿轮位 Ø40", "gear seat Ø40"))):
    ax.axhline(dd, color=D.MUTED, lw=0.8, ls="--")
    ax.text(68, dd + 0.4, name, ha="right", fontsize=8.5, color=D.INK)
ax.plot([tau_30], [30], "o", color=D.FORCE)
ax.annotate(T(f"Ø30 的名义 τ = {tau_30:.0f} MPa", f"nominal τ at Ø30 = {tau_30:.0f} MPa"), (tau_30, 30), (52, 26.2), fontsize=8.5,
            arrowprops=dict(arrowstyle="->", lw=0.8))
ax.set_xlabel(T("许用扭转切应力 [τ] / MPa", "allowable torsional shear stress [τ] / MPa"))
ax.set_ylabel(T("最小直径 d / mm", "minimum diameter d / mm"))
ax.set_ylim(24, 48)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig33_3_1")

out(P=P, n=n, T=T_nmm / 1e3, A0_lo=A0_lo, A0_hi=A0_hi, d_lo=d_lo, d_hi=d_hi, d_lo_k=d_lo_k, d_hi_k=d_hi_k,
    tau_lo=tau_lo, tau_hi=tau_hi, tau_30=tau_30, key_add=key_add)
