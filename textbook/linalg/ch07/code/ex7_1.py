"""7.1 节：数域与向量空间的公理——有理数、实数、复数是数域，整数不是；二元域 GF(2) 的加法与乘法（奇偶校验）；
不满足公理的集合：第一象限、x₁ = 1 的向量。"""
from fractions import Fraction

import numpy as np

from bookout import out, vec

# 整数：2 没有乘法逆元（1/2 不是整数）；有理数：Fraction(1, 2)
out(q_inv=str(Fraction(2) ** -1))
# GF(2)：1 + 1 = 0
add = [[(a + b) % 2 for b in (0, 1)] for a in (0, 1)]
out(gf2_add=str(add))
u, w = np.array([1, 0, 1, 1]), np.array([1, 1, 0, 1])
out(gf2_sum=vec((u + w) % 2, 0), gf2_self=vec((u + u) % 2, 0))
# 奇偶校验：数据位 (1, 0, 1, 1)，校验位为各位之和（模 2）
d = np.array([1, 0, 1, 1])
out(parity=int(d.sum() % 2))
# 复向量空间：i·(1, i) = (i, −1)
z = np.array([1, 1j])
cz = 1j * z
def cstr(c):
    return {1j: r"\mathrm i", -1j: r"-\mathrm i"}.get(complex(c), f"{c.real:g}")


out(cz=r"(" + r",\ ".join(cstr(c) for c in cz) + ")")
# 第一象限对数乘不封闭
p = np.array([1.0, 2.0])
out(neg=vec(-1 * p, 0))
# x₁ = 1 的向量对加法不封闭
a, b = np.array([1.0, 2, 3]), np.array([1.0, -1, 0])
out(sum1=vec(a + b, 0))
