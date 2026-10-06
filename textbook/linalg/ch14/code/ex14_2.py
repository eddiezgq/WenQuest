"""14.2 节：谱定理 A = QΛQᵀ = Σ λᵢ qᵢ qᵢᵀ。
S（14.1 节）的谱分解：三个秩 1 投影的加权和；矩阵函数：柔顺腕 K = [[4, 1], [1, 4]] 的平方根 K^{1/2} = Q Λ^{1/2} Qᵀ。
机器人：两连杆臂（l = 0.4、0.3 m，关节刚度 2000、1000 N·m/rad），姿态 (0°, 90°)：末端刚度 K_x = C⁻¹ 的谱分解给出主刚度与主方向；
沿任意方向推 10 N 的位移 = 沿两主方向分别除以主刚度再合成。"""
import numpy as np

from _arm2 import compliance
from _num import fix_sign, sci
from bookout import out, tex, vec

S = np.array([[2.0, -1, 0], [-1, 2, -1], [0, -1, 2]])
w, Q = np.linalg.eigh(S); Q = fix_sign(Q)
P = [np.outer(Q[:, i], Q[:, i]) for i in range(3)]
out(P2=tex(P[1], 4), sumP=sci(float(np.abs(sum(P) - np.eye(3)).max()) + 1e-30, 0),
    recon=sci(float(np.abs(sum(w[i] * P[i] for i in range(3)) - S).max()) + 1e-30, 0), P2P3=sci(float(np.abs(P[1] @ P[2]).max()) + 1e-30, 0))
K = np.array([[4.0, 1], [1, 4]])
wk, Qk = np.linalg.eigh(K)
Kh = Qk @ np.diag(np.sqrt(wk)) @ Qk.T
out(Kh=tex(Kh, 4), Kh2=sci(float(np.abs(Kh @ Kh - K).max()) + 1e-30, 0), Kh_eig=vec(np.sqrt(wk), 4))
# 两连杆臂的末端刚度
q1, q2 = np.radians(0), np.radians(90)
C = compliance(q1, q2, 2000.0, 1000.0)
Kx = np.linalg.inv(C)
lam, V = np.linalg.eigh(Kx); V = fix_sign(V)
ang = [float(np.degrees(np.arctan2(V[1, i], V[0, i]))) for i in range(2)]
out(Kx=tex(Kx, 0), kmin=float(lam[0]), kmax=float(lam[1]), ratio=float(lam[1] / lam[0]), v1=vec(V[:, 0], 4), v2=vec(V[:, 1], 4),
    ang1=ang[0], ang1p=ang[0] % 180, ang2=ang[1], VtV=sci(float(abs(V[:, 0] @ V[:, 1])) + 1e-30, 0))
F = np.array([0.0, -10.0])                 # 竖直向下 10 N
f = V.T @ F; d = V @ (f / lam)
out(F=vec(F, 0), fmain=vec(f, 3), d_mm=vec(1000 * d, 3), d_solve=vec(1000 * np.linalg.solve(Kx, F), 3),
    dang=float(np.degrees(np.arctan2(d[1], d[0]))))
# 公开课视频（第 22 轮）讲解三步时用到的分量：沿软轴、硬轴分到的力（N）与位移（mm），位移偏离推力的角度
out(fs=float(abs(f[0])), fh=float(abs(f[1])), ds_mm=float(1000 * abs(f[0]) / lam[0]), dh_mm=float(1000 * abs(f[1]) / lam[1]),
    dev=float(np.degrees(np.arccos(d @ F / (np.linalg.norm(d) * np.linalg.norm(F))))))
