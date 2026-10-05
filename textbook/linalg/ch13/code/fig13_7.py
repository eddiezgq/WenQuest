"""图 13.7.1：二重特征值、只有一个特征向量时，幂里出现 k·λᵏ 项。采样 PD 控制，T = 0.05 s，θ₀ = 1：
临界阻尼（K_p = 100，K_d = 20，二重特征值 0.5，几何重数 1）θₖ = (1 + k)·0.5ᵏ，比单纯的 0.5ᵏ 衰减得慢；
无差拍（K_p = 400，K_d = 40，二重特征值 0，A² = 0）两步归零。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

Tt = 0.05
fig, ax = plt.subplots(figsize=(7.5, 3.8))
k = np.arange(0, 16)
for (kp, kd), c, lab in (((100, 20), GREEN, T("临界阻尼：θₖ = (1 + k)·0.5ᵏ", "critically damped: θₖ = (1 + k)·0.5ᵏ")), ((400, 40), ACC, T("无差拍：两步归零", "deadbeat: zero after two steps"))):
    A = np.array([[1, Tt], [-kp * Tt, 1 - kd * Tt]])
    x = np.array([1.0, 0]); th = [1.0]
    for _ in range(15):
        x = A @ x; th.append(x[0])
    ax.plot(k, th, "o-", color=c, ms=4, label=lab)
ax.plot(k, 0.5 ** k, "--", color=MUTED, label=T("对照：0.5ᵏ", "for comparison: 0.5ᵏ"))
ax.set_xlabel(T("采样步 k", "step k")); ax.set_ylabel("$\\theta_k$")
ax.legend(frameon=False, fontsize=10)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title(T("二重特征值的两种情形", "Two cases of a double eigenvalue"), fontsize=11)
figure(fig, "fig13_7_1")
