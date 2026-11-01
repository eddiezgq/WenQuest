"""算例 17.4.1—17.4.3：多智能体值不值（17.4 节）。

同样的预算（一共调 N 次模型），两种花法：
  甲 自洽多采样：独立采 N 次，投票；
  乙 提议—复核：一个角色提议、一个角色复核，一轮两次调用。
（1）多数情况下，同等预算投票更划算，而且 N 越大差距越大。
（2）但有一个条件：错误要够分散。错法一少，投票立刻失效，而复核还管用。
（3）复核者本身会误判；误判率一高，多一个角色就是多烧钱。
"""
import numpy as np

from _ch17 import propose_review, self_consistency, with_verifier
from bookout import out

v = {}
TRIALS = 20000

# ---------- （1）同等预算的对照
v["rows"] = []
for p in (0.40, 0.55, 0.70):
    for n in (4, 8, 16):
        sc = self_consistency(p, n, n_wrong=4, trials=TRIALS)
        pr = propose_review(p, n, tpr=0.8, fpr=0.1)
        v["rows"].append((p, n, round(sc, 3), round(pr, 3)))
        v[f"sc_p{int(p * 100)}_n{n}"] = round(sc, 3)
        v[f"pr_p{int(p * 100)}_n{n}"] = round(pr, 3)
v["n_wrong_default"] = 4
v["tpr"], v["fpr"] = 0.8, 0.1
assert v["sc_p55_n16"] > v["pr_p55_n16"] + 0.1, \
    "错法够分散时，同等预算下投票更划算，而且预算越大差距越大"
v["gap_n4"] = (v["sc_p55_n4"] - v["pr_p55_n4"]) * 100
v["gap_n16"] = (v["sc_p55_n16"] - v["pr_p55_n16"]) * 100
assert v["gap_n16"] > v["gap_n4"], "差距随预算拉开"
# 两种办法相对"只调一次"各赚了多少
v["single_55"] = 0.55
v["sc_gain_pts"] = (v["sc_p55_n8"] - 0.55) * 100
v["pr_gain_pts"] = (v["pr_p55_n8"] - 0.55) * 100

# ---------- （2）错法一少，投票就不灵了
P_HARD = 0.35
v["p_hard"] = P_HARD
v["wrong_rows"] = []
for nw in (1, 2, 4, 8):
    sc = self_consistency(P_HARD, 8, n_wrong=nw, trials=TRIALS)
    v["wrong_rows"].append((nw, round(sc, 3)))
    v[f"sc_wrong{nw}"] = round(sc, 3)
v["pr_same"] = round(propose_review(P_HARD, 8, tpr=0.8, fpr=0.1), 3)
assert v["sc_wrong1"] < P_HARD, \
    "只有一种错法时，投票选出来的就是那个错答案——**比只调一次还差**"
assert v["sc_wrong1"] < v["pr_same"], \
    "这正是复核派得上用场的场合：它不靠'错得各不相同'，靠'错了看得出来'"
v["vote_collapse_pts"] = (v["sc_wrong8"] - v["sc_wrong1"]) * 100

# ---------- （3）复核者的误判
v["review_rows"] = []
for tpr, fpr in ((0.9, 0.02), (0.9, 0.10), (0.9, 0.30), (0.5, 0.02)):
    val = with_verifier(1 - 0.55, 1, tpr, fpr, tries=4)
    v["review_rows"].append((tpr, fpr, round(val, 3)))
    v[f"rev_{int(tpr * 100)}_{int(fpr * 100)}"] = round(val, 3)
assert v["rev_90_30"] < v["rev_90_2"], "误判率一高，好结果就被扔掉了"
v["fpr_cost_pts"] = (v["rev_90_2"] - v["rev_90_30"]) * 100
assert v["rev_50_2"] < v["rev_90_2"], "查错能力不够，复核也白搭"
# 一句能带走的话：复核值不值，取决于 tpr − fpr 这个差
v["useful_margin"] = 0.9 - 0.30

out(**v)
