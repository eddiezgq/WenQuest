"""算例 7.1.1、7.1.2 与 7.1.4 节：AGV 匀加速出发时的平均速度与瞬时速度；UR5e 肩关节五次多项式运动在 t = 0.5 s 的角速度，
用不同步长的前向差商与中心差商逼近，看误差怎样先减小、后增大。"""
import math

import numpy as np

from _traj import quintic
from bookout import out

# 算例 7.1.1：x(t) = 0.25 t²（m），在 [2, 2 + h] 上的平均速度 = 1 + 0.25 h
x = lambda t: 0.25 * t**2
hs = [1, 0.5, 0.1, 0.01, 0.001]
avg = [(x(2 + h) - x(2)) / h for h in hs]
assert all(abs(a - (1 + 0.25 * h)) < 1e-9 for a, h in zip(avg, hs))
out(**{f"avg{i}": a for i, a in enumerate(avg)}, v2=0.5 * 2)

# 7.1.2 节：y = x² 在 (1, 1) 处的割线斜率 2 + h
out(sec_h1=((1 + 0.1) ** 2 - 1) / 0.1, sec_h2=((1 + 0.01) ** 2 - 1) / 0.01)

# 算例 7.1.2：肩关节在 T = 2 s 内由 0 转到 90°（五次多项式），t0 = 0.5 s
T, D = 2.0, math.pi / 2
th = lambda t: float(quintic(t, T, D)[0])
t0 = 0.5
w_true = float(quintic(t0, T, D)[1])
rows = []
for k in range(1, 13):
    h = 10.0 ** (-k)
    fwd = (th(t0 + h) - th(t0)) / h
    cen = (th(t0 + h) - th(t0 - h)) / (2 * h)
    rows.append((k, fwd, abs(fwd - w_true), cen, abs(cen - w_true)))
kf = min(rows, key=lambda r: r[2])
kc = min(rows, key=lambda r: r[4])
out(w_true=w_true, w_deg=math.degrees(w_true), th0=math.degrees(th(t0)),
    f1=rows[0][1], c1=rows[0][3], ef1=rows[0][2], ec1=rows[0][4],
    f2=rows[1][1], c2=rows[1][3], ef2=rows[1][2], ec2=rows[1][4],
    f4=rows[3][1], ef4=rows[3][2], c4=rows[3][3], ec4=rows[3][4],
    f8=rows[7][1], ef8=rows[7][2], c8=rows[7][3], ec8=rows[7][4],
    f12=rows[11][1], ef12=rows[11][2], c12=rows[11][3], ec12=rows[11][4],
    best_f_k=kf[0], best_f_err=kf[2], best_c_k=kc[0], best_c_err=kc[4],
    eps=np.finfo(float).eps)
# 书中的表 7.1.1：逐行列出
table = "\n".join(f"| $10^{{-{k}}}$ | {f:.12f} | {ef:.1e} | {c:.12f} | {ec:.1e} |" for k, f, ef, c, ec in rows)
out(table=table)
