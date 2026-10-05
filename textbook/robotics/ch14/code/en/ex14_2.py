"""Section 14.2: planar two-link and three-link arms.

(1) Example 14.2.1: the 2R arm reaching (0.45, 0.35) m. The geometric method (law of cosines + two direction angles) and
    the algebraic method (cos θ1, sin θ1 as the unknowns of a linear system) give the same result, which is also the same
    as that of Newton's method in Chapter 7 (checked in Program 14.1.1).
(2) Numerical details: for targets exactly on the outer boundary (arm straight), the arccos form judges some "out of reach"
    because of rounding, while the factorized form of Eq. (14.2.6) misses none; when the arm is nearly straight, θ2 is
    extremely sensitive to the target position (Eq. (14.2.7)), checked with a difference quotient.
(3) Example 14.2.2: the planar 3R arm (with a tool l3 = 0.1 m) reaching (0.6, 0.05) m with the tool pointing down (φ = −90°).
(4) The family of solutions when the position is given but not the orientation: target (0.75, 0.10) m; the tool
    orientation φ can take values only in a limited range (the wrist point must lie inside the ring of the 2R arm).
(5) Joints 2, 3, 4 of the UR5e: the position of the wrist point P56 in the plane of joints 2–4 agrees with the formula of
    the planar 3R arm.
"""
import math

import numpy as np

from _ik import H1, H2, L1, L2, W4, fk2r, fk3r, ik2r, ik2r_naive, ik3r, ur_fk, wrap
from bookout import out

l1, l2, l3 = 0.425, 0.392, 0.1

# ---------------------------------------------------------------- (1) Example 14.2.1: two methods
x, y = 0.45, 0.35
r = math.hypot(x, y)
c2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2)
beta = math.atan2(y, x)
psi = math.acos((l1 * l1 + r * r - l2 * l2) / (2 * l1 * r))     # angle between upper arm and the line OP (law of cosines)
geo = [(beta - psi, math.acos(c2)), (beta + psi, -math.acos(c2))]   # elbow down, elbow up
alg = []
for t2 in (math.acos(c2), -math.acos(c2)):
    k1, k2 = l1 + l2 * math.cos(t2), l2 * math.sin(t2)
    c1 = (k1 * x + k2 * y) / (k1 * k1 + k2 * k2)
    s1 = (k1 * y - k2 * x) / (k1 * k1 + k2 * k2)
    alg.append((math.atan2(s1, c1), t2))
lib = ik2r(x, y, l1, l2)
for g, a, b in zip(geo, alg, lib):
    assert abs(wrap(g[0] - a[0])) < 1e-12 and abs(g[1] - a[1]) < 1e-12
    assert abs(wrap(g[0] - b[0])) < 1e-12 and abs(g[1] - b[1]) < 1e-12
    assert np.linalg.norm(fk2r(g, l1, l2) - [x, y]) < 1e-12
k1d, k2d = l1 + l2 * math.cos(geo[0][1]), l2 * math.sin(geo[0][1])

# ---------------------------------------------------------------- (2) numerical accuracy
rng = np.random.default_rng(142)
N = 1000
fail_naive = fail_stable = 0
c_bad = None
for a in rng.uniform(-math.pi, math.pi, N):           # targets exactly on the outer boundary (arm straight)
    p = (l1 + l2) * np.array([math.cos(a), math.sin(a)])
    if len(ik2r_naive(p[0], p[1], l1, l2)) == 0:
        fail_naive += 1
        c = (p[0] ** 2 + p[1] ** 2 - l1 * l1 - l2 * l2) / (2 * l1 * l2)
        c_bad = c_bad or repr(float(c))              # cos θ2 slightly above 1 after rounding
    fail_stable += len(ik2r(p[0], p[1], l1, l2)) == 0
assert fail_stable == 0 and fail_naive > 0

# When the arm is nearly straight, a tiny radial change of the target causes a large change of θ2: from
# r² = l1² + l2² + 2 l1 l2 cos θ2 (Eq. (14.2.1)), dθ2/dr = −r / (l1 l2 sin θ2) (Eq. (14.2.7)). At θ2 = 1°, move the target 1 μm radially inwards:
t2s = math.radians(1.0)
pS = fk2r((0.4, t2s), l1, l2)
rS = float(np.linalg.norm(pS))
dr = -1e-6                                             # 1 μm inwards (at θ2 = 1° the target is about 62 μm from the outer boundary)
pS2 = pS * (rS + dr) / rS
d_ik = ik2r(pS2[0], pS2[1], l1, l2)[0][1] - ik2r(pS[0], pS[1], l1, l2)[0][1]
d_formula = -rS * dr / (l1 * l2 * math.sin(t2s))
assert abs(d_ik - d_formula) < 0.03 * abs(d_formula)
t2m = math.radians(90)                                  # for comparison: the same 1 μm move at θ2 = 90°
pM = fk2r((0.4, t2m), l1, l2)
rM = float(np.linalg.norm(pM))
d_mid = -rM * dr / (l1 * l2 * math.sin(t2m))

# ---------------------------------------------------------------- (3) Example 14.2.2: planar 3R, position and orientation given
px, py, phi = 0.6, 0.05, math.radians(-90)
wx, wy = px - l3 * math.cos(phi), py - l3 * math.sin(phi)
s3 = ik3r(px, py, phi, l1, l2, l3)
assert len(s3) == 2
for s in s3:
    f = fk3r(s, l1, l2, l3)
    assert abs(f[0] - px) < 1e-12 and abs(f[1] - py) < 1e-12 and abs(wrap(f[2] - phi)) < 1e-12
s3d = [tuple(math.degrees(t) for t in s) for s in s3]

# ---------------------------------------------------------------- (4) position only: feasible range of the tool orientation φ
pB = np.array([0.75, 0.10])
rB = float(np.linalg.norm(pB))
# the wrist point w = p − l3 e(φ) must satisfy |w| ≤ l1 + l2 (the inner boundary 0.033 m has no effect here): |p|² + l3² − 2 l3 |p| cos(φ − β) ≤ (l1 + l2)²
bB = math.atan2(pB[1], pB[0])
cmin = (rB * rB + l3 * l3 - (l1 + l2) ** 2) / (2 * l3 * rB)
half = math.acos(cmin)
lo, hi = bB - half, bB + half
grid = np.linspace(-math.pi, math.pi, 7201)
ok = np.array([len(ik3r(pB[0], pB[1], f, l1, l2, l3)) > 0 for f in grid])
inside = np.array([abs(wrap(f - bB)) <= half for f in grid])
assert (ok == inside).all()

# ---------------------------------------------------------------- (5) joints 2, 3, 4 of the UR5e form a planar 3R arm
worst = 0.0
for _ in range(1000):
    t2, t3, t4 = rng.uniform(-math.pi, math.pi, 3)
    T = ur_fk([0, t2, t3, t4, 0, 0])
    pw = T[:3, 3] - W4 * T[:3, 1]                       # wrist point P56
    # side view (looking along −y): horizontal coordinate u = −x, height z; joint angles count as −θ (axes along −y); third segment vertical down at the zero position
    a1, a2, a3 = -t2, -t2 - t3, -t2 - t3 - t4 - math.pi / 2
    u = L1 * math.cos(a1) + L2 * math.cos(a2) + H2 * math.cos(a3)
    z = H1 + L1 * math.sin(a1) + L2 * math.sin(a2) + H2 * math.sin(a3)
    worst = max(worst, abs(-pw[0] - u), abs(pw[2] - z))
assert worst < 1e-12

out(x=x, y=y, r=r, c2=c2, beta_deg=math.degrees(beta), psi_deg=math.degrees(psi), t2_deg=math.degrees(math.acos(c2)),
    k1=k1d, k2=k2d,
    geo1=f"({math.degrees(geo[0][0]):.2f}°, {math.degrees(geo[0][1]):.2f}°)",
    geo2=f"({math.degrees(geo[1][0]):.2f}°, {math.degrees(geo[1][1]):.2f}°)",
    t1d=math.degrees(geo[0][0]), t1u=math.degrees(geo[1][0]),
    N=N, fail_naive=fail_naive, c_bad=c_bad, fail_pct=100 * fail_naive / N,
    d_ik_deg=math.degrees(abs(d_ik)), d_mid_deg=math.degrees(abs(d_mid)), d_ratio=abs(d_ik / d_mid), rS=rS,
    wx=wx, wy=wy, s3a=f"({s3d[0][0]:.2f}°, {s3d[0][1]:.2f}°, {s3d[0][2]:.2f}°)", s3b=f"({s3d[1][0]:.2f}°, {s3d[1][1]:.2f}°, {s3d[1][2]:.2f}°)",
    rB=rB, phi_lo=math.degrees(lo), phi_hi=math.degrees(hi), phi_span=math.degrees(2 * half), bB_deg=math.degrees(bB),
    ur_planar=worst)
