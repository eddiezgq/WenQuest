"""本章共用：平面三连杆机械臂（冗余：末端位置 2 维、关节 3 个）的雅可比矩阵与质量矩阵。以下划线开头，构建时不单独运行。

三根连杆是均匀细杆，长度 l_i、质量 m_i，绕质心的转动惯量 m_i l_i²/12。关节角 q = (q1, q2, q3) 为相对角。
动能 = ½ Σ [ m_i ‖ṗ_ci‖² + I_i ω_i² ]，ṗ_ci = J_ci q̇，ω_i = q̇1 + … + q̇i，所以
    动能 = ½ q̇ᵀ M(q) q̇，  M(q) = Σ_i ( m_i J_ciᵀ J_ci + I_i j_iᵀ j_i ),  j_i = (1, …, 1, 0, …)（前 i 个为 1）。
网页实验 12.3 用同样的参数与公式（lab12_3.js）。
"""
import numpy as np

L = np.array([0.40, 0.35, 0.25])     # 连杆长度 / m
MASS = np.array([4.0, 2.5, 1.0])     # 连杆质量 / kg


def angles(q):
    return np.cumsum(q)               # 各连杆的绝对角


def points(q, l=L):
    """基座、肘、腕、末端四个点的坐标（4×2）。"""
    a = angles(q)
    P = [np.zeros(2)]
    for i in range(3):
        P.append(P[-1] + l[i] * np.array([np.cos(a[i]), np.sin(a[i])]))
    return np.array(P)


def jac_point(q, i, s, l=L):
    """连杆 i（0 起）上距其近端 s 处的点的 2×3 位置雅可比。"""
    a = angles(q)
    J = np.zeros((2, 3))
    for k in range(i + 1):            # 关节 k 转动，带动连杆 k, k+1, …, i
        # 该点相对关节 k 的位置向量 r = Σ_{j=k}^{i-1} l_j e(a_j) + s e(a_i)
        r = sum(l[j] * np.array([np.cos(a[j]), np.sin(a[j])]) for j in range(k, i)) + s * np.array([np.cos(a[i]), np.sin(a[i])])
        J[:, k] = [-r[1], r[0]]
    return J


def jac(q, l=L):
    """末端点的 2×3 雅可比。"""
    return jac_point(q, 2, l[2], l)


def mass(q, l=L, m=MASS):
    M = np.zeros((3, 3))
    for i in range(3):
        Jc = jac_point(q, i, l[i] / 2, l)
        j = np.array([1.0 if k <= i else 0.0 for k in range(3)])
        M += m[i] * Jc.T @ Jc + m[i] * l[i] ** 2 / 12 * np.outer(j, j)
    return M
