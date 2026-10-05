"""7.1 节的计算：

图 7.1.1    用拉力计水平拉一个放在台面上的零件盒（m = 2.0 kg，μ_s = 0.45，μ_k = 0.35）：拉力从零慢慢增大，静摩擦力随之增大，
            达到最大静摩擦力 μ_s F_N 时开始滑动，之后摩擦力降为动摩擦力 μ_k F_N。
算例 7.1.1  斜面测摩擦因数：把零件盒放在可调倾角的斜面上，慢慢抬高，刚开始滑动时 θ_c = 24°，μ_s = tan θ_c；
            把斜面固定在 35°，测得零件盒由静止滑下 0.60 m 用时 0.65 s，求 μ_k。
算例 7.1.2  二指夹爪靠摩擦夹住零件：零件 m = 0.80 kg，指垫与零件之间 μ_s = 0.50。机械臂把零件竖直向上以 4.0 m/s² 加速提起，
            同时水平方向有 3.0 m/s² 的加速度。两指各需多大的夹紧力？取安全系数 2.0（图 7.1.2）。
算例 7.1.3  AGV 的牵引力：总质量 500 kg，驱动轮承担 60% 的重量，轮胎与地面 μ_s = 0.60。最大加速度是多少？
            滚动阻力系数 C_rr = 0.015 时，以 1.0 m/s 匀速行驶要克服多大的滚动阻力、消耗多大功率？
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 图 7.1.1 的数据
m0, mus0, muk0 = 2.0, 0.45, 0.35
FN0 = m0 * g
fs_max, fk = mus0 * FN0, muk0 * FN0
out(m0=m0, mus0=mus0, muk0=muk0, fs_max=fs_max, fk=fk)

# ---- 算例 7.1.1
thc = 24.0
mus = math.tan(math.radians(thc))
th2, L, tL = 35.0, 0.60, 0.65
a = 2 * L / tL ** 2
muk = (g * math.sin(math.radians(th2)) - a) / (g * math.cos(math.radians(th2)))
# 不确定度：角度 ±0.5°，时间 ±0.02 s（秒表），距离 ±0.002 m —— 用数值偏导传递
u_thc = math.radians(0.5) / math.cos(math.radians(thc)) ** 2
def muk_of(L_, t_, th_):
    a_ = 2 * L_ / t_ ** 2; return (g * math.sin(math.radians(th_)) - a_) / (g * math.cos(math.radians(th_)))
parts = [(muk_of(L + 0.002, tL, th2) - muk_of(L - 0.002, tL, th2)) / 2,
         (muk_of(L, tL + 0.02, th2) - muk_of(L, tL - 0.02, th2)) / 2,
         (muk_of(L, tL, th2 + 0.5) - muk_of(L, tL, th2 - 0.5)) / 2]
u_muk = math.sqrt(sum(p * p for p in parts))
out(thc=thc, mus=mus, u_mus=u_thc, th2=th2, L=L, tL=tL, a_slide=a, muk=muk, u_muk=u_muk, u_t_part=abs(parts[1]))

# ---- 算例 7.1.2
m, mu, az, ax, S = 0.80, 0.50, 4.0, 3.0, 2.0
Freq = m * math.hypot(g + az, ax)          # 两指的摩擦力合起来要提供的力的大小（竖直 m(g + a_z)，水平 m a_x）
FN_min = Freq / (2 * mu)
out(m=m, mu=mu, az=az, ax=ax, S=S, Fneed=Freq, FN_min=FN_min, FN=S * FN_min, FN_static=m * g / (2 * mu))

# ---- 算例 7.1.3
M, share, mu_w = 500.0, 0.60, 0.60
a_max = mu_w * share * g
Crr, v_run = 0.015, 1.0
F_roll = Crr * M * g
out(M=M, share=share, mu_w=mu_w, a_drive=a_max, F_drive=mu_w * share * M * g, Crr=Crr, F_roll=F_roll, P_roll=F_roll * v_run,
    a_net=a_max - Crr * g)

plt = style()
# ---- 图 7.1.1
fig, ax = plt.subplots(figsize=(4.8, 3.1))
Fa = np.linspace(0, 14, 400)
ax.plot(Fa[Fa <= fs_max], Fa[Fa <= fs_max], color=d.VA, lw=2.2)
ax.plot([fs_max, fs_max], [fs_max, fk], color=d.VA, lw=1, ls=":")
ax.plot(Fa[Fa >= fs_max], np.full((Fa >= fs_max).sum(), fk), color=d.VR, lw=2.2)
ax.plot(Fa, Fa, color=d.MUTED, lw=0.8, ls="--")
ax.text(1.0, 6.0, T("静摩擦力 = 拉力\n（零件不动）", "static friction = pull\n(at rest)"), color=d.VA, fontsize=8.5)
ax.text(fs_max + 0.4, fk - 1.3, T(r"动摩擦力 $\mu_\mathrm{k}F_\mathrm{N}$" + "\n（滑动）", r"kinetic friction $\mu_\mathrm{k}F_\mathrm{N}$" + "\n(sliding)"), color=d.VR, fontsize=8.5)
ax.annotate(T(r"最大静摩擦力 $\mu_\mathrm{s}F_\mathrm{N}$", r"maximum static friction $\mu_\mathrm{s}F_\mathrm{N}$"), xy=(fs_max, fs_max), xytext=(fs_max + 1.2, fs_max + 1.6), fontsize=8.5,
            arrowprops=dict(arrowstyle="->", color=d.MUTED, lw=0.8))
ax.set_xlabel(T("水平拉力 / N", "horizontal pull / N")); ax.set_ylabel(T("摩擦力的大小 / N", "friction / N")); ax.set_xlim(0, 14); ax.set_ylim(0, 12); d.spines(ax)
figure(fig, "fig7_1_1")

# ---- 图 7.1.2：夹紧力与加速度
fig, ax = plt.subplots(figsize=(4.8, 3.1))
azs = np.linspace(-5, 10, 300)
for axv, col in ((0.0, d.VA), (3.0, d.VR), (6.0, d.VB)):
    ax.plot(azs, S * m * np.hypot(g + azs, axv) / (2 * mu), color=col, lw=2, label=T(f"水平加速度 {axv:.0f} m/s²", f"horizontal {axv:.0f} m/s²"))
ax.plot(az, S * FN_min, "o", color=d.VR)
ax.set_xlabel(T(r"竖直加速度 $a_z$ / (m/s²)（向上为正）", r"vertical acceleration $a_z$ / (m/s²) (up +)")); ax.set_ylabel(T("每指所需夹紧力 / N（安全系数 2）", "grip per finger / N (safety factor 2)"))
ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
figure(fig, "fig7_1_2")
