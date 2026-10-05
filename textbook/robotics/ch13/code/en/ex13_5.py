"""Examples 13.5.1 and 13.5.2: the jump in the DH parameters when adjacent joint axes are nearly parallel, the Hayati parameters, and real calibration data of a UR robot.

Geometry: axis i is the z-axis of {i−1} (through the origin, vertical); axis i+1 is nominally parallel to it, a = 0.425 m away (between joints 2 and 3 of the UR5e, the upper arm),
passing through the point (a, 0, 0). Tilt axis i+1 by a small angle ε: direction (sin ε cos φ, −sin ε sin φ, cos ε); φ = 0 tilts it within the plane of the two axes,
φ = 90° perpendicular to that plane.
(1) Example 13.5.1: a_i, α_i, d_i by the DH rules (common normal, Section 13.1.2); ε from 0.001° to 1°.
(2) Example 13.5.1: a, α, β by Hayati's parameterization Rot(z, θ) Trans(x, a) Rot(x, α) Rot(y, β); then how the screw axis changes. All three parameterizations are checked
       by "rebuilding the line from the parameters and comparing it with the original line".
(3) Example 13.5.2: the factory-calibrated DH parameters of a UR robot given in the UR ROS 2 driver documentation: d₂ and d₃ reach hundreds of metres, while d₂ tan α₂ and d₂ + d₃ + d₄
       come close to the nominal a₂ and d₄ of the UR10e respectively.
"""
import math

import numpy as np

from _dh import common_normal, screw_revolute
from bookout import out

A = 0.425


def tilted(eps, phi=0.0):
    u = np.array([math.sin(eps) * math.cos(phi), -math.sin(eps) * math.sin(phi), math.cos(eps)])
    return np.array([A, 0, 0.0]), u


def dh_of(eps, phi=0.0):
    """DH: the common normal of two lines. If parallel, the rule takes the one through the origin (d = 0). Returns (a, α, d)."""
    p, u = tilted(eps, phi)
    kind, f1, f2, dist, n = common_normal((0, 0, 0), (0, 0, 1), p, u)
    if kind == "parallel":
        return dist, 0.0, 0.0
    alpha = math.atan2(float(np.cross([0, 0, 1.0], u) @ n), float(u[2]))
    # rebuild from the parameters: axis i+1 should pass through f1 + a n, with direction z turned through α about n
    rebuilt = f1 + dist * n
    assert np.linalg.norm(np.cross(rebuilt - p, u)) < 1e-6 * max(1.0, abs(f1[2]))
    return dist, alpha, float(f1[2])


def hayati_of(eps, phi=0.0):
    """Hayati: take the point where axis i+1 meets the xy plane (z = 0) of {i−1}; Rot(z, θ) Trans(x, a) reaches that point, then Rot(x, α) Rot(y, β) aligns the direction."""
    p, u = tilted(eps, phi)
    t = -p[2] / u[2]
    P = p + t * u
    a = math.hypot(P[0], P[1])
    th = math.atan2(P[1], P[0])
    c, s = math.cos(-th), math.sin(-th)
    ul = np.array([c * u[0] - s * u[1], s * u[0] + c * u[1], u[2]])         # direction in the frame after Rot(z, θ)
    beta = math.asin(ul[0])
    alpha = math.atan2(-ul[1], ul[2])
    # check: Rot(x, α) Rot(y, β) e_z = (sin β, −sin α cos β, cos α cos β)
    assert np.allclose([math.sin(beta), -math.sin(alpha) * math.cos(beta), math.cos(alpha) * math.cos(beta)], ul, atol=1e-12)
    return a, alpha, beta


S0 = screw_revolute((0, 0, 1.0), (A, 0, 0))


def sci(x):
    """1.75e-05 → 1.75 × 10^{-5} (LaTeX)."""
    m, e = f"{x:.2e}".split("e")
    return f"{m}\\times 10^{{{int(e)}}}"


eps_deg = [0.001, 0.01, 0.1, 1.0]
rows, d_in, d_out, dS = [], [], [], []
for e in eps_deg:
    eps = math.radians(e)
    a1, al1, d1 = dh_of(eps, 0.0)
    a2, al2, d2 = dh_of(eps, math.pi / 2)
    ha, hal, hb = hayati_of(eps, 0.0)
    p, u = tilted(eps, 0.0)
    ds = float(np.linalg.norm(screw_revolute(u, p) - S0))
    d_in.append(d1)
    d_out.append(d2)
    dS.append(ds)
    z = lambda x, n: "0" if abs(x) < 0.5 * 10 ** (-n) else f"{x:.{n}f}"   # noqa: E731
    rows.append(f"| ${e:g}^\\circ$ | {z(a1, 3)} | ${z(d1, 1)}$ | {z(a2, 3)} | ${z(d2, 1)}$ | {z(ha, 3)} | ${math.degrees(hb):g}^\\circ$ | ${sci(ds)}$ |")
rows = "\n".join(rows)

# parallel (ε = 0)
a0, al0, dd0 = dh_of(0.0)
assert abs(a0 - A) < 1e-12 and dd0 == 0.0
# for small angles d ≈ −a / ε (in-plane tilt), compared with the exact value −a cot ε
e01 = math.radians(0.01)
d01 = dh_of(e01)[2]
assert abs(d01 - (-A / math.tan(e01))) < 1e-6 * abs(d01)
# ε of either sign: d jumps from −∞ to +∞
d_neg = dh_of(-e01)[2]
assert d_neg > 0 > d01
# the Hayati parameters are continuous: β = ε, a unchanged
for e in eps_deg:
    ha, hal, hb = hayati_of(math.radians(e))
    assert abs(hb - math.radians(e)) < 1e-12 and abs(ha - A) < 1e-12
# sensitivity: at ε = 0.01°, how much d changes when ε changes by 0.001°
de = math.radians(0.001)
dd_sens = dh_of(e01 + de)[2] - d01

# ---------------------------------------------------------------- Example 13.5.2: real calibration data (UR ROS 2 driver documentation, ur_calibration, "Calibration correction algorithm")
cal_d = [0.180539811714259, 439.140974079901, -446.027059806332, 7.0603368964236, 0.119811341150314, 0.115670917257426]
cal_a = [2.12234865571206e-05, 0.0193171326277006, -0.569251663611088, -4.61409023720934e-05, -6.39280053471802e-05, 0.0]
cal_alpha = [1.57014608044242, 0.0013941666682559, 0.00693818880325995, 1.56998468543761, -1.57038520649543, 0.0]
ur10e = {"d1": 0.1807, "a2": -0.6127, "a3": -0.57155, "d4": 0.17415, "d5": 0.11985, "d6": 0.11655}   # nominal values of the UR10e published by UR
ur16e_a2 = -0.4784                                    # upper arm of the UR16e published by UR (d₁, d₄, d₅, d₆ the same as the UR10e)
arm = cal_d[1] * math.tan(cal_alpha[1])
# inferring the model (the documentation does not state it): three offsets within 1 mm of the UR10e nominal values; the upper-arm length matches the UR10e and is far from the UR16e
for k, v in (("d1", cal_d[0]), ("d5", cal_d[4]), ("d6", cal_d[5])):
    assert abs(v - ur10e[k]) < 1e-3
assert abs(arm - abs(ur10e["a2"])) < 1e-3 and abs(arm - abs(ur16e_a2)) > 0.1
dsum = cal_d[1] + cal_d[2] + cal_d[3]

out(A=A, rows=rows, d01=d01, d_neg=d_neg, dd_sens=dd_sens, beta01=math.degrees(hayati_of(e01)[2]),
    cal_d2=cal_d[1], cal_d3=cal_d[2], cal_d4=cal_d[3], cal_al2=cal_alpha[1], cal_al2_deg=math.degrees(cal_alpha[1]),
    cal_d1=cal_d[0], cal_d5=cal_d[4], cal_d6=cal_d[5], cal_a3=cal_a[2],
    arm=arm, dsum=dsum, n_a2=ur10e["a2"], n_d4=ur10e["d4"], n_d1=ur10e["d1"], n_d5=ur10e["d5"], n_d6=ur10e["d6"], n_a3=ur10e["a3"], ur16e_a2=abs(ur16e_a2),
    eps_deg=eps_deg, d_in=d_in, d_out=d_out, dS=dS)
