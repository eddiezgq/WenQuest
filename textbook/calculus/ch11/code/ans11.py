"""第 11 章部分习题答案中的数值。"""
import math

from bookout import out


def bis(f, lo, hi, n=100):
    for _ in range(n):
        m = (lo + hi) / 2
        if (f(lo) > 0) == (f(m) > 0):
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


# 11.1.1：有盖圆柱，表面积 1 m²：h = 2r；底盖加倍厚：成本 2·2πr² + 2πrh = 1 → h = 4r
out(e1111_r=math.sqrt(1 / (6 * math.pi)))
# 11.1.6：拐角走廊 a = 2、b = 1.5
out(e1116=(2 ** (2 / 3) + 1.5 ** (2 / 3)) ** 1.5)
# 11.2.3：1.5 m/s，0.2 s，2 m 内停住
out(e1123=1.5 ** 2 / (2 * (2 - 1.5 * 0.2)))
# 11.2.4：相对速度 0.5 m/s，后车减速 0.5 m/s²：相对速度减到 0 用 1 s，期间相对位移 0.25 m
out(e1124=3 - 0.5 * 1 + 0.5 * 0.5 * 1 ** 2)
# 11.3.1：V = 120，A = 300
rows = []
for D in (30, 60, 150):
    if D >= 120 ** 2 / 300:
        rows.append((D, D / 120 + 120 / 300, 120.0))
    else:
        rows.append((D, 2 * math.sqrt(D / 300), math.sqrt(300 * D)))
out(e1131="；".join(f"{d}°：{t:.3f} s，{v:.1f}°/s" for d, t, v in rows))
# 11.3.3：两次 30° 转动
T0 = 2 * 2 * math.sqrt(30 / 400)
out(e1133_0=T0, e1133_V=T0, e1133_A=2 * 2 * math.sqrt(30 / 800))
# 11.4.1：v1 = 1.0
v1, v2 = 1.0, 1.2
dT = lambda x: x / (v1 * math.hypot(x, 3)) - (6 - x) / (v2 * math.hypot(6 - x, 2))
x = bis(dT, 0, 6)
out(e1141_x=x, e1141_T=math.hypot(x, 3) / v1 + math.hypot(6 - x, 2) / v2)
# 11.4.3：临界角
out(e1143=math.degrees(math.asin(1 / 1.33)))
# 11.4.5：救生员
f = lambda x: x / (5 * math.hypot(x, 30)) - (80 - x) / (1.5 * math.hypot(80 - x, 40))
x = bis(f, 0, 80)
Tb = math.hypot(x, 30) / 5 + math.hypot(80 - x, 40) / 1.5
xs = 80 * 30 / 70
Ts = math.hypot(xs, 30) / 5 + math.hypot(80 - xs, 40) / 1.5
out(e1145_x=x, e1145_T=Tb, e1145_Ts=Ts)
# 11.5.1：P′ = 50 − 20 − 0.004q = 0
out(e1151=30 / 0.004)
# 11.5.3：S = 200
D, H = 12000, 4.0
for S in (800.0, 200.0):
    Q = math.sqrt(2 * D * S / H)
    out(**{f"e1153_Q{int(S)}": Q, f"e1153_C{int(S)}": 2 * math.sqrt(D * S * H / 2)})
