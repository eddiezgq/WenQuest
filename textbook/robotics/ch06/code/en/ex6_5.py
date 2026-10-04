"""Examples of Section 6.5.

First we verify the properties of the adjoint matrix: [Ad_T]V agrees with T[V]T⁻¹ (Eq. (6.5.5)); [Ad_T1][Ad_T2] = [Ad_T1T2];
[Ad_T]⁻¹ = [Ad_T⁻¹]; e^{[Ad_T S]θ} = T e^{[S]θ} T⁻¹ (Eq. (6.5.8)); the pitch and the angle do not change with the frame.
Example 6.5.1: the UR5e is at its zero position with a tool 0.15 m long on the flange. The tool is to turn about its own
            x axis at 0.5 rad/s with the tool tip still. Find the twists in the tool frame, the flange frame and the base
            frame. Checks: the tool-tip velocity computed from V_s is zero; V_s found by numerically differentiating
            T_st(t) = T_st e^{[V_t]t} agrees with the result from the adjoint matrix.
Example 6.5.2: the body screw axes of the six joints of the UR5e, B_i = [Ad_{M⁻¹}] S_i; checked with M⁻¹[S_i]M and with
            both forms of the product of exponentials; and the answer to Exercise 6.4.4: the logarithm of the displacement
            in the body frame is the adjoint transformation of the logarithm of the displacement in the space frame, with
            the same angle and pitch.
"""
import math

import numpy as np

from _screw import (UR_M, UR_S, adjoint, axis_of, bracket, exp3, exp6, inv, log6, pose, rot_x, rot_z, skew, unbracket,
                    ur_fk)
from bookout import num, out, tex, vec

d = math.radians
rng = np.random.default_rng(65)


def rand_T():
    w = rng.normal(size=3)
    return pose(exp3(w), rng.normal(size=3))


# ---------------------------------------------------------------- properties
for _ in range(20):
    T1, T2, V = rand_T(), rand_T(), rng.normal(size=6)
    assert np.allclose(adjoint(T1) @ V, unbracket(T1 @ bracket(V) @ inv(T1)))
    assert np.allclose(adjoint(T1) @ adjoint(T2), adjoint(T1 @ T2))
    assert np.allclose(np.linalg.inv(adjoint(T1)), adjoint(inv(T1)))
    S = V / np.linalg.norm(V[:3])
    th = rng.uniform(0.2, 2.5)
    assert np.allclose(exp6(adjoint(T1) @ S, th), T1 @ exp6(S, th) @ inv(T1))
    s1, q1, h1 = axis_of(S)
    s2, q2, h2 = axis_of(adjoint(T1) @ S)
    assert abs(h1 - h2) < 1e-12                                             # pitch unchanged
    assert np.allclose(s2, T1[:3, :3] @ s1)                                 # the axis direction is transformed with the rigid body
    x = T1 @ np.r_[q1, 1]
    assert np.allclose(np.cross(x[:3] - q2, s2), 0, atol=1e-10)             # the axis itself is carried to its new place

# ---------------------------------------------------------------- Example 6.5.1
Tbt = pose(np.eye(3), np.array([0, 0.15, 0]))         # the tool sticks out 0.15 m along the flange normal (y axis of {b})
Tst = UR_M @ Tbt
Vt = np.array([0.5, 0, 0, 0, 0, 0])                   # turn about the tool's own x axis, tip still
Vb = adjoint(Tbt) @ Vt
Vs = adjoint(Tst) @ Vt
assert np.allclose(Vs, adjoint(UR_M) @ Vb)            # V_s = [Ad_{T_sb}] V_b
p_tip = Tst[:3, 3]
assert np.allclose(Vs[3:] + np.cross(Vs[:3], p_tip), 0)   # tool-tip velocity is zero
p_fl = UR_M[:3, 3]
v_flange = Vs[3:] + np.cross(Vs[:3], p_fl)
assert np.allclose(v_flange, UR_M[:3, :3] @ Vb[3:])   # velocity of the flange centre = R v_b
h = 1e-6
Td = (Tst @ exp6(Vt / 0.5, 0.5 * h) - Tst @ exp6(Vt / 0.5, -0.5 * h)) / (2 * h)
assert np.allclose(unbracket(Td @ inv(Tst)), Vs, atol=1e-8)
assert np.allclose(unbracket(inv(UR_M) @ (Td @ inv(Tbt))), Vb, atol=1e-8)

# ---------------------------------------------------------------- Example 6.5.2
AdMi = adjoint(inv(UR_M))
B = [AdMi @ S for S in UR_S]
for S, Bi in zip(UR_S, B):
    assert np.allclose(bracket(Bi), inv(UR_M) @ bracket(S) @ UR_M)
for _ in range(5):
    th = rng.uniform(-math.pi, math.pi, 6)
    Tb = UR_M.copy()
    for Bi, t in zip(B, th):
        Tb = Tb @ exp6(Bi, t)
    assert np.allclose(Tb, ur_fk(th))
rows = r" \\ ".join(f"{i} & " + " & ".join(num(float(x), 3) for x in Bi) for i, Bi in enumerate(B, 1))
# Exercise 6.4.4
theta = np.array([d(30), d(-45), d(60), d(-15), d(90), d(30)])
Tt = ur_fk(theta)
Ss, ts = log6(Tt @ inv(UR_M))
Sb, tb = log6(inv(UR_M) @ Tt)
assert abs(ts - tb) < 1e-12 and np.allclose(Sb, AdMi @ Ss)
assert abs(axis_of(Ss)[2] - axis_of(Sb)[2]) < 1e-12

out(Tbt=tex(Tbt, 2), Tst=tex(Tst, 3), Vt=vec(Vt, 1), Vb=vec(Vb, 4), Vs=vec(Vs, 4), p_tip=vec(p_tip, 3), v_flange=vec(v_flange, 4),
    AdTbt=tex(adjoint(Tbt), 2), AdM=tex(adjoint(UR_M), 3), Brows=rows, B6=vec(B[5], 3), B1=vec(B[0], 3),
    h_space=axis_of(Ss)[2], h_body=axis_of(Sb)[2], th_deg=math.degrees(ts), Sb=vec(Sb, 4))
