"""算例 18.2.1—18.2.4：接触信息值多少、它从哪里来、浅比对为什么救不回来（18.2 节）。

（1）二维格点上把折叠问题全枚举一遍：搜索空间有多大、基态有几条。
（2）给 k 条**正确**的接触，搜索空间缩到多小——这是"共进化信息值多少"的直接度量。
（3）k 条里混进**一条错的**，会怎样。
（4）接触从哪里来：比对深度与接触命中率的关系；以及"相关不等于接触"。
"""
import numpy as np

from _ch18 import (coevolution_scores, contact_precision, contacts,
                   enumerate_folds, fold_energy, indirect_demo,
                   information_curve, one_wrong_contact, simulate_msa)
from bio_facts import LIMITS, PLDDT
from bookout import out

SEQ = "HPHPHPHHHPHPPHPH"          # 16 个残基，H 疏水、P 亲水
N = len(SEQ)
v = {"seq": SEQ, "n_res": N}

# ---------- （1）全枚举
folds = enumerate_folds(N)
energies = np.fromiter((fold_energy(f, SEQ) for f in folds), int, len(folds))
fold_contacts = [contacts(f) for f in folds]
v["n_folds"] = len(folds)
v["n_folds_w"] = len(folds) / 1e4
v["e_native"] = int(energies.min())
v["degeneracy"] = int((energies == energies.min()).sum())
native = fold_contacts[int(np.argmin(energies))]
v["n_native_contacts"] = len(native)
v["native_frac"] = v["degeneracy"] / v["n_folds"] * 100
assert v["degeneracy"] <= 2, "这条序列的基态几乎是唯一的——适合当教学例子"
assert v["n_folds"] > 1e6, "16 个残基就有一百多万种折法：穷举真蛋白是没指望的"

# ---------- （2）k 条正确的接触值多少
KS = (0, 1, 2, 3, 4, 5, 6)
rows = information_curve(fold_contacts, energies, native, KS, seed=0)
v["info_rows"] = [(k, round(left, 1), round(best, 2), round(frac, 3)) for k, left, best, frac in rows]
for k, left, best, frac in rows:
    v[f"left_k{k}"] = round(left, 1)
    v[f"natfrac_k{k}"] = round(frac, 3)
v["shrink_per_contact"] = (v["left_k0"] / v["left_k6"]) ** (1 / 6)      # 折算：平均每条缩多少倍
assert v["left_k6"] < 10, "六条接触就把一百多万种折法缩到个位数"
assert v["natfrac_k6"] > 50, "剩下的里面一多半已经是基态"
assert v["shrink_per_contact"] > 5, "平均每条正确接触把搜索空间缩掉一个量级左右"

# ---------- （3）混进一条错的
v["k_wrong"] = 4
left_bad, ok_pct = one_wrong_contact(fold_contacts, energies, native, N, v["k_wrong"], seed=1)
v["left_wrong"] = round(left_bad, 1)
v["ok_wrong_pct"] = round(ok_pct, 1)
v["left_right"] = v["left_k4"]
assert v["ok_wrong_pct"] < 5, \
    "四条里错一条，基态直接被排除在外——接触信息又强又脆，这是本节最该记住的一条"

# ---------- （4）接触从哪里来
NAT_PAIRS = sorted(native)
DEPTHS = (10, 30, 100, 300, 1000)
v["depth_rows"] = []
for depth in DEPTHS:
    ps = [contact_precision(coevolution_scores(simulate_msa(N, NAT_PAIRS, depth, seed=sd,
                                                            coupling=0.9)),
                            NAT_PAIRS, top=len(NAT_PAIRS)) for sd in range(10)]
    p = float(np.mean(ps))
    v["depth_rows"].append((depth, round(p, 3)))
    v[f"prec_d{depth}"] = round(p, 3)
v["msa_depth_cut"] = LIMITS["msa_depth_cut"]
assert v["prec_d10"] < 0.5 < v["prec_d300"], "比对太浅时，接触基本是猜的"
assert v["prec_d1000"] >= v["prec_d300"], "深了才稳得住"
v["prec_gain_30_300"] = (v["prec_d300"] - v["prec_d30"]) * 100

# "相关不等于接触"
mi01, mi12, mi02 = indirect_demo(4000, seed=3)
v["mi_01"], v["mi_12"], v["mi_02"] = round(mi01, 3), round(mi12, 3), round(mi02, 3)
v["mi_ratio"] = round(mi02 / max(mi01, mi12), 2)
assert v["mi_02"] > 0.05, "0 与 2 并不接触，却照样有可观的互信息——相关不等于接触"
assert v["mi_02"] < min(v["mi_01"], v["mi_12"]), "间接的那一条比直接的弱，但不是零"

# ---------- 置信度是怎么训出来的（为 18.7 节埋线）
v["plddt_trained"] = PLDDT["trained_against"]
v["plddt_fit_r"] = PLDDT["fit_r"]
v["plddt_fit_slope"], v["plddt_fit_intercept"] = PLDDT["fit_slope"], PLDDT["fit_intercept"]

out(**v)
