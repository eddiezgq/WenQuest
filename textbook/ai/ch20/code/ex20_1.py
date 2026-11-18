"""算例 20.1.1—20.1.2：候选空间有多大，以及"挨个算"从一开始就不成立（20.1 节）。

（1）元数每加一，候选数**两个因子同时变大**：挑哪几种元素的组合数，乘上每种组合里的成分点数。
（2）把候选数按"每个第一性原理算多久"折算成年份——这个账一算就知道筛选漏斗为什么是必需的。
（3）**这里不印任何真实机器的速度**：每个算多久由读者自己代，程序只做换算。
"""
import numpy as np

from _ch20 import dft_years, n_candidates, n_compositions
from bookout import out

POOL, GRID = 40, 20          # 元素池 40 种；成分按 5% 一档撒点

v = {"pool": POOL, "grid": GRID}

# ---------- 一、成分点数与候选数
for k in (2, 3, 4, 5):
    v[f"comp_{k}"] = n_compositions(k, GRID)
    v[f"cand_{k}"] = n_candidates(POOL, k, GRID)
    v[f"choose_{k}"] = n_candidates(POOL, k, GRID) // n_compositions(k, GRID)

assert v["cand_2"] < v["cand_3"] < v["cand_4"] < v["cand_5"]
v["jump_3_to_4"] = v["cand_4"] / v["cand_3"]
v["jump_4_to_5"] = v["cand_5"] / v["cand_4"]
print(f"二元 {v['cand_2']:,}　三元 {v['cand_3']:,}　四元 {v['cand_4']:,}　五元 {v['cand_5']:,}")
print(f"三元→四元 ×{v['jump_3_to_4']:.1f}，四元→五元 ×{v['jump_4_to_5']:.1f}")

# ---------- 二、一个成分不是一次计算
# 这是最容易被忽略的那个因子：给定成分，原子怎么排还不知道——晶体结构预测要对同一个成分
# 试很多个候选结构（不同空间群、不同占位），每一个都得松弛一遍。这里把它写成一个显式假设。
TRIALS = 100                 # 每个成分试 100 个候选结构（显式假设，不是实测值）
v["trials_per_comp"] = TRIALS
v["calc_4"] = v["cand_4"] * TRIALS
print(f"\n四元候选 {v['cand_4']:,} 个成分 × 每个成分试 {TRIALS} 个结构 = "
      f"{v['calc_4']:,} 次计算")

# 三种假设的单次耗时，差一个量级：小体系静态能量、结构松弛、带声子的全套
for tag, hours in (("fast", 0.5), ("relax", 8.0), ("full", 72.0)):
    v[f"years_{tag}_1k"] = dft_years(v["calc_4"], hours, 1000)
    v[f"years_{tag}_10k"] = dft_years(v["calc_4"], hours, 10000)
    print(f"单次 {hours:>4.1f} 小时：1000 并行 {v[f'years_{tag}_1k']:>12,.0f} 年，"
          f"10000 并行 {v[f'years_{tag}_10k']:>11,.0f} 年")

# 把三个因子都摆上之后，结论对假设不敏感：最乐观那一档（半小时一个、同时跑一万个）
# 仍然是几十年。这才是"挨个算不成立"的正确说法——**不是因为成分多，是三个因子相乘**；
# 而且只要把任一个因子往现实挪一点（松弛要 8 小时，而不是半小时），立刻变成上千年。
assert v["years_fast_10k"] > 50, "三个因子相乘之后，最乐观的假设也该是几十年量级"
assert v["years_relax_10k"] > 1000, "单次按结构松弛算，就是上千年"
v["optimistic_years"] = v["years_fast_10k"]

# ---------- 三、反过来问：预算有限时能算几分之一
# 假设一年、一万并行、单次 8 小时，能算多少个，占四元候选的比例
budget = 10000 * 365.25 * 24 / 8.0
v["budget_calcs"] = budget
v["budget_share_pct"] = budget / v["cand_4"] * 100
print(f"\n一年、10000 并行、单次 8 小时：能算 {budget:,.0f} 个，"
      f"占四元候选的 {v['budget_share_pct']:.2f}%")
assert v["budget_share_pct"] < 10, "能算的只是候选里的一小部分——所以必须先筛"

# ---------- 四、筛选漏斗：为什么中间必须有一层"便宜但不太糙"的
# 层层的留存率不是任何真实流程的参数，只用来说明漏斗的算术。关键在于**每一层用什么算**：
#   第一层：只看成分的便宜筛子（规则、描述子、分类器），一个结构毫秒级；
#   第二层：机器学习势做结构松弛，一个结构按 1 秒算（显式假设，不是实测值）；
#   第三层：第一性原理复核，一个 8 小时。
keep = [0.01, 0.10, 0.10]
n = float(v["cand_4"])
for i, k in enumerate(keep, 1):
    n *= k
    v[f"funnel_{i}"] = n
v["funnel_final"] = n

v["dft_after_layer1_years"] = dft_years(v["funnel_1"] * TRIALS, 8.0, 1000)
v["mlip_after_layer1_years"] = dft_years(v["funnel_1"] * TRIALS, 1.0 / 3600, 100)
# 机器学习势那一层已经替每个成分挑出了最好的那个结构，所以复核是"一个成分一次"，
# 不再是一个成分一百次——**漏斗不只砍数量，还把每个候选要算的次数也砍下来**。
v["dft_after_layer2_years"] = dft_years(v["funnel_2"], 8.0, 1000)
print(f"\n漏斗（留 1% → 10% → 10%）：{v['cand_4']:,.0f} → {v['funnel_1']:,.0f} → "
      f"{v['funnel_2']:,.0f} → {v['funnel_final']:,.0f}")
print(f"第一层筛完还剩 {v['funnel_1'] * TRIALS:,.0f} 个结构：")
print(f"  直接上第一性原理（8 小时/个、1000 并行）：{v['dft_after_layer1_years']:,.1f} 年　——还是算不动")
print(f"  改用机器学习势（1 秒/个、100 并行）：    {v['mlip_after_layer1_years']:,.3f} 年　"
      f"（约 {v['mlip_after_layer1_years'] * 365.25:,.0f} 天）")
print(f"第二层筛完剩 {v['funnel_2']:,.0f} 个成分（每个只复核挑出来的那一个结构），"
      f"第一性原理这才算得动：{v['dft_after_layer2_years']:,.2f} 年")

# 这是本节真正的结论：**一层便宜筛子不够**。第一层砍掉两个数量级之后，第一性原理仍然要上百年；
# 中间必须插一层"比第一性原理快几个数量级、又比纯描述子可信"的东西——那就是第 20.3 节的机器学习势。
assert v["dft_after_layer1_years"] > 100, "第一层之后直接上第一性原理应当还是算不动"
assert v["mlip_after_layer1_years"] < 1, "机器学习势那一层应当把它压到一年以内"
assert v["dft_after_layer2_years"] < 1, "两层筛完、每个成分只复核一个结构，第一性原理才算得动"
v["speedup_mlip_vs_dft"] = v["dft_after_layer1_years"] / v["mlip_after_layer1_years"]
print(f"同一批结构，机器学习势比第一性原理快 {v['speedup_mlip_vs_dft']:,.0f} 倍"
      f"——**这是按上面那两个假设算的，不是实测**")

out(**v)
