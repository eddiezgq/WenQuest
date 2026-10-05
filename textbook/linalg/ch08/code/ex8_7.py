"""8.7 节：应用——车间配电网的有向图（4 个节点、5 条支路）的关联矩阵：秩 3；零空间是“各节点电位相同”；
左零空间是回路电流（2 个独立回路）；基尔霍夫电流定律与电压定律。Franka Panda 的 6×7 雅可比矩阵：零空间一维，即自运动。"""
import numpy as np
import scipy.linalg as sla

from _arm import panda
from bookout import out, tex, vec

# 支路（起点 → 终点）：1→2, 1→3, 2→3, 2→4, 3→4
edges = [(1, 2), (1, 3), (2, 3), (2, 4), (3, 4)]
M = np.zeros((5, 4))
for k, (i, j) in enumerate(edges):
    M[k, i - 1], M[k, j - 1] = -1, 1
out(M=tex(M, 0), rM=int(np.linalg.matrix_rank(M)))
out(const=vec(M @ np.ones(4), 0))
# 回路：支路 1、3 与 2 反向组成回路 1→2→3→1；支路 3、5 与 4 反向组成回路 2→3→4→2
l1, l2 = np.array([1.0, -1, 1, 0, 0]), np.array([0.0, 0, 1, -1, 1])
out(l1=vec(l1, 0), l2=vec(l2, 0), MTl=vec(M.T @ l1, 0), MTl2=vec(M.T @ l2, 0), dNT=sla.null_space(M.T).shape[1])
# 电位差：节点电位 u，支路电压 e = M u；各回路上电压之和为零
u = np.array([24.0, 23.5, 23.0, 22.0])
e = M @ u
out(e=vec(e, 1), loop=float(l1 @ e), loop2=float(l2 @ e))
# Panda：ready 姿态
arm = panda()
q = np.array([0.0, -np.pi / 4, 0, -3 * np.pi / 4, 0, np.pi / 2, np.pi / 4])
J = arm.jacobian(q)
N = sla.null_space(J)
out(Jshape=f"{J.shape[0]}×{J.shape[1]}", rJ=int(np.linalg.matrix_rank(J)), dNJ=N.shape[1],
    nvec=vec(N[:, 0] / np.abs(N[:, 0]).max() * np.sign(N[np.argmax(np.abs(N[:, 0])), 0]), 3), JN=float(np.abs(J @ N).max()))
# 沿零空间走一小段：末端位置几乎不动，肘部（第 4 个关节的轴上点）移动
p0, el0 = arm.tool(q), arm.frames(q)[0][3][1]
qq = q.copy()
for _ in range(200):
    nn = sla.null_space(arm.jacobian(qq))[:, 0]
    if nn[2] < 0:
        nn = -nn
    qq = qq + 0.0025 * nn
out(dtool=float(np.linalg.norm(arm.tool(qq) - p0)) * 1000, delbow=float(np.linalg.norm(arm.frames(qq)[0][3][1] - el0)) * 1000)
