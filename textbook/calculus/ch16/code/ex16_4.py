"""16.4 节：平面曲线的弧长——单位圆内接正多边形的周长（弧长定义为内接折线长度的上确界）；悬链线电缆的长度 2a sinh(L/a)；
AGV 换道路径（横移 1 m、长 4 m）的长度；摆线一拱的长度 8r；椭圆的周长（椭圆积分）与拉马努金近似。"""
import math

from scipy import integrate

from _quad import gauss
from bookout import out

out(poly_tab="\n".join(f"| {n} | {n * math.sin(math.pi / n):.8f} | {math.pi - n * math.sin(math.pi / n):.2e} |" for n in (6, 12, 24, 96, 192, 3072)))
# 一般曲线：内接折线（n 段）长度随 n 的变化，y = x²，0 ≤ x ≤ 1
f = lambda x: x * x
Lp_ex = integrate.quad(lambda x: math.sqrt(1 + 4 * x * x), 0, 1)[0]
def poly_len(n):
    return sum(math.hypot(1 / n, f((k + 1) / n) - f(k / n)) for k in range(n))
out(par_L=Lp_ex, par_L_ex=math.sqrt(5) / 2 + math.asinh(2) / 4,
    par_tab="\n".join(f"| {n} | {poly_len(n):.8f} | {Lp_ex - poly_len(n):.2e} |" for n in (1, 2, 4, 8, 16, 64, 256)))
# 悬链线：a = 25 m，立柱在 ±10 m
a, L = 25.0, 10.0
cat_num = integrate.quad(lambda x: math.sqrt(1 + math.sinh(x / a) ** 2), -L, L)[0]
out(cat_a=a, cat_L=L, cat_num=cat_num, cat_ex=2 * a * math.sinh(L / a), cat_extra_mm=(cat_num - 2 * L) * 1000)
# AGV 换道：横移 d = 1 m，长 Lx = 4 m
d, Lx = 1.0, 4.0
paths = {
    "cubic": (lambda u: d * (6 * u - 6 * u * u)),
    "cos": (lambda u: d * math.pi / 2 * math.sin(math.pi * u)),
    "quintic": (lambda u: d * (30 * u * u - 60 * u ** 3 + 30 * u ** 4)),
}
names = {"cubic": ("三次多项式", "cubic"), "cos": ("余弦", "cosine"), "quintic": ("五次多项式", "quintic")}
from bookout import T
rows = []
for k, dydu in paths.items():
    Lk = integrate.quad(lambda x: math.sqrt(1 + (dydu(x / Lx) / Lx) ** 2), 0, Lx)[0]
    rows.append(f"| {T(*names[k])} | {Lk:.4f} | {(Lk - Lx) * 1000:.0f} | {(Lk - math.hypot(Lx, d)) * 1000:.0f} |")
out(lane_tab="\n".join(rows), diag=math.hypot(Lx, d), diag_extra=(math.hypot(Lx, d) - Lx) * 1000)
# 摆线一拱：x = r(t − sin t)，y = r(1 − cos t)，r = 0.075 m
r = 0.075
cyc = integrate.quad(lambda t: r * math.sqrt((1 - math.cos(t)) ** 2 + math.sin(t) ** 2), 0, 2 * math.pi)[0]
out(cyc_L=cyc, cyc_8r=8 * r, cyc_circ=2 * math.pi * r)
# 椭圆 a = 2，b = 1 的周长
A, B = 2.0, 1.0
e2 = 1 - B * B / (A * A)
ell = 4 * A * sum(gauss(lambda p: math.sqrt(1 - e2 * math.sin(p) ** 2), k * math.pi / 16, (k + 1) * math.pi / 16, 10) for k in range(8))
ram = math.pi * (3 * (A + B) - math.sqrt((3 * A + B) * (A + 3 * B)))     # 拉马努金的第一个近似（14.7 节习题 14.7.7）
out(ell=ell, ram=ram, ram_err=abs(ram - ell) / ell)
