"""14.2 节：三角函数的积分——关节正弦摆动 θ = A sin Ωt 的功率：惯性部分一个周期平均为零，黏性摩擦部分平均为 bA²Ω²/2；
三角函数系的正交性 ∫₀^{2π} sin mx sin nx dx。"""
import math

from bookout import out

J, b, A, f = 0.5, 0.2, 0.5, 1.0          # kg·m²，N·m·s/rad，rad，Hz
W = 2 * math.pi * f
T = 1 / f
n = 100000
h = T / n
ts = [(k + 0.5) * h for k in range(n)]
om = lambda t: A * W * math.cos(W * t)
al = lambda t: -A * W * W * math.sin(W * t)
P_in = sum(J * al(t) * om(t) for t in ts) * h / T
P_fr = sum(b * om(t) ** 2 for t in ts) * h / T
peak = max(abs((J * al(t) + b * om(t)) * om(t)) for t in ts)
out(J=J, b=b, A=A, f=f, P_in=P_in, P_fr=P_fr, P_fr_x=b * A * A * W * W / 2, P_peak=peak, inertia_peak=J * A * A * W ** 3 / 2)


def ortho(m, k):
    hh = 2 * math.pi / 20000
    return sum(math.sin(m * (j + 0.5) * hh) * math.sin(k * (j + 0.5) * hh) for j in range(20000)) * hh


out(orth_tab="\n".join(f"| {m} | " + " | ".join(f"{ortho(m, k):.4f}" for k in (1, 2, 3)) + " |" for m in (1, 2, 3)))
