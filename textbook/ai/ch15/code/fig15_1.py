"""15.1 节的示意图。

图 15.1.1：（a）小车间里每个格子的价值与最优动作（箭头），油污格与墙画出来；
（b）价值迭代每一轮的误差：按 γ 的幂往下掉，γ 越接近 1 掉得越慢。
"""
import numpy as np

from _ch15 import ACTIONS, shop_mdp, value_iteration
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

P, R, idx, g, start, goal = shop_mdp()
H, W = g.shape
V, pi, iters, deltas = value_iteration(P, R, 0.95)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.2, 4.2))

grid = np.full((H, W), np.nan)
for c, s in idx.items():
    if c != goal:                                  # 出口是吸收态，价值为 0，画进来反而让色阶看不清
        grid[c] = V[s]
im = a.imshow(grid, cmap="RdYlBu_r")
for c, s in idx.items():
    if c == goal:
        a.add_patch(plt.Rectangle((c[1] - 0.5, c[0] - 0.5), 1, 1, color=C["z"], alpha=0.85))
        a.text(c[1], c[0], T("出口", "exit"), ha="center", va="center", fontsize=9, color="white")
        continue
    di, dj = ACTIONS[pi[s]]
    a.arrow(c[1], c[0], dj * 0.3, di * 0.3, head_width=0.14, color="black", alpha=0.75)
    if g[c] == "o":
        a.text(c[1], c[0] - 0.33, T("油污", "oil"), ha="center", fontsize=7, color=C["x"])
for i in range(H):
    for j in range(W):
        if g[i, j] == "#":
            a.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color=C["muted"]))
a.text(start[1], start[0] - 0.33, T("入口", "start"), ha="center", fontsize=8)
a.set_xticks([])
a.set_yticks([])
a.set_title(T("(a) 每个格子值多少，往哪走", "(a) Value of each cell and the best move"), fontsize=10)
fig.colorbar(im, ax=a, fraction=0.046, pad=0.04, label=T("价值", "value"))

for gm, col in ((0.5, C["y"]), (0.8, C["z"]), (0.95, C["x"]), (0.99, C["ink"])):
    _, _, it, d = value_iteration(P, R, gm)
    b.semilogy(np.arange(1, len(d) + 1), np.maximum(d, 1e-12), "o-", ms=3, color=col,
               label=T(f"γ = {gm}", f"γ = {gm}"))
b.semilogy(np.arange(1, 15), 20 * 0.95 ** np.arange(1, 15), color=C["muted"], ls="--", lw=1.0,
           label=T("$20\\cdot\\gamma^k$（γ = 0.95）", "$20\\cdot\\gamma^k$ (γ = 0.95)"))
b.set_ylim(1e-3, 60)
b.set_xlabel(T("迭代轮数", "iteration"))
b.set_ylabel(T("这一轮价值变了多少", "change in value this round"))
b.set_title(T("(b) 每一轮的误差按 γ 的幂往下掉", "(b) The error shrinks by a factor of γ each round"), fontsize=10)
b.legend(fontsize=8)
b.grid(alpha=0.25, lw=0.5, which="both")

fig.tight_layout()
figure(fig, "fig15_1_1")
