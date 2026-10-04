"""Examples 1.4.1–1.4.4: counting degrees of freedom; how large a reduction ratio a joint needs; how far the end
moves for one step of encoder resolution; how far the end travels in one control cycle.

1.4.1 Degrees of freedom of a rigid body: counted as "coordinates of the points − distance constraints", then checked
      independently with the rank of the Jacobian of the constraints (the two methods must agree).
      Joint variables, base DOF and actuator counts of the eight library models are counted from their joint
      tables (Table 1.4.1).
1.4.2 Joint speed 180°/s and an assumed motor rated speed of 3000 r/min give the reduction ratio; compared with the
      gear reducer WQR-105 of the digital factory.
1.4.3 A joint encoder with 2^20 counts per revolution: the arc length at an arm length of 0.85 m.
1.4.4 Control cycle 2 ms (500 Hz): the displacement per cycle at an end speed of 1 m/s.
"""
import math

import numpy as np

from _ch1 import ALL8, dof_summary, factory
from bookout import T, out

rng = np.random.default_rng(14)


# ---------------------------------------------------------------- Example 1.4.1: DOF of a rigid body
def rigid_dof(dim, n_pts):
    """n non-collinear points rigidly connected: dim·n coordinates, constant pairwise distances are the constraints;
    DOF = number of coordinates − rank of the constraint Jacobian."""
    P = rng.normal(size=(n_pts, dim))
    rows = []
    for i in range(n_pts):
        for j in range(i + 1, n_pts):
            g = np.zeros(n_pts * dim)            # partial derivatives of the constraint |p_i − p_j|² = const
            g[i * dim:(i + 1) * dim] = 2 * (P[i] - P[j])
            g[j * dim:(j + 1) * dim] = -2 * (P[i] - P[j])
            rows.append(g)
    rank = np.linalg.matrix_rank(np.array(rows))
    return n_pts * dim - rank, len(rows), rank


plane2 = rigid_dof(2, 2)                         # plane: two points
plane3 = rigid_dof(2, 3)                         # plane: three points (one more point, two more constraints, same DOF)
space3 = rigid_dof(3, 3)                         # space: three points
space4 = rigid_dof(3, 4)
assert plane2[0] == plane3[0] == 3 and space3[0] == space4[0] == 6
assert 2 * 2 - 1 == 3 and 3 * 3 - 3 == 6         # the counts of Eqs. (1.4.1), (1.4.2)

# Table 1.4.1: the eight library models
rows = {r["id"]: r for r in (dof_summary(e) for e in ALL8)}
ur, pa, go, df, x2, g1 = (rows[k] for k in ("B-ARM-UR5E", "B-ARM-PANDA", "B-LEG-GO2", "B-EDU-DIFF", "B-UAV-X2", "B-HUM-G1"))
assert ur["config_dof"] == 6 and pa["n_joints"] == 9 and pa["joints_indep"] == 8
assert go["config_dof"] == 18 and x2["config_dof"] == 6 and x2["n_joints"] == 0 and g1["config_dof"] == 35
# underactuated: fewer actuators than configuration DOF
under = [k for k, r in rows.items() if r["actuators"] < r["config_dof"] and not r["closed"]]
assert set(under) == {"B-LEG-GO2", "B-EDU-DIFF", "B-UAV-X2", "B-HUM-G1"}

# ---------------------------------------------------------------- Example 1.4.2: reduction ratio
w_joint_deg = 180.0                               # maximum speed of each UR5e joint, °/s (datasheet)
n_joint = w_joint_deg / 360 * 60                  # r/min
n_motor = 3000.0                                  # assumed motor rated speed, r/min (assumption)
i_need = n_motor / n_joint
eta = 0.8                                         # assumed reducer efficiency (assumption)
tau_motor = 1.0                                   # assume a motor output of 1 N·m
tau_joint = tau_motor * i_need * eta
data, _ = factory()
i_wqr = data.ratio()                              # WQR-105: product of the tooth ratios of the two gear stages
g = data.GEARS
i_check = (g["GR-202"]["z"] / g["SH-101"]["z"]) * (g["GR-302"]["z"] / g["GR-203"]["z"])
assert abs(i_wqr - i_check) < 1e-12 and abs(i_wqr - 10.5) < 1e-12
n_in = data.INPUT_SPEED_RPM
n_out = n_in / i_wqr

# ---------------------------------------------------------------- Example 1.4.3: encoder resolution
bits = 20
counts = 2 ** bits
dtheta_deg = 360 / counts
dtheta_rad = 2 * math.pi / counts
R_arm = 0.85                                       # m, UR5e reach
ds_um = R_arm * dtheta_rad * 1e6                   # arc length = radius × angle in radians
assert abs(ds_um - R_arm * math.radians(dtheta_deg) * 1e6) < 1e-12
rep_um = 30.0                                      # UR5e pose repeatability ±0.03 mm
# ---------------------------------------------------------------- Example 1.4.4: control cycle
f_ctrl = 500.0                                     # Hz (period of the UR e-Series real-time data interface)
T_ctrl_ms = 1000 / f_ctrl
v_tcp = 1.0                                        # m/s
ds_cycle_mm = v_tcp * T_ctrl_ms                    # m/s × ms = mm

out(plane_coords=4, plane_dof=plane2[0], plane_rank=plane2[2], space_coords=9, space_dof=space3[0], space_rank=space3[2],
    space4_cons=space4[1], space4_rank=space4[2],
    ur_n=ur["n_joints"], pa_n=pa["n_joints"], pa_indep=pa["joints_indep"], go_n=go["n_joints"], go_cfg=go["config_dof"],
    df_n=df["n_joints"], df_cfg=df["config_dof"], x2_n=x2["n_joints"], x2_cfg=x2["config_dof"], g1_n=g1["n_joints"],
    g1_cfg=g1["config_dof"], go_act=go["actuators"], x2_act=x2["actuators"], df_act=df["actuators"], pa_act=pa["actuators"],
    g1_dof_sheet=g1["datasheet"].get("dof"),
    sc_n=rows["B-SCA-WQ4"]["n_joints"], sc_pri=rows["B-SCA-WQ4"]["n_pri"], de_n=rows["B-PAR-DELTA"]["n_joints"],
    n_joint=n_joint, n_motor=n_motor, i_need=i_need, eta=eta, tau_joint=tau_joint, i_wqr=i_wqr, n_in=n_in, n_out=n_out,
    bits=bits, counts=counts, dtheta_deg=dtheta_deg, ds_um=ds_um, rep_um=rep_um, rep_ratio=rep_um / ds_um,
    f_ctrl=f_ctrl, T_ctrl_ms=T_ctrl_ms, ds_cycle_mm=ds_cycle_mm,
    under=T("Go2、差速小车、四旋翼、G1", "Go2, differential cart, quadrotor, G1"))
