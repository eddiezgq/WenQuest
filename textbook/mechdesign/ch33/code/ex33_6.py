"""33.6 节：轴的刚度。

算例 33.6.1  两个平面内的挠度曲线和转角（梁单元法，阶梯截面逐段计入），合成后与许用值比较；
算例 33.6.2  直径和材料对刚度的影响：轴径全部缩小 10%、换成 40Cr、换成铝合金；
图 33.6.1    挠度曲线与转角。
"""
import math

import numpy as np

import _draw as D
import _shaft as S
from bookout import T, figure, out, style
import mdstd

Ft, Fr = S.gear_forces()
z, yx, tx = S.deflection(Ft)
_, yy, ty = S.deflection(Fr)
y = np.hypot(yx, yy)
th = np.hypot(tx, ty)
i_g = int(np.argmin(abs(z - S.Z_GEAR)))
i_A = int(np.argmin(abs(z - S.Z_BRG_A)))
i_B = int(np.argmin(abs(z - S.Z_BRG_B)))
y_gear, th_gear, th_A, th_B = y[i_g], th[i_g], th[i_A], th[i_B]
y_max = y[: i_B + 1].max()
# 许用值：[SHI] 轴一章的典型最大转角（深沟球轴承 0.001–0.003 rad，未修形直齿轮 0.0005 rad）；齿轮处挠度取 0.01 m
th_brg_allow, th_gear_allow = 0.001, 0.0005
y_gear_allow = 0.01 * S.M_GEAR

# ---- 算例 33.6.2：比例关系
lay90 = [(z0, z1, 0.9 * d, *rest) for (z0, z1, d, *rest) in S.LAY_B]
_, a, _ = S.deflection(Ft, lay=lay90)
_, b, _ = S.deflection(Fr, lay=lay90)
ratio_d90 = np.hypot(a, b)[i_g] / y_gear
E_al = mdstd.material("6061-T6")["E"]
ratio_al = mdstd.material(S.MAT)["E"] / E_al
ratio_40 = mdstd.material(S.MAT)["E"] / mdstd.material("40Cr-QT")["E"]

plt = style()
fig, axs = plt.subplots(2, 1, figsize=(7.2, 4.6), sharex=True)
ax = axs[0]
ax.plot(z, y * 1000, color=D.MOMENT, lw=1.8, label=T("合成挠度", "resultant deflection"))
ax.plot(z, np.abs(yx) * 1000, color=D.MOMENT, lw=1.0, ls="--", label=T("水平面（圆周力）", "horizontal (tangential force)"))
ax.plot(z, np.abs(yy) * 1000, color=D.MOMENT, lw=1.0, ls=":", label=T("铅垂面（径向力）", "vertical (radial force)"))
ax.set_ylabel(T("挠度 / μm", "deflection / μm"))
ax.legend(fontsize=8.5, frameon=False)
ax.annotate(f"{y_gear * 1000:.1f} μm", (S.Z_GEAR, y_gear * 1000), (S.Z_GEAR + 25, y_gear * 1000 * 0.95), fontsize=9,
            arrowprops=dict(arrowstyle="->", lw=0.7))
ax = axs[1]
ax.plot(z, th * 1e3, color=D.TORQUE, lw=1.8)
ax.set_ylabel(T("转角 / mrad", "slope / mrad"))
ax.set_xlabel("z / mm")
for zz, v, name in ((S.Z_BRG_A, th_A, "A"), (S.Z_BRG_B, th_B, "B")):
    ax.annotate(f"{name}: {v * 1e3:.3f} mrad", (zz, v * 1e3), (zz + 14, v * 1e3 - 0.035), fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.7))
for a_ in axs:
    for zz in (S.Z_BRG_A, S.Z_BRG_B):
        a_.axvline(zz, color=D.MUTED, lw=0.6, ls=":")
    for s in ("top", "right"):
        a_.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig33_6_1")

out(y_gear_um=y_gear * 1000, y_max_um=y_max * 1000, th_gear=th_gear * 1e3, th_A=th_A * 1e3, th_B=th_B * 1e3,
    th_brg_allow=th_brg_allow * 1e3, th_gear_allow=th_gear_allow * 1e3, y_gear_allow_um=y_gear_allow * 1000,
    margin_y=y_gear_allow / y_gear, margin_th=th_brg_allow / max(th_A, th_B), ratio_d90=ratio_d90, ratio_al=ratio_al,
    ratio_40=ratio_40, E=mdstd.material(S.MAT)["E"] / 1000, E_al=E_al / 1000)
