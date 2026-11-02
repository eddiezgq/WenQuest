"""算例 18.5.1—18.5.4：虚拟筛选的富集与基率、分子性质预测的划分口径（18.5 节）。

（1）富集因子是什么、它和"命中率"是两回事。
（2）同一个打分函数，阳性比例一变，命中率就天差地别——**命中率不能横向比**。
（3）骨架划分与随机划分：同一个模型、同一批分子，两种划分给出的分数差多少。
（4）为什么"用验证集选模型"挡不住骨架外推的失败。
"""
import numpy as np

from _ch18 import (auc_score, enrichment, fit_logistic, hit_rate, knn_score,
                   library, molecules, predict, split_random, split_scaffold)
from bio_facts import MOLNET, SCREEN, SPLITS
from bookout import out

v = {}

# ---------- （1）富集因子
N_LIB = 200_000
v["n_lib"] = N_LIB
v["n_lib_w"] = N_LIB / 1e4
v["ef_formula"] = SCREEN["ef_formula"]
v["active_frac_pct"] = 0.1
score, act = library(N_LIB, v["active_frac_pct"] / 100, seed=0, auc=0.80)
v["n_active"] = int(act.sum())
v["auc_design"] = 0.80
v["auc_check"] = round(auc_score(act.astype(int), score), 3)
assert abs(v["auc_check"] - v["auc_design"]) < 0.02, "打分函数的分辨能力就是设定的那个 AUC"

v["ef_rows"] = []
for frac, tag in ((0.001, "0p1"), (0.01, "1"), (0.05, "5"), (0.10, "10")):
    e = enrichment(score, act, frac)
    v["ef_rows"].append((frac * 100, round(e, 2)))
    v[f"ef_{tag}"] = round(e, 2)
assert v["ef_0p1"] > v["ef_1"] > v["ef_5"] > v["ef_10"], \
    "富集因子一定是前面越少越高——所以不写'前百分之几'的富集因子没有意义"

# ---------- （2）同一个打分函数，阳性比例一变，命中率就变
v["hit_rows"] = []
for frac_pct, tag in ((0.01, "001"), (0.1, "01"), (1.0, "1")):
    s2, a2 = library(N_LIB, frac_pct / 100, seed=1, auc=0.80)
    h = hit_rate(s2, a2, 100)
    e = enrichment(s2, a2, 0.01)
    v["hit_rows"].append((frac_pct, round(h, 1), round(e, 2)))
    v[f"hit_{tag}"], v[f"efc_{tag}"] = round(h, 1), round(e, 2)
assert v["hit_001"] < v["hit_01"] < v["hit_1"], \
    "打分函数一点没变，命中率却差一个量级——变的只是库里本来有多少阳性"
assert abs(v["efc_001"] - v["efc_1"]) < 8, "而富集因子基本不随阳性比例变——这才是可比的那个量"
# 0.01% 那一档，打分最高的 100 个里一个阳性都没有——"命中率 0%"与"打分函数不行"是两件事
assert v["hit_001"] == 0.0, "阳性太稀时，同一个打分函数的命中率可以是 0"

# 公开论文里的三组命中率：分母差一个量级、判据各不相同，**不能并排**
v["ampc_tested"], v["ampc_hits"] = SCREEN["ampc_tested"], SCREEN["ampc_hits"]
v["d4_tested"], v["d4_hits"] = SCREEN["d4_tested"], SCREEN["d4_hits"]
v["mt1_tested"], v["mt1_hits"] = SCREEN["mt1_tested"], SCREEN["mt1_hits"]
v["ampc_pct"] = SCREEN["ampc_hits"] / SCREEN["ampc_tested"] * 100
v["d4_pct"] = SCREEN["d4_hits"] / SCREEN["d4_tested"] * 100
v["mt1_pct"] = SCREEN["mt1_hits"] / SCREEN["mt1_tested"] * 100
v["d4_selection"] = SCREEN["d4_selection"]
v["litpcba_stated"], v["litpcba_sum"] = SCREEN["litpcba_stated"], SCREEN["litpcba_sum"]
v["litpcba_baseline_ef1"] = SCREEN["litpcba_baseline_ef1"]
assert SCREEN["criteria_differ"], "三项研究的活性判据不同，不能并排"

# ---------- （3）两种划分：会记类似物的模型，与只会用真信号的模型
N_MOL, N_SCAF = 4000, 220
v["n_mol"], v["n_scaffold"] = N_MOL, N_SCAF
x, y, scaf = molecules(N_MOL, N_SCAF, seed=2)
v["pos_rate_pct"] = float(y.mean() * 100)

res = {}
for name, sp in (("random", lambda sd: split_random(N_MOL, seed=sd)),
                 ("scaffold", lambda sd: split_scaffold(scaf, seed=sd))):
    knn, lin = [], []
    for sd in range(12):
        tr, te = sp(sd)
        knn.append(auc_score(y[te], knn_score(x[tr], y[tr], x[te])))
        w = fit_logistic(x[tr], y[tr])
        lin.append(auc_score(y[te], predict(w, x[te])))
    res[name] = (float(np.mean(knn)), float(np.std(knn)),
                 float(np.mean(lin)), float(np.std(lin)))

v["knn_random"] = round(res["random"][0], 3)
v["knn_scaffold"] = round(res["scaffold"][0], 3)
v["knn_scaffold_sd"] = round(res["scaffold"][1], 3)
v["knn_random_sd"] = round(res["random"][1], 3)
v["lin_random"] = round(res["random"][2], 3)
v["lin_scaffold"] = round(res["scaffold"][2], 3)
v["knn_drop_pts"] = (v["knn_random"] - v["knn_scaffold"]) * 100
v["lin_drop_pts"] = (v["lin_random"] - v["lin_scaffold"]) * 100

assert v["knn_drop_pts"] > 15, "会记类似物的模型，换成骨架划分就塌"
assert v["lin_drop_pts"] < 5, "只会用真信号的模型几乎不受影响——掉多少取决于模型靠什么吃饭"
assert v["knn_random"] > v["lin_random"] and v["knn_scaffold"] < v["lin_scaffold"], \
    "两种划分把两个模型的名次排**反**了：随机划分选出来的'更好的模型'，骨架划分上更差"
assert v["knn_scaffold_sd"] > 2 * v["knn_random_sd"], \
    "骨架划分不是唯一确定的划分，换一组骨架分数就抖——这一条常被忽略"

# ---------- （4）验证集挡不住
tr, te = split_scaffold(scaf, seed=0)
cut = int(len(tr) * 0.8)
v["auc_train"] = round(auc_score(y[tr[:cut]], knn_score(x[tr[:cut]], y[tr[:cut]], x[tr[:cut]])), 3)
v["auc_valid"] = round(auc_score(y[tr[cut:]], knn_score(x[tr[:cut]], y[tr[:cut]], x[tr[cut:]])), 3)
v["auc_test"] = round(auc_score(y[te], knn_score(x[tr[:cut]], y[tr[:cut]], x[te])), 3)
v["valid_test_gap"] = (v["auc_valid"] - v["auc_test"]) * 100
assert v["auc_valid"] > v["auc_test"] + 0.1, \
    "验证集是从训练那堆骨架里切出来的，所以验证分下不来——它挡不住骨架外推的失败"

# 公开论文里能核到的那一组（口径见资料卡第 12 节）
v["bbbp_train"], v["bbbp_valid"], v["bbbp_test"] = (
    SPLITS["bbbp_train"], SPLITS["bbbp_valid"], SPLITS["bbbp_test"])
v["hiv_train"], v["hiv_valid"], v["hiv_test"] = (
    SPLITS["hiv_train"], SPLITS["hiv_valid"], SPLITS["hiv_test"])
v["bbbp_drop_pts"] = (SPLITS["bbbp_valid"] - SPLITS["bbbp_test"]) * 100
v["paired_known"] = SPLITS["paired_numbers"] is not None
assert not v["paired_known"], \
    "'换成骨架划分平均掉多少分'没有可核的成对数字——本书不印这个数"
v["molnet_bbbp"], v["molnet_bace"] = MOLNET["bbbp"], MOLNET["bace"]
v["molnet_note"] = MOLNET["table1_vs_text"]
v["scaffold_not_unique"] = SPLITS["not_unique"]

out(**v)
