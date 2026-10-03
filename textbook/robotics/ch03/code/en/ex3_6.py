"""Examples of Section 3.6.

Example 3.6.1: the UR5e in the zero position (all joint angles 0), joint 1 turning at 60°/s. The velocity of the flange
           centre v = ω × r, computed with two different reference points on the axis; checked by a numerical
           derivative, "difference in position after turning through a small angle / time".
           The largest rate of joint 1 allowed by the 250 mm/s reduced-speed limit; the centripetal acceleration of the
           flange centre.
Example 3.6.2: joint 2 (horizontal axis, direction −y, through the point (0, −0.138, 0.163) m) turning at 30°/s; the
           velocity of the flange centre.
Everyday example of Section 3.6.6: the Earth's rotation; the speed of a point on the ground in Shanghai (about 31.2° N)
           as it turns with the Earth.
Also checked: the velocity formula for rotation in the plane; when two angular velocities about axes through the same
point act together, the velocity equals their sum crossed with r.
"""
import math

import numpy as np

from _vec import d, skew, unit
from bookout import out, vec


def rot_about(axis, point, t, p):
    """Turn the point p through t about the line through point with direction axis (Rodrigues' formula, Section 4.4)."""
    w = unit(axis)
    K = skew(w)
    R = np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K
    return point + R @ (p - point)


# position of the flange centre of the UR5e in the zero position (as in Example 12.1.2, base frame {s}, in m)
H1, W1, L1, W2, L2, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1
p = np.array([-L1 - L2, -W1 + W2 - W3 - W4, H1 - H2])

# ---------------------------------------------------------------- Example 3.6.1 joint 1
w1 = d(60)                                      # rad/s
axis1, q1 = np.array([0, 0, 1.0]), np.array([0, 0, H1])
omega1 = w1 * axis1
v1 = np.cross(omega1, p - q1)                   # reference point q1 on the axis of joint 1
v1b = np.cross(omega1, p - np.zeros(3))         # reference point at the origin, on the axis
assert np.allclose(v1, v1b)                     # Eq. (3.6.6): independent of where on the axis the reference point is
assert np.allclose(v1, skew(omega1) @ (p - q1))  # Eq. (3.6.5)
h = 1e-6                                        # s
v1_num = (rot_about(axis1, q1, w1 * h, p) - rot_about(axis1, q1, -w1 * h, p)) / (2 * h)
assert np.allclose(v1_num, v1, atol=1e-8)       # check by numerical derivative
rho1 = math.hypot(p[0], p[1])                   # distance to the axis of joint 1
assert abs(np.linalg.norm(v1) - w1 * rho1) < 1e-12
v_lim = 0.25                                    # m/s, limit in manual reduced-speed mode
w1_max = v_lim / rho1                           # rad/s
a1 = np.cross(omega1, np.cross(omega1, p - q1))  # Eq. (3.6.8)
rperp = (p - q1) - ((p - q1) @ axis1) * axis1
assert np.allclose(a1, -w1 ** 2 * rperp)
# check by numerical second derivative
a1_num = (rot_about(axis1, q1, w1 * 1e-4, p) - 2 * p + rot_about(axis1, q1, -w1 * 1e-4, p)) / 1e-8
assert np.allclose(a1_num, a1, atol=1e-5)

# ---------------------------------------------------------------- Example 3.6.2 joint 2
w2 = d(30)
axis2, q2 = np.array([0, -1.0, 0]), np.array([0, -W1, H1])
omega2 = w2 * axis2
v2 = np.cross(omega2, p - q2)
q2b = q2 + 0.3 * axis2                          # another point on the axis
assert np.allclose(v2, np.cross(omega2, p - q2b))
v2_num = (rot_about(axis2, q2, w2 * h, p) - rot_about(axis2, q2, -w2 * h, p)) / (2 * h)
assert np.allclose(v2_num, v2, atol=1e-8)
rho2 = np.linalg.norm((p - q2) - ((p - q2) @ unit(axis2)) * unit(axis2))
assert abs(np.linalg.norm(v2) - w2 * rho2) < 1e-12

# ---------------------------------------------------------------- two angular velocities acting together (two axes through one point)
rng = np.random.default_rng(2)
for _ in range(50):
    wa, wb, r = rng.normal(size=(3, 3))
    assert np.allclose(np.cross(wa, r) + np.cross(wb, r), np.cross(wa + wb, r))

# ---------------------------------------------------------------- velocity in planar rotation
x0, y0, th, thd = 0.2, 0.1, d(30), 0.8          # corner point of Section 4.1, angle turned, angular velocity in rad/s
Rp = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
dR = thd * np.array([[-math.sin(th), -math.cos(th)], [math.cos(th), -math.sin(th)]])
pp = Rp @ [x0, y0]
assert np.allclose(dR @ [x0, y0], thd * np.array([-pp[1], pp[0]]))   # Eq. (3.6.2)

# ---------------------------------------------------------------- Section 3.6.6 the Earth's rotation
wE = 7.292115e-5                                # rad/s, angular velocity of the Earth's rotation (relative to the stars)
RE = 6371.0e3                                   # m, mean radius of the Earth
lat = d(31.2)
v_eq = wE * RE
v_sh = wE * RE * math.cos(lat)
T_sid = 2 * math.pi / wE                        # sidereal day, s

out(
    p=vec(p, 3), px=p[0], py=p[1], pz=p[2],
    w1=w1, v1=vec(v1, 4), v1x=v1[0], v1y=v1[1], v1_len=float(np.linalg.norm(v1)), rho1=rho1,
    v1_num_err=float(np.abs(v1_num - v1).max()),
    w1_max=w1_max, w1_max_deg=math.degrees(w1_max), a1=vec(a1, 4), a1_len=float(np.linalg.norm(a1)),
    w2=w2, r2=vec(p - q2, 3), v2=vec(v2, 4), v2x=v2[0], v2z=v2[2], v2_len=float(np.linalg.norm(v2)), rho2=rho2,
    wE=wE, v_eq=v_eq, v_sh=v_sh, T_sid_h=T_sid / 3600,
)
