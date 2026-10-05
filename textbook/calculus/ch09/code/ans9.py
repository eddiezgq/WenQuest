"""第 9 章部分习题答案中的数值。"""
import math

from _traj import ur5e_links
from bookout import out


def bisect(f, lo, hi, n=80):
    for _ in range(n):
        mid = (lo + hi) / 2
        if (f(lo) > 0) == (f(mid) > 0):
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# 9.1.4：五次多项式的加加速度 60 − 360s + 360s² = 0
T = 2.0
out(e914_1=T * (3 - math.sqrt(3)) / 6, e914_2=T * (3 + math.sqrt(3)) / 6)
# 9.1.8：eˣ = 3x
g = lambda x: math.exp(x) - 3 * x
out(e918_1=bisect(g, 0, 1), e918_2=bisect(g, 1, 2))
# 9.2.1
out(e921_1=2 / math.sqrt(3), e921_2=math.e - 1)
# 9.3.5：关节空间路径到弦 θ₂ = θ₁/2 的最大距离（度）
D1, D2 = 90.0, 45.0
best = 0.0
for k in range(1, 4000):
    s = k / 4000
    t1 = D1 * (10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5)
    t2 = D2 * (3 * s ** 2 - 2 * s ** 3)
    best = max(best, abs(t2 - t1 / 2) / math.sqrt(1.25))
out(e935=best)
# 9.5.2：√4.2
x = 4.2
p2 = 2 + (x - 4) / 4 - (x - 4) ** 2 / 64
out(e952_p=p2, e952_err=abs(math.sqrt(x) - p2), e952_bound=3 / 8 * 4 ** -2.5 * (x - 4) ** 3 / 6)
# 9.5.4：r(θ) 从 60° 到 66°
l1, l2 = ur5e_links()
a, b = l1 * l1 + l2 * l2, 2 * l1 * l2
r = lambda t: math.sqrt(a + b * math.cos(t))
t0, h = math.radians(60), math.radians(6)
R = r(t0)
R1 = -b * math.sin(t0) / (2 * R)
R2 = (-b * math.cos(t0) / 2 - R1 * R1) / R
R3 = (b * math.sin(t0) / 2 - 3 * R1 * R2) / R
out(e954_q=(R1 * h + R2 / 2 * h * h) * 1000, e954_exact=(r(t0 + h) - R) * 1000, e954_est=R3 / 6 * h ** 3 * 1000)
# 9.5.7：五次多项式，|θ‴| 最大 60Δ/T³，h = 10 ms
D = math.pi / 2
J = 60 * D / T ** 3
hh = 0.01
worst = 0.0
for k in range(0, 2001):
    t = k * (T - hh) / 2000
    th = lambda u: D * (10 * (u / T) ** 3 - 15 * (u / T) ** 4 + 6 * (u / T) ** 5)
    s = t / T
    w = D / T * (30 * s ** 2 - 60 * s ** 3 + 30 * s ** 4)
    al = D / T ** 2 * (60 * s - 180 * s ** 2 + 120 * s ** 3)
    worst = max(worst, abs(th(t + hh) - (th(t) + w * hh + al * hh * hh / 2)))
out(e957_J=J, e957_bound=J * hh ** 3 / 6, e957_obs=worst)
# 9.6.3：sin 10°
x = math.radians(10)
out(e963=x - x ** 3 / 6 + x ** 5 / 120, e963_bound=x ** 7 / 5040)
# 9.6.6：腕心缩回 1 mm、10 mm
c = l1 * l2 / (2 * (l1 + l2))
for d in (1, 10):
    ap = math.degrees(math.sqrt(d / 1000 / c))
    target = (l1 + l2) - d / 1000
    ex = math.degrees(math.acos((target ** 2 - l1 * l1 - l2 * l2) / (2 * l1 * l2)))
    out(**{f"e966_{d}_ap": ap, f"e966_{d}_ex": ex})
# 9.6.7：单摆
th0 = math.radians(10)
out(e967_pct=th0 ** 2 / 16 * 100, e967_amp=math.degrees(math.sqrt(16 / 86400)))
# 9.7.2：∛30 = 3(1 + 1/9)^{1/3}
u = 1 / 9
terms, s, k, coef = [], 0.0, 0, 1.0
while True:
    s += coef * u ** k
    nxt = coef * (1 / 3 - k) / (k + 1)
    if abs(3 * nxt * u ** (k + 1)) < 1e-6:
        break
    coef, k = nxt, k + 1
out(e972=3 * s, e972_terms=k + 1, e972_err=abs(3 * s - 30 ** (1 / 3)))
# 9.7.6：五项，阈值与最大相对误差
eps = 2.220446049250313e-16
u5 = (math.factorial(12) * eps) ** (1 / 12)          # 2u¹⁰/12! = 2ε/u²
out(e976_u=u5, e976_err=2 * eps / u5 ** 2)
