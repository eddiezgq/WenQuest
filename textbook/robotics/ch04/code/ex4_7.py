"""4.7 节的算例。

算例 4.7.1：末端从 R0 = I 转到 R1（ZYX 欧拉角 ψ=90°, θ=45°, φ=90°），比较四种插值：
  (a) 矩阵元素直接线性插值——中点不是旋转矩阵；
  (b) 欧拉角线性插值——路径绕远、角速度不均匀；
  (c) 四元数线性插值后归一化（nlerp）——路径对，角速度不均匀；
  (d) 球面线性插值（Slerp）——绕一根轴匀速转过，路径最短。
"""
import math

import numpy as np

from _rot import rot_axis, rot_x, rot_y, rot_z
from bookout import out, tex, vec

d, deg = math.radians, math.degrees


def zyx(psi, th, phi):
    return rot_z(psi) @ rot_y(th) @ rot_x(phi)


def angle_between(Ra, Rb):
    c = (np.trace(Ra.T @ Rb) - 1) / 2
    return math.acos(max(-1.0, min(1.0, c)))


def q_from_R(R):
    q0 = 0.5 * math.sqrt(max(0.0, 1 + np.trace(R)))
    v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (4 * q0)
    return np.concatenate([[q0], v])


def R_from_q(q):
    q0, q1, q2, q3 = q / np.linalg.norm(q)
    return np.array([
        [1 - 2 * (q2 * q2 + q3 * q3), 2 * (q1 * q2 - q0 * q3), 2 * (q1 * q3 + q0 * q2)],
        [2 * (q1 * q2 + q0 * q3), 1 - 2 * (q1 * q1 + q3 * q3), 2 * (q2 * q3 - q0 * q1)],
        [2 * (q1 * q3 - q0 * q2), 2 * (q2 * q3 + q0 * q1), 1 - 2 * (q1 * q1 + q2 * q2)]])


def slerp(qa, qb, t):
    """式 (4.7.2)，含最短路径处理（qa·qb < 0 时取 −qb）。"""
    c = float(qa @ qb)
    if c < 0:
        qb, c = -qb, -c
    om = math.acos(min(1.0, c))
    if om < 1e-9:
        return qa
    return (math.sin((1 - t) * om) * qa + math.sin(t * om) * qb) / math.sin(om)


E1 = (d(90), d(45), d(90))
R0, R1 = np.eye(3), zyx(*E1)
q0, q1 = q_from_R(R0), q_from_R(R1)
theta_total = angle_between(R0, R1)

# (d) Slerp 与测地线 R0 exp(t log(R0ᵀ R1)) 一致
w = np.array([R1[2, 1] - R1[1, 2], R1[0, 2] - R1[2, 0], R1[1, 0] - R1[0, 1]]) / (2 * math.sin(theta_total))
for t in np.linspace(0, 1, 11):
    assert np.allclose(R_from_q(slerp(q0, q1, t)), rot_axis(w, t * theta_total))

# (a) 矩阵中点
Mmid = (R0 + R1) / 2
det_mid = float(np.linalg.det(Mmid))
col_norm = float(np.linalg.norm(Mmid[:, 0]))

# 逐段累计：路径长度（转过的总角度）与角速度
N = 1000
ts = np.linspace(0, 1, N + 1)
paths = {
    "euler": [zyx(*(t * np.array(E1))) for t in ts],
    "nlerp": [R_from_q((1 - t) * q0 + t * q1) for t in ts],
    "slerp": [R_from_q(slerp(q0, q1, t)) for t in ts],
}
length, speed = {}, {}
for k, Rs in paths.items():
    steps = [angle_between(Rs[i], Rs[i + 1]) for i in range(N)]
    length[k] = sum(steps)
    speed[k] = [s * N for s in steps]          # 单位：rad / 单位时间（整个过程用时 1）
assert abs(length["slerp"] - theta_total) < 1e-6 and abs(length["nlerp"] - theta_total) < 1e-6
assert length["euler"] > theta_total * 1.1
assert max(speed["slerp"]) / min(speed["slerp"]) < 1.0001

# 中点姿态的差别
mid = N // 2
mid_gap = angle_between(paths["euler"][mid], paths["slerp"][mid])

out(R1=tex(R1), theta_total=deg(theta_total), w=vec(w), det_mid=det_mid, col_norm=col_norm,
    len_euler=deg(length["euler"]), len_slerp=deg(length["slerp"]), ratio=length["euler"] / theta_total,
    sp_e_max=max(speed["euler"]) / theta_total, sp_e_min=min(speed["euler"]) / theta_total,
    sp_n_max=max(speed["nlerp"]) / theta_total, sp_n_min=min(speed["nlerp"]) / theta_total,
    mid_gap=deg(mid_gap), dot01=float(q0 @ q1), q1=vec(q1).replace("^{\\mathsf T}", ""))
