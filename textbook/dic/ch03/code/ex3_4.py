"""3.4 节：时钟门控与复位。

算例 3.4.1  电机控制芯片里有 2000 个触发器，时钟 100 MHz。每个触发器内部挂在时钟上的电容（本地时钟反相器、四个传输门的栅极、
            反相器的漏极）每个周期充放电一次，求时钟功耗。电机 90 % 的时间停着，每 16 个触发器共用一个门控单元，
            停机时关掉它们的时钟，求省下的功耗（不计时钟树导线，第 8 章再算）。
图 3.4.1    门控时钟的波形：直接用与门时，使能在时钟为高时变化会切出毛刺；锁存器型门控单元不会。
图 3.4.2    (a) 锁存器型时钟门控单元；(b) 异步复位、同步释放的复位同步器。
"""
from bookout import T, figure, out, style
from mos import P, VDD, Wmin, cin, gamma_self, le_g, r_ratio
import _draw as d

r = r_ratio()
g = gamma_self()
C0 = cin(Wmin, r * Wmin)
q = P["problems"]["p34"]
f = q["f_MHz"] * 1e6

# ---------------------------------------------------------------- 算例 3.4.1
c_ff_units = 1 + (3 + g) + (2 + g)             # 时钟输入 + 反相时钟节点 + 同相时钟节点（以参考输入电容 C0 为单位）
c_ff = c_ff_units * C0
e_ff = c_ff * VDD ** 2
p_all = q["n_ff"] * e_ff * f
# 门控单元：一个锁存器（本地反相器 + 两个传输门各一个时钟输入）加一个与门（二输入与非门 + 反相器）
c_icg_units = 1 + (1 + g) + 1 + le_g("nand", 2)
c_icg = c_icg_units * C0
n_icg = q["n_ff"] // q["group"]
p_gated = n_icg * c_icg * VDD ** 2 * f + (1 - q["idle"]) * q["n_ff"] * e_ff * f
out(c_ff_units=c_ff_units, c_ff_ff=c_ff * 1e15, e_ff_fj=e_ff * 1e15, n_ff=q["n_ff"], f_MHz=q["f_MHz"], p_all_mw=p_all * 1e3,
    c_icg_units=c_icg_units, c_icg_ff=c_icg * 1e15, n_icg=n_icg, group=q["group"], idle_pct=q["idle"] * 100,
    icg_overhead_pct=n_icg * c_icg / (q["n_ff"] * c_ff) * 100, p_gated_mw=p_gated * 1e3, saved_pct=(1 - p_gated / p_all) * 100,
    p_ideal_mw=(1 - q["idle"]) * p_all * 1e3)

# ---------------------------------------------------------------- 图 3.4.1 门控波形（示意，单位时间 1 = 半个周期的 1/10）
plt = style()
fig, ax = plt.subplots(figsize=(6.6, 3.2))
t = [i * 0.5 for i in range(161)]                 # 0 … 80
clk = [1 if (x % 20) >= 10 else 0 for x in t]     # 周期 20，上升沿在 10、30、50、70
en = [1 if 14 <= x < 54 else 0 for x in t]        # 使能在时钟为高时（14、54 不在边沿上）变化
lat = []
state = 0
for c, e in zip(clk, en):
    if c == 0:
        state = e                                 # 锁存器在时钟为低时透明
    lat.append(state)
g_and = [c & e for c, e in zip(clk, en)]
g_icg = [c & l for c, l in zip(clk, lat)]
rows = [("CLK", clk, d.PMOS), ("EN", en, d.NMOS), (T("与门输出", "AND output"), g_and, d.LOAD), (T("门控单元输出", "ICG output"), g_icg, d.MEAN)]
for k, (lab, w, c) in enumerate(rows):
    y0 = (len(rows) - 1 - k) * 1.3
    ax.step(t, [y0 + 0.8 * v for v in w], where="post", color=c, lw=1.6)
    ax.text(-1.5, y0 + 0.4, lab, ha="right", va="center", fontsize=9.5, color=c)
ax.annotate(T("毛刺", "glitch"), (15, 1.3 * 1 + 0.8), xytext=(4, 3.1), fontsize=9, color=d.PMOS, arrowprops=dict(arrowstyle="->", color=d.PMOS))
ax.annotate(T("被截短的脉冲", "truncated pulse"), (53, 1.3 + 0.8), xytext=(56, 3.1), fontsize=9, color=d.PMOS, arrowprops=dict(arrowstyle="->", color=d.PMOS))
for x in (10, 30, 50, 70):
    ax.axvline(x, color=d.MUTED, lw=0.6, ls=":")
ax.set_xlim(-14, 80); ax.set_ylim(-0.3, 4.9)
ax.axis("off")
figure(fig, "fig3_4_1")

# ---------------------------------------------------------------- 图 3.4.2 门控单元与复位同步器
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.4, 2.9))
# (a) 门控单元
d.text(a1, (-0.3, 0.4), "EN", d.NMOS, 10, ha="right")
d.wire(a1, [(-0.2, 0.4), (0.3, 0.4)])
d.box(a1, 0.3, 0.4, 1.8, 1.0, T("锁存器\nCLK 低时透明", "latch, transparent\nwhen CLK is low"), d.INK, 8.5)
ia, ib, oo = d.and_gate(a1, 2.8, 0.0)
d.wire(a1, [(2.1, 0.4), (2.5, 0.4), (2.5, ia[1]), ia])
d.wire(a1, [(-0.2, -1.0), (2.5, -1.0), (2.5, ib[1]), ib])
d.wire(a1, [(1.2, -1.0), (1.2, -0.1)])
d.dot(a1, (1.2, -1.0))
d.text(a1, (-0.3, -1.0), "CLK", d.PMOS, 10, ha="right")
d.wire(a1, [oo, (3.9, 0.0)])
d.text(a1, (4.0, 0.0), "GCLK", d.MEAN, 10, ha="left")
d.text(a1, (-1.2, 1.3), T("(a) 锁存器型时钟门控单元", "(a) latch-based clock-gating cell"), d.INK, 10, ha="left")
d.blank(a1, -1.3, 5.0, -1.5, 1.5)
# (b) 复位同步器
for x in (0.6, 2.8):
    d.box(a2, x, 0.3, 1.1, 1.2, "", d.INK)
    d.text(a2, (x + 0.15, 0.6), "D", d.INK, 9, ha="left")
    d.text(a2, (x + 0.95, 0.6), "Q", d.INK, 9, ha="right")
    d.text(a2, (x + 0.12, 0.0), ">", d.INK, 9, ha="left")
    d.text(a2, (x + 0.55, -0.15), "CLR", d.MUTED, 7.5)
    d.wire(a2, [(x - 0.2, -0.75), (x - 0.2, 0.0), (x, 0.0)])
    d.wire(a2, [(x + 0.55, -1.3), (x + 0.55, -0.3)])
d.text(a2, (0.0, 0.6), "1", d.NMOS, 10, ha="right")
d.wire(a2, [(0.05, 0.6), (0.6, 0.6)])
d.wire(a2, [(1.7, 0.6), (2.8, 0.6)])
d.wire(a2, [(3.9, 0.6), (4.5, 0.6)])
d.text(a2, (4.6, 0.6), T("内部复位（低有效）", "internal reset\n(active low)"), d.MEAN, 9, ha="left")
d.wire(a2, [(-0.2, -0.75), (2.6, -0.75)])
d.dot(a2, (0.4, -0.75))
d.text(a2, (-0.3, -0.75), "CLK", d.PMOS, 9, ha="right")
d.wire(a2, [(-0.2, -1.3), (3.35, -1.3)])
d.dot(a2, (1.15, -1.3))
d.text(a2, (-0.3, -1.3), T("外部复位", "external reset"), d.PMOS, 9, ha="right")
d.text(a2, (-1.9, 1.5), T("(b) 复位同步器：异步复位、同步释放", "(b) reset synchronizer: assert async, release sync"), d.INK, 10, ha="left")
d.blank(a2, -2.0, 7.0, -1.6, 1.8)
figure(fig, "fig3_4_2")
