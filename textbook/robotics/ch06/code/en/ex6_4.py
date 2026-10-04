"""Examples of Section 6.4.

First we verify that the closed form of Theorem 6.4.1 agrees with the series and that formula (6.4.8) for G(θ)⁻¹ is right.
Example 6.4.1 (exponential map): the arm grips the rim of a valve handwheel and turns the handwheel 90° anticlockwise;
            the stem thread rises 4 mm per turn. Find the pose of the gripper after the turn. Three methods: the closed
            form of Theorem 6.4.1; the matrix exponential series; the geometric construction of Definition 6.1.1.
Example 6.4.2 (logarithm map): the UR5e moves from its zero position to a set of joint angles; find the screw axis, the
            angle, the pitch and a point on the axis of this displacement; check independently with SciPy's matrix
            logarithm logm, then substitute the result back into the exponential map, which should give the original
            displacement.
Example 6.4.3: two special cases, a pure translation (R = I) and an angle of π.
Also: under interpolation along the screw axis, T(s) = e^{[S]θs} M, the path of the flange centre keeps a constant
distance from the screw axis.
"""
import math

import numpy as np
from scipy.linalg import expm, logm

from _screw import (G, G_inv, UR_M, axis_of, bracket, exp3, exp6, expm_series, inv, log6, pose, screw_from_axis,
                    skew, ur_fk)
from bookout import out, tex, vec

d = math.radians

# ---------------------------------------------------------------- Theorem 6.4.1 and Eq. (6.4.8)
rng = np.random.default_rng(6)
for _ in range(20):
    w = rng.normal(size=3)
    w /= np.linalg.norm(w)
    v = rng.normal(size=3)
    t = rng.uniform(0.1, 3.0)
    S = np.r_[w, v]
    assert np.allclose(exp6(S, t), expm_series(bracket(S) * t), atol=1e-12)
    assert np.allclose(exp6(S, t), expm(bracket(S) * t), atol=1e-12)
    assert np.allclose(G(w, t) @ G_inv(w, t), np.eye(3), atol=1e-12)
    T = exp6(S, t)
    S2, t2 = log6(T)
    assert np.allclose(exp6(S2, t2), T, atol=1e-12)          # logarithm then exponential gets back to the start

# ---------------------------------------------------------------- Example 6.4.1
q = np.array([0.45, 0.20, 0.0])          # a point on the stem axis (m)
s_hat = np.array([0, 0, 1.0])            # stem vertical, upwards; anticlockwise (seen from above) is positive
lead = 0.004                             # lead 4 mm per turn
h = lead / (2 * math.pi)                 # pitch m/rad
S = screw_from_axis(q, s_hat, h)
th = d(90)
T0 = pose(np.diag([1.0, -1.0, -1.0]), np.array([0.45 + 0.12, 0.20, 0.30]))   # gripper: at the rim of the handwheel, z axis pointing down
E = exp6(S, th)
T1 = E @ T0
assert np.allclose(E, expm_series(bracket(S) * th), atol=1e-13)            # series
geo = pose(exp3(s_hat * th), q + exp3(s_hat * th) @ (-q) + h * th * s_hat)  # Definition 6.1.1: x′ = q + R(x − q) + hθŝ
assert np.allclose(E, geo, atol=1e-14)
rise = T1[2, 3] - T0[2, 3]
assert abs(rise - lead / 4) < 1e-15
Gv = G(s_hat, th) @ S[3:]
Iq = (np.eye(3) - exp3(s_hat * th)) @ q + h * th * s_hat
assert np.allclose(Gv, Iq)                                                   # Eq. (6.4.6)

# ---------------------------------------------------------------- Example 6.4.2
theta = np.array([d(30), d(-45), d(60), d(-15), d(90), d(30)])
Tt = ur_fk(theta)
D = Tt @ inv(UR_M)                        # displacement in space: T(θ) = D M
S_log, th_log = log6(D)
Lm = np.real(logm(D))                     # independent method: SciPy's matrix logarithm
assert np.allclose(Lm, bracket(S_log) * th_log, atol=1e-10)
assert np.allclose(exp6(S_log, th_log), D, atol=1e-12)
s2, q2, h2 = axis_of(S_log)
d2 = h2 * th_log
# interpolation along the screw axis: the distance of the flange centre from the axis is constant
p0 = UR_M[:3, 3]
r0 = np.linalg.norm(np.cross(s2, p0 - q2))
path = np.array([(exp6(S_log, th_log * f) @ np.r_[p0, 1])[:3] for f in np.linspace(0, 1, 21)])
for x in path:
    assert abs(np.linalg.norm(np.cross(s2, x - q2)) - r0) < 1e-12
assert np.allclose(path[-1], Tt[:3, 3])
lin_mid = (p0 + Tt[:3, 3]) / 2            # difference between the midpoints of straight-line and screw interpolation
dev_mid = float(np.linalg.norm(path[10] - lin_mid))
# logarithm of the displacement M⁻¹T(θ) in the body frame (used in Section 6.5)
B_log, thb = log6(inv(UR_M) @ Tt)
assert abs(thb - th_log) < 1e-12

# ---------------------------------------------------------------- Example 6.4.3, special cases
Dtr = pose(np.eye(3), np.array([0.3, 0.4, 0.0]))
St, tt = log6(Dtr)
assert np.allclose(St, [0, 0, 0, 0.6, 0.8, 0]) and abs(tt - 0.5) < 1e-15
Dpi = exp6(screw_from_axis([0.1, 0, 0], [0, 0, 1.0], 0.0), math.pi)
Spi, tpi = log6(Dpi)
assert abs(tpi - math.pi) < 1e-12 and np.allclose(exp6(Spi, tpi), Dpi, atol=1e-12)
assert np.allclose(Dpi[:3, 3], [0.2, 0, 0])

out(S=vec(S, 6), h=h, h_mm=h * 1000, E=tex(E, 4), T1=tex(T1, 4), T0=tex(T0, 3), rise_mm=rise * 1000,
    Gth=tex(G(s_hat, th), 4), Gv=vec(Gv, 4),
    theta_deg=vec(np.degrees(theta), 0), Tt=tex(Tt, 4), D=tex(D, 4), S_log=vec(S_log, 4), th_log=th_log,
    th_log_deg=math.degrees(th_log), s2=vec(s2, 4), q2=vec(q2, 4), h2=h2, d2=d2, r0=r0, dev_mid_mm=dev_mid * 1000,
    B_log=vec(B_log, 4), Ginv_err=0.0)
