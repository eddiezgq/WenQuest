"""第 6 章部分习题答案中的数值。"""
import bisect as _bs
import math

import numpy as np

from _arm import L1, L2
from _traj import K, clearance, ee
from bookout import out

# 6.1.6：两级齿轮，总减速比 25π，齿数 12 到 120，小齿轮带大齿轮
target = 25 * math.pi
ratios = sorted({(p / q, p, q) for q in range(12, 121) for p in range(q, 121)})
vals = [t[0] for t in ratios]
best = (1e9, None, None)
for v1, p1, q1 in ratios:
    t = target / v1
    i = _bs.bisect_left(vals, t)
    for j in (i - 1, i):
        if 0 <= j < len(vals):
            e = abs(v1 * vals[j] - target)
            if e < best[0]:
                best = (e, (p1, q1), ratios[j][1:])
out(e616=f"({best[1][0]}/{best[1][1]})·({best[2][0]}/{best[2][1]})", e616_err=best[0], e616_rel=best[0] / target)

# 6.2.8：1 − sin n < 10⁻¹² 的最小 n
n = np.arange(1, 10 ** 6 + 1)
k = int(np.nonzero(1 - np.sin(n.astype(float)) < 1e-12)[0][0])
out(e628=int(n[k]))

# 6.4.4：x = cos x / 2 + 1 在 [1/2, 3/2]
q = math.sin(1.5) / 2
x0, x1 = 1.0, math.cos(1.0) / 2 + 1
kk = math.ceil(math.log(1e-8 * (1 - q) / abs(x1 - x0)) / math.log(q))
x = 1.0
for _ in range(100):
    x = math.cos(x) / 2 + 1
xs = 1.0
it = 0
while abs(xs - x) >= 1e-8:
    xs = math.cos(xs) / 2 + 1
    it += 1
out(e644_q=q, e644_k=kk, e644_root=x, e644_actual=it)


# 6.4.5：CCD 收敛快慢与目标位置
def ccd(tx, ty, n=60):
    t1 = t2 = 0.0
    steps = []
    for _ in range(n):
        o1, o2 = t1, t2
        ex, ey = L1 * math.cos(t1), L1 * math.sin(t1)
        px, py = ex + L2 * math.cos(t1 + t2), ey + L2 * math.sin(t1 + t2)
        t2 += math.atan2(ty - ey, tx - ex) - math.atan2(py - ey, px - ex)
        px, py = ex + L2 * math.cos(t1 + t2), ey + L2 * math.sin(t1 + t2)
        t1 += math.atan2(ty, tx) - math.atan2(py, px)
        t1, t2 = math.remainder(t1, 2 * math.pi), math.remainder(t2, 2 * math.pi)
        steps.append(max(abs(math.remainder(t1 - o1, 2 * math.pi)), abs(math.remainder(t2 - o2, 2 * math.pi))))
    return steps


s1 = ccd(0.45, 0.35)
s2 = ccd(0.70, 0.35)
r = L1 + L2
s3 = ccd(r * 0.8, r * 0.6, 200)
out(e645_r1=s1[20] / s1[19], e645_r2=s2[20] / s2[19], e645_r3=s3[150] / s3[149], e645_dist2=math.hypot(0.70, 0.35))

# 6.5.5：障碍离轨迹 5 mm
t0 = 0.6
x, y = ee(t0)
x2, y2 = ee(t0 + 1e-6)
vx, vy = (x2 - x) / 1e-6, (y2 - y) / 1e-6
v = math.hypot(vx, vy)
o3 = (x - 0.005 * vy / v, y + 0.005 * vx / v)
tt, cnt, rmin = 0.0, 0, 1.0
while True:
    rr = clearance(tt, o3) / K
    cnt += 1
    rmin = min(rmin, rr)
    if tt + rr > 1:
        break
    tt += 0.9 * rr
out(e655_n=cnt, e655_rmin=rmin, e655_dmin=min(clearance(k / 10 ** 5, o3) for k in range(10 ** 5 + 1)))

# 6.6.5：安全距离 30 mm，障碍 2
O2 = (0.176, 0.634)
gmin = min(clearance(k / 10 ** 5, O2) for k in range(10 ** 5 + 1)) - 0.03
out(e665_gmin=gmin * 1000, e665_h=2 * gmin / K)

# 6.7.6：两个扰动频率比为 2
tt = np.arange(0, 200, 0.001)
e = 0.02 * np.sin(2 * math.pi * 1.3 * tt) + 0.01 * np.sin(2 * math.pi * 2.6 * tt)
out(e676=float(e.max()) * 1000)
