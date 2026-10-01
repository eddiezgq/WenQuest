"""4.4 节的算例。

算例 4.4.1：绕 (1,1,1)/√3 转 120°——罗德里格斯公式给出一个只含 0 和 1 的矩阵，正是算例 4.2.2 做法 A 的结果。
算例 4.4.2：对数映射——由算例 4.3.1 的矩阵求指数坐标，与特征向量法的结果一致。
算例 4.4.3：转角为 π 的特殊情形。
另：矢量形式、矩阵形式、矩阵指数（级数）三者一致；级数取多少项才够精确。
"""
import math

import numpy as np
from scipy.linalg import expm

from _rot import is_rotation, rot_axis, rot_x, rot_z, skew
from bookout import out, tex, vec

d = math.radians


def rodrigues_vector(w, t, v):
    """式 (4.4.1)：矢量形式。"""
    return v * math.cos(t) + np.cross(w, v) * math.sin(t) + w * (w @ v) * (1 - math.cos(t))


def exp_series(A, n):
    """矩阵指数的级数，取前 n 项：I + A + A²/2! + …"""
    S, term = np.eye(3), np.eye(3)
    for k in range(1, n):
        term = term @ A / k
        S = S + term
    return S


def log_so3(R):
    """对数映射：由 R 求 (ŵ, θ)，θ ∈ [0, π]。三种情形分开处理。"""
    c = float(np.clip((np.trace(R) - 1) / 2, -1, 1))
    t = math.acos(c)
    if t < 1e-9:
        return None, 0.0
    if math.pi - t < 1e-6:
        # R = 2ŵŵᵀ − I：取 (R + I)/2 中对角元最大的一列
        B = (R + np.eye(3)) / 2
        j = int(np.argmax(np.diag(B)))
        w = B[:, j] / math.sqrt(B[j, j])
        return w / np.linalg.norm(w), math.pi
    W = (R - R.T) / (2 * math.sin(t))
    return np.array([W[2, 1], W[0, 2], W[1, 0]]), t


# [ŵ]² = ŵŵᵀ − I，[ŵ]³ = −[ŵ]
w0 = np.array([0.6, 0.0, 0.8])
K = skew(w0)
assert np.allclose(K @ K, np.outer(w0, w0) - np.eye(3)) and np.allclose(K @ K @ K, -K)

# 算例 4.4.1
w1 = np.ones(3) / math.sqrt(3)
t1 = d(120)
R1 = rot_axis(w1, t1)
assert np.allclose(R1, np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]]))
assert np.allclose(R1, rot_z(d(90)) @ rot_x(d(90)))        # 做法 A
for v in np.eye(3):                                          # 三种写法一致
    assert np.allclose(rodrigues_vector(w1, t1, v), R1 @ v)
assert np.allclose(expm(skew(w1) * t1), R1)

# 级数：误差随项数的变化（图 4.4.2 也用这组数）
A = skew(w1) * t1
errors = [float(np.abs(exp_series(A, n) - R1).max()) for n in range(1, 31)]
n_needed = next(n for n, e in zip(range(1, 31), errors) if e < 1e-12)

# 算例 4.4.2：对数映射
R2 = rot_z(d(30)) @ rot_x(d(45))
w2, t2 = log_so3(R2)
assert is_rotation(R2) and np.allclose(rot_axis(w2, t2), R2)
vals, vecs = np.linalg.eig(R2)
w_eig = np.real(vecs[:, int(np.argmin(abs(vals - 1)))])
assert np.allclose(abs(w_eig @ w2), 1)                       # 与 4.3 节特征向量法一致（同一直线）
W2 = (R2 - R2.T) / 2

# 算例 4.4.3：转角为 π
w3 = np.array([0.6, 0.8, 0.0])
R3 = rot_axis(w3, math.pi)
assert np.allclose(R3, 2 * np.outer(w3, w3) - np.eye(3))
w3_back, t3 = log_so3(R3)
assert abs(t3 - math.pi) < 1e-12 and np.allclose(abs(w3_back @ w3), 1)
assert np.allclose(R3 - R3.T, 0)                             # 此时 R − Rᵀ = 0，一般公式失效

out(R1=tex(R1), sin120=math.sin(t1), w2=vec(w2), t2_deg=math.degrees(t2), t2=t2, expc2=vec(w2 * t2), sin_t2=math.sin(t2),
    W2=tex(W2), R3=tex(R3), half_RI=tex((R3 + np.eye(3)) / 2), n_needed=n_needed,
    err5=errors[4], err10=errors[9], err20=errors[19], _errors=errors)
