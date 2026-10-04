"""7.7 节：坐标——向量在一组基下的坐标（解方程组）；同一个多项式在基 {1, t, t²} 与 {1, t − 1, (t − 1)²} 下的坐标；
机器人：车间中一点在转过 30° 的相机坐标系中的坐标（两坐标系原点重合）。"""
import math

import numpy as np

from bookout import out, tex, vec

b1, b2 = np.array([2.0, 1]), np.array([1.0, 3])
B = np.column_stack([b1, b2])
x = np.array([7.0, 11])
c = np.linalg.solve(B, x)
out(B=tex(B, 0), x=vec(x, 0), c=vec(c, 0))
# 多项式 p(t) = 3 + 2t + t²：在 {1, t − 1, (t − 1)²} 下，p = 6 + 4(t − 1) + (t − 1)²
p = np.poly1d([1, 2, 3])
out(p1=float(p(1)), dp1=float(p.deriv()(1)), d2=float(p.deriv(2)(1) / 2))
# 相机坐标系：两个坐标轴为转 30° 后的 e₁、e₂（单位正交），坐标 = Rᵀ x
t = math.radians(30)
R = np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])
pw = np.array([0.30, 0.20])
out(R=tex(R, 4), ctool=vec(np.linalg.solve(R, pw), 4), ctool2=vec(R.T @ pw, 4))
