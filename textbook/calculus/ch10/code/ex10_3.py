"""10.3 节：凹凸性——五次多项式关节运动的拐点在 T/2，正是速度最大的时刻；
琴生不等式：均方根加速度不小于平均加速度的绝对值，比较三次、五次多项式与梯形速度曲线的峰值、平均、均方根加速度。"""
import math

import numpy as np

from _traj import cubic, quintic, trapezoid
from bookout import out

T, D = 2.0, math.pi / 2
t = np.linspace(0, T, 200001)
rows = []
for name, f in (("三次多项式", lambda t: cubic(t, T, D)), ("五次多项式", lambda t: quintic(t, T, D)),
                ("梯形速度（加速段 T/3）", lambda t: trapezoid(t, T, D, T / 3))):
    th, w, a, j = f(t)
    rows.append(f"| {name} | {np.max(np.abs(w)):.4f} | {np.max(np.abs(a)):.4f} | {np.mean(np.abs(a)):.4f} | {math.sqrt(np.mean(a * a)):.4f} |")
out(prof_tab="\n".join(rows))
_, w, a, _ = quintic(t, T, D)
out(w_peak=float(np.max(w)), t_peak=float(t[np.argmax(w)]), w_formula=15 * D / (8 * T))
