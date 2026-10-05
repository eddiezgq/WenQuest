"""11.1 节：标准正交基与正交矩阵。q1 = (1, 2, 2)/3、q2 = (2, 1, −2)/3、q3 = (2, −2, 1)/3 是 ℝ³ 的标准正交基：
坐标就是点积 qᵢᵀx，‖x‖² 等于坐标的平方和；Q 的逆是 Qᵀ，保持长度与夹角；向 q1、q2 张成的平面投影 P = Q₂Q₂ᵀ。
坐标系转动 30°、点不动时，点在新坐标系中的坐标是 Rᵀp（4.1 节的承诺）。"""
import numpy as np

from _frac import fmat, fvec
from bookout import out, tex, vec

Q = np.array([[1.0, 2, 2], [2, 1, -2], [2, -2, 1]]).T / 3
x = np.array([3.0, 0, 6])
c = Q.T @ x
out(Q=fmat(Q), QtQ=tex(Q.T @ Q, 0), x=vec(x, 0), c=vec(c, 0), back=vec(Q @ c, 0), nx=float(x @ x), nc=float(c @ c), detQ=float(np.linalg.det(Q)))
rng = np.random.default_rng(11)
u, v = rng.normal(size=3), rng.normal(size=3)
out(len_err=float(abs(np.linalg.norm(Q @ u) - np.linalg.norm(u))), dot_err=float(abs((Q @ u) @ (Q @ v) - u @ v)))
Q2 = Q[:, :2]
P = Q2 @ Q2.T
out(P=fmat(P), Px=fvec(P @ x), q3c=fvec(c[2] * Q[:, 2]))
# 坐标系转 30°，点不动
t = np.radians(30)
R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
p = np.array([0.2, 0.1])
out(R=tex(R, 4), p=vec(p, 1), pnew=vec(R.T @ p, 4), RtR=tex(R.T @ R, 0))
# 反射：关于平面 x + y + z = 0 的反射 H = I − 2nnᵀ，行列式 −1
n = np.ones(3) / np.sqrt(3)
H = np.eye(3) - 2 * np.outer(n, n)
out(H=fmat(H), detH=float(np.linalg.det(H)), HtH=float(np.abs(H.T @ H - np.eye(3)).max()))
