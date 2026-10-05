"""9.3 节：线性映射在一组基下的矩阵——第 j 列是 T(第 j 个基向量) 的坐标。求导 D: P_3 → P_3（4×4），积分 I: P_3 → P_4（5×4）；
[T(v)] = [T][v]；D∘I 是 P_3 上的恒等，I∘D 不是。反射在标准基与“沿镜线、垂直镜线”的基下的矩阵；转置映射 M_2 → M_2 的矩阵。"""
import numpy as np

from _poly import D, I, ftex, matrix, ptex
from bookout import out, tex, vec

MD3, MI = matrix(D, 4), matrix(I, 4)
MD43 = matrix(D, 5)[:4, :]        # 求导 P_4 → P_3：4×5
out(MD=tex(MD3, 0), MI=ftex(MI))
p = np.array([2.0, -1, 3, 0])
out(p=ptex(p), pc=vec(p, 0), Dpc=vec(MD3 @ p, 0), Dp=ptex(MD3 @ p))
DI = MD43 @ MI                    # 4×4：P_3 → P_4 → P_3，应为单位矩阵
ID = matrix(I, 3) @ matrix(D, 4)[:3, :]   # 4×4：P_3 → P_2 → P_3（D 看作 P_3 → P_2，I 看作 P_2 → P_3）
out(DI=tex(DI, 0), ID=tex(ID, 0), IDp=ptex(ID @ p))
# 反射：镜线与 x 轴成 30°
t = np.radians(30)
b1, b2 = np.array([np.cos(t), np.sin(t)]), np.array([-np.sin(t), np.cos(t)])
Refl = 2 * np.outer(b1, b1) - np.eye(2)
B = np.column_stack([b1, b2])
out(Refl=tex(Refl, 4), ReflB=tex(np.linalg.solve(B, Refl @ B), 0))
# 转置 M_2 → M_2，基 E11, E12, E21, E22（按行展开为 ℝ⁴）
Tm = np.zeros((4, 4))
for j in range(4):
    E = np.zeros(4)
    E[j] = 1
    Tm[:, j] = E.reshape(2, 2).T.reshape(4)
out(Tm=tex(Tm, 0), trT=float(np.trace(Tm)), detT=float(np.linalg.det(Tm)))
