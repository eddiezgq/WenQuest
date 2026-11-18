"""算例 20.7.1—20.7.3：自主实验室的闭环（20.5 节）。

闭环是"提议 → 合成 → 表征 → 回填 → 再提议"。本算例在一个二维响应面上把三件事算出来：

（1）**收益**：同样的实验预算，贝叶斯优化比网格、随机搜索少试多少次才找到好东西；
（2）**吞吐量不等于收益**：把预算翻倍（吞吐翻倍）带来的改善，与换一个提议策略带来的改善，
    哪个更大；
（3）**系统偏差比随机噪声致命**：噪声能靠多测几次抹平，偏差会把整张面拧歪，
    于是闭环一路爬到错的地方去，而且**它自己以为找到了好东西**。

所以判据必须用**真值**，不能用测量值——这是本算例最该记住的一句。
"""
import numpy as np

from _ch20 import closed_loop, response_surface
from bookout import out

v = {}
ax = np.linspace(0, 1, 41)
AA, BB = np.meshgrid(ax, ax)
surf = response_surface(AA.ravel(), BB.ravel())
v["truth_best"] = float(surf.max())
v["truth_mean"] = float(surf.mean())
i = int(np.argmax(surf))
v["best_a"], v["best_b"] = float(AA.ravel()[i]), float(BB.ravel()[i])
print(f"响应面：最好 {v['truth_best']:.4f}（在 {v['best_a']:.2f}, {v['best_b']:.2f}），"
      f"平均 {v['truth_mean']:.4f}")

N_SEED = 20


def run(strategy, budget, noise=0.0, bias=0.0):
    rs = [closed_loop(strategy, budget, noise=noise, bias=bias, seed=s)
          for s in range(N_SEED)]
    return (float(np.median([r["regret"] for r in rs])),
            float(np.median([r["truth_of_pick"] for r in rs])),
            float(np.median([r["believed"] for r in rs])))


# ---------- 一、同样的预算，三种策略
print("\n干净测量（无噪声、无偏差）：")
for budget in (20, 40, 80):
    for strategy in ("grid", "random", "bayes"):
        reg, got, _ = run(strategy, budget)
        v[f"reg_{strategy}_{budget}"] = reg
        v[f"got_{strategy}_{budget}"] = got
        print(f"  预算 {budget:>3d}　{strategy:>6}：找到 {got:.4f}（距最好差 {reg:.4f}）")

v["bayes_gain_40"] = v["reg_random_40"] / max(v["reg_bayes_40"], 1e-9)
print(f"预算 40 时，贝叶斯的差距是随机搜索的 1/{v['bayes_gain_40']:.1f}")
assert v["reg_bayes_40"] < v["reg_random_40"], "贝叶斯优化应当比随机搜索好"
assert v["reg_bayes_40"] < v["reg_grid_40"], "也应当比网格搜索好"

# ---------- 二、吞吐量 vs 收益：预算翻倍 vs 换策略
v["double_budget_gain"] = v["reg_random_40"] / max(v["reg_random_80"], 1e-9)
v["switch_strategy_gain"] = v["reg_random_40"] / max(v["reg_bayes_40"], 1e-9)
print(f"\n把随机搜索的预算从 40 翻到 80（吞吐量翻倍）：差距缩小 {v['double_budget_gain']:.1f} 倍")
print(f"预算仍是 40，只把策略换成贝叶斯：    差距缩小 {v['switch_strategy_gain']:.1f} 倍")
v["strategy_beats_throughput"] = v["switch_strategy_gain"] > v["double_budget_gain"]
print(f"**换策略比翻吞吐量更合算：{v['strategy_beats_throughput']}**——"
      f"所以“一天能做多少个实验”这个数，不连策略一起说就没意义")

# ---------- 三、噪声与系统偏差，各自怎么伤
# 这张面有两个峰：真最优在 (0.72, 0.35)、高 1.00，还有一个"陪衬峰"在 (0.22, 0.78)、高 0.72。
# 偏差取 bias × (a − 0.5)：负的偏差压低右边、抬高左边，**大到某个程度就会把两个峰的排序掀翻**，
# 闭环于是一头扎进那个陪衬峰。门槛能算出来：0.72 + 0.28|b| > 1.00 − 0.22|b|，即 |b| > 0.56。
v["decoy_height"] = float(response_surface(np.array([0.22]), np.array([0.78]))[0])
v["flip_threshold"] = 0.56
print(f"\n这张面的陪衬峰高 {v['decoy_height']:.4f}，真最优高 {v['truth_best']:.4f}；"
      f"按算术，偏差超过约 {v['flip_threshold']:.2f} 就会把排序掀翻")

print("\n预算 40、贝叶斯策略：")
for tag, noise, bias in (("clean", 0.0, 0.0), ("noise_lo", 0.05, 0.0), ("noise_hi", 0.20, 0.0),
                         ("bias_03", 0.0, -0.30), ("bias_06", 0.0, -0.60),
                         ("bias_10", 0.0, -1.00), ("both", 0.10, -1.00)):
    reg, got, believed = run("bayes", 40, noise=noise, bias=bias)
    v[f"reg_{tag}"] = reg
    v[f"got_{tag}"] = got
    v[f"believed_{tag}"] = believed
    print(f"  噪声 {noise:.2f}　偏差 {bias:+.2f}：真实拿到 {got:.4f}（差 {reg:.4f}），"
          f"自己以为拿到 {believed:.4f}")

v["noise_cost"] = v["reg_noise_hi"] / max(v["reg_clean"], 1e-9)
v["bias_cost_small"] = v["reg_bias_03"] / max(v["reg_clean"], 1e-9)
v["bias_cost_big"] = v["reg_bias_10"] / max(v["reg_clean"], 1e-9)
print(f"\n噪声 0.20：差距放大 {v['noise_cost']:.1f} 倍")
print(f"偏差 −0.30（没到门槛）：放大 {v['bias_cost_small']:.1f} 倍——几乎不伤")
print(f"偏差 −1.00（过了门槛）：放大 {v['bias_cost_big']:.1f} 倍——**闭环扎进了错的那个峰**")
assert v["reg_bias_10"] > v["reg_bias_03"] * 3, \
    "偏差要大到能把候选的排序掀翻才伤——**这是个门槛现象，不是线性关系**"

# 本节真正稳的那条结论：**闭环自己报出来的数不等于真值**，两种方向都错，而且错法不同。
for tag in ("clean", "noise_hi", "bias_03", "bias_10", "both"):
    v[f"gap_{tag}"] = v[f"believed_{tag}"] - v[f"got_{tag}"]
print(f"\n自报成绩减真值：干净 {v['gap_clean']:+.4f}　噪声 {v['gap_noise_hi']:+.4f}　"
      f"偏差−0.30 {v['gap_bias_03']:+.4f}　偏差−1.00 {v['gap_bias_10']:+.4f}　"
      f"两者都有 {v['gap_both']:+.4f}")
assert abs(v["gap_clean"]) < 1e-6, "干净测量时自报就是真值"
assert v["gap_noise_hi"] > 0.05, "**噪声让自报成绩虚高**：挑最大值这个动作自带选择偏倚"
assert abs(v["gap_bias_10"]) > 0.05, "有偏差时自报成绩与真值整体错开（方向随偏差的符号）"
print("噪声让它**虚高**（挑最大值自带选择偏倚），偏差让它**整体错开**（符号随偏差）。")
print("**所以闭环的成绩必须拿独立复核的真值来算**，不能用闭环自己的测量值——"
      "不然噪声越大、报得越好看。")

out(**v)
