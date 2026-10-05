"""9.1 节：费马引理与罗尔定理——关节“去而复返”的轨迹 q(t) = Δ·16s²(1 − s)²（s = t/T）：
两端位置相同、速度为零。罗尔定理一层层往下用：速度、加速度、加加速度各在哪里为零；
x⁵ + x − 1 = 0 恰有一个实根。"""
import math

from bookout import out

T, D = 2.0, math.radians(60)          # 往返 2 s，最远转到 60°


def q(t):
    s = t / T
    return D * 16 * s * s * (1 - s) ** 2


def w(t):                              # 角速度 q′ = 32Δ s(1 − s)(1 − 2s)/T
    s = t / T
    return 32 * D * s * (1 - s) * (1 - 2 * s) / T


def a(t):                              # 角加速度 q″ = 32Δ(1 − 6s + 6s²)/T²
    s = t / T
    return 32 * D * (1 - 6 * s + 6 * s * s) / T ** 2


def j(t):                              # 加加速度 q‴ = 32Δ(12s − 6)/T³
    s = t / T
    return 32 * D * (12 * s - 6) / T ** 3


def bisect(f, lo, hi, n=60):
    flo = f(lo)
    for _ in range(n):
        mid = (lo + hi) / 2
        if (f(mid) > 0) == (flo > 0):
            lo, flo = mid, f(mid)
        else:
            hi = mid
    return (lo + hi) / 2


tw = bisect(w, 0.5, 1.5)                      # 速度在内部的零点（返回点）
ta1, ta2 = bisect(a, 0.01, tw), bisect(a, tw, T - 0.01)
tj = bisect(j, ta1, ta2)
out(T=T, D_deg=60, tw=tw, ta1=ta1, ta2=ta2, tj=tj, ta1_exact=T * (3 - math.sqrt(3)) / 6,
    wmax_deg=math.degrees(max(abs(w(k * T / 2000)) for k in range(2001))))

# x⁵ + x − 1 = 0：f(0) = −1 < 0 < 1 = f(1)，f′ = 5x⁴ + 1 > 0
f = lambda x: x ** 5 + x - 1
out(root5=bisect(f, 0.0, 1.0))
