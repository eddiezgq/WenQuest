"""9.4 节：洛必达法则——几个极限的数值核对；对数、幂、指数的增长比较（何时“反超”）；
关节阶跃响应在 ζ → 1 时的极限：欠阻尼公式在 ζ = 1 处是 0/0 型，极限就是临界阻尼的公式。"""
import math

from bookout import out

# (x − sin x)/x³ → 1/6：直接计算，x 太小时相消
rows = []
for k in (1, 2, 3, 5, 7):
    x = 10.0 ** -k
    val = (x - math.sin(x)) / x ** 3
    rows.append(f"| $10^{{-{k}}}$ | {val:.10f} | {abs(val - 1 / 6):.1e} |")
out(sinx_tab="\n".join(rows))

# ln x 与 x^0.1：令 u = ln x，ln x = x^0.1 ⇔ u = e^{0.1u}；牛顿法求两个交点
def newton(g, dg, u):
    for _ in range(100):
        u -= g(u) / dg(u)
    return u
g = lambda u: u - math.exp(0.1 * u)
dg = lambda u: 1 - 0.1 * math.exp(0.1 * u)
u1, u2 = newton(g, dg, 1.0), newton(g, dg, 40.0)
out(cross1=math.exp(u1), cross2=math.exp(u2), cross2_exp=u2 / math.log(10))
# n^10 与 1.1^n：10 ln n = n ln 1.1 的大根
h = lambda n: 10 * math.log(n) - n * math.log(1.1)
dh = lambda n: 10 / n - math.log(1.1)
out(cross_pow=newton(h, dh, 1000.0))

# 阶跃响应：q(t) = 1 − e^{−ζωₙt}[cos ω_d t + ζ/√(1 − ζ²)·sin ω_d t]，ω_d = ωₙ√(1 − ζ²)
wn, t = 10.0, 0.3
crit = 1 - math.exp(-wn * t) * (1 + wn * t)                      # 临界阻尼 ζ = 1


def q(z):
    s = math.sqrt(1 - z * z)
    wd = wn * s
    return 1 - math.exp(-z * wn * t) * (math.cos(wd * t) + z / s * math.sin(wd * t))


rows = []
for k in (2, 4, 6, 8, 10, 12, 14):
    z = 1 - 10.0 ** -k
    rows.append(f"| $1 - 10^{{-{k}}}$ | {q(z):.15f} | {abs(q(z) - crit):.1e} |")
out(crit=crit, zeta_tab="\n".join(rows))
try:
    q(1.0)
    at1 = "ok"
except ZeroDivisionError:
    at1 = "ZeroDivisionError"
out(at1=at1)
