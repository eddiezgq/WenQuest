"""本章第一幅图（`fig25_1_1`）：各走各的会撞在哪里，协调过的路长什么样。

图 `fig25_1_1`：（a）四台搬运车各自跑 A\\*——代价正好等于下界，但撞了好几处；
（b）冲突搜索给出的无冲突解，代价与**穷举证明的最优值**一样。
"""
from _ch25 import (GRID_WORKSHOP, Grid, cbs, find_conflicts, makespan, optimal_joint,
                   plan_independent, sum_of_costs, trim)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
AGV = (C["x"], C["z"], C["y"], C["accent"])

grid = Grid(GRID_WORKSHOP)
STARTS = [(7, 5), (3, 1), (4, 6), (2, 11)]
GOALS = [(4, 9), (8, 1), (6, 9), (6, 10)]

ind = plan_independent(grid, STARTS, GOALS)
conf = find_conflicts(ind)
sol, _ = cbs(grid, STARTS, GOALS)
sol = trim(sol)
_, opt_cost, _ = optimal_joint(grid, STARTS, GOALS, metric="soc")
lb = int(sum(grid.dist(s, g) for s, g in zip(STARTS, GOALS)))


def draw_map(ax):
    """货架、通道、充电位。行号往下增，所以把纵轴翻过来。"""
    for r in range(grid.h):
        for c in range(grid.w):
            if GRID_WORKSHOP[r][c] == "#":
                ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1,
                                           facecolor="#d9dde0", edgecolor="none"))
            else:
                ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, facecolor="none",
                                           edgecolor="#eceff1", lw=0.6))
    for (r, c) in grid.chargers:
        ax.add_patch(plt.Rectangle((c - 0.35, r - 0.35), 0.7, 0.7, facecolor="none",
                                   edgecolor=C["muted"], lw=1.1, ls=":"))
        ax.annotate(T("充", "chg"), xy=(c, r), ha="center", va="center", fontsize=6.5,
                    color=C["muted"])
    ax.set_xlim(-0.6, grid.w - 0.4)
    ax.set_ylim(grid.h - 0.4, -0.6)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(False)


def draw_paths(ax, paths):
    for i, p in enumerate(paths):
        off = (i - 1.5) * 0.14
        xs = [c + off for (_, c) in p]
        ys = [r + off for (r, _) in p]
        ax.plot(xs, ys, "-", color=AGV[i], lw=1.9, alpha=0.9, zorder=3,
                solid_capstyle="round")
        ax.plot(xs[0], ys[0], "o", color=AGV[i], ms=7, zorder=4)
        ax.plot(xs[-1], ys[-1], "*", color=AGV[i], ms=13, zorder=4)
        ax.annotate(f"{i}", xy=(xs[0], ys[0]), xytext=(0, 0), textcoords="offset points",
                    ha="center", va="center", fontsize=6, color="white", zorder=5)


fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.6))

# ---------------- (a) 各走各的
draw_map(a)
draw_paths(a, ind)
spots: dict = {}
for kind, i, j, where, t in conf:
    cell = where if kind == "vertex" else where[1]
    spots.setdefault(cell, []).append(t)
for k, (cell, ts) in enumerate(sorted(spots.items())):
    a.plot(cell[1], cell[0], "x", color="#b00020", ms=12, mew=2.4, zorder=6)
    dx = 16 if k % 2 == 0 else -16
    a.annotate("t=" + ",".join(str(t) for t in sorted(set(ts))),
               xy=(cell[1], cell[0]), xytext=(dx, 0), textcoords="offset points",
               ha="left" if dx > 0 else "right", va="center", fontsize=7.5,
               color="#b00020", zorder=7,
               bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
a.set_title(T(f"(a) 各车各跑 A*：sum-of-costs {sum_of_costs(ind)} 步 = 下界 {lb} 步，"
              f"但有 {len(conf)} 处冲突",
              f"(a) independent A*: sum-of-costs {sum_of_costs(ind)} = lower bound {lb}, "
              f"but {len(conf)} conflicts"), fontsize=9.5)
a.annotate(T("× 是撞点（点冲突或换位冲突）；圆点起点、星号终点",
             "× marks a conflict (vertex or swap); dot = start, star = goal"),
           xy=(0.5, -0.02), xycoords="axes fraction", ha="center", va="top",
           fontsize=8, color=C["muted"])

# ---------------- (b) 冲突搜索
draw_map(b)
draw_paths(b, sol)
b.set_title(T(f"(b) 冲突搜索：sum-of-costs {sum_of_costs(sol)} 步 = 穷举证明的最优，"
              f"0 处冲突", f"(b) conflict-based search: sum-of-costs {sum_of_costs(sol)} "
              f"= proven optimum, 0 conflicts"), fontsize=9.5)
b.annotate(T(f"协调的代价 = {opt_cost - lb} 步（最优 {opt_cost} − 下界 {lb}）；"
             f"makespan {makespan(sol)} 步",
             f"price of coordination = {opt_cost - lb} steps (optimum {opt_cost} − "
             f"bound {lb}); makespan {makespan(sol)}"),
           xy=(0.5, -0.02), xycoords="axes fraction", ha="center", va="top",
           fontsize=8, color=C["accent"])

fig.tight_layout()
figure(fig, "fig25_1_1")
