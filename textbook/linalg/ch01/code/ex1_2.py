"""1.2 节：差速 AGV 的轮速与车体速度——同一个 2×2 矩阵的三种看法。轮半径 r = 0.075 m，轮距 b = 0.40 m（本节取定）。"""
import numpy as np

from bookout import out, tex, vec

r, b = 0.075, 0.40
A = np.array([[r / 2, r / 2], [-r / b, r / b]])     # (v, ω) = A (ω_L, ω_R)
w1 = np.array([4.0, 4.0])
w2 = np.array([-2.0, 2.0])
w3 = np.array([3.0, 5.0])
want = np.array([0.5, 0.5])                          # 要 v = 0.5 m/s，ω = 0.5 rad/s
sol = np.linalg.solve(A, want)
out(r=r, b=b, A=tex(A, 4), a11=A[0, 0], a21=A[1, 0], a22=A[1, 1],
    y1=vec(A @ w1, 4), y2=vec(A @ w2, 4), y3=vec(A @ w3, 4), y3v=(A @ w3)[0], y3w=(A @ w3)[1],
    R3=(A @ w3)[0] / (A @ w3)[1], sol=vec(sol, 4), solL=sol[0], solR=sol[1], det=np.linalg.det(A),
    Ainv=tex(np.linalg.inv(A), 4))
