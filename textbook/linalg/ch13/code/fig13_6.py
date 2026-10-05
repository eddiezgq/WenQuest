"""图 13.6.1：复特征值就是“转一下、缩一下”。采样 PD 控制（K_p = 100，K_d = 10）的 A 的特征值为 0.866 e^{±i30°}。
(a) 相平面（θ, ω）上状态沿螺线收敛，每 12 步转一周；(b) 在实特征向量基 (u, −w) 下的坐标：每步正好转 30°、缩小到 0.866 倍。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

Tt, kp, kd = 0.05, 100.0, 10.0
A = np.array([[1, Tt], [-kp * Tt, 1 - kd * Tt]])
w, V = np.linalg.eig(A)
k = int(np.argmax(w.imag)); v = V[:, k] / V[0, k]
X = np.column_stack([v.real, -v.imag])
x = np.array([1.0, 0]); xs = [x]
for _ in range(36):
    x = A @ x; xs.append(x)
xs = np.array(xs); ys = np.linalg.solve(X, xs.T).T
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.4))
for ax, pts, xl, yl in ((a1, xs, "θ", "ω"), (a2, ys, "y₁", "y₂")):
    ax.plot(pts[:, 0], pts[:, 1], "-", color=MUTED, lw=0.8)
    ax.scatter(pts[:, 0], pts[:, 1], c=np.arange(len(pts)), cmap="viridis", s=18, zorder=3)
    ax.plot(*pts[0], "o", color=RED, ms=7, zorder=4)
    ax.plot(*pts[12], "s", color=RED, ms=6, mfc="none", zorder=4)
    ax.axhline(0, color=MUTED, lw=0.6); ax.axvline(0, color=MUTED, lw=0.6)
    ax.set_xlabel(xl); ax.set_ylabel(yl)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
a1.text(xs[12, 0] + 0.05, xs[12, 1] + 0.3, T("第 12 步", "step 12"), color=RED, fontsize=9)
a1.set_title(T("(a) 相平面：沿螺线收敛", "(a) Phase plane: a converging spiral"), fontsize=11)
a2.set_aspect("equal")
t = np.linspace(0, 2 * np.pi, 200)
r0 = float(np.linalg.norm(ys[0]))
for r in (r0, r0 * 0.866 ** 6, r0 * 0.866 ** 12):
    a2.plot(r * np.cos(t), r * np.sin(t), color=MUTED, lw=0.6, ls=":")
a2.set_title(T("(b) 在基 (u, −w) 下：每步转 30°、缩小 0.866 倍", "(b) In the basis (u, −w): turn 30°, shrink 0.866× per step"), fontsize=11)
fig.tight_layout()
figure(fig, "fig13_6_1")
