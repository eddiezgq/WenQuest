"""12.8 节的计算：

算例 12.8.1  关节负载（小臂连同 1 kg 负载，绕肘关节）J_L = 0.272 kg·m²，电机转子 J_m = 0.20×10⁻⁴ kg·m²，减速器效率按 1 计。
            负载要以 10 rad/s² 加速：电机转矩随传动比 i 的变化 M_m = α(J_m i + J_L/i)，最小值在哪里；
            负载最高 3.0 rad/s、电机最高 5000 r/min 限制传动比的上限；i = 50、100、160 时的惯量比 J_L/(i²J_m)（图 12.8.1）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

JL, Jm, al = 0.27224, 0.20e-4, 10.0
i_opt = math.sqrt(JL / Jm)
Mm = lambda i: al * (Jm * i + JL / i)
i_max = 5000 * 2 * math.pi / 60 / 3.0
out(JL=JL, Jm_e4=Jm * 1e4, al=al, i_opt=i_opt, M_opt=Mm(i_opt), M50=Mm(50), M160=Mm(160), i_max=i_max,
    ratio50=JL / (50 ** 2 * Jm), ratio100=JL / (100 ** 2 * Jm), ratio160=JL / (160 ** 2 * Jm), M100=Mm(100))
assert abs(JL / (i_opt ** 2 * Jm) - 1) < 1e-12                   # 最优传动比时惯量比为 1

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
ii = np.linspace(20, 300, 400)
ax.plot(ii, Mm(ii), color=d.VR, lw=2, label=T("所需电机转矩", "required motor torque"))
ax.plot(ii, al * Jm * ii, color=d.VA, lw=1.2, ls="--", label=T("用来加速转子", "to accelerate the rotor"))
ax.plot(ii, al * JL / ii, color=d.VB, lw=1.2, ls="--", label=T("用来加速负载", "to accelerate the load"))
ax.plot(i_opt, Mm(i_opt), "o", color=d.VR); ax.text(i_opt + 5, Mm(i_opt) + 0.006, T(f"最优 i ≈ {i_opt:.0f}", f"optimum i ≈ {i_opt:.0f}"), fontsize=8.5)
ax.axvspan(i_max, 300, color=d.MUTED, alpha=0.15, lw=0); ax.text(i_max + 4, 0.006, T("电机转速不够", "motor too slow"), fontsize=8, color=d.MUTED)
ax.set_xlabel(T("传动比 i", "gear ratio i")); ax.set_ylabel(T("电机转矩 / (N·m)", "motor torque / (N·m)")); ax.set_xlim(20, 300); ax.set_ylim(0, 0.1)
ax.legend(frameon=False, fontsize=8, loc="upper right"); d.spines(ax)
figure(fig, "fig12_8_1")
