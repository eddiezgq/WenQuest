"""13.7 节：代数重数与几何重数；相似矩阵的性质。
13.2 节的 B：λ = 3 的代数重数 2、几何重数 1，不能对角化；单位矩阵 I 与剪切 S：特征多项式相同，却不相似。
相似矩阵 B = M⁻¹AM（随机 M）：特征多项式、迹、行列式、秩相同；特征向量变为 M⁻¹v。
机器人：13.5 节采样 PD 控制的“临界阻尼”（K_p = 100，K_d = 20）A 有二重特征值 0.5，几何重数 1：
xₖ 中出现 k·0.5ᵏ 项，先升后降；“无差拍”（K_p = 400，K_d = 40）A² = 0，两步归零。"""
import numpy as np

from _num import sci
from bookout import out, tex, vec

B = np.array([[2.0, 0, 0], [1, 3, 0], [-1, 1, 3]])
out(geoB3=int(3 - np.linalg.matrix_rank(B - 3 * np.eye(3))))
S = np.array([[1.0, 1], [0, 1]])
out(polyS=", ".join(f"{x:.0f}" for x in np.poly(S)), polyI=", ".join(f"{x:.0f}" for x in np.poly(np.eye(2))))
# 相似不变量
rng = np.random.default_rng(137)
A = np.array([[4.0, -5], [2, -3]])
M = np.array([[1.0, 2], [1, 3]])
Bs = np.linalg.solve(M, A @ M)
out(M=tex(M, 0), Bs=tex(Bs, 0), polyBs=", ".join(f"{x:.0f}" for x in np.poly(Bs)), trBs=float(np.trace(Bs)), detBs=float(np.linalg.det(Bs)),
    vB=vec(np.linalg.solve(M, [5.0, 2]), 0), BvB=vec(Bs @ np.linalg.solve(M, [5.0, 2]), 0))
# 临界阻尼与无差拍
T = 0.05
Ab = np.array([[1, T], [-100 * T, 1 - 20 * T]])
Ac = np.array([[1, T], [-400 * T, 1 - 40 * T]])
out(Ab=r"\begin{pmatrix} 1 & 0.05 \\ -5 & 0 \end{pmatrix}", Abchk=float(np.abs(Ab - [[1, 0.05], [-5, 0]]).max()),
    rankAb=int(np.linalg.matrix_rank(Ab - 0.5 * np.eye(2))),
    Ac=r"\begin{pmatrix} 1 & 0.05 \\ -20 & -1 \end{pmatrix}", Acchk=float(np.abs(Ac - [[1, 0.05], [-20, -1]]).max()),
    Ac2=tex(Ac @ Ac, 0), rankAc=int(np.linalg.matrix_rank(Ac)))
x = np.array([1.0, 0]); xs = [x]
for _ in range(20):
    x = Ab @ x; xs.append(x)
xs = np.array(xs)
k_peak = int(np.argmax(np.abs(xs[:, 1])))
out(theta3=float(xs[3, 0]), omega_peak=float(xs[k_peak, 1]), k_peak=k_peak)
# J^k 的形式
v1 = np.array([1.0, -10])                   # (A − 0.5I)v1 = 0
v2 = np.linalg.lstsq(Ab - 0.5 * np.eye(2), v1, rcond=None)[0]   # (A − 0.5I)v2 = v1
X = np.column_stack([v1, v2]); J = np.linalg.solve(X, Ab @ X)
out(v1=vec(v1, 0), Jchk=sci(float(np.abs(J - [[0.5, 1], [0, 0.5]]).max()) + 1e-30, 0), Ab_v1=vec(Ab @ v1, 1))
