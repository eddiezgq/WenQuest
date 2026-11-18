"""算例 21.2.1—21.2.4：不良率、按图片还是按零件、阈值该放哪（21.2 节）。

四件事：
（1）**同一个检测器，不良率一变，印出来的指标就变**——而检测器本身一个参数都没动；
（2）**"准确率 99%" 在千分之几的不良率下还不如全判合格**；
（3）**按图片算与按零件算是两套数**：一个零件拍五张图，任何一张报警就判不良，
    误判会被放大五倍左右；
（4）**阈值不该由准确率定，该由代价定**：漏检与误判代价差多少，最优阈值就移多少。
"""
import numpy as np

from _ch21 import (best_threshold, confusion, cost_of, metrics, per_part, sample_scores)
from bookout import out

N = 200000
SEP = 2.2                      # 检测器的本事：好件与坏件的分数差多少（全程不变）
v = {"n_parts": N, "separation": SEP}

# ---------- 一、同一个检测器，三档不良率
for rate, tag in ((0.05, "5pct"), (0.005, "0p5pct"), (0.0005, "0p05pct")):
    good, bad = sample_scores(N, rate, sep=SEP, seed=1)
    c = confusion(good, bad, 1.1)
    m = metrics(c)
    v[f"prec_{tag}"] = m["precision"] * 100
    v[f"rec_{tag}"] = m["recall"] * 100
    v[f"acc_{tag}"] = m["accuracy"] * 100
    v[f"fpr_{tag}"] = m["fpr"] * 100
    v[f"nbad_{tag}"] = c["tp"] + c["fn"]
    print(f"不良率 {rate * 100:>5.2f}%：准确率 {m['accuracy'] * 100:.2f}%　"
          f"查全率 {m['recall'] * 100:.1f}%　查准率 {m['precision'] * 100:.1f}%　"
          f"误判率 {m['fpr'] * 100:.1f}%")
assert v["prec_5pct"] > v["prec_0p5pct"] > v["prec_0p05pct"], \
    "不良率越低，查准率越低——这是基率，不是模型变差"
v["prec_drop"] = v["prec_5pct"] / v["prec_0p05pct"]
print(f"**查全率与误判率一个没变，查准率却掉到 {v['prec_drop']:.0f} 分之一**——"
      f"变的只是不良率")

# ---------- 二、与"全判合格"比
good, bad = sample_scores(N, 0.0005, sep=SEP, seed=1)
v["all_pass_acc"] = (1 - 0.0005) * 100
v["model_acc"] = v["acc_0p05pct"]
v["beats_all_pass"] = bool(v["model_acc"] > v["all_pass_acc"])
print(f"\n不良率 0.05% 时：全判合格的准确率就是 {v['all_pass_acc']:.2f}%，"
      f"而这个检测器是 {v['model_acc']:.2f}%")
print(f"检测器的准确率比“全判合格”更高吗：{v['beats_all_pass']}。"
      f"**所以在产线上印准确率，基本等于什么都没说**")

# ---------- 三、按图片还是按零件
VIEWS = 5
good5, bad5 = sample_scores(N, 0.004, sep=SEP, seed=7)
img_c = confusion(good5, bad5, 1.1)
img_m = metrics(img_c)
# 零件级：好件的 5 张图都是好图；坏件只要有一张拍到缺陷（这里设缺陷在 2 张图上可见）
rng = np.random.default_rng(3)
good_part = per_part(good5, VIEWS, "max")
n_bad_parts = len(bad5) // 2                       # 每个坏件两张能看见缺陷的图
bad_part = np.maximum(bad5[:n_bad_parts * 2:2], bad5[1:n_bad_parts * 2:2])
part_c = confusion(good_part, bad_part, 1.1)
part_m = metrics(part_c)
v["views"] = VIEWS
v["img_prec"] = img_m["precision"] * 100
v["img_rec"] = img_m["recall"] * 100
v["img_fpr"] = img_m["fpr"] * 100
v["part_prec"] = part_m["precision"] * 100
v["part_rec"] = part_m["recall"] * 100
v["part_fpr"] = part_m["fpr"] * 100
v["fpr_blowup"] = v["part_fpr"] / v["img_fpr"]
print(f"\n按图片算：查准率 {v['img_prec']:.1f}%　查全率 {v['img_rec']:.1f}%　"
      f"误判率 {v['img_fpr']:.2f}%")
print(f"按零件算（{VIEWS} 张图，任何一张报警就判不良）：查准率 {v['part_prec']:.1f}%　"
      f"查全率 {v['part_rec']:.1f}%　误判率 {v['part_fpr']:.2f}%")
assert v["part_fpr"] > v["img_fpr"], "任何一张报警就判不良，误判一定被放大"
assert v["part_rec"] >= v["img_rec"], "多看几眼，查全率只会更高"
print(f"**误判率放大 {v['fpr_blowup']:.1f} 倍，查全率却也上去了**——"
      f"这两件事是同一个决策规则带来的，报指标时必须写明按哪一级算")

# ---------- 四、阈值由代价定
good, bad = sample_scores(N, 0.004, sep=SEP, seed=11)
rows = []
for miss, false_ in ((1.0, 1.0), (10.0, 1.0), (100.0, 1.0), (1000.0, 1.0)):
    thr, cost = best_threshold(good, bad, miss, false_)
    c = confusion(good, bad, thr)
    m = metrics(c)
    rows.append((miss, thr, cost, m["recall"] * 100, m["precision"] * 100))
    tag = f"{int(miss)}"
    v[f"thr_m{tag}"] = thr
    v[f"cost_m{tag}"] = cost
    v[f"rec_m{tag}"] = m["recall"] * 100
    v[f"prec_m{tag}"] = m["precision"] * 100
    print(f"漏检:误判 = {miss:>6.0f}:1　最优阈值 {thr:+.2f}　总代价 {cost:,.0f}　"
          f"查全率 {m['recall'] * 100:.1f}%　查准率 {m['precision'] * 100:.1f}%")
assert v["thr_m1000"] < v["thr_m1"], "漏检越贵，阈值越要往下压（宁可多判几个不良）"
v["thr_move"] = v["thr_m1"] - v["thr_m1000"]
print(f"代价比从 1:1 变到 1000:1，最优阈值往下移了 {v['thr_move']:.2f}")

# 用"准确率最高"去选阈值，代价会差多少
acc_thr, best_acc = 0.0, -1.0
for thr in np.linspace(-3, 6, 901):
    a = metrics(confusion(good, bad, float(thr)))["accuracy"]
    if a > best_acc:
        acc_thr, best_acc = float(thr), a
v["acc_thr"] = acc_thr
v["acc_thr_cost"] = cost_of(confusion(good, bad, acc_thr), 100.0, 1.0)
v["cost_penalty"] = v["acc_thr_cost"] / v["cost_m100"]
print(f"\n按“准确率最高”选的阈值是 {v['acc_thr']:+.2f}（准确率 {best_acc * 100:.2f}%）；"
      f"在漏检:误判 = 100:1 的车间里，它的总代价是最优阈值的 {v['cost_penalty']:.1f} 倍")
assert v["cost_penalty"] > 1.0, "按准确率选阈值在代价不对称时必然吃亏"
print("**结论：阈值是经济决策，不是统计决策**——"
      "要定阈值，先把漏检一个赔多少、误判一个花多少写出来")

out(**v)
