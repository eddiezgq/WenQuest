"""11.6 节：函数的正交。区间 [−π, π] 上 1、cos kx、sin kx 两两正交，傅里叶系数就是投影系数；方波的部分和与吉布斯现象。
机器人：编码器的偏心误差随转角周期变化，在 360 个等距角度上测得误差，用离散傅里叶基（离散意义下也两两正交）拟合，正规方程是对角的，
补偿后误差大幅减小。勒让德多项式：对 1, x, x², x³ 在 [−1, 1] 上做格拉姆–施密特；以它们为基拟合时 AᵀA 的条件数远小于单项式基。"""
import numpy as np
from numpy.polynomial import legendre as Lg

from _num import sci
from bookout import out, vec

x = np.linspace(-np.pi, np.pi, 200001)
ip = lambda f, g: float(np.trapezoid(f * g, x))
out(cs=ip(np.cos(2 * x), np.sin(3 * x)), cc=ip(np.cos(2 * x), np.cos(5 * x)), c2=ip(np.cos(2 * x), np.cos(2 * x)), one=ip(np.ones_like(x), np.ones_like(x)))
# 方波 sign(x) 的傅里叶系数：b_k = 4/(kπ)（k 为奇数）
sq = np.sign(x)
bk = [ip(sq, np.sin(k * x)) / np.pi for k in range(1, 8)]
out(bk=vec(bk, 4), b1=4 / np.pi, b3=4 / (3 * np.pi))
for N in (1, 5, 25, 101):
    S = sum(4 / (k * np.pi) * np.sin(k * x) for k in range(1, N + 1, 2))
    err = np.sqrt(ip(sq - S, sq - S) / (2 * np.pi))
    out(**{f"rms{N}": float(err), f"over{N}": float(S.max() - 1)})
# 编码器偏心误差（角秒）：e(θ) = 40 sin θ + 15 cos θ − 12 sin 2θ + 6 cos 3θ + 噪声 2
rng = np.random.default_rng(116)
th = np.arange(360) * np.pi / 180
e = 40 * np.sin(th) + 15 * np.cos(th) - 12 * np.sin(2 * th) + 6 * np.cos(3 * th) + rng.normal(scale=2.0, size=th.size)
cols, names = [np.ones_like(th)], ["1"]
for k in range(1, 5):
    cols += [np.cos(k * th), np.sin(k * th)]
    names += [f"cos{k}θ", f"sin{k}θ"]
A = np.column_stack(cols)
G = A.T @ A
coef = np.linalg.solve(G, A.T @ e)
res = e - A @ coef
out(Gdiag=vec(np.diag(G), 0), Goff=sci(float(np.abs(G - np.diag(np.diag(G))).max()) + 1e-18, 0), coef=vec(coef, 2),
    rms_before=float(np.sqrt(np.mean(e ** 2))), rms_after=float(np.sqrt(np.mean(res ** 2))))
# 勒让德多项式：对 1, x, x², x³ 在 [−1, 1] 上做格拉姆–施密特（不归一化，取 P(1) = 1）
t = np.linspace(-1, 1, 200001)
ipt = lambda f, g: float(np.trapezoid(f * g, t))
basis = []
for k in range(4):
    f = t ** k
    for p in basis:
        f = f - ipt(f, p) / ipt(p, p) * p
    basis.append(f / f[-1])
leg = [Lg.legval(t, np.eye(4)[k]) for k in range(4)]
out(leg_err=sci(float(max(np.abs(b - l).max() for b, l in zip(basis, leg))), 0))
# 以单项式与勒让德多项式为基拟合（12 个等距点，8 次）：AᵀA 的条件数
xs = np.linspace(-1, 1, 12)
Vm = np.vander(xs, 9, increasing=True)
Vl = Lg.legvander(xs, 8)
out(cond_m=sci(float(np.linalg.cond(Vm.T @ Vm)), 0), cond_l=sci(float(np.linalg.cond(Vl.T @ Vl)), 0))
