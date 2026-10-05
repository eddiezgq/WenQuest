"""算例 11.4.1—11.4.2：分割的指标与一个不用学习的基线（11.4 节）。

（1）在合成的零件图上做阈值分割：把比局部背景暗若干个标准差的像素判为缺陷，算平均交并比（mIoU）与 Dice。
    阈值从松到紧，看两个指标怎样变——松了把纹理也算进来，紧了漏掉划痕的两端。
（2）三类缺陷分别有多难：划痕细长、压痕有高光的坑沿、锈斑边界模糊，同一个阈值在三类上的 Dice 相差很大。
    这正是“逐像素判定”比“一个阈值”更需要学习的地方（11.4.3 节）。
"""
import numpy as np
from scipy import ndimage

from _ch11 import KINDS, dataset, dice, miou, sample
from bookout import out


def threshold_seg(img, k):
    bg = ndimage.uniform_filter(img, 31)
    d = bg - img
    return d > k * d.std()


data = [s for s in dataset(150, start=9000) if s["labels"]]
v = {"n_img": len(data)}
best = (0, -1.0, 0.0)
for k in (1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0):
    m = float(np.mean([miou(threshold_seg(s["image"], k), s["mask"]) for s in data]))
    d = float(np.mean([dice(threshold_seg(s["image"], k), s["mask"]) for s in data]))
    key = str(k).replace(".", "p")
    v[f"k{key}_miou"], v[f"k{key}_dice"] = m, d
    if d > best[1]:
        best = (k, d, m)
v["best_k"], v["best_dice"], v["best_miou"] = best[0], best[1], best[2]
v["k1p0_miou_note"] = "阈值太松：磨削纹理也被判成缺陷"

# （2）按缺陷种类看
for kind in KINDS:
    sub = [s for s in data if s["labels"] and s["labels"][0] == kind and len(s["labels"]) == 1]
    if not sub:
        continue
    d = float(np.mean([dice(threshold_seg(s["image"], best[0]), s["mask"]) for s in sub]))
    key = {"划痕": "scratch", "压痕": "dent", "锈斑": "rust"}[kind]
    v[key + "_dice"] = d
    v[key + "_n"] = len(sub)
v["hard"] = min((v[k + "_dice"], k) for k in ("scratch", "dent", "rust") if k + "_dice" in v)[1]
v["spread"] = max(v[k + "_dice"] for k in ("scratch", "dent", "rust") if k + "_dice" in v) - \
    min(v[k + "_dice"] for k in ("scratch", "dent", "rust") if k + "_dice" in v)

# 一张图上三类的像素占比（类别极不平衡：缺陷像素只占百分之几）
frac = float(np.mean([s["mask"].mean() for s in data])) * 100
v["defect_pct"] = frac
out(**v)
