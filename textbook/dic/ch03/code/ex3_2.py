"""3.2 节：时序约束。

算例 3.2.1  16 位 PWM 计数器：每个时钟周期加 1 后写回自己。用逻辑努力估计行波进位加 1 电路的关键路径，
            求最高时钟频率；与“16 位分辨率、20 kHz PWM”要求的时钟频率比较；时钟固定为 PWM 频率乘 2^n 时，最多能做几位。
算例 3.2.2  编码器数字滤波器的移位寄存器：相邻两级恰好接在第 4 章 4.2 节时钟树的近端和远端分支上，
            后一级的时钟还多经过一个门控单元和缓冲器（示意值 2 个 FO4）。检查保持时间，并用插入反相器对的办法修正。
图 3.2.1    (a) 建立时间预算：不同位数时 tcq + 逻辑 + tsu 与所需的时钟周期；(b) 保持时间检查：三种情况的余量。
"""
from bookout import T, figure, out, style
from mos import P, ff_timing, fo4_tp, gamma_self, hold_slack, inc_delay, r_ratio, setup_slack, tau
import _draw as d
from _skew import skew_ch4

r = r_ratio()
g = gamma_self()
tu = tau()
f4 = fo4_tp(r)
ff = ff_timing()
q = P["problems"]["p32"]

# ---------------------------------------------------------------- 算例 3.2.1 建立时间
per_bit = (1 + 2 * g) + ((2 + r) / (1 + r) + 4 + g)
D16 = inc_delay(q["bits"])
t16 = D16 * tu
Tmin = ff["tcq"] + t16 + ff["tsu"]
f_need = 2 ** q["bits"] * q["pwm_kHz"] * 1e3
f_now = q["f_MHz"] * 1e6
out(per_bit=per_bit, D16=D16, t16_ns=t16 * 1e9, t16_ps=t16 * 1e12, Tmin_ns=Tmin * 1e9, fmax_MHz=1e-6 / Tmin,
    f_need_MHz=f_need / 1e6, f_MHz=q["f_MHz"], pwm_now_kHz=f_now / 2 ** q["bits"] / 1e3, slack_now_ns=setup_slack(1 / f_now, t16) * 1e9,
    slack_need_ps=setup_slack(1 / f_need, t16) * 1e12, logic_pct=t16 / Tmin * 100, bits=q["bits"], pwm_kHz=q["pwm_kHz"])
rows = []
best = 0
for n in range(8, 17):
    tl = inc_delay(n) * tu
    fn = 2 ** n * q["pwm_kHz"] * 1e3
    sl = setup_slack(1 / fn, tl)
    rows.append((n, tl, fn, sl))
    if sl >= 0:
        best = n
fb = 2 ** best * q["pwm_kHz"] * 1e3
out(best_bits=best, best_f_MHz=fb / 1e6, best_slack_ps=setup_slack(1 / fb, inc_delay(best) * tu) * 1e12,
    next_f_MHz=2 * fb / 1e6, next_slack_ps=setup_slack(1 / (2 * fb), inc_delay(best + 1) * tu) * 1e12)

# ---------------------------------------------------------------- 算例 3.2.2 保持时间
skew4 = skew_ch4()                      # 第 4 章算例 4.2.2 的时钟树：数值求解近端与远端 50 % 时刻之差
gate = q["gate_fo4"] * f4
skew = skew4 + gate
pair = 2 * (1 + g) * tu                 # 一对参考反相器，每个只驱动下一个（FO1）
h0 = hold_slack(0.0, 0.0)
h4 = hold_slack(0.0, skew4)
hg = hold_slack(0.0, skew)
npair = 0
while hold_slack(npair * pair, skew) < 0:
    npair += 1
out(skew4_ps=skew4 * 1e12, gate_ps=gate * 1e12, gate_fo4=q["gate_fo4"], skew_ps=skew * 1e12, h0_ps=h0 * 1e12, h4_ps=h4 * 1e12, hg_ps=hg * 1e12,
    pair_ps=pair * 1e12, npair=npair, hfix_ps=hold_slack(npair * pair, skew) * 1e12, hfix2_ps=hold_slack(2 * pair, skew) * 1e12,
    limit_ps=(ff["tcq"] - ff["th"]) * 1e12,
    setup_gain_ps=skew * 1e12)

# ---------------------------------------------------------------- 图 3.2.1
plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.4, 3.6), gridspec_kw={"width_ratios": [1.5, 1]})
ns = [x[0] for x in rows]
tcq_ns, tsu_ns = ff["tcq"] * 1e9, ff["tsu"] * 1e9
a1.bar(ns, [tcq_ns] * len(ns), color=d.MUTED, width=0.6, label="tcq")
a1.bar(ns, [x[1] * 1e9 for x in rows], bottom=[tcq_ns] * len(ns), color=d.NMOS, width=0.6, label=T("加 1 电路", "incrementer"))
a1.bar(ns, [tsu_ns] * len(ns), bottom=[tcq_ns + x[1] * 1e9 for x in rows], color=d.LOAD, width=0.6, label="tsu")
a1.plot(ns, [1e9 / x[2] for x in rows], "o-", color=d.PMOS, lw=1.5, ms=5, label=T("所需周期（20 kHz × 2ⁿ）", "required period (20 kHz × 2ⁿ)"))
a1.set_yscale("log"); a1.set_ylim(0.1, 400)
a1.set_xlabel(T("计数器位数 n", "counter bits n")); a1.set_ylabel(T("时间 / ns", "time / ns"))
a1.set_title(T("(a) 建立时间预算", "(a) setup budget"), fontsize=10)
a1.legend(fontsize=8, frameon=False, loc="upper right")
d.spines(a1)
cases = [(T("同一分支", "same branch"), h0), (T("近端 → 远端", "near → far"), h4), (T("再加门控", "plus gating"), hg),
         (T(f"插 {npair} 对反相器", f"{npair} inverter pair(s)"), hold_slack(npair * pair, skew))]
a2.barh(range(len(cases)), [c[1] * 1e12 for c in cases], color=[d.MEAN if c[1] >= 0 else d.PMOS for c in cases], height=0.55)
a2.set_yticks(range(len(cases)), [c[0] for c in cases], fontsize=9)
a2.invert_yaxis()
a2.axvline(0, color=d.INK, lw=0.8)
for k, c in enumerate(cases):
    a2.text(c[1] * 1e12 + (6 if c[1] >= 0 else -6), k, f"{c[1] * 1e12:.0f} ps", va="center", ha="left" if c[1] >= 0 else "right", fontsize=8.5)
a2.set_xlabel(T("保持时间余量 / ps", "hold slack / ps"))
a2.set_xlim(-120, 280)
a2.set_title(T("(b) 保持时间检查", "(b) hold check"), fontsize=10)
d.spines(a2)
figure(fig, "fig3_2_1")
