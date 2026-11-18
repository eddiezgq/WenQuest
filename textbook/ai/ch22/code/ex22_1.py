"""算例 22.1.1—22.1.3：光伏功率预测，以及为什么要分位数（22.1 节）。

三件事：
（1）**先打赢两个笨基线**：昨天的今天（持续法）与历史同时刻平均（气候法）。打不赢，
    说明模型什么也没学到；
（2）**点预测回答不了调度要问的问题**。调度问的是"有多大把握不低于多少"，
    这要分位数预测；
（3）**区间的名义覆盖率与实际覆盖率是两回事**，必须报实际的——这是第 19 章可靠性图
    在本章的回声。
"""
import numpy as np

from _ch22 import (STEPS_PER_DAY, climatology, coverage, design_matrix, cloud_factor,
                   fit_ls, fit_quantile, interval_width, persistence, pinball, pv_series)
from bookout import out

N_DAYS = 60
v = {"n_days": N_DAYS, "steps_per_day": STEPS_PER_DAY}

pv = pv_series(N_DAYS, seed=0)
true_cloud = cloud_factor(N_DAYS, seed=0)
g = np.random.default_rng(5)
fc_cloud = np.clip(true_cloud + 0.12 * g.normal(0, 1, len(true_cloud)), 0, 1)   # 带误差的气象预报
X = design_matrix(N_DAYS, fc_cloud)

n = len(pv)
cut = int(n * 0.7)
tr, te = np.arange(cut), np.arange(cut, n)
v["n_train"], v["n_test"] = len(tr), len(te)
day_mask = pv[te] > 1.0                      # 夜里全是 0，评估只看白天
v["n_daylight"] = int(day_mask.sum())


def rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


# ---------- 一、两个笨基线
p_per = persistence(pv)[te]
p_cli = climatology(pv)[te]
w = fit_ls(X[tr], pv[tr])
p_mod = np.maximum(X[te] @ w, 0.0)

for name, tag, p in (("持续法（昨天的今天）", "pers", p_per),
                     ("气候法（历史同时刻平均）", "clim", p_cli),
                     ("带气象的回归", "model", p_mod)):
    v[f"rmse_{tag}"] = rmse(pv[te][day_mask], p[day_mask])
    v[f"mae_{tag}"] = float(np.mean(np.abs(pv[te][day_mask] - p[day_mask])))
    print(f"{name:>16}：白天的均方根误差 {v[f'rmse_{tag}']:7.2f} kW，"
          f"平均绝对误差 {v[f'mae_{tag}']:7.2f} kW")
v["gain_vs_pers"] = v["rmse_pers"] / v["rmse_model"]
v["gain_vs_clim"] = v["rmse_clim"] / v["rmse_model"]
assert v["rmse_model"] < v["rmse_clim"] < v["rmse_pers"], "模型要先打赢两个笨基线"
print(f"模型比持续法好 {v['gain_vs_pers']:.1f} 倍、比气候法好 {v['gain_vs_clim']:.1f} 倍")
print("**打不赢这两个基线的模型，不要上线**——它们一行特征工程都不需要")

# ---------- 二、分位数预测
QS = (0.1, 0.5, 0.9)
preds = {}
for q in QS:
    wq = fit_quantile(X[tr], pv[tr], q)
    preds[q] = np.maximum(X[te] @ wq, 0.0)
    v[f"pinball_{int(q * 100)}"] = pinball(pv[te][day_mask], preds[q][day_mask], q)
    print(f"分位数 {q:.1f}：弹球损失 {v[f'pinball_{int(q * 100)}']:.3f}")

lo, hi = preds[0.1], preds[0.9]
v["cover_nominal"] = 80.0                    # 10%—90% 的区间，名义覆盖 80%
v["cover_actual"] = coverage(pv[te][day_mask], lo[day_mask], hi[day_mask])
v["width_mean"] = interval_width(lo[day_mask], hi[day_mask])
v["cover_gap"] = v["cover_actual"] - v["cover_nominal"]
print(f"\n名义 {v['cover_nominal']:.0f}% 的区间，实际盖住 {v['cover_actual']:.1f}%"
      f"（差 {v['cover_gap']:+.1f} 个百分点），平均宽 {v['width_mean']:.1f} kW")
print("**报区间必须报实际覆盖率**：名义值是你要的，实际值才是你有的")

# ---------- 三、点预测回答不了的问题
# 调度要的是"有多大把握不低于多少"。拿点预测当这个数，会错多少？
need = preds[0.5]                            # 以中位数当"保证出力"
short = np.maximum(need[day_mask] - pv[te][day_mask], 0.0)
v["median_short_rate"] = float(np.mean(short > 0)) * 100
v["median_short_mean"] = float(np.mean(short))
q10_short = np.maximum(lo[day_mask] - pv[te][day_mask], 0.0)
v["q10_short_rate"] = float(np.mean(q10_short > 0)) * 100
v["q10_short_mean"] = float(np.mean(q10_short))
print(f"\n拿中位数当“保证出力”：有 {v['median_short_rate']:.0f}% 的时刻达不到，"
      f"平均差 {v['median_short_mean']:.1f} kW")
print(f"拿 10% 分位当“保证出力”：只有 {v['q10_short_rate']:.0f}% 的时刻达不到，"
      f"平均差 {v['q10_short_mean']:.1f} kW")
assert v["q10_short_rate"] < v["median_short_rate"], "低分位数就是为这个用的"
v["short_ratio"] = v["median_short_rate"] / max(v["q10_short_rate"], 1e-9)
print(f"**差 {v['short_ratio']:.1f} 倍**——这就是调度为什么要分位数，而不是点预测")

# ---------- 四、换一种天气型还准不准
pv_calm = pv_series(20, seed=77, calm=0.75)          # 更晴的一段
cloud_calm = cloud_factor(20, seed=77, calm=0.75)
X_calm = design_matrix(20, np.clip(cloud_calm + 0.12 * g.normal(0, 1, len(cloud_calm)), 0, 1))
p_calm = np.maximum(X_calm @ w, 0.0)
m2 = pv_calm > 1.0
v["rmse_newweather"] = rmse(pv_calm[m2], p_calm[m2])
v["weather_ratio"] = v["rmse_newweather"] / v["rmse_model"]
print(f"\n换一段更晴的天气：均方根误差 {v['rmse_newweather']:.2f} kW，"
      f"是原来那段的 {v['weather_ratio']:.2f} 倍")
print("所以验收除了按时间划分，还要单独报**换一种天气型**的那个数")

out(**v)
