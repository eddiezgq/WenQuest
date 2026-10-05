"""9.7 节：泰勒公式的应用——用 ln((1 + x)/(1 − x)) 快速算 ln 2；几个极限的数值核对，n(e − (1 + 1/n)ⁿ) → e/2；
AGV 里程计 Δy = vT(1 − cos ωT)/(ωT) 在 ωT 很小时：直接公式、改写公式与泰勒公式的相对误差，切换阈值的选择。"""
import math

from bookout import out

# ln 2 = 2(x + x³/3 + x⁵/5 + …)，x = 1/3；误差 ≤ 2x^{2n+1}/((2n+1)(1 − x²))
x, s, n = 1 / 3, 0.0, 0
while True:
    s += 2 * x ** (2 * n + 1) / (2 * n + 1)
    n += 1
    if 2 * x ** (2 * n + 1) / ((2 * n + 1) * (1 - x * x)) < 1e-16:
        break
out(ln2_terms=n, ln2_err=abs(s - math.log(2)))

# n(e − (1 + 1/n)ⁿ) → e/2；(1 + 1/n)ⁿ 用 exp(n·log1p(1/n)) 计算，避免 1 + 1/n 的舍入
rows = []
for k in (1, 2, 3, 4, 6):
    m = 10 ** k
    an = math.exp(m * math.log1p(1 / m))
    rows.append(f"| $10^{k}$ | {m * (math.e - an):.8f} |")
out(e_tab="\n".join(rows), e_half=math.e / 2, e_pred10=math.e / 2 - 11 * math.e / 240,
    e_10=10 * (math.e - math.exp(10 * math.log1p(0.1))))
# 72 法则的改进：n ≈ ln2/x + ln2/2，x = 8%
out(rule_pred=math.log(2) / 0.08 + math.log(2) / 2, rule_exact=math.log(2) / math.log1p(0.08))

# (eˣ − 1 − x)/x² → 1/2：直接计算与用 expm1 的计算
rows = []
for k in (2, 4, 6, 8):
    x = 10.0 ** -k
    d = (math.exp(x) - 1 - x) / x ** 2
    g = (math.expm1(x) - x) / x ** 2
    ser = 0.5 + x / 6 + x * x / 24
    rows.append(f"| $10^{{-{k}}}$ | {d:.10f} | {g:.10f} | {ser:.10f} |")
out(expm_tab="\n".join(rows))

# AGV：g(u) = (1 − cos u)/u，u = ωT。参考值用 2 sin²(u/2)/u（没有相消）
ref = lambda u: 2 * math.sin(u / 2) ** 2 / u
direct = lambda u: (1 - math.cos(u)) / u
series = lambda u: u / 2 - u ** 3 / 24 + u ** 5 / 720
fe = lambda e: f"{e:.1e}" if e else "0"
rows = []
for k in range(1, 9):
    u = 10.0 ** -k
    rows.append(f"| $10^{{-{k}}}$ | {fe(abs(direct(u) - ref(u)) / ref(u))} | {fe(abs(series(u) - ref(u)) / ref(u))} |")
out(agv_tab="\n".join(rows))
# 切换阈值：截断误差 u⁶/20160（相对）等于直接公式的舍入误差 2ε/u²
eps = 2.220446049250313e-16
u_sw = (40320 * eps) ** (1 / 8)
out(u_sw=u_sw, direct_at_sw=2 * eps / u_sw ** 2)
