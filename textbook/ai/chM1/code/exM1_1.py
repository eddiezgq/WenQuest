"""算例 M1.1.1—M1.1.3：一批零件的测量数据长什么样（M1.1 节）。

一批样本在计算机里就是一个矩阵：一行一个零件，一列一项测量。本程序给出这批数据的形状与大小、
按行与按列各能看出什么，以及"矩阵乘向量"在这里的实际含义——按一组权重给每个零件打一个分。
"""
import numpy as np

from _chM1 import FEATURES, NOMINAL, UNITS, parts
from bookout import out

X = parts()
n, d = X.shape
v = {"n": n, "d": d, "n_num": n * d}
v["kB32"] = n * d * 4 / 1024                                  # 单精度：每个数 4 字节
v["kB64"] = n * d * 8 / 1024
v["MB_img"] = 200 * 3 * 2160 * 3840 / 1024**2                 # 对比：200 张彩色照片（第 11 章的一帧）

# ---------- 按行看：一个零件；按列看：一项测量
row = X[0]
v["row0"] = [round(float(a), 3) for a in row]
for i, name in enumerate(("od", "id", "len", "round", "ra")):
    v[f"mean_{name}"] = float(X[:, i].mean())
    v[f"sd_{name}"] = float(X[:, i].std(ddof=1))
v["sd_ratio"] = v["sd_len"] / v["sd_od"]                      # 几列的波动差了多少倍（M1.3 节要用）

# ---------- 矩阵乘向量：按一组权重给每个零件打分
w = np.array([0.0, 0.0, 0.0, 1.0, 2.0])                       # 只看圆度与粗糙度，粗糙度加倍
s = X @ w                                                     # (n,5)·(5,) → (n,)：一次矩阵乘向量
v["w"] = w.tolist()
v["score0"] = float(s[0])
v["score_worst"] = float(s.max())
v["i_worst"] = int(s.argmax()) + 1                            # 第几个零件（从 1 数）
v["mac_score"] = n * d                                        # 这一次打分做了多少次乘加
v["flop_score"] = 2 * n * d
# 同一件事用循环写出来，结果必须一样——矩阵乘法只是把这几行循环交给了库（和后面的 GPU）
loop = np.array([sum(X[i, j] * w[j] for j in range(d)) for i in range(n)])
assert np.allclose(loop, s), "循环写法与矩阵乘向量必须给出同一个结果"
# 不记耗时：同一段代码在不同机器上快慢不同，书里的数要能复算（实测统一放第 4 章起的云端 GPU 实验）
v["nominal_od"], v["unit_od"] = NOMINAL[0], UNITS[0]
v["f1"], v["f4"], v["f5"] = FEATURES[0], FEATURES[3], FEATURES[4]
out(**v)
