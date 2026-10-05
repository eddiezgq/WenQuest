"""3.3 节：亚稳态与同步器。

算例 3.3.1  两个参考反相器首尾相接，从略偏离亚稳点的初始状态出发（手算模型数值积分）：偏离多久才放大到逻辑电平，
            与初始偏离的对数成正比；斜率就是 τm，与小信号估计 C/gm 比较，再与 SKY130 仿真值比较。
算例 3.3.2  电机 6000 r/min、编码器 1024 线：A、B 两相每秒各有多少个边沿；进入 100 MHz 时钟域时，每秒有多少次采样落进亚稳窗口。
            打一拍（后面的逻辑只留下 200 ps 余量）、打两拍、打三拍的平均故障间隔；1000 台机器人连续工作 10 年不出一次错，
            需要多少决断时间。
图 3.3.1    交叉耦合反相器从亚稳点附近“决断”的波形（初始偏离 10 mV、1 mV、0.1 mV、10 μV）。
图 3.3.2    平均故障间隔随决断时间的变化（对数纵轴），标出打一拍、打两拍和机队的要求。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from mos import P, VDD, Wmin, cin, ff_timing, fo4_tp, gamma_self, idn, idp, mtbf, r_ratio, sync_tr, tau_m_est, vm
import _draw as d

r = r_ratio()
g = gamma_self()
ff = ff_timing()
f4 = fo4_tp(r)

# ---------------------------------------------------------------- 算例 3.3.1 决断过程（手算模型）
C = cin(Wmin, r * Wmin) * (1 + g)           # 每个节点：另一个反相器的输入 + 自身漏极
V_M = vm(Wmin, r * Wmin)


def resolve(dv, t_end=400e-12, dt=0.02e-12):
    """V1 = VM + dv/2、V2 = VM − dv/2 出发，RK2 积分。返回时间、V1、V2。"""
    def f(v):
        v1, v2 = v
        i1 = idp(VDD - v2, VDD - v1, r * Wmin) - idn(v2, v1, Wmin)       # 反相器 2（输入 V2）给节点 1 的净电流
        i2 = idp(VDD - v1, VDD - v2, r * Wmin) - idn(v1, v2, Wmin)
        return np.array([i1, i2]) / C
    n = int(t_end / dt)
    v = np.array([V_M + dv / 2, V_M - dv / 2])
    ts, out1, out2 = [0.0], [v[0]], [v[1]]
    for k in range(n):
        k1 = f(v)
        k2 = f(v + dt * k1)
        v = np.clip(v + dt / 2 * (k1 + k2), 0, VDD)
        if k % 25 == 0:
            ts.append((k + 1) * dt); out1.append(v[0]); out2.append(v[1])
    return np.array(ts), np.array(out1), np.array(out2)


dvs = [10e-3, 1e-3, 1e-4, 1e-5]
waves, tres = [], []
for dv in dvs:
    t, v1, v2 = resolve(dv)
    waves.append((t, v1, v2))
    tres.append(t[np.argmax(v1 - v2 >= 0.8 * VDD)])
slope = (tres[-1] - tres[0]) / math.log(dvs[0] / dvs[-1])
out(C_ff=C * 1e15, tau_est_ps=tau_m_est() * 1e12, tau_fit_ps=slope * 1e12, tau_sim_ps=ff["tau_m"] * 1e12, tau_sim_fo4=P["ff_sim"]["tau_m"],
    t_10mv_ps=tres[0] * 1e12, t_span_ps=(tres[-1] - tres[0]) * 1e12, t_span_tau=(tres[-1] - tres[0]) / tau_m_est(), t_10uv_ps=tres[-1] * 1e12, step_ps=(tres[1] - tres[0]) * 1e12, est_err_pct=(1 - tau_m_est() / ff["tau_m"]) * 100)

# ---------------------------------------------------------------- 算例 3.3.2 平均故障间隔
q = P["problems"]["p33"]
fclk = q["f_MHz"] * 1e6
fdata = q["rpm"] / 60 * q["lines"] * 2           # 每相每秒的边沿数（每线一个上升沿、一个下降沿）
rate = ff["T0"] * fclk * fdata                   # 每秒落进亚稳窗口的次数
YEAR = 365 * 24 * 3600
need = q["robots"] * q["years"] * YEAR            # 一台机器人的平均故障间隔至少要这么长，机队在 years 年里才平均不到一次
tr_need = ff["tau_m"] * math.log(need * rate)
out(fdata_k=fdata / 1e3, rate=rate, T0_ps=ff["T0"] * 1e12, tsu_ps=ff["tsu"] * 1e12, tcq_ps=ff["tcq"] * 1e12, slack_ps=q["slack_ps"],
    robots=q["robots"], years=q["years"], need_yr=need / YEAR, tr_need_ps=tr_need * 1e12, tr_need_tau=tr_need / ff["tau_m"],
    rpm=q["rpm"], lines=q["lines"], f_MHz=q["f_MHz"], prob_pct=ff["T0"] * fclk * 100)
for n in (1, 2, 3):
    tr = sync_tr(n, fclk, q["slack_ps"] * 1e-12)
    m = mtbf(tr, fclk, fdata)
    out(**{f"tr{n}_ns": tr * 1e9, f"tr{n}_ps": tr * 1e12, f"log_mtbf{n}": math.log10(m), f"mtbf{n}_s": m})
for s_ps in (500, 1000, 2000):
    m = mtbf(s_ps * 1e-12, fclk, fdata)
    out(**{f"m1_{s_ps}_s": m, f"m1_{s_ps}_d": m / 86400, f"m1_{s_ps}_yr": m / YEAR, f"m1_{s_ps}_log": math.log10(m)})
out(fleet_days=mtbf(1000e-12, fclk, fdata) / q["robots"] / 86400)
out(per_ps_factor=math.exp(100e-12 / ff["tau_m"]))

# ---------------------------------------------------------------- 图 3.3.1
plt = style()
fig, ax = plt.subplots(figsize=(5.8, 3.4))
cols = [d.LOAD, d.MEAN, d.NMOS, d.PMOS]
labels = ["10 mV", "1 mV", "0.1 mV", "10 μV"]
for (t, v1, v2), c, lab in zip(waves, cols, labels):
    ax.plot(t * 1e12, v1, color=c, lw=1.6, label=T(f"初始偏离 {lab}", f"initial offset {lab}"))
    ax.plot(t * 1e12, v2, color=c, lw=1.1, ls="--")
ax.axhline(V_M, color=d.MUTED, lw=0.8, ls=":")
ax.set_xlabel(T("时间 / ps", "time / ps")); ax.set_ylabel(T("两个节点的电压 / V", "node voltages / V"))
ax.set_xlim(0, 400); ax.set_ylim(-0.05, VDD + 0.05)
ax.legend(fontsize=8, frameon=False, loc="upper left")
d.spines(ax)
figure(fig, "fig3_3_1")

# ---------------------------------------------------------------- 图 3.3.2
fig, ax = plt.subplots(figsize=(5.8, 3.4))
trs = np.linspace(0, 3000e-12, 200)
ax.plot(trs * 1e12, [math.log10(mtbf(x, fclk, fdata)) for x in trs], color=d.NMOS, lw=1.8)
ax.axhline(math.log10(need), color=d.LOAD, lw=1.0, ls="--")
ax.text(2950, math.log10(need) + 0.8, T(f"机队要求：{q['robots']} 台 × {q['years']} 年", f"fleet target: {q['robots']} robots × {q['years']} years"),
        ha="right", fontsize=8.5, color=d.LOAD)
x1 = q["slack_ps"]
ax.plot(x1, math.log10(mtbf(x1 * 1e-12, fclk, fdata)), "o", color=d.PMOS, ms=7)
ax.annotate(T("打一拍，余量 200 ps", "one flop, 200 ps slack"), (x1, math.log10(mtbf(x1 * 1e-12, fclk, fdata))), textcoords="offset points",
            xytext=(8, -14), fontsize=8.5, color=d.PMOS)
ax.annotate(T(f"打两拍：决断时间约 {sync_tr(2, fclk, x1 * 1e-12) * 1e9:.1f} ns，\n约 10 的 {math.log10(mtbf(sync_tr(2, fclk, x1 * 1e-12), fclk, fdata)):.0f} 次方秒（图外）",
              f"two flops: about {sync_tr(2, fclk, x1 * 1e-12) * 1e9:.1f} ns,\n~10^{math.log10(mtbf(sync_tr(2, fclk, x1 * 1e-12), fclk, fdata)):.0f} s (off the chart)"),
            (3000, 34), xytext=(1700, 30), fontsize=8.5, color=d.MEAN, arrowprops=dict(arrowstyle="->", color=d.MEAN))
ax.set_xlabel(T("决断时间 tr / ps", "resolution time tr / ps")); ax.set_ylabel(T("lg（平均故障间隔 / s）", "log₁₀(MTBF / s)"))
ax.set_xlim(0, 3000); ax.set_ylim(-4, 36)
d.spines(ax)
figure(fig, "fig3_3_2")
