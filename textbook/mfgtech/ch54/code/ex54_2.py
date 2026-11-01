"""算例 54.2.1–54.2.3：原理误差与调整误差（hub/accuracy.py 的 nose_radius_error、chord_length、chord_error、adjustment_error）。
54.2.1：刀尖圆弧半径 r = 0.8 的车刀按假想刀尖编程、不用刀尖圆弧半径补偿，车 C2 倒角（45°）和 30° 锥面时多留的材料厚度；
54.2.2：数控系统用直线段逼近 R30 圆弧，弦高误差不超过 0.002 时允许的段长；
54.2.3：SH-301 工序 60 按试磨件的均值调整，σ = 0.0012，试磨 1、5 件时的调整误差（横进给最小补偿量 0.002）。
画图 54.2.1（刀尖圆弧未补偿）、54.2.2（弦差）、54.2.3（调整误差与试切件数）。"""
import math

import _mfg as M
from bookout import T, figure, out, style

A = M.acc()
p = M.plan()
r = 0.8
e45, e30 = A.nose_radius_error(r, 45), A.nose_radius_error(r, 30)
Rarc, tol = 30.0, 0.002
s_max = A.chord_length(Rarc, tol)
assert abs(A.chord_error(Rarc, s_max) - tol) < 1e-9
sig = 0.0012
a1 = A.adjustment_error(sig, 1, 0.0, 0.002)
a5 = A.adjustment_error(sig, 5, 0.0, 0.002)
op60 = M.op(p, 60)
adj = next(i for i in op60["accuracy"][0]["items"] if i["name"].startswith("调整误差"))
assert abs(adj["range"] - round(a5["total"], 4)) < 1e-9, "工艺规程工序 60 登记的调整误差应等于按 5 件试磨算出的值"

plt = style()
# ---- 图 54.2.1：C2 倒角，刀尖圆弧 r = 0.8，按假想刀尖 P 沿理论倒角线编程
fig, ax = plt.subplots(figsize=(5.6, 4.2))
c = 2.0
extra = (2 - math.sqrt(2)) * r                       # 实际轮廓线 u + v = c + extra
ax.fill([-1.5, 0, c, c, -1.5], [c, c, 0, -1.5, -1.5], color="#f0d9bf", zorder=0)
ax.fill([0, extra, c, c], [c, c, extra, 0], color="#e8a98f", zorder=1)
ax.plot([-1.5, 0, c, c], [c, c, 0, -1.5], color=M.INK, lw=1.2, label=T("图纸轮廓（C2 倒角）", "drawing profile (C2 chamfer)"))
ax.plot([extra, c], [c, extra], color=M.RED, lw=1.4, ls="--", label=T("实际车出的倒角", "chamfer actually cut"))
for t in (0.25, 0.5, 0.75):
    P = (c * t, c * (1 - t))
    C = (P[0] + r, P[1] + r)
    th = [2 * math.pi * i / 100 for i in range(101)]
    ax.plot([C[0] + r * math.cos(a) for a in th], [C[1] + r * math.sin(a) for a in th], color=M.ACCENT, lw=0.8)
    ax.plot([P[0]], [P[1]], "o", color=M.ACCENT, ms=3)
ax.plot([0.5, 0.5 + r], [1.5, 1.5], color=M.ACCENT, lw=0.6, ls=":")
ax.plot([0.5, 0.5], [1.5, 1.5 + r], color=M.ACCENT, lw=0.6, ls=":")
ax.text(0.52, 1.38, T("假想刀尖 P", "imaginary tip P"), fontsize=7.5, color=M.ACCENT, va="top")
ax.text(1.45, 1.95, T("刀尖圆弧 r = 0.8", "nose radius r = 0.8"), fontsize=7.5, color=M.ACCENT)
ax.annotate(T(f"多留 {e45:.2f} mm（法向）", f"{e45:.2f} mm left (normal)"), xy=(1.0 + extra / 2, 1.0 + extra / 2), xytext=(2.2, 1.2),
            fontsize=7.5, color=M.RED, arrowprops=dict(arrowstyle="-", color=M.RED, lw=0.6))
ax.text(-1.4, 1.75, T("外圆", "OD"), fontsize=8)
ax.text(1.7, -1.3, T("端面", "end face"), fontsize=8, rotation=90)
ax.set_aspect("equal"); ax.set_xlim(-1.5, 3.4); ax.set_ylim(-1.5, 3.0)
ax.set_xlabel(T("轴向 / mm", "axial / mm")); ax.set_ylabel(T("径向 / mm", "radial / mm"))
ax.legend(fontsize=7.5, loc="lower left")
figure(fig, "fig54_2_1")

# ---- 图 54.2.2：直线段逼近圆弧的弦差
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.2), gridspec_kw={"width_ratios": [1, 1.2]})
ax = axs[0]
Rd, n = 1.0, 5                                      # 示意：每段 18°，弦差放大
th = [math.pi / 2 * i / 100 for i in range(101)]
ax.plot([Rd * math.cos(a) for a in th], [Rd * math.sin(a) for a in th], color=M.INK, lw=1.2)
pts = [(Rd * math.cos(math.pi / 2 * i / n), Rd * math.sin(math.pi / 2 * i / n)) for i in range(n + 1)]
ax.plot([q[0] for q in pts], [q[1] for q in pts], "o-", color=M.RED, ms=3, lw=1)
am = math.pi / 2 * 1.5 / n
ax.plot([0, Rd * math.cos(am)], [0, Rd * math.sin(am)], color=M.MUTED, lw=0.6, ls=":")
ax.text(0.08, 0.05, "R", fontsize=8)
ax.annotate(T("弦高 h", "chord height h"), xy=(0.93 * math.cos(am), 0.93 * math.sin(am)), xytext=(0.95, 0.95), fontsize=7.5,
            color=M.RED, arrowprops=dict(arrowstyle="-", color=M.RED, lw=0.6))
ax.text(1.03, 0.12, T("段长 s", "segment s"), fontsize=7.5, color=M.RED)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title(T("(a) 直线插补逼近圆弧（放大画）", "(a) linear segments on an arc (exaggerated)"), fontsize=8.5)
ax = axs[1]
ss = [0.05 * i for i in range(1, 41)]
for RR, col in ((10.0, M.WARM), (30.0, M.ACCENT), (100.0, M.GREEN)):
    ax.plot(ss, [A.chord_error(RR, x) * 1000 for x in ss], color=col, label=f"R = {RR:g} mm")
ax.axhline(tol * 1000, color=M.RED, ls="--", lw=0.8)
ax.plot([s_max], [tol * 1000], "o", color=M.RED, ms=4)
ax.text(s_max + 0.05, tol * 1000 + 0.3, f"s = {s_max:.2f} mm", fontsize=7.5, color=M.RED)
ax.set_xlabel(T("段长 s / mm", "segment length s / mm")); ax.set_ylabel(T("弦高误差 / µm", "chord error / µm"))
ax.set_ylim(0, 8); ax.legend(fontsize=7.5); ax.grid(lw=0.3, alpha=0.5)
ax.set_title(T("(b) h ≈ s²/(8R)", "(b) h ≈ s²/(8R)"), fontsize=8.5)
figure(fig, "fig54_2_2")

# ---- 图 54.2.3：调整误差与试切（试磨）件数
fig, ax = plt.subplots(figsize=(5.6, 3.0))
ns = list(range(1, 21))
ax.plot(ns, [A.adjustment_error(sig, k)["trial"] * 1000 for k in ns], "o-", ms=3, color=M.ACCENT, label=T("按试切件均值调整：6σ/√n", "from the mean of n trial parts: 6σ/√n"))
ax.plot(ns, [A.adjustment_error(sig, k, 0.0, 0.002)["total"] * 1000 for k in ns], "s-", ms=3, color=M.RED,
        label=T("再计入最小补偿量 0.002", "plus the 0.002 compensation step"))
ax.axhline(6 * sig * 1000, color=M.MUTED, ls=":", lw=0.8)
ax.text(14, 6 * sig * 1000 + 0.2, T("一件的分散 6σ", "spread of one part 6σ"), fontsize=7.5, color=M.MUTED)
ax.plot([5], [a5["total"] * 1000], "o", ms=7, mfc="none", mec=M.RED)
ax.text(5.5, a5["total"] * 1000 + 0.5, T("工序 60：试磨 5 件", "op 60: 5 trial parts"), fontsize=7.5, color=M.RED)
ax.set_xlabel(T("试切（试磨）件数 n", "trial parts n")); ax.set_ylabel(T("调整误差（范围）/ µm", "setting error (range) / µm"))
ax.set_ylim(0, 8.5); ax.set_xticks([1, 5, 10, 15, 20]); ax.legend(fontsize=7.5); ax.grid(lw=0.3, alpha=0.5)
figure(fig, "fig54_2_3")

out(r=r, e45=e45, e30=e30, s_max=s_max, a1=a1["total"], a1_trial=a1["trial"], a5=a5["total"], a5_trial=a5["trial"], sig=sig)
