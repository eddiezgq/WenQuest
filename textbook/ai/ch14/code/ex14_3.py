"""算例 14.3.1—14.3.3：跨模态检索的命中率，以及它最容易被误读的地方（14.3 节）。

（1）同一个模型，检索池从一百条加到两万条，命中率怎样掉——"R@1 有多少"这句话离开池子大小没有意义。
（2）三种用法：以文搜图、以图搜文、以图搜图（照着一张缺陷照片找同类历史记录），各自的命中率。
（3）公开数字的口径：MSCOCO 的 5K 与 1K 是两套测试集，零样本与微调也不是一回事——
    同一个模型 ALIGN 的 COCO 图→文 R@1 在两种口径下差十几个点。
"""
import numpy as np

from _ch14 import chance_recall, l2, labels_of, pairs, recall_at_k, train
from bookout import out
from mm_facts import RETRIEVAL

v = {}
NOISE = 0.8
xi, xt, a = pairs(6000, 0, noise=NOISE)
Wi, Wt, _ = train(xi, xt, dim=16, batch=256, steps=1800, temp=0.07, lr=0.9)

# ---------- （1）检索池越大越难
rows = []
for n in (100, 500, 2000, 8000, 20000):
    xi_p, xt_p, a_p = pairs(n, 21, noise=NOISE)
    lab = labels_of(a_p)
    zi, zt = l2(xi_p @ Wi), l2(xt_p @ Wt)
    r = recall_at_k(zt, zi, lab, lab)                 # 以文搜图：查询是句子，池子是图
    c = chance_recall(lab, lab)
    rows.append((n, round(r[1], 1), round(r[10], 1), round(c[1], 2)))
v["pool_rows"] = rows
v["r1_100"], v["r1_20000"] = rows[0][1], rows[-1][1]
v["r1_drop"] = v["r1_100"] - v["r1_20000"]
v["chance_100"], v["chance_20000"] = rows[0][3], rows[-1][3]
assert v["r1_100"] > v["r1_20000"], "池子越大，R@1 越低——同一个模型"
# 瞎猜的基线掉得更快：模型相对瞎猜的倍数反而是涨的
v["over_chance_100"] = v["r1_100"] / v["chance_100"]
v["over_chance_20000"] = v["r1_20000"] / v["chance_20000"]
assert v["over_chance_20000"] > v["over_chance_100"]

# ---------- （2）三种用法
xi_q, xt_q, a_q = pairs(2000, 33, noise=NOISE)
lab = labels_of(a_q)
zi, zt = l2(xi_q @ Wi), l2(xt_q @ Wt)
t2i = recall_at_k(zt, zi, lab, lab)
i2t = recall_at_k(zi, zt, lab, lab)
i2i = recall_at_k(zi, zi, lab, lab, drop_self=True)   # 以图搜图：同一个空间里直接比（不算查询自己）
v["t2i_1"], v["t2i_10"] = t2i[1], t2i[10]
v["i2t_1"], v["i2t_10"] = i2t[1], i2t[10]
v["i2i_1"], v["i2i_10"] = i2i[1], i2i[10]
v["pool_q"] = len(zi)
# 以图搜图不需要文字那一端，但它借的正是对齐学出来的空间：没有对齐之前，原始特征也能搜，
# 只是搜到的是"像素像"的，不是"说的是同一件事"的
raw = recall_at_k(l2(xi_q), l2(xi_q), lab, lab, drop_self=True)
v["i2i_raw_1"] = raw[1]
# 以图搜图有个天花板：池子里得真有同类。2000 张图分散在两千多种说法里，不少图根本没有同伴
cnt = np.bincount(lab)
v["i2i_ceiling"] = float((cnt[lab] > 1).mean() * 100)
v["i2i_of_ceiling"] = v["i2i_1"] / v["i2i_ceiling"] * 100
v["i2i_gain"] = v["i2i_1"] - v["i2i_raw_1"]
assert v["i2i_1"] >= v["i2i_raw_1"], "对齐之后的空间，以图搜图不比原始特征差"

# ---------- （3）公开数字的口径
v["align_coco5k_zs_r1"] = RETRIEVAL["align_coco5k_zs_i2t"][0]
v["align_coco5k_ft_r1"] = RETRIEVAL["align_coco5k_ft_i2t"][0]
v["align_gap"] = v["align_coco5k_ft_r1"] - v["align_coco5k_zs_r1"]
v["align_flickr_zs_r1"] = RETRIEVAL["align_flickr_zs_i2t"][0]
v["clip_flickr_zs_r1"] = RETRIEVAL["clip_flickr_zs_i2t"][0]
v["blip2_flickr_zs_r1"] = RETRIEVAL["blip2g_flickr_zs_i2t"][0]
v["flickr_minus_coco"] = v["align_flickr_zs_r1"] - v["align_coco5k_zs_r1"]
assert v["align_gap"] > 10, "同一个模型、同一套测试集，零样本与微调差十几个点"
out(**v)
