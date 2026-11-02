"""算例 19.4.1—19.4.2：降尺度能把统计做对，不能保证某一点上是对的（19.4 节）。

（1）粗网格丢掉了什么：把细场平均成粗场，小尺度的能量去了哪。
（2）两种降尺度：直接复制（什么都没加）与"学出来的"（补一份统计上像样的细节）。
    后者的功率谱与真实场对得上，**可它在单点上的误差并不比前者小**——因为它补的细节
    是凭统计生成的，不是从粗场里推出来的。
（3）决定性的一条：**同一个粗场配两个不同的真实细场，学出来的降尺度给出同一个答案。**
"""
import numpy as np

from _ch19 import (coarse_grain, downscale_learned, downscale_naive, fine_field,
                   same_coarse_variant, sharpness)
from bookout import out

N, F = 512, 8
v = {"n_fine": N, "factor": F, "n_coarse": N // F}

# ---------- （1）粗网格丢掉了什么
SLOPE = 1.0          # 谱斜率：小一点，小尺度的能量占比就更接近真实地面场
v["slope"] = SLOPE
truth = fine_field(N, seed=0, slope=SLOPE)
coarse = coarse_grain(truth, F)
v["sharp_truth"] = round(sharpness(truth), 4)
v["var_truth"] = round(float(truth.var()), 4)
v["var_coarse_up"] = round(float(downscale_naive(coarse, F).var()), 4)
v["var_lost_pct"] = (1 - v["var_coarse_up"] / v["var_truth"]) * 100
assert v["var_lost_pct"] > 10, "平均到粗网格，小尺度的方差就没了"

# ---------- （2）两种降尺度
amp = float(np.std(truth - downscale_naive(coarse, F)))   # 该补多少细节，按真实缺口定
v["detail_amp"] = round(amp, 4)
rows = []
for name, f in (("直接复制", downscale_naive(coarse, F)),
                ("学出来的", downscale_learned(coarse, F, amp * 0.9, seed=3, slope=SLOPE))):
    rmse = float(np.sqrt(np.mean((f - truth) ** 2)))
    rows.append((name, round(rmse, 4), round(sharpness(f), 4), round(float(f.var()), 4)))
v["rows"] = rows
v["rmse_naive"], v["sharp_naive"], v["var_naive"] = rows[0][1], rows[0][2], rows[0][3]
v["rmse_learn"], v["sharp_learn"], v["var_learn"] = rows[1][1], rows[1][2], rows[1][3]

assert v["sharp_learn"] > 2.5 * v["sharp_naive"], "学出来的那个看起来像真的——锐度对上了"
assert abs(v["var_learn"] / v["var_truth"] - 1) < 0.5, "方差也大致对上了"
assert v["rmse_learn"] >= v["rmse_naive"], \
    "**可逐点的均方误差并没有变好，反而更差**——补上去的细节是凭统计生成的"
v["rmse_cost_pct"] = (v["rmse_learn"] / v["rmse_naive"] - 1) * 100

# ---------- （3）同一个粗场，两个不同的真实细场
alt = same_coarse_variant(truth, F, seed=11, slope=SLOPE)
v["coarse_corr"] = round(float(np.corrcoef(coarse_grain(alt, F), coarse)[0, 1]), 4)
v["fine_corr"] = round(float(np.corrcoef(alt, truth)[0, 1]), 3)
assert v["coarse_corr"] > 0.999, "两个细场在粗网格上一模一样——这是构造出来的"
assert v["fine_corr"] < 0.8, "在细网格上却明显不同——粗场本来就定不住细节"

# 学出来的降尺度只看粗场，所以对这两个真实细场给出**完全一样**的答案
d1 = downscale_learned(coarse, F, amp * 0.9, seed=3, slope=SLOPE)
d2 = downscale_learned(coarse_grain(alt, F), F, amp * 0.9, seed=3, slope=SLOPE)
v["downscale_corr"] = round(float(np.corrcoef(d1, d2)[0, 1]), 4)
v["rmse_alt"] = round(float(np.sqrt(np.mean((d1 - alt) ** 2))), 4)
assert v["downscale_corr"] > 0.999, \
    "**同一个粗场，降尺度只有一个答案**——它补的是统计，不是这一次的实况"
assert v["rmse_alt"] > 0.5 * v["rmse_learn"], \
    "所以它对另一个同样合法的细场，误差一样大"

out(**v)
