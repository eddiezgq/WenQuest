"""2.6 节：直线与平面的向量方程——末端直线运动；三点确定的平面；第四个点到平面的距离（平面度检查）；点到直线的距离。"""
import numpy as np

from bookout import out, vec

# 末端从 S 直线移动到 E，路径 x(t) = S + t (E − S)，0 ≤ t ≤ 1
S, E = np.array([0.652, 0.134, 0.335]), np.array([0.552, 0.334, 0.235])
dvec = E - S
out(S=vec(S, 3), E=vec(E, 3), dS=vec(dvec, 3), mid=vec(S + 0.5 * dvec, 3), dlen=float(np.linalg.norm(dvec)))
# 2.5 节的三个探测点（单位 mm）确定的平面 n·(x − P1) = 0，写成 ax + by + cz = d
P1, P2, P3 = np.array([400.0, 100.0, 50.0]), np.array([600.0, 120.0, 52.0]), np.array([450.0, 300.0, 49.0])
n = np.cross(P2 - P1, P3 - P1)
s = 1 / n[2]                                # 把 z 的系数化成 1，便于读
nn, dd = n * s, (n @ P1) * s
out(abc=vec(nn, 5), dd=float(dd), n=vec(n, 0), n3=vec(n / 3, 0), d3=float(n @ P1 / 3))
# 第四个探测点到平面的距离
P4 = np.array([550.0, 250.0, 50.5])
dist = abs(n @ (P4 - P1)) / np.linalg.norm(n)
out(P4=vec(P4, 1), dist=float(dist), dist_um=float(dist * 1e3), above=bool(n @ (P4 - P1) * np.sign(n[2]) > 0))
# 点到直线的距离：夹具上一点 K（程序中记作 O）到末端路径（直线）的距离
O = np.array([0.60, 0.25, 0.25])
dl = np.linalg.norm(np.cross(dvec, O - S)) / np.linalg.norm(dvec)
t_star = (O - S) @ dvec / (dvec @ dvec)
out(K=vec(O, 2), dline=float(dl), tstar=float(t_star), near=vec(S + t_star * dvec, 4))
# 直线与平面的交点：激光测距仪从 L0 沿方向 w 射向上述平面
L0, w = np.array([500.0, 200.0, 400.0]), np.array([0.05, 0.02, -1.0])
t = n @ (P1 - L0) / (n @ w)
out(L0=vec(L0, 0), w=vec(w, 2), thit=float(t), hit=vec(L0 + t * w, 2))
