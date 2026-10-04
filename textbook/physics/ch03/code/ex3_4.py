"""3.4 节的计算：

算例 3.4.1  交流电机绕组中的电流 i(t) = I_m sin ωt，I_m = 10 A。求一个周期内 i² 的平均值和电流的方均根值（有效值）：
            用 sin² = (1 − cos 2ωt)/2 化简后积分（第 36 章交流电路要用）。
算例 3.4.2  1.5 节的均匀分布：误差在 ±a 内均匀分布时，方差 = ∫ x² p(x) dx，p(x) = 1/(2a)。积分得 a²/3，核对式 (1.5.4)。
算例 3.4.3  数值积分：用梯形法和辛普森法计算 ∫₀^π sin t dt = 2，看误差怎样随分段数 n 减小（图 3.4.1）：梯形法 ∝ 1/n²，
            辛普森法 ∝ 1/n⁴。
算例 3.4.4  矢量函数的积分：四旋翼的速度 v(t) = (2.0, 1.5 t, 3.0 − 1.0 t) m/s，从 t = 0 到 4 s 的位移是对每个分量分别积分
            （图 3.4.2）。
"""
import math

import numpy as np
from scipy.integrate import quad, simpson

from bookout import T, figure, out, style
import _draw as d

# ---- 算例 3.4.1
Im = 10.0
w = 2 * math.pi * 50
Tp = 2 * math.pi / w
mean_sq = quad(lambda t: (Im * math.sin(w * t)) ** 2, 0, Tp)[0] / Tp
assert abs(mean_sq - Im ** 2 / 2) < 1e-9
out(Im=Im, mean_sq=mean_sq, rms=math.sqrt(mean_sq), ratio=1 / math.sqrt(2))

# ---- 算例 3.4.2
a = 0.03
var = quad(lambda x: x * x / (2 * a), -a, a)[0]
assert abs(var - a * a / 3) < 1e-15
out(a_mm=a, var_mm2=var, u_mm=math.sqrt(var))

# ---- 算例 3.4.3
ns = np.array([2, 4, 8, 16, 32, 64])
et, es = [], []
for n in ns:
    x = np.linspace(0, math.pi, n + 1)
    et.append(abs(np.trapezoid(np.sin(x), x) - 2))
    es.append(abs(simpson(np.sin(x), x=x) - 2))
et, es = np.array(et), np.array(es)
pt = np.polyfit(np.log(ns[2:]), np.log(et[2:]), 1)[0]
ps = np.polyfit(np.log(ns[2:]), np.log(es[2:]), 1)[0]
out(et4=float(et[1]), et8=float(et[2]), es4=float(es[1]), es8=float(es[2]), pt=pt, ps=ps, et64=float(et[-1]), es64=float(es[-1]))

# ---- 算例 3.4.4
vel = lambda t: np.array([2.0, 1.5 * t, 3.0 - 1.0 * t])
T4 = 4.0
disp = np.array([quad(lambda t, k=k: vel(t)[k], 0, T4)[0] for k in range(3)])
assert np.allclose(disp, [8.0, 12.0, 4.0])
out(dx=disp[0], dy=disp[1], dz=disp[2], dmag=float(np.linalg.norm(disp)),
    zmax=quad(lambda t: 3.0 - t, 0, 3.0)[0])

plt = style()
# ---- 图 3.4.1：数值积分的误差
fig, ax = plt.subplots(figsize=(4.8, 3.3))
ax.loglog(ns, et, "o-", color=d.VA, label=T("梯形法", "trapezoid"))
ax.loglog(ns, es, "s-", color=d.VB, label=T("辛普森法", "Simpson"))
ax.loglog(ns, et[0] * (ns / ns[0]) ** -2.0, color=d.VA, lw=0.8, ls=":")
ax.loglog(ns, es[0] * (ns / ns[0]) ** -4.0, color=d.VB, lw=0.8, ls=":")
ax.text(20, 1.5e-2, r"$\propto n^{-2}$", color=d.VA); ax.text(12, 3e-6, r"$\propto n^{-4}$", color=d.VB)
ax.set_xlabel(T("分段数 n", "number of strips n")); ax.set_ylabel(T("误差", "error"))
ax.legend(frameon=False, fontsize=9); d.spines(ax)
figure(fig, "fig3_4_1")

# ---- 图 3.4.2：四旋翼的速度分量与轨迹
fig = plt.figure(figsize=(7.2, 3.0))
ax = fig.add_subplot(1, 2, 1)
tt = np.linspace(0, T4, 200)
V = np.array([vel(t) for t in tt])
for k, c, n in ((0, d.X_, "$v_x$"), (1, d.Y_, "$v_y$"), (2, d.Z_, "$v_z$")):
    ax.plot(tt, V[:, k], color=c, lw=1.8, label=n)
ax.axhline(0, color=d.MUTED, lw=0.8)
ax.set_xlabel("t / s"); ax.set_ylabel("v / (m/s)"); ax.legend(frameon=False, fontsize=9, ncol=3); d.spines(ax)
ax = fig.add_subplot(1, 2, 2, projection="3d")
P = np.array([[2.0 * t, 0.75 * t * t, 3.0 * t - 0.5 * t * t] for t in tt])
ax.plot(P[:, 0], P[:, 1], P[:, 2], color=d.VR, lw=2)
ax.quiver(0, 0, 0, *disp, color=d.INK, lw=1.4, arrow_length_ratio=0.08)
ax.text(*(disp * 0.5 + np.array([0, -2, 1.0])), r"$\Delta\boldsymbol{r}$", fontsize=11)
ax.set_xlabel("x / m", fontsize=8); ax.set_ylabel("y / m", fontsize=8); ax.set_zlabel("z / m", fontsize=8)
ax.tick_params(labelsize=7); ax.view_init(elev=22, azim=-60)
figure(fig, "fig3_4_2")
