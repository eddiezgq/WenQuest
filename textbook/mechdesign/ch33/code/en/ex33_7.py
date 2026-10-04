"""Section 33.7: critical speed of the shaft.

Example 33.7.1  WQR-105 output shaft (design B): first and second critical speeds from beam elements + lumped gear mass; compared with the operating speed;
             approximation by the Dunkerley formula;
Example 33.7.2  A slender fan shaft (O30, span 800 mm, impeller 25 kg, 2900 r/min): the operating speed is above the first critical speed,
             so it is a "flexible shaft" and must pass quickly through the critical speed at start-up and shutdown;
Fig. 33.7.1    First mode shape of the two shafts; Fig. 33.7.2  Unbalance response (speed ratio and amplification factor).
"""
import math

import numpy as np
from scipy.linalg import eigh

import _draw as D
import _shaft as S
from bookout import T, figure, out, style
import mdstd

E = mdstd.material(S.MAT)["E"]
rho = 7.85e-9                                      # t/mm³
n_cr, zB, modesB = S.critical_speeds(n_modes=2)
m_gear = S.gear_mass()
ratio_B = n_cr[0] / S.N_OUT

# Dunkerley: gear alone (massless shaft) + shaft alone (no gear), 1/n^2 = 1/n_g^2 + 1/n_s^2
Ft = 1000.0
z_, yx, _ = S.deflection(Ft)
k_gear = Ft / yx[int(np.argmin(abs(z_ - S.Z_GEAR)))]          # N/mm: stiffness at the gear
n_g = math.sqrt(k_gear / (m_gear / 1000)) * 60 / (2 * math.pi)
n_s = S.critical_speeds(m_gear=0.0, n_modes=1)[0][0]
n_dunk = 1 / math.sqrt(1 / n_g ** 2 + 1 / n_s ** 2)

# ---- Example 33.7.2: fan shaft
L_f, d_f, m_imp, n_fan = 800.0, 30.0, 25.0, 2900.0
I_f = math.pi * d_f ** 4 / 64
k_mid = 48 * E * I_f / L_f ** 3                      # Mid-span stiffness of a simply supported beam, N/mm
n_fan_hand = math.sqrt(k_mid / (m_imp / 1000)) * 60 / (2 * math.pi)       # Shaft mass neglected
z = np.linspace(0, L_f, 201)
lay = [(0.0, L_f, d_f)]
K, M = S._beam_matrices(z, lay, E, rho)
M[2 * 100, 2 * 100] += m_imp / 1000
free = [i for i in range(2 * len(z)) if i not in (0, 2 * (len(z) - 1))]
w2, V = eigh(K[np.ix_(free, free)], M[np.ix_(free, free)])
n_fan_fe = math.sqrt(w2[0]) * 60 / (2 * math.pi)
n_fan_fe2 = math.sqrt(w2[1]) * 60 / (2 * math.pi)
u = np.zeros(2 * len(z)); u[free] = V[:, 0]; mode_f = u[0::2] / u[0::2][np.argmax(np.abs(u[0::2]))]
ratio_fan = n_fan / n_fan_fe
m_shaft_f = rho * math.pi * d_f ** 2 / 4 * L_f * 1000      # kg

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(8.6, 2.8))
ax = axs[0]
mB = modesB[0] / modesB[0][np.argmax(np.abs(modesB[0]))]
ax.plot(zB, mB, color=D.MOMENT, lw=1.8)
ax.set_title(T(f"WQR-105 输出轴：n_c1 ≈ {n_cr[0]:,.0f} r/min", f"WQR-105 output shaft: n_c1 ≈ {n_cr[0]:,.0f} r/min"), fontsize=9.5)
for zz in (S.Z_BRG_A, S.Z_BRG_B):
    ax.plot(zz, 0, "^", color=D.INK)
ax.plot(S.Z_GEAR, float(np.interp(S.Z_GEAR, zB, mB)), "o", ms=9, color=D.GEAR)
ax = axs[1]
ax.plot(z, mode_f, color=D.FORCE, lw=1.8)
ax.plot([0, L_f], [0, 0], "^", color=D.INK)
ax.plot(L_f / 2, 1, "o", ms=11, color=D.GEAR)
ax.set_title(T(f"风机轴：n_c1 ≈ {n_fan_fe:,.0f} r/min", f"fan shaft: n_c1 ≈ {n_fan_fe:,.0f} r/min"), fontsize=9.5)
for a in axs:
    a.axhline(0, color=D.MUTED, lw=0.6)
    a.set_xlabel("z / mm")
    a.set_yticks([])
    for s in ("top", "right", "left"):
        a.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig33_7_1")

# ---- Fig. 33.7.2: unbalance response
zeta = 0.02
r = np.linspace(0, 3, 600)
amp = r ** 2 / np.sqrt((1 - r ** 2) ** 2 + (2 * zeta * r) ** 2)
fig, ax = plt.subplots(figsize=(6.2, 3.2))
ax.plot(r, amp, color=D.FORCE, lw=1.8)
ax.axvspan(0, 0.7, color=D.MOMENT, alpha=0.10, lw=0)
ax.axvspan(1.3, 3, color=D.GEAR, alpha=0.12, lw=0)
ax.text(0.35, 8, T("刚性轴\nn ≤ 0.7 n_c1", "rigid shaft\nn ≤ 0.7 n_c1"), ha="center", fontsize=9)
ax.text(2.1, 8, T("挠性轴\n1.3 n_c1 ≤ n ≤ 0.7 n_c2", "flexible shaft\n1.3 n_c1 ≤ n ≤ 0.7 n_c2"), ha="center", fontsize=9)
ax.plot([ratio_fan], [ratio_fan ** 2 / math.sqrt((1 - ratio_fan ** 2) ** 2 + (2 * zeta * ratio_fan) ** 2)], "o", color=D.INK)
ax.annotate(T("风机轴的工作点", "fan shaft at speed"), (ratio_fan, 1.2), (ratio_fan + 0.25, 4), fontsize=9,
            arrowprops=dict(arrowstyle="->", lw=0.8))
ax.set_xlabel(T("转速比 n / n_c1", "speed ratio n / n_c1"))
ax.set_ylabel(T("挠度 / 偏心距", "whirl amplitude / eccentricity"))
ax.set_ylim(0, 12)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig33_7_2")

out(n_c1=n_cr[0], n_c2=n_cr[1], n_out=S.N_OUT, ratio_B=ratio_B, m_gear=m_gear, k_gear=k_gear, n_g=n_g, n_s=n_s,
    n_dunk=n_dunk, dunk_err=(n_cr[0] - n_dunk) / n_cr[0] * 100, L_f=L_f, d_f=d_f, m_imp=m_imp, n_fan=n_fan,
    k_mid=k_mid, n_fan_hand=n_fan_hand, n_fan_fe=n_fan_fe, n_fan_fe2=n_fan_fe2, ratio_fan2=n_fan / n_fan_fe2, ratio_fan=ratio_fan, m_shaft_f=m_shaft_f,
    fan_err=(n_fan_hand - n_fan_fe) / n_fan_fe * 100, zeta=zeta)
