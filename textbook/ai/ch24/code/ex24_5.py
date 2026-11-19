"""算例 24.5：抓取位姿打分的几何玩具。

工件是一块 L 形连接板（**质心不在几何中心**，这才有讲头）。在它上面采一批抓取位姿
（夹爪沿某个方向夹在过某点的那条线上），用三条几何判据打分：

1. 两个接触点的连线**离质心多远**——离得远，夹住后容易绕质心转掉；
2. **夹爪开口够不够**——夹不下就是 0 分；
3. **摩擦锥近似**——夹紧方向与接触面法线的夹角超出 arctan(mu) 就容易滑。

“实际成功率”另算（`grasp_truth`）：抓起来之后加定位扰动与晃动，看会不会滑脱或转掉。
它比打分多算两件事——接触点处的**真实法线**（打分里按抓取线方向近似了）、
以及抬起时质心偏置产生的力矩。**打分是近似，真相是另一套算法**，这正是本算例要量的差。

报三件事：几何打分前几名的实际成功率、随便挑的实际成功率、
以及**只看开口不看质心**（工程上最常见的偷懒判据）会错多少。
"""
import math

import numpy as np

from _ch24 import (GRIPPER, cross2, grasp_line, grasp_score, grasp_truth, poly_centroid,
                   polygon)
from bookout import out

N_CAND = 400
TOP = 5

v = {"n_sampled": N_CAND, "top_k": TOP, "open_max_m": GRIPPER["open_max_m"], "mu": GRIPPER["mu"]}

P = polygon("L")
c = poly_centroid(P)
v["centroid_x"], v["centroid_y"] = float(c[0]), float(c[1])
v["bbox_w"] = float(P[:, 0].max() - P[:, 0].min())
v["bbox_h"] = float(P[:, 1].max() - P[:, 1].min())
v["corner_x"] = float((P[:, 0].min() + P[:, 0].max()) / 2)
print(f"工件：L 形连接板，外廓 {v['bbox_w'] * 1000:.0f} × {v['bbox_h'] * 1000:.0f} mm，"
      f"质心在 ({v['centroid_x'] * 1000:.1f}, {v['centroid_y'] * 1000:.1f}) mm"
      f"——**不在外廓中心**")
print(f"夹爪：最大开口 {GRIPPER['open_max_m'] * 1000:.0f} mm，摩擦系数 {GRIPPER['mu']:.2f}"
      f"（显式假设）")

g = np.random.default_rng(0)
cands = []
while len(cands) < N_CAND:
    ctr = np.array([g.uniform(P[:, 0].min(), P[:, 0].max()),
                    g.uniform(P[:, 1].min(), P[:, 1].max())])
    ang = g.uniform(0.0, math.pi)
    gl = grasp_line(P, ctr, ang)
    if gl is None:
        continue
    i = len(cands)
    cands.append({"gl": gl, "score": grasp_score(P, gl), "truth": grasp_truth(P, gl, seed=i),
                  "width": gl["width"]})

score = np.array([x["score"] for x in cands])
truth = np.array([x["truth"] for x in cands])
width = np.array([x["width"] for x in cands])
fits = width <= GRIPPER["open_max_m"]
v["n_fits"] = int(fits.sum())
v["n_score_pos"] = int((score > 0).sum())
print(f"\n采到 {N_CAND} 个能夹到工件的位姿，其中 {v['n_fits']} 个开口夹得下、"
      f"{v['n_score_pos']} 个几何打分 > 0")

# ---------- 一、打分排名前几的实际成功率
order = np.argsort(-score)
v["succ_topk"] = float(truth[order[:TOP]].mean()) * 100
v["succ_top10"] = float(truth[order[:10]].mean()) * 100
v["succ_random"] = float(truth.mean()) * 100
v["succ_random_fits"] = float(truth[fits].mean()) * 100
v["lift"] = v["succ_topk"] / max(v["succ_random"], 1e-9)
print(f"\n几何打分前 {TOP} 名：实际成功率 {v['succ_topk']:.1f}%")
print(f"前 10 名：{v['succ_top10']:.1f}%")
print(f"随便挑一个（{N_CAND} 个全算）：{v['succ_random']:.1f}%；"
      f"只在“夹得下”的里面随便挑：{v['succ_random_fits']:.1f}%")
assert v["succ_topk"] > v["succ_random"] + 30.0, \
    "几何打分要明显优于随便挑——这是本算例的主结论"
print(f"**几何打分比随便挑强 {v['lift']:.1f} 倍**：三条判据全是中学几何，"
      f"一行学习都没有，却把成功率从 {v['succ_random']:.0f}% 提到 {v['succ_topk']:.0f}%。"
      f"**先用几何筛一遍，再谈学**")

v["corr"] = float(np.corrcoef(score, truth)[0, 1])
print(f"打分与实际成功率的相关系数 {v['corr']:.2f}——有用，但**不是 1**："
      f"打分是近似，近似就会错")

# ---------- 二、只看开口不看质心，会错多少
naive = np.where(fits, 1.0 - width / GRIPPER["open_max_m"], -1.0)   # 只挑“夹得最稳当的开口”
order_n = np.argsort(-naive)
v["succ_topk_widthonly"] = float(truth[order_n[:TOP]].mean()) * 100
v["succ_top10_widthonly"] = float(truth[order_n[:10]].mean()) * 100
v["widthonly_loss"] = v["succ_topk"] - v["succ_topk_widthonly"]
print(f"\n只看开口不看质心（挑开口最小的 {TOP} 个）：实际成功率 "
      f"{v['succ_topk_widthonly']:.1f}%，比三条判据一起用低 {v['widthonly_loss']:.1f} 个百分点")
assert v["succ_topk_widthonly"] < v["succ_topk"] - 20.0, \
    "只看开口会挑到“夹得下但离质心远”的位姿——这就是漏掉质心那一条的代价"
off_n = []
for i in order_n[:TOP]:
    gl = cands[i]["gl"]
    d = np.array([math.cos(gl["angle"]), math.sin(gl["angle"])])
    off_n.append(abs(cross2(d, c - gl["p0"])))
v["offset_widthonly_mm"] = float(np.mean(off_n)) * 1000
off_s = []
for i in order[:TOP]:
    gl = cands[i]["gl"]
    d = np.array([math.cos(gl["angle"]), math.sin(gl["angle"])])
    off_s.append(abs(cross2(d, c - gl["p0"])))
v["offset_scored_mm"] = float(np.mean(off_s)) * 1000
print(f"原因在一个数上：只看开口挑出来的那几个，抓取线离质心平均 "
      f"{v['offset_widthonly_mm']:.1f} mm；三条判据挑出来的只有 "
      f"{v['offset_scored_mm']:.1f} mm。**夹得下不等于夹得住**")

# ---------- 三、打分最高的那几个位姿，报给正文
v["top_list"] = []
print(f"\n打分前 {TOP} 名的位姿（给插图用）：")
for rank, i in enumerate(order[:TOP], 1):
    gl = cands[i]["gl"]
    row = [float(gl["center"][0]), float(gl["center"][1]), float(gl["angle"]),
           float(gl["width"]), float(score[i]), float(truth[i]) * 100]
    v["top_list"].append(row)
    print(f"  第 {rank} 名：过点 ({row[0] * 1000:5.1f}, {row[1] * 1000:5.1f}) mm，"
          f"方向 {math.degrees(row[2]):5.1f}°，开口 {row[3] * 1000:5.1f} mm，"
          f"打分 {row[4]:.3f}，实际成功率 {row[5]:.0f}%")
print("这个算例回答不了什么：这里是**平面、刚体、两点接触、摩擦系数已知**。"
      "真工件有形状误差与倒角，摩擦系数只知道个范围，视觉给的位姿也有误差；"
      "几何打分只能当**候选的排序器**，排完还得真抓——真机成功率要连试了多少次一起报")

out(**v)
