"""8.8 曲梁：机器人点焊钳（C 形钳体）的弯曲段。电极夹紧力 F 把钳体的两臂往外撑，C 形弯段的截面同时受弯矩 M = F·e 和拉力 N = F。
钳体尺寸是本书设定的示意值：矩形截面 b × h = 20 × 60 mm，内半径 ri = 50 mm，电极力 3 kN，电极力作用线到截面形心的距离 250 mm。
比较三种算法：直梁公式 σ = N/A ± Mc/I；曲梁的温克勒–巴赫公式；纯弯部分用弹性力学的精确解（铁木辛柯）、加上 N/A。
再看曲率越大（rc/h 越小）直梁公式的误差有多大（算例 8.8.1，图 8.8.1）。"""
import numpy as np

import _ch8 as H
from bookout import T, figure, out, style

b, h, ri = 20.0, 60.0, 50.0
ro = ri + h
F, ARM = 3000.0, 250.0
M, N = F * ARM, F
A, I = b * h, b * h ** 3 / 12
rc = (ri + ro) / 2
rn, e, s_in_wb, s_out_wb = H.curved_rect(ri, ro, b, M, N)
s_in_st, s_out_st = N / A + M * (h / 2) / I, N / A - M * (h / 2) / I
ex_in, ex_out = H.curved_exact_pure(ri, ro, b, M)
s_in_ex, s_out_ex = ex_in + N / A, ex_out + N / A
# 误差随 rc/h
ratios = np.linspace(0.6, 10, 120)
err = []
for k in ratios:
    rci = k * h
    a_, c_ = rci - h / 2, rci + h / 2
    win, _ = H.curved_exact_pure(a_, c_, b, 1.0)
    err.append(((h / 2) / I) / win)          # 直梁公式的内侧应力 / 精确解
err = np.array(err)
k_here = rc / h

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
r = np.linspace(ri, ro, 100)
s_wb = M * (rn - r) / (A * e * r) + N / A
s_st = N / A + M * (rc - r) / I
a0.plot(s_wb, r, color="#d62728", lw=1.4, label=T("曲梁（温克勒–巴赫）", "curved beam (Winkler–Bach)"))
a0.plot(s_st, r, color="#1f77b4", lw=1.2, ls="--", label=T("直梁公式", "straight-beam formula"))
a0.plot([s_in_ex, s_out_ex], [ri, ro], "ko", ms=3.5, label=T("精确解（内、外侧）", "exact (inner, outer)"))
a0.axvline(0, color=H.MUTED, lw=0.5)
a0.axhline(rn, color="#d62728", lw=0.5, ls=":")
a0.axhline(rc, color="#1f77b4", lw=0.5, ls=":")
a0.text(s_out_wb, rn + 1, T(" 纯弯的中性轴 rₙ", " neutral axis rₙ (pure bending)"), fontsize=6.2, color="#d62728")
a0.set_xlabel(T("周向正应力 / MPa", "Circumferential stress / MPa"), fontsize=7.2)
a0.set_ylabel(T("半径 r / mm（内侧在下）", "Radius r / mm (inside at bottom)"), fontsize=7.2)
a0.legend(fontsize=6.0, frameon=False, loc="upper right")
a0.tick_params(labelsize=6.3)
a0.set_title(T("(a) 点焊钳弯段截面上的应力", "(a) Stress across the gun's curved section"), fontsize=7.4)
a1.plot(ratios, 100 * (1 - err), color="#1f77b4", lw=1.3)
a1.axvline(k_here, color="#d62728", lw=0.7, ls="--")
a1.text(k_here + 0.1, 100 * (1 - np.interp(k_here, ratios, err)) + 2, T(f"本例 rc/h = {k_here:.2f}", f"this case rc/h = {k_here:.2f}"), fontsize=6.4, color="#d62728")
a1.set_xlabel(T("rc / h（曲率半径 / 截面高）", "rc / h (radius of curvature / depth)"), fontsize=7.2)
a1.set_ylabel(T("直梁公式低估内侧应力 / %", "Inner stress underestimated by straight formula / %"), fontsize=6.8)
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) 弯得越厉害，直梁公式越不保守（纯弯）", "(b) The sharper the bend, the more unsafe the straight formula (pure bending)"), fontsize=7.0)
fig.tight_layout()
figure(fig, "fig8_8_1")

out(b=b, h=h, ri=ri, ro=ro, rc=rc, F=F / 1000, arm=ARM, M=M / 1e6, A=A, rn=rn, e=e, s_in_wb=s_in_wb, s_out_wb=s_out_wb, s_in_st=s_in_st,
    s_out_st=s_out_st, s_in_ex=s_in_ex, s_out_ex=s_out_ex, k=k_here, under=100 * (1 - s_in_st / s_in_wb), err_wb=100 * abs(s_in_wb - s_in_ex) / s_in_ex,
    k5=float(100 * (1 - np.interp(5, ratios, err))), k1=float(100 * (1 - np.interp(1, ratios, err))))
