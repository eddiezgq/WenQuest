"""图 11.2.2：正交性的损失。(a) 对 n 阶希尔伯特矩阵做正交化，‖QᵀQ − I‖ 随 n 的变化：经典格拉姆–施密特很快失去正交性，修正的好得多，
再正交化一遍（“两遍就够”）在条件数不太大（约 10⁸ 以下）时达到机器精度，豪斯霍尔德始终在机器精度；(b) IMU 陀螺积分的姿态矩阵：一阶欧拉法逐渐失去正交性，每一步重新正交化后保持在机器精度。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from _gs import cgs, cgs2, mgs, orth_err

ns = list(range(3, 14))
E = {k: [] for k in ("cgs", "mgs", "cgs2", "hh")}
for n in ns:
    H = 1.0 / (np.arange(1, n + 1)[:, None] + np.arange(1, n + 1)[None, :] - 1)
    E["cgs"].append(orth_err(cgs(H)[0])); E["mgs"].append(orth_err(mgs(H)[0]))
    E["cgs2"].append(orth_err(cgs2(H)[0])); E["hh"].append(orth_err(np.linalg.qr(H)[0]))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.0))
for k, col, mk, lab in (("cgs", RED, "o", T("经典格拉姆–施密特", "classical Gram–Schmidt")), ("mgs", ACC, "s", T("修正格拉姆–施密特", "modified Gram–Schmidt")),
                        ("cgs2", GREEN, "^", T("经典法做两遍", "classical, twice")), ("hh", BLUE, "D", T("豪斯霍尔德", "Householder"))):
    a1.semilogy(ns, np.maximum(E[k], 1e-17), mk + "-", color=col, ms=5, label=lab)
a1.set_xlabel(T("希尔伯特矩阵的阶数 n", "order n of the Hilbert matrix")); a1.set_ylabel("‖QᵀQ − I‖")
a1.legend(frameon=False, fontsize=9); a1.set_title(T("(a) 病态矩阵上的正交化", "(a) orthogonalizing an ill-conditioned matrix"), fontsize=11)


def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


omega = lambda t: np.array([0.6 * np.sin(0.7 * t), 0.4 * np.cos(0.5 * t), 0.9 + 0.3 * np.sin(1.1 * t)])
dt = 0.01
Ra, Rb = np.eye(3), np.eye(3)
ts, ea, eb = [], [], []
for k in range(6000):
    W = np.eye(3) + skew(omega(k * dt)) * dt
    Ra, Rb = Ra @ W, mgs(Rb @ W)[0]
    if (k + 1) % 50 == 0:
        ts.append((k + 1) * dt); ea.append(orth_err(Ra)); eb.append(max(orth_err(Rb), 1e-17))
a2.semilogy(ts, ea, color=RED, lw=2, label=T("一阶欧拉积分", "first-order Euler"))
a2.semilogy(ts, eb, color=BLUE, lw=2, label=T("每步重新正交化", "re-orthonormalized every step"))
a2.set_xlabel(T("时间 / s", "time / s")); a2.set_ylabel("‖RᵀR − I‖")
a2.legend(frameon=False, fontsize=9); a2.set_title(T("(b) IMU 姿态积分", "(b) integrating IMU attitude"), fontsize=11)
for a in (a1, a2):
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig11_2_2")
