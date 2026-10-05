"""第 8 章部分习题答案中的数值。"""
import math

from _traj import ur5e_links
from bookout import out

l1, l2 = ur5e_links()
# 8.1.2
f = lambda x: x ** 3 - x
out(e812="；".join(f"Δx = {d:g}：Δy = {f(2 + d) - f(2):.6g}，dy = {11 * d:.6g}，差 {f(2 + d) - f(2) - 11 * d:.4g}" for d in (1, 0.1, 0.01)))
# 8.1.7：r′(θ) = −l₁l₂ sin θ / r
r = lambda t: math.sqrt(l1 * l1 + l2 * l2 + 2 * l1 * l2 * math.cos(t))
dr = lambda t: -l1 * l2 * math.sin(t) / r(t)
d = math.radians(0.5)
out(e817_60=dr(math.radians(60)) * d * 1000, e817_10=dr(math.radians(10)) * d * 1000, e817_170=dr(math.radians(170)) * d * 1000)
best = max(range(1, 1800), key=lambda k: abs(dr(math.radians(k / 10))))
out(e817_max_deg=best / 10, e817_max=abs(dr(math.radians(best / 10))) * 1000)
# 8.1.8：油漆体积
R, t = 2.0, 0.0005
out(e818_d=4 * math.pi * R * R * t, e818_exact=4 / 3 * math.pi * ((R) ** 3 - (R - t) ** 3))
# 8.2.3：sin x ≈ x 误差 < 1e−4
out(e823_bound=(2e-4) ** (1 / 3), e823_true=(6e-4) ** (1 / 3))
# 8.2.4：θ₀ = 60°
m, g, L = 5, 9.81, l1 + l2
th0 = math.radians(60)
tau = lambda th: m * g * L * math.cos(th)
lin = lambda th: tau(th0) - m * g * L * math.sin(th0) * (th - th0)
def edge(sign):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if abs(tau(th0 + sign * mid) - lin(th0 + sign * mid)) <= 0.01 * tau(th0) else (lo, mid)
    return math.degrees(lo)
out(e824_bound=math.degrees(math.sqrt(0.02 * math.cos(th0))), e824_plus=edge(1), e824_minus=edge(-1))
# 8.2.5：arccos 在 0.9999 处的条件数
x = 0.9999
out(e825=abs(x / (math.sqrt(1 - x * x) * math.acos(x))))
# 8.3.4：手臂伸直、θ₂ = 150°
out(e834_0=(r(0) + l2) * 1e-3 * 1000, e834_150=(r(math.radians(150)) + l2) * 1e-3 * 1000)
# 8.4.1、8.4.2
x = 2.0
for _ in range(8):
    x = x - (x ** 3 - 2 * x - 5) / (3 * x * x - 2)
out(e841=x)
x = 2.0
for _ in range(8):
    x = x - (x ** 3 - 10) / (3 * x * x)
out(e842=x)
# 8.4.5：ζ = 0.4、0.8，牛顿法到 |f| < 1e−12 的步数
for z in (0.4, 0.8):
    wn = 10.0
    wd = wn * math.sqrt(1 - z * z)
    c = z / math.sqrt(1 - z * z)
    q = lambda t: 1 - math.exp(-z * wn * t) * (math.cos(wd * t) + c * math.sin(wd * t)) - 0.95
    dq = lambda t: math.exp(-z * wn * t) * (wn ** 2 / wd) * math.sin(wd * t)
    t, k = 0.2, 0
    while abs(q(t)) >= 1e-12 and k < 50:
        t -= q(t) / dq(t)
        k += 1
    out(**{f"e845_{int(z * 10)}": t, f"e845_{int(z * 10)}_n": k})
# 8.5.1：e^x 在 1 处
best_f = min((abs((math.exp(1 + 10 ** -k) - math.e) / 10 ** -k - math.e), k) for k in range(1, 16))
best_c = min((abs((math.exp(1 + 10 ** -k) - math.exp(1 - 10 ** -k)) / (2 * 10 ** -k) - math.e), k) for k in range(1, 16))
out(e851_f_k=best_f[1], e851_f=best_f[0], e851_c_k=best_c[1], e851_c=best_c[0])
# 8.5.4：理查森
D0 = lambda h: (math.sin(1 + h) - math.sin(1 - h)) / (2 * h)
R1 = (4 * D0(0.05) - D0(0.1)) / 3
R2 = (4 * D0(0.025) - D0(0.05)) / 3
out(e854_1=abs(R1 - math.cos(1)), e854_2=abs((16 * R2 - R1) / 15 - math.cos(1)), e854_c=abs(D0(0.05) - math.cos(1)))
# 8.5.5：20 位编码器
q20 = 2 * math.pi / 2 ** 20
amax = 1.7368937594455558
hs = math.sqrt(2 * q20 / (math.sqrt(6) * amax))
out(e855_h=hs * 1000, e855_E=amax * hs / 2 + q20 / (math.sqrt(6) * hs))
