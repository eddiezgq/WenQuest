"""8.4 节：时钟树与时钟分布。

算例 8.4.1  第 3 章算例 3.4.1 的芯片：2000 个触发器、100 MHz，核心区按 1 mm × 1 mm（教学设定）。用 H 形树把时钟送到 4^L 个
            区（每区一个叶子缓冲器驱动本区的触发器），导线走 met3（最小线宽），每个分叉一个 size 倍参考反相器的缓冲器。
            比较 L = 1～4、size = 4～32：插入延时、某区触发器多 20 % 时的偏斜、时钟网络的总电容与功耗，
            以及导线和缓冲器的电容是触发器时钟电容的几倍（第 3 章取的示意值是 1.5）。
图 8.4.1    三层 H 形树（64 个叶子）。
图 8.4.2    size = 16 时插入延时、偏斜与时钟功耗随层数的变化。
"""
from bookout import T, figure, out, style
from mos import P, htree, ff_clk_cap
import _draw as d

q = P["problems"]["p84"]
n_ff, f = P["problems"]["p34"]["n_ff"], P["problems"]["p34"]["f_MHz"] * 1e6
LV, SZ = [1, 2, 3, 4], [4, 8, 16, 32]
tab = {(L, s): htree(L, q["die_um"], n_ff, s, q["layer"], q["imb"], f=f) for L in LV for s in SZ}
h = tab[(q["levels"], q["size"])]
vals = dict(die_mm=q["die_um"] / 1e3, n_ff=n_ff, f_MHz=f / 1e6, L=q["levels"], size=q["size"], imb_pct=q["imb"] * 100,
            leaves=h["leaves"], n_per=h["n_per"], n_buf=h["n_buf"], ins_ps=h["insertion"] * 1e12, tree_ps=h["t_tree"] * 1e12,
            leaf_ps=h["t_leaf"] * 1e12, skew_ps=h["skew"] * 1e12, ratio=h["ratio"], p_mw=h["power"] * 1e3, pff_mw=h["p_ff"] * 1e3,
            cff_fF=ff_clk_cap() * 1e15, wire_mm=h["wire_um"] / 1e3, c_wire_pF=(h["c_wire"] + h["c_local"]) * 1e12,
            c_buf_pF=h["c_buf"] * 1e12, c_ff_pF=h["c_ff"] * 1e12, c_tot_pF=h["c_total"] * 1e12)
for L in LV:
    a = tab[(L, 16)]
    vals[f"ins{L}"], vals[f"skew{L}"], vals[f"p{L}"], vals[f"r{L}"] = a["insertion"] * 1e12, a["skew"] * 1e12, a["power"] * 1e3, a["ratio"]
a1 = tab[(1, 4)]
vals.update(ins1_4_ns=a1["insertion"] * 1e9, skew1_4_ns=a1["skew"] * 1e9, ins1_4=a1["insertion"] * 1e12, skew1_4=a1["skew"] * 1e12, n_per1=a1["n_per"],
            ins1_32=tab[(1, 32)]["insertion"] * 1e12, skew1_32=tab[(1, 32)]["skew"] * 1e12)
a4 = tab[(4, 32)]
vals.update(ins4_32=a4["insertion"] * 1e12, r4_32=a4["ratio"], p4_32=a4["power"] * 1e3)
out(**vals)

plt = style()
fig, ax = plt.subplots(figsize=(4.6, 4.6))


def hdraw(x, y, half, lev, maxlev):
    if lev > maxlev:
        ax.plot(x, y, "s", color=d.MEAN, ms=3)
        return
    lw = 2.6 - 0.5 * lev
    ax.plot([x - half, x + half], [y, y], color=d.NMOS, lw=lw)
    for xx in (x - half, x + half):
        ax.plot([xx, xx], [y - half, y + half], color=d.NMOS, lw=lw)
        for yy in (y - half, y + half):
            hdraw(xx, yy, half / 2, lev + 1, maxlev)


hdraw(0, 0, 0.25, 1, 3)
ax.plot(0, 0, "o", color=d.PMOS, ms=7)
ax.text(0.02, 0.03, T("时钟入口", "clock in"), fontsize=9, color=d.PMOS)
ax.add_patch(__import__("matplotlib").patches.Rectangle((-0.5, -0.5), 1, 1, fill=False, ec=d.MUTED, lw=1))
ax.set_xlim(-0.55, 0.55); ax.set_ylim(-0.55, 0.55); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig8_4_1")

fig, (a1x, a2x) = plt.subplots(1, 2, figsize=(8.0, 3.0))
a1x.plot(LV, [tab[(L, 16)]["insertion"] * 1e12 for L in LV], "o-", color=d.NMOS, label=T("插入延时", "insertion delay"))
a1x.plot(LV, [tab[(L, 16)]["skew"] * 1e12 for L in LV], "s-", color=d.PMOS, label=T("偏斜（某区多 20 %）", "skew (+20 % in one region)"))
a1x.set_yscale("log"); a1x.set_xticks(LV); a1x.set_xlabel(T("H 树层数 L", "H-tree levels L")); a1x.set_ylabel("ps")
a1x.legend(fontsize=8, frameon=False); d.spines(a1x)
a2x.bar([L - 0.2 for L in LV], [tab[(L, 16)]["p_ff"] * 1e3 for L in LV], width=0.4, color=d.MUTED, label=T("触发器", "flip-flops"))
a2x.bar([L + 0.2 for L in LV], [(tab[(L, 16)]["power"] - tab[(L, 16)]["p_ff"]) * 1e3 for L in LV], width=0.4, color=d.LOAD,
        label=T("导线与缓冲器", "wires and buffers"))
a2x.set_xticks(LV); a2x.set_xlabel(T("H 树层数 L", "H-tree levels L")); a2x.set_ylabel(T("时钟功耗 / mW", "clock power / mW"))
a2x.legend(fontsize=8, frameon=False); d.spines(a2x)
fig.tight_layout()
figure(fig, "fig8_4_2")
