"""15.3 节：高斯求积——2～5 点高斯–勒让德的节点与权；n 点公式对 2n − 1 次多项式准确；
变截面连杆的转动惯量（被积函数是三次多项式，2 点高斯准确）；同样的求值次数下高斯与辛普森的误差比较。"""
import math

from _quad import gauss, gauss_nodes, simpson
from bookout import out

rows = []
for n in (2, 3, 4, 5):
    xs, ws = gauss_nodes(n)
    pairs = sorted(zip(xs, ws))
    rows.append(f"| {n} | " + "，".join(f"{x:+.6f}" for x, _ in pairs) + " | " + "，".join(f"{w:.6f}" for _, w in pairs) + " |")
out(node_tab="\n".join(rows))
# 准确的最高次数
deg = {}
for n in (2, 3, 4):
    k = 0
    while True:
        exact = 0.0 if k % 2 else 2 / (k + 1)
        if abs(gauss(lambda x: x ** k, -1, 1, n) - exact) > 1e-12:
            break
        k += 1
    deg[n] = k - 1
out(deg2=deg[2], deg3=deg[3], deg4=deg[4])
# 变截面铝连杆：长 L，截面积 A(x) = A0(1 − 0.5x/L)，绕根部 x = 0 的转动惯量 ∫ρA(x)x² dx
rho, L, A0 = 2700.0, 0.5, 4e-4
f = lambda x: rho * A0 * (1 - 0.5 * x / L) * x * x
I_ex = rho * A0 * (L ** 3 / 3 - 0.5 / L * L ** 4 / 4)
m_link = rho * A0 * (L - 0.25 * L)
out(I_ex=I_ex, I_g2=gauss(f, 0, L, 2), m_link=m_link, taper_gain=(m_link * L * L / 3 / I_ex - 1) * 100)
# 同样的求值次数：高斯 n 点 vs 辛普森 n 个点（n − 1 段，n 为奇数）
g = lambda x: math.exp(-x * x)
ex = 0.5 * math.sqrt(math.pi) * math.erf(1.0)
rows = []
for n in (3, 5, 7, 9):
    rows.append(f"| {n} | {simpson(g, 0, 1, n - 1) - ex:.2e} | {gauss(g, 0, 1, n) - ex:.2e} |")
out(cmp_tab="\n".join(rows))
