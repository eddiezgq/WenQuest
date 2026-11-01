"""5.3 节：降压与频率调节。

算例 5.3.1  电压与速度：SKY130 仿真的 FO4 延时随 VDD 的变化，与长沟道手算模型比较（手算在阈值附近失效）。
算例 5.3.2  巡检机器人的关节控制芯片：每 100 μs（10 kHz 控制环）要完成 2000 个时钟周期的运算，关键路径 30 个 FO4；
            两万个门、翻转率 0.1、每门 5 fF。(1) 1.8 V 全速跑完再空闲（时钟门控，空闲时只有漏电）；(2) 降到刚好赶上截止时间的电压和频率；
            比较每个控制周期的能量（27 °C 与 85 °C）。
算例 5.3.3  最低能量点：每个运算周期的能量（动态 + 漏电）随电压的变化，27 °C 与 85 °C 时最低点在哪里。
图 5.3.1    FO4 延时随 VDD 的变化（相对 1.8 V，对数纵轴）：仿真与手算。
图 5.3.2    每个运算周期的能量随电压的变化（动态、漏电与合计），27 °C 与 85 °C。
"""
import numpy as np

from bookout import T, figure, out, style
from mos import P, VDD, energy_per_op, fo4_scale, fo4_tp, leak_inv, r_ratio, VTn, VTp
import _draw as d

r = r_ratio()
f4 = fo4_tp(r)
q = P["problems"]["p53"]
N, a, C = q["n_gates"], q["alpha"], q["c_gate_fF"] * 1e-15

# ---------------------------------------------------------------- 算例 5.3.1
for v in (1.2, 1.0, 0.8, 0.6):
    hand = fo4_tp(r, v) / f4 if v > max(VTn, VTp) + 0.02 else float("inf")
    out(**{f"sim_{int(v * 10)}": fo4_scale(v), f"hand_{int(v * 10)}": hand, f"e_{int(v * 10)}_pct": (v / VDD) ** 2 * 100})

# ---------------------------------------------------------------- 算例 5.3.2
period = 1 / (q["loop_kHz"] * 1e3)
cyc = q["cycles"]


def fmax(v):
    return 1 / (q["depth_fo4"] * f4 * fo4_scale(v))


def plan(v, temp, gated_idle=True):
    """在电压 v 下以最高频率跑完 cyc 个周期，余下时间空闲（时钟关掉，只剩漏电）。返回 (能量, 运算时间)。"""
    ed, el, tc = energy_per_op(v, N, a, C, q["depth_fo4"], temp)
    busy = cyc * tc
    e = cyc * (ed + el) + N * leak_inv(temp, v) * v * max(0.0, period - busy)
    return e, busy


f18 = fmax(VDD)
# 刚好赶上截止时间的最低电压（0.01 V 步长）
v_dvfs = VDD
v = VDD
while v > 0.4:
    if cyc / fmax(v - 0.01) > period:
        break
    v -= 0.01
v_dvfs = round(v, 2)
out(period_us=period * 1e6, cycles=cyc, depth=q["depth_fo4"], fmax18_mhz=f18 / 1e6, busy18_us=cyc / f18 * 1e6,
    f_need_mhz=cyc / period / 1e6, scale_need=f18 / (cyc / period), v_dvfs=v_dvfs, f_dvfs_mhz=fmax(v_dvfs) / 1e6, scale_dvfs=fo4_scale(v_dvfs), n_gates=N, alpha=a,
    c_gate=q["c_gate_fF"])
for t in (q["temp"], q["hot"]):
    e1, b1 = plan(VDD, t)
    e2, b2 = plan(v_dvfs, t)
    out(**{f"race{t}_nj": e1 * 1e9, f"dvfs{t}_nj": e2 * 1e9, f"save{t}_pct": (1 - e2 / e1) * 100,
           f"race{t}_uw": e1 / period * 1e6, f"dvfs{t}_uw": e2 / period * 1e6,
           f"idle{t}_pct": N * leak_inv(t, VDD) * VDD * (period - b1) / e1 * 100})

# ---------------------------------------------------------------- 算例 5.3.3
vs = np.round(np.arange(0.40, 1.801, 0.01), 2)
curves = {}
for t in (q["temp"], q["hot"]):
    ed = np.array([energy_per_op(v, N, a, C, q["depth_fo4"], t)[0] for v in vs])
    el = np.array([energy_per_op(v, N, a, C, q["depth_fo4"], t)[1] for v in vs])
    k = int(np.argmin(ed + el))
    curves[t] = (ed, el)
    out(**{f"mep{t}_v": vs[k], f"mep{t}_pj": (ed + el)[k] * 1e12, f"mep{t}_leak_pct": el[k] / (ed + el)[k] * 100,
           f"mep{t}_fmhz": fmax(vs[k]) / 1e6, f"e18_{t}_pj": (ed + el)[-1] * 1e12, f"mep{t}_ratio": (ed + el)[-1] / (ed + el)[k]})

# ---------------------------------------------------------------- 图 5.3.1
plt = style()
fig, ax = plt.subplots(figsize=(5.8, 3.4))
sim = P["power_sim"]["vdd"]
ax.semilogy([v for v, _, _ in sim], [s for _, s, _ in sim], "o-", color=d.NMOS, lw=1.8, label=T("SKY130 仿真", "SKY130 simulation"))
vh = np.linspace(0.62, 1.8, 80)
ax.semilogy(vh, [fo4_tp(r, v) / f4 for v in vh], color=d.PMOS, lw=1.4, ls="--", label=T("长沟道手算模型", "long-channel hand model"))
ax.axvline(VTn, color=d.MUTED, lw=0.8, ls=":")
ax.text(VTn + 0.02, 2e4, T("手算的 VT", "hand-model VT"), fontsize=8.5, color=d.MUTED)
ax.set_xlabel("VDD / V"); ax.set_ylabel(T("FO4 延时 / 1.8 V 时的值", "FO4 delay / value at 1.8 V"))
ax.set_xlim(0.38, 1.82); ax.set_ylim(0.8, 1e5)
ax.legend(fontsize=8.5, frameon=False, loc="upper right")
d.spines(ax)
figure(fig, "fig5_3_1")

# ---------------------------------------------------------------- 图 5.3.2
fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.4), sharey=True)
for axx, t in zip(axs, (q["temp"], q["hot"])):
    ed, el = curves[t]
    axx.semilogy(vs, ed * 1e12, color=d.NMOS, lw=1.4, ls="--", label=T("动态", "dynamic"))
    axx.semilogy(vs, el * 1e12, color=d.PMOS, lw=1.4, ls="--", label=T("漏电", "leakage"))
    axx.semilogy(vs, (ed + el) * 1e12, color=d.INK, lw=2.0, label=T("合计", "total"))
    k = int(np.argmin(ed + el))
    axx.plot(vs[k], (ed + el)[k] * 1e12, "o", color=d.MEAN, ms=7)
    axx.annotate(T(f"最低点 {vs[k]:.2f} V", f"minimum {vs[k]:.2f} V"), (vs[k], (ed + el)[k] * 1e12), textcoords="offset points", xytext=(6, -16),
                 fontsize=8.5, color=d.MEAN)
    axx.set_title(f"{t} °C", fontsize=10)
    axx.set_xlabel("VDD / V")
    axx.set_ylim(0.1, 1e3)
    d.spines(axx)
axs[0].set_ylabel(T("每个运算周期的能量 / pJ", "energy per operation / pJ"))
axs[0].legend(fontsize=8.5, frameon=False, loc="upper right")
figure(fig, "fig5_3_2")
