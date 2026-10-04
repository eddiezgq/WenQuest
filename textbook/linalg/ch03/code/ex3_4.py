"""3.4 节：行阶梯形与简化行阶梯形；主元、主元列与自由变量；写出全部解。"""
import numpy as np

from bookout import out
from _elim import F, forward, fstr, rref, tex_aug

# 三个方程、四个未知数
M = [[1, 2, 2, 2, 1], [2, 4, 6, 8, 5], [3, 6, 8, 10, 6]]
U, steps, _ = forward(M)
R, piv = rref(M, 4)
out(M=tex_aug(M), U=tex_aug(U), R=tex_aug(R), piv=", ".join(str(p + 1) for p in piv), free=", ".join(str(c + 1) for c in range(4) if c not in piv))
# 通解：x1 = R[0][4] − R[0][1] x2 − R[0][3] x4，x3 = R[1][4] − R[1][3] x4
out(xp=f"({fstr(R[0][4])}, 0, {fstr(R[1][4])}, 0)", s1=f"({fstr(-R[0][1])}, 1, 0, 0)", s2=f"({fstr(-R[0][3])}, 0, {fstr(-R[1][3])}, 1)")
# 检验：任取 x2 = 3, x4 = −1
x2, x4 = 3, -1
x = np.array([float(R[0][4] - R[0][1] * x2 - R[0][3] * x4), x2, float(R[1][4] - R[1][3] * x4), x4])
A = np.array(M, float)
out(xchk="(" + ", ".join(f"{v:g}" for v in x) + ")", ok=bool(np.allclose(A[:, :4] @ x, A[:, 4])))
