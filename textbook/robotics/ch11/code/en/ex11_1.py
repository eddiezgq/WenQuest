"""Section 11.1: joints as screws.

(1) Table 11.1.1: the subspace spanned by the twists allowed by each of the seven joints (R, P, H, C, U, S, E). Its rank
    is the number of degrees of freedom f of the joint; the wrenches of "zero power" against it (the constraint wrenches)
    span a subspace of dimension 6 − f (Theorem 11.1.1), checked in two ways: the null space by singular value
    decomposition; and verifying ℱᵀ𝒱 = 0 one by one, cross-checked with the reciprocal product (6.6.10).
(2) Example 11.1.1: the ball-screw spline shaft. For a screw with a lead of 20 mm the pitch is h = lead / 2π; when the
    spline nut turns the shaft through 90° while the screw nut is held, the shaft moves hθ along its own axis. Computed
    with the matrix exponential (11.1.2) of the screw axis of a helical joint (11.1.1), and checked against the geometric
    procedure "turn first, then move" and the series definition.
(3) The constraint wrenches of an ideal (frictionless) helical joint: an axial force F must come with a torque hF; the
    torque for an axial force of 50 N is computed.
"""
import math

import numpy as np

from _ch11 import exp6, expm_series, bracket, null_space, rot, screw_helical, screw_prismatic, screw_revolute
from bookout import T, out

z = np.array([0, 0, 1.0])
x = np.array([1.0, 0, 0])
y = np.array([0, 1.0, 0])
o = np.zeros(3)

# ---------------------------------------------------------------- (1) the seven joints: allowed twists
h_demo = 0.02 / (2 * math.pi)        # helical joint with a lead of 20 mm
joints = [
    ("R", T("转动关节", "revolute"), [screw_revolute(z, o)]),
    ("P", T("移动关节", "prismatic"), [screw_prismatic(z)]),
    ("H", T("螺旋副", "helical"), [screw_helical(z, o, h_demo)]),
    ("C", T("圆柱副", "cylindrical"), [screw_revolute(z, o), screw_prismatic(z)]),
    ("U", T("万向节", "universal"), [screw_revolute(x, o), screw_revolute(y, o)]),
    ("S", T("球关节", "spherical"), [screw_revolute(x, o), screw_revolute(y, o), screw_revolute(z, o)]),
    ("E", T("平面副", "planar"), [screw_revolute(z, o), screw_prismatic(x), screw_prismatic(y)]),
]

f_of = {}
for sym, name, twists in joints:
    V = np.column_stack(twists)                  # 6 × k, columns are the allowed twists
    f = np.linalg.matrix_rank(V)
    W, rankVt = null_space(V.T)                  # wrenches ℱ = (m, f) with Vᵀℱ = 0: the constraint wrenches
    c = W.shape[1]
    assert f == rankVt and f + c == 6            # Theorem 11.1.1: f + c = 6
    for Fw in W.T:                               # power ℱᵀ𝒱 = m·ω + f·v = 0, Eq. (6.6.3)
        for Vt in V.T:
            assert abs(Fw @ Vt) < 1e-12
            # reciprocal product (6.6.10): with the wrench written as (f, m) (direction first, moment second), its reciprocal product with 𝒱 is the power
            s1, v1, s2, v2 = Vt[:3], Vt[3:], Fw[3:], Fw[:3]
            assert abs(s1 @ v2 + s2 @ v1 - Fw @ Vt) < 1e-12
    f_of[sym] = (f, c)

# physical meaning of the constraint wrenches (revolute joint: three forces through the axis + two moments perpendicular to the axis)
W_R, _ = null_space(np.column_stack(joints[0][2]).T)
# the space spanned by W_R must equal the one spanned by {forces x, y, z (lines of action through the origin), moments x, y}
basis_R = np.array([[0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0]], float).T
assert np.linalg.matrix_rank(np.column_stack([W_R, basis_R])) == 5

# the f and c printed in Table 11.1.1 (hand-typed integers) must agree with the computation
book = {"R": (1, 5), "P": (1, 5), "H": (1, 5), "C": (2, 4), "U": (2, 4), "S": (3, 3), "E": (3, 3)}
assert f_of == book, f_of

# ---------------------------------------------------------------- (2) Example 11.1.1: ball-screw spline shaft
lead = 0.020                                     # lead (m/rev)
h = lead / (2 * math.pi)                         # pitch (m/rad), Section 6.1: lead = 2πh
q_axis = np.array([0.6, 0.0, 0.0])               # position of the axis: horizontal position of axes 3 and 4 of the parts-library SCARA
w_axis = np.array([0, 0, -1.0])                  # direction: vertically down (the positive direction of SCARA joint 3)
S_H = screw_helical(w_axis, q_axis, h)
th = math.radians(90)
E = exp6(S_H, th)
assert np.allclose(E, expm_series(bracket(S_H) * th), atol=1e-12)
# geometric procedure (Theorem 6.4.2): turn θ about the axis through q, then move hθ along the axis
Rg = rot(w_axis, th)
pt = np.array([0.62, 0.0, 0.2])                  # a point moving with the shaft (a spline tooth 0.02 m from the axis)
p_geo = q_axis + Rg @ (pt - q_axis) + h * th * w_axis
p_exp = (E @ np.r_[pt, 1.0])[:3]
assert np.allclose(p_geo, p_exp, atol=1e-12)
dz = h * th                                      # distance moved along the axis
# screw-nut compensation: screw motion of the shaft relative to the screw nut = spline angle − screw-nut angle; compensated, the two are equal and the shaft neither rises nor falls
comp_deg = 90.0

# ---------------------------------------------------------------- (3) constraint wrenches of an ideal helical joint
W_H, _ = null_space(S_H.reshape(6, 1).T)
F_axial = 50.0                                   # axial force (N)
# the one in W_H that is "force F along the axis + moment m along the axis": m·ω + f·v = 0 ⇒ m_ax = −h F_ax (measured along ω)
m_ax = -h * F_axial
Fw = np.r_[m_ax * w_axis + np.cross(q_axis, F_axial * w_axis), F_axial * w_axis]
assert abs(Fw @ S_H) < 1e-12
tau_needed = h * F_axial                         # torque needed to keep the shaft from turning (N·m)

out(h=h, h_mm=h * 1000, dz_mm=dz * 1000, comp_deg=comp_deg,
    tau=tau_needed, p_geo=p_geo.tolist(), z_end=p_exp[2])
