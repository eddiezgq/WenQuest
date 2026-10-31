"""第 14 章部分习题答案中的数值。"""
import math

from scipy import integrate, special

from bookout import out

# 14.1.2、14.1.5
out(e1412b=(2 * math.e ** 3 + 1) / 9, e1412c=math.pi / 4 - 0.5, e1415=6 - 2 * math.e)
# 14.2.3：A = 0.3 rad，2 Hz，J = 0.2，b = 0.1
A, W, J, b = 0.3, 4 * math.pi, 0.2, 0.1
out(e1423_P=b * A * A * W * W / 2, e1423_pk=J * A * A * W ** 3 / 2)
# 14.2.4：14.2.4 节的数据，只计 P > 0 的部分
J2, b2, A2, W2 = 0.5, 0.2, 0.5, 2 * math.pi
n = 200000
h = 1.0 / n
s = 0.0
for k in range(n):
    t = (k + 0.5) * h
    om = A2 * W2 * math.cos(W2 * t)
    P = (-J2 * A2 * W2 * W2 * math.sin(W2 * t) + b2 * om) * om
    s += max(P, 0.0) * h
out(e1424=s)
# 14.3.3：r = 0.1，L = 0.5，液位误差 1 mm
r, L = 0.1, 0.5
dV = lambda hh: 2 * L * math.sqrt(2 * r * hh - hh * hh) * 0.001 * 1e6     # mL
out(e1433a=dV(0.01), e1433b=dV(0.1))
# 14.4.3
out(e1443=math.pi / (3 * math.sqrt(3)))
# 14.4.4：m = 200，F0 = 300，k = 0.5，v0 = 2
m, F0, k, v0 = 200.0, 300.0, 0.5, 2.0
xa = m / (2 * k) * math.log(1 + k * v0 * v0 / F0)
x0 = m * v0 * v0 / (2 * F0)
out(e1444=xa, e1444_0=x0, e1444_pct=(x0 - xa) / x0 * 100)
# 14.4.5：滑行距离 ≤ 15 m 的 c₂
m, c1, v0, v1 = 1.5, 0.3, 10.0, 1.0
X = lambda c2: m / c2 * math.log((c1 + c2 * v0) / (c1 + c2 * v1))
lo, hi = 0.01, 5.0
for _ in range(100):
    mid = (lo + hi) / 2
    if X(mid) > 15:
        lo = mid
    else:
        hi = mid
out(e1445=hi)
# 14.5.4：ω₀ = 90°/s，ε = 0.2
T = 4 / math.sqrt(1 - 0.04)
out(e1454_T=T, e1454_w=360 / T, e1454_half=T / 2)
# 14.5.6：1/√(1 − ε²) 与 1 + ε²/2 相差 1%
lo, hi = 0.01, 0.99
for _ in range(100):
    mid = (lo + hi) / 2
    if (1 / math.sqrt(1 - mid * mid)) / (1 + mid * mid / 2) - 1 < 0.01:
        lo = mid
    else:
        hi = mid
out(e1456=lo)
# 14.7.4：l = 0.6 m，从 60° 释放
Leq = 0.4
T0 = 2 * math.pi * math.sqrt(Leq / 9.81)
r60 = 2 / math.pi * special.ellipk(math.sin(math.radians(30)) ** 2)
lo, hi = 1.0, 60.0
for _ in range(100):
    mid = (lo + hi) / 2
    if 2 / math.pi * special.ellipk(math.sin(math.radians(mid) / 2) ** 2) < 1.005:
        lo = mid
    else:
        hi = mid
out(e1474_T0=T0, e1474_T=T0 * r60, e1474_th=lo)
# 14.7.7：a = 2，b = 1 的椭圆周长
a, bb = 2.0, 1.0
e2 = 1 - (bb / a) ** 2
per, _ = integrate.quad(lambda p: math.sqrt(1 - e2 * math.sin(p) ** 2), 0, math.pi / 2)
out(e1477=4 * a * per, e1477_r=math.pi * (3 * (a + bb) - math.sqrt((3 * a + bb) * (a + 3 * bb))))
