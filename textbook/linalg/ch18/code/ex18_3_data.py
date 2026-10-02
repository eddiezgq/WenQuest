"""图 18.3.2 用的数：与 ex18_3.py 相同的检测数据（同一个随机数种子）。由 fig18_3.py 导入，本身也作为程序运行。"""
import math

import numpy as np

from bookout import out

rng = np.random.default_rng(1810)
n = 50
a = 42.0 + 0.05 * rng.standard_normal(n)
b = 31.5 + 0.04 * rng.standard_normal(n)
X = np.c_[a, b, a + b]
Xc = X - X.mean(axis=0)
s_exact = np.linalg.svd(Xc, compute_uv=False)
s_exact = np.maximum(s_exact, 1e-16)
s_meas = np.linalg.svd(Xc + 0.002 * rng.standard_normal(Xc.shape), compute_uv=False)
tol = 0.002 * (math.sqrt(n) + math.sqrt(3))
if __name__ == "__main__":
    out(check=float(s_meas[2]))
