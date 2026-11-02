"""算例 19.6.1—19.6.3：案例——风电场明天发多少电（19.6 节）。

（1）风功率与风速是三次方关系，所以**同样大的风速误差，在不同风速上造成的发电量误差
    差得很远**。
（2）确定性预报答不了电网真正要问的那个问题："明天低于切入风速的概率是多少"。
（3）一个校准良好的集合能答，而且它的价值可以折算成钱（少挨多少罚）。

**本章不印任何"AI 把预报误差降低了 X%"的数**：没有口径完整的公开来源。这一节的账全部
由本书按风功率曲线自己算，并明写是折算。
"""
import numpy as np

from _ch19 import WIND, power_curve, power_error, wind_cases
from bookout import out
from geo_facts import WIND as WIND_FACTS

v = {"cut_in": WIND["cut_in"], "rated": WIND["rated"], "cut_out": WIND["cut_out"]}
v["power_law"] = WIND_FACTS["power_law"]
v["published_relation_known"] = WIND_FACTS["speed_to_power_published"] is not None
assert not v["published_relation_known"], \
    "'风速误差→功率误差'的量化关系核不到口径完整的公开来源，这一节的账是本书的折算"

# ---------- （1）同样 1 m/s 的风速误差，在不同风速上差多少
ERR = 1.0
v["speed_err"] = ERR
v["rows"] = []
for vv in (4.0, 6.0, 8.0, 10.0, 12.0, 14.0):
    dp = float(power_error(np.array([vv]), ERR)[0]) * 100
    v["rows"].append((vv, round(float(power_curve(np.array([vv]))[0]) * 100, 1), round(dp, 1)))
    v[f"dp_v{int(vv)}"] = round(dp, 1)
    v[f"p_v{int(vv)}"] = round(float(power_curve(np.array([vv]))[0]) * 100, 1)
assert v["dp_v8"] > 3 * v["dp_v12"], \
    "额定以上再刮大风也不多发电，所以同样的风速误差在那里几乎不造成功率误差"
assert v["dp_v10"] > v["dp_v4"], "三次方关系：风速越高，同样的误差放大得越厉害"
v["worst_v"] = max(v["rows"], key=lambda r: r[2])[0]
v["worst_dp"] = max(r[2] for r in v["rows"])

# ---------- （2）一批真实风速上的账
N = 20000
g = np.random.default_rng(0)
vt = wind_cases(N, seed=0, mean=8.0)
v["n_cases"] = N
v["mean_speed"] = round(float(vt.mean()), 2)
v["below_cutin_pct"] = round(float((vt < WIND["cut_in"]).mean()) * 100, 2)
v["above_rated_pct"] = round(float((vt >= WIND["rated"]).mean()) * 100, 1)

for sd, tag in ((0.5, "05"), (1.0, "10"), (2.0, "20")):
    err = g.normal(0, sd, N)
    dp = power_curve(vt + err) - power_curve(vt)
    v[f"mape_{tag}"] = round(float(np.abs(dp).mean()) * 100, 2)
    v[f"p90_{tag}"] = round(float(np.quantile(np.abs(dp), 0.9)) * 100, 2)
assert v["mape_20"] > 1.5 * v["mape_10"], "风速误差翻倍，功率误差涨得更快"
v["amplify"] = round(v["mape_20"] / v["mape_10"], 2)

# ---------- （3）确定性预报答不了的那个问题
TRUE_SD = 1.6                   # 明天风速的真实不确定性
M = 50
sig = g.normal(0, 2.0, N) + 8.0                      # "可预报的那部分"
truth = sig + g.normal(0, TRUE_SD, N)
det = sig                                            # 确定性预报：只给一个数
ens = sig[None, :] + g.normal(0, TRUE_SD, (M, N))    # 校准良好的集合

v["rmse_det"] = round(float(np.sqrt(((det - truth) ** 2).mean())), 3)
v["rmse_ens_mean"] = round(float(np.sqrt(((ens.mean(0) - truth) ** 2).mean())), 3)
assert abs(v["rmse_det"] - v["rmse_ens_mean"]) < 0.1, \
    "集合均值与确定性预报的 RMSE 差不多——所以光看 RMSE 看不出集合的价值"

# 电网真正要问的：明天低于切入风速的概率
occurred = truth < WIND["cut_in"]
v["event_rate_pct"] = round(float(occurred.mean()) * 100, 2)
p_ens = (ens < WIND["cut_in"]).mean(0)
p_det = (det < WIND["cut_in"]).astype(float)         # 确定性预报只能答"是"或"否"
v["brier_ens"] = round(float(((p_ens - occurred) ** 2).mean()), 4)
v["brier_det"] = round(float(((p_det - occurred) ** 2).mean()), 4)
v["brier_clim"] = round(float(((occurred.mean() - occurred) ** 2).mean()), 4)
assert v["brier_ens"] < v["brier_det"], \
    "同一套信息，集合给的概率比'一刀切'的是/否好得多"
assert v["brier_ens"] < v["brier_clim"], "也比每次都报气候概率好"
v["brier_gain_pct"] = (1 - v["brier_ens"] / v["brier_det"]) * 100
v["skill_ens"] = round(1 - v["brier_ens"] / v["brier_clim"], 3)
v["skill_det"] = round(1 - v["brier_det"] / v["brier_clim"], 3)
v["skill_ratio"] = round(v["skill_ens"] / max(v["skill_det"], 1e-9), 1)
assert v["skill_ens"] > 3 * v["skill_det"], \
    "**RMSE 一模一样，而回答概率问题的本事差好几倍**——这正是确定性预报的盲区"

out(**v)
