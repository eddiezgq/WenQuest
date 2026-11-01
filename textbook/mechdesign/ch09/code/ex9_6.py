"""9.6 薄壁结构与局部失稳。

算例 9.6.1  UR5e 小臂管 Ø75（6061-T6）：壁厚从 3 mm 减到 0.3 mm，受弯时管壁局部屈曲的临界应力（经典值乘 NASA SP-8007 的折减系数）
            与屈服强度比较——壁厚小于多少时局部屈曲先于屈服；与 8.4 节的工作应力（肘关节处，末端 5 kg）比较；
算例 9.6.2  AGV 底盘的承载顶板（Q235 钢板，长 600、宽 200、厚 2 mm，本书设定）：底盘受弯时顶板沿长度方向均匀受压，四边按简支的屈曲应力；
            在宽度中间沿长度方向点焊一根扁钢做加强筋（厚 2 mm、高 h_s），用里茨法（双正弦级数，板和筋的应变能一起算）求屈曲应力随筋高的变化，
            找出筋要多高才能把板分成两块各自屈曲（屈曲应力达到无筋时的 4 倍）。筋的惯性矩取 t·h_s³/3（绕板中面，偏大，是上限）；
图 9.6.1。
"""
import math

import numpy as np
from scipy.linalg import eigh

import _ch9 as H
from bookout import T, figure, out, style

# ---------------------------------------------------------------- 算例 9.6.1
AL = H.mat("6061-T6")
D = 75.0
R = D / 2
ts = np.linspace(0.3, 3.0, 271)
cr = np.array([H.tube_local_cr(AL["E"], AL["nu"], t, R - t / 2)[0] for t in ts])
cl = np.array([H.tube_local_cr(AL["E"], AL["nu"], t, R - t / 2, knock=False)[0] for t in ts])
r5 = H.arm_sag(5.0)
M_elbow = r5["T3"] * 1e3                                   # N·mm：肘关节处的弯矩（= 小臂以外对肘的力矩）
sig = np.array([M_elbow / (H.I_tube(D, t) / R) for t in ts])
t_y = float(ts[np.argmin(abs(cr - AL["sy"]))])
Rt_y = (R - t_y / 2) / t_y
cr2, g2 = H.tube_local_cr(AL["E"], AL["nu"], 2.0, R - 1.0)
sig2 = M_elbow / (H.I_tube(D, 2.0) / R)

# ---------------------------------------------------------------- 算例 9.6.2
ST = H.mat("Q235")
E, nu = ST["E"], ST["nu"]
a, b, t = 600.0, 200.0, 2.0
Dp = E * t ** 3 / (12 * (1 - nu ** 2))
k0 = H.plate_k(a / b)
s0 = H.plate_cr(E, nu, t, b, k0)
k_half = H.plate_k(a / (b / 2))
s_half = H.plate_cr(E, nu, t, b / 2, k_half)


def ritz(hs, M=8, N=9):
    """四边简支板 + y = b/2 处一道筋（矩形 t × hs，绕板中面的惯性矩 t hs³/3），沿 x 受压、板和筋同一应力。返回屈曲应力 MPa"""
    Is, As = t * hs ** 3 / 3, t * hs
    best = 1e9
    ns = np.arange(1, N + 1)
    sn = np.sin(ns * math.pi / 2)
    for m in range(1, M + 1):
        am = m * math.pi / a
        Kp = np.diag(Dp * a * b / 4 * (am ** 2 + (ns * math.pi / b) ** 2) ** 2)
        Ks = E * Is * a / 2 * am ** 4 * np.outer(sn, sn)
        Gp = np.diag(t * a * b / 4 * am ** 2 * np.ones(N))
        Gs = As * a / 2 * am ** 2 * np.outer(sn, sn)
        lam = eigh(Kp + Ks, Gp + Gs, eigvals_only=True)[0]
        best = min(best, lam)
    return best


hss = np.linspace(0, 30, 61)
sr = np.array([ritz(x) for x in hss])
s_r0 = ritz(0.0)
hs_need = float(np.interp(0.98 * s_half, sr, hss))
s15 = ritz(15.0)

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
a0.plot(ts, cr, color="#d62728", lw=1.5, label=T("局部屈曲应力（含折减）", "local buckling stress (knocked down)"))
a0.plot(ts, cl, color="#d62728", lw=0.8, ls=":", label=T("经典值（不折减）", "classical value"))
a0.axhline(AL["sy"], color="#1f77b4", lw=1.0, ls="--", label=T(f"屈服强度 {AL['sy']:.0f} MPa", f"yield strength {AL['sy']:.0f} MPa"))
a0.plot(ts, sig, color="#2ca02c", lw=1.3, label=T("肘关节处的弯曲应力（5 kg）", "bending stress at the elbow (5 kg)"))
a0.axvline(t_y, color=H.MUTED, lw=0.6, ls="--")
a0.text(t_y + 0.05, 1500, f"t = {t_y:.2f} mm", fontsize=6.2, color=H.MUTED)
a0.set_yscale("log")
a0.set_ylim(2, 5000)
a0.set_xlabel(T("壁厚 t / mm（外径 75 mm）", "Wall thickness t / mm (OD 75 mm)"), fontsize=7.2)
a0.set_ylabel(T("应力 / MPa", "Stress / MPa"), fontsize=7.2)
a0.legend(fontsize=5.8, frameon=False, loc="lower right")
a0.tick_params(labelsize=6.3)
a0.set_title(T("(a) 小臂管：多薄时管壁先局部屈曲", "(a) Forearm tube: when the wall buckles first"), fontsize=7.3)
a1.plot(hss, sr, color="#1f77b4", lw=1.5, label=T("里茨法（板 + 筋）", "Ritz (plate + stiffener)"))
a1.axhline(s0, color="#d62728", lw=0.8, ls=":", label=T(f"无筋，k = {k0:.2f}", f"no stiffener, k = {k0:.2f}"))
a1.axhline(s_half, color="#2ca02c", lw=0.8, ls="--", label=T("分成两块各自屈曲（上限）", "two half-panels buckle (upper bound)"))
a1.axhline(ST["sy"], color=H.MUTED, lw=0.8, ls="-.", label=T(f"屈服强度 {ST['sy']:.0f} MPa", f"yield strength {ST['sy']:.0f} MPa"))
a1.set_xlabel(T("加强筋高度 h_s / mm（厚 2 mm）", "Stiffener height h_s / mm (2 mm thick)"), fontsize=7.2)
a1.set_ylabel(T("屈曲应力 / MPa", "Buckling stress / MPa"), fontsize=7.2)
a1.set_ylim(0, s_half * 1.15)
a1.legend(fontsize=5.8, frameon=False, loc="center right")
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) AGV 顶板：加一道筋", "(b) AGV deck plate: one stiffener"), fontsize=7.3)
fig.tight_layout()
figure(fig, "fig9_6_1")

out(D=D, sy_al=AL["sy"], M_elbow=M_elbow / 1e3, t_y=t_y, Rt_y=Rt_y, cr2=cr2, g2=g2, sig2=sig2, ratio2=cr2 / sig2,
    a=a, b=b, t=t, sy_st=ST["sy"], k0=k0, s0=s0, k_half=k_half, s_half=s_half, s_r0=s_r0, err_r0=abs(s_r0 / s0 - 1) * 100,
    hs_need=hs_need, s15=s15, r15=s15 / s0, S0=ST["sy"] / s0, pct15=15.0 * t / (b * t) * 100)
