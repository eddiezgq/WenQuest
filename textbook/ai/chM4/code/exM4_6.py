"""算例 M4.6.1—M4.6.3：条件数、病态与归一化（M4.6 节）。

M1.7 节给出了条件数的定义，M2.5 节说它决定训练要走多少步。这一节从数值的角度再看一遍：
（1）"相近的两个数相减"会把相对误差放大多少（灾难性抵消）——方差的两种算法是最好的例子；
（2）同一个最小二乘问题，归一化前后在单精度下的误差差多少；
（3）归一化为什么同时改善了三件事：距离、条件数、数值精度。
"""
import numpy as np

from bookout import out

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conventions"))
from parts import parts, standardize  # noqa: E402  数学篇共用的零件数据

v = {}
# ---------- （1）灾难性抵消：方差的两种算法
x = (np.arange(1, 1001, dtype=np.float64) * 1e-3 + 1e6)      # 一组差别很小、但本身很大的数
exact = float(np.var(x.astype(np.float128) if hasattr(np, "float128") else x, ddof=0))
x32 = x.astype(np.float32)
# 教科书公式 E[x²] − (E[x])²：两个很大的数相减，有效数字几乎全被抵消掉
bad = float(np.mean(x32.astype(np.float32) ** 2, dtype=np.float32) - np.mean(x32, dtype=np.float32) ** 2)
# 两遍算法：先算均值，再算偏差的平方和
mu = np.mean(x32, dtype=np.float32)
good = float(np.mean((x32 - mu) ** 2, dtype=np.float32))
v["exact_var"] = exact
v["bad_var"], v["good_var"] = bad, good
v["bad_rel"] = abs(bad - exact) / exact * 100
v["good_rel"] = abs(good - exact) / exact * 100
v["bad_negative"] = bad < 0
assert v["bad_rel"] > 10 * v["good_rel"], "教科书公式在单精度下错得多得多"
v["mag"] = float(x.mean())
v["spread"] = float(x.max() - x.min())

# ---------- （2）归一化前后：同一个最小二乘问题在单精度下的误差
X = parts()
Z, mu_, sd_ = standardize(X)
Xt = np.c_[np.ones(len(X)), X[:, 0], X[:, 1], X[:, 2]]
Xz = np.c_[np.ones(len(Z)), Z[:, 0], Z[:, 1], Z[:, 2]]
y = X[:, 4]
v["kappa_raw"] = float(np.linalg.cond(Xt))
v["kappa_std"] = float(np.linalg.cond(Xz))
for tag, A in (("raw", Xt), ("std", Xz)):
    w64 = np.linalg.lstsq(A, y, rcond=None)[0]
    w32 = np.linalg.lstsq(A.astype(np.float32), y.astype(np.float32), rcond=None)[0].astype(np.float64)
    v[f"err32_{tag}"] = float(np.linalg.norm(w32 - w64) / np.linalg.norm(w64) * 100)
v["err_ratio"] = v["err32_raw"] / max(v["err32_std"], 1e-18)
assert v["err32_raw"] > v["err32_std"], "不归一化时单精度的误差更大"

# ---------- （3）归一化同时改善了三件事（把三个数并排放一起）
v["dist_share_raw"] = float((((X - X[0]) ** 2).sum(0) / ((X - X[0]) ** 2).sum()).max() * 100)   # 距离被一项主导（M1.3 节）
v["dist_share_std"] = float((((Z - Z[0]) ** 2).sum(0) / ((Z - Z[0]) ** 2).sum()).max() * 100)
H_raw = 2 * Xt.T @ Xt / len(X)
H_std = 2 * Xz.T @ Xz / len(Z)
v["steps_raw"] = float(np.linalg.cond(H_raw) / 2)            # 步数 ≈ ½κ·ln(1/ε)，这里只比相对倍数（M2.5 节）
v["steps_std"] = float(np.linalg.cond(H_std) / 2)
v["steps_ratio"] = v["steps_raw"] / v["steps_std"]
out(**v)
