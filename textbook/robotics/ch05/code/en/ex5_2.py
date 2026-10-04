"""Examples 5.2.1 and 5.2.2: writing down a homogeneous transformation matrix, and two of its uses.

5.2.1 Write T_ws (the UR5e base relative to the worktable) and T_wc (the camera relative to the worktable: 0.90 m high,
      optical axis 15° off the vertical), filling them in column by column as "the three axes and the origin of {b}",
      and compare with assembling them from the blocks R and p.
      Use T_wc to take a point measured by the camera, (0.05, −0.02, 0.885) m (on the top face of the gear blank), into {w},
      and take the direction of the optical axis, (0, 0, 1), into {w} as a free vector:
      a point has 1 as its fourth component and the translation is added; a direction has 0, and the translation drops out
      by itself. Compare term by term with Theorem 5.1.1.
5.2.2 Displacement operator: a part on the table turns 90° about its own centre and is translated; check Theorem 5.2.3
      (distances and cross products are preserved).
"""
import math

import numpy as np

from _frames import DEG, P_WC, T, T_wc, T_ws, hdir, hom, is_se3, rot_axis, rot_z, texm, trans, vecm
from bookout import out

# ---------------------------------------------------------------- Example 5.2.1
Tws = T_ws()
Twc = T_wc()
# Fill in column by column: the components of the three axes of {c} in {w}, and the origin
c15, s15 = math.cos(15 * DEG), math.sin(15 * DEG)
xc = np.array([0, 1, 0.0])
yc = np.array([c15, 0, -s15])
zc = np.array([-s15, 0, -c15])
Twc_cols = np.eye(4)
Twc_cols[:3, 0], Twc_cols[:3, 1], Twc_cols[:3, 2], Twc_cols[:3, 3] = xc, yc, zc, P_WC
assert np.allclose(Twc_cols, Twc, atol=1e-15)
assert is_se3(Twc) and is_se3(Tws)
assert abs(np.dot(np.cross(xc, yc), zc) - 1) < 1e-15              # right-handed

p_c = np.array([0.05, -0.02, 0.885])         # a point on the top face of the gear blank measured by the camera, m
p_w = (Twc @ hom(p_c))[:3]
p_w_thm = Twc[:3, :3] @ p_c + Twc[:3, 3]     # Theorem 5.1.1
assert np.allclose(p_w, p_w_thm, atol=1e-15)
axis_w = (Twc @ hdir([0, 0, 1]))
assert abs(axis_w[3]) < 1e-15 and np.allclose(axis_w[:3], zc)
# Where the optical axis meets the table top (z_w = 0): go a distance t along the axis from the camera origin until z = 0
t_hit = -P_WC[2] / zc[2]
hit = P_WC + t_hit * zc

# ---------------------------------------------------------------- Example 5.2.2 displacement operator
# The four corners of the part (a 120 mm × 80 mm rectangular block), initially centred at (0.80, 0.45) m; it turns 90° about its own centre, then the whole block is translated by (−0.10, 0.20) m
ctr = np.array([0.80, 0.45, 0.0])
corners = np.array([[0.06, 0.04, 0], [-0.06, 0.04, 0], [-0.06, -0.04, 0], [0.06, -0.04, 0]]) + ctr
D = trans(-0.10, 0.20, 0) @ trans(*ctr) @ T(rot_z(math.pi / 2)) @ trans(*(-ctr))      # one displacement operator
moved = np.array([(D @ hom(p))[:3] for p in corners])
assert is_se3(D)
# Theorem 5.2.3: the distance between any two points is preserved, and cross products "turn along"
rng = np.random.default_rng(5)
for _ in range(200):
    G = T(rot_axis(rng.normal(size=3), rng.uniform(-3, 3)), rng.normal(size=3))
    a, b, c = rng.normal(size=(3, 3))
    ga, gb, gc = ((G @ hom(x))[:3] for x in (a, b, c))
    assert abs(np.linalg.norm(ga - gb) - np.linalg.norm(a - b)) < 1e-12
    assert np.allclose(np.cross(gb - ga, gc - ga), G[:3, :3] @ np.cross(b - a, c - a), atol=1e-12)
assert all(abs(np.linalg.norm(moved[i] - moved[j]) - np.linalg.norm(corners[i] - corners[j])) < 1e-15
           for i in range(4) for j in range(4))
# Eq. (5.2.10): rotation about a point c = Trans(c) Rot Trans(−c) = [[R, c − R c], [0, 1]]
Rc = T(rot_z(math.pi / 2))
assert np.allclose(trans(*ctr) @ Rc @ trans(*(-ctr)), T(rot_z(math.pi / 2), ctr - rot_z(math.pi / 2) @ ctr))
# Theorem 5.2.2: closure and inverses (Eqs. (5.2.7) and (5.2.8))
for _ in range(200):
    A = T(rot_axis(rng.normal(size=3), rng.uniform(-3, 3)), rng.normal(size=3))
    B = T(rot_axis(rng.normal(size=3), rng.uniform(-3, 3)), rng.normal(size=3))
    AB = A @ B
    assert is_se3(AB) and np.allclose(AB[:3, 3], A[:3, :3] @ B[:3, 3] + A[:3, 3])
    Ai = T(A[:3, :3].T, -A[:3, :3].T @ A[:3, 3])
    assert np.allclose(A @ Ai, np.eye(4)) and np.allclose(Ai @ A, np.eye(4))
# Midpoints go to midpoints (a numerical check of Exercise 5.2.5)
mid = (corners[0] + corners[2]) / 2
assert np.allclose((D @ hom(mid))[:3], (moved[0] + moved[2]) / 2)

out(
    Tws=texm(Tws, 2), Twc=texm(Twc, 4), c15=c15, s15=s15,
    pw=vecm(p_w, 4), pw_x=p_w[0], pw_y=p_w[1], pw_z=p_w[2],
    axw=vecm(axis_w, 4), hit_x=hit[0], hit_y=hit[1], t_hit=t_hit,
    D=texm(D, 2), D_p=D[:3, 3].tolist(), moved=texm(moved.T, 2),
    m1=vecm(moved[0], 2),
)
