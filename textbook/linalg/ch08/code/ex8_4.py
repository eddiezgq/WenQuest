"""8.4 节：行空间与左零空间——Aᵀ 的列空间与零空间；左零空间 y = (1, 1, −1) 记录了“第 3 行 = 第 1 行 + 第 2 行”，
给出相容条件 yᵀb = 0。"""
import numpy as np
import scipy.linalg as sla

from _a import A
from bookout import out, vec

y = sla.null_space(A.T)[:, 0]
y = np.rint(y / y[0])   # 化为整数向量 (1, 1, −1)，相容条件可精确检验
out(y=vec(y, 0), yA=vec(y @ A, 0))
for b in (np.array([1.0, 3, 4]), np.array([1.0, 3, 5])):
    out(**{f"yb{int(b[2])}": float(y @ b)})
# 行空间的基：简化行阶梯形的非零行；它们与零空间的向量垂直
r1, r2 = np.array([1.0, 2, 0, 1]), np.array([0.0, 0, 1, 1])
s1, s2 = np.array([-2.0, 1, 0, 0]), np.array([-1.0, 0, -1, 1])
out(dots=", ".join(f"{a @ b:.0f}" for a in (r1, r2) for b in (s1, s2)))
