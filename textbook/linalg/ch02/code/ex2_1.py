"""2.1 节：位移是向量——车间里 AGV 的位移、它的长度，UR5e 末端点在基座坐标系中的位置向量。"""
import math

import numpy as np

from bookout import out, vec
from _arm import ur5e

# 车间地面坐标系（单位 m）：AGV 从上料工位 A 开到装配工位 B
A = np.array([2.0, 1.0])
B = np.array([5.0, 5.0])
d = B - A
out(A=vec(A, 0), B=vec(B, 0), d=vec(d, 0), L=float(np.linalg.norm(d)))
# 同一个位移从另一处出发：从 C 开出同样的位移，到达 C + d
C = np.array([6.0, 2.0])
out(C=vec(C, 0), Cd=vec(C + d, 0))
# UR5e 在实验 1.6 的起始姿态 θ = (0, −60°, 90°, −120°, −90°, 0)，末端点（wrist_3_link 原点）在基座坐标系中的位置
q0 = np.radians([0, -60, 90, -120, -90, 0])
p = ur5e().tool(q0)
out(p=vec(p, 3), p_len=float(np.linalg.norm(p)))
# 一条检测记录也是一组有次序的数（2.7 节）
rec = np.array([3.0, 12.0, 61.5, 18.0, 1.4, 2.5])
out(rec=vec(rec, 1), n=len(rec))
