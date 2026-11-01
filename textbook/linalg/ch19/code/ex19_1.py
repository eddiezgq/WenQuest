"""19.1 节：数据矩阵、中心化与协方差矩阵。算例 19.1.1 的四件减速器（手算）；中心化矩阵 H 的性质；
200 件减速器的均值、标准差、协方差矩阵与相关矩阵；相关系数是中心化后两列的夹角余弦；线性组合的方差。"""
import numpy as np

from _qc import ITEMS, N_I, X_I
from bookout import out, tex, vec

# 算例 19.1.1：四件减速器的空载噪声 dB(A) 与振动速度 mm/s
X4 = np.array([[60.0, 1.20], [62.0, 1.50], [59.0, 1.10], [63.0, 1.60]])
m4 = X4.mean(axis=0)
Xc4 = X4 - m4
S4 = Xc4.T @ Xc4 / 3
r4 = S4[0, 1] / np.sqrt(S4[0, 0] * S4[1, 1])
out(X4=tex(X4, 2), m4=vec(m4, 2), Xc4=tex(Xc4, 2), S4_11=float(S4[0, 0]), S4_22=float(S4[1, 1]), S4_12=float(S4[0, 1]), r4=float(r4))

# 中心化矩阵 H = I − 11ᵀ/N（N = 4）：对称、幂等、秩 N − 1，HX 就是中心化
N = 4
H = np.eye(N) - np.ones((N, N)) / N
assert np.allclose(H @ H, H) and np.allclose(H, H.T)
assert np.allclose(H @ X4, Xc4)
out(H4=tex(H * 4, 0), rankH=int(np.linalg.matrix_rank(H)))

# 200 件减速器的检测数据
X = X_I
m = X.mean(axis=0)
Xc = X - m
S = Xc.T @ Xc / (N_I - 1)
assert np.allclose(S, np.cov(X.T))
s = np.sqrt(np.diag(S))
R = S / np.outer(s, s)
out(N=N_I, mean=vec(m, 2), sd=vec(s, 2), S=tex(S, 2), R=tex(R, 2),
    r_nv=float(R[2, 4]), r_tv=float(R[3, 4]), r_nt=float(R[2, 3]), r_db=float(R[0, 5]), r_dr=float(R[0, 1]),
    trS=float(np.trace(S)))
# 相关系数 = 中心化后两列（ℝ²⁰⁰ 中的向量）夹角的余弦
a, b = Xc[:, 2], Xc[:, 4]
cosab = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
assert abs(cosab - R[2, 4]) < 1e-12
out(ang_nv=float(np.degrees(np.arccos(cosab))))
# 线性组合的方差 Var(Xc u) = uᵀ S u：标准化后“噪声 + 振动”与“噪声 − 振动”
Z = Xc / s
for name, u in (("sum", np.array([0, 0, 1, 0, 1, 0]) / np.sqrt(2)), ("dif", np.array([0, 0, 1, 0, -1, 0]) / np.sqrt(2))):
    v_direct = float(np.var(Z @ u, ddof=1))
    v_form = float(u @ R @ u)
    assert abs(v_direct - v_form) < 1e-12
    out(**{f"var_{name}": v_form})
out(items="、".join(ITEMS))
