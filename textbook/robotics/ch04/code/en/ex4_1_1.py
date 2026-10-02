"""Example 4.1.1: where corner P of the part goes when the wrist turns through 30°.

Computed twice, by Eq. (4.1.3) (via polar coordinates) and by Eqs. (4.1.4), (4.1.5) (the rotation matrix); the two
must agree. Then the properties of Theorem 4.1.1 are checked: length is preserved, and turning back is the transpose.
"""
import math

import numpy as np

from bookout import out

x, y = 0.2, 0.1                      # components of corner P in {a}, m
theta = math.radians(30)             # angle of rotation, rad

# Eqs. (4.1.2), (4.1.3): polar coordinates
r = math.hypot(x, y)
phi = math.atan2(y, x)
xp_polar = r * math.cos(phi + theta)
yp_polar = r * math.sin(phi + theta)

# Eqs. (4.1.4), (4.1.5): the rotation matrix
c, s = math.cos(theta), math.sin(theta)
R = np.array([[c, -s], [s, c]])
p = np.array([x, y])
pp = R @ p

assert abs(pp[0] - xp_polar) < 1e-12 and abs(pp[1] - yp_polar) < 1e-12        # the two methods agree
assert np.allclose(R.T @ R, np.eye(2)) and abs(np.linalg.det(R) - 1) < 1e-12   # Theorem 4.1.1 (1)(2)
back = R.T @ pp
assert np.allclose(back, p)                                                  # Theorem 4.1.1 (3)
assert abs(np.linalg.norm(pp) - np.linalg.norm(p)) < 1e-12                   # Theorem 4.1.1 (4)

out(
    r=r, r_sq=x * x + y * y, phi_deg=math.degrees(phi), phi_theta_deg=math.degrees(phi + theta),
    c30=c, s30=s, theta_rad=theta,
    x_p=pp[0], y_p=pp[1],
    term_xc=x * c, term_ys=y * s, term_xs=x * s, term_yc=y * c,
    norm_p=float(np.linalg.norm(p)), norm_pp=float(np.linalg.norm(pp)),
)
