"""本章共用：UR5e 的标准 DH 模型与运动学标定的模拟数据（23.2、23.5、23.6 节）。以下划线开头，构建时不单独运行。
名义 DH 参数取自优傲机器人公布的 UR5e 参数：d = (0.1625, 0, 0, 0.1333, 0.0997, 0.0996) m，
a = (0, −0.425, −0.3922, 0, 0, 0) m，α = (π/2, 0, 0, π/2, −π/2, 0)。
每个关节 4 个参数 (θ₀ᵢ, dᵢ, aᵢ, αᵢ)，共 24 个；第 i 个关节的变换为 Rz(qᵢ + θ₀ᵢ)·Tz(dᵢ)·Tx(aᵢ)·Rx(αᵢ)。
“真实”机器人在每个参数上加一个小误差（长度 ±1 mm 量级、角度 ±1 mrad 量级，随机数种子固定）；
激光跟踪仪测末端（法兰中心）的位置，噪声标准差 0.05 mm。"""
import math

import numpy as np

D0 = np.array([0.1625, 0.0, 0.0, 0.1333, 0.0997, 0.0996])
A0 = np.array([0.0, -0.425, -0.3922, 0.0, 0.0, 0.0])
AL0 = np.array([math.pi / 2, 0.0, 0.0, math.pi / 2, -math.pi / 2, 0.0])
TH0 = np.zeros(6)
NOMINAL = np.concatenate([TH0, D0, A0, AL0])        # 参数向量：(θ₀₁…θ₀₆, d₁…d₆, a₁…a₆, α₁…α₆)
NAMES = [f"θ0{i + 1}" for i in range(6)] + [f"d{i + 1}" for i in range(6)] + [f"a{i + 1}" for i in range(6)] + [f"α{i + 1}" for i in range(6)]
TEXNAMES = ([f"\\theta_{{0{i + 1}}}" for i in range(6)] + [f"d_{i + 1}" for i in range(6)] + [f"a_{i + 1}" for i in range(6)]
            + [f"\\alpha_{i + 1}" for i in range(6)])     # 正文公式中的写法


def fk(p, q):
    """参数 p（24 维）、关节角 q（6 维）→ 末端位置（m）。"""
    th, d, a, al = p[0:6], p[6:12], p[12:18], p[18:24]
    T = np.eye(4)
    for i in range(6):
        ct, st = math.cos(q[i] + th[i]), math.sin(q[i] + th[i])
        ca, sa = math.cos(al[i]), math.sin(al[i])
        Ti = np.array([[ct, -st * ca, st * sa, a[i] * ct],
                       [st, ct * ca, -ct * sa, a[i] * st],
                       [0.0, sa, ca, d[i]],
                       [0.0, 0.0, 0.0, 1.0]])
        T = T @ Ti
    return T[:3, 3].copy()


def fk_all(p, Q):
    return np.concatenate([fk(p, q) for q in Q])


def jac(p, Q, h=1e-7):
    """测量（3N 个坐标）对 24 个参数的雅可比矩阵（中心差分）。"""
    J = np.zeros((3 * len(Q), 24))
    for k in range(24):
        e = np.zeros(24)
        e[k] = h
        J[:, k] = (fk_all(p + e, Q) - fk_all(p - e, Q)) / (2 * h)
    return J


def true_params(seed=23061):
    rng = np.random.default_rng(seed)
    dp = np.concatenate([rng.normal(0, 1e-3, 6),           # 关节零点 θ₀：1 mrad
                         rng.normal(0, 1e-3, 6),           # d：1 mm
                         rng.normal(0, 1e-3, 6),           # a：1 mm
                         rng.normal(0, 1e-3, 6)])          # α：1 mrad
    return NOMINAL + dp


def poses(n, seed=23062):
    rng = np.random.default_rng(seed)
    lo = np.radians([-170, -150, -150, -170, -170, -170])
    hi = np.radians([170, -30, 150, 170, 170, 170])
    return rng.uniform(lo, hi, size=(n, 6))


def measure(p_true, Q, sigma=5e-5, seed=23063):
    rng = np.random.default_rng(seed)
    return fk_all(p_true, Q) + rng.normal(0, sigma, 3 * len(Q))
