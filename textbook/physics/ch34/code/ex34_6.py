"""34.6 节的计算：

算例 34.6.1  交流发电机：线圈在匀强磁场中匀速转动，ε(t) = N B A ω sin ωt（图 34.6.1）；
算例 34.6.2  直流电机：反电动势、空载转速、堵转电流、带载工作点（图 34.6.2 机械特性）；
算例 34.6.3  拖动示教：用手转动断电的关节电机，端子开路与短路时的电压和阻力矩。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

# ---- 算例 34.6.1
N, B, A, n_rpm = 200, 0.25, 0.01, 3000
w = 2 * math.pi * n_rpm / 60
emf_max = N * B * A * w
emf_rms = emf_max / math.sqrt(2)
f_e = n_rpm / 60

# ---- 算例 34.6.2：直流电机（永磁），K_e = K_t = K（SI 单位）
V, Ra, k = 24.0, 0.5, 0.05      # V、Ω、V·s/rad（= N·m/A）
w0 = V / k                      # 空载转速（不计摩擦）
I_stall = V / Ra
T_stall = k * I_stall
T_load = 0.5
I_load = T_load / k
w_load = (V - I_load * Ra) / k
P_out = T_load * w_load
P_in = V * I_load
eta = P_out / P_in
assert abs(V - (I_load * Ra + k * w_load)) < 1e-12

# ---- 算例 34.6.3：拖动示教（同一台电机，用手以 10 r/min 转动输出轴；减速比 100）
gear, n_hand = 100, 10
w_motor = 2 * math.pi * n_hand / 60 * gear
emf_hand = k * w_motor
I_short = emf_hand / Ra
T_brake_motor = k * I_short
T_brake_out = T_brake_motor * gear

out(N=N, B=B, A_cm2=A * 1e4, n_rpm=n_rpm, w=w, emf_max=emf_max, emf_rms=emf_rms, f_e=f_e,
    V=V, Ra=Ra, K=k, w0=w0, n0=w0 * 60 / (2 * math.pi), I_stall=I_stall, T_stall=T_stall,
    T_load=T_load, I_load=I_load, w_load=w_load, n_load=w_load * 60 / (2 * math.pi), emf_load=k * w_load,
    P_out=P_out, P_in=P_in, eta=100 * eta,
    gear=gear, n_hand=n_hand, w_motor=w_motor, emf_hand=emf_hand, I_short=I_short, T_brake_motor=T_brake_motor, T_brake_out=T_brake_out)

plt = style()
fig, ax = plt.subplots(figsize=(5.6, 2.9))
tt = np.linspace(0, 2 / f_e, 400)
ax.plot(tt * 1000, emf_max * np.sin(w * tt), color=d.CURR, lw=2)
ax.axhline(0, color=d.MUTED, lw=0.8)
ax.set_xlabel(T("时间 $t$ / ms", "time $t$ / ms")); ax.set_ylabel(T("$\\mathcal{E}$ / V", "$\\mathcal{E}$ / V"))
ax.text(14, emf_max * 1.2, r"$\mathcal{E}=NBA\omega\sin\omega t$", fontsize=11, color=d.INK)
ax.set_ylim(-emf_max * 1.15, emf_max * 1.4)
ax.set_xlim(0, tt[-1] * 1000); d.spines(ax)
# 线圈的取向：电动势最大时线圈平面与 B 平行，为零时与 B 垂直
ax.annotate(T("线圈平面 ∥ B\n（Φ = 0）", "coil plane ∥ B\n(Φ = 0)"), (5, emf_max), xytext=(7.0, emf_max * 0.9),
            fontsize=8, color=d.MUTED, arrowprops=dict(arrowstyle="->", color=d.MUTED, lw=0.8))
ax.annotate(T("线圈平面 ⊥ B\n（Φ 最大）", "coil plane ⊥ B\n(Φ largest)"), (10, 0), xytext=(2.0, -emf_max * 0.75),
            fontsize=8, color=d.MUTED, arrowprops=dict(arrowstyle="->", color=d.MUTED, lw=0.8))
figure(fig, "fig34_6_1")

fig, ax1 = plt.subplots(figsize=(5.6, 3.2))
TT = np.linspace(0, T_stall, 200)
ax1.plot(TT, (V - TT / k * Ra) / k * 60 / (2 * math.pi), color=d.FIELD, lw=2, label=T("转速", "speed"))
ax1.set_xlabel(T("负载转矩 $M_\\mathrm{L}$ / (N·m)", "load torque $M_\\mathrm{L}$ / (N·m)")); ax1.set_ylabel(T("转速 / (r/min)", "speed / (r/min)"), color=d.FIELD)
ax2 = ax1.twinx()
ax2.plot(TT, TT / k, color=d.FORCE, lw=2, ls="--", label=T("电流", "current"))
ax2.set_ylabel(T("电流 $I$ / A", "current $I$ / A"), color=d.FORCE)
ax1.plot([T_load], [w_load * 60 / (2 * math.pi)], "o", color=d.INK)
ax1.annotate(T("工作点", "operating point"), (T_load, w_load * 60 / (2 * math.pi)), xytext=(T_load + 0.3, 4200), fontsize=9,
             arrowprops=dict(arrowstyle="->", color=d.MUTED))
ax1.set_xlim(0, T_stall * 1.02); ax1.set_ylim(0, 5000); ax2.set_ylim(0, 50)
ax1.spines["top"].set_visible(False); ax2.spines["top"].set_visible(False)
figure(fig, "fig34_6_2")
