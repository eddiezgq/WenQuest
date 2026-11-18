"""算例 20.2.1—20.2.3：晶体的图表示能分辨什么、不能分辨什么（20.2 节）。

（1）截断半径是人定的，一改图就变——先把这件事量出来。
（2）**存在两个不同的结构，它们所有原子对的距离完全相同**（同距结构）。于是任何只用
    两体距离的描述子对它们给出一模一样的输入：**模型不是学不会，是看不见**。
（3）补上三体信息（一维里是"相邻两段的长短搭配"），两者立刻分开——所以三体项不是摆设。

这一条与 19.4 节"同一个粗场配两个细场"是同一个形状的论证：**先证明信息不在输入里，
再谈算法好坏**。
"""
import numpy as np

from _ch20 import (angle_feature, edge_histogram, homometric_pair, neighbor_graph,
                   pair_distances, same_up_to_symmetry)
from bookout import out

L = 18                       # 一维周期晶体，周期 18，胞内 6 个原子
A, B = homometric_pair(L)

v = {"period": L, "n_atoms": len(A),
     "sites_a": " ".join(str(x) for x in A), "sites_b": " ".join(str(x) for x in B)}

# ---------- 一、截断半径一改，图就变
for rc in (2, 3, 4, 5, 6, 8):
    v[f"edges_rc{rc}"] = len(neighbor_graph(A, L, rc))
    v[f"deg_rc{rc}"] = 2 * len(neighbor_graph(A, L, rc)) / len(A)
    print(f"截断 {rc}：边数 {v[f'edges_rc{rc}']:3d}，平均配位数 {v[f'deg_rc{rc}']:.2f}")
assert v["edges_rc2"] < v["edges_rc4"] < v["edges_rc8"], "截断越大边越多"
v["edge_ratio_2_to_8"] = v["edges_rc8"] / v["edges_rc2"]
print(f"截断从 2 加到 8，边数变成 {v['edge_ratio_2_to_8']:.1f} 倍——"
      f"**同一个晶体，喂给模型的图完全不同**")

# ---------- 二、两个不同的结构，距离集合完全相同
da, db = pair_distances(A, L), pair_distances(B, L)
v["n_pairs"] = len(da)
v["dist_identical"] = bool(np.array_equal(da, db))
v["not_same_structure"] = not same_up_to_symmetry(A, B, L)
v["dists"] = " ".join(f"{d:.0f}" for d in da)
print(f"\n两套位置：{v['sites_a']}  与  {v['sites_b']}")
print(f"全部 {v['n_pairs']} 个原子对的距离：{v['dists']}")
print(f"距离集合完全相同：{v['dist_identical']}；而两者不是平移或镜像："
      f"{v['not_same_structure']}")
assert v["dist_identical"] and v["not_same_structure"], \
    "这一对必须既同距、又确实是两个不同结构，否则整个论证不成立"

# 任何截断半径下，两体描述子看到的直方图都一样
same_hist = []
for rc in range(2, L // 2 + 1):
    ha, hb = edge_histogram(A, L, rc), edge_histogram(B, L, rc)
    same_hist.append(bool(np.array_equal(ha, hb)))
v["hist_same_all_cutoffs"] = all(same_hist)
v["n_cutoffs_checked"] = len(same_hist)
print(f"试过的 {v['n_cutoffs_checked']} 个截断半径，边长直方图全都一样："
      f"{v['hist_same_all_cutoffs']}")
assert v["hist_same_all_cutoffs"], "换截断半径救不了——两体信息本来就不够"

# ---------- 三、补上三体信息，立刻分开
fa, fb = angle_feature(A, L), angle_feature(B, L)
v["angle_gap"] = float(np.abs(fa - fb).max())
v["angle_separates"] = bool(v["angle_gap"] > 1e-6)
print(f"\n三体特征（相邻两段的长短之比）最大差 {v['angle_gap']:.4f}："
      f"{'分开了' if v['angle_separates'] else '还是分不开'}")
assert v["angle_separates"], "三体项应当能把同距结构分开"

# ---------- 四、这件事有多常见：周期 18、6 个原子里，同距但不同构的配对有多少
from itertools import combinations

seen: dict[tuple, list[tuple]] = {}
for comb in combinations(range(L), len(A)):
    if comb[0] != 0:                       # 固定第一个原子在 0，去掉平移带来的重复
        continue
    key = tuple(pair_distances(comb, L))
    seen.setdefault(key, []).append(comb)
# 一个距离类里的多种排法，可能只是彼此的平移或镜像——那不算两个结构。
# 所以要先按对称把每个距离类里的排法归并，再看归并后是不是还剩不止一个。
n_classes_multi = 0
pairs = 0
for g in seen.values():
    reps: list[tuple] = []
    for cfg in g:
        if not any(same_up_to_symmetry(list(cfg), list(r), L) for r in reps):
            reps.append(cfg)
    if len(reps) > 1:
        n_classes_multi += 1
        pairs += len(reps) * (len(reps) - 1) // 2

v["n_configs"] = sum(len(g) for g in seen.values())
v["n_dist_classes"] = len(seen)
v["n_homometric_pairs"] = pairs
v["homometric_class_pct"] = 100 * n_classes_multi / len(seen)
print(f"\n周期 {L}、{len(A)} 个原子、固定一个在原点：一共 {v['n_configs']:,} 种排法，"
      f"归成 {v['n_dist_classes']:,} 个距离类")
print(f"其中 {v['homometric_class_pct']:.1f}% 的距离类里装着**不止一个互不等价的结构**，"
      f"这样的配对共 {v['n_homometric_pairs']:,} 对")
assert v["n_homometric_pairs"] > 0, "同距结构不是孤例"
assert v["homometric_class_pct"] > 1, "这件事在这个尺寸上就已经相当常见"

out(**v)
