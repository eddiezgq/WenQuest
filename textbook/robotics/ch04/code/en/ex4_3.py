"""Examples of Section 4.3.

Example 4.3.1: R = Rot(ẑ,30°) Rot(x̂,45°) (the body-axis result of Example 4.2.3). Find its rotation axis and angle by
Euler's theorem: the axis is the eigenvector for eigenvalue 1, the angle comes from the trace, tr R = 1 + 2 cos θ;
turning through that angle about that axis must give back the original R.
"""
import math

import numpy as np

from _rot import is_rotation, rot_axis, rot_x, rot_z
from bookout import out, tex, vec

d = math.radians
R = rot_z(d(30)) @ rot_x(d(45))
assert is_rotation(R)

# proof of Theorem 4.3.1: det(R − I) = 0
det_RI = np.linalg.det(R - np.eye(3))
assert abs(det_RI) < 1e-12

# the axis: the eigenvector for eigenvalue 1
vals, vecs = np.linalg.eig(R)
k = int(np.argmin(abs(vals - 1)))
w = np.real(vecs[:, k])
w = w / np.linalg.norm(w)
assert np.allclose(R @ w, w)

# the angle: tr R = 1 + 2 cos θ, θ ∈ [0, π]
tr = float(np.trace(R))
theta = math.acos((tr - 1) / 2)
# choose the direction of the axis so that the right-hand turn is θ (not −θ)
if not np.allclose(rot_axis(w, theta), R):
    w = -w
assert np.allclose(rot_axis(w, theta), R)

# the other two eigenvalues are e^{±iθ}
others = sorted((v for i, v in enumerate(vals) if i != k), key=lambda z: z.imag)
assert np.allclose(others[1], complex(math.cos(theta), math.sin(theta)))

# points on the axis stay put; a vector perpendicular to the axis, turned through θ, stays perpendicular with the same length
u = np.cross(w, [1.0, 0, 0])
u /= np.linalg.norm(u)
Ru = R @ u
assert abs(Ru @ w) < 1e-12 and abs(np.linalg.norm(Ru) - 1) < 1e-12
assert abs(math.acos(float(np.clip(u @ Ru, -1, 1))) - theta) < 1e-12

out(R=tex(R), w=vec(w), w1=w[0], w2=w[1], w3=w[2], tr=tr, cos_theta=(tr - 1) / 2,
    theta_deg=math.degrees(theta), theta_rad=theta, ev_re=others[1].real, ev_im=others[1].imag)
