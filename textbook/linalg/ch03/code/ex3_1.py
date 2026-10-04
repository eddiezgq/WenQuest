"""3.1 节：方程组的行图与列图——二元的例子；三种合金配料（三元，列图就是“用三种料凑出目标成分”）。"""
import numpy as np

from bookout import out, tex, vec

# 二元：2x − y = 1，x + y = 5
A2 = np.array([[2.0, -1.0], [1.0, 1.0]])
b2 = np.array([1.0, 5.0])
x2 = np.linalg.solve(A2, b2)
out(x2=vec(x2, 0), col1=vec(A2[:, 0], 0), col2=vec(A2[:, 1], 0))
# 三种合金料的成分（质量分数：铜、锌、锡），各取多少 kg 才能配出 100 kg 目标成分？
A = np.array([[0.80, 0.60, 0.70],
              [0.15, 0.35, 0.10],
              [0.05, 0.05, 0.20]])
b = np.array([71.0, 19.5, 9.5])            # 目标：铜 71 kg、锌 19.5 kg、锡 9.5 kg
x = np.linalg.solve(A, b)
out(A=tex(A, 2), b=vec(b, 1), x=vec(x, 0), total=float(x.sum()), resid=float(np.abs(A @ x - b).max()))
# 列图：b 是三列的组合
out(c1=vec(x[0] * A[:, 0], 1), c2=vec(x[1] * A[:, 1], 1), c3=vec(x[2] * A[:, 2], 1))
