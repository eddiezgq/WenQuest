"""15.6 节：多元函数的极值与黑塞矩阵。
(1) f(x, y) = x⁴ + y⁴ − 4xy 的三个驻点 (0, 0)、(1, 1)、(−1, −1)：黑塞矩阵的特征值判定鞍点与极小值；
(2) 机器人：竖直向上的两连杆臂（参数见 _arm2m.py），关节装扭簧 k₁、k₂（N·m/rad）。θ = 0（直立）是平衡点，
    势能 V = ½k₁θ₁² + ½k₂θ₂² + 重力势能，黑塞矩阵 H = diag(k₁, k₂) − G。直立稳定 ⇔ H 正定。
    k₂ = 5 时，k₁ = 20 稳定；k₁ = 9.5 时 H 的对角元都正，但 det H < 0，不稳定。求 k₁ 的临界值。
(3) 末端受水平力 F = 2 N 时的平衡姿态：用牛顿法解 ∇V = 0，每一步解 H(θ)Δθ = −∇V(θ)；在解处检查 H 正定（稳定平衡）。"""
import numpy as np

import _arm2m as A2
from _num import sci
from bookout import out, tex, vec

# (1)
f_h = lambda x, y: np.array([[12 * x * x, -4.0], [-4.0, 12 * y * y]])
for name, (x, y) in (("o", (0, 0)), ("p", (1, 1))):
    H = f_h(x, y)
    out(**{f"H_{name}": tex(H), f"lam_{name}": vec(np.linalg.eigvalsh(H), 0)})
out(fmin=int(1 + 1 - 4))
# (2) 直立双连杆
G = A2.gravity_hessian()
out(G=tex(G, 2))
for name, k1 in (("s", 20.0), ("u", 9.5)):
    H = np.diag([k1, 5.0]) - G
    l = np.linalg.eigvalsh(H)
    out(**{f"H_{name}": tex(H, 2), f"lam_{name}": vec(l, 2), f"det_{name}": float(np.linalg.det(H)),
           f"min_{name}": float(H[0, 0])})
# 不稳定方向
w, V = np.linalg.eigh(np.diag([9.5, 5.0]) - G)
v = V[:, 0] * np.sign(V[0, 0])
out(v_u=vec(v, 2), v_ratio=float(v[1] / v[0]))
# 临界 k₁：det H = 0  ⇔  (k₁ − G₁₁)(k₂ − G₂₂) = G₁₂²
k2 = 5.0
k1c = G[0, 0] + G[0, 1] ** 2 / (k2 - G[1, 1])
out(k1c=float(k1c), G11=float(G[0, 0]))
# 差分检验黑塞矩阵
h = 1e-4
V0 = lambda a, b: A2.potential(a, b, 20.0, 5.0)
Hn = np.array([[(V0(h, 0) - 2 * V0(0, 0) + V0(-h, 0)) / h ** 2, (V0(h, h) - V0(h, -h) - V0(-h, h) + V0(-h, -h)) / (4 * h * h)],
               [0, (V0(0, h) - 2 * V0(0, 0) + V0(0, -h)) / h ** 2]])
Hn[1, 0] = Hn[0, 1]
out(err_H=float(np.abs(Hn - (np.diag([20.0, 5.0]) - G)).max()))

# (3) 牛顿法：末端水平力 F
k1, k2, F = 20.0, 5.0, 2.0
m1, m2, l1, l2, g = A2.M1, A2.M2, A2.L1, A2.L2, A2.G
a, b = (m1 * l1 / 2 + m2 * l1) * g, m2 * l2 / 2 * g


def grad(t):
    t1, t12 = t[0], t[0] + t[1]
    return np.array([k1 * t[0] - a * np.sin(t1) - b * np.sin(t12) - F * (l1 * np.cos(t1) + l2 * np.cos(t12)),
                     k2 * t[1] - b * np.sin(t12) - F * l2 * np.cos(t12)])


def hess(t):
    t1, t12 = t[0], t[0] + t[1]
    c = -b * np.cos(t12) + F * l2 * np.sin(t12)
    return np.array([[k1 - a * np.cos(t1) + F * l1 * np.sin(t1) + c, c], [c, k2 + c]])


t = np.zeros(2)
hist = []
for it in range(8):
    gn = np.linalg.norm(grad(t))
    hist.append(gn)
    if gn < 1e-12:
        break
    t = t - np.linalg.solve(hess(t), grad(t))
Hs = hess(t)
out(theta_deg=vec(np.degrees(t), 2), iters=len(hist) - 1, hist=",\\ ".join(sci(v, 1) for v in hist),
    Hs=tex(Hs, 2), lamHs=vec(np.linalg.eigvalsh(Hs), 2),
    tip_x=float(l1 * np.sin(t[0]) + l2 * np.sin(t[0] + t[1])))
# 线性化估计 Δθ ≈ H⁻¹ (Jᵀ F)
H0 = np.diag([k1, k2]) - G
Jt = np.array([F * (l1 + l2), F * l2])
out(lin_deg=vec(np.degrees(np.linalg.solve(H0, Jt)), 2))
