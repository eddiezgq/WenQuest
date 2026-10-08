"""算例 M4.3.1—M4.3.2：互信息（M4.3 节）。

互信息回答："知道了甲，对乙的不确定性减少了多少？"它在特征选择、检验工位的诊断里都用得上。
本程序在车间抽检的数据上算：检验结果与真实状态之间的互信息有多少、一次检验"值"多少比特，
以及一个要当心的事——互信息为零只说明"线性与非线性都无关"，但它对噪声很敏感，小样本上会被高估。
"""
import numpy as np

from bookout import out

v = {}
LOG2 = np.log(2)
P_BAD, SENS, SPEC = 0.02, 0.90, 0.97                        # 与 M3 章同一台检验机


def ent(p):
    p = np.asarray(p, dtype=float)
    p = p[p > 1e-15]
    return float(-(p * np.log2(p)).sum())


# ---------- （1）联合分布（真实状态 × 检验结果）
joint = np.array([[P_BAD * SENS, P_BAD * (1 - SENS)],       # 坏件：判坏、判好
                  [(1 - P_BAD) * (1 - SPEC), (1 - P_BAD) * SPEC]])
px = joint.sum(axis=1)                                      # 真实状态的边缘分布
py = joint.sum(axis=0)                                      # 检验结果的边缘分布
v["H_state"] = ent(px)                                      # 不做检验时的不确定性
v["H_flag"] = ent(py)
v["H_joint"] = ent(joint.ravel())
v["MI"] = v["H_state"] + v["H_flag"] - v["H_joint"]          # 互信息 = H(X) + H(Y) − H(X,Y)
v["H_given"] = v["H_state"] - v["MI"]                        # 做完检验还剩多少不确定性
v["cut_pct"] = v["MI"] / v["H_state"] * 100
assert v["MI"] >= 0 and v["H_given"] >= 0

# ---------- （2）检验机变好，互信息怎样涨
for sens, spec_, tag in ((0.90, 0.97, "base"), (0.99, 0.97, "sens"), (0.90, 0.999, "spec")):
    j = np.array([[P_BAD * sens, P_BAD * (1 - sens)],
                  [(1 - P_BAD) * (1 - spec_), (1 - P_BAD) * spec_]])
    mi = ent(j.sum(axis=1)) + ent(j.sum(axis=0)) - ent(j.ravel())
    v[f"MI_{tag}"] = mi
v["gain_sens"] = v["MI_sens"] - v["MI_base"]
v["gain_spec"] = v["MI_spec"] - v["MI_base"]
assert v["gain_spec"] > v["gain_sens"], "降误报率带来的信息，比提检出率多（与 M3.1 节的结论一致）"

# ---------- （3）互信息的估计会被高估：两列毫不相干的随机数
g = np.random.default_rng(42)
def mi_hat(x, y, bins=8):
    """直方图法估计互信息（最常见、也最容易被高估的做法）。"""
    c, _, _ = np.histogram2d(x, y, bins=bins)
    pj = c / c.sum()
    return ent(pj.sum(axis=1)) + ent(pj.sum(axis=0)) - ent(pj.ravel())


for n in (50, 200, 2000, 20000):
    vals = [mi_hat(g.normal(size=n), g.normal(size=n)) for _ in range(200)]
    v[f"mi_noise_{n}"] = float(np.mean(vals))
assert v["mi_noise_50"] > 5 * v["mi_noise_20000"], "样本越少，互信息被高估得越厉害"
v["bins"] = 8
v["mi_bias_ratio"] = v["mi_noise_50"] / v["mi_noise_20000"]
out(**v)
