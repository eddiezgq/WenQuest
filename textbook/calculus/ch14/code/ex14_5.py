"""14.5 节：可化为有理函数的积分——转速有波动的关节：ω(θ) = ω₀(1 + ε cos θ)，转一圈的时间 T = ∫₀^{2π} dθ/ω
= 2π/(ω₀√(1 − ε²))（万能代换），对时间平均的转速 ω₀√(1 − ε²) 低于对角度平均的 ω₀；数值核对。"""
import math

from bookout import out

w0 = 2 * math.pi        # rad/s（1 转/秒）


def T_num(eps, n=200000):
    h = 2 * math.pi / n
    return sum(1 / (w0 * (1 + eps * math.cos((k + 0.5) * h))) for k in range(n)) * h


rows = []
for eps in (0.05, 0.1, 0.3, 0.5):
    Tf = 2 * math.pi / (w0 * math.sqrt(1 - eps * eps))
    rows.append(f"| {eps:g} | {Tf:.6f} | {T_num(eps):.6f} | {(Tf - 1) * 100:.2f} |")
out(ripple_tab="\n".join(rows))
n = 200000
h = 2 * math.pi / n
out(cos2=sum(1 / (2 + math.cos((k + 0.5) * h)) for k in range(n)) * h, cos2x=2 * math.pi / math.sqrt(3))
# 时间平均与角度平均的相对差（ε = 0.1）
out(ripple_diff=(1 - math.sqrt(1 - 0.1 ** 2)) * 100)
