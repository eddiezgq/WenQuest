"""4.3 节：插入中继器。

算例 4.3.1  3 mm 长的 met1 最小线宽时钟线，末端负载 20 个参考反相器。一个 20 倍反相器直接驱动整条线的延时；
            按闭式解求中继器的最优段数 k 与尺寸，再在整数 k、整数尺寸上搜索最小延时。
算例 4.3.2  同一条线改走 met3（最小线宽）：还需要中继器吗？
图 4.3.1    总延时随段数 k 的变化（met1，几种中继器尺寸；met3 对照）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from mos import P, Wmin, cin, r_ratio, repeater_delay, repeater_opt, wire_c, wire_r
import _draw as d

q = P["problems"]["p43"]
L, lay, w = q["L_um"], q["layer"], q["w_um"]
C0 = cin(Wmin, r_ratio() * Wmin)
CL = q["load_units"] * C0

t_direct = repeater_delay(L, lay, w, 1, 20, CL)
k_opt, s_opt = repeater_opt(L, lay, w)
best = min(((repeater_delay(L, lay, w, k, s, CL), k, s) for k in range(1, 11) for s in range(1, 81)))
out(L_mm=L / 1000, t_direct_ps=t_direct * 1e12, k_opt=k_opt, s_opt=s_opt, t_best_ps=best[0] * 1e12, k_best=best[1], s_best=best[2],
    save_pct=(1 - best[0] / t_direct) * 100, Rw_k=wire_r(lay, w) * L / 1e3, Cw_ff=wire_c(lay, w) * L * 1e15,
    seg_mm=L / best[1] / 1000)
# 每毫米的延时：中继后与线长成正比
t_per_mm = best[0] / (L / 1000)
out(t_per_mm_ps=t_per_mm * 1e12)
# 6 mm：不加中继器与加中继器
L2 = 2 * L
t2_direct = repeater_delay(L2, lay, w, 1, 20, CL)
b2 = min(((repeater_delay(L2, lay, w, k, s, CL), k, s) for k in range(1, 16) for s in range(1, 81)))
out(t2_direct_ps=t2_direct * 1e12, t2_best_ps=b2[0] * 1e12, k2_best=b2[1], direct_ratio=t2_direct / t_direct, rep_ratio=b2[0] / best[0])

# 算例 4.3.2：met3
w3 = 0.3
t3_direct = repeater_delay(L, "met3", w3, 1, 20, CL)
k3, s3 = repeater_opt(L, "met3", w3)
# 同样用 20 倍的中继器比较段数（尺寸不设上限时，搜索会让第一级越大越好——前一级驱动它的代价没有计入）
t3 = {k: repeater_delay(L, "met3", w3, k, 20, CL) for k in (1, 2, 3)}
out(t3_direct_ps=t3_direct * 1e12, k3_opt=k3, s3_opt=s3, t3_k2_ps=t3[2] * 1e12, t3_k3_ps=t3[3] * 1e12)

# 图 4.3.1
plt = style()
fig, ax = plt.subplots(figsize=(5.8, 3.5))
ks = np.arange(1, 9)
for s, col in ((10, d.MUTED), (20, d.NMOS), (40, d.PMOS)):
    ax.plot(ks, [repeater_delay(L, lay, w, k, s, CL) * 1e12 for k in ks], "o-", color=col, lw=1.6, ms=4,
            label=T(f"met1，中继器 {s} 倍", f"met1, repeaters {s}×"))
ax.plot(ks, [repeater_delay(L, "met3", w3, k, 20, CL) * 1e12 for k in ks], "s--", color=d.MEAN, lw=1.6, ms=4,
        label=T("met3，中继器 20 倍", "met3, repeaters 20×"))
ax.plot([best[1]], [best[0] * 1e12], "o", ms=11, mfc="none", mec=d.INK, mew=1.4)
ax.set_xlabel(T("段数 k（中继器个数）", "number of segments k (repeaters)"))
ax.set_ylabel(T("总延时 / ps", "total delay / ps"))
ax.set_ylim(0, None)
ax.legend(fontsize=8.5, frameon=False, ncol=2, loc="lower right")
d.spines(ax)
figure(fig, "fig4_3_1")
