"""1.6 节：第一段 Python 与 NumPy 程序——变量、列表、循环、函数、数组、矩阵乘法、解方程组、浮点数。"""
import numpy as np

from bookout import out

# 1. 变量与算术
a = 0.1 + 0.2
# 2. 列表与循环：三个负载产生的力矩之和
masses = [1.0, 2.0, 0.5]
total = 0.0
for m in masses:
    total = total + m * 9.80665 * 0.817
# 3. NumPy 数组：逐元素相乘与矩阵乘法
x = np.array([1.0, 2.0, 3.0])
y = np.array([4.0, 5.0, 6.0])
A = np.array([[3.0, 2.0, 1.0], [2.0, 3.0, 1.0], [1.0, 2.0, 3.0]])
# 4. 解方程组：《九章算术》方程第一题
sol = np.linalg.solve(A, np.array([39.0, 34.0, 26.0]))
out(a=repr(a), a_eq=a == 0.3, total=total, xy=str((x * y).tolist()), dot=float(x @ y), Ax=str((A @ x).tolist()),
    shape=str(A.shape), sol=str(sol.tolist()), close=bool(np.isclose(a, 0.3)))
