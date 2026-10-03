"""1.3 节：四个小例子——旋转一个点、调图像亮度与模糊、四个网页的 PageRank、神经网络的一层。"""
import math

import numpy as np

from bookout import out, tex, vec

# 机器人：腕部转 30°，吸盘下零件角点的新位置（与《机器人学》4.1 节同一题）
t = math.radians(30)
R = np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])
p = np.array([0.2, 0.1])
out(R=tex(R, 4), Rp=vec(R @ p, 4))

# 图像：4×4 的小图，亮度乘一个数是数乘；左右相邻平均（模糊）是右乘一个矩阵
I = np.array([[0.1, 0.1, 0.9, 0.9], [0.1, 0.1, 0.9, 0.9], [0.9, 0.9, 0.1, 0.1], [0.9, 0.9, 0.1, 0.1]])
B = np.array([[2, 1, 0, 0], [1, 1, 1, 0], [0, 1, 1, 1], [0, 0, 1, 2]]) / 3.0
out(I=tex(I, 1), B3=tex(B * 3, 0), IB=tex(I @ B, 4))

# 搜索引擎：四个网页的链接，阻尼系数 0.85 的 PageRank（幂法）
links = {1: [2, 3], 2: [3], 3: [1], 4: [1, 3]}       # 网页 j 链接到哪些网页
n = 4
M = np.zeros((n, n))
for j, outs in links.items():
    for i in outs:
        M[i - 1, j - 1] = 1 / len(outs)
d = 0.85
G = d * M + (1 - d) / n * np.ones((n, n))
x = np.ones(n) / n
for k in range(100):
    x_new = G @ x
    if np.abs(x_new - x).max() < 1e-12:
        break
    x = x_new
w, V = np.linalg.eig(G)
v = np.real(V[:, np.argmin(np.abs(w - 1))])
v = v / v.sum()
assert np.allclose(v, x, atol=1e-9)
out(M3=tex(M * 6, 0), rank=", ".join(f"{t:.4f}" for t in x), iters=k + 1, top=int(np.argmax(x)) + 1)

# 神经网络的一层：y = ReLU(Wx + b)
W = np.array([[0.5, -1.0, 0.2], [1.5, 0.3, -0.7]])
xin = np.array([1.0, 2.0, 0.5])
bias = np.array([0.1, -0.2])
z = W @ xin + bias
out(W=tex(W, 1), xin=vec(xin, 1), bias=vec(bias, 1), z=vec(z, 2), y=vec(np.maximum(z, 0), 2))
