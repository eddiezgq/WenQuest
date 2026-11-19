"""算例 24.3：动作离散化的代价。

现在的视觉—语言—动作模型把连续动作**分箱成整数**再当词来预测：资料卡里
RT-1 是“每维 256 个均匀分箱”、RT-2 的动作是 8 个整数、连续维同样每维 256 个均匀分箱
（`conventions/robot_facts.py` 的 `RT1["action_bins"]`、`RT2["action_bins"]`）。
分箱越粗越省词表、越好学，但机器人只能走格子点——代价要算出来。

扫分箱数，看两件事：**任务成功率**与**动作抖动**（相邻两步动作差的平均绝对值）。
还要算“分箱数翻倍”带来的收益：它是递减的，而且比直觉衰减得快得多。

策略固定（算例 24.1 训出来那种“带纠正的”策略，在标称仿真里训），
**只在执行时把它的输出分箱**——这样比较的是离散化本身，不是别的。
"""
import numpy as np

from _ch24 import DEGREE, SIM, evaluate, make_policy, sample_starts, sample_targets, train_policy
from bookout import out

BINS = (2, 4, 8, 16, 32, 64, 128, 256)     # 按 2 的幂扫，方便算“翻倍的收益”
BINS_ODD = 3                               # 单独试一个奇数：中间那一档正好是 0
N_TEST = 80

v = {"bins": list(BINS), "n_trials": N_TEST, "rt1_bins": 256, "rt2_bins": 256,
     "bins_note": "分箱口径参照 robot_facts：RT-1 与 RT-2 都是每维 256 个均匀分箱"}

W = train_policy(160, rounds=4, seed=0)
pol = (lambda p, w: make_policy(W, DEGREE))
test_poses = sample_targets(N_TEST, seed=11)
test_starts = sample_starts(N_TEST, seed=11, spread=0.25)

base = evaluate(pol, test_poses, test_starts, SIM, seed=7)
v["succ_cont"], v["jitter_cont"] = base["success_pct"], base["jitter"]
print(f"不分箱（连续动作）：成功率 {v['succ_cont']:.1f}%（试了 {N_TEST} 次），"
      f"抖动 {v['jitter_cont']:.4f}")

succ, jit, perr = [], [], []
print("\n分箱数　成功率　抖动　平均位置误差")
for b in BINS:
    r = evaluate(pol, test_poses, test_starts, SIM, seed=7, bins=b)
    succ.append(r["success_pct"])
    jit.append(r["jitter"])
    perr.append(r["pos_err"])
    print(f"  {b:4d}　{r['success_pct']:6.1f}%　{r['jitter']:.4f}　{r['pos_err'] * 100:5.2f} cm")
succ = np.array(succ)
jit = np.array(jit)
v["success_pct"] = succ.tolist()
v["jitter"] = jit.tolist()
v["pos_err_cm"] = [p * 100 for p in perr]

# ---------- 一、分箱太少，成功率明显掉
v["succ_2bins"] = float(succ[0])
v["succ_256bins"] = float(succ[-1])
v["succ_drop_2bins"] = v["succ_cont"] - v["succ_2bins"]
print(f"\n只分 2 个箱（动作只能取 ±1）：成功率 {v['succ_2bins']:.1f}%，"
      f"比连续动作低 {v['succ_drop_2bins']:.1f} 个百分点，抖动涨到 {jit[0]:.4f}"
      f"（是连续动作的 {jit[0] / v['jitter_cont']:.1f} 倍）")
assert v["succ_2bins"] < v["succ_cont"] - 20.0, "分箱太少，成功率明显下降"

r3 = evaluate(pol, test_poses, test_starts, SIM, seed=7, bins=BINS_ODD)
v["succ_3bins"] = r3["success_pct"]
print(f"分 3 个箱（取值 −1、0、+1）：成功率 {v['succ_3bins']:.1f}%——"
      f"**连“闭合夹爪”这一位都表达不出来了**：夹爪那一维被四舍五入到 0，永远不闭合，"
      f"于是一次也没成功。离散化不只是精度问题，**它会把某些动作整个抹掉**")
assert v["succ_3bins"] < 1.0, "3 个箱时夹爪指令被抹平，一次都成不了"

# ---------- 二、翻倍的收益递减
gain_s = np.diff(succ)                               # 每翻一倍，成功率涨多少
gain_j = -np.diff(jit)                               # 每翻一倍，抖动降多少
v["succ_gain_per_doubling"] = gain_s.tolist()
v["jitter_gain_per_doubling"] = gain_j.tolist()
print("\n分箱数翻倍换来什么：")
for i in range(len(BINS) - 1):
    print(f"  {BINS[i]:3d} → {BINS[i + 1]:3d}：成功率 {gain_s[i]:+5.1f} 个百分点，"
          f"抖动 {-gain_j[i]:+.4f}")
v["jitter_gain_first"], v["jitter_gain_last"] = float(gain_j[0]), float(gain_j[-1])
v["jitter_gain_ratio"] = v["jitter_gain_first"] / max(v["jitter_gain_last"], 1e-12)
assert np.all(gain_j >= -1e-9), "抖动随分箱数单调下降"
assert v["jitter_gain_first"] > 5 * v["jitter_gain_last"], \
    "翻倍带来的收益递减——头一次翻倍省下的抖动，是最后一次的好几倍"
print(f"**收益递减得很快**：2 → 4 这一次翻倍省下 {v['jitter_gain_first']:.4f} 的抖动，"
      f"128 → 256 只省 {v['jitter_gain_last']:.4f}，差 {v['jitter_gain_ratio']:.0f} 倍")

# ---------- 三、成功率在哪里就饱和了
i_sat = int(np.argmax(succ >= v["succ_cont"] - 3.0))
v["bins_saturate"] = int(BINS[i_sat])
v["succ_saturate"] = float(succ[i_sat])
print(f"\n成功率在 **{v['bins_saturate']} 个箱**上就追平了连续动作"
      f"（{v['succ_saturate']:.1f}% 对 {v['succ_cont']:.1f}%），"
      f"再往上翻到 256 个箱，成功率没有再涨（{v['succ_256bins']:.1f}%）")
assert abs(succ[-1] - v["succ_cont"]) < 6.0, "分到 256 个箱，成功率与连续动作基本一样"
print(f"**所以 256 个箱买的不是成功率，是平顺**：从 {v['bins_saturate']} 个箱到 256 个箱，"
      f"成功率几乎不动，抖动却从 {jit[i_sat]:.4f} 降到 {jit[-1]:.4f}"
      f"（降 {(1 - jit[-1] / jit[i_sat]) * 100:.0f}%）。"
      f"抖动在真机上是实打实的代价——冲击、噪声、减速器磨损")
print("这个算例回答不了什么：这里分的是本书这台玩具臂的关节速度指令。"
      "真模型分的是末端位姿增量，维数、量程、分箱是否均匀都不同；"
      "**不要把这里的 8 个箱和 RT-1 的 256 个箱放在一起比**")

out(**v)
