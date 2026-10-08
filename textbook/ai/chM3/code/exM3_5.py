"""算例 M3.5.1—M3.5.3：KL 散度与交叉熵（M3.5 节）。

交叉熵 = 熵 + KL 散度。这个分解在本书里出现三次：
训练时最小化交叉熵等价于最小化 KL（熵与模型无关）；语言模型的困惑度是交叉熵的指数（M4.2 节）；
对齐时用 KL 把新策略拴在参考策略附近（13.5 节）。本程序把三件事都算出来，并验证 KL 不对称。
"""
import numpy as np

from bookout import out

v = {}
# ---------- （1）分解：交叉熵 = 熵 + KL
p = np.array([0.55, 0.30, 0.15])                               # 真实的三类缺陷比例（第 11 章）
q = np.array([0.40, 0.35, 0.25])                               # 模型给出的
H = float(-(p * np.log(p)).sum())
CE = float(-(p * np.log(q)).sum())
KL = float((p * np.log(p / q)).sum())
v["p"], v["q"] = [round(float(a), 2) for a in p], [round(float(a), 2) for a in q]
v["H"], v["CE"], v["KL"] = H, CE, KL
assert abs(CE - (H + KL)) < 1e-12, "交叉熵 = 熵 + KL"
v["H_bits"] = H / np.log(2)                                    # 换成比特
v["CE_bits"] = CE / np.log(2)

# ---------- （2）KL 不对称
KL_rev = float((q * np.log(q / p)).sum())
v["KL_rev"] = KL_rev
v["asym_ratio"] = KL_rev / KL
assert abs(KL - KL_rev) > 1e-3, "KL 不对称：方向换了，数就变了"
# 零概率的代价：模型给某一类 0，正向 KL 会变成无穷
q0 = np.array([0.6, 0.4, 0.0])
with np.errstate(divide="ignore"):
    v["KL_zero"] = float((p * np.log(p / q0)).sum())
v["KL_zero_inf"] = bool(np.isinf(v["KL_zero"]))
assert v["KL_zero_inf"], "真实有、模型给 0，正向 KL 是无穷——所以要平滑"
eps = 1e-3
q_s = np.array([0.6 - eps / 2, 0.4 - eps / 2, eps])
v["eps"] = eps
v["KL_smooth"] = float((p * np.log(p / q_s)).sum())

# ---------- （3）最小化交叉熵 = 最小化 KL：扫一遍模型参数看两条曲线差一个常数
ts = np.linspace(0.05, 0.9, 20000)
ce_curve, kl_curve = [], []
for t in ts:                                                   # 一族模型：第一类的概率为 t，其余按比例分
    qq = np.array([t, (1 - t) * 0.667, (1 - t) * 0.333])
    ce_curve.append(float(-(p * np.log(qq)).sum()))
    kl_curve.append(float((p * np.log(p / qq)).sum()))
ce_curve, kl_curve = np.array(ce_curve), np.array(kl_curve)
v["t_ce"] = float(ts[int(ce_curve.argmin())])
v["t_kl"] = float(ts[int(kl_curve.argmin())])
assert v["t_ce"] == v["t_kl"], "两者的最小值点必定相同"
v["diff_const"] = float(np.abs((ce_curve - kl_curve) - H).max())
assert v["diff_const"] < 1e-12, "两条曲线相差的正是熵（与模型无关）"
v["ce_min"], v["kl_min"] = float(ce_curve.min()), float(kl_curve.min())
v["p1"] = float(p[0])
out(**v)
