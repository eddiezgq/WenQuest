"""算例 19.2.1—19.2.3："越推越平"是均方误差的最优解本身（19.2 节）。

（1）每个波数的记忆长短不同：小尺度先失忆。
（2）均方误差最优的一步预测，就是把每个分量乘上它自己的相关系数——**所以最优预测一定
    比真实场平**。自回归推 n 步之后振幅是 ρ^n，高波数掉得最快。
（3）把振幅调回去（保锐）：场看起来像真的了，RMSE 却一定更差。**两者只能选一个。**
"""
import numpy as np

from _ch19 import (field_from_complex, mode_correlation, modes_forecast,
                   modes_truth, mse_optimal_amplitude, sharpness, spectrum,
                   extreme_hits)
from bookout import out
from geo_facts import AIFS, GRAPHCAST, SMOOTHING

M, NX = 40, 256
amp = spectrum(M)
rho1 = mode_correlation(M)
v = {"n_modes": M, "n_x": NX}

# ---------- （1）小尺度先失忆
v["rho_k1"] = round(float(rho1[0]), 3)
v["rho_k5"] = round(float(rho1[4]), 3)
v["rho_k20"] = round(float(rho1[19]), 4)
assert v["rho_k1"] > 0.8 > v["rho_k5"] > v["rho_k20"], "波数越高，一步之后剩下的相关越少"

# ---------- （2）推 n 步之后还剩多少
v["keep_rows"] = []
for n in (1, 2, 4, 8, 16):
    keep = mse_optimal_amplitude(rho1, n)
    energy = float(np.sum((amp * keep) ** 2) / np.sum(amp ** 2))
    v["keep_rows"].append((n, round(energy, 4)))
    v[f"energy_n{n}"] = round(energy, 4)
assert v["energy_n1"] < 0.8, "只推一步，均方误差最优的预测就已经丢掉两成以上的能量"
assert v["energy_n16"] < 0.02, "推十六步，几乎只剩最低的那几个波数——场成了一团糊"

# ---------- （3）最优（抹平） vs 保锐
STEP = 4
v["step"] = STEP
rho = rho1 ** STEP
g = np.random.default_rng(0)
N_CASE = 300
res = {"opt": {"rmse": [], "sharp": [], "hit": []},
       "sharp": {"rmse": [], "sharp": [], "hit": []}}
truth_sharp = []
for _ in range(N_CASE):
    z = modes_truth(amp, g)
    z_opt, z_sharp = modes_forecast(z, amp, rho, g)
    truth = field_from_complex(z, NX)
    truth_sharp.append(sharpness(truth))
    for key, zh in (("opt", z_opt), ("sharp", z_sharp)):
        f = field_from_complex(zh, NX)
        res[key]["rmse"].append(np.sqrt(np.mean((f - truth) ** 2)))
        res[key]["sharp"].append(sharpness(f))
        res[key]["hit"].append(extreme_hits(f, truth)[0])

v["truth_sharp"] = round(float(np.mean(truth_sharp)), 4)
for key, tag in (("opt", "opt"), ("sharp", "shp")):
    v[f"rmse_{tag}"] = round(float(np.mean(res[key]["rmse"])), 4)
    v[f"sharp_{tag}"] = round(float(np.mean(res[key]["sharp"])), 4)
    v[f"hit_{tag}"] = round(float(np.nanmean(res[key]["hit"])), 3)

v["rmse_cost_pct"] = (v["rmse_shp"] / v["rmse_opt"] - 1) * 100
v["sharp_ratio"] = v["truth_sharp"] / v["sharp_opt"]
v["hit_ratio"] = v["hit_shp"] / max(v["hit_opt"], 1e-9)

assert v["rmse_opt"] < v["rmse_shp"], "抹平的那个 RMSE 一定更低——这是均方误差的定义决定的"
assert v["sharp_opt"] < v["truth_sharp"] / 2, "可它比真实场平了一倍以上"
assert v["hit_shp"] > 3 * v["hit_opt"], "而保锐的那个在极端事件上好几倍"

# ---------- 口径：这件事有比 AI 论文早得多的官方引文
v["ecmwf_mos"] = SMOOTHING["ecmwf_mos"]
v["ecmwf_caveat"] = SMOOTHING["ecmwf_caveat"]
v["graphcast_quote"] = GRAPHCAST["blur_quote"]
v["aifs_limit"] = AIFS["limits"][0]
# ---------- 两个模型的公开口径（数从事实模块来，不手抄）
v["gc_res"] = GRAPHCAST["res_deg"]
v["gc_levels"] = GRAPHCAST["levels"]
v["gc_step"] = GRAPHCAST["step_h"]
v["gc_params"] = GRAPHCAST["params_m"]
v["aifs_levels"] = AIFS["levels"]
v["aifs_step"] = AIFS["step_h"]
v["aifs_res_announce"] = AIFS["res_km_announcement"]
v["aifs_res_card"] = AIFS["res_km_modelcard"]
assert v["aifs_res_announce"] != v["aifs_res_card"], \
    "官方公告与官方模型卡给的分辨率不一样——本书两个都印，不替任何一方圆场"
v["aifs_params_known"] = AIFS["params"] is not None
assert not v["aifs_params_known"], "AIFS 的参数量官方未公布"
v["aifs_day1_split"] = AIFS["day1_worse_vs_analysis"] and AIFS["day1_not_worse_vs_radiosonde"]
assert v["aifs_day1_split"], "同一个模型，对分析场评分与对探空观测评分给出相反的结论"

v["graphcast_rmse_known"] = GRAPHCAST["rmse_values"] is not None
assert not v["graphcast_rmse_known"], "GraphCast 正文不给绝对 RMSE，只给技巧改进百分比"

out(**v)
