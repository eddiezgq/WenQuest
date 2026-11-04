"""11.6 变幅载荷：雨流计数与迈因纳法则——WQ-CR5 大臂的寿命。

算例 11.6.1  WQ-CR5 带 5 kg 跑标准动作（4.8 s 一个节拍，_ch11.py：多体动力学 → 端面载荷 → 有限元单位工况叠加），
            大臂 J2 端法兰内角的最危险点、最危险的面（临界平面，11.5 节）上的正应力历程：
            雨流计数（数字工厂 fatigue.rainflow）→ 每个循环古德曼修正 → S–N 曲线（材料库 6061-T6，精车 β、尺寸 0.85，
            数字工厂 fatigue.compute）→ 迈因纳累积。寿命要求：两班（每天 16 h）、每年 250 天、5 年（本书设定）。
            三种累积：原始迈因纳（低于 S_D 不计）、海巴赫（低于 S_D 斜率 2k − 1）、“最大一个循环 × 全部次数”的粗算；
算例 11.6.2  载荷还能放大多少：所有载荷乘 λ（更快的动作、更重的负载的粗略代表），损伤刚好在 5 年用完的 λ；
            数字工厂现在的做法（静态冯·米塞斯 × |M|，11.5 节）给出的 λ 作对照；
图 11.6.1。
"""
import math

import numpy as np

import _ch11 as H
from bookout import T, figure, out, style

R = H.heavy()
t, L6, L0 = R["t"], R["L6"], R["L0"]
TCYC = float(t[-1])
U = R["U"]["J2"]
F = H.field(U, L6, L0)
ip, nvec, ang, sn = H.critical_plane(U, F, "J2")

N_LIFE = H.cycles_per_life(TCYC)                         # 5 年的节拍数
LIFE_H = H.SHIFT_H * H.DAYS * H.YEARS
cyc = H.FT.rainflow(sn)
D_h, s_h = H.damage(sn, haibach=True)
D_m, s_m = H.damage(sn, haibach=False)
# 粗算：最大一个循环（古德曼修正后）× 每个节拍的循环数
sa_eq_max = s_h["sa_eq"]
N_max = H.AL["N_D"] * (s_h["S_D"] / sa_eq_max) ** H.AL["k"] if sa_eq_max >= s_h["S_D"] else \
    H.AL["N_D"] * (s_h["S_D"] / sa_eq_max) ** (2 * H.AL["k"] - 1)
n_real = int(np.sum(cyc[:, 0] > 0.1))                  # 幅值大于 0.1 MPa 的循环（其余是停顿时数值上的微小波动）
D_rough = n_real / N_max


lam_h = H.lam_for_life(lambda x: x * sn, N_LIFE)
lam_m = H.lam_for_life(lambda x: x * sn, N_LIFE, haibach=False)
Mabs = np.linalg.norm(L6[3:], axis=0)
M0 = float(np.linalg.norm(L0[3:]))
Dfac, _ = H.FT.compute(F["vm0"], M0, list(Mabs), TCYC, H.AL, "fine_turned", 0.85, 1.0, True)
ia = int(np.argmax(Dfac))
lam_fac = H.lam_for_life(lambda x: x * F["vm0"][ia] * Mabs / M0, N_LIFE)
# λ = lam_h 时每个循环的损伤贡献（“头”与“尾”）
scaled = lam_h * cyc
S_D = s_h["S_D"]
k = H.AL["k"]
contrib = []
for a, m in scaled:
    sa_eq = a / (1 - min(abs(m) / H.AL["ultimate_mpa"], 0.999))
    N = H.AL["N_D"] * (S_D / sa_eq) ** (k if sa_eq >= S_D else 2 * k - 1)
    contrib.append((sa_eq, N_LIFE / N))
contrib.sort(key=lambda x: -x[0])
D_tot = sum(c[1] for c in contrib)
share_top = contrib[0][1] / D_tot * 100
n_above = sum(1 for c in contrib if c[0] >= S_D)
share_above = sum(c[1] for c in contrib if c[0] >= S_D) / D_tot * 100

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
a0.plot(t, sn, color="#1f77b4", lw=1.1)
a0.set_xlabel(T("时间 / s", "Time / s"), fontsize=7.0)
a0.set_ylabel(T("临界平面上的正应力 / MPa", "Normal stress on the critical plane / MPa"), fontsize=7.0)
a0.tick_params(labelsize=6.2)
a0.set_title(T("(a) J2 端内角最危险点，一个节拍（{:.1f} s）".format(TCYC), "(a) Worst point, J2-end corner, one cycle ({:.1f} s)".format(TCYC)),
             fontsize=7.0)
xs = np.arange(1, len(contrib) + 1)
a1.plot(xs, [c[0] for c in contrib], "o", color="#1f77b4", ms=3)
a1.set_ylim(0, S_D * 1.7)
a1.axhline(S_D, color="#d62728", lw=0.9, ls="--")
a1.text(len(contrib) * 0.6, S_D * 1.05, T("S_D = {:.1f} MPa".format(S_D), "S_D = {:.1f} MPa".format(S_D)), fontsize=6.3, color="#d62728")
a1.annotate(T("这一个循环占总损伤的 {:.4f}%".format(share_top), "this one cycle: {:.4f}% of the damage".format(share_top)),
            (1, contrib[0][0]), textcoords="offset points", xytext=(10, 2), fontsize=6.3)
a1.set_xlabel(T("每个节拍里的循环（按等效应力幅从大到小）", "Cycles in one block (by equivalent amplitude)"), fontsize=7.0)
a1.set_ylabel(T("古德曼等效应力幅 / MPa", "Goodman equivalent amplitude / MPa"), fontsize=7.0)
a1.tick_params(labelsize=6.2)
a1.set_title(T("(b) 载荷放大 λ = {:.1f} 倍（5 年刚好用完）".format(lam_h), "(b) Loads scaled by λ = {:.1f} (life used up in 5 years)".format(lam_h)),
             fontsize=7.0)
fig.tight_layout()
figure(fig, "fig11_6_1")

out(t_cycle=TCYC, n_cyc=len(cyc), N_life=N_LIFE, life_h=LIFE_H, th=math.degrees(F["theta"][ip]), ph=F["phi"][ip], ang=ang,
    sa_max=float(cyc[:, 0].max()), sm_at=float(cyc[int(np.argmax(cyc[:, 0])), 1]), sa_eq_max=sa_eq_max, S_D=S_D, S_fat=s_h["S_fat"],
    D_h=D_h, D_m=D_m, D_rough=D_rough, D_life_h=D_h * N_LIFE, life_blocks_h=1 / D_h if D_h > 0 else 0.0,
    life_years_h=(1 / D_h) * TCYC / 3600 / (H.SHIFT_H * H.DAYS) if D_h > 0 else 0.0,
    lam_h=lam_h, lam_m=lam_m, lam_fac=lam_fac, lam_ratio=lam_fac / lam_h, share_top=share_top, n_above=n_above,
    D_exp=math.floor(math.log10(D_h)), yrs_exp=math.floor(math.log10((1 / D_h) * TCYC / 3600 / (H.SHIFT_H * H.DAYS))),
    rough_ratio=D_rough / D_h, share_above=share_above, n_real=n_real, k2=2 * k - 1, smax=float(sn.max()), smin=float(sn.min()))
