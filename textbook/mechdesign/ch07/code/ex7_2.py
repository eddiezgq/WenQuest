"""7.2 载荷的种类：静载、动载、冲击、交变，各取一个数字工厂或机器人里的例子，画出时间历程，求平均值、幅值和应力比 R
（算例 7.2.1，图 7.2.1）。
(a) 静载：UR5e 手臂伸直水平、持 5 kg 静止，肩关节的重力矩（程序 7.1.1 的模型）；
(b) 动载：同一手臂从 θ = −30° 转到 +30°（梯形速度，加速、匀速、减速各 1/3），肩关节力矩 = 重力矩 + 惯性力矩 J·θ̈（集中质量，
    不计连杆绕自身质心的转动惯量和科氏力——单关节转动时科氏力为零）；
(c) 冲击：跑合试验台“工况模拟”段第一次起动的输出转矩（数字工厂仿真车间的记录）；
(d) 交变：WQR-105 输出轴齿轮位表面一点的弯曲应力——弯矩方向不变，轴在转，这一点的应力正弦变化（额定转矩、输出转速）；
    支反力用数字孪生的简化布置（A 版轴段，跨距较短），数值与第 33 章 B 版不同。"""
import math

import numpy as np

import _ch7 as H
from bookout import T, figure, out, style

arm = H.ur5e_arm(5.0)
M0 = sum(m * H.G * x for _, m, x in arm)
J = sum(m * x * x for _, m, x in arm)                        # 对肩关节轴的转动惯量（集中质量）kg·m²
# (b) 梯形速度：转角 60°、时间 1.2 s，加速、匀速、减速各 0.4 s
TH0, TH1, TM = math.radians(-30), math.radians(30), 1.2
ta = TM / 3
w_max = (TH1 - TH0) / (TM - ta)
alpha = w_max / ta
t2 = np.linspace(0, TM, 601)


def motion(t):
    if t < ta:
        return TH0 + 0.5 * alpha * t * t, alpha
    if t < TM - ta:
        return TH0 + 0.5 * alpha * ta * ta + w_max * (t - ta), 0.0
    tr = TM - t
    return TH1 - 0.5 * alpha * tr * tr, -alpha


tau2 = np.array([M0 * math.cos(motion(t)[0]) + J * motion(t)[1] for t in t2])
grav2 = np.array([M0 * math.cos(motion(t)[0]) for t in t2])
# (c) 冲击
tb, yb, rec = H.bench()
tb, yb = np.array(tb), np.array(yb)
first = tb < 25
peak_c = yb[first].max()
run_c = yb[(tb > 5) & (tb < 22)].mean()
k_start = peak_c / run_c
t_rise = tb[first][np.argmax(yb[first])]
# (d) 交变：齿轮位表面一点
Mb, Tq, d = H.shaft_out_gear_seat()
Wb = math.pi * d ** 3 / 32                                    # mm³
sig_a = Mb * 1000 / Wb                                        # MPa
tau_m = Tq * 1000 / (2 * Wb)
n_out = H.TM.speeds()["out"]
f_rot = n_out / 60
t4 = np.linspace(0, 3 / f_rot, 600)
sig4 = sig_a * np.sin(2 * math.pi * f_rot * t4)


def stats(y):
    mx, mn = float(np.max(y)), float(np.min(y))
    return (mx + mn) / 2, (mx - mn) / 2, (mn / mx if mx != 0 else float("nan"))


S2, S4 = stats(tau2), stats(sig4)

plt = style()
fig, axs = plt.subplots(2, 2, figsize=(7.6, 4.8))
a = axs[0, 0]
ts = np.linspace(0, 5, 50)
a.plot(ts, np.full_like(ts, M0), color="#1f77b4", lw=1.4)
a.set_ylim(0, M0 * 1.4)
a.set_xlabel(T("时间 / s", "Time / s"), fontsize=7)
a.set_ylabel(T("肩关节力矩 / N·m", "Shoulder torque / N·m"), fontsize=7)
a.set_title(T("(a) 静载：手臂水平静止，持 5 kg", "(a) Static: arm horizontal, holding 5 kg"), fontsize=7.4)
a = axs[0, 1]
a.plot(t2, tau2, color="#1f77b4", lw=1.4, label=T("总力矩", "total"))
a.plot(t2, grav2, color=H.MUTED, lw=0.9, ls="--", label=T("其中重力矩", "gravity part"))
a.set_xlabel(T("时间 / s", "Time / s"), fontsize=7)
a.set_ylabel(T("肩关节力矩 / N·m", "Shoulder torque / N·m"), fontsize=7)
a.legend(fontsize=6.2, frameon=False)
a.set_title(T("(b) 动载：转 60°，用时 1.2 s", "(b) Dynamic: 60° move in 1.2 s"), fontsize=7.4)
a = axs[1, 0]
a.plot(tb[first], yb[first], color="#d62728", lw=1.0)
a.axhline(H.RATED, color=H.MUTED, lw=0.7, ls=":")
a.text(24, H.RATED + 8, T("额定 350", "rated 350"), fontsize=6.2, color=H.MUTED, ha="right")
a.set_xlabel(T("时间 / s", "Time / s"), fontsize=7)
a.set_ylabel(T("输出转矩 / N·m", "Output torque / N·m"), fontsize=7)
a.set_title(T("(c) 冲击：跑合试验台的一次起动", "(c) Impact: one start on the run-in bench"), fontsize=7.4)
a = axs[1, 1]
a.plot(t4, sig4, color="#2ca02c", lw=1.3, label=T("弯曲应力 σ", "bending stress σ"))
a.axhline(tau_m, color="#9467bd", lw=1.1, ls="--", label=T("扭转切应力 τ（不变）", "torsional stress τ (steady)"))
a.axhline(0, color=H.MUTED, lw=0.5)
a.set_xlabel(T("时间 / s", "Time / s"), fontsize=7)
a.set_ylabel(T("应力 / MPa", "Stress / MPa"), fontsize=7)
a.set_ylim(-32, 42)
a.legend(fontsize=6.2, frameon=False, loc="lower center", ncol=2)
a.set_title(T("(d) 交变：输出轴齿轮位表面一点", "(d) Alternating: a point on the output shaft's gear seat"), fontsize=7.4)
for a in axs.flat:
    a.tick_params(labelsize=6.3)
fig.tight_layout()
figure(fig, "fig7_2_1")

out(M0=M0, J=J, alpha=alpha, w_max=math.degrees(w_max), tau_acc=J * alpha, t_move=TM,
    tau2_max=float(tau2.max()), tau2_min=float(tau2.min()), m2=S2[0], a2=S2[1], R2=S2[2], dyn_ratio=float(tau2.max()) / M0,
    peak_c=peak_c, run_c=run_c, k_start=k_start, t_rise=t_rise, peak_rated=peak_c / H.RATED,
    Mb=Mb, Tq=Tq, d=d, sig_a=sig_a, tau_m=tau_m, n_out=n_out, f_rot=f_rot, R4=S4[2])
