"""9.2 节：核与像；秩–零化度定理。求导 D: P_3 → P_3 的核是常数（1 维），像是 P_2（3 维），1 + 3 = 4。
取值映射 E(p) = (p(0), p(1), p(2), p(3)) 的核只有零多项式，所以它是满射：过任意 4 个点有唯一的三次插值多项式。
迹 tr: M_2 → ℝ 的核是迹为零的矩阵（3 维）。"""
import numpy as np
import scipy.linalg as sla

from _poly import D, matrix, ptex
from bookout import out, tex

MD = matrix(D, 4)
rk = int(np.linalg.matrix_rank(MD))
out(MD=tex(MD, 0), rD=rk, kD=4 - rk, kerD=tex(sla.null_space(MD)[:, 0] / sla.null_space(MD)[0, 0], 0))
# 取值映射：在节点 0, 1, 2, 3 上取值，矩阵是范德蒙德矩阵
xs = np.array([0.0, 1, 2, 3])
E = np.vander(xs, 4, increasing=True)
out(E=tex(E, 0), rE=int(np.linalg.matrix_rank(E)), detE=float(np.linalg.det(E)))
# 机械臂关节在 t = 0, 1, 2, 3 s 时的示教角度（°），求过这 4 点的三次多项式
y = np.array([0.0, 20.0, 50.0, 60.0])
c = np.linalg.solve(E, y)
out(y=tex(y, 0), interp=ptex(c, "t"), check=float(np.abs(E @ c - y).max()))
# 迹映射 M_2 → ℝ：把 2×2 矩阵看作 ℝ⁴ 中的向量 (a, b, c, d)
Tr = np.array([[1.0, 0, 0, 1]])
out(rTr=int(np.linalg.matrix_rank(Tr)), kTr=sla.null_space(Tr).shape[1])
