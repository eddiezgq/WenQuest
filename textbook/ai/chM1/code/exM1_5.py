"""算例 M1.5.1—M1.5.3：协方差矩阵的特征值、主成分与幂迭代（M1.5 节）。

对称矩阵的特征分解在人工智能里最常见的落点是协方差矩阵：它的特征向量指出数据散布得最开的方向，
特征值就是那个方向上的方差。本程序在标准化后的零件数据上算出这些方向，看前两个方向解释了多少波动，
再用最朴素的幂迭代把最大的那个方向迭出来——用来说明"反复乘同一个矩阵"会发生什么（这也是后面
深度网络里梯度爆炸与消失的同一件事，M2.5 节）。
"""
import numpy as np

from _chM1 import FEATURES, parts, standardize
from bookout import out

v = {}
Z, mu, sd = standardize(parts())
n, d = Z.shape
C = Z.T @ Z / (n - 1)                                          # 协方差矩阵（标准化后即相关系数矩阵）
v["n"], v["d"] = n, d
v["c_od_ra"] = float(C[0, 4])                                  # 外径与粗糙度的相关系数
v["c_len_ra"] = float(C[2, 4])
v["sym_err"] = float(np.abs(C - C.T).max())

lam, Q = np.linalg.eigh(C)                                     # 对称矩阵：特征值全为实数，特征向量正交
lam, Q = lam[::-1], Q[:, ::-1]
v["lam"] = [round(float(x), 3) for x in lam]
v["lam1"], v["lam2"] = float(lam[0]), float(lam[1])
v["pc1_pct"] = float(lam[0] / lam.sum() * 100)
v["pc12_pct"] = float(lam[:2].sum() / lam.sum() * 100)
v["trace_C"] = float(np.trace(C))                              # 迹 = 特征值之和 = 总方差（标准化后等于 d）
assert abs(v["trace_C"] - lam.sum()) < 1e-10 and abs(v["trace_C"] - d) < 1e-10
v["det_C"] = float(np.linalg.det(C))                           # 行列式 = 特征值之积
assert abs(v["det_C"] - float(np.prod(lam))) < 1e-10
v["orth_err"] = float(np.abs(Q.T @ Q - np.eye(d)).max())       # 特征向量正交

# 第一主成分的载荷：哪几项一起动
w1 = Q[:, 0] * np.sign(Q[0, 0])
for name, a in zip(("od", "id", "len", "round", "ra"), w1):
    v[f"pc1_{name}"] = float(a)
v["pc1_top"] = FEATURES[int(np.abs(w1).argmax())]
v["pc1_min"] = FEATURES[int(np.abs(w1).argmin())]

# ---------- 幂迭代：反复乘同一个矩阵，方向收敛到最大特征值那一个
x = np.ones(d) / np.sqrt(d)
hist = []
for k in range(1, 31):
    x = C @ x
    x /= np.linalg.norm(x)
    hist.append(float(1 - abs(x @ w1)))                         # 与真方向的差距
v["iter_5"], v["iter_10"], v["iter_30"] = hist[4], hist[9], hist[29]
v["k_1e6"] = next(k for k, e in enumerate(hist, 1) if e < 1e-6)
v["gap"] = float(lam[1] / lam[0])                               # 收敛快慢由前两个特征值之比决定
assert hist[-1] < 1e-9
out(**v)
