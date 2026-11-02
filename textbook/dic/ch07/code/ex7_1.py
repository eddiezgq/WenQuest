"""7.1 节：存储器的组织。

算例 7.1.1  控制芯片的 4 KB 数据缓冲（32768 位，每次读一个 32 位字）排成 rows 行 × cols 列（cols = 32768/rows，列选比 M = cols/32）。
            按“译码 + 字线 + 位线 + 灵敏放大 + 列选与输出”估算存取时间，并估算面积与长宽；行数取 64～1024。
算例 7.1.2  位线只摆 100 mV：与位线放电到 VDD/2 相比，时间和每次读的位线能量各差多少（256 行 × 128 列）。
图 7.1.1    存储阵列的组织：行译码、字线、位线、灵敏放大器与列选。
图 7.1.2    各种划分的存取时间分段（堆叠条形图）与面积。
"""
import math

from bookout import T, figure, out, style
from mos import P, VDD, sram_access, tau, fo4_tp, r_ratio, sa_time, Wmin, Cg
import _draw as d

q = P["problems"]["p71"]
S = P["sram_sim"]
bits, word = q["bits"], q["word"]
ROWS = [64, 128, 256, 512, 1024]
res = {R: sram_access(R, bits // R, word, q["dv"]) for R in ROWS}
best = min(ROWS, key=lambda R: res[R]["total"])
small = min(ROWS, key=lambda R: res[R]["area"])
vals = dict(bits=bits, kbytes=bits / 8 / 1024, word=word, cell_w=q["cell_w"], cell_h=q["cell_h"], cell_a=q["cell_w"] * q["cell_h"],
            dec_w=q["dec_w"], col_h=q["col_h"], dv_mV=q["dv"] * 1e3, best=best, best_cols=bits // best, small=small,
            tau_ps=tau() * 1e12, fo4_ps=fo4_tp(r_ratio()) * 1e12, i_read_uA=S["i_read"] * 1e6, c_cell_fF=S["c_cell"] * 1e15,
            sa100_ps=sa_time(0.1) * 1e12, sa50_ps=sa_time(0.05) * 1e12, sa25_ps=sa_time(0.025) * 1e12)
for R in ROWS:
    a = res[R]
    for k in ("dec", "wl", "bl", "sa", "out", "total"):
        vals[f"{k}{R}"] = a[k] * 1e12
    vals[f"area{R}"] = a["area"] / 1e6           # mm²
    vals[f"w{R}"], vals[f"h{R}"], vals[f"mux{R}"], vals[f"N{R}"] = a["w_um"], a["h_um"], a["mux"], a["dec_N"]
    vals[f"cbl{R}"] = a["c_bl"] * 1e15
    vals[f"cwl{R}"] = a["c_wl"] * 1e15
vals["ff_area"] = P["problems"]["p73"]["ff_area"]
vals["ff_mm2"] = bits * vals["ff_area"] / 1e6
vals["cells_eff"] = bits * q["cell_w"] * q["cell_h"] / 1e6 / res[small]["area"] * 1e6 * 100   # 单元占面积的百分比
vals["tall_x"] = res[1024]["total"] / res[best]["total"]
vals["wide_x"] = res[64]["total"] / res[best]["total"]
vals["dec_share"] = res[best]["dec"] / res[best]["total"] * 100
vals["tall_bl_x"] = res[1024]["bl"] / res[best]["bl"]
vals["aspect1024"] = res[1024]["h_um"] / res[1024]["w_um"]

# 算例 7.1.2：256 行 × 128 列，位线摆 100 mV 与放电到 VDD/2
R, C = 256, 128
a = res[R]
t_small = a["bl"]
t_half = S["t_bl0"] + a["c_bl"] * (VDD / 2) / S["i_read"]           # 粗估：读电流按常数（实际电流随位线电压下降而变小）
e_small = C * a["c_bl"] * VDD * q["dv"]                 # 整条字线上的单元都在放电，预充时由电源补回
e_half = C * a["c_bl"] * VDD * (VDD / 2)
vals.update(t_bl0_ps=S["t_bl0"] * 1e12, cbl_dev256=a["c_bl_dev"] * 1e15, cbl_wire256=a["c_bl_wire"] * 1e15,
            wire_share=a["c_bl_wire"] / a["c_bl"] * 100, t_small=t_small * 1e12, t_half=t_half * 1e12, t_ratio=t_half / t_small, e_small_pJ=e_small * 1e12,
            e_half_pJ=e_half * 1e12, e_ratio=e_half / e_small, cbl256=a["c_bl"] * 1e15,
            wl_load_cells=2 * C, c_pg_fF=Wmin * Cg * 1e15)
out(**vals)

# ---------------------------------------------------------------- 图 7.1.1 阵列的组织
plt = style()
import matplotlib.patches as mp  # noqa: E402
fig, ax = plt.subplots(figsize=(7.4, 4.6))
x0, y0, W_, H_ = 2.2, 1.6, 6.0, 4.0
ax.add_patch(mp.Rectangle((x0, y0), W_, H_, fill=False, ec=d.INK, lw=1.2))
nr, nc = 6, 8
for i in range(nr):                                          # 字线
    y = y0 + (i + 0.5) * H_ / nr
    ax.plot([x0 - 0.1, x0 + W_], [y, y], color=d.PMOS if i == 2 else d.MUTED, lw=1.6 if i == 2 else 0.6)
for j in range(nc):                                          # 位线对
    x = x0 + (j + 0.5) * W_ / nc
    for dx in (-0.12, 0.12):
        ax.plot([x + dx, x + dx], [y0 - 0.05, y0 + H_], color=d.NMOS if j == 5 else d.MUTED, lw=1.4 if j == 5 else 0.5)
for i in range(nr):
    for j in range(nc):
        x, y = x0 + (j + 0.5) * W_ / nc, y0 + (i + 0.5) * H_ / nr
        ax.add_patch(mp.Rectangle((x - 0.2, y - 0.16), 0.4, 0.32, fill=True, color=d.MEAN if (i == 2 and j == 5) else "#d9dee2", zorder=3))
ax.add_patch(mp.Rectangle((0.3, y0), 1.6, H_, fill=False, ec=d.INK, lw=1.0))
ax.text(1.1, y0 + H_ / 2, T("行\n译码器", "row\ndecoder"), ha="center", va="center", fontsize=10)
ax.add_patch(mp.Rectangle((x0, 0.2), W_, 1.1, fill=False, ec=d.INK, lw=1.0))
ax.text(x0 + W_ / 2, 0.95, T("预充 · 灵敏放大器 · 列选（M 选 1）", "precharge · sense amplifiers · column mux (M:1)"), ha="center", fontsize=9.5)
ax.text(x0 + W_ / 2, 0.45, T("→ 数据输出（一个字）", "→ data out (one word)"), ha="center", fontsize=9.5, color=d.MUTED)
ax.annotate(T("行地址", "row address"), xy=(1.1, y0 + H_ + 0.05), xytext=(1.1, y0 + H_ + 0.7), ha="center", fontsize=9.5,
            arrowprops=dict(arrowstyle="->", color=d.INK, lw=0.8))
ax.text(x0 + W_ + 0.15, y0 + 2.5 * H_ / nr, T("字线", "word line"), color=d.PMOS, fontsize=9.5, va="center")
ax.text(x0 + 5.5 * W_ / nc, y0 + H_ + 0.12, T("位线对", "bit-line pair"), color=d.NMOS, fontsize=9.5, ha="center")
ax.text(x0 + W_ / 2, y0 + H_ + 0.55, T("rows 行 × cols 列 存储单元", "rows × cols memory cells"), ha="center", fontsize=10)
ax.set_xlim(0, 9.8); ax.set_ylim(0, 6.6); ax.axis("off")
figure(fig, "fig7_1_1")

# ---------------------------------------------------------------- 图 7.1.2 存取时间分段与面积
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.6, 3.4), gridspec_kw={"width_ratios": [1.6, 1]})
parts = [("dec", T("译码", "decode"), d.NMOS), ("wl", T("字线", "word line"), "#7fb3e0"), ("bl", T("位线", "bit line"), d.PMOS),
         ("sa", T("灵敏放大", "sense amp"), d.LOAD), ("out", T("列选与输出", "mux & output"), d.MEAN)]
xs = range(len(ROWS))
bottom = [0.0] * len(ROWS)
for k, lab, col in parts:
    v = [res[R][k] * 1e12 for R in ROWS]
    a1.bar(xs, v, bottom=bottom, color=col, width=0.62, label=lab)
    bottom = [b + x for b, x in zip(bottom, v)]
for i, R in enumerate(ROWS):
    a1.text(i, bottom[i] + 12, f"{bottom[i]:.0f}", ha="center", fontsize=9)
a1.set_xticks(list(xs)); a1.set_xticklabels([f"{R}×{bits // R}" for R in ROWS], fontsize=9)
a1.set_xlabel(T("行 × 列", "rows × columns")); a1.set_ylabel(T("存取时间 / ps", "access time / ps"))
a1.set_ylim(0, max(bottom) * 1.18); a1.legend(fontsize=8, ncol=3, loc="upper left", frameon=False)
d.spines(a1)
a2.bar(xs, [res[R]["area"] / 1e6 for R in ROWS], color=d.MUTED, width=0.62)
for i, R in enumerate(ROWS):
    a2.text(i, res[R]["area"] / 1e6 + 0.003, f"{res[R]['area'] / 1e6:.3f}", ha="center", fontsize=8)
a2.set_xticks(list(xs)); a2.set_xticklabels([str(R) for R in ROWS], fontsize=9)
a2.set_xlabel(T("行数", "rows")); a2.set_ylabel(T("面积 / mm²", "area / mm²"))
a2.set_ylim(0, max(res[R]["area"] for R in ROWS) / 1e6 * 1.15)
d.spines(a2)
fig.tight_layout()
figure(fig, "fig7_1_2")
