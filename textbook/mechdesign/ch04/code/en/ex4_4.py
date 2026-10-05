"""Section 4.4 Evaluation of geometrical tolerances: roundness of the bearing seat of SH-301. The same set of CMM points evaluated with the least-squares circle (LSCI) and the minimum zone circle (MZCI)
gives different results; the tolerance zone defined by GB/T 1182 / ISO 1101 is the minimum zone (Example 4.4.1, Figure 4.4.1)."""
import math
import random

import numpy as np
from scipy.optimize import linprog

import _ch4 as H
from bookout import T, figure, out, style

# ---------------------------------------------------------------- Points: one section of the Ø35 bearing seat, CMM scan of N points
N = 360
R0 = 35.0095 / 2                     # Actual radius of the section (mm), the mean of the measured diameters of the bearing seat
E = (0.0062, -0.0038)               # Fixturing eccentricity (mm): the workpiece axis does not coincide with the rotary-table axis; removed in the evaluation
LOBES = [(2, 0.0008, 0.4), (3, 0.00105, 1.1), (5, 0.0003, 2.0)]   # (number of lobes, amplitude mm, phase): ovality, three-lobing (vibration in grinding, center-hole errors)
NOISE = 0.0002                      # Standard deviation of the random error (surface roughness, probe)
TOL = 0.004                         # Roundness tolerance (SH-301 bearing seat in this book: taken from the recommendation of GB/T 275 for seats of normal-class bearings)
rng = random.Random(44)
th = np.array([2 * math.pi * k / N for k in range(N)])
form = sum(a * np.cos(n * th + ph) for n, a, ph in LOBES) + np.array([rng.gauss(0, NOISE) for _ in range(N)])
r_true = R0 + form
x = r_true * np.cos(th) + E[0]
y = r_true * np.sin(th) + E[1]
# The CMM gives (x, y); polar coordinates are taken about the centroid of the points
r = np.hypot(x - x.mean(), y - y.mean())
t = np.arctan2(y - y.mean(), x - x.mean())
c, s = np.cos(t), np.sin(t)

# ---------------------------------------------------------------- Least-squares circle (linearized: r ≈ R + a cosθ + b sinθ, valid when the eccentricity is much smaller than the radius)
A = np.column_stack([np.ones_like(r), c, s])
R_ls, a_ls, b_ls = np.linalg.lstsq(A, r, rcond=None)[0]
res_ls = r - (R_ls + a_ls * c + b_ls * s)
rnd_ls = res_ls.max() - res_ls.min()

# ---------------------------------------------------------------- Minimum zone circle: two concentric circles enclosing all points with the smallest difference in radius (linear programming)
# Variables [a, b, R_in, w]: R_in ≤ r_i - a c_i - b s_i ≤ R_in + w, minimize w
cost = [0, 0, 0, 1]
A_ub = np.vstack([np.column_stack([c, s, np.ones_like(r), np.zeros_like(r)]),          # a c + b s + R_in ≤ r
                  np.column_stack([-c, -s, -np.ones_like(r), -np.ones_like(r)])])      # r ≤ a c + b s + R_in + w
b_ub = np.concatenate([r, -r])
lp = linprog(cost, A_ub=A_ub, b_ub=b_ub, bounds=[(None, None)] * 3 + [(0, None)], method="highs")
a_mz, b_mz, Rin_mz, rnd_mz = lp.x
res_mz = r - (a_mz * c + b_mz * s + Rin_mz)
n_contact = int(np.sum(np.abs(res_mz) < 1e-7) + np.sum(np.abs(res_mz - rnd_mz) < 1e-7))
centre_shift = math.hypot(a_mz - a_ls, b_mz - b_ls) * 1000          # μm
ecc = math.hypot(*E) * 1000

# ---------------------------------------------------------------- Figure
plt = style()
fig = plt.figure(figsize=(7.4, 3.3))
MAG = 2500                          # Magnification of the deviations (micrometers enlarged on the polar plot)
base = 22.0                         # Radius of the base circle on the plot (arbitrary units): a deviation of 1 μm is enlarged to 2.5


def polar(ax, res, inner, outer, color, title, lab):
    ang = np.append(t, t[0])
    ax.plot(np.cos(ang) * (base + MAG * np.append(res, res[0])), np.sin(ang) * (base + MAG * np.append(res, res[0])), color=H.INK, lw=0.6)
    for rr, ls in ((inner, "-"), (outer, "-")):
        q = np.linspace(0, 2 * math.pi, 200)
        ax.plot(np.cos(q) * (base + MAG * rr), np.sin(q) * (base + MAG * rr), color=color, lw=0.9, ls=ls)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=8)
    ax.text(0, -base - MAG * outer - 4, lab, ha="center", va="top", fontsize=7.2, color=color)


a1 = fig.add_subplot(1, 3, 1)
polar(a1, res_ls - res_ls.mean(), res_ls.min() - res_ls.mean(), res_ls.max() - res_ls.mean(), "#1f77b4",
      T("(a) 最小二乘圆", "(a) Least-squares circle"), T("圆度 ", "roundness ") + f"{rnd_ls * 1000:.1f} μm")
a2 = fig.add_subplot(1, 3, 2)
polar(a2, res_mz - rnd_mz / 2, -rnd_mz / 2, rnd_mz / 2, "#2ca02c",
      T("(b) 最小区域圆", "(b) Minimum-zone circles"), T("圆度 ", "roundness ") + f"{rnd_mz * 1000:.1f} μm")
a3 = fig.add_subplot(1, 3, 3)
deg = np.degrees(t) % 360
o = np.argsort(deg)
a3.plot(deg[o], 1000 * res_mz[o], color=H.INK, lw=0.6)
a3.axhline(0, color="#2ca02c", lw=0.8)
a3.axhline(1000 * rnd_mz, color="#2ca02c", lw=0.8)
a3.axhline(1000 * TOL, color="#d62728", lw=0.8, ls="--")
a3.text(5, 1000 * TOL + 0.1, T("公差 ", "tolerance ") + f"{TOL * 1000:.0f} μm", fontsize=6.6, color="#d62728", va="bottom")
a3.set_xlabel(T("角度 / (°)", "Angle / (°)"), fontsize=7.5)
a3.set_ylabel(T("到内圆的距离 / μm", "Distance from inner circle / μm"), fontsize=7.5)
a3.tick_params(labelsize=6.5)
a3.set_xlim(0, 360)
a3.set_title(T("(c) 展开：最小区域", "(c) Unrolled: minimum zone"), fontsize=8)
fig.tight_layout()
figure(fig, "fig4_4_1")

assert rnd_mz <= rnd_ls + 1e-9
out(N=N, ecc=ecc, rnd_ls=rnd_ls * 1000, rnd_mz=rnd_mz * 1000, tol=TOL * 1000, n_contact=n_contact, centre_shift=centre_shift,
    ok_ls=T("合格", "conforms") if rnd_ls <= TOL else T("不合格", "does not conform"),
    ok_mz=T("合格", "conforms") if rnd_mz <= TOL else T("不合格", "does not conform"),
    diff_pct=100 * (rnd_ls - rnd_mz) / rnd_mz, mag=MAG)
