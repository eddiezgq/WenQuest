"""Examples of Section 6.6.

Example 6.6.1: the UR5e in the zero position holds a 5 kg load whose centre of mass lies 0.05 m from the centre of
               the flange along ŷ_b. The wrench F_s the robot applies to the load (holding it); the static torque
               needed at each joint in the zero position, τ_i = S_iᵀ F_s (Eq. (6.6.6)).
               Independent check: the principle of virtual work -- τ_i equals the partial derivative of the load's
               gravitational potential energy m𝔤 z_c(θ) with respect to θ_i (numerical differentiation).
Example 6.6.2: the readings of the six-axis force/torque sensor on the flange, F_b = [Ad_{T_sb}]ᵀ F_s (Eq. (6.6.4)),
               compared with the direct calculation f_b = Rᵀf, m_b = r_b × f_b.
               Invariance of power: with joint 2 turning at 30°/s, F_sᵀV_s = F_bᵀV_b = τ₂θ̇₂.
Example 6.6.3: the central axis and pitch of a wrench (Poinsot): the wrench of two forces not in one plane.
Also: the geometric formula (6.6.11) for the reciprocal product agrees with the definition (6.6.10) for random screws;
the screw axis of a revolute joint is reciprocal to any force whose line passes through its axis.
"""
import math

import numpy as np

from _screw import UR_AXES, UR_M, UR_S, adjoint, exp6, inv, pose, screw_from_axis, ur_fk
from bookout import out, tex, vec

g = 9.81
m = 5.0
rb = np.array([0, 0.05, 0])                       # position of the load's centre of mass in {b} (m)
c = (UR_M @ np.r_[rb, 1])[:3]                     # position of the load's centre of mass in {s} in the zero position
f_up = np.array([0, 0, m * g])                    # force with which the robot holds the load
F = np.r_[np.cross(c, f_up), f_up]                # wrench F_s = (m_s, f_s), moment about the origin of {s}
tau = np.array([S @ F for S in UR_S])


def zc(th):
    return (ur_fk(th) @ np.r_[rb, 1])[2]


h = 1e-6
tau_vw = np.array([m * g * (zc(np.eye(6)[i] * h) - zc(-np.eye(6)[i] * h)) / (2 * h) for i in range(6)])
assert np.allclose(tau, tau_vw, atol=1e-6)
# geometrically: τ_i = ω_i · ((c − q_i) × f)
for (w, q), t in zip(UR_AXES, tau):
    assert abs(w @ np.cross(c - q, f_up) - t) < 1e-12

# ---------------------------------------------------------------- Example 6.6.2
Fg_s = -F                                          # wrench the load exerts on the flange (this is what the sensor measures)
Fb = adjoint(UR_M).T @ Fg_s
R = UR_M[:3, :3]
fb = R.T @ Fg_s[3:]
mb = np.cross(rb, fb)
assert np.allclose(Fb, np.r_[mb, fb])
# invariance of power
rate = math.radians(30)
Vs = UR_S[1] * rate
Vb = adjoint(inv(UR_M)) @ Vs
P_s, P_b = F @ Vs, (adjoint(UR_M).T @ F) @ Vb
assert abs(P_s - P_b) < 1e-12 and abs(P_s - tau[1] * rate) < 1e-12

# ---------------------------------------------------------------- Example 6.6.3: central axis
# two forces: f1 = (0, 0, −10) N at (0.2, 0, 0) m; f2 = (0, 10, 0) N at (0, 0, 0.3) m
P1, f1 = np.array([0.2, 0, 0]), np.array([0, 0, -10.0])
P2, f2 = np.array([0, 0, 0.3]), np.array([0, 10.0, 0])
fR = f1 + f2
mR = np.cross(P1, f1) + np.cross(P2, f2)
hw = float(mR @ fR / (fR @ fR))                    # pitch (m)
qw = np.cross(fR, mR) / (fR @ fR)                  # point of the central axis nearest the origin
assert np.allclose(np.r_[mR, fR], np.r_[np.cross(qw, fR) + hw * fR, fR])     # Eq. (6.6.7)
# on the central axis the moment is parallel to the force and smallest
mq = mR - np.cross(qw, fR)
assert np.allclose(np.cross(mq, fR), 0) and np.linalg.norm(mq) <= np.linalg.norm(mR) + 1e-12
m_central = float(np.linalg.norm(mq))

# ---------------------------------------------------------------- geometric formula for the reciprocal product
rng = np.random.default_rng(66)


def recip(S1, S2):
    return S1[:3] @ S2[3:] + S2[:3] @ S1[3:]


for _ in range(50):
    s1, s2 = (x / np.linalg.norm(x) for x in rng.normal(size=(2, 3)))
    q1, q2 = rng.normal(size=(2, 3))
    h1, h2 = rng.normal(size=2)
    A, B = screw_from_axis(q1, s1, h1), screw_from_axis(q2, s2, h2)
    n = np.cross(s1, s2)
    sa = np.linalg.norm(n)
    n /= sa
    ca = s1 @ s2
    # signed distance d along the common perpendicular: from axis 1 to axis 2, measured along n
    dd = (q2 - q1) @ n
    assert abs(recip(A, B) - ((h1 + h2) * ca - dd * sa)) < 1e-10
# the screw axis of joint 2 is reciprocal to a force through the axis of joint 2: the force gives joint 2 no torque
w2, q2_ = UR_AXES[1]
fx = np.array([0.3, 0.0, -1.0])
Fx = np.r_[np.cross(q2_, fx), fx]
assert abs(UR_S[1] @ Fx) < 1e-12

out(c=vec(c, 3), F=vec(F, 3), tau=vec(tau, 2), tau2=tau[1], tau3=tau[2], tau4=tau[3], mg=m * g,
    Fb=vec(Fb, 3), fb=vec(fb, 2), mb=vec(mb, 4), Vs=vec(Vs, 4), Vb=vec(Vb, 4), P=P_s, rate=rate,
    fR=vec(fR, 1), mR=vec(mR, 1), hw=hw, qw=vec(qw, 4), m_central=m_central, AdMT=tex(adjoint(UR_M).T, 3))
