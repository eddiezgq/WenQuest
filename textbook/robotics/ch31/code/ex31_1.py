"""31.1 节的计算：连杆受力分析。

(1) 算例 31.1.1：WQ-CR5 手臂水平伸直、工具朝下、带 5 kg 负载（结构的代表工况），大臂、小臂铝管各截面的轴力、剪力、扭矩、弯矩
    （factory/digital/cae/wqcr5.py 的 section()：截面外侧所有零件重力的合力、合力矩）；与 MuJoCo 逆动力学的关节力矩核对。
(2) 算例 31.1.2：各关节承受的载荷：驱动力矩（电机、减速器）与倾覆力矩、轴向力、径向力（关节模组里的交叉滚子轴承）。
(3) 算例 31.1.3：强度校核：大臂、小臂根部的弯曲正应力、扭转切应力、剪切应力，第四强度理论的当量应力与屈服强度之比；
    再按“电机能出的最大力矩”（J2 模组的峰值能力）校核一次。
(4) 改变腕部的角度，J2 的重力矩最大能比代表工况大多少。
"""
import itertools
import math

import numpy as np

from _ch31 import G0, Q_OUT, W, tube_props
from bookout import out

q = Q_OUT
# ---------------------------------------------------------------- (1) 截面内力
sec = {}
for i, key in ((1, "u"), (2, "f")):
    s0, s1 = W.section(q, i, 0.0), W.section(q, i, 1.0)
    sec[key] = (s0, s1)
    out(**{f"{key}_V0": s0["V"], f"{key}_V1": s1["V"], f"{key}_M0": s0["Mb"], f"{key}_M1": s1["Mb"], f"{key}_T": abs(s0["T"]),
           f"{key}_N": abs(s0["N"])})
assert abs(sec["u"][0]["T"] - sec["u"][1]["T"]) < 1e-9 and abs(sec["u"][0]["N"]) < 1e-9          # 伸直水平：扭矩沿管不变，没有轴力
# 与 MuJoCo 的逆动力学核对：大臂根部的弯矩 = J2 的重力矩，J3 端 = J3 的重力矩
import mujoco  # noqa: E402
m = mujoco.MjModel.from_xml_string(W.mjcf(friction=False, payload_kg=W.PAYLOAD_KG))
d = mujoco.MjData(m)
d.qpos[:6] = q
mujoco.mj_inverse(m, d)
tau_mj = np.abs(d.qfrc_inverse[:6])
assert abs(sec["u"][0]["Mb"] - tau_mj[1]) < 1e-4 and abs(sec["u"][1]["Mb"] - tau_mj[2]) < 1e-4      # MJCF 里的质量写 6 位有效数字
# 手算：大臂根部 = J3 端的弯矩 + J3 端的剪力 × 管长 + 管与罩壳自重（均布）× 管长 / 2
a2 = abs(W.DH[1]["a"])
q_u = (sec["u"][0]["V"] - sec["u"][1]["V"]) / a2                    # N/m
M_hand = sec["u"][1]["Mb"] + sec["u"][1]["V"] * a2 + q_u * a2 ** 2 / 2
assert abs(M_hand - sec["u"][0]["Mb"]) < 1e-6
out(q_u=q_u, m_u_per_m=q_u / G0, M_hand=M_hand, d4_cm=W.DH[3]["d"] * 100, tau2=tau_mj[1], tau3=tau_mj[2])

# ---------------------------------------------------------------- (2) 关节载荷
J = [W.joint_loads(q, j) for j in range(6)]
out(**{f"jt{j + 1}": abs(J[j]["tau"]) for j in range(6)}, **{f"jm{j + 1}": J[j]["tilt"] for j in range(6)},
    **{f"ja{j + 1}": abs(J[j]["axial"]) for j in range(6)}, **{f"jr{j + 1}": J[j]["radial"] for j in range(6)})
assert J[0]["tilt"] > J[1]["tilt"] * 10 and abs(J[0]["tau"]) < 1e-9       # 伸直时 J1 不受驱动力矩，却扛着整条手臂的倾覆力矩
m_arm = sum(mm for _, mm, _, _ in W.gravity_points(q)) - W.PAYLOAD_KG
out(m_arm=m_arm, W_arm=(m_arm + W.PAYLOAD_KG) * G0)

# ---------------------------------------------------------------- (3) 强度
Y = W.YIELD_AL / 1e6
rows = {}
for key, (i, name, r, t) in zip(("u", "f"), ((1, "大臂", *W.TUBES["upper"]), (2, "小臂", *W.TUBES["fore"]))):
    pr = tube_props(r, t)
    s0 = sec[key][0]
    sig = s0["Mb"] / pr["Wb"] / 1e6
    tau_t = abs(s0["T"]) * r / pr["J"] / 1e6
    tau_v = 2 * s0["V"] / pr["A"] / 1e6                         # 薄壁圆管的最大剪应力（在中性轴上）≈ 2V/A
    vm = math.sqrt(sig ** 2 + 3 * tau_t ** 2)
    rows[key] = (sig, tau_t, tau_v, vm)
    out(**{f"{key}_sig": sig, f"{key}_taut": tau_t, f"{key}_tauv": tau_v, f"{key}_vm": vm, f"{key}_n": Y / vm,
           f"{key}_I_cm4": pr["I"] * 1e8, f"{key}_W_cm3": pr["Wb"] * 1e6, f"{key}_A_cm2": pr["A"] * 1e4})
cap2 = W.capacity("L")["peak"]
pr = tube_props(*W.TUBES["upper"])
sig_pk = cap2 / pr["Wb"] / 1e6
assert rows["u"][0] > rows["u"][1] * 10 and rows["u"][0] > rows["u"][2] * 10       # 弯曲正应力是大头
out(Y=Y, cap2=cap2, sig_pk=sig_pk, n_pk=Y / sig_pk, k_pk=cap2 / sec["u"][0]["Mb"])

# ---------------------------------------------------------------- (4) 腕部角度
best = 0.0
for q4, q5, q6 in itertools.product(range(-180, 180, 15), range(-180, 180, 15), range(-180, 180, 45)):
    qq = np.radians((0, 0, 0, q4, q5, q6))
    best = max(best, abs(W.joint_loads(qq, 1)["tau"]))
out(tau2_max=best, tau2_up=(best / tau_mj[1] - 1) * 100)
