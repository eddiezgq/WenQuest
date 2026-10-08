"""算例 M3.2.1—M3.2.3：期望、方差、大数定律与中心极限定理（M3.2 节）。

抽检 n 个零件，看到的坏件数是个随机变量。本程序算清三件事：
（1）它的期望与方差（二项分布），以及"抽多少个才看得出"；
（2）大数定律：样本比例随 n 收敛到真实比例，误差按 1/√n 缩小——这是整本书里最常用的那个尺子；
（3）中心极限定理：不管原来的分布什么样，样本均值的分布都趋于正态——这是置信区间的依据（M3.7 节）。
"""
import numpy as np

from _chM3 import P_BAD, rng
from bookout import out

v = {"p": P_BAD}
# ---------- （1）二项分布的期望与方差
for n in (50, 200, 1000):
    v[f"mean_{n}"] = n * P_BAD
    v[f"sd_{n}"] = float(np.sqrt(n * P_BAD * (1 - P_BAD)))
    v[f"p0_{n}"] = float((1 - P_BAD) ** n)                    # 一个坏件都没抽到的概率
v["p0_50_pct"] = v["p0_50"] * 100
v["n_for_one"] = int(np.ceil(1 / P_BAD))                      # 平均抽多少个才遇到一个坏件
# 要有 95% 的把握至少抽到一个坏件，n 要多大
v["n_95"] = int(np.ceil(np.log(0.05) / np.log(1 - P_BAD)))
assert (1 - P_BAD) ** v["n_95"] <= 0.05 < (1 - P_BAD) ** (v["n_95"] - 1)

# ---------- （2）大数定律：误差按 1/√n 缩小
g = rng(1)
REP = 2000
for n in (25, 100, 400, 1600):
    s = g.binomial(n, P_BAD, REP) / n
    v[f"err_{n}"] = float(np.abs(s - P_BAD).mean())           # 平均绝对误差
    v[f"sd_hat_{n}"] = float(s.std(ddof=1))
v["ratio_25_100"] = v["sd_hat_25"] / v["sd_hat_100"]          # n 翻 4 倍，波动减半
v["ratio_100_400"] = v["sd_hat_100"] / v["sd_hat_400"]
v["ratio_400_1600"] = v["sd_hat_400"] / v["sd_hat_1600"]
for r in ("ratio_25_100", "ratio_100_400", "ratio_400_1600"):
    assert 1.7 < v[r] < 2.3, "n 翻 4 倍，标准差应当大约减半"
v["sd_theory_400"] = float(np.sqrt(P_BAD * (1 - P_BAD) / 400))
v["sd_rel_err_400"] = abs(v["sd_hat_400"] - v["sd_theory_400"]) / v["sd_theory_400"] * 100

# ---------- （3）中心极限定理：取一个很不像正态的分布试试
#     每个零件的返工工时：八成是 0，两成在 0.5—3 小时之间（极偏的分布）
def rework_hours(size, g):
    hit = g.random(size) < 0.2
    return np.where(hit, g.uniform(0.5, 3.0, size), 0.0)


one = rework_hours(100000, g)
v["skew_mean"], v["skew_sd"] = float(one.mean()), float(one.std())
v["skew_zero_pct"] = float((one == 0).mean() * 100)
for n in (1, 5, 30, 200):
    m = rework_hours((8000, n), g).mean(axis=1)
    z = (m - v["skew_mean"]) / (v["skew_sd"] / np.sqrt(n))
    v[f"in95_{n}"] = float((np.abs(z) < 1.96).mean() * 100)   # 落在 ±1.96 内的比例（正态是 95%）
    v[f"skew_{n}"] = float(((z - z.mean()) ** 3).mean())      # 偏度：正态是 0，它按 1/√n 消失
    v[f"sd_mean_{n}"] = float(m.std(ddof=1))
assert v["skew_1"] > 1.5 and v["skew_200"] < 0.3, "偏度应当随 n 增大而趋于零"
assert abs(v["in95_200"] - 95) < 1.5, "n 大时与正态的 95% 对得上"
v["skew_drop"] = v["skew_1"] / v["skew_200"]                  # 与 √200 ≈ 14 同量级
v["sqrt200"] = float(np.sqrt(200))
v["sd_mean_theory_200"] = v["skew_sd"] / np.sqrt(200)
out(**v)
