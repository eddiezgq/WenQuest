"""算例 14.1.1—14.1.4：把图和文放进同一个空间（14.1 节）。

（1）对齐之前与之后：两端的特征本来各说各话，学两个投影之后，配对的靠在一起、不配对的分开。
（2）批大小：一个批里有多少负样本，就是这一步能比较多少"不是它"。批大到一定程度就够用了——
    这一条用本章的合成数据量出来，并与 CLIP（32768）、SigLIP（"32k 已够用"）的公开数字对照。
（3）InfoNCE 能提供的信息有上限：$\\ln B$。这是一条定理，不是经验——批里只有 B 个候选，
    一次比较最多只能说清 $\\log_2 B$ 比特。
（4）温度：它决定梯度有多少压在"最像的那个负样本"上。
"""
import numpy as np

from _ch14 import chance_recall, infonce, l2, labels_of, pairs, recall_at_k, train
from bookout import out
from mm_facts import ALIGN, CLIP, SIGLIP

v = {}
NOISE = 0.8
xi, xt, a = pairs(6000, 0, noise=NOISE)                  # 训练用的图文对
xi_t, xt_t, a_t = pairs(1500, 9, noise=NOISE)            # 另一批，评测用
lab = labels_of(a_t)
v["n_train"], v["n_test"] = len(xi), len(xi_t)
v["n_classes"] = int(len(set(labels_of(a))))             # 这批数据里出现了多少种说法
v["img_dim"], v["txt_dim"] = xi.shape[1], xt.shape[1]

# ---------- （1）对齐之前与之后
zi0, zt0 = l2(xi_t[:, :16]), l2(xt_t @ np.eye(xt_t.shape[1], 16))   # 没学过的"同一个空间"：直接截断
v["r1_before"] = recall_at_k(zi0, zt0, lab, lab)[1]
Wi, Wt, hist = train(xi, xt, dim=16, batch=256, steps=1800, temp=0.07, lr=0.9)
zi, zt = l2(xi_t @ Wi), l2(xt_t @ Wt)
r = recall_at_k(zi, zt, lab, lab)
v["r1"], v["r5"], v["r10"] = r[1], r[5], r[10]
v["loss0"], v["loss1"] = float(hist[0]), float(hist[-1])
ch = chance_recall(lab, lab)
v["r1_chance"], v["r10_chance"] = ch[1], ch[10]
assert v["r1"] > 40 * v["r1_chance"], "对齐之后的命中率要远高于瞎猜"
# 配对的与不配对的，余弦相似度各是多少
s = zi @ zt.T
same = lab[:, None] == lab[None, :]
v["cos_pair"] = float(s[same].mean())
v["cos_other"] = float(s[~same].mean())
v["cos_gap"] = v["cos_pair"] - v["cos_other"]
assert v["cos_pair"] > v["cos_other"]

# ---------- （2）批大小：一步能比较多少"不是它"
SEEN = len(xi) * 20                                      # 各档看过的样本数一样（公平比较）
rows = []
for B in (8, 32, 128, 512):
    Wi_b, Wt_b, h_b = train(xi, xt, dim=16, batch=B, steps=SEEN // B, temp=0.07, lr=0.5 * (B / 64) ** 0.5)
    rb = recall_at_k(l2(xi_t @ Wi_b), l2(xt_t @ Wt_b), lab, lab)
    rows.append((B, B - 1, SEEN // B, round(rb[1], 1)))
v["batch_rows"] = rows
v["r1_b8"], v["r1_b512"] = rows[0][3], rows[-1][3]
v["batch_gain"] = v["r1_b512"] - v["r1_b8"]
assert v["r1_b512"] > v["r1_b8"], "同样看过的样本数下，批越大命中率越高"
# 一个批里"难"的负样本有多少：同零件或同缺陷的
lab_tr = labels_of(a)
g = np.random.default_rng(5)
hard = []
for B in (8, 32, 128, 512, 2048):
    idx = g.choice(len(a), B, replace=False)
    same_part = (a[idx, 0][:, None] == a[idx, 0][None, :]) | (a[idx, 1][:, None] == a[idx, 1][None, :])
    np.fill_diagonal(same_part, False)
    hard.append((B, float(same_part.sum(1).mean())))
v["hard_rows"] = [(b, round(h, 1)) for b, h in hard]
v["hard_8"], v["hard_2048"] = hard[0][1], hard[-1][1]

# ---------- （3）InfoNCE 的信息上限：ln B
v["cap_rows"] = [(B, round(float(np.log(B)), 2), round(float(np.log2(B)), 1)) for B in (8, 256, 4096, CLIP["batch"])]
v["clip_batch"] = CLIP["batch"]
v["clip_cap_nats"] = float(np.log(CLIP["batch"]))
v["clip_cap_bits"] = float(np.log2(CLIP["batch"]))
v["align_batch"] = ALIGN["batch"]
v["siglip_enough"] = SIGLIP["batch_enough"]
v["siglip_softmax_peak"] = SIGLIP["softmax_peak_batch"]
v["siglip_below"] = SIGLIP["sigmoid_wins_below"]
# 什么都没学会时（所有得分都一样），InfoNCE 的损失正好是 ln B：B 个候选里只能瞎猜
B0 = 256
flat = np.tile(l2(np.random.default_rng(3).normal(0, 1, (1, 16))), (B0, 1))   # 所有嵌入相同 → 得分全相等
v["loss_flat"] = float(infonce(flat, flat, 0.07)[0])
v["ln_B0"] = float(np.log(B0))
assert abs(v["loss_flat"] - v["ln_B0"]) < 1e-9, "得分全相等时，InfoNCE 的损失就是 ln B"

# ---------- （4）温度：梯度压在最像的那个负样本上有多少
rows_t = []
for temp in (0.01, 0.07, 0.3, 1.0):
    ss = (zi[:200] @ zt[:200].T) / temp
    p = np.exp(ss - ss.max(1, keepdims=True))
    p /= p.sum(1, keepdims=True)
    np.fill_diagonal(p, 0.0)                             # 只看负样本之间怎么分配
    p = p / np.maximum(p.sum(1, keepdims=True), 1e-12)
    top = np.sort(p, axis=1)[:, -1].mean()               # 最像的那个负样本占多少权重
    eff = float(np.exp(-(p * np.log(np.maximum(p, 1e-12))).sum(1)).mean())   # 等效上有几个负样本在起作用
    rows_t.append((temp, round(float(top) * 100, 1), round(eff, 1)))
v["temp_rows"] = rows_t
v["top_lo"], v["top_hi"] = rows_t[0][1], rows_t[-1][1]
v["eff_lo"], v["eff_hi"] = rows_t[0][2], rows_t[-1][2]
assert v["top_lo"] > v["top_hi"] and v["eff_lo"] < v["eff_hi"], "温度越低，梯度越集中在最像的负样本上"
v["clip_temp_init"] = CLIP["temp_init"]
v["clip_cap"] = CLIP["logit_scale_cap"]
v["clip_pairs_yi"] = CLIP["pairs"] / 1e8                 # 亿
v["clip_zs"] = CLIP["in1k_zeroshot_top1"]
v["align_pairs_yi"] = ALIGN["pairs"] / 1e8
v["align_zs"] = ALIGN["in1k_zeroshot_top1"]
out(**v)
