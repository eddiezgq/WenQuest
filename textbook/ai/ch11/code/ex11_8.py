"""算例 11.8.1—11.8.3：案例的三件事（11.8 节）。

（1）数据：合成数据集的规模、类别分布与缺陷像素的占比；训练、验证、测试按种子区间划分，互不重叠。
（2）阈值不是按准确率选的：产线上漏检一个缺陷件的代价远高于误判一个合格件（返修 vs 停线、客诉）。
    给定漏检与误检的代价，算出使总代价最小的判定阈值，并与“让准确率最高”的阈值对照。
（3）尺寸测量：用同一套图像量出轴径的像素数，按每像素 12 微米换算，与 SH-301 的公差带（Ø35 k6）比较；
    像素量化本身带来多大的测量不确定度——这决定了视觉测量能不能替代量具（答案是：这个分辨率下不能）。
"""
import numpy as np
from scipy import ndimage

from _ch11 import KINDS, PIX_UM, dataset, dice
from bookout import out

v = {}
# ---------- （1）数据
train, val, test = dataset(400, 0), dataset(100, 400), dataset(200, 500)
v["n_train"], v["n_val"], v["n_test"] = len(train), len(val), len(test)
allsets = train + val + test
v["n_all"] = len(allsets)
ok = sum(1 for s in allsets if s["label"] == "无")
v["ok_pct"] = ok / len(allsets) * 100
for kind in KINDS:
    key = {"划痕": "scratch", "压痕": "dent", "锈斑": "rust"}[kind]
    v[key + "_n"] = sum(1 for s in allsets if kind in s["labels"])
v["defect_px_pct"] = float(np.mean([s["mask"].mean() for s in allsets])) * 100
v["imbalance"] = v["ok_pct"] / (100 - v["ok_pct"])

# ---------- （2）代价敏感的阈值
def score(img, seed=0):
    """这张图“有多像有缺陷”：取局部对比度的高分位数（不是最大值——最大值只看一个像素，
    在合成数据上把两类分得过开，真实产线上没有这么干净），再加一点测量噪声代表光照与镜头的波动。"""
    bg = ndimage.uniform_filter(img, 31)
    d = ndimage.uniform_filter(bg - img, 3)                    # 先平滑，单个噪点不算数
    base = float(np.percentile(d, 99.9) / max(d.std(), 1e-6))
    return base + float(np.random.default_rng(777 + seed).normal(0, 0.25))


scores = np.array([score(s["image"], 500 + i) for i, s in enumerate(test)])
labels = np.array([s["label"] != "无" for s in test])
v["score_ok"] = float(scores[~labels].mean())
v["score_bad"] = float(scores[labels].mean())

C_MISS, C_FALSE = 50.0, 1.0                       # 漏检一个缺陷件 50 元，误判一个合格件 1 元（返修与复检的工时）
v["c_miss"], v["c_false"] = C_MISS, C_FALSE
best_cost, best_acc = (None, 1e18), (None, -1)
rows = []
for t in np.linspace(scores.min(), scores.max(), 200):
    pred = scores >= t
    fn = int((~pred & labels).sum())
    fp = int((pred & ~labels).sum())
    tp = int((pred & labels).sum())
    tn = int((~pred & ~labels).sum())
    cost = fn * C_MISS + fp * C_FALSE
    acc = (tp + tn) / len(test)
    rows.append((float(t), cost, acc, fn, fp, tp / max(tp + fn, 1), tp / max(tp + fp, 1)))
    if cost < best_cost[1]:
        best_cost = (float(t), cost)
    if acc > best_acc[1]:
        best_acc = (float(t), acc)
tc, cost = best_cost
ta, acc = best_acc
pc = [r for r in rows if r[0] == tc][0]
pa = [r for r in rows if r[0] == ta][0]
v["t_cost"], v["cost_min"] = tc, cost
v["t_acc"], v["acc_max"] = ta, acc * 100
v["cost_at_acc"] = pa[1]
v["cost_extra"] = pa[1] - cost                    # 按“准确率最高”选阈值，每 200 件多付的代价
v["recall_cost"], v["prec_cost"] = pc[5] * 100, pc[6] * 100
v["recall_acc"], v["prec_acc"] = pa[5] * 100, pa[6] * 100
v["miss_cost"], v["miss_acc"] = pc[3], pa[3]
v["false_cost"], v["false_acc"] = pc[4], pa[4]
v["roc"] = [[float(r[0]), float(r[5]), float(r[6])] for r in rows[::10]]
assert tc != ta and v["cost_extra"] > 0, "代价最小与准确率最高的阈值重合了，这个算例就没有意义——检查打分函数"

# ---------- （3）尺寸测量
D_NOM, TOL_LO, TOL_HI = 35.0, 35.002, 35.018      # SH-301 输出轴 Ø35 k6 的公差带（毫米）
v["d_nom"], v["tol_lo"], v["tol_hi"] = D_NOM, TOL_LO, TOL_HI
v["tol_um"] = (TOL_HI - TOL_LO) * 1000            # 公差带宽度（微米）
v["pix_um"] = PIX_UM
v["pix_per_tol"] = v["tol_um"] / PIX_UM           # 整条公差带只有一个多像素
# 边缘定位做到亚像素（取 1/5 像素）时的测量不确定度：直径是两条边缘之差，按独立误差合成乘 √2
v["sub_um"] = PIX_UM / 5 * np.sqrt(2)
v["ratio_tol"] = v["tol_um"] / v["sub_um"]
v["enough"] = v["ratio_tol"] >= 10                # 测量系统通常要求不确定度不超过公差的十分之一
out(**v)
