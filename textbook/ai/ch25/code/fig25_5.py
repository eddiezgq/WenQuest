"""本章第五幅图（`fig25_5_1`，案例）：搬运车加到多少台就不划算了。

图 `fig25_5_1`：（a）车队规模对吞吐——**“先升后降”这条曲线不是物理定律，它取决于堵车怎么处理**：
一处卡住只停那一台车，吞吐升上去就平了；一处卡住停一片（区域联锁），吞吐就真的掉下来。
（b）同一批跑出来的死锁次数与单车吞吐：**总吞吐还在涨的时候，单车产出已经塌了**。
"""
import numpy as np

from _ch25 import FLEET, GRID_WORKSHOP, Grid, run_fleet
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
grid = Grid(GRID_WORKSHOP)
NS = [2, 4, 6, 8, 10, 12, 16, 20, 26, 32, 38, 44]
SEEDS = range(8)
STEPS = 1200


def sweep(zone: int) -> dict:
    cfg = dict(FLEET)
    cfg["zone_radius"] = zone
    out = {k: [] for k in ("done", "deadlocks", "overdue", "per")}
    for n in NS:
        rs = [run_fleet(grid, n, steps=STEPS, seed=s, cfg=cfg) for s in SEEDS]
        out["done"].append(np.mean([r["done"] for r in rs]))
        out["deadlocks"].append(np.mean([r["deadlocks"] for r in rs]))
        out["overdue"].append(np.mean([r["overdue"] for r in rs]))
        out["per"].append(np.mean([r["done"] for r in rs]) / n)
    return {k: np.array(v) for k, v in out.items()}


plain = sweep(0)        # 死锁只停那一台车
zoned = sweep(2)        # 区域联锁：堵一处停一片

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 吞吐
a.plot(NS, plain["done"], "o-", color=C["z"], lw=2.2, ms=5,
       label=T("一处卡住只停那一台车", "a jam stops only that one vehicle"))
a.plot(NS, zoned["done"], "s-", color=C["x"], lw=2.2, ms=5,
       label=T("区域联锁：一处卡住停一片", "zone interlock: a jam stops the whole zone"))
i_pk = int(np.argmax(zoned["done"]))
a.plot(NS[i_pk], zoned["done"][i_pk], "o", mfc="none", mec=C["x"], ms=16, mew=2.0)
a.annotate(T(f"峰值 {NS[i_pk]} 台：{zoned['done'][i_pk]:.0f} 个任务；"
             f"加到 {NS[-1]} 台只剩 {zoned['done'][-1]:.0f} 个",
             f"peak at {NS[i_pk]} vehicles ({zoned['done'][i_pk]:.0f} tasks); "
             f"{NS[-1]} vehicles → {zoned['done'][-1]:.0f}"),
           xy=(NS[i_pk], zoned["done"][i_pk]), xytext=(26, -14),
           textcoords="offset points", fontsize=8.5, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.1))
a.annotate(T(f"没有联锁时只是**涨不动**：{NS[4]} 台 {plain['done'][4]:.0f} 个，"
             f"{NS[-1]} 台 {plain['done'][-1]:.0f} 个".replace("**", ""),
             f"without the interlock it merely saturates: {plain['done'][-1]:.0f} tasks "
             f"at {NS[-1]} vehicles"),
           xy=(0.98, 0.10), xycoords="axes fraction", ha="right", va="bottom",
           fontsize=8.5, color=C["z"])
a.set_xlabel(T("搬运车数量（台）", "number of vehicles"))
a.set_ylabel(T(f"{STEPS} 步里完成的任务数", f"tasks completed in {STEPS} steps"))
a.set_title(T("(a) 先升后降，还是升上去就平——看堵车怎么处理",
              "(a) hump or plateau: it depends on how jams are handled"), fontsize=10)
a.legend(fontsize=8, loc="center right", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 死锁与单车吞吐
b.plot(NS, plain["deadlocks"], "o-", color=C["z"], lw=2.0, ms=5,
       label=T("死锁次数：不联锁", "deadlocks: no interlock"))
b.plot(NS, zoned["deadlocks"], "s-", color=C["x"], lw=2.0, ms=5,
       label=T("死锁次数：区域联锁", "deadlocks: zone interlock"))
b.set_xlabel(T("搬运车数量（台）", "number of vehicles"))
b.set_ylabel(T("死锁次数", "deadlocks"))
b2 = b.twinx()
b2.plot(NS, plain["per"], ":", color=C["y"], lw=2.4,
        label=T("单车吞吐：不联锁", "per-vehicle output: no interlock"))
b2.plot(NS, zoned["per"], "-.", color=C["accent"], lw=2.0,
        label=T("单车吞吐：区域联锁", "per-vehicle output: zone interlock"))
b2.set_ylabel(T("单车完成任务数", "tasks per vehicle"))
b2.set_ylim(0, max(plain["per"]) * 1.18)
h1, l1 = b.get_legend_handles_labels()
h2, l2 = b2.get_legend_handles_labels()
b.legend(h1 + h2, l1 + l2, fontsize=7.6, loc="upper left", framealpha=0.92)
b.set_title(T("(b) 总吞吐还在涨的时候，单车产出已经塌了",
               "(b) per-vehicle output collapses while the total still climbs"),
            fontsize=10)
b.annotate(T(f"单车吞吐从 {plain['per'][1]:.0f} 跌到 {plain['per'][-1]:.0f} 个"
             f"——加车要先问这一列",
             f"per-vehicle output falls from {plain['per'][1]:.0f} to "
             f"{plain['per'][-1]:.0f}: ask this column before buying vehicles"),
           xy=(0.97, 0.55), xycoords="axes fraction", ha="right", va="bottom",
           fontsize=8.5, color=C["accent"])
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig25_5_1")
