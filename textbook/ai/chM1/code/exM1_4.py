"""算例 M1.4.1—M1.4.3：正交、投影与最小二乘（M1.4 节）。

车间的问题：粗糙度要用轮廓仪单独测，慢；外径与内径在三坐标上顺手就量了。能不能用快的几项估出慢的那一项？
这就是最小二乘：在"几项测量的所有线性组合"构成的平面（列空间）里，找离真值最近的那一点。
本程序验证三件事：正规方程给出的解确实使残差最小；残差与列空间正交；投影矩阵是幂等的。
"""
import numpy as np

from _chM1 import parts, standardize
from bookout import out

v = {}
X0 = parts()
Z, mu, sd = standardize(X0)
A = np.c_[np.ones(len(Z)), Z[:, 0], Z[:, 1]]                   # 常数项、外径、内径（都已标准化）
y = Z[:, 4]                                                    # 要估的：粗糙度
n, p = A.shape
v["n"], v["p"] = n, p

# ---------- （1）正规方程
beta = np.linalg.solve(A.T @ A, A.T @ y)
r = y - A @ beta
v["b0"], v["b_od"], v["b_id"] = [float(x) for x in beta]
v["rss"] = float(r @ r)
v["rmse"] = float(np.sqrt(v["rss"] / n))                       # 标准化尺度下的均方根误差
v["rmse_um"] = v["rmse"] * float(sd[4])                        # 换回微米
v["sd_ra_um"] = float(sd[4])
v["R2"] = float(1 - v["rss"] / ((y - y.mean()) @ (y - y.mean())))
# 随便挪一点都更差：最小二乘确实是最小
g = np.random.default_rng(4)
worse = 0
for _ in range(200):
    b2 = beta + g.normal(0, 0.05, p)
    worse += float((y - A @ b2) @ (y - A @ b2)) > v["rss"]
assert worse == 200, "任意扰动都应使残差平方和变大"
v["n_try"] = 200

# ---------- （2）残差与列空间正交
v["orth"] = float(np.abs(A.T @ r).max())                       # 应当是 0（到浮点精度）
assert v["orth"] < 1e-10
v["cos_r_od"] = float(abs(r @ A[:, 1]) / (np.linalg.norm(r) * np.linalg.norm(A[:, 1])))

# ---------- （3）投影矩阵
P = A @ np.linalg.solve(A.T @ A, A.T)
v["idem"] = float(np.abs(P @ P - P).max())                     # 幂等：投影两次等于投影一次
v["sym"] = float(np.abs(P - P.T).max())
v["trace_P"] = float(np.trace(P))                              # 迹等于列空间的维数
assert abs(v["trace_P"] - p) < 1e-8 and v["idem"] < 1e-10
# 勾股定理：|y|² = |投影|² + |残差|²
v["lhs"] = float(y @ y)
v["rhs"] = float((P @ y) @ (P @ y) + r @ r)
assert abs(v["lhs"] - v["rhs"]) < 1e-8
out(**v)
