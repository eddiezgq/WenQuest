"""6.4 节：柯西收敛准则——“相邻两步之差足够小就停”的陷阱（调和级数）；压缩迭代 x = cos x 的事后误差估计；
两节连杆的循环坐标下降（CCD）逆运动学迭代：步长、压缩比与真实误差；用有理指数逼近 2^√2。"""
import math

from _arm import L1, L2
from bookout import out

# 调和级数的部分和：步长 1/n → 0，部分和却趋于无穷
H, n = 0.0, 0
while True:
    n += 1
    H += 1 / n
    if 1 / n < 1e-6:
        break
out(h_stop_n=n, h_stop=H, h_1e12=math.log(1e12) + 0.5772156649)

# x = cos x：|g'(x)| = |sin x| ≤ sin 1 = q 在 [0, 1] 上
q = math.sin(1)
xs = [1.0]
for _ in range(60):
    xs.append(math.cos(xs[-1]))
xstar = 0.7390851332151607
rows = []
for k in (5, 10, 20, 40):
    step = abs(xs[k] - xs[k - 1])
    rows.append(f"| {k} | {step:.2e} | {q / (1 - q) * step:.2e} | {abs(xs[k] - xstar):.2e} |")
out(cos_tab="\n".join(rows), q=q, qfac=q / (1 - q))

# 两节连杆 CCD：交替转动肘关节、肩关节，使末端指向目标
tx, ty = 0.45, 0.35
t1, t2 = 0.0, 0.0
log = []
for it in range(1, 41):
    o1, o2 = t1, t2
    ex, ey = L1 * math.cos(t1), L1 * math.sin(t1)                       # 肘
    px, py = ex + L2 * math.cos(t1 + t2), ey + L2 * math.sin(t1 + t2)   # 末端
    t2 += math.atan2(ty - ey, tx - ex) - math.atan2(py - ey, px - ex)
    px, py = ex + L2 * math.cos(t1 + t2), ey + L2 * math.sin(t1 + t2)
    t1 += math.atan2(ty, tx) - math.atan2(py, px)
    t1, t2 = math.remainder(t1, 2 * math.pi), math.remainder(t2, 2 * math.pi)
    px = L1 * math.cos(t1) + L2 * math.cos(t1 + t2)
    py = L1 * math.sin(t1) + L2 * math.sin(t1 + t2)
    log.append((it, max(abs(t1 - o1), abs(t2 - o2)), math.hypot(px - tx, py - ty), t1, t2))
c = (tx * tx + ty * ty - L1 * L1 - L2 * L2) / (2 * L1 * L2)
t2e = math.acos(c)                                  # 肘部朝上、朝下两组解，CCD 收敛到其中一组
cand = []
for s in (1, -1):
    a2 = s * t2e
    a1 = math.atan2(ty, tx) - math.atan2(L2 * math.sin(a2), L1 + L2 * math.cos(a2))
    cand.append((a1, a2))
a1, a2 = min(cand, key=lambda p: abs(math.remainder(p[0] - log[-1][3], 2 * math.pi)) + abs(p[1] - log[-1][4]))
rows = []
for it, st, err, x1, x2 in log:
    if it in (1, 2, 5, 10, 20, 40):
        jerr = max(abs(math.remainder(x1 - a1, 2 * math.pi)), abs(x2 - a2))
        rows.append(f"| {it} | {st:.2e} | {jerr:.2e} | {err * 1000:.2e} |")
out(ccd_tab="\n".join(rows), ccd_ratio=log[20][1] / log[19][1], ccd_t1=math.degrees(a1), ccd_t2=math.degrees(a2))

# 2^√2：用 √2 的十进制截断 r_k（有理数）
r2 = math.sqrt(2)
rows = []
for k in (1, 2, 4, 8, 12):
    rk = math.floor(r2 * 10 ** k) / 10 ** k
    rows.append(f"| {k} | {rk:.{k}f} | {2 ** rk:.12f} |")
out(pow_tab="\n".join(rows), pow_true=2 ** r2)
