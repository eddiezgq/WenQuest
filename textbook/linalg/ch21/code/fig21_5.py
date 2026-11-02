"""图 21.5.1：AGV 在五个工位之间调度的马尔可夫链。(a) 从原料库出发，第 k 次任务后 AGV 在各工位的概率，趋于平稳分布 π（虚线）；
(b) 与 π 的距离 ‖p_k − π‖₁ 按 |λ₂|ᵏ 衰减；周期链（两侧工位交替）的距离不衰减，取前 k 步的平均后才收敛。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

P = np.array([[0.0, 0.1, 0.3, 0.7, 0.5],
              [0.6, 0.0, 0.0, 0.2, 0.3],
              [0.3, 0.5, 0.0, 0.0, 0.2],
              [0.0, 0.3, 0.6, 0.0, 0.0],
              [0.1, 0.1, 0.1, 0.1, 0.0]])
w, V = np.linalg.eig(P)
o = np.argsort(-abs(w))
pi = np.abs(V[:, o[0]].real)
pi /= pi.sum()
lam2 = abs(w[o[1]])
K = 25
p = np.array([1.0, 0, 0, 0, 0])
hist = []
for k in range(K + 1):
    hist.append(p.copy())
    p = P @ p
hist = np.array(hist)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.5))
names = [T("原料库", "store"), T("机加工", "machining"), T("装配", "assembly"), T("检验", "inspection"), T("充电站", "charger")]
for i, col in enumerate((RED, GREEN, BLUE, ACC, INK)):
    a1.plot(range(K + 1), hist[:, i], "o-", color=col, ms=3, lw=1.2, label=names[i])
    a1.axhline(pi[i], color=col, lw=0.8, ls="--")
a1.set_xlabel(T("任务次数 k", "task number k"))
a1.set_ylabel(T("概率", "probability"))
a1.legend(frameon=False, fontsize=8.5, ncol=2)
a1.set_title(T("(a) p_k = Pᵏp₀，p₀ = 原料库", "(a) p_k = Pᵏp₀, starting at the store"), fontsize=10)
ks = np.arange(K + 1)
err = np.abs(hist - pi).sum(axis=1)
a2.semilogy(ks, err, "o-", color=RED, ms=3, lw=1.2, label=T("本原链：‖p_k − π‖₁", "primitive chain: ‖p_k − π‖₁"))
a2.semilogy(ks, 2 * lam2 ** ks, color=MUTED, ls="--", lw=1, label=f"∝ |λ₂|ᵏ = {lam2:.3f}ᵏ")
Pp = np.array([[0, 0.5, 0, 0.4], [0.7, 0, 0.6, 0], [0, 0.5, 0, 0.6], [0.3, 0, 0.4, 0]])
wq, Vq = np.linalg.eig(Pp)
piq = np.abs(Vq[:, np.argmin(abs(wq - 1))].real)
piq /= piq.sum()
q, acc, e1, e2 = np.array([1.0, 0, 0, 0]), np.zeros(4), [], []
for k in range(K + 1):
    acc += q
    e1.append(np.abs(q - piq).sum())
    e2.append(np.abs(acc / (k + 1) - piq).sum())
    q = Pp @ q
a2.semilogy(ks, e1, "s-", color=BLUE, ms=3, lw=1, label=T("周期链：‖p_k − π‖₁", "periodic chain: ‖p_k − π‖₁"))
a2.semilogy(ks, e2, color=GREEN, lw=1.5, label=T("周期链：前 k 步平均与 π 的距离", "periodic chain: average of first k steps"))
a2.set_xlabel(T("任务次数 k", "task number k"))
a2.set_ylim(1e-4, 3)
a2.legend(frameon=False, fontsize=8.5, loc="lower left")
a2.set_title(T("(b) 收敛快慢由第二大特征值的模决定", "(b) The rate is set by the second-largest |λ|"), fontsize=10)
for a in (a1, a2):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig21_5_1")
