"""3.2 节：高斯消元法——消元的每一步、乘数、上三角方程组与回代；主元为零时交换行。"""
import numpy as np

from bookout import out
from _elim import forward, fstr, tex_aug

M = [[2, 1, 1, 3], [4, 3, 3, 7], [8, 7, 9, 19]]
U, steps, mult = forward(M)
out(M0=tex_aug(M), s1=tex_aug(steps[0][1]), s2=tex_aug(steps[1][1]), s3=tex_aug(steps[2][1]),
    l21=fstr(mult[(2, 1)]), l31=fstr(mult[(3, 1)]), l32=fstr(mult[(3, 2)]), nsteps=len(steps))
# 回代：2z = 4，y + z = 1，2x + y + z = 3
z = U[2][3] / U[2][2]
y = (U[1][3] - U[1][2] * z) / U[1][1]
x = (U[0][3] - U[0][1] * y - U[0][2] * z) / U[0][0]
out(x=fstr(x), y=fstr(y), z=fstr(z), piv=", ".join(fstr(U[i][i]) for i in range(3)))
xs = np.linalg.solve(np.array([r[:3] for r in M], float), np.array([r[3] for r in M], float))
out(np_x=str(np.round(xs, 12).tolist()))
# 主元为零：0x + y = 2，x + y = 3 —— 先交换两行
U2, steps2, _ = forward([[0, 1, 2], [1, 1, 3]])
out(swap0=steps2[0][0], swapM=tex_aug(steps2[0][1]))
# 无法补救的零主元：x + y + z = 1，2x + 2y + 5z = 4，4x + 4y + 8z = 2 —— 第 2 列下方全为零
U3, steps3, _ = forward([[1, 1, 1, 1], [2, 2, 5, 4], [4, 4, 8, 2]])
out(brk=tex_aug(U3))
