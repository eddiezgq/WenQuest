"""13.5 节：换元积分法——几个换元的数值核对；单位圆面积；奇偶函数在对称区间上的积分；
周期函数在一个周期上的积分与起点无关；轨迹的时间缩放：五次多项式运动中 ∫α² dt 与 T³ 成反比。"""
import math

from bookout import out


def mid(f, a, b, n=200000):
    h = (b - a) / n
    return sum(f(a + (k + 0.5) * h) for k in range(n)) * h


out(sub1=mid(lambda t: 2 * t * math.cos(t * t), 0, math.sqrt(math.pi / 2)),          # = sin(π/2) = 1
    sub2=mid(lambda t: t * math.exp(-t * t), 0, 2), sub2x=(1 - math.exp(-4)) / 2,
    sub3=mid(lambda t: math.tan(t), 0, math.pi / 3), sub3x=math.log(2),
    circle=4 * mid(lambda t: math.sqrt(max(1 - t * t, 0.0)), 0, 1), pi=math.pi,
    odd=mid(lambda t: t ** 3 * math.cos(t), -2, 2),
    per=[mid(lambda t: math.sin(t) ** 2, c, c + math.pi, 20000) for c in (0.0, 1.0, 2.5)])

# 五次多项式 θ = Δ s(t/T)：α = Δ s''(u)/T²，∫₀ᵀ α² dt = Δ²/T³ ∫₀¹ s''² du = (120/7) Δ²/T³
D = math.pi / 2
s2 = lambda u: 60 * u - 180 * u ** 2 + 120 * u ** 3
rows = []
for T in (0.5, 1.0, 2.0, 4.0):
    num = mid(lambda t: (D * s2(t / T) / T ** 2) ** 2, 0, T, 20000)
    rows.append(f"| {T:g} | {num:.4f} | {120 / 7 * D ** 2 / T ** 3:.4f} | {math.sqrt(num / T):.4f} |")
out(scale_tab="\n".join(rows), c120_7=120 / 7)
