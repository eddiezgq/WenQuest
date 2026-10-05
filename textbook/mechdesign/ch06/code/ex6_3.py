"""6.3 钣金：XM540 舵机支架（5052 铝板，厚 2 mm，一次 90° 折弯）的展开长度——折弯余量 BA = θ(r + Kt)；
直接按外形尺寸相加会多出多少；K 因子取值的影响。算例 6.3.1，图 6.3.1。"""
import math

from matplotlib.patches import Arc, Circle, Rectangle

import _ch6 as H
from bookout import T, figure, out, style

s = H.sheet()
t, r = s["t"], s["r"]
naive = H.BASE_L + H.UP_H                       # 直接把两条外边相加
inside = (H.BASE_L - t) + (H.UP_H - t)          # 按内侧尺寸相加
err_naive = naive - s["L_flat"]
err_inside = inside - s["L_flat"]
k_lo, k_hi = 0.25, 0.45
dL_k = H.bend_allowance(t, r, 90, k_hi) - H.bend_allowance(t, r, 90, k_lo)
MIN_FLANGE = 4 * t                              # 最短翻边（常用指南 ≥ 4t；准确值按下模 V 口宽度，约 V/2 + t）
HOLE_EDGE = 2 * t + r                           # 孔到折弯线的最小距离（经验 ≥ 2t + r，孔才不被拉变形）

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.4, 1.0]})
W = H.B_WIDTH
a0.add_patch(Rectangle((0, 0), s["L_flat"], W, fc="#eaf3ea", ec=H.INK, lw=0.9))
x_b0, x_b1 = s["flat_base"], s["flat_base"] + s["BA"]
for xb in (x_b0, x_b1):
    a0.plot([xb, xb], [0, W], color=H.MUTED, lw=0.6, ls="--")
a0.plot([(x_b0 + x_b1) / 2] * 2, [0, W], color="#d62728", lw=0.8, ls=(0, (6, 2, 1, 2)))
for k in range(H.N_HOLE_BASE):
    a0.add_patch(Circle((12 + (k % 2) * 22, W / 2 + (-1) ** (k // 2) * 16), H.D_HOLE_BASE / 2, fc="white", ec=H.INK, lw=0.7))
for k in range(H.N_HOLE_UP):
    a0.add_patch(Circle((x_b1 + 12 + (k % 2) * 28, W / 2 + (-1) ** (k // 2) * 12), H.D_HOLE_UP / 2, fc="white", ec=H.INK, lw=0.7))
a0.annotate("", xy=(s["L_flat"], -5), xytext=(0, -5), arrowprops=dict(arrowstyle="<->", lw=0.6))
a0.text(s["L_flat"] / 2, -6, T(f"展开长 {s['L_flat']:.1f}", f"flat length {s['L_flat']:.1f}"), ha="center", va="top", fontsize=6.8)
a0.text((x_b0 + x_b1) / 2, W + 2, T(f"折弯区 BA = {s['BA']:.2f}", f"bend allowance {s['BA']:.2f}"), ha="center", fontsize=6.6, color="#d62728")
a0.set_xlim(-5, s["L_flat"] + 5)
a0.set_ylim(-14, W + 8)
a0.set_aspect("equal")
a0.axis("off")
a0.set_title(T("(a) 展开图（激光切割的外形和孔）", "(a) Flat pattern (laser-cut outline and holes)"), fontsize=7.8)
# (b) 折弯后的侧视
ri, ro = r, r + t
a1.add_patch(Rectangle((ro, 0), H.BASE_L - ro, t, fc="#cfe3cf", ec=H.INK, lw=0.8))
a1.add_patch(Rectangle((0, ro), t, H.UP_H - ro, fc="#cfe3cf", ec=H.INK, lw=0.8))
a1.add_patch(Arc((ro, ro), 2 * ro, 2 * ro, theta1=180, theta2=270, lw=0.8, color=H.INK))
a1.add_patch(Arc((ro, ro), 2 * ri, 2 * ri, theta1=180, theta2=270, lw=0.8, color=H.INK))
a1.add_patch(Arc((ro, ro), 2 * (ri + H.K_FACTOR * t), 2 * (ri + H.K_FACTOR * t), theta1=180, theta2=270, lw=0.8, color="#d62728", ls="--"))
a1.text(ro + 3, ro + 3, T(f"中性层 r + Kt\nK = {H.K_FACTOR}", f"neutral axis r + Kt\nK = {H.K_FACTOR}"), fontsize=6.4, color="#d62728")
a1.text(H.BASE_L / 2, -4, f"{H.BASE_L:.0f}", ha="center", va="top", fontsize=6.8)
a1.text(-3, H.UP_H / 2, f"{H.UP_H:.0f}", ha="right", va="center", fontsize=6.8)
a1.set_xlim(-12, H.BASE_L + 4)
a1.set_ylim(-10, H.UP_H + 4)
a1.set_aspect("equal")
a1.axis("off")
a1.set_title(T(f"(b) 折弯后（t = {t:.0f}，内半径 r = {r:.0f}）", f"(b) Bent (t = {t:.0f}, inner radius r = {r:.0f})"), fontsize=7.8)
fig.tight_layout()
figure(fig, "fig6_3_1")

out(t=t, r=r, K=H.K_FACTOR, BA=s["BA"], L_flat=s["L_flat"], base=H.BASE_L, up=H.UP_H, width=H.B_WIDTH, naive=naive, inside=inside,
    err_naive=err_naive, err_inside=err_inside, k_lo=k_lo, k_hi=k_hi, dL_k=dL_k, min_flange=MIN_FLANGE, hole_edge=HOLE_EDGE,
    mass_g=s["mass"] * 1000, cut_len=s["cut_len"])
