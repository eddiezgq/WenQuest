"""Examples of Section 3.3.

Example 3.3.1: a camera turned 30° about the vertical axis; Example 3.1.1 recomputed with the direction cosine matrix.
Example 3.3.2: a camera looking down on a conveyor. The components in the base frame {a} of the three axes of the camera
           frame {b} are known (optical axis z_b pointing down and leaning 20°); from them write the direction cosine
           matrix R_ab and check its orthogonality and determinant; the camera measures the displacement d_b of a part
           relative to the camera; find d_a and compute back.
Example 3.3.3: the same camera mounted through a bracket: the bracket {c} is turned −90° about z relative to {a}, and
           the camera {b} is turned 160° about x relative to the bracket. Check R_ab = R_ac R_cb.
Also: check that R preserves dot and cross products (Theorems 3.3.3 and 3.3.4), and that for a left-handed frame
the cross product changes sign.
"""
import math

import numpy as np

from _vec import d, is_rotation, rot_x, rot_z
from bookout import out, tex, vec

c20, s20 = math.cos(d(20)), math.sin(d(20))
xb = np.array([0.0, -1.0, 0.0])
yb = np.array([-c20, 0.0, s20])
zb = np.array([-s20, 0.0, -c20])
R_ab = np.column_stack([xb, yb, zb])             # column j = axis j of {b} written in {a}

# direction cosines: r_ij = (axis i of {a})·(axis j of {b}) = cos(angle)
A_axes = np.eye(3)
DC = np.array([[A_axes[:, i] @ R_ab[:, j] for j in range(3)] for i in range(3)])
assert np.allclose(DC, R_ab)
ang = np.degrees(np.arccos(np.clip(R_ab, -1, 1)))   # the nine angles, degrees

assert np.allclose(R_ab.T @ R_ab, np.eye(3))        # Theorem 3.3.2: orthogonal
det = float(np.linalg.det(R_ab))
mixed = float(np.cross(xb, yb) @ zb)                # Eq. (3.2.12): determinant = scalar triple product
assert abs(det - 1) < 1e-12 and abs(mixed - 1) < 1e-12

d_b = np.array([0.12, -0.05, 0.60])                 # displacement measured by the camera, m
d_a = R_ab @ d_b                                    # Eq. (3.3.3)
# second method: expand axis by axis, d = d1 x_b + d2 y_b + d3 z_b
assert np.allclose(d_a, d_b[0] * xb + d_b[1] * yb + d_b[2] * zb)
back = R_ab.T @ d_a                                 # Eq. (3.3.4)
assert np.allclose(back, d_b)
assert abs(np.linalg.norm(d_a) - np.linalg.norm(d_b)) < 1e-12

# ---------------------------------------------------------------- Example 3.3.3: mounting through a bracket
R_ac = rot_z(d(-90))
R_cb = rot_x(d(160))
assert np.allclose(R_ac @ R_cb, R_ab)               # Eq. (3.3.6)
assert is_rotation(R_ac) and is_rotation(R_cb)

# ---------------------------------------------------------------- Example 3.3.1: Example 3.1.1 recomputed
R30 = rot_z(d(30))
d1_a = np.array([0.30, 0.20, 0.0])
d1_b = R30.T @ d1_a
Lp, ph = math.hypot(0.30, 0.20), math.atan2(0.20, 0.30) - d(30)       # the projection method of Section 3.1
assert np.allclose(d1_b, [Lp * math.cos(ph), Lp * math.sin(ph), 0.0])

# ---------------------------------------------------------------- dot and cross products preserved
rng = np.random.default_rng(7)
for _ in range(200):
    u, v = rng.normal(size=(2, 3))
    assert abs((R_ab @ u) @ (R_ab @ v) - u @ v) < 1e-12                       # Theorem 3.3.3
    assert np.allclose(np.cross(R_ab @ u, R_ab @ v), R_ab @ np.cross(u, v))   # Theorem 3.3.4
    M = np.diag([1.0, 1.0, -1.0])                                             # mirror reflection, det = −1
    assert np.allclose(np.cross(M @ u, M @ v), -(M @ np.cross(u, v)))

out(
    c20=c20, s20=s20, R_ab=tex(R_ab, 4), R_abT=tex(R_ab.T, 4),
    d_a=tex(d_a, 4), d_a_vec=vec(d_a, 4), da1=d_a[0], da2=d_a[1], da3=d_a[2],
    L=float(np.linalg.norm(d_b)), depth=-d_a[2],
    ang11=ang[0, 0], ang13=ang[0, 2], ang33=ang[2, 2], ang31=ang[2, 0], ang21=ang[1, 0], ang32=ang[2, 1],
    R_ac=tex(R_ac, 4), R_cb=tex(R_cb, 4), c160=math.cos(d(160)), s160=math.sin(d(160)),
)
