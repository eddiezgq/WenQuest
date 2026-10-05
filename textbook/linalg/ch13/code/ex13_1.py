"""13.1 节：变换下不改变方向的向量。
A = [[3, 1], [0, 2]]：一般的向量被转离原来的直线，(1, 0) 与 (−1, 1) 只被拉长，Av = 3v、Av = 2v。
机器人一：柔顺腕的刚度矩阵 K = [[4, 1], [1, 4]] kN/m。沿 x 推工具尖端，位移并不沿 x；只有沿 (1, 1)、(1, −1) 推时位移与力同向。
机器人二：旋转矩阵 R 把转轴上的向量留在原处，Rv = v：转轴是特征值 1 的特征向量。
1.3 节的网页排名：G x = x，得分向量是 G 的特征值 1 的特征向量。"""
import numpy as np

from _frac import fvec
from bookout import out, vec

A = np.array([[3.0, 1], [0, 2]])
for name, v in (("a", [1.0, 1]), ("b", [0.0, 1]), ("e1", [1.0, 0]), ("e2", [-1.0, 1])):
    v = np.array(v); w = A @ v
    ang = np.degrees(np.arctan2(v[0] * w[1] - v[1] * w[0], v @ w))
    out(**{f"v_{name}": vec(v, 0), f"Av_{name}": vec(w, 0), f"ang_{name}": float(abs(ang))})
# 刚度矩阵（kN/m）：F = K d
K = np.array([[4.0, 1], [1, 4]])
F = np.array([10.0, 0])                         # 沿 x 推 10 N
d = np.linalg.solve(K, F)                        # mm（N / (kN/m) = mm）
out(K=r"\begin{pmatrix}4 & 1\\ 1 & 4\end{pmatrix}", F=vec(F, 0), d=fvec(d), d_ang=float(np.degrees(np.arctan2(d[1], d[0]))), d_angabs=float(abs(np.degrees(np.arctan2(d[1], d[0])))))
for name, u in (("p", [1.0, 1]), ("m", [1.0, -1])):
    u = np.array(u) / np.sqrt(2); dd = np.linalg.solve(K, 10 * u)
    out(**{f"d_{name}": vec(dd, 3), f"k_{name}": float(10 / np.linalg.norm(dd))})
# 旋转矩阵：先绕 x 转 90°，再绕 z 转 90°
Rx = np.array([[1.0, 0, 0], [0, 0, -1], [0, 1, 0]])
Rz = np.array([[0.0, -1, 0], [1, 0, 0], [0, 0, 1]])
R = Rz @ Rx
axis = np.array([1.0, 1, 1])
out(R=r"\begin{pmatrix}0 & 0 & 1\\ 1 & 0 & 0\\ 0 & 1 & 0\end{pmatrix}", R_ok=float(np.abs(R - np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])).max()),
    Raxis=vec(R @ axis, 0))
# 网页排名矩阵的特征值 1
links = {1: [2, 3], 2: [3], 3: [1], 4: [1, 3]}
M = np.zeros((4, 4))
for j, outs in links.items():
    for i in outs:
        M[i - 1, j - 1] = 1 / len(outs)
G = 0.85 * M + 0.15 / 4 * np.ones((4, 4))
w, V = np.linalg.eig(G)
k = int(np.argmin(np.abs(w - 1)))
x = np.real(V[:, k]); x = x / x.sum()
out(G_lam1=float(np.real(w[k])), rank=", ".join(f"{t:.4f}" for t in x), G_others=float(np.sort(np.abs(w))[-2]))
