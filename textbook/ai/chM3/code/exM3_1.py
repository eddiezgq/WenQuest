"""算例 M3.1.1—M3.1.3：条件概率与贝叶斯公式——检出了就一定是坏件吗（M3.1 节）。

检验工位的参数：不合格率 2%，检出率（坏件被判坏）90%，误报率（好件被判坏）3%。
直觉上"检出率 90% 很高"，但判为坏件的那些零件里，真坏的还不到四成——因为好件的基数太大。
这件事在医学筛查、缺陷检测、垃圾邮件、风控里一再出现，是本节要算清的第一笔账。
"""
import numpy as np

from _chM3 import P_BAD, SENS, SPEC, bayes, inspect
from bookout import out

v = {"p_bad": P_BAD, "sens": SENS, "spec": SPEC, "fpr": 1 - SPEC}
# ---------- （1）贝叶斯：判坏之后，真坏的概率
v["post"] = bayes()
v["post_pct"] = v["post"] * 100
v["odds_prior"] = P_BAD / (1 - P_BAD)
v["lr"] = SENS / (1 - SPEC)                                   # 似然比：一次"判坏"把几率放大多少倍
v["odds_post"] = v["odds_prior"] * v["lr"]
assert abs(v["odds_post"] / (1 + v["odds_post"]) - v["post"]) < 1e-12, "几率形式与概率形式必须一致"

# 一万个零件的四格表（用大数核对公式）
N = 10000
bad, flag = inspect(N)
tp = int(((bad == 1) & (flag == 1)).sum())
fp = int(((bad == 0) & (flag == 1)).sum())
fn = int(((bad == 1) & (flag == 0)).sum())
tn = int(((bad == 0) & (flag == 0)).sum())
v["N"], v["tp"], v["fp"], v["fn"], v["tn"] = N, tp, fp, fn, tn
v["flagged"] = tp + fp
v["post_emp"] = tp / max(tp + fp, 1)
v["post_emp_pct"] = v["post_emp"] * 100
assert abs(v["post_emp"] - v["post"]) < 0.05, "一万个样本上的实测与公式应当接近"

# ---------- （2）复检：同一个零件再测一次（两次结果条件独立）
v["post2"] = SENS ** 2 * P_BAD / (SENS ** 2 * P_BAD + (1 - SPEC) ** 2 * (1 - P_BAD))
v["post2_pct"] = v["post2"] * 100
v["post3"] = SENS ** 3 * P_BAD / (SENS ** 3 * P_BAD + (1 - SPEC) ** 3 * (1 - P_BAD))
v["post3_pct"] = v["post3"] * 100

# ---------- （3）不合格率变了，结论跟着变
for p in (0.002, 0.02, 0.2):
    key = str(p).replace(".", "")
    v[f"post_at_{key}"] = bayes(p_bad=p) * 100
v["post_at_low"], v["post_at_mid"], v["post_at_high"] = v["post_at_0002"], v["post_at_002"], v["post_at_02"]
# 要让后验过半，不合格率至少要多大
ps = np.linspace(1e-4, 0.5, 50000)
v["p_half"] = float(ps[np.argmax(np.array([bayes(p_bad=p) for p in ps]) >= 0.5)])
v["p_half_pct"] = v["p_half"] * 100
out(**v)
