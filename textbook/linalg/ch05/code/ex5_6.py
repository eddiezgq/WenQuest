"""5.6 节：三对角方程组与追赶法——LU 分解保持三对角结构，消元与回代都只需 O(n) 次运算；
机器人关节轨迹的三次样条（三对角方程组）；十万个节点的杆的稳态温度。"""

import numpy as np
from scipy.interpolate import CubicSpline

from _num import sci
from bookout import out, vec


def thomas(a, b, c, d):
    """追赶法解三对角方程组：a 为下对角（a[0] 不用），b 为主对角，c 为上对角（c[-1] 不用），d 为右端。"""
    n = len(b)
    cp, dp = np.zeros(n), np.zeros(n)
    cp[0], dp[0] = c[0] / b[0], d[0] / b[0]
    for i in range(1, n):   # “追”：消去下对角
        m = b[i] - a[i] * cp[i - 1]
        cp[i] = c[i] / m if i < n - 1 else 0.0
        dp[i] = (d[i] - a[i] * dp[i - 1]) / m
    x = np.zeros(n)
    x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):   # “赶”：回代
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


# 关节轨迹：6 个时刻（s）与关节角（°）；自然三次样条，内点的二阶导数 M₁…M₄ 满足三对角方程组（h = 1 s）
t = np.arange(6.0)
th = np.array([0.0, 20, 60, 90, 70, 40])
rhs = 6 * (th[2:] - 2 * th[1:-1] + th[:-2])
n = len(rhs)
M_in = thomas(np.ones(n), 4 * np.ones(n), np.ones(n), rhs)
M = np.concatenate([[0.0], M_in, [0.0]])
cs = CubicSpline(t, th, bc_type="natural")
out(th=vec(th, 0), rhs=vec(rhs, 0), M=vec(M_in, 2), spl_same=bool(np.allclose(cs(t, 2), M)))
tt = np.linspace(0, 5, 501)
out(vmax=float(np.abs(cs(tt, 1)).max()), amax=float(np.abs(cs(tt, 2)).max()))
# 十万个节点的杆：-u'' = 1，两端温度为 0；精确解 u = x(1 - x)/2，最大值 1/8
N = 100000
h = 1.0 / (N + 1)
u = thomas(-np.ones(N), 2 * np.ones(N), -np.ones(N), h * h * np.ones(N))
x = h * np.arange(1, N + 1)
out(umax=float(u.max()), uerr=sci(float(np.abs(u - x * (1 - x) / 2).max()), 1), ops=8 * N)
