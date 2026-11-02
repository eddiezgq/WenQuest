"""8.3 节：流水线与重定时。

算例 8.3.1  低成本 PI 数据通路要 50 MHz。比较：(a) 不插寄存器；(b) 在某一块后面插一级寄存器（四个位置）；(c) 在两处插；
            (d) 不插寄存器、换成快速结构。各方案的各级延时、最高频率、增加的延迟拍数与面积（触发器每个按 SKY130 标准单元约 20 μm²）。
算例 8.3.2  100 MHz 能不能靠插寄存器做到？阵列乘法器本身的延时。
图 8.3.1    各方案每一级的延时（含 tcq + tsu）与 50 MHz 的周期。
"""
from itertools import combinations

from bookout import T, figure, out, style
from mos import P, ff_timing
import _draw as d
import _pi

ff = ff_timing()
f = P["problems"]["p81"]["f_MHz"]
Tp = 1 / (f * 1e6)
ffa = P["problems"]["p73"]["ff_area"]
cuts_all = ["sub", "mul", "add1", "add2"]
res = {}
for k in range(0, 3):
    for c in combinations(cuts_all, k):
        st, tmin, loop, nreg = _pi.stages("cheap", set(c))
        res[c] = (st, tmin, nreg, _pi.area("cheap", set(c), ffa))
one = {c[0]: res[c] for c in res if len(c) == 1}
ok1 = [c for c in cuts_all if one[c][1] <= Tp]
best2 = min((c for c in res if len(c) == 2), key=lambda c: res[c][1])
st_f, tmin_f, loop_f, _ = _pi.stages("fast", set())
a_cheap, a_fast = _pi.area("cheap", set(), ffa), _pi.area("fast", set(), ffa)
b = _pi.blocks("cheap")
oh = ff["tcq"] + ff["tsu"]
vals = dict(f_MHz=f, T_ns=Tp * 1e9, t0_ns=res[()][1] * 1e9, f0=1e-6 / res[()][1], ok1="、".join(ok1), n_ok1=len(ok1),
            mul_st1=one["mul"][0][0] * 1e9, mul_st2=one["mul"][0][1] * 1e9, mul_tmin=one["mul"][1] * 1e9, mul_f=1e-6 / one["mul"][1],
            mul_reg=one["mul"][2], mul_area=one["mul"][3], area0=a_cheap, reg_area=one["mul"][2] * ffa,
            reg_pct=one["mul"][2] * ffa / a_cheap * 100, sub_st2=one["sub"][0][1] * 1e9, add1_st1=one["add1"][0][0] * 1e9,
            add2_st1=one["add2"][0][0] * 1e9, best2="、".join(best2), best2_tmin=res[best2][1] * 1e9, best2_max=max(res[best2][0]) * 1e9, best2_f=1e-6 / res[best2][1],
            fast_tmin=tmin_f * 1e9, fast_f=1e-6 / tmin_f, fast_area=a_fast, fast_x=a_fast / a_cheap,
            fast_extra=a_fast - a_cheap, mul_ns=b["mul"][0] * 1e9, mul_f_lim=1e-6 / (b["mul"][0] + oh),
            loop_ns=(oh + b["add1"][0]) * 1e9, loop_f=1e-6 / (oh + b["add1"][0]), oh_ps=oh * 1e12,
            sub_t1=(one["sub"][0][0] + oh) * 1e9, sub_t2=(one["sub"][0][1] + oh) * 1e9, mul_t1=(one["mul"][0][0] + oh) * 1e9,
            mul_t2=(one["mul"][0][1] + oh) * 1e9, ff_share=one["mul"][2] / P["problems"]["p34"]["n_ff"] * 100,
            lat_ns=Tp * 1e9, loop_period_us=1e3 / P["problems"]["p85"]["loop_kHz"])
out(**vals)

plt = style()
fig, ax = plt.subplots(figsize=(7.6, 3.4))
cases = [((), T("不插", "none")), (("sub",), T("减法后", "after sub")), (("mul",), T("乘法后", "after mul")),
         (("add1",), T("第一个加法后", "after add 1")), (("add2",), T("第二个加法后", "after add 2")), (best2, T("减法、乘法后", "after sub & mul"))]
for i, (c, lab) in enumerate(cases):
    st = res[c][0]
    for j, v in enumerate(st):
        x = i + (j - (len(st) - 1) / 2) * 0.24
        tot = (v + oh) * 1e9
        ax.bar(x, tot, width=0.22, color=d.MEAN if tot <= Tp * 1e9 else d.PMOS)
        ax.text(x, tot + 0.4, f"{tot:.1f}", ha="center", fontsize=7.5)
ax.axhline(Tp * 1e9, color=d.LOAD, ls="--", lw=1.2)
ax.text(len(cases) - 0.5, Tp * 1e9 + 0.5, T(f"{f:.0f} MHz 的周期", f"{f:.0f} MHz period"), ha="right", fontsize=9, color=d.LOAD)
ax.set_xticks(range(len(cases))); ax.set_xticklabels([l for _, l in cases], fontsize=9)
ax.set_ylabel(T("每一级的时间 / ns", "time per stage / ns")); ax.set_ylim(0, 33)
d.spines(ax)
figure(fig, "fig8_3_1")
