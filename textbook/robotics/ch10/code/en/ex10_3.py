"""Examples 10.3.1, 10.3.2: velocity and acceleration in cylindrical (polar) coordinates.

Example 10.3.1: the SCARA of the parts library (l1 = 0.35 m, l2 = 0.25 m). At some instant θ1 = 30°, θ2 = 90°,
  θ̇1 = 1.0 rad/s, θ̇2 = −1.5 rad/s, with zero angular acceleration at both joints; the ball screw descends at 0.1 m/s.
  From Eqs. (10.3.11)-(10.3.13) find the cylindrical coordinates (ρ, φ, z) of the end-effector and their derivatives,
  and from Eqs. (10.3.8), (10.3.9) the radial, transverse and vertical components of the velocity and acceleration.
  Check: write the Cartesian coordinates x(t), y(t) from the forward kinematics, differentiate twice numerically and
  project onto e_ρ, e_φ; the results agree.
Example 10.3.2: the arm of a cylindrical robot extends steadily at ρ̇ = 0.2 m/s while turning steadily at
  φ̇ = 1.0 rad/s; the acceleration at ρ = 0.5 m, checked by numerical differentiation in Cartesian coordinates; the
  sideways force needed for the gripper together with a 2 kg part.
"""
import math

import numpy as np

from _kin import cyl_basis, d1, d2
from bookout import out

l1, l2 = 0.35, 0.25
th1, th2 = math.radians(30), math.radians(90)
w1, w2 = 1.0, -1.5                     # θ̇1, θ̇2, rad/s
zdot = -0.1                            # the ball screw descends, m/s


def joints(t):
    return th1 + w1 * t, th2 + w2 * t


def xyz(t):                            # SCARA forward kinematics (Section 12.3)
    q1, q2 = joints(t)
    return np.array([l1 * math.cos(q1) + l2 * math.cos(q1 + q2), l1 * math.sin(q1) + l2 * math.sin(q1 + q2), 0.242 + zdot * t])


# Eqs. (10.3.11)-(10.3.13): ρ, φ and their derivatives (analytic)
rho = math.sqrt(l1 ** 2 + l2 ** 2 + 2 * l1 * l2 * math.cos(th2))
beta = math.atan2(l2 * math.sin(th2), l1 + l2 * math.cos(th2))
phi = th1 + beta
rhod = -l1 * l2 * math.sin(th2) * w2 / rho
rhodd = (-l1 * l2 * math.cos(th2) * w2 ** 2 - rhod ** 2) / rho          # θ̈2 = 0
dbeta = (l2 ** 2 + l1 * l2 * math.cos(th2)) / rho ** 2                   # dβ/dθ2
phid = w1 + dbeta * w2
d2beta = -l1 * l2 * math.sin(th2) * (l1 ** 2 - l2 ** 2) / rho ** 4        # d²β/dθ2²
phidd = d2beta * w2 ** 2                                                  # θ̈1 = θ̈2 = 0

# check ρ(t), φ(t) against numerical differentiation
rho_t = lambda t: math.hypot(*xyz(t)[:2])
phi_t = lambda t: math.atan2(xyz(t)[1], xyz(t)[0])
assert abs(rho_t(0) - rho) < 1e-12 and abs(phi_t(0) - phi) < 1e-12
assert abs(d1(rho_t, 0, 1e-5) - rhod) < 1e-8 and abs(d2(rho_t, 0, 1e-4) - rhodd) < 1e-5
assert abs(d1(phi_t, 0, 1e-5) - phid) < 1e-8 and abs(d2(phi_t, 0, 1e-4) - phidd) < 1e-5

# Eqs. (10.3.8), (10.3.9)
v_rho, v_phi, v_z = rhod, rho * phid, zdot
a_rho = rhodd - rho * phid ** 2
a_phi = rho * phidd + 2 * rhod * phid
a_cent, a_cor, a_ang = -rho * phid ** 2, 2 * rhod * phid, rho * phidd

# check: differentiate the Cartesian coordinates numerically, then project onto the local basis
er, ep, ez = cyl_basis(phi)
v_num, a_num = d1(xyz, 0, 1e-5), d2(xyz, 0, 1e-4)
assert np.allclose([v_num @ er, v_num @ ep, v_num @ ez], [v_rho, v_phi, v_z], atol=1e-8)
assert np.allclose([a_num @ er, a_num @ ep, a_num @ ez], [a_rho, a_phi, 0.0], atol=1e-5)
a_xy = a_rho * er + a_phi * ep
speed = math.sqrt(v_rho ** 2 + v_phi ** 2 + v_z ** 2)
assert abs(speed - np.linalg.norm(v_num)) < 1e-8

# ---------------------------------------------------------------- Example 10.3.2
rd2, pd2, r2 = 0.2, 1.0, 0.5
a2_rho, a2_phi = -r2 * pd2 ** 2, 2 * rd2 * pd2
m = 2.0
xy2 = lambda t: np.array([(r2 + rd2 * t) * math.cos(pd2 * t), (r2 + rd2 * t) * math.sin(pd2 * t)])
an = d2(xy2, 0, 1e-4)
assert np.allclose(an, [a2_rho, a2_phi], atol=1e-6)        # at t = 0, e_ρ = x̂ and e_φ = ŷ

out(l1=l1, l2=l2, rho=rho, phi_deg=math.degrees(phi), beta_deg=math.degrees(beta), rhod=rhod, rhodd=rhodd,
    dbeta=dbeta, phid=phid, phidd=phidd, v_rho=v_rho, v_phi=v_phi, v_z=v_z, speed=speed,
    a_rho=a_rho, a_phi=a_phi, a_cent=a_cent, a_cor=a_cor, a_ang=a_ang, rhodd_term=rhodd,
    a_mag=float(math.hypot(a_rho, a_phi)), ax=a_xy[0], ay=a_xy[1], vx=v_num[0], vy=v_num[1],
    rd2=rd2, pd2=pd2, r2=r2, a2_rho=a2_rho, a2_phi=a2_phi, a2_mag=math.hypot(a2_rho, a2_phi),
    m=m, F_side=m * a2_phi)
