"""Section 14.3: the Paden–Kahan subproblems.

(1) The three invariants of Lemma 14.3.1: points on the axis do not move; the distance to a point on the axis does not
    change; the component along the axis does not change (checked at random).
(2) Example 14.3.1 (Subproblem 1): how far joint 1 of the UR5e must turn for the flange centre of the zero position to
    reach the point on the positive y-axis at the same height and the same radius.
(3) Example 14.3.2 (Subproblem 2): UR5e in the zero position, the axes of joints 5 and 6 meet at P56. Find θ5, θ6 that
    turn the end-effector x-axis to the direction (1, 1, −1)/√3.
(4) Example 14.3.3 (Subproblem 3): UR5e in the zero position; turn joint 3 so that the wrist point q4 is 0.6 m from the
    shoulder point q2.
(5) Ten thousand sets of random data: the solutions of the three subproblems substituted back into the original
    equations; for data made from known angles, the original angles must be among the solutions; for arbitrary data
    (a solution is not guaranteed), the proportions of cases in which Subproblems 2 and 3 have 0 or 2 solutions.
(6) The planar 2R arm is just "Subproblem 3 + Subproblem 1": compared with the formulas of Section 14.2.
"""
import math

import numpy as np

from _ik import UR_M, UR_Q, UR_S, UR_W, P56, act, exp6, ik2r, rot, sp1, sp1_ok, sp2, sp3, ur_fk, wrap
from bookout import out, vec

rng = np.random.default_rng(143)


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def rot_about(w, r, t, p):                               # turn through t about the axis through r with direction w (Eq. (12.1.2))
    return r + rot(w, t) @ (np.asarray(p, float) - r)


# ---------------------------------------------------------------- (1) the three invariants
for _ in range(1000):
    w, r, p, t = unit(rng.normal(size=3)), rng.normal(size=3), rng.normal(size=3), rng.uniform(-math.pi, math.pi)
    k = rng.normal()
    on = r + k * w
    assert np.allclose(rot_about(w, r, t, on), on, atol=1e-12)
    assert abs(np.linalg.norm(rot_about(w, r, t, p) - on) - np.linalg.norm(p - on)) < 1e-12
    assert abs(w @ (rot_about(w, r, t, p) - r) - w @ (p - r)) < 1e-12

# ---------------------------------------------------------------- (2) Example 14.3.1: Subproblem 1
p0 = UR_M[:3, 3]                                       # flange centre in the zero position
rad = math.hypot(p0[0], p0[1])
q_target = np.array([0.0, rad, p0[2]])
t1 = sp1(UR_W[0], UR_Q[0], p0, q_target)
assert sp1_ok(UR_W[0], UR_Q[0], p0, q_target)
assert np.allclose(act(exp6(UR_S[0], t1), p0), q_target, atol=1e-12)
assert np.allclose(ur_fk([t1, 0, 0, 0, 0, 0])[:3, 3], q_target, atol=1e-12)
u0 = p0 - UR_Q[0]
phi_p = math.degrees(math.atan2(p0[1], p0[0]))
bad_q = q_target + np.array([0, 0, 0.05])             # different height: the first part of condition (14.3.3) fails
assert not sp1_ok(UR_W[0], UR_Q[0], p0, bad_q)

# ---------------------------------------------------------------- (3) Example 14.3.2: Subproblem 2 (axes 5 and 6 meet at P56)
xb = UR_M[:3, 0]                                       # end-effector x-axis in the zero position, (1, 0, 0)
d = unit([1, 1, -1])
s2 = sp2(UR_W[4], UR_W[5], P56, P56 + xb, P56 + d)
assert len(s2) == 2
k12 = UR_W[4] @ UR_W[5]
alpha_beta = []
for t5, t6, c in s2:
    R = rot(UR_W[4], t5) @ rot(UR_W[5], t6)
    assert np.allclose(R @ xb, d, atol=1e-12)
    T = ur_fk([0, 0, 0, 0, t5, t6])
    assert np.allclose(T[:3, 0], d, atol=1e-12)          # forward kinematics: the end-effector x-axis really does point along d
    alpha_beta.append(c - P56)
u2 = xb
a2 = (k12 * (UR_W[5] @ u2) - UR_W[4] @ d) / (k12 * k12 - 1)
b2 = (k12 * (UR_W[4] @ d) - UR_W[5] @ u2) / (k12 * k12 - 1)
n2 = np.cross(UR_W[4], UR_W[5])
g2 = (u2 @ u2 - a2 * a2 - b2 * b2 - 2 * a2 * b2 * k12) / (n2 @ n2)
s2d = sorted([(math.degrees(t5), math.degrees(t6)) for t5, t6, _ in s2], reverse=True)

# ---------------------------------------------------------------- (4) Example 14.3.3: Subproblem 3
delta = 0.6
s3 = sp3(UR_W[2], UR_Q[2], UR_Q[3], UR_Q[1], delta)
assert len(s3) == 2
for t in s3:
    q4 = act(exp6(UR_S[2], t), UR_Q[3])
    assert abs(np.linalg.norm(q4 - UR_Q[1]) - delta) < 1e-12
    T = ur_fk([0, 0, t, 0, 0, 0])
W2 = 0.131
L1, L2 = 0.425, 0.392
dprime = math.sqrt(delta ** 2 - W2 ** 2)              # first take out the offset W2 along the axis
cos_d = (L1 ** 2 + L2 ** 2 - dprime ** 2) / (2 * L1 * L2)
check = sorted(wrap(math.pi + sg * math.acos(cos_d)) for sg in (1, -1))
assert np.allclose(sorted(s3), check, atol=1e-12)
s3d = sorted(math.degrees(t) for t in s3)

# ---------------------------------------------------------------- (5) random data
N = 10000
worst = 0.0
n0 = {2: 0, 3: 0}
for _ in range(N):
    # Subproblem 1
    w, r, p, t = unit(rng.normal(size=3)), rng.normal(size=3), rng.normal(size=3), rng.uniform(-math.pi, math.pi)
    q = rot_about(w, r, t, p)
    s = sp1(w, r, p, q)
    assert abs(wrap(s - t)) < 1e-9
    # Subproblem 2: the two axes meet at r
    w1, w2 = unit(rng.normal(size=3)), unit(rng.normal(size=3))
    ta, tb = rng.uniform(-math.pi, math.pi, 2)
    q = r + rot(w1, ta) @ rot(w2, tb) @ (p - r)
    sols = sp2(w1, w2, r, p, q)
    assert any(abs(wrap(a - ta)) < 1e-7 and abs(wrap(b - tb)) < 1e-7 for a, b, _ in sols)
    for a, b, _ in sols:
        worst = max(worst, float(np.linalg.norm(r + rot(w1, a) @ rot(w2, b) @ (p - r) - q)))
    n0[2] += len(sp2(w1, w2, r, p, r + unit(rng.normal(size=3)) * np.linalg.norm(p - r))) == 0
    # Subproblem 3
    qq = rng.normal(size=3)
    dl = float(np.linalg.norm(rot_about(w, r, t, p) - qq))
    sols = sp3(w, r, p, qq, dl)
    assert any(abs(wrap(a - t)) < 1e-6 for a in sols)
    for a in sols:
        worst = max(worst, abs(float(np.linalg.norm(rot_about(w, r, a, p) - qq)) - dl))
    n0[3] += len(sp3(w, r, p, qq, rng.uniform(0, 4))) == 0
assert worst < 1e-9

# ---------------------------------------------------------------- (6) planar 2R = Subproblem 3 + Subproblem 1
z = np.array([0, 0, 1.0])
for _ in range(1000):
    th = rng.uniform(-math.pi, math.pi, 2)
    tip = np.array([L1 * math.cos(th[0]) + L2 * math.cos(th[0] + th[1]), L1 * math.sin(th[0]) + L2 * math.sin(th[0] + th[1]), 0])
    tip0, q2 = np.array([L1 + L2, 0, 0]), np.array([L1, 0, 0])
    for b in sp3(z, q2, tip0, np.zeros(3), float(np.linalg.norm(tip))):    # joint 2: distance from end-effector to base
        a = sp1(z, np.zeros(3), rot_about(z, q2, b, tip0), tip)            # joint 1: turn onto the target
        assert any(abs(wrap(a - x)) < 1e-9 and abs(wrap(b - y)) < 1e-9 for x, y in ik2r(tip[0], tip[1], L1, L2))

out(p0=vec(p0, 3), rad=rad, qt=vec(q_target, 4), t1_deg=math.degrees(t1), phi_p=phi_p,
    d=vec(d, 4), a2=a2, b2=b2, g2=g2, g=math.sqrt(g2), k12=k12,
    s2a=f"({s2d[0][0]:.2f}°, {s2d[0][1]:.2f}°)", s2b=f"({s2d[1][0]:.2f}°, {s2d[1][1]:.2f}°)",
    c1=vec(alpha_beta[0], 4), c2=vec(alpha_beta[1], 4),
    delta=delta, dprime=dprime, cos_d=cos_d, s3a=s3d[0], s3b=s3d[1], acos_d=math.degrees(math.acos(cos_d)),
    N=N, worst=worst, sp2_none=100 * n0[2] / N, sp3_none=100 * n0[3] / N)
