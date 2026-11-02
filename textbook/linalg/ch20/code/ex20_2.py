"""20.2 节：矩阵范数。算例 20.2.1 的 1-、2-、∞-范数（公式与“试遍单位向量”比较）、弗罗贝尼乌斯范数、核范数；
两连杆机械臂（UR5e 肩、肘）在关节限速下的末端最大速度：不同的问题用不同的范数；相容性 ‖AB‖ ≤ ‖A‖‖B‖；
谱半径不超过任何算子范数，但 ‖Bᵏ‖ 可以先变大后变小。"""
import math

import numpy as np

from bookout import out, tex, vec

A = np.array([[1.0, -2.0], [3.0, 4.0]])
s = np.linalg.svd(A, compute_uv=False)
n1, ni, n2 = np.linalg.norm(A, 1), np.linalg.norm(A, np.inf), np.linalg.norm(A, 2)
nF, nN = np.linalg.norm(A, "fro"), np.linalg.norm(A, "nuc")
# “试遍”单位向量：在三种单位球的边界上取 3600 个点
t = np.linspace(0, 2 * math.pi, 3601)[:-1]
C = np.vstack([np.cos(t), np.sin(t)])
ratio = {}
for p in (1, 2, np.inf):
    X = C / np.linalg.norm(C, p, axis=0)
    ratio[p] = np.max(np.linalg.norm(A @ X, p, axis=0))
out(A=tex(A, 0), n1=float(n1), ni=float(ni), n2=float(n2), nF=float(nF), nN=float(nN), s=vec(s, 4),
    r1=float(ratio[1]), r2=float(ratio[2]), ri=float(ratio[np.inf]))
assert abs(ratio[1] - n1) < 1e-9 and abs(ratio[np.inf] - ni) < 1e-9 and abs(ratio[2] - n2) < 1e-4
# 范数之间的不等式（r = rank A）
r = 2
assert n2 <= nF <= math.sqrt(r) * n2 and nF <= nN <= math.sqrt(r) * nF
# 正交不变性：‖QAZ‖ 不变（2、F、核范数），1-范数会变
Q = np.array([[math.cos(0.7), -math.sin(0.7)], [math.sin(0.7), math.cos(0.7)]])
QA = Q @ A
out(n2Q=float(np.linalg.norm(QA, 2)), nFQ=float(np.linalg.norm(QA, "fro")), n1Q=float(np.linalg.norm(QA, 1)))

# 两连杆机械臂：θ₁ = 30°，θ₂ = 60°，每个关节最快 π rad/s（180°/s）
l1, l2 = 0.425, 0.392
t1, t2 = math.radians(30), math.radians(60)
J = np.array([[-l1 * math.sin(t1) - l2 * math.sin(t1 + t2), -l2 * math.sin(t1 + t2)],
              [l1 * math.cos(t1) + l2 * math.cos(t1 + t2), l2 * math.cos(t1 + t2)]])
w = math.pi
# (a) 每个关节各自不超过 π（“方盒”约束），末端在 x、y 方向上最快多少？—— ∞-范数（行和）
vmax_axis = w * np.sum(np.abs(J), axis=1)
# (b) 同样的方盒约束，末端合速度最快多少？—— 方盒的顶点之一（∞→2 范数）
verts = np.array([[1, 1], [1, -1], [-1, 1], [-1, -1]], float) * w
vmax_box = max(np.linalg.norm(J @ q) for q in verts)
# (c) 若约束的是两个关节速度的平方和（‖q̇‖₂ ≤ π），末端最快 π σ₁
sJ = np.linalg.svd(J, compute_uv=False)
out(J=tex(J, 4), vx=float(vmax_axis[0]), vy=float(vmax_axis[1]), Jinf=float(np.linalg.norm(J, np.inf)),
    vbox=float(vmax_box), v2=float(w * sJ[0]), sJ1=float(sJ[0]))

# 相容性：随机矩阵上验证 ‖AB‖ ≤ ‖A‖‖B‖
rng = np.random.default_rng(20)
worst = 0.0
for _ in range(2000):
    X, Y = rng.standard_normal((4, 4)), rng.standard_normal((4, 4))
    for p in (1, 2, np.inf, "fro"):
        worst = max(worst, np.linalg.norm(X @ Y, p) / (np.linalg.norm(X, p) * np.linalg.norm(Y, p)))
out(worst=float(worst))
# 谱半径与范数：B 的特征值都是 0.9，可 ‖B‖₂ > 1；‖Bᵏ‖₂ 先增大、后衰减（第 17 章的若尔当块）
B = np.array([[0.9, 1.0], [0.0, 0.9]])
rho = max(abs(np.linalg.eigvals(B)))
pk = [np.linalg.norm(np.linalg.matrix_power(B, k), 2) for k in range(0, 121)]
kmax = int(np.argmax(pk))
k_below = next(k for k in range(1, 121) if k > 5 and pk[k] < 1)
out(B=tex(B, 1), rho=float(rho), nB=float(np.linalg.norm(B, 2)), nB1=float(np.linalg.norm(B, 1)), kmax=kmax, pkmax=float(pk[kmax]),
    k_below=k_below, p20=float(pk[20]))
# 弗罗贝尼乌斯范数不是算子范数：‖I‖_F = √n
out(IF3=float(np.linalg.norm(np.eye(3), "fro")))
