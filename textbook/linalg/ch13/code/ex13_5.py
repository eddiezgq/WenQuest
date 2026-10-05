"""13.5 节：矩阵的幂与差分方程。
斐波那契数列 F_{k+1} = F_k + F_{k−1}：A = [[1, 1], [1, 0]]，λ = (1 ± √5)/2，F_k = (φᵏ − ψᵏ)/√5，F_k₊₁/F_k → φ。
人口模型（莱斯利矩阵，三个年龄组）：最大特征值是长期增长率，对应的特征向量是稳定的年龄结构。
机器人一：工作站的状态（正常 / 故障）按马尔可夫链变化，P = [[0.9, 0.4], [0.1, 0.6]]，特征值 1 与 0.5；长期可用率由 λ = 1 的特征向量给出。
机器人二：采样控制的关节（单位惯量，θ̈ = u），PD 控制 u = −K_p θ − K_d ω，周期 T = 0.05 s，前向欧拉离散化
x_{k+1} = A x_k，A = [[1, T], [−K_p T, 1 − K_d T]]；特征值的模决定收敛快慢与是否稳定。"""
import numpy as np

from _num import sci
from bookout import out, vec

# 斐波那契
A = np.array([[1, 1], [1, 0]], dtype=np.int64)
phi, psi = (1 + 5 ** 0.5) / 2, (1 - 5 ** 0.5) / 2
Fk = [0, 1]
for _ in range(40):
    Fk.append(Fk[-1] + Fk[-2])
binet = lambda k: (phi ** k - psi ** k) / 5 ** 0.5
out(phi=phi, psi=psi, F10=Fk[10], F20=Fk[20], F30=Fk[30], F40=Fk[40], binet40=float(binet(40)), round40=float(round(phi ** 40 / 5 ** 0.5)),
    ratio10=Fk[11] / Fk[10], ratio20=Fk[21] / Fk[20], A40=int(np.linalg.matrix_power(A, 40)[0, 1]))
# 莱斯利矩阵：幼年、成年、老年；只有成年、老年生育，存活率 0.5、0.8
Lm = np.array([[0.0, 1.5, 0.8], [0.5, 0, 0], [0, 0.8, 0]])
w, V = np.linalg.eig(Lm)
k = int(np.argmax(w.real)); lam = float(w[k].real); v = np.real(V[:, k]); v = v / v.sum()
x = np.array([100.0, 0, 0])
for _ in range(50):
    x = Lm @ x
out(Lm=r"\begin{pmatrix}0 & 1.5 & 0.8\\ 0.5 & 0 & 0\\ 0 & 0.8 & 0\end{pmatrix}", lamL=lam, vL=vec(v, 3), x50=vec(x / x.sum(), 3),
    others=float(np.sort(np.abs(w))[-2]), growth_pct=100 * (lam - 1), ratio50=float(np.sum(Lm @ x) / np.sum(x)))
# 马尔可夫：正常(1)、故障(2)
P = np.array([[0.9, 0.4], [0.1, 0.6]])
w, V = np.linalg.eig(P)
idx = np.argsort(-w); w, V = w[idx], V[:, idx]
s = V[:, 0] / V[:, 0].sum()
xk = np.array([1.0, 0])
hist = [xk[0]]
for _ in range(10):
    xk = P @ xk; hist.append(xk[0])
out(Peig=", ".join(f"{t:g}" for t in w), steady=vec(s, 1), av1=hist[1], av2=hist[2], av5=hist[5], av10=hist[10],
    gap10=sci(hist[10] - 0.8, 1))
# 采样 PD 控制
T = 0.05
def Amat(kp, kd):
    return np.array([[1, T], [-kp * T, 1 - kd * T]])
cases = {"a": (100.0, 10.0), "b": (100.0, 20.0), "c": (400.0, 40.0), "d": (1000.0, 10.0), "e": (100.0, 4.0)}
for key, (kp, kd) in cases.items():
    tr, de = 2 - kd * T, 1 - kd * T + kp * T * T          # λ² − tr λ + det = 0
    disc = tr * tr / 4 - de
    if disc >= -1e-12:
        r = np.sqrt(max(disc, 0.0)); ev = [tr / 2 + r, tr / 2 - r]
    else:
        ev = [complex(tr / 2, np.sqrt(-disc)), complex(tr / 2, -np.sqrt(-disc))]
    rho = float(max(abs(z) for z in ev))
    x = np.array([1.0, 0]); th = [1.0]
    for kk in range(400):
        x = Amat(kp, kd) @ x; th.append(x[0])
    th = np.abs(np.array(th))
    n10 = next((k for k in range(len(th)) if np.all(th[k:] < 0.01)), None) if th[-1] < 0.01 else None   # 从第 k 步起 |θ| 都小于 0.01
    out(**{f"kp_{key}": kp, f"kd_{key}": kd, f"rho_{key}": rho,
           f"ev_{key}": ", ".join((f"{complex(z).real:.3f}" if abs(complex(z).imag) < 1e-12 else f"{z.real:.3f} {'+' if z.imag > 0 else '-'} {abs(z.imag):.3f}\\mathrm i") for z in ev), f"tr_{key}": tr, f"e1_{key}": f"{complex(ev[0]).real:.3f}", f"det_{key}": de,
           f"n_{key}": n10 if n10 is not None else -1})
# 对照：零阶保持的精确离散模型（控制量在一个周期内保持不变）A = [[1 − K_p T²/2, T − K_d T²/2], [−K_p T, 1 − K_d T]]
def Azoh(kp, kd):
    return np.array([[1 - kp * T * T / 2, T - kd * T * T / 2], [-kp * T, 1 - kd * T]])
out(zoh_e=float(np.max(np.abs(np.linalg.eigvals(Azoh(100, 4))))), zoh_c=", ".join(f"{z.real:.1f}" for z in sorted(np.linalg.eigvals(Azoh(400, 40)).real)),
    zoh_dead=float(np.max(np.abs(np.linalg.eigvals(Azoh(1 / T ** 2, 1.5 / T))))), zoh_dead_kp=1 / T ** 2, zoh_dead_kd=1.5 / T)
