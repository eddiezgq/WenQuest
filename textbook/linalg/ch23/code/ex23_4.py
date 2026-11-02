"""23.4 节：约束最小二乘。
(1) 等式约束：示教得到的关节轨迹（30 个带噪声的采样点，0～2 s），用 5 次多项式拟合，要求起点、终点的位置与给定值严格相等、速度为零。
三种解法：KKT 方程组；零空间法（约束矩阵的 QR 分解，把约束消掉）；加权法（把约束当成权很大的方程）——权取 10⁴、10⁸、10¹⁴ 时
约束误差与拟合误差的变化，权太大时病态；
(2) 不等式约束：用四种回炉料配 100 kg 铜合金（3.1、20.3 节的料 A、B、C 再加一种料 D），目标成分为铜 88%、锌 3%、锡 7%、铅 2%。
四个元素给出 4 个方程，另加“总质量 100 kg”的约束。不加约束的最小二乘要用 −42 kg 的料 B（不可能）；
要求用量非负、总质量为 100 kg，用“有效集”的思想：在每一种“哪些料不用”的组合上解等式约束最小二乘，取可行解中残差最小的。"""
import itertools

import numpy as np
from scipy.linalg import qr

from _num import sci
from bookout import T, out, vec

rng = np.random.default_rng(23041)
# (1) 轨迹拟合
t = np.linspace(0, 2, 30)
s = t - 1.0                                               # 缩放到 [−1, 1]
q0, q1 = 0.2, 1.4                                         # 起点、终点位置（rad）
q_true = q0 + (q1 - q0) * (10 * (t / 2) ** 3 - 15 * (t / 2) ** 4 + 6 * (t / 2) ** 5) + 0.03 * np.sin(2 * np.pi * t / 2)
y = q_true + rng.normal(0, 0.01, t.size)
A = np.vander(s, 6, increasing=True)
# 约束：s = −1、1 处位置为 q0、q1，导数为 0
def row(sv, der):
    return np.array([0 if k < der else np.prod(range(k - der + 1, k + 1)) * sv ** (k - der) for k in range(6)], dtype=float)


Cm = np.vstack([row(-1, 0), row(1, 0), row(-1, 1), row(1, 1)])
d = np.array([q0, q1, 0.0, 0.0])
# KKT
K = np.block([[A.T @ A, Cm.T], [Cm, np.zeros((4, 4))]])
x_kkt = np.linalg.solve(K, np.concatenate([A.T @ y, d]))[:6]
# 零空间法：Cᵀ = Q R，x = Q₁ R⁻ᵀ d + Q₂ z
Qc, Rc = qr(Cm.T)
Q1, Q2 = Qc[:, :4], Qc[:, 4:]
x_p = Q1 @ np.linalg.solve(Rc[:4, :4].T, d)
z = np.linalg.lstsq(A @ Q2, y - A @ x_p, rcond=None)[0]
x_ns = x_p + Q2 @ z
assert np.allclose(x_kkt, x_ns, atol=1e-10)
fit_rms = float(np.sqrt(np.mean((A @ x_ns - y) ** 2)))
free = np.linalg.lstsq(A, y, rcond=None)[0]
out(fit_rms=fit_rms * 1000, free_rms=float(np.sqrt(np.mean((A @ free - y) ** 2))) * 1000,
    free_end=float(abs(Cm[1] @ free - q1) * 1000), free_v0=float(abs(Cm[2] @ free)), con_err=sci(float(np.max(np.abs(Cm @ x_ns - d))), 1),
    nfree=6 - 4)
for w in (1e4, 1e8, 1e14):
    Aw = np.vstack([A, w * Cm])
    xw = np.linalg.lstsq(Aw, np.concatenate([y, w * d]), rcond=None)[0]
    key = f"w{int(np.log10(w))}"
    out(**{f"{key}_con": sci(float(np.max(np.abs(Cm @ xw - d))), 1), f"{key}_diff": sci(float(np.linalg.norm(xw - x_ns)), 1),
           f"{key}_k": sci(float(np.linalg.cond(Aw)), 1)})

# (2) 配料：列为料 A、B、C、D，行为铜、锌、锡、铅的质量分数
M = np.array([[0.80, 0.60, 0.70, 0.90],
              [0.15, 0.35, 0.10, 0.02],
              [0.04, 0.04, 0.18, 0.03],
              [0.01, 0.01, 0.02, 0.05]])
target = 100 * np.array([0.88, 0.03, 0.07, 0.02])
x_ls = np.linalg.solve(M, target)
out(M=vec(M[:, 3], 2), x_ls=vec(x_ls, 1), x_ls_sum=float(x_ls.sum()))


def eq_ls(Msub, tgt, total):
    """min ‖Msub x − tgt‖，约束 Σx = total（KKT）。"""
    k = Msub.shape[1]
    Kk = np.block([[Msub.T @ Msub, np.ones((k, 1))], [np.ones((1, k)), np.zeros((1, 1))]])
    return np.linalg.solve(Kk, np.concatenate([Msub.T @ tgt, [total]]))[:k]


best = None
tried = 0
for r in range(1, 5):
    for S in itertools.combinations(range(4), r):
        xs = eq_ls(M[:, S], target, 100.0)
        tried += 1
        if np.all(xs >= -1e-12):
            x = np.zeros(4)
            x[list(S)] = xs
            resn = float(np.linalg.norm(M @ x - target))
            if best is None or resn < best[0]:
                best = (resn, x, S)
resn, xb, S = best
comp = M @ xb / 100
out(tried=tried, x_nn=vec(xb, 1), used=T("、", ", ").join("ABCD"[i] for i in S), res_nn=resn, comp=T("、", ", ").join(f"{100 * c:.2f}%" for c in comp))
# 有效集的验证：未用的料，拉格朗日乘数（梯度方向）非负——再加一点它，目标函数不会下降
g = 2 * M.T @ (M @ xb - target)
mu = g - g[list(S)].mean()                                      # 去掉总质量约束的乘数
out(kkt=", ".join(f"{(0.0 if abs(v) < 5e-4 else v):.3f}" for v in mu))
