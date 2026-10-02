"""18.4 节：低秩逼近。算例 18.4.1（接算例 18.2.1）；用随机的秩 1 矩阵检验埃卡特–杨定理；范数与奇异值的关系。"""
import numpy as np

from _arm import svd_fixed
from bookout import out, tex

A = np.array([[3.0, 2.0, 2.0], [2.0, 3.0, -2.0]])
U, s, V = svd_fixed(A)
A1 = s[0] * np.outer(U[:, 0], V[:, 0])
E = A - A1
out(A1=tex(A1, 2), E=tex(E, 4), E2=np.linalg.norm(E, 2), EF=np.linalg.norm(E, "fro"), AF=np.linalg.norm(A, "fro"),
    AF_sq=round(np.linalg.norm(A, "fro") ** 2), A2=np.linalg.norm(A, 2))

# 随机试 10 万个秩 1 矩阵 B = x yᵀ，看 ‖A − B‖₂ 能否小于 σ2 = 3
rng = np.random.default_rng(184)
best = np.inf
for _ in range(100000):
    x = rng.standard_normal(2)
    y = rng.standard_normal(3)
    y = y * (x @ A @ y) / (x @ x) / (y @ y)          # 给定方向 x、y，取最好的倍数（使 A − B 在这对方向上的分量最小）
    best = min(best, np.linalg.norm(A - np.outer(x, y), 2))
out(trials=100000, best=best)
