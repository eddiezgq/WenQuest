"""18.3 节：四个基本子空间的标准正交基（接算例 18.2.1）；数值秩（检测数据）；Panda 雅可比矩阵的零空间。"""
import math

import numpy as np

from _arm import panda, svd_fixed
from bookout import out, tex, vec

# 算例 18.3.1：一个秩为 2 的 4×3 矩阵
A = np.array([[1.0, 2.0, 3.0], [2.0, 1.0, 3.0], [1.0, -1.0, 0.0], [0.0, 1.0, 1.0]])
U, s, V = svd_fixed(A)
r = int(np.sum(s > max(A.shape) * np.finfo(float).eps * s[0]))
out(A=tex(A, 0), s1=s[0], s2=s[1], s3=s[2], r=r, v3=vec(V[:, 2], 4), u3=vec(U[:, 2], 4), u4=vec(U[:, 3], 4),
    Av3=np.abs(A @ V[:, 2]).max(), Atu3=np.abs(A.T @ U[:, 2]).max(), Atu4=np.abs(A.T @ U[:, 3]).max(),
    eps=np.finfo(float).eps)

# 18.3.2 节：数值秩。减速器检测：每件零件测 3 个量——两段轴肩长度 a、b 与总长 c = a + b（单位 mm）。
rng = np.random.default_rng(1810)
n = 50
a = 42.0 + 0.05 * rng.standard_normal(n)
b = 31.5 + 0.04 * rng.standard_normal(n)
c = a + b
X = np.c_[a, b, c]
Xc = X - X.mean(axis=0)                      # 中心化（第 19 章）：只看各件之间的差异
s_exact = np.linalg.svd(Xc, compute_uv=False)
meas = Xc + 0.002 * rng.standard_normal(Xc.shape)      # 量具的测量误差约 0.002 mm
s_meas = np.linalg.svd(meas, compute_uv=False)
tol_np = max(meas.shape) * np.finfo(float).eps * s_meas[0]
out(n=n, se1=s_exact[0], se2=s_exact[1], se3=s_exact[2], sm1=s_meas[0], sm2=s_meas[1], sm3=s_meas[2],
    rank_np=int(np.linalg.matrix_rank(meas)), tol_np=tol_np,
    # 量具误差 δ = 0.002 mm：纯噪声组成的 50×3 矩阵，最大奇异值约为 δ(√50 + √3)
    tol_eng=0.002 * (math.sqrt(n) + math.sqrt(3)), rank_eng=int(np.sum(s_meas > 0.002 * (math.sqrt(n) + math.sqrt(3)))),
    ratio32=s_meas[2] / s_meas[1])
_, _, Vm = svd_fixed(meas)
out(vm3=vec(Vm[:, 2], 3))

# 18.3.3 节：Panda 在“准备姿态”下的 6×7 雅可比矩阵
P = panda()
q = np.array([0, -math.pi / 4, 0, -3 * math.pi / 4, 0, math.pi / 2, math.pi / 4])
J = P.jacobian(q)
Uj, sj, Vj = svd_fixed(J)
z = Vj[:, 6]
out(pj=", ".join(f"{x:.4f}" for x in sj), pj_min=sj[-1], pj_rank=int(np.linalg.matrix_rank(J)), pz=vec(z, 4),
    pJz=np.abs(J @ z).max(), ptool=vec(P.tool(q), 4), pversion=P.version,
    # 沿零空间方向以 0.1 rad/s 的“速率”走 1 s（每步重新求零空间），末端点漂移多少
    )
qq = q.copy()
p0 = P.tool(q)
for _ in range(1000):
    zz = svd_fixed(P.jacobian(qq))[2][:, 6]
    if np.dot(zz, z) < 0:
        zz = -zz
    z = zz
    qq = qq + 0.1 * 0.001 * zz
out(drift_mm=1000 * np.linalg.norm(P.tool(qq) - p0), dq=vec(qq - q, 4), dq_deg=", ".join(f"{math.degrees(x):.2f}" for x in qq - q))
