"""Examples of Section 3.2.

Example 3.2.1: the angle between the axis of a polishing tool and the normal of the workpiece surface (dot product),
               and the split of the tool axis into a part along the normal and a part along the surface (projection
               formula).
Example 3.2.2: the moment m = r × F on a force sensor, computed three ways and checked against each other: the
               component formula, the skew-symmetric matrix [r]F, and geometry (lever arm × force).
Example 3.2.3: three points determine the top of a fixture; the distance of a fourth point from it = scalar triple
               product / parallelogram area; checked against the determinant and against "dot product with the normal".
Also verified: the vector triple product formula, [a]² = aaᵀ − |a|²I, Lagrange's identity and the Jacobi identity
(random vectors); the determinant of a left-handed frame is −1.
"""
import math

import numpy as np

from _vec import cross, d, skew, unit
from bookout import out, tex, vec

# ---------------------------------------------------------------- Example 3.2.1: dot product and projection
u_raw = np.array([0.05, 0.12, -0.99])           # direction of the tool axis (in the base frame {a}, not normalized)
u = unit(u_raw)
n = np.array([0.0, -math.sin(d(10)), math.cos(d(10))])   # outward normal of the surface (unit vector)
m_in = -n                                        # the tool should point into the surface along the inward normal
cos_t = float(u @ m_in)                          # Eq. (3.2.3): component formula
theta = math.degrees(math.acos(cos_t))
# Geometric check: the same angle from the length of the cross product, |u × m| = sin θ
assert abs(math.degrees(math.asin(np.linalg.norm(np.cross(u, m_in)))) - theta) < 1e-9
u_par = (u @ n) * n                               # Eq. (3.2.5): the part along the normal
u_perp = u - u_par                               # the part along the surface
assert abs(u_perp @ n) < 1e-15 and abs(np.linalg.norm(u_perp) - math.sin(math.radians(theta))) < 1e-12

# ---------------------------------------------------------------- Example 3.2.2: cross product and moment
r = np.array([0.08, 0.03, -0.10])               # sensor centre → centre of mass of the part, m
mass, g = 1.5, 9.81
F = np.array([0.0, 0.0, -mass * g])             # weight, N
m1 = cross(r, F)                                 # component formula (3.2.9)
m2 = skew(r) @ F                                 # skew-symmetric matrix (3.2.10)
assert np.allclose(m1, m2) and np.allclose(m1, np.cross(r, F))
rho = math.hypot(r[0], r[1])                     # lever arm: distance from the centre of mass to "the vertical line through the sensor centre"
assert abs(np.linalg.norm(m1) - rho * mass * g) < 1e-12        # geometry: |m| = lever arm × force
assert abs(m1 @ r) < 1e-12 and abs(m1 @ F) < 1e-12             # m is perpendicular to r and F
assert np.allclose(skew(r).T, -skew(r))

# ---------------------------------------------------------------- Example 3.2.3: scalar triple product
P = np.array([[400, -200, 100], [700, -180, 103], [450, 150, 98], [680, 120, 104]], float)   # mm
a, b, c = P[1] - P[0], P[2] - P[0], P[3] - P[0]
axb = np.cross(a, b)
area = np.linalg.norm(axb)                       # parallelogram area, mm²
mixed = float(axb @ c)                           # scalar triple product = signed volume of the parallelepiped, mm³
det = float(np.linalg.det(np.column_stack([a, b, c])))
assert abs(mixed - det) < 1e-6 * abs(det)        # theorem: scalar triple product = determinant
h = mixed / area                                 # signed distance from the fourth point to the top, mm
nhat = axb / area
assert abs(h - nhat @ c) < 1e-9                  # second method: dot product with the unit normal
assert abs(np.cross(b, c) @ a - mixed) < 1e-6 and abs(np.cross(c, a) @ b - mixed) < 1e-6   # unchanged by cyclic permutation
tilt = math.degrees(math.acos(abs(nhat[2])))     # tilt of the top relative to the horizontal

# ---------------------------------------------------------------- right-handed and left-handed frames
X, Y, Z = np.array([0, 1.0, 0]), np.array([1.0, 0, 0]), np.array([0, 0, 1.0])   # three axes given by a configuration file
det_lh = float(np.linalg.det(np.column_stack([X, Y, Z])))
assert abs(det_lh + 1) < 1e-12 and abs(np.cross(X, Y) @ Z + 1) < 1e-12

# ---------------------------------------------------------------- identities (random vectors)
rng = np.random.default_rng(3)
for _ in range(200):
    A, B, Cc = rng.normal(size=(3, 3))
    assert np.allclose(np.cross(A, np.cross(B, Cc)), B * (A @ Cc) - Cc * (A @ B))      # vector triple product
    assert np.allclose(np.cross(np.cross(A, B), Cc), B * (A @ Cc) - A * (B @ Cc))
    assert np.allclose(skew(A) @ skew(A), np.outer(A, A) - (A @ A) * np.eye(3))       # [a]²
    assert abs(np.linalg.norm(np.cross(A, B)) ** 2 - ((A @ A) * (B @ B) - (A @ B) ** 2)) < 1e-9   # Lagrange's identity
    jac = np.cross(A, np.cross(B, Cc)) + np.cross(B, np.cross(Cc, A)) + np.cross(Cc, np.cross(A, B))
    assert np.allclose(jac, 0)                                                          # Jacobi identity
    assert np.allclose(skew(A) @ skew(A) @ skew(A), -(A @ A) * skew(A))                # [a]³ = −|a|²[a]

out(
    u1=u[0], u2=u[1], u3=u[2], u_norm=float(np.linalg.norm(u_raw)), s10=math.sin(d(10)), c10=math.cos(d(10)),
    cos_t=cos_t, theta=theta, un=float(u @ n), u_perp=vec(u_perp, 4), u_perp_len=float(np.linalg.norm(u_perp)),
    Fz=F[2], m_vec=vec(m1, 4), mx=m1[0], my=m1[1], m_len=float(np.linalg.norm(m1)), rho=rho, mg=mass * g,
    skew_r=tex(skew(r), 2),
    a_vec=vec(a, 0), b_vec=vec(b, 0), c_vec=vec(c, 0), axb=vec(axb, 0), area=area, mixed=mixed, h=h, tilt=tilt,
    det_lh=det_lh,
)
