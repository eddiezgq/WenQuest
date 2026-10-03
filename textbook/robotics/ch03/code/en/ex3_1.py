"""Examples of Section 3.1.

Example 3.1.1: the displacement vector d from the gripper to the part has components (0.30, 0.20, 0) m in the robot
               base frame {a}; the camera frame {b} is turned through 30° relative to {a} about the vertical axis.
               Find the components of d in {b} geometrically, by "projection", and verify that the lengths measured
               in the two frames are the same. Recompute once with the transformation matrix of Section 3.3; the two
               methods must agree.
Example 3.1.2: the displacement e from the part to the fixture is (−0.10, 0.25, 0) m in {a}. Find the displacement
               d + e from the gripper to the fixture; then demonstrate the wrong result of adding d in {b} directly
               to e in {a}, and give the error.
"""
import math

import numpy as np

from _vec import d, rot_z
from bookout import out

# ---------------------------------------------------------------- Example 3.1.1
d_a = np.array([0.30, 0.20, 0.0])          # m, components in {a}
beta = d(30)                               # angle of {b} relative to {a} about the z axis, rad

L_a = math.sqrt(d_a @ d_a)                 # Eq. (3.1.4): length from the components in {a}
phi_a = math.atan2(d_a[1], d_a[0])         # angle between d and the x_a axis
phi_b = phi_a - beta                       # angle between d and the x_b axis: measured from x_b, β less
d_b = np.array([L_a * math.cos(phi_b), L_a * math.sin(phi_b), 0.0])   # projected onto the two axes of {b}

# Second method (Section 3.3): d_b = R_abᵀ d_a; the columns of R_ab are the components of the three axes of {b} in {a}
R_ab = rot_z(beta)
assert np.allclose(R_ab.T @ d_a, d_b)
L_b = math.sqrt(d_b @ d_b)
assert abs(L_a - L_b) < 1e-12                                   # length is an invariant
# Third method: component = dot product of the vector with the unit vector of each axis (Section 3.2)
xb, yb = R_ab[:, 0], R_ab[:, 1]
assert abs(d_a @ xb - d_b[0]) < 1e-12 and abs(d_a @ yb - d_b[1]) < 1e-12

# ---------------------------------------------------------------- Example 3.1.2
e_a = np.array([-0.10, 0.25, 0.0])
s_a = d_a + e_a                            # right: add components in the same frame
wrong = d_b + e_a                          # wrong: components in {b} added to components in {a}
err = np.linalg.norm(wrong - s_a)
# The right way can also be done entirely in {b}: e_b = R_abᵀ e_a, then d_b + e_b converted back to {a}
assert np.allclose(R_ab @ (d_b + R_ab.T @ e_a), s_a)

out(
    L=L_a, phi_a_deg=math.degrees(phi_a), phi_b_deg=math.degrees(phi_b),
    db1=d_b[0], db2=d_b[1], L_b=L_b, c30=math.cos(beta),
    s1=s_a[0], s2=s_a[1], s_len=float(np.linalg.norm(s_a)),
    w1=wrong[0], w2=wrong[1], w_len=float(np.linalg.norm(wrong)), err=err, err_mm=err * 1000,
)
