"""Examples 10.5.1-10.5.3: natural coordinates, tangential and normal acceleration, curvature.

Example 10.5.1: the tool tip of the UR5e deburrs along a horizontal circle of radius R = 0.10 m; from rest it speeds up
  with a tangential acceleration of 0.5 m/s² to 0.25 m/s and then moves at constant speed. Find the tangential, normal
  and total accelerations at the middle and at the end of the speed-up; check by numerical differentiation in Cartesian
  coordinates, and check the curvature with κ = |v × a|/|v|³.
Example 10.5.2: the sealant ellipse of Section 10.2. The largest and smallest curvature; for dispensing sealant at constant speed with
  the normal acceleration not exceeding 1.0 m/s², the highest allowed speed and the time for one loop.
  Also the tangential and normal accelerations of the uniform-angle parametrization of Section 10.2 at t = 0.5 s,
  checked against |a| of Example 10.2.1.
Example 10.5.3: the components of the velocity and acceleration at one instant on the local bases of four coordinate
  systems: Cartesian, cylindrical, spherical (origin at the optical centre of a camera 0.3 m directly above the centre
  of the ellipse) and natural; the four sets of components have the same lengths.
"""
import math

import numpy as np

from _kin import cyl_basis, d1, d2, sph_basis, to_sph
from bookout import out

# ---------------------------------------------------------------- Example 10.5.1
R, at0, vmax = 0.10, 0.5, 0.25
t_acc = vmax / at0
c = np.array([-0.50, -0.20, 0.25])          # position of the centre of the circle in the UR5e base frame, m


def s_of(t):                                 # arc length s(t): first uniform acceleration, then constant speed
    return 0.5 * at0 * t * t if t <= t_acc else 0.5 * at0 * t_acc ** 2 + vmax * (t - t_acc)


def pos(t):
    u = s_of(t) / R
    return c + R * np.array([math.cos(u), math.sin(u), 0.0])


def natural(t):
    sd = at0 * t if t <= t_acc else vmax
    sdd = at0 if t < t_acc else 0.0
    return sdd, sd * sd / R                  # Eq. (10.5.6): a_t = s̈, a_n = κ ṡ²


res = {}
for name, t in (("mid", 0.5 * t_acc), ("end", t_acc - 1e-9)):
    a_t, a_n = natural(t)
    tt = min(t, t_acc - 2e-3)               # take the numerical derivative inside the speed-up
    a_num = d2(pos, tt, 1e-4)
    v_num = d1(pos, tt, 1e-5)
    et = v_num / np.linalg.norm(v_num)
    at_n, an_n = natural(tt)
    assert abs(a_num @ et - at_n) < 1e-5 and abs(np.linalg.norm(a_num - (a_num @ et) * et) - an_n) < 1e-5
    kappa = np.linalg.norm(np.cross(v_num, a_num)) / np.linalg.norm(v_num) ** 3
    assert abs(kappa - 1 / R) < 1e-3
    res[name] = (a_t, a_n, math.hypot(a_t, a_n), math.degrees(math.atan2(a_n, a_t)))
s_acc = s_of(t_acc)

# ---------------------------------------------------------------- Example 10.5.2
a, b = 0.12, 0.08
kmax, kmin = a / b ** 2, b / a ** 2
u = np.linspace(0, 2 * math.pi, 200001)
xp, yp = -a * np.sin(u), b * np.cos(u)
xpp, ypp = -a * np.cos(u), -b * np.sin(u)
kap = np.abs(xp * ypp - yp * xpp) / (xp ** 2 + yp ** 2) ** 1.5      # Eq. (10.5.9)
assert abs(kap.max() - kmax) < 1e-6 and abs(kap.min() - kmin) < 1e-6
an_lim = 1.0
v0 = math.sqrt(an_lim / kmax)
ds = np.sqrt(xp ** 2 + yp ** 2)
L = float(np.sum((ds[1:] + ds[:-1]) / 2 * np.diff(u)))              # perimeter by the trapezoidal rule
hh = ((a - b) / (a + b)) ** 2
L_ram = math.pi * (a + b) * (1 + 3 * hh / (10 + math.sqrt(4 - 3 * hh)))  # Ramanujan's approximation
assert abs(L - L_ram) < 1e-9
T_cycle = L / v0
# the parametrization of Section 10.2 at t = 0.5 s
w, t1 = math.pi / 2, 0.5
v1 = np.array([-a * w * math.sin(w * t1), b * w * math.cos(w * t1), 0])
a1 = np.array([-a * w * w * math.cos(w * t1), -b * w * w * math.sin(w * t1), 0])
sp = np.linalg.norm(v1)
k1 = np.linalg.norm(np.cross(v1, a1)) / sp ** 3
at1 = v1 @ a1 / sp
an1 = k1 * sp * sp
assert abs(math.hypot(at1, an1) - np.linalg.norm(a1)) < 1e-12

# ---------------------------------------------------------------- Example 10.5.3: four decompositions
xc, yc, z0 = 0.40, 0.05, 0.10
P = np.array([xc + a * math.cos(w * t1), yc + b * math.sin(w * t1), z0])
cam = np.array([0.40, 0.05, 0.40])          # optical centre of the camera: 0.3 m directly above the centre of the ellipse
comp = {}
comp["cart"] = (v1.copy(), a1.copy())
phi = math.atan2(P[1], P[0])
B = np.array(cyl_basis(phi))
comp["cyl"] = (B @ v1, B @ a1)
r, th, ph = to_sph(P - cam)
B = np.array(sph_basis(th, ph))
comp["sph"] = (B @ v1, B @ a1)
et = v1 / sp
en = (a1 - (a1 @ et) * et)
en /= np.linalg.norm(en)
eb = np.cross(et, en)
B = np.array([et, en, eb])
comp["nat"] = (B @ v1, B @ a1)
for k, (vv, aa) in comp.items():
    assert abs(np.linalg.norm(vv) - sp) < 1e-12 and abs(np.linalg.norm(aa) - np.linalg.norm(a1)) < 1e-12
assert abs(comp["nat"][0][1]) < 1e-15 and abs(comp["nat"][1][2]) < 1e-15
assert abs(comp["nat"][1][0] - at1) < 1e-12 and abs(comp["nat"][1][1] - an1) < 1e-12

vals = {}
for k, (vv, aa) in comp.items():
    for i in range(3):
        vals[f"{k}_v{i}"] = 0.0 if abs(vv[i]) < 1e-12 else float(vv[i])     # round-off errors are recorded as 0
        vals[f"{k}_a{i}"] = 0.0 if abs(aa[i]) < 1e-12 else float(aa[i])

out(R=R, at0=at0, vmax=vmax, t_acc=t_acc, s_acc=s_acc, s_acc_deg=math.degrees(s_acc / R),
    mid_at=res["mid"][0], mid_an=res["mid"][1], mid_a=res["mid"][2], mid_ang=res["mid"][3],
    end_at=res["end"][0], end_an=res["end"][1], end_a=res["end"][2], end_ang=res["end"][3],
    kmax=kmax, kmin=kmin, rmin=1 / kmax, rmax=1 / kmin, v0=v0, L=L, T_cycle=T_cycle, an_lim=an_lim,
    k1=float(k1), at1=float(at1), an1=float(an1), a1=float(np.linalg.norm(a1)), sp1=float(sp),
    cyl_phi_deg=math.degrees(phi), sph_r=r, sph_th_deg=math.degrees(th), sph_ph_deg=math.degrees(ph), **vals)
