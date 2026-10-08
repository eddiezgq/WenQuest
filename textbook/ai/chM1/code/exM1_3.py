"""算例 M1.3.1—M1.3.3：范数、距离与为什么要先归一化（M1.3 节）。

（1）同一个向量，三种常用范数给出三个数，各自强调什么不同。
（2）在原始数据上找"最像的那个零件"，结果几乎只由圆度决定——不是因为圆度更重要，而是因为它按微米记，
    数值的波动比按毫米记的几项大得多。换个单位，答案就变了。按列标准化以后，找出来的是另一个零件。
（3）余弦相似度只看方向、不看长短，所以它对"整体放大"不敏感——这正是它在检索与说话人识别里的用处。
"""
import numpy as np

from _chM1 import FEATURES, parts, standardize
from bookout import out

v = {}
X = parts()
# ---------- （1）三种范数
a = X[0] - X[1]                                               # 两个零件的差
v["l1"] = float(np.abs(a).sum())
v["l2"] = float(np.sqrt((a ** 2).sum()))
v["linf"] = float(np.abs(a).max())
v["i_inf"] = FEATURES[int(np.abs(a).argmax())]                # 无穷范数由哪一项决定
assert v["linf"] <= v["l2"] <= v["l1"], "三种范数的大小关系"
v["ratio_1_2"] = v["l1"] / v["l2"]

# ---------- （2）最近邻：归一化前后换了人
q = 0                                                          # 以第 1 个零件为查询
d_raw = np.sqrt(((X - X[q]) ** 2).sum(1))
d_raw[q] = np.inf
Z, mu, sd = standardize(X)
d_std = np.sqrt(((Z - Z[q]) ** 2).sum(1))
d_std[q] = np.inf
i_raw, i_std = int(d_raw.argmin()), int(d_std.argmin())
v["i_raw"], v["i_std"] = i_raw + 1, i_std + 1
v["same"] = i_raw == i_std
# 原始距离里，各项贡献了多少（平方和的占比）
share = (X - X[q]) ** 2
share = share.sum(0) / share.sum() * 100
for name, p in zip(("od", "id", "len", "round", "ra"), share):
    v[f"share_{name}"] = float(p)
v["share_top"] = FEATURES[int(share.argmax())]
share_z = (Z - Z[q]) ** 2
share_z = share_z.sum(0) / share_z.sum() * 100
v["share_len_std"] = float(share_z[2])
v["sd_len"], v["sd_ra"] = float(sd[2]), float(sd[4])
v["sd_ratio"] = float(sd[2] / sd[4])

# ---------- （3）余弦只看方向
u = Z[q]
w = Z[i_std]
cos = float(u @ w / (np.linalg.norm(u) * np.linalg.norm(w)))
v["cos"] = cos
v["cos_scaled"] = float(u @ (3.7 * w) / (np.linalg.norm(u) * np.linalg.norm(3.7 * w)))
assert abs(v["cos"] - v["cos_scaled"]) < 1e-12, "余弦对整体放大不变"
v["l2_scaled_ratio"] = float(np.linalg.norm(u - 3.7 * w) / np.linalg.norm(u - w))
out(**v)
