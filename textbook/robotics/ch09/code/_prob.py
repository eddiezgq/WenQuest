"""第 9 章共用：高斯密度、平面 2R 臂（取 UR5e 大臂与小臂的长度，与第 2 章相同）、UR5e 的指数积正运动学（表 12.1.1），
不确定性椭圆的画法。以下划线开头，构建时不单独运行。"""
import math

import numpy as np

L2R = (0.425, 0.392)          # 平面 2R 臂：L1、L2，m（2.1 节）


def gauss_pdf(x, mu=0.0, sigma=1.0):
    """一维高斯密度，式 (9.1.13)。"""
    x = np.asarray(x, float)
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))


def p_within(k):
    """标准高斯变量落在 [−k, k] 内的概率 erf(k/√2)。"""
    return math.erf(k / math.sqrt(2))


# ---------------------------------------------------------------- 平面 2R 臂

def fk2(th, L=L2R):
    """末端位置 (x, y)，th 为 (θ1, θ2)，rad；θ2 相对大臂。可以对多组关节角同时计算（th 的形状为 (2, N)）。"""
    t1, t2 = th[0], th[1]
    return np.array([L[0] * np.cos(t1) + L[1] * np.cos(t1 + t2), L[0] * np.sin(t1) + L[1] * np.sin(t1 + t2)])


def jac2(th, L=L2R):
    """雅可比矩阵，式 (2.1.9)，单位 m/rad。"""
    t1, t2 = th
    s1, c1, s12, c12 = math.sin(t1), math.cos(t1), math.sin(t1 + t2), math.cos(t1 + t2)
    return np.array([[-L[0] * s1 - L[1] * s12, -L[1] * s12], [L[0] * c1 + L[1] * c12, L[1] * c12]])


# ---------------------------------------------------------------- UR5e（第 12 章表 12.1.1 的旋量轴）

def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]], dtype=float)


def exp6(w, v, t):
    """转动关节的 e^{[S]θ}，S = (ω, v)，式 (12.1.5)。"""
    K = skew(w)
    T = np.eye(4)
    T[:3, :3] = np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K
    G = np.eye(3) * t + (1 - math.cos(t)) * K + (t - math.sin(t)) * K @ K
    T[:3, 3] = G @ v
    return T


H1, W1, LU1, W2, LU2, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1
_yd = np.array([0, -1.0, 0])
UR_AXES = [(np.array([0, 0, 1.0]), np.array([0, 0, H1])), (_yd, np.array([0, -W1, H1])),
           (_yd, np.array([-LU1, -W1 + W2, H1])), (_yd, np.array([-LU1 - LU2, -W1 + W2, H1])),
           (np.array([0, 0, -1.0]), np.array([-LU1 - LU2, -W1 + W2 - W3, H1])),
           (_yd, np.array([-LU1 - LU2, -W1 + W2 - W3, H1 - H2]))]
UR_M = np.array([[1.0, 0, 0, -LU1 - LU2], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]])


def ur_fk(th):
    """UR5e 法兰中心的位姿 T = e^{[S1]θ1} … e^{[S6]θ6} M（式 (12.2.3)）。"""
    T = np.eye(4)
    for (w, q), t in zip(UR_AXES, th):
        T = T @ exp6(w, -np.cross(w, q), t)
    return T @ UR_M


def ur_jac_pos(th):
    """法兰中心位置对六个关节角的雅可比矩阵（3×6）：第 i 列 = 当前第 i 根轴的方向 × (末端 − 轴上一点)。"""
    p = ur_fk(th)[:3, 3]
    T = np.eye(4)
    cols = []
    for (w, q), t in zip(UR_AXES, th):
        wi = T[:3, :3] @ w
        qi = T[:3, :3] @ q + T[:3, 3]
        cols.append(np.cross(wi, p - qi))
        T = T @ exp6(w, -np.cross(w, q), t)
    return np.array(cols).T


def num_jac(f, x, h=1e-6):
    """中心差分求雅可比矩阵：第 i 列 = (f(x + h eᵢ) − f(x − h eᵢ)) / 2h。"""
    x = np.asarray(x, float)
    cols = []
    for i in range(len(x)):
        e = np.zeros_like(x)
        e[i] = h
        cols.append((f(x + e) - f(x - e)) / (2 * h))
    return np.array(cols).T


# ---------------------------------------------------------------- 不确定性椭圆

def ellipse_pts(Sigma, center=(0, 0), c=1.0, n=200):
    """满足 (x − μ)ᵀ Σ⁻¹ (x − μ) = c² 的椭圆上的点（2×n）。"""
    lam, V = np.linalg.eigh(Sigma)
    t = np.linspace(0, 2 * math.pi, n)
    circ = np.vstack([np.cos(t), np.sin(t)])
    return np.asarray(center, float)[:, None] + c * V @ np.diag(np.sqrt(lam)) @ circ
