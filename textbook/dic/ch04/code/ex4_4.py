"""4.4 节：串扰与耦合。

算例 4.4.1  编码器信号线（受害线）与一条 PWM 信号线（干扰线）在 met2 上以最小间距平行走 500 μm。
            求耦合电容和受害线对地电容；受害线悬空（如动态节点）时，干扰线跳变 1.8 V 引起的最坏电压跳动；
            受害线由最小反相器保持在 0 时，干扰线以 100 ps 的边沿跳变，受害线上的峰值噪声。
算例 4.4.2  三种办法的效果：间距加倍、受害线的驱动加大到 4 倍、两线之间插一条接地的屏蔽线。
图 4.4.1    受害线峰值噪声随间距的变化（三种驱动强度），对照 1.2 节的噪声容限。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from mos import P, VDD, Wmin, cin, noise_margins, r_ratio, wire_cc, xtalk, WIRES
import _draw as d

q = P["problems"]["p44"]
lay, w, Lw = q["layer"], q["w_um"], q["len_um"]
r = r_ratio()
C0 = cin(Wmin, r * Wmin)
s0 = WIRES[lay]["smin"]
tr = q["tr_ps"] * 1e-12
nm = noise_margins(Wmin, r * Wmin)
NM = min(nm["NML"], nm["NMH"])


def noise(s, size, tr=tr):
    """受害线：对地电容 Cg（面积 + 两侧边缘，邻线对边缘电容的屏蔽忽略不计）+ 接收端 1 个参考反相器；耦合 Cc。
    悬空时 ΔV = VDD·Cc/(Cc + Cg)；有驱动（电阻 R）时，斜坡跳变注入的峰值 VDD·Cc/(Cc+Cg)·(τ/tr)(1 − e^(−tr/τ))，τ = R(Cc + Cg)。
    算法在 conventions/mos.py 的 xtalk()，与实验 4.4 共用。"""
    return xtalk(lay, w, s, Lw, size, tr)


Cc, Cg, dv_float, dv1, tau1 = noise(s0, 1)
out(Cc_ff=Cc * 1e15, Cg_ff=Cg * 1e15, ratio=Cc / (Cc + Cg), ratio_pct=Cc / (Cc + Cg) * 100, dv_float=dv_float, dv1=dv1, tau1_ps=tau1 * 1e12, NM=NM,
    s0=s0, tr_ps=q["tr_ps"], len_um=Lw)
_, _, _, dv_2s, _ = noise(2 * s0, 1)
_, _, _, dv_4x, tau4 = noise(s0, 4)
Cc2 = wire_cc(lay, 2 * s0) * Lw
out(dv_2s=dv_2s, Cc2_ff=Cc2 * 1e15, dv_4x=dv_4x, tau4_ps=tau4 * 1e12)
# 屏蔽：两线之间插一条接地线，受害线与干扰线之间的耦合近似消失，原耦合电容变成对屏蔽线（地）的电容
dv_shield = 0.0
Cg_shield = Cg + wire_cc(lay, s0) * Lw
out(Cg_shield_ff=Cg_shield * 1e15, shield_delay_pct=(Cg_shield / Cg - 1) * 100)
# 对延时的影响：干扰线反向跳变时，耦合电容的效果加倍（米勒系数 2），同向时为 0
for m in (0, 1, 2):
    out(**{f"cmiller{m}_ff": (Cg + m * Cc) * 1e15})
both_dv2 = noise(2 * s0, 4)[3]
out(dv_both=both_dv2)

# 图 4.4.1
plt = style()
fig, ax = plt.subplots(figsize=(5.8, 3.4))
ss = np.linspace(s0, 6 * s0, 60)
for size, col in ((1, d.PMOS), (2, d.LOAD), (4, d.NMOS)):
    ax.plot(ss, [noise(s, size)[3] for s in ss], color=col, lw=1.8, label=T(f"受害线驱动 {size} 倍", f"victim driver {size}×"))
ax.plot(ss, [noise(s, 1)[2] for s in ss], color=d.MUTED, lw=1.2, ls="--", label=T("受害线悬空", "floating victim"))
ax.axhline(NM, color=d.INK, lw=0.9, ls=":")
ax.text(6 * s0, NM + 0.03, T(f"噪声容限 {NM:.2f} V", f"noise margin {NM:.2f} V"), fontsize=8.5, ha="right")
ax.set_xlabel(T("两线间距 / μm", "spacing / μm")); ax.set_ylabel(T("受害线峰值噪声 / V", "peak noise on victim / V"))
ax.set_ylim(0, 1.3)
ax.legend(fontsize=8.5, frameon=False, loc="upper right")
d.spines(ax)
figure(fig, "fig4_4_1")
