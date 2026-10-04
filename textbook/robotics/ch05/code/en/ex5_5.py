"""Examples 5.5.1 and 5.5.2: the camera–arm–workpiece chain of frames.

Workstation (Figure 5.5.1): worktable {w}; UR5e base {s} (at (0.30, 0.40) m on the table top, turned 180° about z); fixed camera {c}
(0.90 m high, optical axis 15° from the vertical); gear blank {o}; grasp frame {g} (on the workpiece, z_g pointing down);
gripper tool frame {t} (0.15 m beyond the flange).
So that the result can be checked, the gear blank is first placed at a known position in the virtual workstation: centre at
(0.80, 0.45) m, on a 20 mm high tray, turned 25° about z; the pose estimate of the camera gives T_co (computed here from the
known position, standing for an ideal measurement).

5.5.1 From the camera reading, the pose the arm should reach:
      T_sg = T_sw T_wc T_co T_og, flange target T_sb* = T_sg T_bt⁻¹.
      Method 1: multiply along the chain by hand; method 2: the general path algorithm of the frame tree; method 3: compare
      with the known position of the workpiece.
      Then solve for the joint angles θ* by numerical inverse kinematics (Chapter 15) and compute T_sb(θ*) with the algorithm
      of the web 3D model; it must agree with T_sb*.
5.5.2 Error propagation along the chain: the camera mounting angle has an error of 0.5° (about x_c, y_c, z_c in turn); by how
      much does the point reached by the gripper miss?
      Compare with the first-order estimate |δ × r| (r is the vector from the camera origin to the grasp point).
"""
import math

import numpy as np

from _frames import (DEG, FrameTree, P_WC, T, T_bt, T_og, T_wc, T_ws, clean, hom, inv, log_rot, rot_axis, rot_x, rot_y, rot_z,
                     texm, ur_fk_glb, ur_fk_poe, ur_ik, vecm)
from bookout import T as TT, out

# Known position of the workpiece in the virtual workstation (used only to produce the camera reading and for the final check)
Two_true = T(rot_z(25 * DEG), (0.80, 0.45, 0.02))
Tco = inv(T_wc()) @ Two_true                     # result of the camera's pose estimation

# ---------------------------------------------------------------- Example 5.5.1
Tsw = inv(T_ws())
Tsg_1 = Tsw @ T_wc() @ Tco @ T_og()               # method 1: the chain written by hand
tree = FrameTree("w")
tree.add("s", "w", T_ws())
tree.add("c", "w", T_wc())
tree.add("o", "c", Tco)                           # the workpiece seen by the camera: hung under {c}
tree.add("g", "o", T_og())
Tsg_2 = tree.T("s", "g")                          # method 2: the path algorithm of the tree
assert np.allclose(Tsg_1, Tsg_2, atol=1e-15)
Tsg_3 = Tsw @ Two_true @ T_og()                   # method 3: compare with the known position
assert np.allclose(Tsg_1, Tsg_3, atol=1e-15)
Two = T_wc() @ Tco
assert np.allclose(Two, Two_true, atol=1e-15)

Tsb_goal = Tsg_1 @ inv(T_bt())
# The two sides of the closure equation (5.5.1) are equal: the robot side and the camera side give the same T_wt
# Pre-grasp pose: tool centre point 50 mm directly above the grasp point (along −z_g), T_gt = Trans(0, 0, −0.05)
Tsb_pre = Tsg_1 @ T(None, (0, 0, -0.05)) @ inv(T_bt())
assert np.allclose(Tsb_pre[:3, 3] - Tsb_goal[:3, 3], [0, 0, 0.05])
# A marker point on the outer edge of the gear blank ((0.04, 0, 0.03) in {o}, on the edge of the top face), transferred into {s} along both paths
mark_o = np.array([0.04, 0.0, 0.03])
m1 = (Tsw @ T_wc() @ Tco @ hom(mark_o))[:3]
m2 = (tree.T("s", "o") @ hom(mark_o))[:3]
assert np.allclose(m1, m2)

# Can the arm reach it? Numerical inverse kinematics (Chapter 15)
seed = np.array([0, -60, 100, -130, -90, 0]) * DEG
th = ur_ik(Tsb_goal, seed)
th = (th + math.pi) % (2 * math.pi) - math.pi
Tsb_reach = ur_fk_glb(th)                         # independent check with the algorithm of the 3D model
err_reach = np.abs(Tsb_reach - Tsb_goal).max()
assert err_reach < 1e-12
Tst_reach = Tsb_reach @ T_bt()
assert np.allclose(Tst_reach, Tsg_1, atol=1e-12)
assert np.allclose(T_ws() @ Tsb_reach @ T_bt(), T_wc() @ Tco @ T_og(), atol=1e-12)        # closure equation (5.5.1)
# Display form of the UR controller (x, y, z, rx, ry, rz): position in mm, orientation as a rotation vector (the exponential coordinates of Section 4.4)
rv = log_rot(Tsg_1[:3, :3])
assert np.allclose(rot_axis(rv, np.linalg.norm(rv)), Tsg_1[:3, :3], atol=1e-12)      # recover the orientation from the rotation vector

# ---------------------------------------------------------------- Example 5.5.2: error propagation
delta = 0.5 * DEG
p_g_w = (T_wc() @ Tco @ T_og())[:3, 3]
r_cg_w = p_g_w - P_WC                                 # from the camera origin to the grasp point, in {w}
errs, est = [], []
for k, R_err in enumerate((rot_x(delta), rot_y(delta), rot_z(delta))):
    Twc_bad = T_wc() @ T(R_err)                       # the actual camera orientation is off by δ about its own axis, while the program still uses the nominal value
    p_bad = (Twc_bad @ Tco @ T_og())[:3, 3]
    errs.append(np.linalg.norm(p_bad - p_g_w))
    axis_w = T_wc()[:3, k]                             # the error axis in {w}
    est.append(np.linalg.norm(np.cross(delta * axis_w, r_cg_w)))
for e, a in zip(errs, est):
    assert abs(e - a) < 0.01 * a + 1e-6                # the first-order estimate is within 1% of the exact value
lever = np.linalg.norm(r_cg_w)
# The same 0.5° error in the mounting of the robot base (about z_s): the lever is the distance from the grasp point to the z_s axis
Tws_bad = T_ws() @ T(rot_z(delta))
p_bad_s = (inv(Tws_bad) @ hom(p_g_w))[:3]
err_base = np.linalg.norm(p_bad_s - Tsg_1[:3, 3])
r_base = math.hypot(Tsg_1[0, 3], Tsg_1[1, 3])
assert abs(err_base - 2 * r_base * math.sin(delta / 2)) < 1e-12

out(
    Tco=texm(clean(Tco), 4), pco=vecm(Tco[:3, 3], 4), dist_co=np.linalg.norm(Tco[:3, 3]),
    Tsw=texm(clean(Tsw), 2), Tog=texm(clean(T_og()), 3),
    Two=texm(clean(Two), 4), Tsg=texm(clean(Tsg_1), 4), psg=vecm(Tsg_1[:3, 3], 4),
    Tsb_goal=texm(clean(Tsb_goal), 4), psb=vecm(Tsb_goal[:3, 3], 4), psb_pre=vecm(Tsb_pre[:3, 3], 4),
    m_s=vecm(m1, 4), th_deg=TT("，", ", ").join(f"{math.degrees(x):.2f}°".replace("-", "−") for x in th),
    th=[math.degrees(x) for x in th], err_reach=err_reach,
    ur_x=Tsg_1[0, 3] * 1000, ur_y=Tsg_1[1, 3] * 1000, ur_z=Tsg_1[2, 3] * 1000, rx=rv[0], ry=rv[1], rz=float(clean([rv[2]])[0]),
    rv_deg=math.degrees(np.linalg.norm(rv)),
    ex_mm=errs[0] * 1000, ey_mm=errs[1] * 1000, ez_mm=errs[2] * 1000,
    ax_mm=est[0] * 1000, ay_mm=est[1] * 1000, az_mm=est[2] * 1000,
    lever=lever, delta_rad=delta, base_mm=err_base * 1000, r_base=r_base,
    rcg=vecm(r_cg_w, 4),
)
