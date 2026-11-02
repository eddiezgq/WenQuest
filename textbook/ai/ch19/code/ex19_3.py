"""算例 19.3.1—19.3.4：概率预报——为什么一个确定性预报不够（19.3 节）。

（1）CRPS 的两种标准估计量分母不同；M = 1 时它退化成平均绝对误差。
（2）离散度不足与离散度过大各是什么样：离散度/技巧比与 CRPS 一起看才判得准。
（3）可靠性图：预报说 70% 的那些次，是不是真的有七成发生了。
（4）把同一套集合压成一个确定性预报：RMSE 可以更低，可"低于切入风速的概率"这类问题
    它一个也答不了。
"""
import numpy as np

from _ch19 import (brier, crps_ensemble, make_ensemble, reliability,
                   spread_skill)
from bookout import out
from geo_facts import CRPS, ERA5, IFS

M, N = 50, 4000
v = {"n_members": M, "n_cases": N}

# ---------- （1）两种估计量
mem, obs = make_ensemble(M, N, seed=1)
v["crps_unbiased"] = round(crps_ensemble(mem, obs, unbiased=True), 4)
v["crps_biased"] = round(crps_ensemble(mem, obs, unbiased=False), 4)
v["crps_gap_pct"] = (v["crps_biased"] / v["crps_unbiased"] - 1) * 100
v["denom_unbiased"] = CRPS["denominator_wb2"]
v["denom_biased"] = CRPS["denominator_gencast"]
assert v["crps_biased"] > v["crps_unbiased"], "有偏估计量系统性地偏大——分母小一点"
assert CRPS["two_estimators"], "两种估计量都在用，印公式必须说明用的是哪一个"

one = crps_ensemble(mem[:1], obs)
mae = float(np.abs(mem[0] - obs).mean())
v["crps_m1"], v["mae_m1"] = round(one, 4), round(mae, 4)
assert abs(one - mae) < 1e-9, "M = 1 时 CRPS 恰好退化成平均绝对误差"

# ---------- （2）离散度扫一遍
v["spread_rows"] = []
for sf, tag in ((0.5, "05"), (0.8, "08"), (1.0, "10"), (1.4, "14")):
    m2, o2 = make_ensemble(M, N, seed=1, spread_factor=sf)
    sp, rm, ratio = spread_skill(m2, o2)
    cr = crps_ensemble(m2, o2)
    v["spread_rows"].append((sf, round(ratio, 3), round(cr, 4)))
    v[f"ratio_{tag}"], v[f"crps_{tag}"] = round(ratio, 3), round(cr, 4)
assert abs(v["ratio_10"] - 1.0) < 0.05, "校准良好的集合，离散度/技巧比应当接近 1"
assert v["crps_10"] < v["crps_05"] and v["crps_10"] < v["crps_14"], \
    "CRPS 在校准最好的那一档最小——它同时罚'太自信'和'太含糊'"
v["overconfident_cost"] = (v["crps_05"] - v["crps_10"]) * 1000
v["era5_spread_quote"] = ERA5["spread_overconfident"]

# ---------- （3）可靠性图
THRESH = 1.0
v["thresh"] = THRESH
prob = (mem > THRESH).mean(0)
occurred = obs > THRESH
v["rel_rows"] = [(round(c, 2), None if np.isnan(f) else round(f, 3), n)
                 for c, f, n in reliability(prob, occurred)]
for c, f, n in reliability(prob, occurred):          # 正文要印的那几档，逐个取出来
    tag = f"{int(round(c * 100)):02d}"
    v[f"rel_f{tag}"] = None if np.isnan(f) else round(f, 3)
    v[f"rel_n{tag}"] = n
v["brier"] = round(brier(prob, occurred), 4)
v["brier_clim"] = round(brier(np.full(N, occurred.mean()), occurred), 4)
v["brier_skill"] = round(1 - v["brier"] / v["brier_clim"], 3)
assert v["brier"] < v["brier_clim"], "这个集合比'每次都报气候概率'好"
fin = [(c, f) for c, f, n in reliability(prob, occurred) if n > 30 and not np.isnan(f)]
v["rel_max_dev"] = round(max(abs(c - f) for c, f in fin), 3)
assert v["rel_max_dev"] < 0.12, "点基本落在 45° 对角线附近——这个集合是可靠的"

# 离散度不足的集合，可靠性图会歪到哪一边
m3, o3 = make_ensemble(M, N, seed=1, spread_factor=0.5)
p3 = (m3 > THRESH).mean(0)
fin3 = [(c, f) for c, f, n in reliability(p3, o3 > THRESH) if n > 30 and not np.isnan(f)]
v["rel_max_dev_over"] = round(max(abs(c - f) for c, f in fin3), 3)
v["brier_over"] = round(brier(p3, o3 > THRESH), 4)
assert v["rel_max_dev_over"] > 2 * v["rel_max_dev"], \
    "太自信的集合，可靠性图明显离开对角线"

# ---------- （4）压成一个确定性预报会丢掉什么
det = mem.mean(0)
v["rmse_det"] = round(float(np.sqrt(((det - obs) ** 2).mean())), 4)
v["mae_det"] = round(float(np.abs(det - obs).mean()), 4)
v["crps_ens"] = v["crps_unbiased"]
assert v["mae_det"] > v["crps_ens"], \
    "集合的 CRPS 比确定性预报的平均绝对误差小——这正是 CRPS 把'说得准'也算进去的结果"
v["det_prob_answerable"] = False
v["ens_members"] = IFS and 51          # ECMWF 中期集合：50 个扰动成员 + 1 个控制

out(**v)
