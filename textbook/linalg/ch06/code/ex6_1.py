"""6.1 节：行列式的几何意义——2 阶行列式是两列张成的平行四边形的有向面积，3 阶是平行六面体的有向体积；
变换把一切面积放大 |det A| 倍；反射使行列式变号；与 2.5 节的叉积、混合积对照。"""
import numpy as np

from bookout import out, tex, vec

A = np.array([[3.0, 1.0], [1.0, 2.0]])
out(A=tex(A, 0), detA=float(np.linalg.det(A)), a1=vec(A[:, 0], 0), a2=vec(A[:, 1], 0))
# 平行四边形面积：底 × 高，与 ad − bc 比较
a1, a2 = A[:, 0], A[:, 1]
h = np.linalg.norm(a2 - (a2 @ a1) / (a1 @ a1) * a1)
out(base=float(np.linalg.norm(a1)), height=float(h), area=float(np.linalg.norm(a1) * h))
# 任一图形面积放大 |det A| 倍：单位圆 → 椭圆，面积 π → 5π
t = np.linspace(0, 2 * np.pi, 20001)
P = A @ np.vstack([np.cos(t), np.sin(t)])
shoelace = 0.5 * abs(np.sum(P[0, :-1] * P[1, 1:] - P[0, 1:] * P[1, :-1]))
out(ellipse=shoelace / np.pi)
# 交换两列（反射）：行列式变号
F = A[:, ::-1]
out(F=tex(F, 0), detF=float(np.linalg.det(F)))
# 3 阶：平行六面体的有向体积 = 混合积 a₁ · (a₂ × a₃)
B = np.array([[1.0, 1.0, 0.0], [0.0, 2.0, 1.0], [0.0, 0.0, 3.0]])
b1, b2, b3 = B[:, 0], B[:, 1], B[:, 2]
out(B=tex(B, 0), detB=float(np.linalg.det(B)), triple=float(b1 @ np.cross(b2, b3)))
