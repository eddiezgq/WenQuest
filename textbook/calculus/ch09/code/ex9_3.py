"""9.3 节：柯西中值定理——两个关节同时运动：肩关节按五次多项式转 90°，肘关节按三次多项式转 45°，同在 T = 2 s 内完成。
关节空间里的路径 (θ₁(t), θ₂(t)) 的弦与某一时刻的切线平行：θ₂′(ξ)/θ₁′(ξ) = Δθ₂/Δθ₁。
与“分别用两次拉格朗日中值定理”比较：两个中值点一般不同。"""
import math

from bookout import out

T, D1, D2 = 2.0, 90.0, 45.0
w1 = lambda t: D1 / T * 30 * (t / T) ** 2 * (1 - t / T) ** 2      # °/s
w2 = lambda t: D2 / T * 6 * (t / T) * (1 - t / T)


def roots(f, lo, hi, n=4000):
    rs = []
    for k in range(n):
        a, b = lo + (hi - lo) * k / n, lo + (hi - lo) * (k + 1) / n
        if f(a) * f(b) < 0:
            for _ in range(60):
                m = (a + b) / 2
                a, b = (a, m) if f(a) * f(m) <= 0 else (m, b)
            rs.append((a + b) / 2)
    return rs


# 柯西：w1(ξ)·Δ₂ − w2(ξ)·Δ₁ = 0
xc = roots(lambda t: w1(t) * D2 - w2(t) * D1, 1e-3, T - 1e-3)
out(xi_c=", ".join(f"{x:.4f}" for x in xc), xi_c1=xc[0], xi_c_exact=T * (1 - math.sqrt(0.2)) / 2,
    ratio_c=w2(xc[0]) / w1(xc[0]))
# 分别用拉格朗日：w1(ξ₁) = Δ₁/T，w2(ξ₂) = Δ₂/T
x1 = roots(lambda t: w1(t) - D1 / T, 1e-3, T - 1e-3)
x2 = roots(lambda t: w2(t) - D2 / T, 1e-3, T - 1e-3)
out(xi_1=x1[0], xi_2=x2[0], wrong_ratio=w2(x1[0]) / w1(x1[0]))
