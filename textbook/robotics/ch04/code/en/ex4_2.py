"""Examples of Section 4.2.

Example 4.2.1: the tool frame {b} has orientation Rot(ẑ, 30°) relative to {s}; a point on the tool has components
(0.1, 0, 0.05) m in {b}; find its components in {s}.
Example 4.2.2: the same two 90° turns in a different order give a different result (the book experiment).
Example 4.2.3: turning 45° about the fixed axis x̂_s and 45° about the body axis x̂_b give different results.
"""
import math

import numpy as np

from bookout import out, tex, vec


from _rot import is_rotation, rot_x, rot_z  # noqa: E402

d = math.radians

# Example 4.2.1
R_sb = rot_z(d(30))
p_b = np.array([0.1, 0.0, 0.05])
p_s = R_sb @ p_b
assert is_rotation(R_sb)
assert abs(np.linalg.norm(p_s) - np.linalg.norm(p_b)) < 1e-12

# Example 4.2.2: the book turns 90° about x, then 90° about z (fixed axes, left multiplication); compare with the reverse order
A = rot_z(d(90)) @ rot_x(d(90))
B = rot_x(d(90)) @ rot_z(d(90))
assert is_rotation(A) and is_rotation(B) and not np.allclose(A, B)
# where the spine direction ŷ (the book's own y axis) ends up
spine_A, spine_B = A @ np.array([0, 1, 0]), B @ np.array([0, 1, 0])

# Example 4.2.3: starting from R_sb = Rot(z,30°), turn 45° about the fixed axis x̂_s, and about the body axis x̂_b
R_fixed = rot_x(d(45)) @ R_sb      # left multiplication
R_body = R_sb @ rot_x(d(45))       # right multiplication
assert is_rotation(R_fixed) and is_rotation(R_body) and not np.allclose(R_fixed, R_body)
# about the body axis: x̂_b does not move; about the fixed axis: components along x̂_s do not change
assert np.allclose(R_body[:, 0], R_sb[:, 0])
assert np.allclose(R_fixed[0, :], R_sb[0, :])

out(
    Rsb=tex(R_sb), p_s=tex(p_s), p_s_x=p_s[0], p_s_y=p_s[1], c30=math.cos(d(30)), norm_p=float(np.linalg.norm(p_b)),
    Rx90=tex(rot_x(d(90))), Rz90=tex(rot_z(d(90))), A=tex(A), B=tex(B), spine_A=vec(spine_A), spine_B=vec(spine_B),
    Rx45=tex(rot_x(d(45))), R_fixed=tex(R_fixed), R_body=tex(R_body), c45=math.cos(d(45)),
)
