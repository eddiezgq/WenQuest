"""8.6 一点的应力状态：主应力与莫尔圆（算例 8.6.1、8.6.2，图 8.6.1）。
1. 算例 8.5.1 的危险点（SH-301 齿轮位表面，σ 与 τ 同时作用）：主应力、主方向、最大切应力和莫尔圆；
2. 关节力矩传感器（RJ-201 的 Ø50/Ø30 截面，假设表面露在外面，见程序 8.1.1）上的直角应变花（0°、45°、90°，0° 沿轴线）：取数字工厂“运动与动力分析”算出的
   一个节拍里肩关节力矩最大的时刻（第 33 章同一个模型），由转矩和弯矩（取外侧轴承处的弯矩作为上限）算出三片应变片的读数（取到 0.1 µε，当作“测得”的），
   再由读数反求主应力和主方向；并说明 ±45° 全桥为什么不受弯矩的影响。"""
import math

import numpy as np

import _ch8 as H
import _rj as R
from bookout import T, figure, out, style

# 1. 危险点
import _shaft as S
d = S.diameter_at(S.Z_GEAR)
sx1, tau1 = S.M_total(S.Z_GEAR) / S.W_solid(d), S.torque_at(S.Z_GEAR) / S.WT_solid(d)
s1, s2, th1, r1 = H.principal2(sx1, 0.0, tau1)
# 2. 应变花
ST = H.mat("40Cr-QT")
t, Tq, F, W = R.cycle()
i = int(np.argmax(np.abs(Tq)))
T_i, F_i = abs(float(Tq[i])), float(F[i])
ARM = R.arm_offset(R.SEAT)                       # 外侧轴承中心到大臂连接面的距离 mm（第 33 章）：F·ARM 是外侧轴承处的弯矩，
                                                 # 两轴承之间线性减小，这里取它作为贴片处弯矩的上限；F 取合力的大小（含轴向分量，偏保守）
D, dd = R.SEAT, R.BORE
M_b = F_i * ARM                                  # N·mm
sx = M_b / (H.Wp_hollow(D, dd) / 2)              # 弯曲应力：W = W_p / 2
tau = T_i * 1e3 / H.Wp_hollow(D, dd)
E, nu, G = ST["E"], ST["nu"], ST["G"]
ex, ey, gxy = sx / E, -nu * sx / E, tau / G
e45 = (ex + ey) / 2 + gxy / 2
em45 = (ex + ey) / 2 - gxy / 2
read = [round(v * 1e7) / 1e7 for v in (ex, e45, ey)]          # 0.1 µε
e_1, e_2, th2 = H.rosette_rect(*read)
p1, p2 = H.strain_to_stress(e_1, e_2, E, nu)
q1, q2, th_true, _ = H.principal2(sx, 0.0, tau)
bridge = e45 - em45                               # ±45° 全桥只感受 γ：弯矩项 (εx + εy)/2 抵消

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.1))
for ax, (sxx, txy, ttl) in zip(axs, ((sx1, tau1, T("(a) SH-301 齿轮位的危险点", "(a) Critical point on the SH-301 gear seat")),
                                     (sx, tau, T("(b) 力矩传感器表面一点", "(b) A point on the torque sensor")))):
    c, r = sxx / 2, math.hypot(sxx / 2, txy)
    ph = np.linspace(0, 2 * np.pi, 200)
    ax.plot(c + r * np.cos(ph), r * np.sin(ph), color="#1f77b4", lw=1.3)
    ax.plot([sxx, 0], [txy, -txy], color=H.MUTED, lw=0.8)
    ax.plot(sxx, txy, "o", color="#d62728", ms=4)
    ax.plot(0, -txy, "o", color="#2ca02c", ms=4)
    ax.text(sxx, txy, T(" x 面", " x face"), fontsize=6.4, va="bottom", color="#d62728")
    ax.text(0, -txy, T(" y 面", " y face"), fontsize=6.4, va="top", color="#2ca02c")
    for v, lab, ha, dx in ((c + r, "σ₁", "left", 0.04), (c - r, "σ₃", "right", -0.04)):
        ax.plot(v, 0, "k.", ms=4)
        ax.text(v + dx * r, -0.08 * r, f"{lab} = {v:.1f}", fontsize=6.4, ha=ha)
    ax.set_xlim(c - 1.6 * r, c + 1.6 * r)
    ax.axhline(0, color=H.MUTED, lw=0.5)
    ax.axvline(0, color=H.MUTED, lw=0.5)
    ax.set_aspect("equal")
    ax.set_xlabel(T("正应力 σ / MPa", "Normal stress σ / MPa"), fontsize=7.0)
    ax.set_ylabel(T("切应力 τ / MPa（向下为正）", "Shear stress τ / MPa (down positive)"), fontsize=6.8)
    ax.invert_yaxis()
    ax.tick_params(labelsize=6.3)
    ax.set_title(ttl, fontsize=7.4)
fig.tight_layout()
figure(fig, "fig8_6_1")

out(sx1=sx1, tau1=tau1, s1=s1, s3=s2, th1=th1, tmax1=r1, T_i=T_i, F_i=F_i, arm=ARM, M_b=M_b / 1e3, t_i=float(t[i]),
    sx=sx, tau=tau, ex=ex * 1e6, ey=ey * 1e6, e45=e45 * 1e6, em45=em45 * 1e6, r0=read[0] * 1e6, r45=read[1] * 1e6, r90=read[2] * 1e6,
    e1=e_1 * 1e6, e2=e_2 * 1e6, p1=p1, p2=p2, th2=th2, q1=q1, q2=q2, th_true=th_true, bridge=bridge * 1e6, gam=gxy * 1e6)
