"""11.2 节：直线运动——x(t) = t³ − 6t² + 9t 的运动方向、加速减速与路程；AGV 的安全车速：
激光雷达探测距离 d，反应时间 t_r，最大减速度 a_b，停车距离 v t_r + v²/(2a_b) ≤ d。"""
import math

from bookout import out

x = lambda t: t ** 3 - 6 * t ** 2 + 9 * t
v = lambda t: 3 * t * t - 12 * t + 9
a = lambda t: 6 * t - 12
out(x1=x(1), x3=x(3), x4=x(4), dist=abs(x(1) - x(0)) + abs(x(3) - x(1)) + abs(x(4) - x(3)), disp=x(4) - x(0))

tr, ab = 0.2, 1.5           # s，m/s²
vmax = lambda d: ab * (-tr + math.sqrt(tr * tr + 2 * d / ab))
rows = []
for d in (1.0, 2.0, 3.0, 5.0, 8.0):
    v0 = vmax(d)
    rows.append(f"| {d:.0f} | {v0:.2f} | {v0 * tr:.2f} | {v0 * v0 / (2 * ab):.2f} |")
out(tr=tr, ab=ab, brake_tab="\n".join(rows), v3=vmax(3.0))
# 反应时间加倍
tr2 = 0.4
out(v3_slow=ab * (-tr2 + math.sqrt(tr2 * tr2 + 2 * 3.0 / ab)))
