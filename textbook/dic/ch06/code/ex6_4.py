"""6.4 节：移位器与比较器。

算例 6.4.1  定点数的缩放：16 位对数移位器（左移 0–15 位）的级数、二选一的个数与 SKY130 综合结果；与“一级 16 选 1”的做法比较。
算例 6.4.2  第 3 章 PWM 的比较器（计数值 < 占空比？）：比较器就是减法器的进位输出。行波比较器与前缀比较器的综合结果；
            高速版本（时钟 500 MHz）时哪个满足预算。
图 6.4.1    16 位对数移位器：四级二选一，分别移 1、2、4、8 位（只画出 8 位以便看清）。
"""
from bookout import T, figure, out, style
from mos import P, ff_timing
import _draw as d

S = P["arith_syn"]
q = P["problems"]["p64"]
ff = ff_timing()
budget = 1 / (q["f_MHz"] * 1e6) - ff["tcq"] - ff["tsu"]
n = 16
out(levels=4, muxes=4 * n, mux16=n, mux16_inputs=n, sh_d=S["shift_16"]["delay"], sh_a=S["shift_16"]["area"],
    cr_d=S["cmp_rca_16"]["delay"], cr_a=S["cmp_rca_16"]["area"], ck_d=S["cmp_ks_16"]["delay"], ck_a=S["cmp_ks_16"]["area"],
    cmp_x=S["cmp_rca_16"]["delay"] / S["cmp_ks_16"]["delay"], cmp_ax=S["cmp_ks_16"]["area"] / S["cmp_rca_16"]["area"],
    f_MHz=q["f_MHz"], budget_ps=budget * 1e12, rc_ok=int(S["cmp_rca_16"]["delay"] * 1e-12 <= budget),
    ks_ok=int(S["cmp_ks_16"]["delay"] * 1e-12 <= budget), cmp_vs_add=S["cmp_ks_16"]["area"] / S["add_ks_16"]["area"])

# ---------------------------------------------------------------- 图 6.4.1（8 位示意）
plt = style()
fig, ax = plt.subplots(figsize=(7.2, 3.6))
m = 8
for lv in range(3):
    dd = 1 << lv
    y0, y1 = -lv * 1.2, -(lv + 1) * 1.2
    for i in range(m):
        ax.plot([i, i], [y0, y1 + 0.25], color=d.NMOS, lw=1.0)
        if i >= dd:
            ax.plot([i - dd, i], [y0, y1 + 0.25], color=d.PMOS, lw=0.9, alpha=0.8)
        ax.add_patch(__import__("matplotlib").patches.Rectangle((i - 0.18, y1 + 0.05), 0.36, 0.2, fill=True, color=d.INK))
    ax.text(m - 0.2, (y0 + y1) / 2, T(f"sh[{lv}]：移 {dd} 位", f"sh[{lv}]: shift by {dd}"), fontsize=9, va="center")
for i in range(m):
    ax.text(i, 0.25, f"a{i}", ha="center", fontsize=8, color=d.MUTED)
    ax.text(i, -3.95, f"y{i}", ha="center", fontsize=8, color=d.MUTED)
ax.set_xlim(-0.8, m + 2.4); ax.set_ylim(-4.2, 0.6)
ax.axis("off")
figure(fig, "fig6_4_1")
