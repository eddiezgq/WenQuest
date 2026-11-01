"""8.5 组合变形：WQR-105 输出轴 SH-301 B 版（第 33 章的几何与受力，材料 40Cr 调质）在额定转矩下，齿轮位截面同时受弯和受扭。
弯矩取圆周力、径向力两个平面的合成（第 33 章 _shaft.M_total），扭矩 350 N·m；截面按光轴算（键槽和过盈配合的影响在第 10、11 章）。
找出截面上的危险点，按第三、第四强度理论求当量应力；再沿轴长画出当量应力的分布（算例 8.5.1，图 8.5.1）。"""
import math

import numpy as np

import _ch8 as H
import _shaft as S
from bookout import T, figure, out, style

z0 = S.Z_GEAR
d = S.diameter_at(z0)
M = S.M_total(z0)                      # N·mm
Tq = S.torque_at(z0)
W = S.W_solid(d)
WT = S.WT_solid(d)
sig, tau = M / W, Tq / WT
eq3 = math.sqrt(sig ** 2 + 4 * tau ** 2)
eq4 = math.sqrt(sig ** 2 + 3 * tau ** 2)
Ft, Fr = S.gear_forces()
ang_M = math.degrees(math.atan2(S.moment(z0, Fr), S.moment(z0, Ft)))      # 合成弯矩矢量相对圆周力平面的方向
MAT = H.mat("40Cr-QT")                      # B 版材料（第 33.8 节的决定）
# 沿轴长
zs = np.linspace(0.5, S.LEN_B - 0.5, 600)
ds = np.array([S.diameter_at(z) for z in zs])
sz = np.array([S.M_total(z) for z in zs]) / (math.pi * ds ** 3 / 32)
tz = np.array([S.torque_at(z) for z in zs]) / (math.pi * ds ** 3 / 16)
ez = np.sqrt(sz ** 2 + 3 * tz ** 2)
k = int(np.argmax(ez))

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.6, 3.0), gridspec_kw={"width_ratios": [1.0, 1.35]})
th = np.linspace(0, 360, 361)
s_th = sig * np.cos(np.radians(th))
a0.plot(th, s_th, color="#1f77b4", lw=1.3, label=T("弯曲正应力 σ", "bending σ"))
a0.plot(th, np.full_like(th, tau), color="#2ca02c", lw=1.3, label=T("扭转切应力 τ", "torsional τ"))
a0.plot(th, np.sqrt(s_th ** 2 + 3 * tau ** 2), color="#d62728", lw=1.3, ls="--", label=T("当量应力（第四强度理论）", "equivalent (von Mises)"))
a0.set_xlabel(T("表面上的位置角 / (°)（0° 为受拉最大处）", "Position around the surface / ° (0° = max tension)"), fontsize=6.8)
a0.set_ylabel(T("应力 / MPa", "Stress / MPa"), fontsize=7.2)
a0.set_xticks([0, 90, 180, 270, 360])
a0.legend(fontsize=6.0, frameon=False, loc="upper center", ncol=2)
a0.set_ylim(-sig * 1.25, max(eq4, sig) * 1.75)
a0.tick_params(labelsize=6.3)
a0.set_title(T(f"(a) 齿轮位截面（Ø{d:.0f}）表面一圈", f"(a) Around the gear-seat section (Ø{d:.0f})"), fontsize=7.4)
a1.plot(zs, sz, color="#1f77b4", lw=1.0, label="σ")
a1.plot(zs, tz, color="#2ca02c", lw=1.0, label="τ")
a1.plot(zs, ez, color="#d62728", lw=1.4, label=T("当量应力", "equivalent"))
a1.axvline(z0, color=H.MUTED, lw=0.6, ls=":")
a1.text(z0, ez.max() * 1.05, T("齿轮", "gear"), fontsize=6.4, ha="center", color=H.MUTED)
a1.set_xlabel(T("沿轴长的位置 z / mm", "Position along the shaft z / mm"), fontsize=7.2)
a1.set_ylabel(T("表面应力的最大值 / MPa", "Maximum surface stress / MPa"), fontsize=7.2)
a1.legend(fontsize=6.2, frameon=False, loc="upper right")
a1.set_ylim(0, ez.max() * 1.18)
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) 沿轴长（光轴，未计应力集中）", "(b) Along the shaft (plain, no stress concentration)"), fontsize=7.4)
fig.tight_layout()
figure(fig, "fig8_5_1")

out(z0=z0, d=d, M=M / 1e3, T=Tq / 1e3, Ft=Ft, Fr=Fr, sig=sig, tau=tau, eq3=eq3, eq4=eq4, ratio34=eq3 / eq4, ang_M=ang_M, sy=MAT["sy"],
    S4=MAT["sy"] / eq4, z_max=float(zs[k]), d_max=float(ds[k]), eq_max=float(ez[k]), span=S.SPAN)
