"""算例 19.5.1—19.5.2：遥感的划分口径——按像素随机划分会高估（19.5 节）。

地表是成片的，所以**相邻像素几乎总是同一类**。按像素随机划分时，测试集里的每个像素在
训练集里几乎都有一个紧挨着的同类近邻——一个只会"找最像的像素"的模型就能考高分。
按区块划分把这条路切断，分数才说明问题。这与第 18.5 节的骨架划分是同一件事。
"""
import numpy as np

from _ch19 import (knn_classify, satellite_tile, split_blocks, split_pixels)
from bookout import out
from geo_facts import REMOTE

N, PATCH = 96, 8
v = {"n_side": N, "patch": PATCH, "n_pixels": N * N,
     "n_blocks": (N // PATCH) ** 2}

feat, cls, bid = satellite_tile(N, seed=0, patch=PATCH)
v["n_classes"] = int(len(np.unique(cls)))
v["chance"] = round(1 / v["n_classes"], 3)

# ---------- （1）两种划分
res = {}
for name, sp in (("pixel", lambda sd: split_pixels(len(cls), seed=sd)),
                 ("block", lambda sd: split_blocks(bid, seed=sd))):
    accs = []
    for sd in range(8):
        tr, te = sp(sd)
        pred = knn_classify(feat[tr], cls[tr], feat[te])
        accs.append(float((pred == cls[te]).mean()))
    res[name] = (float(np.mean(accs)), float(np.std(accs)))

v["acc_pixel"], v["sd_pixel"] = round(res["pixel"][0], 4), round(res["pixel"][1], 4)
v["acc_block"], v["sd_block"] = round(res["block"][0], 4), round(res["block"][1], 4)
v["gap_pts"] = (v["acc_pixel"] - v["acc_block"]) * 100
v["overestimate_pct"] = (v["acc_pixel"] / v["acc_block"] - 1) * 100

assert v["acc_pixel"] > v["acc_block"], "按像素随机划分系统性地偏高"
assert v["gap_pts"] > 5, "差距要足够大，才看得出这是口径问题而不是噪声"
assert v["sd_block"] > v["sd_pixel"], \
    "按区块划分的分数更抖——换哪几块进测试集，分数就变"

# ---------- （2）地物越成片，高估得越厉害
v["rows"] = []
for patch in (2, 4, 8, 16):
    f2, c2, b2 = satellite_tile(N, seed=1, patch=patch)
    tr, te = split_pixels(len(c2), seed=0)
    a_px = float((knn_classify(f2[tr], c2[tr], f2[te]) == c2[te]).mean())
    tr, te = split_blocks(b2, seed=0)
    a_bk = float((knn_classify(f2[tr], c2[tr], f2[te]) == c2[te]).mean())
    v["rows"].append((patch, round(a_px, 3), round(a_bk, 3), round((a_px - a_bk) * 100, 1)))
    v[f"px_p{patch}"], v[f"bk_p{patch}"] = round(a_px, 3), round(a_bk, 3)
v["gap_p2"] = (v["px_p2"] - v["bk_p2"]) * 100
v["gap_p16"] = (v["px_p16"] - v["bk_p16"]) * 100
assert v["gap_p16"] > v["gap_p2"], \
    "地物越成片，随机像素划分高估得越厉害——这正是真实地表的情形"

# ---------- 口径：这件事该引谁
v["bigearthnet_claim"] = REMOTE["bigearthnet_leakage_claim"]
assert not v["bigearthnet_claim"], \
    "不要把'随机像素划分会泄漏'安在那个数据集头上——它从未用过 leakage 一词"
v["overestimate_published"] = REMOTE["kattenborn_overestimate_pct"]
v["underestimate_low"], v["underestimate_high"] = REMOTE["stock_underestimate_pct"]
v["wrong_model_pct"] = REMOTE["stock_wrong_model_pct"]

out(**v)
