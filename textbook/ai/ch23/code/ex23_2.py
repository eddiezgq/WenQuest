"""算例 23.3.1：多传感器融合，以及一个偶尔骗人的传感器怎样把融合拖坏（23.3 节）。

三件事：
（1）**干净的时候，融合确实比任一路单用都好**——这是融合值得做的理由；
（2）**有一路偶尔骗人的时候，朴素融合比只用好的那一路还差**。这不是实现 bug，
    是卡尔曼滤波的前提（观测误差是零均值高斯）被破坏了；
（3）加一行新息门限（观测与预测差得太远就这一帧不信它），能恢复多少——以及它的代价
    （真的目标突然出现时，门限也会把它挡在外面）。

传感器的两种真实失效方式都写进来了：**野值**（误检到更远的目标上）与**卡死**
（跟踪器锁在上一帧不动）。高斯噪声不是失效，这两种才是。
"""
import numpy as np

from _ch23 import DT, camera_range, kalman_fuse, lead_track, radar_range
from bookout import out

N = 1200                   # 60 s
v = {"n_steps": N, "dt_s": DT, "duration_s": N * DT}

s_l, v_l = lead_track(N, DT, seed=4)
s_e = np.cumsum(np.full(N, 21.0)) * DT
x_true = s_l - s_e                       # 真实距离（m）
v["range_min_m"], v["range_max_m"] = float(x_true.min()), float(x_true.max())
v["range_mean_m"] = float(x_true.mean())
print(f"{v['duration_s']:.0f} s 的跟车，真实距离在 {v['range_min_m']:.1f}—"
      f"{v['range_max_m']:.1f} m 之间（均值 {v['range_mean_m']:.1f} m）")

SIG_A = 0.45                             # 毫米波式：与距离无关
REL_B = 0.022                            # 相机式：按距离成比例
SIG_B = REL_B * v["range_mean_m"]        # 折成给滤波器用的等效标准差
v["sigma_a_m"], v["rel_b"], v["sigma_b_m"] = SIG_A, REL_B, SIG_B
print(f"传感器 A（毫米波式）：标准差 {SIG_A:.2f} m，与距离无关")
print(f"传感器 B（相机式）：相对标准差 {REL_B:.1%}，在均值距离上折成 {SIG_B:.2f} m")


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def p95(a, b):
    return float(np.quantile(np.abs(np.asarray(a) - np.asarray(b)), 0.95))


# ================================================ 一、干净的时候：融合确实更好
g = np.random.default_rng(11)
z_a = radar_range(x_true, g, SIG_A)
z_b = camera_range(x_true, g, REL_B)

est_a, _ = kalman_fuse([(z_a, SIG_A)])
est_b, _ = kalman_fuse([(z_b, SIG_B)])
est_ab, _ = kalman_fuse([(z_a, SIG_A), (z_b, SIG_B)])

v["rmse_clean_a"] = rmse(est_a, x_true)
v["rmse_clean_b"] = rmse(est_b, x_true)
v["rmse_clean_fused"] = rmse(est_ab, x_true)
v["fuse_gain_pct"] = (1 - v["rmse_clean_fused"] / min(v["rmse_clean_a"], v["rmse_clean_b"])) * 100
print(f"\n【干净】只用 A：{v['rmse_clean_a']:.3f} m；只用 B：{v['rmse_clean_b']:.3f} m；"
      f"融合：{v['rmse_clean_fused']:.3f} m")
assert v["rmse_clean_fused"] < min(v["rmse_clean_a"], v["rmse_clean_b"]), \
    "两路都是零均值高斯时，融合必须比任一路单用都好"
print(f"融合比更好的那一路又好 {v['fuse_gain_pct']:.1f}%——**这才是融合值得做的理由**")

# ================================================ 二、一路偶尔骗人
OUT_P = 0.03               # 野值概率，显式假设
OUT_M = 14.0               # 野值偏移（m）：误检到后面一辆车上
STUCK = (520, 580)         # 卡死 3 s：跟踪器锁在上一帧不动
v["outlier_p"] = OUT_P
v["outlier_m"] = OUT_M
v["stuck_s"] = (STUCK[1] - STUCK[0]) * DT

g2 = np.random.default_rng(11)
z_a2 = radar_range(x_true, g2, SIG_A)
z_b2 = camera_range(x_true, g2, REL_B, outlier_p=OUT_P, outlier_m=OUT_M, stuck=STUCK)
v["n_outlier_like"] = int(np.sum(np.abs(z_b2 - x_true) > 5.0))
v["bad_frac_pct"] = v["n_outlier_like"] / N * 100
print(f"\n【B 偶尔骗人】野值概率 {OUT_P:.0%}（偏 {OUT_M:.0f} m），再加一段 "
      f"{v['stuck_s']:.1f} s 的卡死")
print(f"B 这一路里偏真值 5 m 以上的帧共 {v['n_outlier_like']} 帧，占 {v['bad_frac_pct']:.1f}%")

est_a3, _ = kalman_fuse([(z_a2, SIG_A)])
est_b3, _ = kalman_fuse([(z_b2, SIG_B)])
est_naive, _ = kalman_fuse([(z_a2, SIG_A), (z_b2, SIG_B)])

v["rmse_bad_a"] = rmse(est_a3, x_true)
v["rmse_bad_b"] = rmse(est_b3, x_true)
v["rmse_bad_naive"] = rmse(est_naive, x_true)
v["p95_bad_a"] = p95(est_a3, x_true)
v["p95_bad_naive"] = p95(est_naive, x_true)
print(f"只用 A：{v['rmse_bad_a']:.3f} m（95 分位 {v['p95_bad_a']:.3f} m）")
print(f"只用 B：{v['rmse_bad_b']:.3f} m")
print(f"朴素融合（来什么都吃）：{v['rmse_bad_naive']:.3f} m"
      f"（95 分位 {v['p95_bad_naive']:.3f} m）")
v["naive_worse_than_a_pct"] = (v["rmse_bad_naive"] / v["rmse_bad_a"] - 1) * 100
assert v["rmse_bad_naive"] > v["rmse_bad_a"], \
    "有野值时，朴素融合必须比只用好的那一路更差——这正是本节要教的事"
print(f"**朴素融合比只用 A 差 {v['naive_worse_than_a_pct']:.0f}%**："
      f"多一路传感器，结果更差了。多传感器融合不是“越多越好”")

# ================================================ 三、加新息门限
print("\n门限扫一遍（σ 是新息的理论标准差，含预测不确定度）：")
GATES = (8.0, 6.0, 5.0, 4.0, 3.0, 2.0)
sweep = []
for gate in GATES:
    est_g, rej = kalman_fuse([(z_a2, SIG_A), (z_b2, SIG_B)], gate=gate)
    tag = f"{gate:.0f}s"
    v[f"rmse_gate_{tag}"] = rmse(est_g, x_true)
    v[f"rej_pct_gate_{tag}"] = rej / (2 * N) * 100
    sweep.append((gate, v[f"rmse_gate_{tag}"], rej))
    print(f"  {gate:.0f}σ：{v[f'rmse_gate_{tag}']:7.3f} m，挡掉 {rej:4d} 次观测"
          f"（占全部观测的 {v[f'rej_pct_gate_{tag}']:4.1f}%）")

g_best, rm_best, rej_best = min(sweep, key=lambda t: t[1])
v["gate_best"] = g_best
v["rmse_gated"] = rm_best
v["rej_best"] = rej_best
v["recover_pct"] = (1 - v["rmse_gated"] / v["rmse_bad_naive"]) * 100
v["gated_vs_a_pct"] = (1 - v["rmse_gated"] / v["rmse_bad_a"]) * 100
v["gated_vs_clean_ratio"] = v["rmse_gated"] / v["rmse_clean_fused"]
assert v["rmse_gated"] < v["rmse_bad_naive"], "门限必须把朴素融合被拖坏的那一部分收回来"
assert v["rmse_gated"] < v["rmse_bad_a"], "加了门限，融合应当重新比单传感器好"
print(f"\n最好的那一档是 {g_best:.0f}σ：{v['rmse_gated']:.3f} m，"
      f"比朴素融合好 {v['recover_pct']:.0f}%，比只用 A 好 {v['gated_vs_a_pct']:.1f}%，"
      f"几乎回到干净情形下的融合结果（是它的 {v['gated_vs_clean_ratio']:.2f} 倍）")

# **要照实报的一条：门限不是越紧越好。** 3σ、2σ 反而比朴素融合还差
v["rmse_gate_tight"] = v["rmse_gate_3s"]
v["tight_vs_naive_pct"] = (v["rmse_gate_tight"] / v["rmse_bad_naive"] - 1) * 100
assert v["rmse_gate_3s"] > v["rmse_bad_naive"] and v["rmse_gate_2s"] > v["rmse_gate_3s"], \
    "门限收得太紧会比不设门限更差——这条要照实印，不许只报最好的那一档"
print(f"**但门限不是越紧越好**：收到 3σ 就比朴素融合还差 "
      f"{v['tight_vs_naive_pct']:.0f}%，2σ 更差（{v['rmse_gate_2s']:.3f} m）。"
      f"原因不难看：前车急刹时，匀加速模型的新息本来就会冲高，"
      f"**紧门限正好在最该相信传感器的那几帧把好观测也挡在外面**。"
      f"所以门限要用自己的残差分布标，不能照抄一个“3σ 保险”。")

# ================================================ 四、门限的代价：真目标也会被挡在外面
# 一辆车突然切入，真实距离一步跳近 12 m。两路都看到了，但门限会把这一帧当野值
CUT_K = 800
CUT_M = -12.0
x_cut = x_true.copy()
x_cut[CUT_K:] += CUT_M
g3 = np.random.default_rng(31)
z_ac = radar_range(x_cut, g3, SIG_A)
z_bc = camera_range(x_cut, g3, REL_B)
v["cutin_k"], v["cutin_m"] = CUT_K, CUT_M
for gate, tag in ((None, "none"), (3.0, "3p0"), (2.0, "2p0")):
    est_c, _ = kalman_fuse([(z_ac, SIG_A), (z_bc, SIG_B)], gate=gate)
    err = np.abs(est_c - x_cut)
    # 多少拍之后估计值重新跟上（误差回到 1 m 以内）
    after = err[CUT_K:CUT_K + 200]
    ok = np.where(after < 1.0)[0]
    v[f"settle_steps_{tag}"] = int(ok[0]) if len(ok) else 200
    v[f"settle_s_{tag}"] = v[f"settle_steps_{tag}"] * DT
    v[f"cutin_peak_{tag}"] = float(after.max())
    print(f"切入后，门限 {tag}：峰值误差 {v[f'cutin_peak_{tag}']:.2f} m，"
          f"{v[f'settle_s_{tag}']:.2f} s 才跟上")
assert v["settle_steps_2p0"] >= v["settle_steps_none"], \
    "门限越紧，真目标突然出现时跟上得越慢——这是门限的代价"
v["gate_cost_s"] = v["settle_s_2p0"] - v["settle_s_none"]
print(f"**门限的价钱是 {v['gate_cost_s']:.2f} s 的反应迟滞**（2σ 对不设门限）："
      f"它分不清“传感器在骗我”与“世界真的变了”，只能按“变得太快就先不信”办")

print("\n这个算例回答不了什么：真传感器的失效方式远不止野值与卡死（多路径、同步错位、"
      "标定漂移、整路掉线），而且常常**两路一起错**（同一场雨、同一片逆光），"
      "那时门限挡谁都不对；本算例的两路误差是独立的，这个前提在真车上经常不成立。"
      "门限参数也不能照抄：它要用本车自己的观测残差分布标出来。")

out(**v)
