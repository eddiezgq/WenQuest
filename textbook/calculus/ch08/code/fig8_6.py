"""图 8.6.1：自动微分的计算图——r = √(l₁² + l₂² + 2l₁l₂ cos θ₂)：前向模式每个节点同时带着值与导数。"""
import math

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _traj import ur5e_links

l1, l2 = ur5e_links()
t2 = math.radians(60)
v1 = math.cos(t2)
d1 = -math.sin(t2)
v2 = l1 * l1 + l2 * l2 + 2 * l1 * l2 * v1
d2 = 2 * l1 * l2 * d1
v3 = math.sqrt(v2)
d3 = d2 / (2 * v3)
nodes = [("θ₂", f"{t2:.4f}", "1", 0.6),
         ("u = cos θ₂", f"{v1:.4f}", f"−sin θ₂ · 1 = {d1:.4f}", 3.4),
         ("w = l₁² + l₂² + 2l₁l₂u", f"{v2:.4f}", f"2l₁l₂ · u′ = {d2:.4f}", 6.6),
         ("r = √w", f"{v3:.4f}", f"w′/(2√w) = {d3:.4f}", 9.8)]
fig, ax = plt.subplots(figsize=(12, 3.2))
for i, (name, v, d, x) in enumerate(nodes):
    ax.add_patch(plt.Rectangle((x - 1.3, 0.25), 2.6, 1.5, fc="#eef3fa", ec=BLUE, lw=1.5))
    ax.text(x, 1.45, name, ha="center", fontsize=10)
    ax.text(x, 1.0, T(f"值 {v}", f"value {v}"), ha="center", fontsize=9, color=INK)
    ax.text(x, 0.55, T(f"导数 {d}", f"deriv. {d}"), ha="center", fontsize=8.5, color=RED)
    if i:
        ax.annotate("", xy=(x - 1.3, 1.0), xytext=(nodes[i - 1][3] + 1.3, 1.0), arrowprops=dict(arrowstyle="->", color=INK))
ax.set_xlim(-1, 11.4)
ax.set_ylim(0, 2)
ax.axis("off")
ax.set_title(T("前向模式：每一步按局部求导公式把导数往后传（θ₂ = 60°，长度单位 m）", "Forward mode: each step passes the derivative on (θ₂ = 60°, lengths in m)"), fontsize=10)
fig.tight_layout()
figure(fig, "fig8_6_1")
