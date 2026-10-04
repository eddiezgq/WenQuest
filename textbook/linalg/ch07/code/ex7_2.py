"""7.2 节：向量空间的例子——多项式（次数不超过 3）、函数（y'' + y = 0 的解）、2×2 矩阵、离散信号（采样序列）。
在每个例子中做加法与数乘。"""
import numpy as np
from numpy.polynomial import Polynomial as Pn

from _num import sci
from bookout import out, tex, vec

p, q = Pn([1, -2, 0, 3]), Pn([0, 1, 4, -1])       # 1 − 2t + 3t³，t + 4t² − t³
r = 2 * p - q
out(r=vec(r.coef, 0))
# y'' + y = 0：sin 与 cos 是解，它们的任意组合也是解（数值验证 y'' + y ≈ 0）
t = np.linspace(0, 2 * np.pi, 2001)
h = t[1] - t[0]
y = 3 * np.cos(t) - 2 * np.sin(t)
ypp = (y[2:] - 2 * y[1:-1] + y[:-2]) / h ** 2
out(ode_res=sci(float(np.abs(ypp + y[1:-1]).max()), 0))
# 2×2 矩阵空间
M1, M2 = np.array([[1.0, 2], [0, -1]]), np.array([[0.0, 1], [3, 1]])
out(M1=tex(M1, 0), M2=tex(M2, 0), M=tex(M1 + 2 * M2, 0))
# 离散信号：两路 8 点采样相加
x = np.array([0, 1, 2, 3, 2, 1, 0, -1.0])
n = np.array([0.1, -0.1, 0.2, 0.0, -0.2, 0.1, 0.0, 0.1])
out(sig=vec(x + n, 1), sig_scaled=vec(0.5 * x, 1))
