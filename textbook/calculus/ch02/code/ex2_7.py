"""2.7 节：分段函数、参数方程、极坐标——AGV 的梯形速度曲线与位置；车轮上一点的摆线；
激光雷达在矩形房间里的一圈扫描（极坐标 → 直角坐标）。"""
import math

import numpy as np

from bookout import out

# 算例 2.7.1：加速度 0.5 m/s² 加速到 1 m/s，匀速，再以同样的加速度减速停下，共走 5 m
a, vmax, S = 0.5, 1.0, 5.0
ta = vmax / a                    # 加速时间
sa = 0.5 * a * ta**2             # 加速段距离
tc = (S - 2 * sa) / vmax         # 匀速时间
Ttot = 2 * ta + tc


def v(t):
    if t < 0 or t > Ttot:
        return 0.0
    if t < ta:
        return a * t
    if t <= ta + tc:
        return vmax
    return a * (Ttot - t)


def x(t):
    t = min(max(t, 0.0), Ttot)
    if t < ta:
        return 0.5 * a * t**2
    if t <= ta + tc:
        return sa + vmax * (t - ta)
    return S - 0.5 * a * (Ttot - t) ** 2


# 分段处的衔接：左右两个公式给出同一个值
for tj in (ta, ta + tc):
    assert abs((0.5 * a * tj**2 if tj == ta else sa + vmax * (tj - ta)) - x(tj)) < 1e-12
# 用很小的时间步把速度加起来，核对位置公式
dt = 1e-4
ts = np.arange(0, Ttot, dt)
xs = np.cumsum([v(t) * dt for t in ts])                 # 第 i 项是 t_i + dt 时刻的位置的近似
cum_err = max(abs(xs[i] - x(ts[i] + dt)) for i in range(ts.size))
out(ta=ta, sa=sa, tc=tc, Ttot=Ttot, x3=x(3.0), x6=x(6.0), cum_err=cum_err)

# 算例 2.7.2：车轮半径 r = 0.075 m，轮缘上一点的摆线；车轮转一圈前进 2πr
r = 0.075
th = np.linspace(0, 4 * math.pi, 2001)
cx, cy = r * (th - np.sin(th)), r * (1 - np.cos(th))
assert abs(cy.max() - 2 * r) < 1e-9
# 轮缘上一点的速度与车速之比：用差商估计 |d(x, y)/dθ| / r，最大值在最高点
sp = np.hypot(np.diff(cx), np.diff(cy)) / np.diff(th) / r
out(r=r, circ=2 * math.pi * r, top_speed_ratio=round(float(sp.max()), 3))

# 算例 2.7.3：激光雷达位于 4 m × 3 m 房间内 (1, 1) 处，每 1° 一束，测距噪声 σ = 1 cm（固定种子）
W, H, px, py = 4.0, 3.0, 1.0, 1.0
rng = np.random.default_rng(3)
phi = np.radians(np.arange(0, 360, 1.0))
dist = []
for p in phi:
    c, s = math.cos(p), math.sin(p)
    cand = []
    if c > 1e-12:
        cand.append((W - px) / c)
    if c < -1e-12:
        cand.append(-px / c)
    if s > 1e-12:
        cand.append((H - py) / s)
    if s < -1e-12:
        cand.append(-py / s)
    dist.append(min(cand))
dist = np.array(dist) + rng.normal(0, 0.01, phi.size)
X, Y = px + dist * np.cos(phi), py + dist * np.sin(phi)
# 右墙（x = 4）上的点：转成直角坐标后横坐标都接近 4
right = np.abs(X - W) < 0.05
out(n_beams=phi.size, r0=float(dist[0]), r45=float(dist[45]), r90=float(dist[90]),
    right_n=int(right.sum()), right_mean=float(X[right].mean()), right_sd=float(X[right].std()))
# 墙 x = 4 在以雷达为原点的极坐标下是 r = 3 / cos φ
out(r_wall30=(W - px) / math.cos(math.radians(30)))
