"""9.3 节的计算：

算例 9.3.1  测弹簧的劲度系数和功：送料机构的复位弹簧，每压缩 5 mm 读一次测力计（读数有 ±0.3 N 以内的误差），
            到 30 mm 为止。用最小二乘直线求 k，用梯形法由数据直接求外力做的功，与 ½kx² 比较（图 9.3.1）。
算例 9.3.2  轨道车的端部缓冲器：穿梭车（RGV）M = 300 kg，失控时以 0.50 m/s 撞上弹簧缓冲器，k = 3.0×10⁴ N/m。
            弹簧最多压缩多少？最大冲击力和减速度多大？要把最大减速度限制在 2.5 m/s²，k 应取多大、行程要多长？
            与同样减速度的恒力（液压）缓冲器比较（图 9.3.2）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 9.3.1：测弹簧
k_true = 1200.0                                                 # N/m（学生不知道；读数由它加误差生成）
xs = np.arange(0, 31, 5) / 1000.0                               # m
noise = np.array([0.0, 0.21, -0.17, 0.26, -0.24, 0.12, -0.08])  # N，测力计读数误差（固定，便于复算）
Fs = np.round(k_true * xs + noise, 1)                           # 读数，修约到 0.1 N
A_ = np.vstack([xs, np.ones_like(xs)]).T
(k_fit, b_fit), res, *_ = np.linalg.lstsq(A_, Fs, rcond=None)
n = len(xs)
s_res = math.sqrt(float(res[0]) / (n - 2))
u_k = s_res / math.sqrt(np.sum((xs - xs.mean()) ** 2))           # 斜率的标准不确定度（第 1.6 节）
W_trap = float(np.sum((Fs[1:] + Fs[:-1]) / 2 * np.diff(xs)))
W_half = 0.5 * k_fit * xs[-1] ** 2
out(x_mm=[round(x * 1000) for x in xs], F_read=Fs.tolist(), k_fit=k_fit, b_fit=b_fit, u_k=u_k, W_trap=W_trap, W_half=W_half,
    W_line=0.5 * k_fit * xs[-1] ** 2 + b_fit * xs[-1], xmax_mm=xs[-1] * 1000, Fmax_read=Fs[-1])

# ---- 算例 9.3.2：缓冲器
M, v, k = 300.0, 0.50, 3.0e4
K = 0.5 * M * v * v
x_max = v * math.sqrt(M / k)
assert abs(0.5 * k * x_max ** 2 - K) < 1e-9                       # 动能全部变成对弹簧做的功
F_max = k * x_max
a_max = F_max / M
a_lim = 2.5
k_lim = M * (a_lim / v) ** 2
x_lim = v * v / a_lim                                            # a_max x_max = v²
x_hyd = v * v / (2 * a_lim)                                      # 恒力缓冲：F x = ½Mv²，a = F/M
assert abs(v * math.sqrt(M / k_lim) - x_lim) < 1e-12
out(M=M, v=v, k=k, K=K, x_max=x_max, x_max_mm=x_max * 1000, F_max=F_max, a_max=a_max, a_max_g=a_max / g, a_lim=a_lim,
    k_lim=k_lim, x_lim_mm=x_lim * 1000, x_hyd_mm=x_hyd * 1000, F_hyd=M * a_lim, t_spring=math.pi / 2 * math.sqrt(M / k_lim),
    t_hyd=v / a_lim)

plt = style()
# ---- 图 9.3.1
fig, ax = plt.subplots(figsize=(4.8, 3.1))
xx = np.linspace(0, xs[-1], 50)
ax.fill_between(xx * 1000, k_fit * xx + b_fit, color=d.FIT, alpha=0.12, lw=0)
ax.plot(xx * 1000, k_fit * xx + b_fit, color=d.FIT, lw=1.8, label=T(f"拟合直线 k = {k_fit:.0f} N/m", f"fitted line k = {k_fit:.0f} N/m"))
ax.plot(xs * 1000, Fs, "o", color=d.DATA, ms=5, label=T("测力计读数", "force gauge readings"))
ax.text(17, 6, T(r"面积 $\approx \frac{1}{2}kx^2$" + "\n= 压缩弹簧做的功", r"area $\approx \frac{1}{2}kx^2$" + "\n= work to compress"), fontsize=9, color=d.FIT)
ax.set_xlabel(T("压缩量 x / mm", "compression x / mm")); ax.set_ylabel(T("外力 F / N", "applied force F / N"))
ax.set_xlim(0, 32); ax.set_ylim(0, 40); ax.legend(frameon=False, fontsize=8.5, loc="upper left"); d.spines(ax)
figure(fig, "fig9_3_1")

# ---- 图 9.3.2：弹簧缓冲与恒力缓冲
fig, ax = plt.subplots(figsize=(4.8, 3.1))
ax.fill_between([0, x_lim * 1000], [0, k_lim * x_lim], color=d.VA, alpha=0.18, lw=0)
ax.plot([0, x_lim * 1000], [0, k_lim * x_lim], color=d.VA, lw=2, label=T(f"弹簧 k = {k_lim:.0f} N/m", f"spring k = {k_lim:.0f} N/m"))
ax.fill_between([0, x_hyd * 1000], [M * a_lim, M * a_lim], color=d.VR, alpha=0.15, lw=0)
ax.plot([0, 0, x_hyd * 1000, x_hyd * 1000], [0, M * a_lim, M * a_lim, 0], color=d.VR, lw=2, label=T("恒力（液压）缓冲器", "constant-force (hydraulic) buffer"))
ax.text(x_lim * 1000 * 0.6, M * a_lim * 0.25, T(f"两块面积相等\n= ½Mv² = {K:.1f} J", f"equal areas\n= ½Mv² = {K:.1f} J"), fontsize=9)
ax.set_xlabel(T("压缩量 x / mm", "stroke x / mm")); ax.set_ylabel(T("缓冲力 / N", "buffer force / N"))
ax.set_xlim(0, x_lim * 1000 * 1.08); ax.set_ylim(0, M * a_lim * 1.25); ax.legend(frameon=False, fontsize=8.5, loc="upper right"); d.spines(ax)
figure(fig, "fig9_3_2")
