"""图 16.4.1：Go2 一条腿的三质量链（程序 16.4.1）。(a) 示意：躯干 + 髋、大腿、小腿 + 足，三根弹簧与阻尼；
(b) 三个振型（无阻尼），横向画位移；(c) 落地（初速度 −0.3 m/s，弹簧尚未受力）后躯干相对静平衡位置的位移：精确解 e^{At}u₀ 与只取第 1 模态的近似。"""
import numpy as np
import scipy.linalg as sl

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from _leg import C3, K3, MASS, chain, state_matrix
from _num import fix_sign

M, K, C = np.diag(MASS), chain(K3), chain(C3)
lam, Phi = sl.eigh(K, M)
Phi = fix_sign(Phi)
w = np.sqrt(lam)
fig = plt.figure(figsize=(12.0, 4.4))
gs = fig.add_gridspec(1, 3, width_ratios=[0.6, 1.1, 1.3])
ax = fig.add_subplot(gs[0, 0])
ys = [3.0, 2.0, 1.0]
names = [T("躯干¼ + 髋", "¼ body + hip"), T("大腿", "thigh"), T("小腿 + 足", "calf + foot")]
for y, mm, nm in zip(ys, MASS, names):
    s = 0.25 + 0.12 * mm
    ax.add_patch(plt.Rectangle((-s, y - 0.18), 2 * s, 0.36, color=BLUE, alpha=0.8))
    ax.text(0.75, y, f"{nm}\n{mm:.3f} kg", va="center", fontsize=8.5, color=INK)


def spring(ax, y0, y1, x=0.0):
    t = np.linspace(0, 1, 60)
    ax.plot(x + 0.08 * np.sin(2 * np.pi * 6 * t) * (t > 0.15) * (t < 0.85), y0 + (y1 - y0) * t, color=INK, lw=1)


for (y0, y1), k, c in zip(((2.82, 2.18), (1.82, 1.18), (0.82, 0.05)), K3, C3):
    spring(ax, y0, y1, -0.12)
    ax.plot([0.15, 0.15], [y0, y1], color=MUTED, lw=2.5, alpha=0.6)
    ax.text(-0.6, (y0 + y1) / 2, f"k={k:.0f}\nc={c:.0f}", fontsize=7.5, color=ACC, ha="right", va="center")
ax.plot([-0.6, 0.6], [0.0, 0.0], color=INK, lw=2.5)
ax.text(0, -0.3, T("地面", "ground"), ha="center", fontsize=9)
ax.set_xlim(-1.4, 1.8); ax.set_ylim(-0.5, 3.5); ax.axis("off")
ax.set_title(T("(a) 腿的三质量链", "(a) Three-mass leg chain"), fontsize=11)
ax = fig.add_subplot(gs[0, 1])
for j, col in enumerate((BLUE, GREEN, RED)):
    v = Phi[:, j] / np.abs(Phi[:, j]).max()
    x0 = 3 * j
    ax.plot([x0, x0], [0.6, 3.2], color=MUTED, lw=0.8, ls=":")
    ax.plot(x0 + 0.9 * v, ys, "o-", color=col, lw=2, ms=8)
    ax.text(x0, 3.45, f"{w[j] / 2 / np.pi:.1f} Hz", ha="center", fontsize=10, color=col)
ax.set_yticks(ys); ax.set_yticklabels([T("躯干", "body"), T("大腿", "thigh"), T("小腿", "calf")])
ax.set_xticks([0, 3, 6]); ax.set_xticklabels([T("振型 1", "mode 1"), T("振型 2", "mode 2"), T("振型 3", "mode 3")])
ax.set_ylim(0.6, 3.7); ax.set_xlim(-1.2, 7.2)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title(T("(b) 振型（竖直位移横向画出）", "(b) Mode shapes (vertical motion drawn sideways)"), fontsize=11)
ax = fig.add_subplot(gs[0, 2])
A = state_matrix(M, K, C)
q0 = np.linalg.solve(K, M @ np.full(3, 9.81))           # 触地瞬间弹簧未受力：在静平衡位置上方
u0 = np.r_[q0, -0.3 * np.ones(3)]
ts = np.linspace(0, 1.0, 1001)
qb = np.array([(sl.expm(A * t) @ u0)[0] for t in ts])
ax.plot(ts, 1000 * qb, color=INK, lw=2, label=T("精确解 e^(At)u₀", "exact e^(At)u₀"))
ev = np.linalg.eigvals(A); ev = ev[ev.imag > 0]; ev = ev[np.argsort(np.abs(ev))]
s1 = ev[0]
e0, ed = (Phi.T @ M @ u0[:3])[0], (Phi.T @ M @ u0[3:])[0]
wd = s1.imag
approx = Phi[0, 0] * np.exp(s1.real * ts) * (e0 * np.cos(wd * ts) + (ed - s1.real * e0) / wd * np.sin(wd * ts))
ax.plot(ts, 1000 * approx, color=BLUE, lw=1.4, ls="--", label=T("只取第 1 模态", "mode 1 only"))
ax.axhline(0, color=MUTED, lw=0.6)
ax.set_xlabel(T("t / s", "t / s")); ax.set_ylabel(T("躯干位移（相对静平衡）/ mm", "body displacement (from equilibrium) / mm"))
ax.legend(frameon=False, fontsize=9)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title(T("(c) 落地后躯干的振动", "(c) Body motion after landing"), fontsize=11)
fig.tight_layout()
figure(fig, "fig16_4_1")
