"""3.3 节：增广矩阵与初等行变换——三种变换各做一次，并验证它们都可以撤销、不改变解。"""
import numpy as np

from bookout import out
from _elim import F, fstr, rref, tex_aug

M = F([[1, 2, -1, 2], [2, 5, 1, 9], [-1, 1, 4, 7]])
out(M=tex_aug(M))
# 1) 第 2 行减去第 1 行的 2 倍；2) 第 3 行加上第 1 行；3) 第 3 行减去第 2 行的 3 倍
A1 = [r[:] for r in M]
A1[1] = [a - 2 * b for a, b in zip(A1[1], A1[0])]
A2 = [r[:] for r in A1]
A2[2] = [a + b for a, b in zip(A2[2], A2[0])]
A3 = [r[:] for r in A2]
A3[2] = [a - 3 * b for a, b in zip(A3[2], A3[1])]
out(A1=tex_aug(A1), A2=tex_aug(A2), A3=tex_aug(A3))
z = A3[2][3] / A3[2][2]
y = (A3[1][3] - A3[1][2] * z) / A3[1][1]
x = (A3[0][3] - A3[0][1] * y - A3[0][2] * z) / A3[0][0]
out(x=fstr(x), y=fstr(y), z=fstr(z))
R, piv = rref(M, 3)
out(R=tex_aug(R))
# 原方程组的解同样满足变换后的方程组
Mf = np.array([[float(v) for v in r] for r in M])
sol = np.array([float(x), float(y), float(z)])
out(check=bool(np.allclose(Mf[:, :3] @ sol, Mf[:, 3])))
