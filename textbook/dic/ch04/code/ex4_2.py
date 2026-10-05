"""4.2 节：RC 延时——Elmore 延时与分布式 RC 线。

算例 4.2.1  1 mm 长的 met2 最小线宽导线，一端接理想阶跃电压源，另一端开路：把它当作一个集总 RC（0.69RC）、
            用 Elmore 延时（RC/2）和把线切成很多小段数值求解，三种方法给出的末端 50 % 延时。
算例 4.2.2  时钟缓冲器（20 倍参考反相器）经 1 mm 主干分出两条支线，送到近处（0.4 mm）和远处（1.6 mm）两个计数器，
            每个计数器的时钟负载约 20 个参考反相器。用 Elmore 延时估计两个计数器收到时钟的时间和二者之差（时钟偏斜），
            与数值解比较。
图 4.2.1    均匀 RC 线末端的阶跃响应：集总模型与分段数值解（段数 1、2、4、50）。
"""
import numpy as np

from bookout import T, figure, out, style
from mos import P, VDD, Wmin, cin, gamma_self, r_ratio, req_n, req_p, wire_c, wire_r
from _rc import Tree, t50
import _draw as d

# ---------------------------------------------------------------- 算例 4.2.1
w = 0.14
Lm = 1000
Rw, Cw = wire_r("met2", w) * Lm, wire_c("met2", w) * Lm
RC = Rw * Cw
res = {}
for n in (1, 2, 4, 50):
    tr = Tree(1e-3, 0.0)                         # 近似理想电压源：驱动电阻 1 mΩ
    if n == 1:
        end = tr.add(0, Rw, Cw)                  # 集总：全部电阻串一个、全部电容放在末端
    else:
        end = tr.wire(0, Rw, Cw, n)
    ts, V = tr.step(VDD, 3 * RC, 6000)
    res[n] = (ts, V[:, end])
    out(**{f"t50_n{n}": t50(ts, V[:, end], VDD) / RC})
out(Rw=Rw, Cw_ff=Cw * 1e15, RC_ps=RC * 1e12, lumped_ps=0.69 * RC * 1e12, elmore_ps=RC / 2 * 1e12,
    dist_ps=t50(*res[50], VDD) * 1e12)

# ---------------------------------------------------------------- 算例 4.2.2
q = P["problems"]["p42"]
r = r_ratio()
R0 = (req_n(Wmin) + req_p(r * Wmin)) / 2
C0 = cin(Wmin, r * Wmin)
size = q["driver_size"]
Rd, Cself = R0 / size, gamma_self() * C0 * size
CL = q["leaf_load_units"] * C0
lay, ww = q["layer"], q["w_um"]
seg = lambda Lum: (wire_r(lay, ww) * Lum, wire_c(lay, ww) * Lum)  # noqa: E731
tr = Tree(Rd, Cself)
j = tr.wire(0, *seg(q["trunk_um"]), 40)
near = tr.wire(j, *seg(q["near_um"]), 20)
tr.C[near] += CL
far = tr.wire(j, *seg(q["far_um"]), 60)
tr.C[far] += CL
el = tr.elmore()
ts, V = tr.step(VDD, 6 * el[far], 6000)
tn, tf = t50(ts, V[:, near], VDD), t50(ts, V[:, far], VDD)
out(Rd=Rd, CL_ff=CL * 1e15, el_near_ps=el[near] * 1e12, el_far_ps=el[far] * 1e12, el_skew_ps=(el[far] - el[near]) * 1e12,
    est_near_ps=0.69 * el[near] * 1e12, est_far_ps=0.69 * el[far] * 1e12, est_skew_ps=0.69 * (el[far] - el[near]) * 1e12,
    sim_near_ps=tn * 1e12, sim_far_ps=tf * 1e12, sim_skew_ps=(tf - tn) * 1e12,
    err_far_pct=(1 - 0.69 * el[far] / tf) * 100, err_near_pct=(0.69 * el[near] / tn - 1) * 100)

# ---------------------------------------------------------------- 图 4.2.1
plt = style()
fig, ax = plt.subplots(figsize=(5.8, 3.4))
styles = {1: (d.LOAD, "--", T("集总（1 段）", "lumped (1 section)")), 2: (d.MUTED, ":", T("2 段", "2 sections")),
          4: (d.PMOS, "-.", T("4 段", "4 sections")), 50: (d.NMOS, "-", T("50 段（接近分布式）", "50 sections (≈ distributed)"))}
for n, (ts, v) in res.items():
    c, ls, name = styles[n]
    ax.plot(ts / RC, v, color=c, ls=ls, lw=1.8, label=name)
ax.axhline(VDD / 2, color=d.MUTED, lw=0.8)
for x, txt in ((0.69, "0.69RC"), (0.38, "0.38RC")):
    ax.axvline(x, color=d.INK, lw=0.6, ls=":")
    ax.text(x + 0.02, 0.15, txt, fontsize=8.5)
ax.set_xlim(0, 2.5); ax.set_ylim(0, 1.9)
ax.set_xlabel(T("时间 / RC", "time / RC")); ax.set_ylabel(T("末端电压 / V", "far-end voltage / V"))
ax.legend(fontsize=8.5, frameon=False, loc="lower right")
d.spines(ax)
figure(fig, "fig4_2_1")
