"""21.4 节：特征值与奇异值的扰动。(1) 外尔不等式：关节电机热模型（对称化后）的热阻有 ±10% 的误差，
各衰减率的变化不超过 ‖E‖₂；(2) 奇异值的外尔不等式：两连杆机械臂的两个关节编码器零点各差 0.2°，雅可比矩阵的奇异值变化不超过 ‖δJ‖₂，
接近奇异的位形上最小奇异值的相对误差大；(3) 鲍尔–费克定理：非对称的 A = −C⁻¹G 由 V = C^{−1/2}Q 对角化，κ₂(V) = √10；
(4) 单个特征值的条件数 1/|yᴴx|：友矩阵；(5) 不可对角化：8 个相同一阶环节串联，扰动 ε 使特征值移动约 ε^{1/8}。"""
import math

import numpy as np

from _num import sci
from _thermal import model
from bookout import out, vec

rng = np.random.default_rng(21041)
# (1) 外尔不等式（对称矩阵）
cap, G, A = model()
Ch = np.diag(cap ** -0.5)
S = -Ch @ G @ Ch                       # 与 A 相似的对称矩阵
lam = np.linalg.eigvalsh(S)
worst = 0.0
ratios = []
for trial in range(500):
    f = lambda v: tuple(x * (1 + 0.1 * (2 * rng.random() - 1)) for x in v)
    cap2, G2, A2 = model(rwh=f((0.5,) * 3), rha=f((1.0,) * 3), rhh=f((2.0,) * 2))
    S2 = -Ch @ G2 @ Ch
    E = S2 - S
    shift = np.max(np.abs(np.linalg.eigvalsh(S2) - lam))
    nE = np.linalg.norm(E, 2)
    assert shift <= nE + 1e-15
    ratios.append(shift / nE)
out(lam=", ".join(f"{x:.5f}" for x in lam), w_ratio_max=float(max(ratios)), w_ratio_med=float(np.median(ratios)))
# 一次具体的扰动
cap2, G2, A2 = model(rwh=(0.55, 0.5, 0.5), rha=(1.0, 1.1, 1.0), rhh=(2.0, 1.8, ))
S2 = -Ch @ G2 @ Ch
d = np.linalg.eigvalsh(S2) - lam
out(nE1=sci(float(np.linalg.norm(S2 - S, 2)), 1), dmax1=sci(float(np.max(np.abs(d))), 1))

# (2) 奇异值的外尔不等式：两连杆（UR5e 上臂、前臂，与 20.2 节相同）
def jac(t1, t2, l1=0.425, l2=0.392):
    return np.array([[-l1 * math.sin(t1) - l2 * math.sin(t1 + t2), -l2 * math.sin(t1 + t2)],
                     [l1 * math.cos(t1) + l2 * math.cos(t1 + t2), l2 * math.cos(t1 + t2)]])


for name, t2 in (("a", 60.0), ("b", 5.0)):
    J = jac(math.radians(30), math.radians(t2))
    Jd = jac(math.radians(30.2), math.radians(t2 + 0.2))           # 两个编码器的零点各差 0.2°
    s, sd = np.linalg.svd(J, compute_uv=False), np.linalg.svd(Jd, compute_uv=False)
    dJ = np.linalg.norm(Jd - J, 2)
    assert np.all(np.abs(sd - s) <= dJ + 1e-15)
    out(**{f"s_{name}": vec(s, 4), f"ds_{name}": ", ".join(sci(float(abs(x)), 1) for x in sd - s), f"dJ_{name}": sci(float(dJ), 1),
           f"rel2_{name}": float(abs(sd[1] - s[1]) / s[1]), f"relb_{name}": float(dJ / s[1])})

# (3) 鲍尔–费克：A = −C⁻¹G 不对称，A = V Λ V⁻¹，V = C^{−1/2} Q
mu, Q = np.linalg.eigh(S)
V = Ch @ Q
assert np.allclose(np.linalg.inv(V) @ A @ V, np.diag(mu))
kV = np.linalg.cond(V, 2)
# 只扰动外壳 h₂ 那一行（例如外壳热容估错）
E = np.zeros((6, 6))
E[3] = 0.05 * A[3]
lamE = np.linalg.eigvals(A + E)
shifts = [np.min(np.abs(lamE - m)) for m in mu]
out(kV=float(kV), sqrt10=math.sqrt(10), nE3=sci(float(np.linalg.norm(E, 2)), 2), bf=sci(float(kV * np.linalg.norm(E, 2)), 2),
    maxshift3=sci(float(max(np.min(np.abs(mu - z)) for z in lamE)), 2))

# (4) 单个特征值的条件数：根为 1, 2, …, 6 的多项式的友矩阵
n = 6
p = np.poly(np.arange(1, n + 1))
Cm = np.zeros((n, n))
Cm[0, :] = -p[1:]
Cm[1:, :-1] = np.eye(n - 1)
w, X = np.linalg.eig(Cm)
Y = np.linalg.inv(X).conj().T            # 左特征向量（列）
order = np.argsort(w.real)
kap = []
for i in order:
    x = X[:, i] / np.linalg.norm(X[:, i])
    y = Y[:, i] / np.linalg.norm(Y[:, i])
    kap.append(1 / abs(np.vdot(y, x)))
eps = 1e-10
sh = np.zeros(n)
for trial in range(200):
    E = rng.standard_normal((n, n))
    E *= eps / np.linalg.norm(E, 2)
    w2 = np.linalg.eigvals(Cm + E)
    for j, i in enumerate(order):
        sh[j] = max(sh[j], np.min(np.abs(w2 - w[i])))
out(kap=", ".join(sci(k, 1) for k in kap), sh=", ".join(sci(x, 1) for x in sh), kapmax=sci(max(kap), 1), shmax=sci(float(max(sh)), 1),
    kVc=sci(float(np.linalg.cond(X)), 1))
assert all(sh[j] <= kap[j] * eps * 1.05 for j in range(n))

# (5) 8 个时间常数 τ = 1 s 的一阶环节串联：A = −I + N（N 为下移位矩阵），特征值 −1 是 8 重的，只有一个若尔当块
m = 8
Ach = -np.eye(m) + np.diag(np.ones(m - 1), -1)
for e_ in (1e-8, 1e-4):
    P = Ach.copy()
    P[0, m - 1] += e_                                   # 最后一级的输出有一点漏回第一级
    z = np.linalg.eigvals(P)
    out(**{f"rad{int(-math.log10(e_))}": float(np.max(np.abs(z + 1))), f"pred{int(-math.log10(e_))}": e_ ** (1 / m)})
