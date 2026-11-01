"""算例 16.8.1—16.8.4：案例——车间缺陷样本不够用，拿合成图补（16.8 节）。

（1）先说清口径：七成的件是合格的，缺陷大多很轻微；检测器用最近邻（它吃数据，所以"补数据
     有没有用"问得出来）；成绩看两个数：曲线下面积，以及把误报压到 5% 时能查出多少缺陷。
（2）只有 60 张真实图能做到什么：与 960 张真实图比，差距有多大。
（3）补 900 张合成图：分布对得上时，几乎追平 960 张真实标注；
     分布偏了（底纹太干净、只合成偏重的缺陷、整类漏了）**比完全不用合成数据还差**。
（4）落点：合成数据补的是"样本量"，补不了"没见过的那一类"；而且补错了是要倒扣的。
"""
import numpy as np

from _ch16 import auc, dataset, knn_score, recall_at_fpr, KINDS, PK, SEV
from bookout import out

v = {}
N_TEST, N_REAL, N_SYN, SEEDS = 3000, 60, 900, 5
v["n_test"], v["n_real"], v["n_syn"], v["n_seeds"] = N_TEST, N_REAL, N_SYN, SEEDS
v["sev_lo"], v["sev_hi"] = SEV
v["p_ok"] = PK[0] * 100
v["kinds"] = list(KINDS)
v["n_defect_kinds"] = len(KINDS) - 1

Xte, yte, kte = dataset(N_TEST, seed=99)
v["test_defect_pct"] = float(yte.mean()) * 100

# 偏了的那一批有三处毛病，都是真实生成器会犯的：底纹的朝向与照明是固定的（生成器没学会
# 这部分变化）、只合成偏重的缺陷（0.25—0.35）、整类"压痕"根本没合成。
BIAS_SEV = (0.25, SEV[1])
BIAS_KINDS = (0, 1, 3)
v["bias_sev_lo"], v["bias_sev_hi"] = BIAS_SEV
v["bias_missing"] = KINDS[2]
Xs, ys, _ = dataset(N_SYN, seed=2)
Xb, yb, _ = dataset(N_SYN, seed=3, sev_range=BIAS_SEV, kinds=BIAS_KINDS, p=[0.7, 0.15, 0.15],
                    plain_bg=True)


def evaluate(X, y):
    s = knn_score(X, y, Xte)
    per = {}
    for k in (1, 2, 3):
        m = (kte == 0) | (kte == k)
        per[KINDS[k]] = round(recall_at_fpr(s[m], (kte[m] == k).astype(int)), 3)
    return auc(s, yte), recall_at_fpr(s, yte), per


def over_seeds(make):
    a, r, pers = [], [], []
    for s in range(SEEDS):
        Xr, yr, _ = dataset(N_REAL, seed=10 + s)
        X, y = make(Xr, yr)
        au, rc, per = evaluate(X, y)
        a.append(au)
        r.append(rc)
        pers.append(per)
    per_mean = {k: round(float(np.mean([p[k] for p in pers])), 3) for k in pers[0]}
    return (float(np.mean(a)), float(np.min(a)), float(np.max(a)), float(np.mean(r)), per_mean)


# ---------- （2）只有真实数据
real = over_seeds(lambda Xr, yr: (Xr, yr))
v["auc_real"], v["auc_real_lo"], v["auc_real_hi"], v["rec_real"], v["per_real"] = real
big = [evaluate(*dataset(N_REAL + N_SYN, seed=20 + s)[:2]) for s in range(3)]
v["auc_big"] = float(np.mean([b[0] for b in big]))
v["rec_big"] = float(np.mean([b[1] for b in big]))
v["n_big"] = N_REAL + N_SYN
assert v["auc_big"] > v["auc_real"] + 0.03, "样本量确实是瓶颈：全真 960 张比 60 张好一大截"
v["auc_gap"] = v["auc_big"] - v["auc_real"]
v["real_spread"] = v["auc_real_hi"] - v["auc_real_lo"]
assert v["real_spread"] > 0.02, "只有 60 张时，换一批真实图成绩就差很多——这也是少样本的毛病"

# ---------- （3）补合成图
match = over_seeds(lambda Xr, yr: (np.r_[Xr, Xs], np.r_[yr, ys]))
v["auc_match"], _, _, v["rec_match"], v["per_match"] = match
bias = over_seeds(lambda Xr, yr: (np.r_[Xr, Xb], np.r_[yr, yb]))
v["auc_bias"], _, _, v["rec_bias"], v["per_bias"] = bias

v["rows"] = [
    (f"只用 {N_REAL} 张真实图", round(v["auc_real"], 3), round(v["rec_real"] * 100, 1)),
    (f"{N_REAL} 张真实 + {N_SYN} 张合成（分布对得上）", round(v["auc_match"], 3),
     round(v["rec_match"] * 100, 1)),
    (f"{N_REAL} 张真实 + {N_SYN} 张合成（分布偏了）", round(v["auc_bias"], 3),
     round(v["rec_bias"] * 100, 1)),
    (f"{v['n_big']} 张全是真实图（参照）", round(v["auc_big"], 3), round(v["rec_big"] * 100, 1)),
]
v["auc_recovered_pct"] = (v["auc_match"] - v["auc_real"]) / (v["auc_big"] - v["auc_real"]) * 100
v["rec_gain_pt"] = (v["rec_match"] - v["rec_real"]) * 100
assert v["auc_match"] > v["auc_real"] + 0.04, "分布对得上的合成图确实有用"
assert v["auc_recovered_pct"] > 70, "它把'再标 900 张真实图'的收益补回了七成以上"
assert v["auc_bias"] < v["auc_real"], \
    "分布一偏，不只是收益没了——比完全不用合成数据还差。这是本节最该记住的一句"
v["bias_vs_real_pt"] = (v["auc_real"] - v["auc_bias"]) * 100
v["rec_bias_vs_real_pt"] = (v["rec_real"] - v["rec_bias"]) * 100

# ---------- （4）落点：偏差偏在哪一类上
v["per_rows"] = [(k, v["per_real"][k], v["per_match"][k], v["per_bias"][k]) for k in v["per_real"]]
for i, k in enumerate(KINDS[1:], start=1):
    v[f"miss_s{i}"], v[f"match_s{i}"], v[f"bias_s{i}"] = v["per_real"][k], v["per_match"][k], v["per_bias"][k]
miss = v["bias_missing"]
v["miss_real"], v["miss_match"], v["miss_bias"] = (v["per_real"][miss], v["per_match"][miss],
                                                   v["per_bias"][miss])
assert v["miss_bias"] < v["miss_match"], \
    f"没合成的那一类（{miss}）在偏差那一组上掉得最明显——合成数据补不了没见过的那一类"
v["miss_drop_pt"] = (v["miss_match"] - v["miss_bias"]) * 100

out(**v)
