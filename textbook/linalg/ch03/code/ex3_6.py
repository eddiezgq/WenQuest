"""3.6 节：齐次方程组——总有零解；未知数多于方程时一定有非零解；非齐次方程组的解 = 一个特解 + 齐次方程组的解。"""
import numpy as np

from bookout import out
from _elim import fstr, rref, tex_aug

# 齐次：3 个方程 4 个未知数（3.4 节的系数矩阵）
H = [[1, 2, 2, 2, 0], [2, 4, 6, 8, 0], [3, 6, 8, 10, 0]]
R, piv = rref(H, 4)
out(RH=tex_aug(R), npiv=len(piv))
# 3.4 节的特解加上齐次解，仍是非齐次方程组的解
A = np.array([r[:4] for r in H], float)
b = np.array([1.0, 5.0, 6.0])
xp = np.array([-2.0, 0.0, 1.5, 0.0])
s1, s2 = np.array([-2.0, 1, 0, 0]), np.array([2.0, 0, -2, 1])
out(h1=bool(np.allclose(A @ s1, 0)), h2=bool(np.allclose(A @ s2, 0)), comb=bool(np.allclose(A @ (xp + 7 * s1 - 3 * s2), b)))
# 两个解之差是齐次方程组的解
x1, x2 = xp + s1, xp - 2 * s2
out(diff=bool(np.allclose(A @ (x1 - x2), 0)))
# 方阵：只有零解 ⇔ 主元个数等于 n
S = [[1, 1, 1, 0], [1, 2, 3, 0], [2, 3, 5, 0]]
Rs, ps = rref(S, 3)
out(RS=tex_aug(Rs), nps=len(ps))
