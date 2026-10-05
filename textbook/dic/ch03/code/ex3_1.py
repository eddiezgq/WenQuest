"""3.1 节：锁存器与触发器。

蝴蝶图  两个参考反相器首尾相接：画出两条电压传输特性，求三个交点（两个稳定点、一个亚稳点）和亚稳点处的增益。
算例 3.1.1  编码器计数器如果用高电平透明的锁存器：时钟为高的 5 ns 里，最低位绕“锁存器 → 取反 → 锁存器”转了多少圈。
算例 3.1.2  传输门主从触发器的时序参数：仿真值（以 FO4 为单位）换算成 ps；时钟到输出延时的逻辑努力手算估计。
图 3.1.1    交叉耦合反相器的“蝴蝶图”。
图 3.1.2    (a) 传输门锁存器；(b) 主从 D 触发器（与仿真电路一致）。
图 3.1.3    建立时间、保持时间与时钟到输出延时的定义（示意，不按比例）。
"""
import numpy as np

from bookout import T, figure, out, style
from mos import P, VDD, Wmin, ff_tcq_le, ff_timing, fo4_tp, gamma_self, r_ratio, tau, vm, vout
import _draw as d

CB = r"$\overline{\mathrm{CLK}}$"
QB = r"$\overline{Q}$"

r = r_ratio()
g = gamma_self()
tu = tau()
f4 = fo4_tp(r)
FF = P["ff_sim"]
ff = ff_timing()

# ---------------------------------------------------------------- 蝴蝶图：双稳态
vs = np.linspace(0, VDD, 721)
vo = np.array([vout(v, Wmin, r * Wmin) for v in vs])
V_M = vm(Wmin, r * Wmin)
i = int(np.argmin(abs(vs - V_M)))
gain = -(vo[i + 1] - vo[i - 1]) / (vs[i + 1] - vs[i - 1])
out(VM=V_M, gain=gain, vol=vo[-1], voh=vo[0])

# ---------------------------------------------------------------- 算例 3.1.1 锁存器的竞争
q = P["problems"]["p31"]
half = 0.5 / (q["f_MHz"] * 1e6)
st = ff_tcq_le()
loop_tau = st[2] + st[3] + (1 + g)          # 锁存器从数据到输出（传输门 + 反相器）+ 最低位取反（一个反相器驱动一个参考输入）
loop = loop_tau * tu
out(f_MHz=q["f_MHz"], bits=q["bits"], half_ns=half * 1e9, loop_tau=loop_tau, loop_ps=loop * 1e12, laps=int(half // loop))

# ---------------------------------------------------------------- 算例 3.1.2 时序参数
out(fo4_ps=f4 * 1e12, tau_ps=tu * 1e12, gamma=g)
for k in ("tcq", "tsu", "th", "tau_m", "T0"):
    out(**{f"{k}_fo4": FF[k], f"{k}_ps": ff[k] * 1e12})
out(th_abs_ps=-ff["th"] * 1e12)
for n, v in enumerate(st, 1):
    out(**{f"st{n}": v})
le = sum(st)
out(tcq_le=le, tcq_le_ps=le * tu * 1e12, tcq_le_fo4=le * tu / f4, tcq_err_pct=(le * tu / ff["tcq"] - 1) * 100,
    window_ps=(ff["tsu"] + ff["th"]) * 1e12)

# ---------------------------------------------------------------- 图 3.1.1 蝴蝶图
plt = style()
fig, ax = plt.subplots(figsize=(4.2, 4.0))
ax.plot(vs, vo, color=d.NMOS, lw=1.8, label=T("反相器 1：V₂ = f(V₁)", "inverter 1: V₂ = f(V₁)"))
ax.plot(vo, vs, color=d.PMOS, lw=1.8, label=T("反相器 2：V₁ = f(V₂)", "inverter 2: V₁ = f(V₂)"))
for (x, y, c, lab) in ((0, VDD, d.MEAN, T("稳定", "stable")), (VDD, 0, d.MEAN, T("稳定", "stable")), (V_M, V_M, d.LOAD, T("亚稳", "metastable"))):
    ax.plot(x, y, "o", color=c, ms=8, zorder=5)
    ax.annotate(lab, (x, y), textcoords="offset points", xytext=(10, 6) if y < 1 else (10, -14), fontsize=9, color=c)
ax.set_xlabel(T("V₁ / V", "V₁ / V")); ax.set_ylabel(T("V₂ / V", "V₂ / V"))
ax.set_xlim(-0.05, VDD + 0.05); ax.set_ylim(-0.05, VDD + 0.05)
ax.set_aspect("equal")
ax.legend(fontsize=8, frameon=False, loc="upper right")
d.spines(ax)
figure(fig, "fig3_1_1")

# ---------------------------------------------------------------- 图 3.1.2 锁存器与主从触发器
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.6, 5.6), gridspec_kw={"height_ratios": [1, 1.05]})
# (a) 锁存器：D → TG(CLK 高导通) → X → INV → Q̄ ；X ← TG(CLK 低导通) ← INV ← Q̄
y = 0
d.text(a1, (-0.35, y), "D", d.NMOS, 11)
l, rgt = d.tg(a1, 0, y, "CLK", CB)
d.wire(a1, [(-0.15, y), l])
d.wire(a1, [rgt, (1.3, y)])
d.dot(a1, (1.0, y))
d.text(a1, (1.0, y + 0.3), "X", d.MUTED, 9)
i1, o1 = d.inv(a1, 1.3, y)
d.wire(a1, [o1, (2.9, y)])
d.dot(a1, (2.4, y))
d.text(a1, (3.15, y), QB, d.NMOS, 11)
i2, o2 = d.inv(a1, 2.4 - 0.0, y - 1.3, right=False)
d.wire(a1, [(2.4, y), (2.4, y - 1.3)])
l2, r2 = d.tg(a1, 1.05, y - 1.3, CB, "CLK")
d.wire(a1, [o2, r2])
d.wire(a1, [l2, (1.0, y - 1.3), (1.0, y)])
d.text(a1, (4.6, y - 0.4), T("CLK = 1：透明，" + QB + " 跟随 D\nCLK = 0：反馈环接通，保持", "CLK = 1: transparent, " + QB + " follows D\nCLK = 0: loop closed, holds"), d.INK, 9, ha="left")
d.text(a1, (-0.5, 1.0), T("(a) 传输门锁存器（高电平透明）", "(a) transmission-gate latch (transparent high)"), d.INK, 10, ha="left")
d.blank(a1, -0.6, 8.2, -2.15, 1.2)
# (b) 主从触发器
y = 0
d.text(a2, (-0.35, y), "D", d.NMOS, 11)


def latch(ax, x0, top, bot, lbl):
    """在 x0 处画一个锁存器（输入传输门 + 反相器 + 反馈），返回输出点。"""
    l, rr = d.tg(ax, x0, y, top, bot)
    d.wire(ax, [rr, (x0 + 1.3, y)])
    _, o = d.inv(ax, x0 + 1.3, y)
    d.wire(ax, [o, (x0 + 2.6, y)])
    d.dot(ax, (x0 + 2.35, y))
    _, ob = d.inv(ax, x0 + 2.35, y - 1.3, right=False)
    d.wire(ax, [(x0 + 2.35, y), (x0 + 2.35, y - 1.3)])
    lb, rb = d.tg(ax, x0 + 1.0, y - 1.3, bot, top)
    d.wire(ax, [ob, rb])
    d.wire(ax, [lb, (x0 + 0.95, y - 1.3), (x0 + 0.95, y)])
    d.dot(ax, (x0 + 0.95, y))
    ax.add_patch(__import__("matplotlib").patches.FancyBboxPatch((x0 - 0.15, y - 2.2), 2.85, 2.9, boxstyle="round,pad=0.05",
                                                                 fill=False, ec=d.MUTED, lw=0.8, ls="--"))
    d.text(ax, (x0 + 1.3, y + 0.95), lbl, d.MUTED, 9)
    return l, (x0 + 2.6, y)


l1, o1 = latch(a2, 0, CB, "CLK", T("主锁存器：CLK = 0 时透明", "master: transparent when CLK = 0"))
d.wire(a2, [(-0.15, y), l1])
l2, o2 = latch(a2, 3.2, "CLK", CB, T("从锁存器：CLK = 1 时透明", "slave: transparent when CLK = 1"))
d.wire(a2, [o1, l2])
d.wire(a2, [o2, (6.4, y)])
d.text(a2, (6.65, y), "Q", d.NMOS, 11)
d.text(a2, (6.25, y - 1.3), T("时钟先经两级反相器\n得到 " + CB + " 和 CLK", "the clock passes two inverters\nto give " + CB + " and CLK"), d.MUTED, 8.5, ha="left")
d.text(a2, (-0.5, 1.25), T("(b) 主从 D 触发器（上升沿触发）", "(b) master-slave D flip-flop (rising edge)"), d.INK, 10, ha="left")
d.blank(a2, -0.6, 8.2, -2.3, 1.5)
figure(fig, "fig3_1_2")

# ---------------------------------------------------------------- 图 3.1.3 时序参数（示意，不按比例）
fig, ax = plt.subplots(figsize=(6.4, 2.9))
SU, HO, CQ = 120, 80, 200          # 示意宽度


def bus(y0, t1, t2, color, label, mid=""):
    """总线画法：t1、t2 处交叉，中间是有效数据。"""
    h, k = 0.32, 18
    for sgn in (1, -1):
        ax.plot([-420, t1 - k, t1 + k, t2 - k, t2 + k, 420], [y0 + sgn * h, y0 + sgn * h, y0 - sgn * h, y0 - sgn * h, y0 + sgn * h, y0 + sgn * h],
                color=color, lw=1.6)
    ax.text(-440, y0, label, ha="right", va="center", fontsize=10, color=color)
    if mid:
        ax.text((t1 + t2) / 2, y0, mid, ha="center", va="center", fontsize=8.5, color=color)


ax.plot([-420, -10, 10, 420], [2.2, 2.2, 2.9, 2.9], color=d.PMOS, lw=1.8)
ax.text(-440, 2.55, "CLK", ha="right", va="center", fontsize=10, color=d.PMOS)
bus(1.35, -300, 260, d.NMOS, "D", T("新数据", "new data"))
bus(0.25, CQ, 600, d.MEAN, "Q", T("新数据", "new data"))
ax.add_patch(__import__("matplotlib").patches.Rectangle((-SU, 0.95), SU + HO, 0.8, color=d.LOAD, alpha=0.25, lw=0))
ax.axvline(0, color=d.MUTED, lw=0.8, ls=":")
ax.annotate("", xy=(-SU, 1.85), xytext=(0, 1.85), arrowprops=dict(arrowstyle="<->", color=d.LOAD, lw=1))
ax.text(-SU / 2, 1.9, "tsu", ha="center", va="bottom", fontsize=9, color=d.LOAD)
ax.annotate("", xy=(0, 1.85), xytext=(HO, 1.85), arrowprops=dict(arrowstyle="<->", color=d.LOAD, lw=1))
ax.text(HO / 2, 1.9, "th", ha="center", va="bottom", fontsize=9, color=d.LOAD)
ax.annotate("", xy=(0, 0.7), xytext=(CQ, 0.7), arrowprops=dict(arrowstyle="<->", color=d.MEAN, lw=1))
ax.text(CQ / 2, 0.75, "tcq", ha="center", va="bottom", fontsize=9, color=d.MEAN)
ax.text(300, 1.95, T("橙色窗口内 D 必须稳定", "D must be stable in the orange window"), ha="left", va="bottom", fontsize=8.5, color=d.LOAD)
ax.set_xlim(-520, 440); ax.set_ylim(-0.2, 3.1)
ax.axis("off")
figure(fig, "fig3_1_3")
