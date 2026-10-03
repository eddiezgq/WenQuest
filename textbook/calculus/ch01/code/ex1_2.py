"""1.2 节：位置与速度——相减得速度，相加回位置；AGV 编码器数据的差分与累加。"""
import math

import numpy as np

from bookout import out

# 每小时一记：里程 0, 1, 4, 9, 16（平方数），相减得每小时的速度 1, 3, 5, 7，相加回到里程
dist = [0, 1, 4, 9, 16]
speed = [b - a for a, b in zip(dist, dist[1:])]
back = [sum(speed[:k]) for k in range(len(speed) + 1)]
assert back == dist
out(speeds=", ".join(map(str, speed)), sum_speeds=sum(speed))

# 匀加速出发的 AGV：x(t) = 0.25 t²，编码器每 Ts 秒读一次；读数取整到 0.1 mm，再加 ±0.5 mm 的均匀噪声（假设值）
Ts = 0.02
t = np.arange(0, 4 + Ts / 2, Ts)
x = 0.25 * t**2
rng = np.random.default_rng(1)
xm = np.round((x + rng.uniform(-5e-4, 5e-4, t.size)) * 1e4) / 1e4
v = np.diff(xm) / Ts                       # 每个采样周期的平均速度
tmid = (t[:-1] + t[1:]) / 2
err_v = float(np.max(np.abs(v - 0.5 * tmid)))
xr = np.concatenate([[xm[0]], xm[0] + np.cumsum(v) * Ts])   # 把速度乘时间加回去
err_x = float(np.max(np.abs(xr - xm)))
# 只知道速度表（真速度 0.5t），用矩形累加求里程
for n in (4, 20, 200):
    h = 4 / n
    est = sum(0.5 * (k * h) * h for k in range(n))           # 左端点：每段用起点的速度
    out(**{f"odo{n}": est})
out(Ts_ms=Ts * 1000, n_samples=t.size, err_v=err_v, err_x=err_x, x_end=float(xm[-1]), v_last=float(v[-1]))
