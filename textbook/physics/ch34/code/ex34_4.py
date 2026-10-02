"""34.4 节的计算：

算例 34.4.1  长直螺线管内磁场均匀变化，管内外的感生电场 E(r)（图 34.4.1）；
             并用 ∮E·dl = −dΦ/dt 在几个半径上数值核对。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

Rs = 0.05                        # 螺线管半径，m
dBdt = 10.0                      # T/s


def E(r):
    r = np.asarray(r, dtype=float)
    return np.where(r <= Rs, r / 2 * dBdt, Rs ** 2 / (2 * np.maximum(r, 1e-12)) * dBdt)


for r in (0.01, 0.03, 0.05, 0.08, 0.2):
    circ = 2 * math.pi * r * float(E(r))                  # ∮E·dl
    flux_rate = math.pi * min(r, Rs) ** 2 * dBdt          # |dΦ/dt|
    assert abs(circ - flux_rate) < 1e-12

r3, r8 = 0.03, 0.08
emf_loop = math.pi * Rs ** 2 * dBdt                       # 套在管外任意大小的单匝线圈中的电动势

out(Rs_cm=Rs * 100, dBdt=dBdt, E3=float(E(r3)), E8=float(E(r8)), Emax=float(E(Rs)), emf_loop_mV=emf_loop * 1000)

plt = style()
fig, ax = plt.subplots(figsize=(5.4, 3.0))
rr = np.linspace(0, 0.2, 400)
ax.plot(rr * 100, E(rr), color=d.EFIELD, lw=2)
ax.axvline(Rs * 100, color=d.MUTED, ls="--", lw=1)
ax.text(Rs * 100 + 0.3, 0.02, T("管壁 $r = a$", "wall $r = a$"), fontsize=9, color=d.MUTED)
ax.text(1.0, 0.27, r"$E_\mathrm{i}=\frac{r}{2}\frac{\mathrm{d}B}{\mathrm{d}t}$", fontsize=11, color=d.INK)
ax.text(10, 0.17, r"$E_\mathrm{i}=\frac{a^2}{2r}\frac{\mathrm{d}B}{\mathrm{d}t}$", fontsize=11, color=d.INK)
ax.set_xlabel(T("到轴线的距离 $r$ / cm", "distance from the axis $r$ / cm"))
ax.set_ylabel(T("感生电场 $E_\\mathrm{i}$ / (V/m)", "induced field $E_\\mathrm{i}$ / (V/m)"))
ax.set_xlim(0, 20); ax.set_ylim(0, 0.3); d.spines(ax)
figure(fig, "fig34_4_1")
