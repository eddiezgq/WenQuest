"""8.4 节：牛顿法——关节阶跃响应到达 95% 的时刻 t₉₅（与 5.5 节二分法比较）；误差平方递减：e_{k+1}/e_k² → |f″/(2f′)|；
求倒数不用除法；失效：arctan x 从远处出发发散、x³ − 2x + 2 从 0 出发循环、重根时退化为线性收敛。"""
import math

from bookout import out

zeta, wn = 0.6, 10.0
wd = wn * math.sqrt(1 - zeta * zeta)
c = zeta / math.sqrt(1 - zeta * zeta)
q = lambda t: 1 - math.exp(-zeta * wn * t) * (math.cos(wd * t) + c * math.sin(wd * t))
dq = lambda t: math.exp(-zeta * wn * t) * (wn ** 2 / wd) * math.sin(wd * t)        # q′(t)
f = lambda t: q(t) - 0.95
# 高精度的参考根（二分到底）
lo, hi = 0.0, math.pi / wd
for _ in range(200):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if f(m) < 0 else (lo, m)
root = (lo + hi) / 2
t = 0.2
rows, errs = [], []
for k in range(1, 7):
    t = t - f(t) / dq(t)
    errs.append(abs(t - root))
    rows.append(f"| {k} | {t:.15f} | {abs(t - root):.2e} |" if t != root else f"| {k} | {t:.15f} | 0 |")
out(newton_tab="\n".join(rows), t95=root, t0=0.2)
# 误差比 e_{k+1}/e_k² 与理论值 |f″/(2f′)|
h = 1e-5
d2 = (dq(root + h) - dq(root - h)) / (2 * h)
out(ratio2=errs[2] / errs[1] ** 2, ratio_th=abs(d2 / (2 * dq(root))))
# 二分法达到同样精度（1e−15 s）所需步数
out(bis_steps=math.ceil(math.log2((math.pi / wd) / 1e-15)))

# 求倒数 1/a 不用除法：x_{k+1} = x_k(2 − a x_k)
a, x = 7.0, 0.1
rec = []
for _ in range(6):
    x = x * (2 - a * x)
    rec.append(abs(x - 1 / a))
out(recip=", ".join(f"{e:.1e}" if e else "0" for e in rec))

# 失效 1：arctan x，x₀ = 1.5 发散，x₀ = 1.0 收敛
for x0 in (1.0, 1.5):
    x, xs = x0, []
    for _ in range(5):
        x = x - math.atan(x) * (1 + x * x)
        xs.append(x)
    out(**{f"atan_{str(x0).replace('.', '_')}": ", ".join(f"{v:.4g}" for v in xs)})
# 临界初值：|x₀| = x_c 时迭代在 ±x_c 之间来回，满足 2x = (1 + x²) arctan x
lo, hi = 1.0, 2.0
g = lambda x: (1 + x * x) * math.atan(x) - 2 * x
for _ in range(80):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if g(m) < 0 else (lo, m)
out(atan_crit=lo)
# 失效 2：x³ − 2x + 2，从 0 出发在 0 与 1 之间循环
x, xs = 0.0, []
for _ in range(6):
    x = x - (x ** 3 - 2 * x + 2) / (3 * x * x - 2)
    xs.append(x)
out(cycle=", ".join(f"{v:g}" for v in xs))
# 失效 3：重根 (x − 1)²，误差每步减半
x, es = 2.0, []
for _ in range(6):
    x = x - (x - 1) ** 2 / (2 * (x - 1))
    es.append(abs(x - 1))
out(double=", ".join(f"{e:g}" for e in es))
