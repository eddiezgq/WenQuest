"""Section 33.4: combined bending-and-torsion strength calculation.

Example 33.4.1  Forces on the gear, reactions in the two planes, bending-moment and torque diagrams (Fig. 33.4.1);
Example 33.4.2  Nominal stresses at the checked sections; static safety factor under the maximum torque (start-up shock, taken from the run-in test rig record);
Example 33.4.3  The "equivalent bending moment" method of Chinese textbooks compared with von Mises combination.
"""
import math

import numpy as np

import _draw as D
import _shaft as S
from bookout import T, figure, out, style
import mdstd

mat = mdstd.material(S.MAT)
Ft, Fr = S.gear_forces()
RAx, RBx = S.reactions(Ft)
RAy, RBy = S.reactions(Fr)
z = np.linspace(0, S.LEN_B, 1221)
Mx = np.array([S.moment(t, Ft) for t in z]) / 1e3        # Horizontal plane (circumferential force), N·m
My = np.array([S.moment(t, Fr) for t in z]) / 1e3        # Vertical plane (radial force)
M = np.hypot(Mx, My)
Tz = np.array([S.torque_at(t) for t in z]) / 1e3
M_gear_x, M_gear_y = S.moment(S.Z_GEAR, Ft) / 1e3, S.moment(S.Z_GEAR, Fr) / 1e3
M_gear = math.hypot(M_gear_x, M_gear_y)

# Start-up shock: maximum torque recorded on the run-in test rig
series, rate, rated = S.torque_series()
T_peak = float(series.max())
K_peak = T_peak / rated

secs = {}
for k, sec in S.SECTIONS.items():
    d = sec["d"]
    Mk = S.M_total(sec["z"])
    Tk = S.torque_at(sec["z"])
    sig = Mk / S.W_solid(d)
    tau = Tk / S.WT_solid(d)
    # At start-up shock: M and T are scaled by the same factor (gear forces are proportional to torque)
    s_vm = math.sqrt((K_peak * sig) ** 2 + 3 * (K_peak * tau) ** 2)
    S_static = mat["sigma_s"] / s_vm
    # Equivalent bending moment: sigma_ca = sqrt(M^2 + (alpha T)^2)/W, alpha = 0.6 (torque treated as pulsating), third strength theory; compared with [sigma_-1]b
    alpha = 0.6
    Mca = math.hypot(Mk, alpha * Tk)
    secs[k] = dict(M=Mk / 1e3, T=Tk / 1e3, sigma=sig, tau=tau, s_vm=s_vm, S_static=S_static, Mca=Mca / 1e3,
                   sigma_ca=Mca / (0.1 * d ** 3))
sigma_1b_allow = 60.0           # Allowable bending stress [sigma_-1]b of quenched-and-tempered 45 steel (empirical value from Chinese textbooks, used for comparison; see the text)

# ---- Fig. 33.4.1: forces and internal-force diagrams
plt = style()
fig, axs = plt.subplots(5, 1, figsize=(8.0, 8.4), gridspec_kw={"height_ratios": [1.5, 1, 1, 1, 0.8]}, sharex=True)
ax = axs[0]
D.shaft(ax, S.LAY_B)
D.support(ax, S.Z_BRG_A, -21, 3)
D.support(ax, S.Z_BRG_B, -21, 3)
D.force(ax, S.Z_GEAR, 48, 0, -26, r"$F_\mathrm{r}$", size=11, off=(8, 10))
ax.plot(S.Z_GEAR, 0, "o", ms=9, mfc="white", mec=D.FORCE, mew=1.6, zorder=8)
ax.plot(S.Z_GEAR, 0, "x", ms=7, color=D.FORCE, mew=1.6, zorder=9)
ax.text(S.Z_GEAR + 9, -8, r"$F_\mathrm{t}$" + T("（垂直纸面）", " (into the page)"), color=D.FORCE, fontsize=10)
ax.text(S.Z_CPL, 26, T("转矩 T 由联轴器输出", "torque T out at the coupling"), ha="center", fontsize=9, color=D.TORQUE)
for zz, name in ((S.Z_BRG_A, "A"), (S.Z_BRG_B, "B")):
    ax.text(zz, -40, name, ha="center", fontsize=10, weight="bold")
ax.set_ylim(-46, 52)
ax.axis("off")
D.diagram(axs[1], z, My, D.MOMENT, T("$M_V$（铅垂面）", "$M_V$ (vertical)"), "N·m")
D.diagram(axs[2], z, Mx, D.MOMENT, T("$M_H$（水平面）", "$M_H$ (horizontal)"), "N·m")
D.diagram(axs[3], z, M, D.FORCE, T("合成弯矩 M", "resultant M"), "N·m")
D.diagram(axs[4], z, Tz, D.TORQUE, T("转矩 T", "torque T"), "N·m")
for ax, v in ((axs[1], M_gear_y), (axs[2], M_gear_x), (axs[3], M_gear)):
    ax.annotate(f"{v:.1f}", (S.Z_GEAR, v), (S.Z_GEAR + 12, v * 0.9), fontsize=9, arrowprops=dict(arrowstyle="-", lw=0.6))
for k, sec in S.SECTIONS.items():
    axs[3].axvline(sec["z"], color=D.MUTED, lw=0.6, ls=":")
    axs[3].text(sec["z"], M_gear * 1.12, k, ha="center", fontsize=9, color=D.INK)
axs[3].set_ylim(0, M_gear * 1.3)
axs[4].set_xlabel("z / mm")
fig.tight_layout()
figure(fig, "fig33_4_1")

o = dict(Ft=Ft, Fr=Fr, RAx=RAx, RBx=RBx, RAy=RAy, RBy=RBy, RA=math.hypot(RAx, RAy), RB=math.hypot(RBx, RBy),
         M_gear_x=M_gear_x, M_gear_y=M_gear_y, M_gear=M_gear, T=S.T_RATED / 1e3, T_peak=T_peak, K_peak=K_peak,
         sigma_s=mat["sigma_s"], sigma_1b_allow=sigma_1b_allow, d_gear=S.D_GEAR, alpha_deg=math.degrees(S.ALPHA))
for k, v in secs.items():
    for kk, vv in v.items():
        o[f"{kk}_{k}"] = vv
o["S_static_min"] = min(v["S_static"] for v in secs.values())
o["S_static_min_at"] = min(secs, key=lambda k: secs[k]["S_static"])
out(**o)
