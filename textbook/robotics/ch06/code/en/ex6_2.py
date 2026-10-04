"""Examples of Section 6.2.

Example 6.2.1: starting from the zero position, joint 1 of a UR5e turns uniformly at 30°/s and joint 6 at 90°/s. Find the spatial angular velocity ω_s
            and the body angular velocity ω_b of the flange at t = 1 s. Three methods check one another:
            (a) the vector sum of the joint angular velocities (Theorem 3.6.2), the axis of joint 6 being carried round by joint 1;
            (b) numerical differentiation of the orientation R(t): [ω_s] = Ṙ Rᵀ, [ω_b] = Rᵀ Ṙ (Eqs. (6.2.3), (6.2.4));
            (c) ω_b = Rᵀ ω_s.
Example 6.2.2: the exponential coordinates of the total change of orientation over 1 s, R(1)R(0)ᵀ, compared with the time integral of the angular velocity ∫ω_s dt: they differ.
            Also verify that they agree when only one joint turns (fixed axis).
Also: gyroscope integration. Integrate step by step with R_{k+1} = R_k e^{[ω_b]Δt} (postmultiplication, body angular velocity) and compare with the exact orientation;
    if ω_b is wrongly premultiplied, the error does not vanish as the step size decreases.
"""
import math

import numpy as np
from scipy.integrate import quad

from _screw import UR_AXES, UR_M, exp3, log3, skew, unskew
from bookout import out, tex, vec

d = math.radians
w1, w6 = UR_AXES[0][0], UR_AXES[5][0]           # axes of joints 1 and 6 (zero position, in {s})
R0 = UR_M[:3, :3]
r1, r6 = d(30), d(90)                            # joint rates, rad/s


def R(t):
    """Orientation: e^{[ω1]θ1} e^{[ω6]θ6} R0 (rotational part of the product-of-exponentials formula, Chapter 12)."""
    return exp3(w1 * r1 * t) @ exp3(w6 * r6 * t) @ R0


t = 1.0
Rt = R(t)
# (a) vector sum of angular velocities
ws_a = r1 * w1 + r6 * exp3(w1 * r1 * t) @ w6
# (b) numerical differentiation
h = 1e-6
Rdot = (R(t + h) - R(t - h)) / (2 * h)
Ws = Rdot @ Rt.T
Wb = Rt.T @ Rdot
assert np.allclose(Ws, -Ws.T, atol=1e-8) and np.allclose(Wb, -Wb.T, atol=1e-8)   # Ṙ Rᵀ and Rᵀ Ṙ are skew-symmetric
ws_b, wb_b = unskew(Ws), unskew(Wb)
assert np.allclose(ws_a, ws_b, atol=1e-8)
# (c) ω_b = Rᵀ ω_s
wb_c = Rt.T @ ws_a
assert np.allclose(wb_c, wb_b, atol=1e-8)
assert abs(np.linalg.norm(ws_a) - np.linalg.norm(wb_c)) < 1e-12               # same magnitude
assert np.allclose(skew(wb_c), Rt.T @ skew(ws_a) @ Rt)                          # Eq. (3.4.6)
# at t = 0
ws0 = r1 * w1 + r6 * w6
wb0 = R0.T @ ws0

# ---------------------------------------------------------------- Example 6.2.2
Dt = Rt @ R(0).T
w_log, th_log = log3(Dt)
expc = w_log * th_log
a = r1
integral = r1 * w1 + r6 * np.array([(1 - math.cos(a)) / a, -math.sin(a) / a, 0.0])  # closed form of ∫0^1 Rot(z, a t)(−ŷ) dt
num = np.array([quad(lambda s, i=i: (r1 * w1 + r6 * exp3(w1 * r1 * s) @ w6)[i], 0, 1)[0] for i in range(3)])
assert np.allclose(integral, num, atol=1e-10)
assert np.allclose(exp3(expc), Dt)
gap = float(np.linalg.norm(expc - integral))
assert gap > 1e-2                                                               # the two really differ
# with only joint 6 turning (fixed axis) the two are the same
D6 = exp3(w6 * r6 * 1.0)
w6log, th6 = log3(D6)
assert np.allclose(w6log * th6, r6 * w6)

# ---------------------------------------------------------------- gyroscope integration
def integrate(n, right=True):
    Rk, dt = R(0).copy(), 1.0 / n
    for k in range(n):
        tm = (k + 0.5) * dt
        wb = R(tm).T @ (r1 * w1 + r6 * exp3(w1 * r1 * tm) @ w6)   # gyroscope reading: body angular velocity
        Rk = Rk @ exp3(wb * dt) if right else exp3(wb * dt) @ Rk
    return Rk


def err_deg(A, B):
    return math.degrees(math.acos(np.clip((np.trace(A.T @ B) - 1) / 2, -1, 1)))


e_r10, e_r100 = err_deg(integrate(10), Rt), err_deg(integrate(100), Rt)
e_l100 = err_deg(integrate(100, right=False), Rt)
assert e_r100 < e_r10 < 0.1 and e_l100 > 10

out(Rt=tex(Rt, 4), ws=vec(ws_a, 4), wb=vec(wb_c, 4), wnorm=float(np.linalg.norm(ws_a)), wnorm_deg=math.degrees(np.linalg.norm(ws_a)),
    ws0=vec(ws0, 4), wb0=vec(wb0, 4), Ws=tex(Ws, 4), Wb=tex(Wb, 4),
    w_log=vec(w_log, 4), th_log_deg=math.degrees(th_log), expc=vec(expc, 4), integral=vec(integral, 4), gap=gap,
    gap_deg=math.degrees(gap), e_r10=e_r10, e_r100=e_r100, e_l100=e_l100, r1=r1, r6=r6)
