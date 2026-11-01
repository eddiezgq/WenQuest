"""8.3 圆轴扭转：WQR-105 输出轴外伸段（Ø30 实心，长 68 mm，额定 350 N·m）的最大切应力和扭转角；
协作机器人肩关节空心轴 RJ-201（Ø50/Ø30，起停峰值 157 N·m）与同样截面积（同样质量）的实心轴比较（算例 8.3.1、8.3.2，图 8.3.1）。
τ = T·r / J，τ_max = T / W_p，φ = T·L / (G·J)。"""
import math

import numpy as np

import _ch8 as H
import _rj as R
import _shaft as S
from bookout import T, figure, out, style

ST45, ST40 = H.mat("40Cr-QT"), H.mat("40Cr-QT")     # SH-301 B 版、RJ-201 都是 40Cr 调质（第 33 章）
# 1. 外伸段
d1, L1 = 30.0, 68.0
T1 = S.T_RATED                                   # N·mm
J1 = math.pi * d1 ** 4 / 32
tau1 = T1 * (d1 / 2) / J1
phi1 = T1 * L1 / (ST45["G"] * J1)
# 2. 空心与实心（同截面积）
D2, d2 = R.SEAT, R.BORE
T2 = R.harmonic("25-100")["repeat"] * 1e3
A2 = math.pi / 4 * (D2 ** 2 - d2 ** 2)
d_eq = math.sqrt(D2 ** 2 - d2 ** 2)              # 同面积实心轴的直径
J_h, J_s = H.J_hollow(D2, d2), math.pi * d_eq ** 4 / 32
W_h, W_s = J_h / (D2 / 2), J_s / (d_eq / 2)
tau_h, tau_s = T2 / W_h, T2 / W_s
L2 = 100.0                                        # 比较用的长度 mm
phi_h, phi_s = T2 * L2 / (ST40["G"] * J_h), T2 * L2 / (ST40["G"] * J_s)
# 同样的 W_p（同强度），实心轴要多粗、重多少
d_same_W = (16 * W_h / math.pi) ** (1 / 3)
mass_ratio = d_same_W ** 2 / (D2 ** 2 - d2 ** 2)

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 2.9))
r = np.linspace(-D2 / 2, D2 / 2, 400)
th = np.where(np.abs(r) >= d2 / 2, T2 * np.abs(r) / J_h, np.nan)
a0.plot(r, th, color="#1f77b4", lw=1.6, label=T(f"空心 Ø{D2:.0f}/Ø{d2:.0f}", f"hollow Ø{D2:.0f}/Ø{d2:.0f}"))
rs = np.linspace(-d_eq / 2, d_eq / 2, 200)
a0.plot(rs, T2 * np.abs(rs) / J_s, color="#d62728", lw=1.2, ls="--", label=T(f"实心 Ø{d_eq:.0f}（同质量）", f"solid Ø{d_eq:.0f} (same mass)"))
a0.set_xlabel(T("到轴线的距离 / mm", "Distance from the axis / mm"), fontsize=7.2)
a0.set_ylabel(T("切应力 / MPa", "Shear stress / MPa"), fontsize=7.2)
a0.legend(fontsize=6.3, frameon=False, loc="upper center")
a0.set_ylim(0, max(tau_h, tau_s) * 1.35)
a0.tick_params(labelsize=6.3)
a0.set_title(T(f"(a) 截面上的切应力（{T2 / 1e3:.0f} N·m）", f"(a) Shear stress across the section ({T2 / 1e3:.0f} N·m)"), fontsize=7.4)
labels = [T("最大切应力", "max shear stress"), T("每 100 mm 扭转角", "twist per 100 mm")]
vh, vs = [tau_h, math.degrees(phi_h) * 60], [tau_s, math.degrees(phi_s) * 60]
x = np.arange(2)
a1.bar(x - 0.18, [1, 1], 0.36, color="#1f77b4", label=T("空心", "hollow"))
a1.bar(x + 0.18, [vs[0] / vh[0], vs[1] / vh[1]], 0.36, color="#d62728", label=T("同质量实心", "solid, same mass"))
for i in range(2):
    a1.text(i + 0.18, vs[i] / vh[i] + 0.03, f"{vs[i] / vh[i]:.2f}", ha="center", fontsize=6.4)
a1.set_xticks(x)
a1.set_xticklabels(labels, fontsize=6.8)
a1.set_ylabel(T("与空心轴之比", "Ratio to the hollow shaft"), fontsize=7.2)
a1.legend(fontsize=6.3, frameon=False)
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) 同样质量：空心轴的应力和扭转角都小", "(b) Same mass: the hollow shaft has less stress and twist"), fontsize=7.4)
fig.tight_layout()
figure(fig, "fig8_3_1")

out(d1=d1, L1=L1, T1=T1 / 1e3, tau1=tau1, phi1_deg=math.degrees(phi1), phi1_arcmin=math.degrees(phi1) * 60, G45=ST45["G"],
    D2=D2, d2=d2, T2=T2 / 1e3, d_eq=d_eq, tau_h=tau_h, tau_s=tau_s, J_ratio=J_h / J_s, W_ratio=W_h / W_s,
    phi_h_arcmin=math.degrees(phi_h) * 60, phi_s_arcmin=math.degrees(phi_s) * 60, L2=L2, d_same_W=d_same_W, mass_ratio=mass_ratio,
    tau_inner=T2 * (d2 / 2) / J_h)
