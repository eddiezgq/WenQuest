"""9.5 节：同构——取定一组基，坐标映射把 n 维空间同构地变成 ℝⁿ。P_2 在基 1, x − 1, (x − 1)² 下的坐标就是在 x = 1 处的泰勒系数；
判断多项式组是否线性无关，只需看坐标组成的矩阵；y'' + ω²y = 0 的解空间是二维的，(y(0), y'(0)) 给出它到 ℝ² 的同构。"""
import numpy as np

from _poly import D, ev, ptex
from _num import sci
from bookout import out, tex, vec

p = np.array([2.0, -1, 3])                         # 2 − x + 3x²
c = np.array([ev(p, 1), ev(D(p), 1), ev(D(D(p)), 1) / 2])
# 由坐标还原：c0 + c1 (x − 1) + c2 (x − 1)²
back = c[0] * np.array([1.0, 0, 0]) + c[1] * np.array([-1.0, 1, 0]) + c[2] * np.array([1.0, -2, 1])
out(p=ptex(p), cB=vec(c, 0), back=ptex(back))
# 1 + x, x + x², 1 + x² 是否线性无关：坐标作列
Q = np.column_stack([[1, 1, 0], [0, 1, 1], [1, 0, 1]]).astype(float)
out(Q=tex(Q, 0), detQ=float(np.linalg.det(Q)))
Q2 = np.column_stack([[1, 1, 0], [0, 1, 1], [1, 2, 1]]).astype(float)   # 第三个 = 前两个之和
out(rQ2=int(np.linalg.matrix_rank(Q2)))
# 振动：连杆末端的小振动 y'' + ω² y = 0，ω = 2π·5 rad/s；初始偏移 2 mm、初速度 0.1 m/s
w = 2 * np.pi * 5
y0, v0 = 0.002, 0.1
a, b = y0, v0 / w                                   # y = a cos ωt + b sin ωt
t = np.linspace(0, 0.4, 2001)
y = a * np.cos(w * t) + b * np.sin(w * t)
dt = t[1] - t[0]
ydd = np.gradient(np.gradient(y, dt), dt)
out(w=w, a=a * 1000, b=b * 1000, amp=float(np.hypot(a, b)) * 1000,
    ode_res=sci(float(np.abs(ydd[5:-5] + w ** 2 * y[5:-5]).max() / (w ** 2 * np.abs(y).max())), 1))
