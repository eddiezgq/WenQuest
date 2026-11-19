"""本章第三幅图（`fig25_3_1`）：等一等还是绕一绕——两种代价给出不同的选择。

图 `fig25_3_1`：（a）同一次相遇的两种消解：**等**（实线，只多一步等待）与
**绕**（虚线，远的那台车直走、近的那台车多绕八步）；
（b）穷举出来的帕累托前沿：makespan 最优与 sum-of-costs 最优**不是同一个解**。
"""
from _ch25 import (GRID_WORKSHOP, Grid, makespan, path_profile, sum_of_costs,
                   tradeoff_joint)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
AGV = (C["x"], C["z"])

grid = Grid(GRID_WORKSHOP)
STARTS = [(4, 6), (3, 5)]
GOALS = [(5, 3), (9, 11)]
front = tradeoff_joint(grid, STARTS, GOALS, t_max=20)
p_detour = front["paths_at"](front["mk_min"])          # makespan 最优 = 绕
p_wait = front["paths_at"](max(front["curve"]))        # sum-of-costs 最优 = 等
prof_wait = path_profile(grid, p_wait, STARTS, GOALS)
prof_detour = path_profile(grid, p_detour, STARTS, GOALS)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.5))

# ---------------- (a) 地图上的两种解
for r in range(grid.h):
    for c in range(grid.w):
        if GRID_WORKSHOP[r][c] == "#":
            a.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1,
                                      facecolor="#d9dde0", edgecolor="none"))
        else:
            a.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, facecolor="none",
                                      edgecolor="#eceff1", lw=0.6))
for i, (pw, pd) in enumerate(zip(p_wait, p_detour)):
    off = (i - 0.5) * 0.16
    a.plot([c + off for (_, c) in pw], [r + off for (r, _) in pw], "-",
           color=AGV[i], lw=2.2, alpha=0.95, zorder=3, solid_capstyle="round")
    a.plot([c - off for (_, c) in pd], [r - off for (r, _) in pd], "--",
           color=AGV[i], lw=2.0, alpha=0.85, zorder=3, dashes=(4, 2.4))
    a.plot(STARTS[i][1], STARTS[i][0], "o", color=AGV[i], ms=8, zorder=4)
    a.plot(GOALS[i][1], GOALS[i][0], "*", color=AGV[i], ms=14, zorder=4)
    a.annotate(f"{i}", xy=(STARTS[i][1], STARTS[i][0]), ha="center", va="center",
               fontsize=6.5, color="white", zorder=5)
wait_cell = [p for p, q in zip(p_wait[1][1:], p_wait[1][:-1]) if p == q]
if wait_cell:
    a.plot(wait_cell[0][1], wait_cell[0][0], "s", mfc="none", mec=C["z"], ms=16,
           mew=2.0, zorder=5)
    a.annotate(T("等 1 步", "wait 1 step"), xy=(wait_cell[0][1], wait_cell[0][0]),
               xytext=(14, 10), textcoords="offset points", fontsize=8.5, color=C["z"],
               arrowprops=dict(arrowstyle="->", color=C["z"], lw=1.0))
a.annotate(T(f"绕 {prof_detour[0][1]} 步", f"detour {prof_detour[0][1]} steps"),
           xy=(2.0, 7.4), fontsize=8.5, color=C["x"])
a.set_xlim(-0.6, grid.w - 0.4)
a.set_ylim(grid.h - 0.4, -0.6)
a.set_aspect("equal")
a.set_xticks([])
a.set_yticks([])
for side in ("top", "right", "bottom", "left"):
    a.spines[side].set_visible(False)
a.set_title(T("(a) 实线 = 等（总行程短），虚线 = 绕（最后一台车早到）",
              "(a) solid = wait (less travel), dashed = detour (earlier finish)"),
            fontsize=9.5)
a.annotate(T(f"近的那台（0 号）只要 {prof_wait[0][0]} 步；"
             f"远的那台（1 号）要 {prof_detour[1][0]} 步——谁有富余，谁去绕",
             f"car 0 needs {prof_wait[0][0]} steps, car 1 needs {prof_detour[1][0]}; "
             f"the one with slack takes the detour"),
           xy=(0.5, -0.02), xycoords="axes fraction", ha="center", va="top",
           fontsize=8, color=C["muted"])

# ---------------- (b) 帕累托前沿
ts = sorted(front["curve"])
cs = [front["curve"][t] for t in ts]
b.step(ts, cs, where="post", color=C["ink"], lw=2.0)
b.plot(front["mk_min"], front["curve"][front["mk_min"]], "o", color=C["x"], ms=11,
       zorder=4)
mk_of_wait = makespan(p_wait)
b.plot(mk_of_wait, front["soc_min"], "o", color=C["z"], ms=11, zorder=4)
b.annotate(T(f"绕：makespan {front['mk_min']}、sum-of-costs "
             f"{sum_of_costs(p_detour)}\n（makespan 最优）",
             f"detour: makespan {front['mk_min']}, sum-of-costs "
             f"{sum_of_costs(p_detour)}\n(makespan-optimal)"),
           xy=(front["mk_min"], front["curve"][front["mk_min"]]), xytext=(26, -40),
           textcoords="offset points", fontsize=8.5, color=C["x"], va="center",
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.1))
b.annotate(T(f"等：makespan {mk_of_wait}、sum-of-costs {front['soc_min']}\n"
             f"（sum-of-costs 最优）",
             f"wait: makespan {mk_of_wait}, sum-of-costs {front['soc_min']}\n"
             f"(sum-of-costs optimal)"),
           xy=(mk_of_wait, front["soc_min"]), xytext=(16, 24),
           textcoords="offset points", fontsize=8.5, color=C["z"],
           arrowprops=dict(arrowstyle="->", color=C["z"], lw=1.1))
b.set_xlim(front["mk_min"] - 0.8, mk_of_wait + 2.6)
b.set_xticks(list(range(front["mk_min"], mk_of_wait + 3)))
b.set_ylim(front["soc_min"] - 2.5, sum_of_costs(p_detour) + 3.5)
b.set_xlabel(T("makespan（步）：最后一台车到位的时刻",
               "makespan (steps): when the last car arrives"))
b.set_ylabel(T("sum-of-costs（步）：逐车到位时刻之和",
               "sum-of-costs (steps): per-car arrival times summed"))
b.set_title(T("(b) 穷举出来的帕累托前沿：只有两个点",
              "(b) the exhaustively computed Pareto front: just two points"), fontsize=10)
b.annotate(T(f"要早 {mk_of_wait - front['mk_min']} 步下线，"
             f"就得多走 {sum_of_costs(p_detour) - front['soc_min']} 步总行程——\n"
             f"两种代价给出不同的最优解，报表必须写明优化的是哪一个",
             f"finishing {mk_of_wait - front['mk_min']} step earlier costs "
             f"{sum_of_costs(p_detour) - front['soc_min']} extra steps of travel;\n"
             f"the two cost functions pick different solutions"),
           xy=(0.5, 0.06), xycoords="axes fraction", ha="center", va="bottom",
           fontsize=8.5, color=C["accent"])
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig25_3_1")
