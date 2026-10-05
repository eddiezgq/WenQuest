"""9.6 节：常用函数的麦克劳林公式与误差——eˣ 要多少项（拉格朗日余项），交错求和 e^{−10} 的相消；
带区间约化的 sin 的多项式计算与库函数比较；单片机上的 e^{−Tₛ/τ}；ln(1 + x) 的部分和在 |x| > 1 时发散；
手臂接近伸直时腕心距离的二次近似。"""
import math
import random

from _traj import ur5e_links
from bookout import out

# eˣ：取到 xⁿ/n! 时，余项 ≤ e^{max(x,0)}|x|^{n+1}/(n+1)!；要求相对误差 < 10⁻¹⁶
rows = []
for x in (0.5, 1.0, 5.0, 10.0):
    n = 0
    while math.exp(max(x, 0)) * abs(x) ** (n + 1) / math.factorial(n + 1) >= 1e-16 * math.exp(x):
        n += 1
    rows.append(f"| {x:g} | {n} |")
out(exp_terms="\n".join(rows))
# e^{−10}：直接求交错和，与 1/e^{10} 比较
s, term = 0.0, 1.0
for k in range(1, 80):
    s += term
    term *= -10.0 / k
big = max(10.0 ** k / math.factorial(k) for k in range(30))
out(em10_direct=s, em10_true=math.exp(-10), em10_rel=abs(s - math.exp(-10)) / math.exp(-10), em10_big=big,
    em10_recip=1 / sum(10.0 ** k / math.factorial(k) for k in range(80)))

# sin：约化到 [−π/4, π/4]，再用 sin 或 cos 的泰勒多项式
n_sin = 0
while (math.pi / 4) ** (2 * n_sin + 3) / math.factorial(2 * n_sin + 3) >= 1.1e-16:
    n_sin += 1
deg = 2 * n_sin + 1
out(sin_deg=deg, sin_bound=(math.pi / 4) ** (deg + 2) / math.factorial(deg + 2))


def psin(x):
    return sum((-1) ** k * x ** (2 * k + 1) / math.factorial(2 * k + 1) for k in range(n_sin + 1))


def pcos(x):
    return sum((-1) ** k * x ** (2 * k) / math.factorial(2 * k) for k in range(n_sin + 2))


def mysin(x):
    k = round(x / (math.pi / 2))
    r = x - k * (math.pi / 2)
    return [psin(r), pcos(r), -psin(r), -pcos(r)][k % 4]


random.seed(96)
pts = [random.uniform(-100, 100) for _ in range(100000)]
out(sin_maxerr=max(abs(mysin(x) - math.sin(x)) for x in pts),
    sin_small=max(abs(psin(x) - math.sin(x)) for x in (random.uniform(-math.pi / 4, math.pi / 4) for _ in range(100000))),
    sin_noreduce=abs(sum((-1) ** k * 30.0 ** (2 * k + 1) / math.factorial(2 * k + 1) for k in range(60)) - math.sin(30.0)))

# 单片机：e^{−Tₛ/τ}，Tₛ = 1 ms，τ = 20 ms
x = 1 / 20
out(mcu_x=x, mcu_e1=abs(math.exp(-x) - (1 - x)), mcu_b1=x * x / 2, mcu_e2=abs(math.exp(-x) - (1 - x + x * x / 2)), mcu_b2=x ** 3 / 6)

# ln(1 + x) 的部分和
rows = []
for x in (0.5, 1.0, 1.5):
    cells = []
    for n in (5, 10, 20, 40):
        sn = sum((-1) ** (k + 1) * x ** k / k for k in range(1, n + 1))
        cells.append(f"{sn:.6f}")
    rows.append(f"| {x:g} | " + " | ".join(cells) + f" | {math.log1p(x):.6f} |")
out(ln_tab="\n".join(rows))

# 手臂接近伸直：r(θ) = √(l₁² + l₂² + 2l₁l₂cos θ) ≈ (l₁ + l₂) − l₁l₂θ²/(2(l₁ + l₂))
l1, l2 = ur5e_links()
rows = []
for deg in (5, 10, 20, 40):
    t = math.radians(deg)
    exact = math.sqrt(l1 * l1 + l2 * l2 + 2 * l1 * l2 * math.cos(t))
    appr = (l1 + l2) - l1 * l2 * t * t / (2 * (l1 + l2))
    rows.append(f"| {deg} | {exact * 1000:.3f} | {appr * 1000:.3f} | {abs(exact - appr) * 1000:.3f} |")
out(reach_tab="\n".join(rows), reach_coef=l1 * l2 / (2 * (l1 + l2)) * 1000)
