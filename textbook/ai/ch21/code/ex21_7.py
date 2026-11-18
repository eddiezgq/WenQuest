"""算例 21.7.1—21.7.4：减速器车间的预测性维护，这笔账怎么算（21.8 节案例）。

一队设备（本例取 60 台份的轴承/刀具这类易损件），每台有自己的退化速度与测量噪声。
三种维护办法摆在一起比：

* **坏了再修**：不维护，等它失效；
* **定期更换**：到了固定周期就换，不看状态；
* **按状态报警**：量一个退化指标，越过阈值就安排停机。

本算例要算清三件事：**提前期**（报警到失效还有多久）、**误报与漏报**、**总代价**。
而且要说明一条：**同一个模型，换一个阈值，总代价能差几倍**——所以"模型准不准"
这个问题，不连阈值与代价一起问，就没有答案。
"""
import numpy as np

from _ch21 import degradation, first_cross, maintenance_cost
from bookout import out

N_UNITS, N_STEPS = 60, 160
COST_PLAN, COST_FAIL, COST_EARLY = 1.0, 12.0, 0.02
v = {"n_units": N_UNITS, "n_steps": N_STEPS,
     "cost_plan": COST_PLAN, "cost_fail": COST_FAIL, "cost_early": COST_EARLY}

g = np.random.default_rng(0)
fleet = [degradation(N_STEPS, rate=float(g.uniform(0.004, 0.012)),
                     noise=float(g.uniform(0.01, 0.05)), seed=int(g.integers(1 << 30)))
         for _ in range(N_UNITS)]
lives = [first_cross(x, 1.0) for x in fleet]
alive = [i for i, t in enumerate(lives) if t is None]
v["n_never_fail"] = len(alive)
fl = [t for t in lives if t is not None]
v["life_median"] = float(np.median(fl))
v["life_min"] = float(np.min(fl))
v["life_max"] = float(np.max(fl))
v["life_spread"] = v["life_max"] / v["life_min"]
print(f"{N_UNITS} 台：寿命中位 {v['life_median']:.0f} 个周期，"
      f"最短 {v['life_min']:.0f}、最长 {v['life_max']:.0f}（差 {v['life_spread']:.1f} 倍），"
      f"{v['n_never_fail']} 台到期没坏")
print("**寿命差这么多，正是“定期更换”吃亏的地方**：按最短的定周期，好件白换；"
      "按中位定，一半要出事")

# ---------- 一、坏了再修
r_run = maintenance_cost(fleet, thr=99.0, cost_plan=COST_PLAN, cost_fail=COST_FAIL,
                         cost_early=COST_EARLY)
v["cost_runtofail"] = r_run["total"]
v["fail_runtofail"] = r_run["failed"]
print(f"\n坏了再修：失效 {r_run['failed']} 台，总代价 {r_run['total']:.1f}")

# ---------- 二、定期更换：扫一遍周期
best_fixed, best_fixed_cost = 0, float("inf")
for period in range(20, 160, 5):
    plan = fail = 0
    waste = 0.0
    for x in fleet:
        t_fail = first_cross(x, 1.0)
        t_fail = N_STEPS - 1 if t_fail is None else t_fail
        if period < t_fail:
            plan += 1
            waste += COST_EARLY * (t_fail - period)
        else:
            fail += 1
    cost = plan * COST_PLAN + fail * COST_FAIL + waste
    if cost < best_fixed_cost:
        best_fixed, best_fixed_cost = period, cost
v["fixed_period"] = best_fixed
v["cost_fixed"] = best_fixed_cost
print(f"定期更换：最好的周期是 {best_fixed} 个周期，总代价 {best_fixed_cost:.1f}")

# ---------- 三、按状态报警：扫一遍阈值
rows = []
for thr in np.arange(0.30, 0.96, 0.05):
    r = maintenance_cost(fleet, thr=float(thr), cost_plan=COST_PLAN,
                         cost_fail=COST_FAIL, cost_early=COST_EARLY)
    rows.append((float(thr), r))
best_thr, best_r = min(rows, key=lambda t: t[1]["total"])
worst_thr, worst_r = max(rows, key=lambda t: t[1]["total"])
v["best_thr"] = best_thr
v["cost_cbm"] = best_r["total"]
v["lead_best"] = best_r["lead_mean"]
v["fail_best"] = best_r["failed"]
v["plan_best"] = best_r["planned"]
v["worst_thr"] = worst_thr
v["cost_cbm_worst"] = worst_r["total"]
v["thr_cost_ratio"] = worst_r["total"] / best_r["total"]
print(f"按状态报警：最好的阈值 {best_thr:.2f}，总代价 {best_r['total']:.1f}"
      f"（计划停机 {best_r['planned']} 台、失效 {best_r['failed']} 台、"
      f"平均提前 {best_r['lead_mean']:.1f} 个周期）")
print(f"同一组数据、同一个指标，阈值取 {worst_thr:.2f} 时总代价是 {worst_r['total']:.1f}——"
      f"**差 {v['thr_cost_ratio']:.1f} 倍**")
assert v["cost_cbm"] < v["cost_fixed"] < v["cost_runtofail"], \
    "按状态应当胜过定期，定期应当胜过坏了再修"
v["save_vs_fixed_pct"] = (1 - v["cost_cbm"] / v["cost_fixed"]) * 100
v["save_vs_run_pct"] = (1 - v["cost_cbm"] / v["cost_runtofail"]) * 100
print(f"按状态比定期省 {v['save_vs_fixed_pct']:.0f}%，比坏了再修省 {v['save_vs_run_pct']:.0f}%")

# ---------- 四、提前期才是车间真正要的那个数
for thr, tag in ((0.5, "50"), (0.7, "70"), (0.9, "90")):
    r = maintenance_cost(fleet, thr=thr, cost_plan=COST_PLAN, cost_fail=COST_FAIL,
                         cost_early=COST_EARLY)
    v[f"lead_{tag}"] = r["lead_mean"]
    v[f"leadmin_{tag}"] = r["lead_min"]
    v[f"fail_{tag}"] = r["failed"]
    v[f"cost_{tag}"] = r["total"]
    print(f"阈值 {thr:.2f}：平均提前 {r['lead_mean']:.1f} 个周期"
          f"（最短的那台只提前 {r['lead_min']} 个），失效 {r['failed']} 台，"
          f"代价 {r['total']:.1f}")
assert v["lead_50"] > v["lead_90"], "阈值越低报得越早"
print("**只报“平均提前多少”是不够的**：车间要的是“最短提前多少”——"
      "备件到货要三天，那就得保证提前期大于三天，而不是平均大于三天")

# 把这条写成验收条款该怎么写
v["lead_need"] = 10
ok_thr = [thr for thr, r in rows if r["lead_min"] >= v["lead_need"] and r["failed"] == 0]
v["n_thr_ok"] = len(ok_thr)
v["thr_ok_max"] = max(ok_thr) if ok_thr else float("nan")
v["cost_at_ok"] = (maintenance_cost(fleet, thr=v["thr_ok_max"], cost_plan=COST_PLAN,
                                    cost_fail=COST_FAIL, cost_early=COST_EARLY)["total"]
                   if ok_thr else float("nan"))
v["cost_penalty_pct"] = (v["cost_at_ok"] / v["cost_cbm"] - 1) * 100 if ok_thr else float("nan")
print(f"\n验收条款写成“每一台都至少提前 {v['lead_need']} 个周期报警、且不许有失效”：")
if ok_thr:
    print(f"  满足的阈值有 {v['n_thr_ok']} 档，其中最省的是 {v['thr_ok_max']:.2f}，"
          f"总代价 {v['cost_at_ok']:.1f}（比不加这条约束的最省方案贵 "
          f"{(v['cost_at_ok'] / v['cost_cbm'] - 1) * 100:.0f}%）")
else:
    print("  没有一档阈值满足——**这说明要么指标不够好，要么这条约束本身定得不现实**")
print("**这就是把“模型指标”翻译成“验收条款”的样子**：提前期、漏报数、总代价，"
      "三个数一起写，缺一个这条款就验不了")

out(**v)
