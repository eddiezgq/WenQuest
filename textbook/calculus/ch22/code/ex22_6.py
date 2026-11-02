"""22.6 节：存在唯一性定理与皮卡迭代。
(1) y' = y、y(0) = 1 的皮卡迭代就是 e^x 的泰勒多项式，误差与定理给出的上界比较；
(2) y' = x² + y²、y(0) = 0：符号计算前几次迭代；定理保证的存在区间与数值求出的爆破点；
(3) 格朗沃尔不等式：UR5e 上臂初始角度差 0.001 rad 时，两条轨线的实际距离与上界 δe^{Lt}。"""
import math

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

from bookout import out

x, t = sp.symbols("x t")

# ---------- (1) y' = y ----------
rows = []
y = sp.Integer(1)
for n in range(1, 7):
    y = 1 + sp.integrate(y.subs(x, t), (t, 0, x))
    err = float(math.e - y.subs(x, 1))
    # 线性方程的误差估计：e_n = y − y_n 满足 e_n(x) = ∫₀ˣ e_{n−1}，|e_0| ≤ e − 1，所以 |e_n(1)| ≤ (e − 1)/n!
    bound = (math.e - 1) / math.factorial(n)
    rows.append(f"| {n} | {err:.2e} | {bound:.2e} |")
out(pc_exp_tab="\n".join(rows), pc_y3=sp.latex(sp.expand(sp.Integer(1) + x + x**2 / 2 + x**3 / 6)))

# ---------- (2) y' = x² + y² ----------
ys = [sp.Integer(0)]
for n in range(3):
    ys.append(sp.expand(sp.integrate((t ** 2 + ys[-1].subs(x, t) ** 2), (t, 0, x))))
out(pc_y1=sp.latex(ys[1]), pc_y2=sp.latex(ys[2]), pc_y3_terms=len(ys[3].as_ordered_terms()),
    pc_y3_lead=sp.latex(sp.Add(*sorted(ys[3].as_ordered_terms(), key=lambda e: sp.degree(e, x))[:3])))
# 矩形 |x| ≤ a、|y| ≤ b 上 M = a² + b²，保证的区间长度 h = min(a, b/M)；在 a、b 上求最大
# 对固定的 a，b/(a² + b²) 在 b = a 时最大，为 1/(2a)；min(a, 1/(2a)) 在 a = 1/√2 时最大
grid = max(min(a, b / (a * a + b * b)) for a in np.linspace(0.05, 2, 400) for b in np.linspace(0.05, 2, 400))
out(pc_h_best=1 / math.sqrt(2), pc_h_grid=grid, pc_h_11=min(1, 1 / 2))
ev = lambda xx, yy: yy[0] - 1e8
ev.terminal = True
s = solve_ivp(lambda xx, yy: [xx * xx + yy[0] ** 2], (0, 5), [0.0], events=ev, rtol=1e-12, atol=1e-12)
out(pc_blowup=float(s.t_events[0][0]))
# 第 3 次迭代在 x = 1 处与数值解比较
s1 = solve_ivp(lambda xx, yy: [xx * xx + yy[0] ** 2], (0, 1), [0.0], rtol=1e-12, atol=1e-14)
out(pc_true_1=float(s1.y[0, -1]), pc_true_05=float(solve_ivp(lambda xx, yy: [xx * xx + yy[0] ** 2], (0, 0.5), [0.0], rtol=1e-12, atol=1e-14).y[0, -1]))
out(**{f"pc_it{n}_1": float(ys[n].subs(x, 1)) for n in (1, 2, 3)}, **{f"pc_it{n}_05": float(ys[n].subs(x, 0.5)) for n in (1, 2, 3)})

# ---------- (3) 格朗沃尔 ----------
m, d, I, g = 8.393, 0.2125, 0.5129, 9.81
c = m * g * d / I
F = lambda tt, yy: [yy[1], -c * math.cos(yy[0])]
delta = 1e-3
te = [0.25, 0.5, 1.0, 2.0]
a = solve_ivp(F, (0, 2), [0.0, 0.0], t_eval=te, rtol=1e-12, atol=1e-12).y
b = solve_ivp(F, (0, 2), [delta, 0.0], t_eval=te, rtol=1e-12, atol=1e-12).y
dist = np.linalg.norm(a - b, axis=0)
out(gr_c=c, gr_L=max(1.0, c), gr_tab="\n".join(f"| {tt:g} | {dd:.2e} | {delta * math.exp(max(1.0, c) * tt):.1e} |" for tt, dd in zip(te, dist)))
