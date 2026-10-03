"""1.2.2 节手算核对：由 v、ω 求两轮角速度。"""
from fractions import Fraction as F

from bookout import out

r, b = F(75, 1000), F(40, 100)
v, w = F(1, 2), F(1, 2)
s = 2 * v / r            # ω_L + ω_R
d = w * b / r            # ω_R − ω_L
out(s=str(s), d=str(d), wR=str((s + d) / 2), wL=str((s - d) / 2))
