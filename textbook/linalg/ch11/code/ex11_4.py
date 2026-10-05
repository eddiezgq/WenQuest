"""11.4 节：豪斯霍尔德反射与吉文斯旋转。把 x = (2, 1, 2) 反射成 (−3, 0, 0)；4×3 矩阵的豪斯霍尔德 QR，每一步对角线以下变为零；
吉文斯旋转把 (3, 4) 变成 (5, 0)；用吉文斯旋转逐行更新最小二乘（新的测量一到，只做 n 次旋转），结果与一次性求解相同。"""
import numpy as np

from _frac import fmat, fvec
from _hh import givens, house, householder_qr
from _num import sci
from bookout import out, tex, vec

x = np.array([2.0, 1, 2])
v = house(x)
H = np.eye(3) - 2 * np.outer(v, v) / (v @ v)
out(x=vec(x, 0), v=vec(v, 0), H=fmat(H), Hx=vec(H @ x, 0), HH=float(np.abs(H @ H - np.eye(3)).max()))
A = np.array([[1.0, 2, 0], [1, 0, 1], [1, 1, 3], [1, 3, 1]])
Q, R, hist = householder_qr(A)
out(A=tex(A, 0), S1=tex(hist[1], 4), S2=tex(hist[2], 4), R=tex(R, 4), QR=float(np.abs(Q @ R - A).max()), QtQ=sci(float(np.abs(Q.T @ Q - np.eye(4)).max()) + 1e-18, 0))
c, s = givens(3.0, 4.0)
G = np.array([[c, s], [-s, c]])
out(c=c, s=s, G=tex(G, 1), Gx=vec(G @ np.array([3.0, 4]), 0))
# 运算量（浮点运算次数的主项）：m = 1000，n = 10
m_, n_ = 1000, 10
out(fl_hh=2 * m_ * n_ ** 2 - 2 * n_ ** 3 / 3, fl_mgs=2 * m_ * n_ ** 2)
# 逐行更新的最小二乘：拟合直线 y = c0 + c1 t，数据一行一行到来
rng = np.random.default_rng(114)
t = np.linspace(0, 10, 200)
y = 1.5 + 0.8 * t + rng.normal(scale=0.2, size=t.size)
Rk = np.zeros((2, 2))
z = np.zeros(2)                                 # Qᵀb 的前两项
rho = 0.0                                       # 已累计的残差平方和
for ti, yi in zip(t, y):
    row, rhs = np.array([1.0, ti]), yi
    for j in range(2):                          # 用吉文斯旋转把新行的第 j 个元素消去
        cc, ss = givens(Rk[j, j], row[j])
        Rj, rj = Rk[j, :].copy(), z[j]
        Rk[j, :] = cc * Rj + ss * row
        row = -ss * Rj + cc * row
        z[j] = cc * rj + ss * rhs
        rhs = -ss * rj + cc * rhs
    rho += rhs ** 2
xin = np.linalg.solve(Rk, z)
Ab = np.column_stack([np.ones_like(t), t])
xb = np.linalg.lstsq(Ab, y, rcond=None)[0]
rb = y - Ab @ xb
out(xin=vec(xin, 4), xb=vec(xb, 4), dx=sci(float(np.abs(xin - xb).max()) + 1e-18, 0), rho=float(rho), rss=float(rb @ rb))
