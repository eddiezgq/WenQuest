"""1.4 节：《九章算术》卷八“方程”第一题，按刘徽注的“遍乘直除”逐步计算（分数精确运算），并与 NumPy 核对。
三列（从右到左）依次是三个方程；每列自上而下是上禾、中禾、下禾的秉数和“实”（斗）。"""
from fractions import Fraction as F

import numpy as np

from bookout import out

right = [F(3), F(2), F(1), F(39)]
mid = [F(2), F(3), F(1), F(34)]
left = [F(1), F(2), F(3), F(26)]
steps = []
# 以右行上禾 3 遍乘中行，再减去右行两次：中行上禾消为 0
mid = [3 * a for a in mid]
steps.append(("中行遍乘 3", mid[:]))
mid = [a - 2 * c for a, c in zip(mid, right)]
steps.append(("中行减右行 2 次", mid[:]))
left = [3 * a for a in left]
left = [a - c for a, c in zip(left, right)]
steps.append(("左行遍乘 3 后减右行 1 次", left[:]))
left = [5 * a for a in left]
left = [a - 4 * c for a, c in zip(left, mid)]
steps.append(("左行遍乘 5 后减中行 4 次", left[:]))
xia = left[3] / left[2]
zhong = (mid[3] - mid[2] * xia) / mid[1]
shang = (right[3] - right[1] * zhong - right[2] * xia) / right[0]
A = np.array([[3, 2, 1], [2, 3, 1], [1, 2, 3]], float)
b = np.array([39, 34, 26], float)
x = np.linalg.solve(A, b)
assert np.allclose(x, [float(shang), float(zhong), float(xia)])
fmt = lambda v: " ".join(str(a) for a in v)
out(**{f"s{i}": fmt(v) for i, (_, v) in enumerate(steps)}, shang=str(shang), zhong=str(zhong), xia=str(xia),
    shang_f=float(shang), zhong_f=float(zhong), xia_f=float(xia), left36=str(left[2]), left99=str(left[3]))
