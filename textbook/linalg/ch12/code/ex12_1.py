"""12.1 节：一般内积与范数。
加权内积 ⟨u, v⟩_W = uᵀWv：在点积下不垂直的两个向量，在 W 下可以正交；格拉姆矩阵；[0, 1] 上 1, x, x² 的格拉姆矩阵是希尔伯特矩阵；
矩阵的弗罗贝尼乌斯内积：对称部分与反对称部分正交；平行四边形法则对 1-范数、∞-范数不成立；极化恒等式。
机器人：平面三连杆机械臂的质量矩阵 M(q) 定义了关节速度空间的“动能内积”，两个关节速度的动能交叉项就是它们的 M-内积。"""
import numpy as np

from _arm3 import L, MASS, mass
from _frac import fmat
from bookout import out, tex, vec

# 加权内积
W = np.array([[2.0, 1], [1, 2]])
u, v = np.array([1.0, 0]), np.array([-1.0, 2])
ipW = lambda a, b: float(a @ W @ b)
out(W=tex(W, 0), dot_uv=float(u @ v), W_uv=ipW(u, v), nu2=ipW(u, u), nv2=ipW(v, v), eigW1=float(np.linalg.eigvalsh(W)[0]), eigW2=float(np.linalg.eigvalsh(W)[1]))
# 柯西–施瓦茨在 W 内积下（随机向量检验）
rng = np.random.default_rng(121)
worst = 0.0
for _ in range(10000):
    a, b = rng.normal(size=2), rng.normal(size=2)
    worst = max(worst, abs(ipW(a, b)) / np.sqrt(ipW(a, a) * ipW(b, b)))
out(cs_worst=worst)
# 格拉姆矩阵：[0, 1] 上 1, x, x² 的 ⟨x^i, x^j⟩ = 1/(i + j + 1)
G = np.array([[1 / (i + j + 1) for j in range(3)] for i in range(3)])
out(G3=fmat(G), G3eig=vec(np.linalg.eigvalsh(G), 4))
# 弗罗贝尼乌斯内积：A = S + K，⟨S, K⟩ = tr(SᵀK) = 0
A = np.array([[1.0, 2], [0, 3]])
S, K = (A + A.T) / 2, (A - A.T) / 2
fro = lambda X, Y: float(np.trace(X.T @ Y))
out(A=tex(A, 0), S=tex(S, 0), K=tex(K, 0), SK=fro(S, K), nA2=fro(A, A), nS2=fro(S, S), nK2=fro(K, K))
# 平行四边形法则
e1, e2 = np.array([1.0, 0]), np.array([0.0, 1])
for name, p in (("n1", 1), ("n2", 2), ("ninf", np.inf)):
    nn = lambda x: np.linalg.norm(x, p)
    out(**{f"{name}_lhs": float(nn(e1 + e2) ** 2 + nn(e1 - e2) ** 2), f"{name}_rhs": float(2 * (nn(e1) ** 2 + nn(e2) ** 2))})
# 机器人：动能内积
q = np.radians([30.0, 60.0, -45.0])
M = mass(q)
qa, qb = np.array([1.0, 0, 0]), np.array([0, 0, 1.0])     # 只转关节 1、只转关节 3（rad/s）
ke = lambda w: 0.5 * float(w @ M @ w)
out(L=vec(L, 2), m=vec(MASS, 1), q_deg=vec(np.degrees(q), 0), M=tex(M, 4), Meig=vec(np.linalg.eigvalsh(M), 4),
    ke_a=ke(qa), ke_b=ke(qb), ratio=ke(qa) / ke(qb), ke_ab=ke(qa + qb), M13=float(M[0, 2]), cross=ke(qa + qb) - ke(qa) - ke(qb),
    cosM=float(qa @ M @ qb / np.sqrt((qa @ M @ qa) * (qb @ M @ qb))), angM=float(np.degrees(np.arccos(qa @ M @ qb / np.sqrt((qa @ M @ qa) * (qb @ M @ qb))))))
