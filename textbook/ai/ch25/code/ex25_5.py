"""算例 25.5.1—25.5.3：电量约束下的充电排班——**吞吐最高的阈值不是最安全的阈值**（25.4、25.7 节）。

搬运车要穿插去充电，而充电位只有四个。两种排班策略：

* **低阈值充电**：电量掉到阈值以下才去充（车间里最常见）；
* **机会充电**：没活干、电量又不满时就顺手去充。

两种口径下各扫一遍阈值，报四个数：吞吐、**半路耗光的车次**、任务超时数、死锁次数。
按本章纪律，成绩必须连“失败的那一列”一起报——这里的失败有两种：
车在半路耗光（要人去拖），和任务超时。

两种工况分开跑，因为瓶颈不在一处：**活干不完**时瓶颈是车队（充电时间直接吃吞吐），
**活正好够**时瓶颈是任务（充电时间藏得住，但阈值定低了会让任务超时）。
车队参数（电量、充电速度、充电位个数、死锁恢复时间）全部是**显式假设**，
一个厂家样本都没用——资料卡里仓储机器人的充电门限本来就没核到任何官方文档。
"""
import numpy as np

from _ch25 import FLEET, GRID_WORKSHOP, Grid, run_fleet
from bookout import out

grid = Grid(GRID_WORKSHOP)
N_AGV = 10
STEPS = 1500
SEEDS = range(12)
THRS = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.65, 0.80)
v = {**{f"thr{int(t * 100)}": t for t in THRS},   # 第 175 轮补：正文表格的阈值行标签
     "n_agv": N_AGV, "steps": STEPS, "n_seeds": len(list(SEEDS)),
     "n_chargers": len(grid.chargers), "battery_full": FLEET["battery_full"],
     "charge_rate": FLEET["charge_rate"], "thresholds": str(list(THRS))}
print(f"{N_AGV} 台搬运车、{len(grid.chargers)} 个充电位，跑 {STEPS} 步，"
      f"{v['n_seeds']} 个随机种子取平均")
print(f"满电能走 {FLEET['battery_full']} 步，充电位上每步回 {FLEET['charge_rate']} 步的电量"
      f"（**显式假设**，不取自任何厂家样本）")


def sweep(task_every: int, policy: str) -> list:
    cfg = dict(FLEET)
    cfg["task_every"] = task_every
    rows = []
    for thr in THRS:
        rs = [run_fleet(grid, N_AGV, steps=STEPS, seed=s, cfg=cfg,
                        policy=policy, low_thr=thr) for s in SEEDS]
        rows.append({k: float(np.mean([r[k] for r in rs]))
                     for k in ("done", "stranded", "overdue", "deadlocks",
                               "charge_steps", "backlog")} | {"thr": thr})
    return rows


# ================================================================ 一、活干不完：瓶颈在车队
BUSY = 2                      # 平均每 2 步来一个任务，比这 10 台车做得完的还多
busy_thr = sweep(BUSY, "threshold")
busy_opp = sweep(BUSY, "opportunistic")
print(f"\n① 活干不完（每 {BUSY} 步来一个任务，瓶颈在车队）——低阈值充电：")
print("阈值    完成任务   半路耗光   超时任务   死锁   充电步数")
for r in busy_thr:
    print(f"{r['thr']:.2f}    {r['done']:7.1f}   {r['stranded']:7.2f}   "
          f"{r['overdue']:7.1f}  {r['deadlocks']:5.1f}   {r['charge_steps']:7.0f}")
    v[f"busy_done_thr{int(r['thr'] * 100)}"] = r["done"]
    v[f"busy_strand_thr{int(r['thr'] * 100)}"] = r["stranded"]

print(f"   （这一工况的活本来就干不完，所以“超时任务”那一列反映的是积压、不随阈值动；"
      f"能分好坏的是“半路耗光”那一列）")

peak = max(busy_thr, key=lambda r: r["done"])
safe = [r for r in busy_thr if r["stranded"] == 0.0]
assert safe, "阈值调到足够高，必须能做到一次都不耗光"
safe_best = max(safe, key=lambda r: r["done"])
v["busy_peak_thr"], v["busy_peak_done"] = peak["thr"], peak["done"]
v["busy_peak_strand"] = peak["stranded"]
v["busy_safe_thr"], v["busy_safe_done"] = safe_best["thr"], safe_best["done"]
v["busy_safety_price_pct"] = (1 - safe_best["done"] / peak["done"]) * 100
v["busy_lowest_done"] = busy_thr[0]["done"]
v["busy_lowest_strand"] = busy_thr[0]["stranded"]
v["busy_highest_done"] = busy_thr[-1]["done"]
print(f"\n   吞吐最高的阈值是 {peak['thr']:.2f}：完成 {peak['done']:.0f} 个任务，"
      f"但平均有 {peak['stranded']:.2f} 车次**在半路耗光**")
print(f"   一次都不耗光的最好设置是 {safe_best['thr']:.2f}：完成 {safe_best['done']:.0f} 个，"
      f"**安全的价钱是 {v['busy_safety_price_pct']:.1f}% 的吞吐**")
assert peak["done"] > safe_best["done"] and peak["stranded"] > 0, \
    "本算例要讲的就是“调快就不安全”：吞吐最高的那个设置必须是会耗光的那个"
assert busy_thr[0]["stranded"] > busy_thr[-3]["stranded"], "阈值越低，耗光越多"
print(f"   两头都不行：阈值 {THRS[0]:.2f} 时车一个接一个趴在路上（耗光 "
      f"{busy_thr[0]['stranded']:.1f} 车次，吞吐只有 {busy_thr[0]['done']:.0f}），"
      f"阈值 {THRS[-1]:.2f} 时车一直在充电（吞吐 {busy_thr[-1]['done']:.0f}）")
print("   **所以充电排班是一个有最优点的问题，不是“越早充越保险”**")

print(f"\n   同一工况，换成机会充电：")
print("阈值    完成任务   半路耗光   超时任务")
for r in busy_opp:
    print(f"{r['thr']:.2f}    {r['done']:7.1f}   {r['stranded']:7.2f}   {r['overdue']:7.1f}")
    v[f"busy_opp_done_thr{int(r['thr'] * 100)}"] = r["done"]
    v[f"busy_opp_strand_thr{int(r['thr'] * 100)}"] = r["stranded"]
v["busy_opp_low_done"] = busy_opp[0]["done"]
v["busy_opp_low_gain_pct"] = (busy_opp[0]["done"] / busy_thr[0]["done"] - 1) * 100
v["busy_opp_peak_done"] = max(r["done"] for r in busy_opp)
v["busy_opp_vs_peak_pct"] = (v["busy_opp_peak_done"] / peak["done"] - 1) * 100
print(f"   阈值定到最低（{THRS[0]:.2f}）时，机会充电把吞吐从 {busy_thr[0]['done']:.0f} 拉到 "
      f"{busy_opp[0]['done']:.0f}（+{v['busy_opp_low_gain_pct']:.0f}%）")
print(f"   但在各自最好的设置上，两种策略差不多（机会充电 {v['busy_opp_peak_done']:.0f} 对 "
      f"{peak['done']:.0f}，{v['busy_opp_vs_peak_pct']:+.1f}%）")
assert busy_opp[0]["done"] > busy_thr[0]["done"], \
    "机会充电的本事在于：阈值定错了也不至于塌"
print("   **机会充电的价值不是提高吞吐，是把“阈值定错”的后果抹平**——"
      "这类“让参数不那么要紧”的改动，在车间里比多榨两个点的吞吐值钱")

# ================================================================ 二、活正好够：瓶颈在任务
EASY = 4
easy_thr = sweep(EASY, "threshold")
easy_opp = sweep(EASY, "opportunistic")
print(f"\n② 活正好够（每 {EASY} 步来一个任务，瓶颈在任务）：")
print("阈值    低阈值：完成/耗光/超时        机会充电：完成/耗光/超时")
for a, b in zip(easy_thr, easy_opp):
    print(f"{a['thr']:.2f}    {a['done']:7.1f} / {a['stranded']:5.2f} / {a['overdue']:6.1f}"
          f"        {b['done']:7.1f} / {b['stranded']:5.2f} / {b['overdue']:6.1f}")
    v[f"easy_done_thr{int(a['thr'] * 100)}"] = a["done"]
    v[f"easy_overdue_thr{int(a['thr'] * 100)}"] = a["overdue"]
    v[f"easy_opp_done_thr{int(b['thr'] * 100)}"] = b["done"]
    v[f"easy_opp_overdue_thr{int(b['thr'] * 100)}"] = b["overdue"]
v["easy_cap_done"] = max(r["done"] for r in easy_thr)
v["easy_low_done"] = easy_thr[0]["done"]
v["easy_low_overdue"] = easy_thr[0]["overdue"]
v["easy_opp_low_overdue"] = easy_opp[0]["overdue"]
v["easy_overdue_ratio"] = (v["easy_low_overdue"]
                           / max(v["easy_opp_low_overdue"], 1e-9))
print(f"   任务来得慢，充电时间藏得住：阈值 {THRS[3]:.2f} 以上吞吐都顶到任务上限"
      f"（约 {v['easy_cap_done']:.0f} 个），**吞吐这一列看不出任何差别**")
print(f"   差别全在失败那两列：阈值 {THRS[0]:.2f} 时超时 {v['easy_low_overdue']:.0f} 个任务、"
      f"耗光 {easy_thr[0]['stranded']:.1f} 车次；机会充电同一个阈值只超时 "
      f"{v['easy_opp_low_overdue']:.1f} 个")
assert v["easy_low_overdue"] > easy_thr[-1]["overdue"], \
    "阈值定低了，超时数必须涨——这就是“只看吞吐会漏掉的那一列”"
print("   **只报吞吐，这一整张表都是平的**；超时数与耗光车次才是分得出好坏的那两列")

# ================================================================ 三、结论
print(f"\n本算例的三条：")
print(f"  1. 充电阈值有最优点：太低车趴窝，太高车一直在充；本工况下最优在 "
      f"{v['busy_peak_thr']:.2f} 附近，但那个点**会有车耗光**；")
print(f"  2. 要“一次都不耗光”，就得把阈值提到 {v['busy_safe_thr']:.2f}，"
      f"代价是 {v['busy_safety_price_pct']:.1f}% 的吞吐——**这笔钱要摆在台面上讲**，"
      f"与第 22 章安全层的价钱是同一件事；")
print(f"  3. 瓶颈在任务时，吞吐这一列是平的，差别只在超时与耗光两列——"
      f"**报表少一列，结论就反过来**。")

# ================================================================ 四、车队加到多少台（与图 25.5.1 同一组扫描）
# 第 174 轮交付时发现：这三行数原来只在 fig25_5.py 里算，正文取不到占位符。
# 这里按同样的设置（1200 步、8 个种子）重算一遍，交给正文，图与正文从此是同一个数。
FLEET_NS = [2, 4, 6, 8, 10, 12, 16, 20, 26, 32, 38, 44]
FLEET_SEEDS, FLEET_STEPS = range(8), 1200


def _sweep_fleet(zone: int) -> dict:
    cfg = dict(FLEET)
    cfg["zone_radius"] = zone
    done, dead = [], []
    for n in FLEET_NS:
        rs = [run_fleet(grid, n, steps=FLEET_STEPS, seed=s, cfg=cfg) for s in FLEET_SEEDS]
        done.append(float(np.mean([r["done"] for r in rs])))
        dead.append(float(np.mean([r["deadlocks"] for r in rs])))
    return {"done": done, "dead": dead, "per": [d / n for d, n in zip(done, FLEET_NS)]}


_plain, _zoned = _sweep_fleet(0), _sweep_fleet(2)
_i10 = FLEET_NS.index(10)
v["fleet_n_ref"] = FLEET_NS[_i10]        # 第 175 轮补：正文表格里那一行的车队规模
v["fleet_n_min"], v["fleet_n_max"] = FLEET_NS[0], FLEET_NS[-1]
v["fleet_steps"], v["fleet_seeds"] = FLEET_STEPS, len(list(FLEET_SEEDS))
v["fleet_plain_done_10"] = _plain["done"][_i10]
v["fleet_plain_done_max"] = _plain["done"][-1]
v["fleet_plain_done_peak"] = max(_plain["done"])
v["fleet_plain_per_10"] = _plain["per"][_i10]
v["fleet_plain_per_max"] = _plain["per"][-1]
v["fleet_plain_dead_10"] = _plain["dead"][_i10]
v["fleet_plain_dead_max"] = _plain["dead"][-1]
_ipk = int(np.argmax(_zoned["done"]))
v["fleet_zone_peak_n"] = FLEET_NS[_ipk]
v["fleet_zone_peak_done"] = _zoned["done"][_ipk]
v["fleet_zone_done_max"] = _zoned["done"][-1]
v["fleet_zone_drop_pct"] = 100.0 * (1 - _zoned["done"][-1] / _zoned["done"][_ipk])
v["fleet_plain_drop_pct"] = 100.0 * (1 - _plain["done"][-1] / max(_plain["done"]))
v["fleet_per_fall_x"] = _plain["per"][_i10] / _plain["per"][-1]

print(f"\n四、车队加到多少台（{FLEET_STEPS} 步、{v['fleet_seeds']} 个种子，与图 25.5.1 同一组）")
print(f"   一处卡住只停那一台车：{FLEET_NS[_i10]} 台 {v['fleet_plain_done_10']:.0f} 个任务，"
      f"{FLEET_NS[-1]} 台 {v['fleet_plain_done_max']:.0f} 个——**总吞吐只是涨不动，没有掉下来**")
print(f"   同一批里塌掉的是别的两列：单车吞吐 {v['fleet_plain_per_10']:.1f} → "
      f"{v['fleet_plain_per_max']:.1f} 个（少 {v['fleet_per_fall_x']:.1f} 倍）、"
      f"死锁 {v['fleet_plain_dead_10']:.0f} → {v['fleet_plain_dead_max']:.0f} 次")
print(f"   加上“堵一处停一片”的区域联锁，才真出现先升后降：峰值 {v['fleet_zone_peak_n']} 台 "
      f"{v['fleet_zone_peak_done']:.0f} 个，加到 {FLEET_NS[-1]} 台只剩 {v['fleet_zone_done_max']:.0f} 个"
      f"（跌 {v['fleet_zone_drop_pct']:.0f}%）")
assert v["fleet_plain_drop_pct"] < 5.0, \
    "不联锁时总吞吐不应当明显下降——这条结论是本节的要点，变了就要改正文"
assert v["fleet_zone_drop_pct"] > 30.0, "联锁时必须真出现先升后降"
assert v["fleet_per_fall_x"] > 2.0, "单车吞吐必须明显塌下来"
print("   **“车多了吞吐先升后降”不是定律，它取决于堵车怎么处理**——"
      "报这条曲线必须把这个假设写在旁边")

out(**v)
