"""Section 14.5: the 8 solutions of the UR5e.

Screw axes and the zero-position pose M from Table 12.1.1 (dimensions of the parts-library model). The inverse solution
follows the three steps of Section 14.5 (_ik.ur_ik):
  θ1: the component of the wrist point along ω2 (Eq. (14.5.3)); θ5, θ6: Subproblem 2 on directions; θ3, θ2, θ4:
  Subproblems 3, 1, 1.

(1) Example 14.5.1: the target pose is the end-effector pose of Example 12.3.1 (θ* = (30°, −60°, 90°, −120°, −90°, 45°)).
    Find the 8 solutions and, for each, compute the end-effector pose with the 3D model of the parts library (an
    algorithm independent of the product of exponentials) and compare it with the target; the position error must be
    below 10⁻⁹ m.
(2) Another method: the formulas of Hawkins (2013) based on the standard DH parameters (Chapter 13) give the same
    8 solutions.
(3) The numerical method, started from 200 random initial guesses, finds exactly these 8 distinct solutions.
(4) Three thousand random poses: the distribution of the number of solutions; every solution is checked against the
    parts-library model.
(5) Choosing a solution: the one nearest the current joint angles (this is also how URScript's get_inverse_kin chooses).
(6) Three singularities: at the shoulder (ρ = d4) and at the elbow (θ3 = 0) two branches merge; at the wrist (θ5 = 0)
    θ6 is arbitrary and the solutions form a family.
"""
import math

import numpy as np

from _ik import (D4, RX90, UR_M, UR_Q, UR_S, W4, YD, act, distinct, exp6, inv, numeric_ik, pose_err, same_solution,
                 ur_fk, ur_ik, ur_ik_234, ur_ik_dh, ur_model, ur_ordered, ur_points, wrap)
from bookout import T as tr, out, tex, vec

ur = ur_model()
rng = np.random.default_rng(145)

# ---------------------------------------------------------------- (1) Example 14.5.1
ths = np.radians([30, -60, 90, -120, -90, 45])
Td = ur_fk(ths)
assert pose_err(Td, ur.fk(ths))[0] < 1e-9
pd, Rd = Td[:3, 3], Td[:3, :3]
pw = pd - W4 * Rd[:, 1]                                        # wrist point = flange centre moved back W4 along the normal, Eq. (14.5.1)
rho = math.hypot(pw[0], pw[1])
base = math.degrees(math.atan2(pw[0], -pw[1]))
gam = math.degrees(math.atan2(math.sqrt(rho * rho - D4 * D4), D4))
sols = ur_ik(Td)
assert len(sols) == 8
t1s = sorted({round(math.degrees(s[0]), 9) for s, _ in sols}, reverse=True)

# intermediate quantities of step 2 (first value of θ1)
t1a = sols[0][0][0]
Rg = exp6(UR_S[0], -t1a)[:3, :3] @ Rd @ UR_M[:3, :3].T
v = Rg.T @ YD
c5 = float(v @ YD)
t5a = math.degrees(math.acos(c5))
# intermediate quantities of step 3 (first pair θ5, θ6)
s0 = sols[0][0]
g = exp6(UR_S[0], -s0[0]) @ Td @ inv(UR_M) @ exp6(UR_S[5], -s0[5]) @ exp6(UR_S[4], -s0[4])
p4 = act(g, UR_Q[3])
dl = float(np.linalg.norm(p4 - UR_Q[1]))


rows, worst_p, worst_R = [], 0.0, 0.0
star = None
sols_ordered = []
for i, (s, (sh, el, noflip)) in enumerate(ur_ordered(sols), 1):
    ep, eR = pose_err(ur.fk(s), Td)                           # parts-library model: an algorithm independent of the product of exponentials
    worst_p, worst_R = max(worst_p, ep), max(worst_R, eR)
    assert ep < 1e-9 and eR < 1e-9
    if same_solution(s, ths, 1e-9):
        star = i
    sols_ordered.append(s)
    m, e = f"{ep:.1e}".split("e")
    rows.append(f"| {i} | {sh} | {tr('上', 'up') if el == 'up' else tr('下', 'down')} | "
                f"{tr('不翻', 'no') if noflip else tr('翻', 'yes')} | " + " | ".join(f"{math.degrees(x):.2f}".replace("-", "−") for x in s) +
                f" | ${m}\\times 10^{{{int(e)}}}$ |")
assert star is not None
table = "\n".join(rows)
below = [i for i, s in enumerate(sols_ordered, 1) if ur_points(s)[2:, 2].min() < 0]     # a joint or link corner beyond the shoulder lies below the mounting surface

# the two wrist-flip solutions: θ5 changes sign, θ6 differs by π; θ2, θ3, θ4 change as well (the wrist is not spherical)
for s in sols_ordered:
    partner = [o for o in sols_ordered if abs(wrap(o[0] - s[0])) < 1e-9 and abs(o[4] + s[4]) < 1e-9]
    assert partner and abs(abs(wrap(partner[0][5] - s[5])) - math.pi) < 1e-9

# ---------------------------------------------------------------- (2) the DH formulas of Hawkins (2013)
dh = ur_ik_dh(Td @ inv(RX90))
assert len(dh) == 8 and all(any(same_solution(s, d, 1e-9) for d in dh) for s in sols_ordered)

# ---------------------------------------------------------------- (3) counting with the numerical method
found = [numeric_ik(ur_fk, Td, rng.uniform(-math.pi, math.pi, 6)) for _ in range(200)]
D = distinct(found)
assert len(D) == 8 and all(any(same_solution(d, s, 1e-6) for s in sols_ordered) for d in D)
n_conv = sum(x is not None for x in found)

# ---------------------------------------------------------------- (4) three thousand random poses
N = 3000
hist = {k: 0 for k in (0, 2, 4, 6, 8)}
wp = wR = 0.0
for _ in range(N):
    th = rng.uniform(-math.pi, math.pi, 6)
    T = ur_fk(th)
    S = ur_ik(T)
    hist[len(S)] += 1
    assert any(same_solution(s, th, 1e-6) for s, _ in S)
    for s, _ in S:
        e = pose_err(ur.fk(s), T)
        wp, wR = max(wp, e[0]), max(wR, e[1])
assert wp < 1e-9 and wR < 1e-9 and hist[0] == 0
# poses that may not be reachable: random flange centre and orientation in a 1.2 m cube
hist_any = {k: 0 for k in (0, 2, 4, 6, 8)}
for _ in range(2000):
    T = np.eye(4)
    q = rng.normal(size=4)
    q /= np.linalg.norm(q)
    a, b, c, d = q
    T[:3, :3] = [[1 - 2 * (c * c + d * d), 2 * (b * c - a * d), 2 * (b * d + a * c)],
                 [2 * (b * c + a * d), 1 - 2 * (b * b + d * d), 2 * (c * d - a * b)],
                 [2 * (b * d - a * c), 2 * (c * d + a * b), 1 - 2 * (b * b + c * c)]]
    T[:3, 3] = rng.uniform([-0.6, -0.6, -0.3], [0.6, 0.6, 0.9])
    hist_any[len(ur_ik(T))] += 1

# ---------------------------------------------------------------- (5) choosing: nearest the current joint angles
cur = np.radians([25, -55, 85, -115, -85, 40])
dist = [math.sqrt(sum(wrap(a - b) ** 2 for a, b in zip(s, cur))) for s in sols_ordered]
near = int(np.argmin(dist)) + 1
assert near == star
dist_sorted = sorted(dist)

# ---------------------------------------------------------------- (6) three singularities
# wrist: at θ5 = 0 axis 6 is parallel to axes 2, 3, 4 and θ6 is arbitrary; for each θ6, step 3 gives θ2, θ3, θ4 (a family of solutions)
t_w = ths.copy()
t_w[4] = 0.0
Tw = ur_fk(t_w)
Sw = [s for s, _ in ur_ik(Tw) if abs(wrap(s[0] - ths[0])) < 1e-9]
n_w = len(distinct(Sw, 1e-6))
for t6 in np.radians([-150, -60, 0, 45, 120]):
    fam = ur_ik_234(Tw, ths[0], 0.0, t6)
    assert fam
    for t2, t3, t4 in fam:
        assert max(pose_err(ur.fk([ths[0], t2, t3, t4, 0.0, t6]), Tw)) < 1e-9
# elbow: at θ3 = 0 (forearm in line with upper arm) the elbow-up and elbow-down branches merge
t_e = ths.copy()
t_e[2] = 0.0
Te = ur_fk(t_e)
Se = [s for s, lab in ur_ik(Te) if abs(wrap(s[0] - ths[0])) < 1e-9 and lab[1] == -1]
n_e = len(distinct(Se, 1e-6))
# shoulder: when the wrist point is exactly d4 from the base axis the two θ1 branches merge
Ts = Td.copy()
pw_s = Ts[:3, 3] - W4 * Ts[:3, 1]
Ts[:2, 3] += pw_s[:2] / np.linalg.norm(pw_s[:2]) * (D4 - np.linalg.norm(pw_s[:2]))
pw_s = Ts[:3, 3] - W4 * Ts[:3, 1]
assert abs(math.hypot(pw_s[0], pw_s[1]) - D4) < 1e-12
n_s = len({round(s[0], 9) for s, _ in ur_ik(Ts)})

out(pd=vec(pd, 4), pw=vec(pw, 4), rho=rho, base=base, gam=gam, t1a=t1s[0], t1b=t1s[1],
    v=vec(v, 4), c5=c5, t5a=t5a, p4=vec(p4, 4), dl=dl,
    table=table, star=star, worst_p=worst_p, worst_R=worst_R,
    n_conv=n_conv, N=N, h8=100 * hist[8] / N, h6=100 * hist[6] / N, h4=100 * hist[4] / N, h2=100 * hist[2] / N,
    wp=wp, wR=wR, a0=100 * hist_any[0] / 2000, a8=100 * hist_any[8] / 2000,
    cur=vec(np.degrees(cur), 0), near=near, dmin=math.degrees(dist_sorted[0]), d2=math.degrees(dist_sorted[1]),
    n_w=n_w, n_e=n_e, n_s=n_s, d4=D4, below=tr('、'.join(str(i) for i in below), (', '.join(str(i) for i in below[:-1]) + ' and ' if len(below) > 1 else '') + str(below[-1])), n_below=len(below))
