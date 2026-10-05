"""算例 11.6.1—11.6.3：视频的三笔账（11.6 节）。

（1）时序冗余：相邻两帧之间变化的像素占百分之几（在合成的传送带画面上算），
    以及“每帧都从头检测”与“检测一次、中间几帧只做跟踪”在算力上差多少。
（2）检测加关联：用交并比做代价矩阵、贪心匹配与最优匹配（匈牙利算法）各得到什么结果；
    漏检一帧时轨迹会不会断（这决定了要不要卡尔曼滤波的预测）。
（3）每帧的时间预算：3840×2160、每秒 60 帧，一帧 16.7 ms；检测网络（算例 11.1.3）、跟踪与后处理各占多少，
    与第 6 章三段流水重叠后的吞吐量对照。
"""
import numpy as np
from scipy.optimize import linear_sum_assignment

from _ch11 import MODELS, iou
from bookout import out

rng = np.random.default_rng(116)
v = {}

# ---------- （1）时序冗余：传送带上零件匀速移动
H, W = 256, 256
base = rng.normal(0.6, 0.02, (H, W)).astype(np.float32)
obj = np.zeros((H, W), bool)
obj[100:140, 60:120] = True


def frame(t, speed=6):
    img = base + rng.normal(0, 0.012, (H, W)).astype(np.float32)   # 每帧都有独立的读出噪声，不然帧间差严格为零
    sh = int(t * speed)
    m = np.roll(obj, sh, axis=1)
    img[m] -= 0.25
    return img, m


f0, m0 = frame(0)
f1, m1 = frame(1)
diff = np.abs(f1 - f0) > 0.05
v["changed_pct"] = float(diff.mean()) * 100
v["speed_px"] = 6

# 每帧的运算量：检测网络按 ResNet-50 一级的主干（算例 11.1.2 算出 224×224 时 7.72 GFLOP），
# 检测时输入放大到 1280×1280（卷积网络的运算量随像素数成正比），跟踪只做匹配与滤波
DET_GF, TRK_GF = MODELS["res"][0] / 1e9 * (1280 / 224) ** 2, 0.05
for k in (1, 2, 5, 10):
    v[f"every{k}_GF"] = (DET_GF + (k - 1) * TRK_GF) / k
v["save5"] = v["every1_GF"] / v["every5_GF"]
v["det_GF"], v["trk_GF"] = DET_GF, TRK_GF

# ---------- （2）关联：三条轨迹、三个检测框
prev = [(10, 10, 50, 50), (100, 100, 140, 140), (200, 60, 240, 100)]
cur = [(104, 103, 144, 143), (14, 12, 54, 52), (205, 64, 245, 104)]
cost = np.array([[1 - iou(p, c) for c in cur] for p in prev])
row, col = linear_sum_assignment(cost)
v["match_cost"] = float(cost[row, col].sum())
greedy, used = [], set()
for i in range(len(prev)):                        # 贪心：每条轨迹各自挑最像的那个框
    j = int(np.argmin([cost[i][j] if j not in used else 9 for j in range(len(cur))]))
    greedy.append(j)
    used.add(j)
v["greedy_cost"] = float(sum(cost[i][greedy[i]] for i in range(len(prev))))
# 一个贪心会出错的例子：第一条轨迹与两个框都像，第二条只与其中一个像。
# 代价矩阵（1 − 交并比）写成下面这样时，贪心先让第一条占住最像的那个，第二条就只剩很差的选择。
c2 = np.array([[0.10, 0.20], [0.15, 0.90]])
r2, cc2 = linear_sum_assignment(c2)
g2, used2 = [], set()
for i in range(2):
    j = int(np.argmin([c2[i][j] if j not in used2 else 9 for j in range(2)]))
    g2.append(j)
    used2.add(j)
v["near_opt"] = float(c2[r2, cc2].sum())
v["near_greedy"] = float(sum(c2[i][g2[i]] for i in range(2)))
v["greedy_worse"] = v["near_greedy"] > v["near_opt"] + 1e-9

# ---------- （3）每帧的预算
FPS = 60
v["budget_ms"] = 1000 / FPS
v["det_trk_ratio"] = DET_GF / TRK_GF                  # 跟踪比检测便宜多少
A10 = 125e12
v["det_ms"] = DET_GF * 1e9 / A10 * 1e3            # 按峰值算的下限
v["det_ms_real"] = v["det_ms"] / 0.35             # 实际按峰值的三成多算（第 7、8 章的实测量级）
v["left_ms"] = v["budget_ms"] - v["det_ms_real"]
v["fits"] = v["left_ms"] > 0
out(**v)
