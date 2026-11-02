"""本章共用：机械臂三个关节电机的六节点热模型（21.3、21.4 节）。以下划线开头，构建时不单独运行。
每个电机两节点（绕组、外壳），参数同 16.1 节的 _motor.py；相邻关节的外壳经连杆导热（热阻 R_hh）。
节点顺序 (w₁, h₁, w₂, h₂, w₃, h₃)，温升 x 满足 C ẋ = −G x + P，G 为热导矩阵（对称），A = −C⁻¹G。"""
import numpy as np

CW, CH, RWH, RHA, RHH = 50.0, 500.0, 0.5, 1.0, 2.0


def model(rwh=(RWH,) * 3, rha=(RHA,) * 3, rhh=(RHH,) * 2):
    cap = np.array([CW, CH] * 3)
    G = np.zeros((6, 6))

    def link(i, j, g):
        G[i, i] += g; G[j, j] += g; G[i, j] -= g; G[j, i] -= g

    for k in range(3):
        link(2 * k, 2 * k + 1, 1 / rwh[k])
        G[2 * k + 1, 2 * k + 1] += 1 / rha[k]
    for k in range(2):
        link(2 * k + 1, 2 * k + 3, 1 / rhh[k])
    return cap, G, -G / cap[:, None]
