"""算例 14.5.1—14.5.3：把动作也当词元（14.5 节）。

（1）动作怎样离散成词元：7 维、每维 256 个区间。区间按**第 1—99 分位数**划分还是按极值划分，
    差别有多大——示教记录里总有几条手抖的离群值，按极值划分会把量程撑坏，正常动作全挤进几个区间。
（2）离散化本身带来的误差：区间数从 64 到 1024，量化误差怎样降，与机器人的重复定位精度比一比。
（3）频率的账：模型跑一次要多久，控制周期有多长，差多少。公开数字：RT-2-55B 是 1—3 Hz，
    OpenVLA 在一块 4090 上约 6 Hz，而真机控制器要 5—15 Hz。
"""
import numpy as np

from _ch14 import action_log, dequantize, quantize
from bookout import out
from mm_facts import OPENVLA, RT2

v = {}
a = action_log(4000, seed=0)
v["n_steps"], v["dims"] = a.shape[0], a.shape[1]
v["bins"] = OPENVLA["bins"]
v["q_lo"], v["q_hi"] = OPENVLA["quantile"]

# ---------- （1）分位数 vs 极值
rows, err = [], {}
for tag in ("分位数", "极值"):
    tot, occ = [], []
    for j in range(3):                                   # 只看三个位置增量（离群值在这几维上）
        x = a[:, j]
        lo, hi = (np.percentile(x, v["q_lo"]), np.percentile(x, v["q_hi"])) if tag == "分位数" else (x.min(), x.max())
        q = quantize(x, lo, hi, v["bins"])
        back = dequantize(q, lo, hi, v["bins"])
        inside = (x >= lo) & (x <= hi)
        tot.append(float(np.abs(back[inside] - x[inside]).mean()))
        occ.append(len(np.unique(q)))
    err[tag] = (float(np.mean(tot)), float(np.mean(occ)))
    rows.append((tag, round(err[tag][0] * 1000, 4), round(err[tag][1], 1)))
v["quant_rows"] = rows                                    # （口径, 平均量化误差 mm, 用到的区间数）
v["err_q_um"] = err["分位数"][0] * 1e6                     # 微米
v["err_m_um"] = err["极值"][0] * 1e6
v["bins_used_q"], v["bins_used_m"] = err["分位数"][1], err["极值"][1]
v["err_ratio"] = v["err_m_um"] / v["err_q_um"]
assert v["err_ratio"] > 3, "按极值划分，正常动作上的量化误差要大好几倍"
v["clip_share"] = float(((a[:, 0] < np.percentile(a[:, 0], 1)) | (a[:, 0] > np.percentile(a[:, 0], 99))).mean() * 100)

# ---------- （2）区间数与量化误差
x = a[:, 0]
lo, hi = np.percentile(x, v["q_lo"]), np.percentile(x, v["q_hi"])
rows_b = []
for b in (64, 128, 256, 1024):
    back = dequantize(quantize(x, lo, hi, b), lo, hi, b)
    inside = (x >= lo) & (x <= hi)
    rows_b.append((b, round(float(np.abs(back[inside] - x[inside]).mean()) * 1e6, 1)))
v["bin_rows"] = rows_b                                    # （区间数, 平均误差 μm）
v["err_64"], v["err_1024"] = rows_b[0][1], rows_b[-1][1]
v["err_256"] = rows_b[2][1]
REPEAT_UM = 30.0                                          # 一台工业机械臂的重复定位精度（微米，数字工厂 WQR-105）
v["repeat_um"] = REPEAT_UM
v["err_vs_repeat"] = v["err_256"] / REPEAT_UM
# 256 个区间在这个量程上给出的误差与机器人自身的重复定位精度同一量级：够用，但不富裕。
# 量程越大，同样的区间数就越粗——这正是要按分位数而不是按极值定量程的理由。
assert 0.5 < v["err_vs_repeat"] < 3, "256 个区间的量化误差与重复定位精度同一量级"
assert v["err_64"] > v["err_256"] > v["err_1024"]
v["vocab_cost"] = v["dims"] * 1                           # 一步动作占几个词元：每维一个
v["tokens_per_sec_6hz"] = v["vocab_cost"] * 6

# ---------- （3）频率的账
v["rt2_55b_lo"], v["rt2_55b_hi"] = RT2["hz_55b"]
v["rt2_5b"] = RT2["hz_5b"]
v["openvla_hz"] = OPENVLA["hz_4090"]
v["ctrl_lo"], v["ctrl_hi"] = OPENVLA["ctrl_hz"]
v["period_model_ms"] = 1000.0 / v["openvla_hz"]
v["period_ctrl_ms"] = 1000.0 / v["ctrl_hi"]
v["behind"] = v["period_model_ms"] / v["period_ctrl_ms"]
assert v["behind"] > 1, "模型出一条动作的时间，比高频控制器的一个周期长得多"
# 一条传送带上的零件在这段时间里走多远
BELT_MM_S = 150.0
v["belt_mm_s"] = BELT_MM_S
v["drift_mm"] = BELT_MM_S * v["period_model_ms"] / 1000
v["openvla_params_B"] = OPENVLA["params"] / 1e9
v["openvla_a100h"] = OPENVLA["a100_hours"]
v["openvla_demos_w"] = OPENVLA["demos"] / 1e4             # 万条
v["openvla_int4_gb"], v["openvla_bf16_gb"] = OPENVLA["mem_int4_gb"], OPENVLA["mem_bf16_gb"]
v["succ_bf16"], v["succ_int4"] = OPENVLA["succ_bf16"], OPENVLA["succ_int4"]
v["mem_save"] = v["openvla_bf16_gb"] / v["openvla_int4_gb"]
v["over_rt2x_points"] = OPENVLA["over_rt2x_points"]
v["rt2_unseen"], v["rt2_rt1_unseen"] = RT2["unseen_55b"], RT2["unseen_rt1"]
v["rt2_seen"], v["rt2_rt1_seen"] = RT2["seen_55b"], RT2["seen_rt1"]
out(**v)
