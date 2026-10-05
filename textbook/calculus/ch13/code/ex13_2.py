"""13.2 节：微积分基本定理——用牛顿–莱布尼茨公式 F(b) − F(a) 与数值积分（中点和，n = 100）比较；
回到第 12 章：AGV 一趟能耗的准确值（分段求原函数）。"""
import math

from _agv import ETA, G, M, MU, P0, T
from bookout import out


def mid(f, a, b, n=100):
    h = (b - a) / n
    return sum(f(a + (k + 0.5) * h) for k in range(n)) * h


cases = [
    ("$\\int_0^1x^2\\,dx$", lambda x: x * x, 0, 1, 1 / 3),
    ("$\\int_0^\\pi\\sin x\\,dx$", math.sin, 0, math.pi, 2.0),
    ("$\\int_1^2\\frac{dx}{x}$", lambda x: 1 / x, 1, 2, math.log(2)),
    ("$\\int_0^1e^x\\,dx$", math.exp, 0, 1, math.e - 1),
    ("$\\int_0^1\\frac{dx}{1+x^2}$", lambda x: 1 / (1 + x * x), 0, 1, math.pi / 4),
]
rows = []
for name, f, a, b, ex in cases:
    m = mid(f, a, b)
    rows.append(f"| {name} | {ex:.10f} | {m:.10f} | {abs(m - ex):.1e} |")
out(ftc_tab="\n".join(rows), ln2=math.log(2), pi4=math.pi / 4)

# 能耗的准确值：加速段 [0, TA] 上 v = A t、a = A；匀速段 v = V、a = 0；减速段机械功率 (−MA + μMg)v < 0，只计 P0
A, V = 0.5, 1.2
TA = V / A
TC = T - 2 * TA
F1 = M * A + MU * M * G                       # 加速段牵引力
E_acc = F1 * A * TA ** 2 / 2 / ETA            # ∫₀^{TA} F1·A t dt / η
E_cru = MU * M * G * V * TC / ETA
E_dec = 0.0
assert -M * A + MU * M * G < 0
E = E_acc + E_cru + E_dec + P0 * T
out(E_acc=E_acc, E_cru=E_cru, E_P0=P0 * T, E_exact=E)
