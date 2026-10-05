"""算例 11.3.1—11.3.3：检测器怎样评分（11.3 节）。

（1）交并比与非极大值抑制：手算一个例子核对 _ch11.iou 与 nms；同一个物体上重复的框被抑制掉几个。
（2）平均精度（AP）：在合成数据集上做一个“取巧的检测器”——直接用阈值分割找出暗区域作为检测框（11.4 节的基线），
    给每个框一个得分（面积 × 暗度），算出 IoU 阈值 0.5 下的 AP 与查准率—查全率曲线。
（3）得分阈值怎样影响查准率与查全率：这就是 11.8 节代价敏感阈值的来源。
"""
import numpy as np
from scipy import ndimage

from _ch11 import average_precision, dataset, iou, nms
from bookout import out

v = {}
# ---------- （1）手算核对
a, b, c = (0, 0, 10, 10), (5, 5, 15, 15), (0, 0, 10, 10)
v["iou_half"] = iou(a, b)                                      # 交 25、并 175
v["iou_same"] = iou(a, c)
v["iou_hand"] = 25 / 175
assert abs(v["iou_half"] - v["iou_hand"]) < 1e-12
boxes = [(0, 0, 10, 10), (1, 1, 11, 11), (2, 0, 12, 10), (60, 60, 70, 70)]
scores = [0.9, 0.85, 0.8, 0.7]
keep = nms(boxes, scores, 0.5)
v["nms_in"], v["nms_out"] = len(boxes), len(keep)
v["nms_drop"] = len(boxes) - len(keep)


# ---------- （2）阈值分割做的“检测器”
def threshold_detect(img, k=2.0):
    """把比局部背景暗 k 个标准差的像素连成块，每块给一个框与得分。这是不用学习的基线。"""
    bg = ndimage.uniform_filter(img, 31)
    d = bg - img
    hit = d > k * d.std()
    lab, n = ndimage.label(hit)
    out_boxes, out_scores = [], []
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < 20:                                       # 太小的连通块当作噪声
            continue
        ys, xs = np.nonzero(m)
        out_boxes.append((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
        out_scores.append(float(d[m].mean() * np.sqrt(m.sum())))
    return out_boxes, out_scores


data = dataset(120, start=5000)
pb, ps, gb, pi, gi = [], [], [], [], []
per_img = []
for n, s in enumerate(data):
    bx, sc = threshold_detect(s["image"])
    k = nms(bx, sc, 0.3)
    bx, sc = [bx[i] for i in k], [sc[i] for i in k]
    per_img.append((bx, sc, s["boxes"]))
    pb += bx
    ps += sc
    pi += [n] * len(bx)
    gb += s["boxes"]
    gi += [n] * len(s["boxes"])
mx = max(ps) if ps else 1.0
ps = [x / mx for x in ps]                                      # 得分归一到 0—1
ap, prec, rec = average_precision(pb, ps, gb, 0.5, pi, gi)      # 逐图匹配：一张图的预测不去命中另一张图的真值
v["n_img"] = len(data)
v["n_gt"] = len(gb)
v["n_pred"] = len(pb)
v["ap50"] = ap
ap75, _, _ = average_precision(pb, ps, gb, 0.75, pi, gi)
v["ap75"] = ap75
v["prec"] = [float(x) for x in prec]
v["rec"] = [float(x) for x in rec]

# ---------- （3）得分阈值的影响
rows = []
for t in (0.05, 0.1, 0.2, 0.4):
    tp = fp = 0
    fn = 0
    for bx, sc, gt in per_img:
        sel = [bx[i] for i in range(len(bx)) if sc[i] / mx >= t]        # 得分按全集的最大值归一后再比阈值
        used = [False] * len(gt)
        for p in sel:
            best, bi = 0.0, -1
            for j, g in enumerate(gt):
                val = iou(p, g)
                if val > best:
                    best, bi = val, j
            if best >= 0.5 and bi >= 0 and not used[bi]:
                used[bi] = True
                tp += 1
            else:
                fp += 1
        fn += used.count(False)
    rows.append((t, tp, fp, fn, tp / max(tp + fp, 1), tp / max(tp + fn, 1)))
for t, tp, fp, fn, p, r in rows:
    key = str(t).replace("0.", "p")
    v[f"t{key}_prec"], v[f"t{key}_rec"] = p * 100, r * 100
v["t_low"], v["t_high"] = rows[0][0], rows[-1][0]
v["prec_low"], v["rec_low"] = rows[0][4] * 100, rows[0][5] * 100
v["prec_high"], v["rec_high"] = rows[-1][4] * 100, rows[-1][5] * 100
out(**v)
