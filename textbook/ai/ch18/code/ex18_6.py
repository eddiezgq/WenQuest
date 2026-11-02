"""算例 18.6.1—18.6.2：批次效应——不校正看不见真结构，校正过度看见的是假结构（18.6 节）。

（1）两批细胞、三种类型。不校正时，降维图上分开的是**批次**，不是类型。
（2）把"去掉几个方向"从 0 加到 4：批次混得越来越匀，而细胞类型在第 3 个方向之后被抹平到
    与瞎猜一样。**只看批次混合度这一个指标，会把一次彻底的失败判成成功。**
"""
import numpy as np

from _ch18 import cells, correct_batch, mixing, neighbour_purity, pca
from bookout import out

v = {}
N_PER, N_GENE = 120, 60
x, types, batch = cells(N_PER, N_GENE, seed=0, batch_shift=1.6, batch_p=(0.7, 0.5, 0.3))
v["n_cells"], v["n_gene"] = len(types), N_GENE
v["n_types"] = int(len(np.unique(types)))
v["n_batch"] = int(len(np.unique(batch)))
v["chance_purity"] = 1 / v["n_types"]
v["mix_ideal"] = 0.5

# 两批的细胞组成本来就不一样——真实实验里从来不会一样，这正是校正过度会伤到真信号的来由
v["comp_rows"] = [(int(k), int(((types == k) & (batch == 0)).sum()),
                   int(((types == k) & (batch == 1)).sum())) for k in range(v["n_types"])]
v["comp_t0_b0"], v["comp_t0_b1"] = v["comp_rows"][0][1], v["comp_rows"][0][2]
v["comp_t2_b0"], v["comp_t2_b1"] = v["comp_rows"][2][1], v["comp_rows"][2][2]

# ---------- 扫"去掉几个方向"
v["rows"] = []
for n in (0, 1, 2, 3, 4):
    z = pca(correct_batch(x, batch, n), 2)
    p, m = neighbour_purity(z, types), mixing(z, batch)
    v["rows"].append((n, round(p, 3), round(m, 3)))
    v[f"pur_{n}"], v[f"mix_{n}"] = round(p, 3), round(m, 3)

assert v["mix_0"] < 0.05, "不校正时两批几乎完全不挨着（理想值 0.5）"
assert v["pur_1"] > v["pur_0"] + 0.1, "去掉批次方向，类型才聚得起来"
assert v["mix_1"] > v["mix_0"] + 0.2, "也才混得匀一些"
assert v["pur_3"] < v["chance_purity"] + 0.05, \
    "去掉三个方向，细胞类型被抹平到与瞎猜一样"
assert v["mix_3"] > v["mix_1"], \
    "而批次混合度一路变好——**只看它会把一次彻底的失败判成成功**"

v["best_n"] = max(v["rows"], key=lambda r: r[1])[0]
v["over_purity_loss"] = (v["pur_1"] - v["pur_3"]) * 100
v["over_mixing_gain"] = (v["mix_3"] - v["mix_1"]) * 100
assert v["best_n"] == 1, "恰好去掉批次方向那一档最好"

out(**v)
