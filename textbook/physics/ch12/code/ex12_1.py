"""12.1 节的计算：

算例 12.1.1  机械臂的肘关节在 1.0 s 内转过 90°，角速度曲线为梯形（加速、减速各 0.25 s）。求最大角速度、角加速度；
            离关节 0.60 m 的工具点的最大线速度、切向加速度和法向加速度（图 12.1.1）。
算例 12.1.2  关节电机上装 17 位绝对值编码器（每转 2¹⁷ 个读数），经传动比 100 的减速器驱动关节。关节转角的分辨率多少弧度？
            离关节 0.80 m 处对应多大的位移？
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

dth, Tm, ta, r = math.pi / 2, 1.0, 0.25, 0.60
wmax = dth / (Tm - ta)
al = wmax / ta
out(wmax=wmax, al=al, rpm=wmax * 60 / (2 * math.pi), v_tip=wmax * r, at_tip=al * r, an_tip=wmax ** 2 * r, r=r,
    a_tot=math.hypot(al * r, wmax ** 2 * r))

bits, i, R = 17, 100, 0.80
res = 2 * math.pi / (2 ** bits * i)
out(counts=2 ** bits, res_urad=res * 1e6, res_um=res * R * 1e6, res_deg=math.degrees(res) * 3600)

t = np.linspace(0, Tm, 1001)
w = np.where(t < ta, al * t, np.where(t < Tm - ta, wmax, al * (Tm - t)))
a = np.where(t < ta, al, np.where(t < Tm - ta, 0.0, -al))
plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.8))
a1.plot(t, w, color=d.VA, lw=2); a1.set_xlabel(T("时间 / s", "time / s")); a1.set_ylabel(T("角速度 ω / (rad/s)", "angular speed ω / (rad/s)")); d.spines(a1)
a1.set_title(T("(a) 关节角速度", "(a) joint angular speed"), fontsize=9.5)
a2.plot(t, a * r, color=d.VR, lw=2, label=T("切向 rα", "tangential rα"))
a2.plot(t, w ** 2 * r, color=d.VB, lw=2, label=T("法向 ω²r", "normal ω²r"))
a2.axhline(0, color=d.MUTED, lw=0.6)
a2.set_xlabel(T("时间 / s", "time / s")); a2.set_ylabel(T("工具点加速度 / (m/s²)", "tool-point acceleration / (m/s²)")); a2.legend(frameon=False, fontsize=8); d.spines(a2)
a2.set_title(T("(b) 离关节 0.60 m 处的加速度", "(b) acceleration 0.60 m from the joint"), fontsize=9.5)
fig.tight_layout()
figure(fig, "fig12_1_1")
