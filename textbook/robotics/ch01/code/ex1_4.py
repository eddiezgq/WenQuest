"""算例 1.4.1–1.4.4：自由度的计数；关节需要多大的减速比；编码器分辨率对应末端多大的位移；一个控制周期里末端走多远。

1.4.1 刚体的自由度：用“点的坐标数 − 距离约束数”计数，再用约束的雅可比矩阵的秩独立核对（两种方法必须一致）。
      零件库八台模型的关节变量、基座自由度和执行器数，由关节表统计（表 1.4.1）。
1.4.2 关节转速 180°/s，设电机额定转速 3000 r/min，求减速比；与数字工厂 WQR-105 的齿轮减速器对照。
1.4.3 设关节编码器每转 2^20 个读数，臂长 0.85 m 处的弧长。
1.4.4 控制周期 2 ms（500 Hz），末端速度 1 m/s 时每个周期的位移。
"""
import math

import numpy as np

from _ch1 import ALL8, dof_summary, factory
from bookout import T, out

rng = np.random.default_rng(14)


# ---------------------------------------------------------------- 算例 1.4.1：刚体的自由度
def rigid_dof(dim, n_pts):
    """n 个不共线的点刚性连接：坐标 dim·n 个，两两距离不变是约束；自由度 = 坐标数 − 约束雅可比的秩。"""
    P = rng.normal(size=(n_pts, dim))
    rows = []
    for i in range(n_pts):
        for j in range(i + 1, n_pts):
            g = np.zeros(n_pts * dim)            # 约束 |p_i − p_j|² = 常数 对各坐标的偏导数
            g[i * dim:(i + 1) * dim] = 2 * (P[i] - P[j])
            g[j * dim:(j + 1) * dim] = -2 * (P[i] - P[j])
            rows.append(g)
    rank = np.linalg.matrix_rank(np.array(rows))
    return n_pts * dim - rank, len(rows), rank


plane2 = rigid_dof(2, 2)                         # 平面：两点
plane3 = rigid_dof(2, 3)                         # 平面：三点（多一个点，约束多两个，自由度不变）
space3 = rigid_dof(3, 3)                         # 空间：三点
space4 = rigid_dof(3, 4)
assert plane2[0] == plane3[0] == 3 and space3[0] == space4[0] == 6
assert 2 * 2 - 1 == 3 and 3 * 3 - 3 == 6         # 式 (1.4.1)、(1.4.2) 的计数

# 表 1.4.1：零件库八台模型
rows = {r["id"]: r for r in (dof_summary(e) for e in ALL8)}
ur, pa, go, df, x2, g1 = (rows[k] for k in ("B-ARM-UR5E", "B-ARM-PANDA", "B-LEG-GO2", "B-EDU-DIFF", "B-UAV-X2", "B-HUM-G1"))
assert ur["config_dof"] == 6 and pa["n_joints"] == 9 and pa["joints_indep"] == 8
assert go["config_dof"] == 18 and x2["config_dof"] == 6 and x2["n_joints"] == 0 and g1["config_dof"] == 35
# 欠驱动：执行器少于构型自由度
under = [k for k, r in rows.items() if r["actuators"] < r["config_dof"] and not r["closed"]]
assert set(under) == {"B-LEG-GO2", "B-EDU-DIFF", "B-UAV-X2", "B-HUM-G1"}

# ---------------------------------------------------------------- 算例 1.4.2：减速比
w_joint_deg = 180.0                               # UR5e 各关节最大转速，°/s（厂家参数表）
n_joint = w_joint_deg / 360 * 60                  # r/min
n_motor = 3000.0                                  # 设电机额定转速，r/min（假设）
i_need = n_motor / n_joint
eta = 0.8                                         # 设减速器效率（假设）
tau_motor = 1.0                                   # 设电机输出 1 N·m
tau_joint = tau_motor * i_need * eta
data, _ = factory()
i_wqr = data.ratio()                              # WQR-105：两级齿轮齿数比之积
g = data.GEARS
i_check = (g["GR-202"]["z"] / g["SH-101"]["z"]) * (g["GR-302"]["z"] / g["GR-203"]["z"])
assert abs(i_wqr - i_check) < 1e-12 and abs(i_wqr - 10.5) < 1e-12
n_in = data.INPUT_SPEED_RPM
n_out = n_in / i_wqr

# ---------------------------------------------------------------- 算例 1.4.3：编码器分辨率
bits = 20
counts = 2 ** bits
dtheta_deg = 360 / counts
dtheta_rad = 2 * math.pi / counts
R_arm = 0.85                                       # m，UR5e 工作半径
ds_um = R_arm * dtheta_rad * 1e6                   # 弧长 = 半径 × 弧度
assert abs(ds_um - R_arm * math.radians(dtheta_deg) * 1e6) < 1e-12
rep_um = 30.0                                      # UR5e 重复定位精度 ±0.03 mm
# ---------------------------------------------------------------- 算例 1.4.4：控制周期
f_ctrl = 500.0                                     # Hz（UR e 系列实时数据接口的周期）
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
