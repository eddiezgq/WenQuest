"""第 5 章部分习题答案中的数值。"""
import math

from _arm import L1, L2
from bookout import out


def bisect(f, a, b, tol=1e-13):
    fa = f(a)
    while b - a > tol:
        m = (a + b) / 2
        if m in (a, b):
            break
        fm = f(m)
        if (fm > 0) == (fa > 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


# 5.1.7：跳变处的差商 (−2π + ωT)/T
w = 0.5
out(e517_5=(-2 * math.pi + w * 0.005) / 0.005, e517_1=(-2 * math.pi + w * 0.001) / 0.001)
# 5.2.4：航向差折回 (−π, π]
d = -3.0 - 3.0
out(e524=math.atan2(math.sin(d), math.cos(d)))
# 5.2.5：每个控制周期最多转过的计数
out(e525_counts=math.pi * 1e-3 / (2 * math.pi) * 4096, e525_turns=65536 / 4096)
# 5.4.7：肘关节限位 [10°, 160°]
r = lambda t: math.sqrt(L1 * L1 + L2 * L2 + 2 * L1 * L2 * math.cos(math.radians(t)))
out(e547_max=r(10) * 1000, e547_min=r(160) * 1000)
# 5.5.1、5.5.2：方程的根
out(e551=bisect(lambda x: x ** 3 + x - 1, 0, 1), e551_n=math.ceil(math.log2(1 / 1e-8)))
out(e552_1=bisect(lambda x: math.exp(-x) - x, 0, 1), e552_2=bisect(lambda x: x * math.log(x) - 1, 1, 2),
    e552_3=bisect(lambda x: math.tan(x) - x, math.pi + 0.1, 1.5 * math.pi - 1e-9))
# 5.5.4：不同阻尼比下到达 95% 的时间
for z in (0.4, 0.8):
    wd = 10 * math.sqrt(1 - z * z)
    q = lambda t: 1 - math.exp(-z * 10 * t) * (math.cos(wd * t) + z / math.sqrt(1 - z * z) * math.sin(wd * t))
    out(**{f"e554_{int(z * 10)}": bisect(lambda t: q(t) - 0.95, 0, math.pi / wd)})
# 5.5.5：r = 700 mm
rr = 0.7
out(e555=math.degrees(bisect(lambda t: math.sqrt(L1 * L1 + L2 * L2 + 2 * L1 * L2 * math.cos(t)) - rr, 0, math.pi)),
    e555_exact=math.degrees(math.acos((rr * rr - L1 * L1 - L2 * L2) / (2 * L1 * L2))))
# 5.5.6：sin(10x) + 0.5x 在 [0, 3] 中的根（x = 0 是根）
g = lambda x: math.sin(10 * x) + 0.5 * x
n = 3000
xs = [3 * k / n for k in range(n + 1)]
roots = [0.0] + [bisect(g, a, b) for a, b in zip(xs[1:], xs[2:]) if (g(a) > 0) != (g(b) > 0)]
out(e556_n=len(roots), e556_last=roots[-1])
# 5.5.8：10⁹ 个元素的二分查找
out(e558=math.ceil(math.log2(1e9 + 1)))
# 5.6.6：末端误差 0.03 mm 时编码器的位数
dth = 3e-5 / (L1 + 2 * L2)
out(e566_bits=math.ceil(math.log2(2 * math.pi / dth)), e566_dth=dth)
# 5.6.7：θ₂ ∈ [10°, 160°] 时，角度误差 0.1° 允许的测距误差（两端都要看，取较小者）
e = math.radians(0.1)
d10 = r(10) - r(10 + 0.1)                      # θ₂ 从 10° 增到 10.1°，r 的变化
d160 = r(160 - 0.1) - r(160)                   # θ₂ 从 160° 减到 159.9°
d0 = (L1 + L2) - math.sqrt(L1 * L1 + L2 * L2 + 2 * L1 * L2 * math.cos(e))
dpi = math.sqrt(L1 * L1 + L2 * L2 - 2 * L1 * L2 * math.cos(e)) - abs(L1 - L2)
out(e567_10=d10 * 1000, e567_160=d160 * 1000, e567_ratio=min(d10, d160) / min(d0, dpi))
