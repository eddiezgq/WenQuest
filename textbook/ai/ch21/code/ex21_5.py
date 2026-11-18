"""算例 21.5.1—21.5.3：在产线上调工艺参数（21.4 节）。

20.5 节的闭环放到车间里，多了三条约束：

* **试出来的废品是真花钱的**——找最优的过程本身有成本；
* **一次只能动一点点**——工人要跟得上、设备要稳得住，不能今天 500 转明天 2000 转；
* **一个班只有有限次试验**——产线首先要出活，不是给你做实验的。

于是"谁找得准"这个问题要换成**"同样的试验次数，谁找得准、而且试坏的少"**。
三种办法：不管约束的随机搜索、车间几十年的单因素轮换、代理模型 + 信赖域。
"""
import numpy as np

from _ch21 import best_feasible, cut_objective, cut_quality, cut_scrap, search_parameters
from bookout import out

BUDGET = 40
SEEDS = range(9)
v = {"budget": BUDGET, "n_repeat": len(list(SEEDS))}

# ---------- 一、先把真值算出来（读者看不到，但本算例要拿它判分）
bs, bf, best_val = best_feasible()
v["opt_speed"], v["opt_feed"], v["opt_value"] = bs, bf, best_val
v["opt_quality"] = cut_quality(bs, bf)
print(f"真值（网格扫出来的）：切削速度 {bs:.3f}、进给 {bf:.3f}，"
      f"产出 {best_val:.4f}，此时表面质量 {v['opt_quality']:.3f}")
print(f"合格线是质量 0.72，所以**最优点就贴着合格线**——这正是工艺优化难在哪里："
      f"好参数总在废品区的边上")

# ---------- 二、三种办法
rows = []
for method, name in (("free", "随机搜索（不管约束）"),
                     ("ofat", "单因素轮换"),
                     ("trust", "代理模型 + 信赖域")):
    vals, scraps = [], []
    for sd in SEEDS:
        r = search_parameters(method, BUDGET, seed=sd)
        vals.append(r["best_val"])
        scraps.append(r["scrap"])
    med_val = float(np.median(vals))
    med_scrap = float(np.median(scraps))
    v[f"val_{method}"] = med_val
    v[f"share_{method}"] = med_val / best_val * 100
    v[f"scrap_{method}"] = med_scrap
    v[f"scrap_pct_{method}"] = med_scrap / BUDGET * 100
    rows.append((name, med_val, med_scrap))
    print(f"{name}：找到的产出中位 {med_val:.4f}（真值的 {v[f'share_{method}']:.1f}%），"
          f"{BUDGET} 次试验里试坏 {med_scrap:.0f} 件（{v[f'scrap_pct_{method}']:.0f}%）")

assert v["val_trust"] > v["val_free"], "信赖域应当比乱撒点找得好"
assert v["scrap_trust"] < v["scrap_free"], "信赖域应当试坏得更少"
v["scrap_saved"] = v["scrap_free"] - v["scrap_trust"]
v["val_gain_pts"] = v["share_trust"] - v["share_free"]
print(f"\n**信赖域比随机搜索多找回 {v['val_gain_pts']:.1f} 个百分点的产出，"
      f"同时少试坏 {v['scrap_saved']:.0f} 件**")
print("单因素轮换不坏——它之所以在车间活了几十年，正是因为它天然满足"
      "“一次只动一点点”这条约束；它的毛病是**遇到两因素耦合时会卡住**")

# ---------- 三、预算从哪来：少试几次，损失多少
for budget in (10, 20, 40, 80):
    vals = [search_parameters("trust", budget, seed=sd)["best_val"] for sd in SEEDS]
    v[f"trust_b{budget}"] = float(np.median(vals))
    v[f"trust_b{budget}_pct"] = v[f"trust_b{budget}"] / best_val * 100
    print(f"预算 {budget:>3d} 次：找到真值的 {v[f'trust_b{budget}_pct']:.1f}%")
v["budget_gain_10_to_40"] = v["trust_b40_pct"] - v["trust_b10_pct"]
v["budget_gain_40_to_80"] = v["trust_b80_pct"] - v["trust_b40_pct"]
print(f"从 10 次加到 40 次，多找回 {v['budget_gain_10_to_40']:.1f} 个百分点；"
      f"从 40 次加到 80 次，只多找回 {v['budget_gain_40_to_80']:.1f} 个百分点")
print("**边际收益掉得很快**——所以“再多试几次”这个提议，要连“每次试验花多少”一起算")

# ---------- 四、合格线一提，最优点就跑了
# 这是本节最该记住的一条：工艺窗口是被质量要求定出来的，不是被机床定出来的。
for line, tag in ((0.72, "72"), (0.80, "80"), (0.86, "86")):
    ax = np.linspace(0.05, 0.95, 201)
    best, bsx, bfx = -1.0, 0.0, 0.0
    for s in ax:
        for f in ax:
            q = cut_quality(float(s), float(f))
            val = 0.0 if q < line else float(s) * float(f)
            if val > best:
                best, bsx, bfx = val, float(s), float(f)
    v[f"line{tag}_value"] = best
    v[f"line{tag}_speed"] = bsx
    v[f"line{tag}_feed"] = bfx
    print(f"合格线 {line:.2f}：最优点 (速度 {bsx:.3f}, 进给 {bfx:.3f})，产出 {best:.4f}")
v["line_cost_pct"] = (1 - v["line86_value"] / v["line72_value"]) * 100
assert v["line86_value"] < v["line72_value"], "合格线提高，能拿到的产出必然下降"
print(f"合格线从 0.72 提到 0.86，产出要让出 {v['line_cost_pct']:.0f}%——"
      f"**质量与产出的取舍是一条可以算出来的曲线，不是一句口号**")

out(**v)
