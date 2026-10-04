"""Examples of Section 6.1.

Example 6.1.1: the pole of a planar displacement. A part on a tabletop moves from pose A to pose B; find a point c such that one turn about c performs the whole displacement.
            Two methods: solving the linear equation (I − R)c = p (Eq. (6.1.2)); intersecting the perpendicular bisectors of the lines joining two points to their new positions (geometric construction).
Example 6.1.2: a UR5e carries a part from the conveyor to the fixture; the displacement between the two poses of the part is a screw motion.
            Find ŝ, θ, d, q and h by the construction of Theorem 6.1.2; find q again with the closed form (6.1.7);
            finally take the eight corners of the part and verify that "turn θ about the axis, then slide d along it" agrees point by point with the displacement, and that the two steps can be swapped.
"""
import math

import numpy as np

from _screw import exp3, log3, pose, rot_z
from bookout import out, tex, vec

d = math.radians

# ---------------------------------------------------------------- Example 6.1.1, planar
def rot2(t):
    return np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])


pA, phiA = np.array([0.30, 0.05]), d(0)          # position (m) and heading of the reference point of the part
pB, phiB = np.array([0.54, 0.13]), d(60)
R2 = rot2(phiB - phiA)
p2 = pB - R2 @ pA                                # p in the displacement x′ = R x + p
c_lin = np.linalg.solve(np.eye(2) - R2, p2)      # method 1: (I − R) c = p

# method 2: two points P1, P2 of the part each move from old to new position; the perpendicular bisectors of the two joining lines meet at the pole
P1, P2 = pA, pA + np.array([0.15, 0.0])          # reference point and the point 0.15 m along the long side of the part
Q1, Q2 = R2 @ P1 + p2, R2 @ P2 + p2


def bisector(a, b):
    m = (a + b) / 2
    n = b - a                                    # perpendicular bisector: n · (x − m) = 0
    return n, n @ m


n1, c1 = bisector(P1, Q1)
n2, c2 = bisector(P2, Q2)
c_geo = np.linalg.solve(np.array([n1, n2]), np.array([c1, c2]))
assert np.allclose(c_lin, c_geo, atol=1e-12)
assert np.allclose(R2 @ (pA - c_lin) + c_lin, pB)                       # a turn of 60° about c takes A to B
assert abs(np.linalg.norm(pA - c_lin) - np.linalg.norm(pB - c_lin)) < 1e-12
cot = 1 / math.tan((phiB - phiA) / 2)
c_formula = 0.5 * (p2 + cot * np.array([-p2[1], p2[0]]))               # planar form of Eq. (6.1.7)
assert np.allclose(c_formula, c_lin)

# ---------------------------------------------------------------- Example 6.1.2, spatial
p1 = np.array([0.5, -0.2, 0.1])                  # position of the part on the conveyor (m), orientation the same as {s}
T1 = pose(np.eye(3), p1)
R_2 = rot_z(d(90))                               # into the fixture: turned 90° about the vertical, position raised
T2 = pose(R_2, np.array([0.3, 0.4, 0.25]))
D = T2 @ np.linalg.inv(T1)                       # displacement: x′ = R x + p (described in {s}), T2 = D T1
R, p = D[:3, :3], D[:3, 3]

# construction of Theorem 6.1.2
s, th = log3(R)                                  # Euler's theorem: axis and angle
dd = float(s @ p)                                # translation along the axis
p_perp = p - dd * s
A = np.eye(3) - R
# solve (I − R) q = p⊥ in the plane perpendicular to ŝ: least squares (I − R is singular, but p⊥ lies in its range), then remove the component along ŝ
q = np.linalg.lstsq(A, p_perp, rcond=None)[0]
q = q - (q @ s) * s
assert np.allclose(A @ q, p_perp, atol=1e-12)
q_formula = 0.5 * (p_perp + (1 / math.tan(th / 2)) * np.cross(s, p_perp))   # Eq. (6.1.7)
assert np.allclose(q, q_formula, atol=1e-12)
h = dd / th


def screw_motion(x, frac=1.0):
    """Turn frac·θ about the axis through q with direction ŝ, then slide frac·d along ŝ."""
    return q + exp3(s * th * frac) @ (x - q) + frac * dd * s


a, b, c = 0.06, 0.04, 0.03                       # half-lengths of the part (m)
corners = [p1 + np.array([x, y, z]) for x in (-a, a) for y in (-b, b) for z in (-c, c)]
for x in corners:
    xd = R @ x + p
    assert np.allclose(screw_motion(x), xd, atol=1e-12)                   # agrees point by point
    swapped = q + exp3(s * th) @ (x + dd * s - q)                         # slide first, then turn
    assert np.allclose(swapped, xd, atol=1e-12)
# a point on the axis only moves by d along the axis
assert np.allclose(screw_motion(q) - q, dd * s)
# the helix traced by the centre of the part: its distance to the axis stays the same
r0 = np.linalg.norm(np.cross(s, p1 - q))
for f in np.linspace(0, 1, 11):
    x = screw_motion(p1, f)
    assert abs(np.linalg.norm(np.cross(s, x - q)) - r0) < 1e-12

out(R2=tex(R2, 4), p2=vec(p2, 4), c=vec(c_lin, 4), cx=c_lin[0], cy=c_lin[1], rA=float(np.linalg.norm(pA - c_lin)),
    D=tex(D, 3), p=vec(p, 3), s=vec(s, 3), th_deg=math.degrees(th), d=dd, p_perp=vec(p_perp, 3),
    q=vec(q, 3), h=h, h_mm_per_deg=h * 1000 * math.pi / 180, r0=r0, cot=1 / math.tan(th / 2),
    s_cross=vec(np.cross(s, p_perp), 3))
