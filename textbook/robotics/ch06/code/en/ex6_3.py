"""Examples of Section 6.3.

Example 6.3.1: the UR5e is at its zero position and only joint 2 turns, at 30°/s. Find the spatial twist V_s and the body
               twist V_b of the flange, and the velocity of the flange centre.
               Two methods: from the screw axis, V_s = S₂θ̇₂, and Eq. (6.3.9); by numerically differentiating the pose T(t),
               Ṫ T⁻¹ and T⁻¹ Ṫ (Eqs. (6.3.4), (6.3.7)).
               The velocity of the flange centre is also compared with ω × r of Example 3.6.2 in Chapter 3.
Example 6.3.2: at the zero position joints 1 and 3 turn together at 30°/s. Find the spatial twist and its instantaneous
               screw axis: direction, a point q on the axis, pitch h (Eqs. (6.3.11), (6.3.12)).
               Checks: the velocities of the points on the axis are all parallel to ω, with magnitude h|ω|; the twist
               found by numerical differentiation equals the sum of the screw axes; points farther from the axis move
               faster, and the velocity component perpendicular to the axis is proportional to the distance from the axis.
"""
import math

import numpy as np

from _screw import UR_M, UR_S, axis_of, bracket, exp6, inv, screw_from_axis, skew, unbracket
from bookout import out, tex, vec

d = math.radians


def fk(th):
    T = np.eye(4)
    for S, t in zip(UR_S, th):
        T = T @ exp6(S, t)
    return T @ UR_M


def num_twists(theta_of_t, t=0.0, h=1e-6):
    T = fk(theta_of_t(t))
    Td = (fk(theta_of_t(t + h)) - fk(theta_of_t(t - h))) / (2 * h)
    return T, unbracket(Td @ inv(T)), unbracket(inv(T) @ Td)


# ---------------------------------------------------------------- Example 6.3.1
rate2 = d(30)
S2 = UR_S[1]
Vs = S2 * rate2
T0, Vs_num, Vb_num = num_twists(lambda t: [0, rate2 * t, 0, 0, 0, 0])
assert np.allclose(Vs, Vs_num, atol=1e-8)
R, p = T0[:3, :3], T0[:3, 3]
w_s, v_s = Vs[:3], Vs[3:]
Vb = np.r_[R.T @ w_s, R.T @ (v_s + np.cross(w_s, p))]       # Eq. (6.3.9) solved backwards: ω_b = Rᵀω_s, v_b = Rᵀṗ, ṗ = v_s + ω_s × p
assert np.allclose(Vb, Vb_num, atol=1e-8)
pdot = v_s + np.cross(w_s, p)                                # velocity of the flange centre (origin of {b})
q2 = np.array([0, -0.138, 0.163])
assert np.allclose(pdot, np.cross(w_s, p - q2))             # the same as ω × r of Chapter 3
assert np.allclose(R @ Vb[3:], pdot)

# ---------------------------------------------------------------- Example 6.3.2
r1 = r3 = d(30)
V = UR_S[0] * r1 + UR_S[2] * r3
_, V_num, _ = num_twists(lambda t: [r1 * t, 0, r3 * t, 0, 0, 0])
assert np.allclose(V, V_num, atol=1e-8)
w, v = V[:3], V[3:]
wn = float(np.linalg.norm(w))
s_hat, q, hp = axis_of(V)
assert np.allclose(screw_from_axis(q, s_hat, hp) * wn, V)
# points on the axis: velocity = v + ω × x, should be parallel to ω with magnitude h|ω|
for lam in (-0.5, 0.0, 0.7):
    x = q + lam * s_hat
    vx = v + np.cross(w, x)
    assert np.allclose(np.cross(vx, w), 0, atol=1e-12) and abs(vx @ s_hat - hp * wn) < 1e-12
# a point at distance r from the axis: velocity component perpendicular to the axis = |ω| r
e = np.cross(s_hat, [1.0, 0, 0])
e /= np.linalg.norm(e)
for r in (0.1, 0.3):
    x = q + r * e
    vx = v + np.cross(w, x)
    assert abs(np.linalg.norm(vx - (vx @ s_hat) * s_hat) - wn * r) < 1e-12
# another way to find the axis: look for the point of smallest velocity (least squares); the points minimizing v + ω × x all lie on the screw axis
A = skew(w)
x_ls = np.linalg.lstsq(A, -v, rcond=None)[0]                # the point nearest the origin among those minimizing |v + ω × x|
assert np.allclose(x_ls, q, atol=1e-12)
# pitch and the distance between the two axes: h = θ̇1θ̇3 L1 /(θ̇1² + θ̇3²)
L1 = 0.425
assert abs(hp - r1 * r3 * L1 / (r1 ** 2 + r3 ** 2)) < 1e-12
vmin = hp * wn
# with equal rates the screw axis passes through the midpoint (−L1/2, 0, H1) of the common perpendicular of the two axes
mid = np.array([-L1 / 2, 0.0, 0.163])
assert np.allclose(np.cross(mid - q, s_hat), 0, atol=1e-12)

out(Vs=vec(Vs, 4), Vb=vec(Vb, 4), pdot=vec(pdot, 4), pdot_len=float(np.linalg.norm(pdot)), p=vec(p, 3), rate2=rate2,
    S2=vec(S2, 3), S1=vec(UR_S[0], 3), S3=vec(UR_S[2], 3), V=vec(V, 4), s_hat=vec(s_hat, 4), q=vec(q, 4), h=hp, wn=wn,
    vmin=vmin, wv=float(w @ v), vsx=float(Vs[3]), mid=vec(mid, 4), Tdot=tex(bracket(Vs) @ T0, 4), M=tex(UR_M, 3))
