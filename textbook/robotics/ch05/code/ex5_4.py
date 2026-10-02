"""算例 5.4.1、5.4.2：坐标系树。

5.4.1 UR5e 本身是一条坐标系链：模型文件为每个连杆记下 T_父,子(θ) = Trans(xyz)·Rot_rpy·Rot(轴, θ)。
      在关节角 θ_A = (0°, −90°, 90°, −90°, −90°, 0°) 时，沿链相乘得到法兰位姿 T_sb，用三种互相独立的算法核对：
      (1) 模型关节表 entry.json 的数（rpy 写成 1.570796，有舍入）；(2) 网页三维模型 default.glb 的节点矩阵；
      (3) 第 12 章的指数积公式。并说明 (1) 与另两者相差约 10⁻⁶ m 的原因。
5.4.2 工作站的坐标系树（根为工作台 {w}）：求相机看到的工具位姿 T_ct。
      (1) 通用的树路径算法；(2) 手写的链 T_cw T_ws T_sb T_bt。再做回路检查 T_wc T_ct T_tw = I。
      转动关节 1 时，只有关节 1 以下的子树移动：T_wc 不变，T_ct 改变。
"""
import math

import numpy as np

from _frames import (DEG, FrameTree, T, T_bt, T_wc, T_ws, UR_LINKS, clean, inv, rot_z, texm, ur_edges_from_table, ur_entry,
                     ur_fk_glb, ur_fk_poe, ur_fk_table, vecm)
from bookout import T as TT, out

thA = np.array([0, -90, 90, -90, -90, 0]) * DEG

# ---------------------------------------------------------------- 算例 5.4.1
edges = ur_edges_from_table(thA)
T1, T2, T3 = ur_fk_table(thA), ur_fk_glb(thA), ur_fk_poe(thA)
d12, d23 = np.abs(T1 - T2).max(), np.abs(T2 - T3).max()
d12_p = np.linalg.norm(T1[:3, 3] - T2[:3, 3])                       # 位置差，m
d12_R = np.abs(T1[:3, :3] - T2[:3, :3]).max()                      # 姿态差（旋转矩阵元素），无量纲
assert d23 < 1e-12            # 网页模型与指数积：完全一致（只差舍入）
assert d12 < 1e-6             # 关节表：1.570796 与 π/2 相差 3.3e-7 rad，乘以约 1 m 的臂长
rpy_file = ur_entry()["robot"]["joints"][1]["origin"]["rpy"][1]          # 模型文件中记录的 π/2
rpy_err = abs(rpy_file - math.pi / 2)

# 每条边的位置部分（零位关节角时的连杆偏置）列成表 5.4.1
names = ["base"] + UR_LINKS + ["b"]
labels = [TT("基座连杆", "base link")] + [TT(f"连杆 {i}", f"link {i}") for i in range(1, 7)] + [TT("法兰 {b}", "flange {b}")]
rows = []
for (child, parent, Tm), lab in zip(edges, labels):
    rows.append(f"{lab} & {vecm(clean(Tm[:3, 3]), 3)}")

# 每个连杆坐标系原点在 {s} 中的位置（图 5.4.2 用）
M = np.eye(4)
origins = []
for _, _, Tm in edges:
    M = M @ Tm
    origins.append(M[:3, 3].copy())
assert np.allclose(M, T1)

# ---------------------------------------------------------------- 算例 5.4.2 工作站的坐标系树
tree = FrameTree("w")
tree.add("s", "w", T_ws())
for child, parent, Tm in edges:
    tree.add(child, parent, Tm)
tree.add("t", "b", T_bt())
tree.add("c", "w", T_wc())

Tct = tree.T("c", "t")
Tct_hand = inv(T_wc()) @ T_ws() @ T3 @ T_bt()
assert np.allclose(Tct, Tct_hand, atol=1e-6)
path = tree.path("c", "t")
n_up = sum(1 for _, _, d in path if d == "up")
n_down = len(path) - n_up
loop = T_wc() @ Tct @ tree.T("t", "w")
assert np.allclose(loop, np.eye(4), atol=1e-14)
Twt = tree.T_root("t")
assert np.allclose(Twt, tree.T("w", "t"), atol=1e-14)

# 转动关节 1：只有它下面的子树移动
before_wc, before_ct = tree.T("w", "c"), Tct.copy()
th2 = thA.copy()
th2[0] = 30 * DEG
for child, parent, Tm in ur_edges_from_table(th2):
    tree.set(child, Tm)
assert np.allclose(tree.T("w", "c"), before_wc)
assert not np.allclose(tree.T("c", "t"), before_ct)
assert np.allclose(tree.T("w", "s"), T_ws())

out(
    TsbA=texm(clean(T3), 4), d12=d12, d12_p=d12_p, d12_R=d12_R, d23=d23, rpy_err=rpy_err, rpy_file=rpy_file, rows=r" \\ ".join(rows),
    Tct=texm(clean(Tct), 4), pct=vecm(Tct[:3, 3], 4), dist_ct=np.linalg.norm(Tct[:3, 3]),
    n_up=n_up, n_down=n_down, n_edges=len(path),
    Twt=texm(clean(Twt), 4), pwt=vecm(Twt[:3, 3], 4),
    origins=[o.tolist() for o in origins],
)
