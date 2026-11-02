"""7.3 节：寄存器堆与 FIFO。

算例 7.3.1  多端口寄存器堆：每多一个端口，单元多一条字线、一条位线（各占一个走线间距 track），单元面积怎样随端口数涨（粗估）。
算例 7.3.2  电流采样 FIFO：ADC 每秒写入 f_in 个 16 位采样，处理器每隔 t_svc 来取一次，取的时候每秒读 f_rd 个。
            逐个时钟模拟 2 ms，记录 FIFO 里的最多个数，定深度（取 2 的幂）与指针位数；
            比较用触发器（sky130_fd_sc_hd 的 D 触发器约 20 μm²）与用 SRAM 单元（4.32 μm²，加外围）存这些数据的面积。
图 7.3.1    FIFO 里数据个数随时间的变化（锯齿形）。
"""
import math

from bookout import T, figure, out, style
from mos import P, sram_access
import _draw as d

q = P["problems"]["p73"]
c = P["problems"]["p71"]
# ---------------- 算例 7.3.1 多端口单元（粗估）
tr = q["track_um"]
ports = q["ports"]
a1 = c["cell_w"] * c["cell_h"]
areas = {p: (c["cell_w"] + (p - 1) * tr) * (c["cell_h"] + (p - 1) * tr) for p in ports}
vals = {f"rf_a{p}": areas[p] for p in ports}
vals.update({f"rf_x{p}": areas[p] / a1 for p in ports}, track=tr)

# ---------------- 算例 7.3.2 FIFO
f_in, t_svc, f_rd, wd = q["f_in_MHz"] * 1e6, q["t_svc_us"] * 1e-6, q["f_rd_MHz"] * 1e6, q["word"]
dt = 1 / f_rd                       # 以读时钟为步长
T_sim = 2e-3
n_steps = int(T_sim / dt)
occ, mx, trace = 0, 0, []
next_w, next_svc, serving = 1 / f_in, t_svc, False
for k in range(n_steps):
    t = k * dt
    if t >= next_w - 1e-15:
        occ += 1
        next_w += 1 / f_in
    if not serving and t >= next_svc - 1e-15:
        serving = True
    if serving:
        if occ > 0:
            occ -= 1
        if occ == 0:
            serving = False
            next_svc += t_svc
    mx = max(mx, occ)
    if k % 20 == 0 and t < 1e-4:
        trace.append((t * 1e6, occ))
depth = 1 << math.ceil(math.log2(mx + 1))
ptr_bits = int(math.log2(depth)) + 1
bits = depth * wd
ff_area = bits * q["ff_area"]
rows = 64 if depth * wd >= 64 * 64 else depth
sr = sram_access(rows, bits // rows, wd)
drain_us = (f_in * t_svc) / (f_rd - f_in) * 1e6
peak_later = f_in * (t_svc - drain_us * 1e-6)
vals.update(peak_later=peak_later, t_in_us=1 / q["f_in_MHz"], f_in_MHz=q["f_in_MHz"], t_svc_us=q["t_svc_us"], f_rd_MHz=q["f_rd_MHz"], word=wd, fill=f_in * t_svc, max_occ=mx, depth=depth,
            ptr_bits=ptr_bits, fifo_bits=bits, ff_area=q["ff_area"], ff_mm2=ff_area / 1e6, sram_mm2=sr["area"] / 1e6,
            sram_rows=rows, sram_cols=bits // rows, ff_vs_sram=ff_area / sr["area"], drain_us=drain_us,
            cell_vs_ff=q["ff_area"] / a1)
out(**vals)

plt = style()
fig, ax = plt.subplots(figsize=(7.2, 2.8))
ax.step([a for a, _ in trace], [b for _, b in trace], where="post", color=d.NMOS, lw=1.4)
ax.axhline(depth, color=d.LOAD, ls=":", lw=1.2)
ax.text(trace[-1][0], depth - 4, T(f"深度 {depth}", f"depth {depth}"), ha="right", va="top", fontsize=9, color=d.LOAD)
ax.set_xlabel(T("时间 / μs", "time / μs")); ax.set_ylabel(T("FIFO 中的数据个数", "words in the FIFO"))
ax.set_ylim(0, depth * 1.12)
d.spines(ax)
figure(fig, "fig7_3_1")
