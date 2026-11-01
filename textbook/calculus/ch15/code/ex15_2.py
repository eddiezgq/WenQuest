"""15.2 节：误差估计与龙贝格积分——∫₀¹ e^{−x²} dx 的梯形、辛普森误差随 n 的变化（阶 2 与 4）及误差公式的核对；
龙贝格表；周期函数的梯形公式（转速波动的关节转一圈的时间，14.5 节）误差按指数衰减。"""
import math

from _quad import romberg, simpson, trap
from bookout import out

f = lambda x: math.exp(-x * x)
ex = 0.5 * math.sqrt(math.pi) * math.erf(1.0)
rows = []
for n in (2, 4, 8, 16, 32, 64):
    et, es = trap(f, 0, 1, n) - ex, simpson(f, 0, 1, n) - ex
    rows.append(f"| {n} | {et:.3e} | {et * n * n:.5f} | {es:.3e} | {es * n ** 4:.5f} |")
# 渐近常数（近似值 − 准确值）× nᵖ：梯形 (f'(1) − f'(0))/12，辛普森 (f'''(1) − f'''(0))/180（[0, 1] 上 h = 1/n）
fp = lambda x: -2 * x * math.exp(-x * x)
fppp = lambda x: (-8 * x ** 3 + 12 * x) * math.exp(-x * x)
out(ex=ex, err_tab="\n".join(rows), ct=(fp(1) - fp(0)) / 12, cs=(fppp(1) - fppp(0)) / 180)
R = romberg(f, 0, 1, 5)
rows = []
for k, row in enumerate(R):
    cells = [f"{v:.10f}" for v in row] + [""] * (4 - k)
    rows.append(f"| {2 ** k} | " + " | ".join(cells) + " |")
out(romb_tab="\n".join(rows), romb_err=R[4][4] - ex, romb_evals=2 ** 4 + 1,
    simp17=simpson(f, 0, 1, 16) - ex)
# 周期函数：∫₀^{2π} dθ/(1 + 0.5 cos θ) = 2π/√0.75
g = lambda t: 1 / (1 + 0.5 * math.cos(t))
exg = 2 * math.pi / math.sqrt(0.75)
out(per_tab="\n".join(f"| {n} | {trap(g, 0, 2 * math.pi, n) - exg:.2e} | {simpson(g, 0, 2 * math.pi, n) - exg:.2e} |" for n in (4, 8, 16, 32)))
