"""第 2 章部分习题答案中的数值（02-99.md“部分习题答案与提示”引用）。与正文程序用同一个模型。"""
import math

from bookout import out
from mos import (Cd, Cg, P, Wmin, cin, gamma_self, le_g, le_p, noise_margins, path_delay, r_ratio, tau)

r = r_ratio()
gam = gamma_self()
Cinv = cin(Wmin, r * Wmin)

# 2.2.1
out(a221_nand4=le_g("nand", 4), a221_nor4=le_g("nor", 4), a221_nor4_wp=4 * r * Wmin)

# 2.3.2  二输入与非门驱动 4 个同样的门
for k in ("nand", "nor"):
    g = le_g(k, 2)
    out(**{f"a232_{k}_f": 4 * g, f"a232_{k}_d": 4 * g + le_p(k, 2)})

# 2.3.3  译码器负载加倍
q = P["problems"]["p23"]
H2 = 2 * q["Cout_units"] / q["Cin_units"]
gn, pn, pi = le_g("nand", q["n_addr"]), le_p("nand", q["n_addr"]), le_p("inv", 1)
D = {N: path_delay([gn] + [1.0] * (N - 1), [pn] + [pi] * (N - 1), q["branch"], H2)[0] for N in (2, 3, 4, 5)}
best = min(D, key=D.get)
D_old = path_delay([gn, 1.0, 1.0], [pn, pi, pi], q["branch"], q["Cout_units"] / q["Cin_units"])[0]
out(a233_F=gn * q["branch"] * H2, a233_best=best, a233_D=D[best], a233_D3=D[3], a233_D4=D[4], a233_inc_ps=(D[best] - D_old) * tau() * 1e12)

# 2.3.5  第 1 章反相器链：F = CL / Cinv，D(N) = N·F^(1/N) + N·γ
CL = P["problems"]["p14"]["CL"]
F = CL / Cinv
Dn = {N: N * F ** (1 / N) + N * gam for N in range(1, 11)}
nb = min(Dn, key=Dn.get)
out(a235_F=F, a235_N=nb, a235_D=Dn[nb], a235_ps=Dn[nb] * tau() * 1e12)

# 2.4.2  50 个伪 NMOS 门，2 % 输出为低
I = P["gates_sim"]["pseudo_nmos"][2]["I"]
out(a242_mw=50 * 0.02 * I * P["VDD"] * 1e3)

# 2.4.4  “弱 1”驱动对称反相器
nm = noise_margins(Wmin, r * Wmin)
v1 = P["gates_sim"]["pass"]["nmos"]
out(a244_v1=v1, a244_vih=nm["VIH"], a244_nmh=v1 - nm["VIH"])

# 2.5.2  无底管的动态门
out(a252_g=Wmin * Cg / Cinv)

# 2.5.4  四输入：动态或 + 反相器 vs 静态或非 + 反相器，H = 4
g_dyn = 2 * Wmin * Cg / Cinv
p_dyn4 = (4 * 2 * Wmin + r * Wmin + Wmin) / ((1 + r) * Wmin) * gam


def best2(gs, ps, H=4.0):
    return 2 * (math.prod(gs) * H) ** 0.5 + sum(ps)


out(a254_dyn=best2([g_dyn, 1.0], [p_dyn4, pi]), a254_static=best2([le_g("nor", 4), 1.0], [le_p("nor", 4), pi]))

# 2.3.4  3 级结构中与非门尺寸取最优值的 x 倍（其余不变）
F3 = gn * q["branch"] * q["Cout_units"] / q["Cin_units"]
f3 = F3 ** (1 / 3)
P3 = pn + 2 * pi
Dopt = 3 * f3 + P3


def d_scaled(x):
    return f3 * (x + 1 / x + 1) + P3        # 第 1 级努力乘 x，第 2 级除以 x，第 3 级不变


out(a234_half=(d_scaled(0.5) / Dopt - 1) * 100, a234_20=(d_scaled(1.2) / Dopt - 1) * 100)
