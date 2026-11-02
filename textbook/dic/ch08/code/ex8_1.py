"""8.1 节：同步系统的时序。

算例 8.1.1  时钟周期里有多少留给逻辑：T = tcq + t逻辑 + tsu + 偏斜 + 抖动。触发器取第 3 章（SKY130 仿真），偏斜取 8.4 节时钟树
            算出的负载不均偏斜，抖动取 100 ps（教学设定）。比较 50 MHz（PI 数据通路）与 500 MHz（第 6 章高速版本的比较器）
            两种时钟下，这些“开销”各占周期的多少。
图 8.1.1    两种时钟下周期的分配。
"""
from bookout import T, figure, out, style
from mos import P, ff_timing, htree, hold_slack
import _draw as d

ff = ff_timing()
q = P["problems"]["p81"]
q4 = P["problems"]["p84"]
n_ff = P["problems"]["p34"]["n_ff"]
h = htree(q4["levels"], q4["die_um"], n_ff, q4["size"], q4["layer"], q4["imb"])
skew, jit = h["skew"], q["jitter_ps"] * 1e-12
vals = dict(tcq_ps=ff["tcq"] * 1e12, tsu_ps=ff["tsu"] * 1e12, th_ps=ff["th"] * 1e12, skew_ps=skew * 1e12, jit_ps=jit * 1e12)
rows = []
for f in (q["f_MHz"], P["problems"]["p64"]["f_MHz"]):
    Tp = 1 / (f * 1e6)
    over = ff["tcq"] + ff["tsu"] + skew + jit
    k = f"{f:.0f}"
    vals[f"T{k}_ns"] = Tp * 1e9
    vals[f"over{k}_ps"] = over * 1e12
    vals[f"over{k}_pct"] = over / Tp * 100
    vals[f"logic{k}_ns"] = (Tp - over) * 1e9
    rows.append((f, Tp, over))
vals["f_lo"], vals["f_hi"] = q["f_MHz"], P["problems"]["p64"]["f_MHz"]
vals["hold0_ps"] = hold_slack(0.0, skew) * 1e12          # 两个触发器直接相连、接收端时钟晚到 skew 时的保持余量
out(**vals)

plt = style()
fig, axs = plt.subplots(2, 1, figsize=(7.4, 2.9))
for ax, (f, Tp, over) in zip(axs, rows):
    parts = [(ff["tcq"], "tcq", d.NMOS), (Tp - over, T("留给逻辑", "logic"), d.MEAN), (ff["tsu"], "tsu", d.PMOS),
             (skew, T("偏斜", "skew"), d.LOAD), (jit, T("抖动", "jitter"), d.MUTED)]
    x = 0.0
    for v, lab, col in parts:
        ax.barh(0, v / Tp * 100, left=x, color=col, height=0.6, label=lab)
        if v > 1e-9:
            ax.text(x + v / Tp * 50, 0, f"{lab} {v * 1e9:.2f} ns", ha="center", va="center", fontsize=8.5, color="white")
        x += v / Tp * 100
    ax.set_xlim(0, 100); ax.set_yticks([0]); ax.set_yticklabels([f"{f:.0f} MHz"])
    ax.text(101, 0, T(f"开销 {over / Tp * 100:.1f} %", f"overhead {over / Tp * 100:.1f} %"), va="center", fontsize=9)
    d.spines(ax)
axs[1].set_xlabel(T("占时钟周期的百分比", "share of the clock period (%)"))
axs[0].legend(ncol=5, fontsize=8, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0))
fig.tight_layout()
figure(fig, "fig8_1_1")
