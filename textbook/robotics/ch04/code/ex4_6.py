"""4.6 节的算例。

算例 4.6.1：用四元数合成“先绕 x 轴转 90°、再绕 z 轴转 90°”，得到 (1/2, 1/2, 1/2, 1/2)，即绕 (1,1,1)/√3 转 120°（与算例 4.4.1 一致）。
算例 4.6.2：由算例 4.3.1 的旋转矩阵求四元数，再换回旋转矩阵核对。
另：q v q* 与罗德里格斯公式一致；q 与 −q 给出同一转动；四元数乘法不可交换；运算量比较。
"""
import math

import numpy as np

from _rot import is_rotation, rot_axis, rot_x, rot_z
from bookout import out, tex, vec

d = math.radians


def qmul(a, b):
    """式 (4.6.4)：(a0, a)(b0, b) = (a0 b0 − a·b, a0 b + b0 a + a×b)。"""
    a0, av, b0, bv = a[0], a[1:], b[0], b[1:]
    return np.concatenate([[a0 * b0 - av @ bv], a0 * bv + b0 * av + np.cross(av, bv)])


def qconj(q):
    return np.concatenate([[q[0]], -q[1:]])


def q_axis(w, t):
    """式 (4.6.5)：q = (cos θ/2, sin θ/2 ŵ)。"""
    w = np.asarray(w, float) / np.linalg.norm(w)
    return np.concatenate([[math.cos(t / 2)], math.sin(t / 2) * w])


def q_rotate(q, v):
    return qmul(qmul(q, np.concatenate([[0.0], v])), qconj(q))[1:]


def q_to_R(q):
    """式 (4.6.7)。"""
    q0, q1, q2, q3 = q
    return np.array([
        [1 - 2 * (q2 * q2 + q3 * q3), 2 * (q1 * q2 - q0 * q3), 2 * (q1 * q3 + q0 * q2)],
        [2 * (q1 * q2 + q0 * q3), 1 - 2 * (q1 * q1 + q3 * q3), 2 * (q2 * q3 - q0 * q1)],
        [2 * (q1 * q3 - q0 * q2), 2 * (q2 * q3 + q0 * q1), 1 - 2 * (q1 * q1 + q2 * q2)]])


def R_to_q(R):
    """式 (4.6.8)–(4.6.10)：先求四个分量中绝对值最大的一个，再由它求其余三个（数值稳定）。"""
    tr = np.trace(R)
    cand = [1 + tr, 1 + 2 * R[0, 0] - tr, 1 + 2 * R[1, 1] - tr, 1 + 2 * R[2, 2] - tr]   # 即 4q_i²
    i = int(np.argmax(cand))
    s = math.sqrt(cand[i]) / 2
    q = np.zeros(4)
    q[i] = s
    if i == 0:
        q[1:] = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (4 * s)
    elif i == 1:
        q[0], q[2], q[3] = (R[2, 1] - R[1, 2]) / (4 * s), (R[0, 1] + R[1, 0]) / (4 * s), (R[0, 2] + R[2, 0]) / (4 * s)
    elif i == 2:
        q[0], q[1], q[3] = (R[0, 2] - R[2, 0]) / (4 * s), (R[0, 1] + R[1, 0]) / (4 * s), (R[1, 2] + R[2, 1]) / (4 * s)
    else:
        q[0], q[1], q[2] = (R[1, 0] - R[0, 1]) / (4 * s), (R[0, 2] + R[2, 0]) / (4 * s), (R[1, 2] + R[2, 1]) / (4 * s)
    return q if q[0] >= 0 else -q


# 乘法表：ij = k, jk = i, ki = j, ji = −k, i² = −1
i_, j_, k_ = np.eye(4)[1], np.eye(4)[2], np.eye(4)[3]
assert np.allclose(qmul(i_, j_), k_) and np.allclose(qmul(j_, i_), -k_)
assert np.allclose(qmul(i_, i_), [-1, 0, 0, 0]) and np.allclose(qmul(qmul(i_, j_), k_), [-1, 0, 0, 0])

# q v q* 与罗德里格斯公式一致（随机的轴、角、矢量）
rng = np.random.default_rng(7)
for _ in range(20):
    w, t, v = rng.normal(size=3), rng.uniform(-math.pi, math.pi), rng.normal(size=3)
    assert np.allclose(q_rotate(q_axis(w, t), v), rot_axis(w, t) @ v)
    assert np.allclose(q_rotate(-q_axis(w, t), v), rot_axis(w, t) @ v)      # q 与 −q 同一转动
    assert np.allclose(q_to_R(q_axis(w, t)), rot_axis(w, t))

# 由 R 求 q：四个分支都要正确（含转角接近 180° 的情形）
for _ in range(200):
    w, t = rng.normal(size=3), rng.uniform(0, math.pi)
    Rr = rot_axis(w, t)
    assert np.allclose(q_to_R(R_to_q(Rr)), Rr)
for axis in np.eye(3):
    Rr = rot_axis(axis, math.pi)
    assert np.allclose(q_to_R(R_to_q(Rr)), Rr)


def tup(v):
    return vec(v).replace("^{\\mathsf T}", "")


# 算例 4.6.1
qx, qz = q_axis([1, 0, 0], d(90)), q_axis([0, 0, 1], d(90))
q = qmul(qz, qx)                         # 先 qx 后 qz：后做的写在左边
assert np.allclose(q, [0.5, 0.5, 0.5, 0.5])
assert np.allclose(q_to_R(q), rot_z(d(90)) @ rot_x(d(90)))
q_rev = qmul(qx, qz)
half_angle = math.degrees(math.acos(q[0]))

# 算例 4.6.2
R = rot_z(d(30)) @ rot_x(d(45))
qR = R_to_q(R)
assert is_rotation(R) and np.allclose(q_to_R(qR), R) and abs(np.linalg.norm(qR) - 1) < 1e-12
theta = 2 * math.acos(qR[0])
w = qR[1:] / math.sin(theta / 2)
assert np.allclose(rot_axis(w, theta), R)

# 运算量：合成两次转动
mul_matrix, add_matrix = 27, 18           # 3×3 矩阵乘法
mul_quat, add_quat = 16, 12               # 四元数乘法

# 图 4.6.1 的数据：转角从 0 到 4π，q0 = cos(θ/2) 与 R 的 (1,1) 元素
ts = list(np.linspace(0, 4 * math.pi, 241))
out(qx=tup(qx), qz=tup(qz), q=tup(q), q_rev=tup(q_rev), half_angle=half_angle, c45=math.cos(d(45)),
    R=tex(R), qR=tup(qR), q0R=qR[0], theta_deg=math.degrees(theta), w=vec(w),
    mul_matrix=mul_matrix, add_matrix=add_matrix, mul_quat=mul_quat, add_quat=add_quat,
    _ts=ts)
