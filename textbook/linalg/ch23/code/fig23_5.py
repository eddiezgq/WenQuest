"""图 23.5.1：(a) AGV 的 UWB 定位：目标函数 Σ(dᵢ − ‖p − aᵢ‖)² 的等值线与高斯–牛顿法的迭代点（从仓库中心出发，两三步就到）；
(b) 电机冷却曲线的两指数拟合：从差的初值出发，高斯–牛顿法把 τ₂ 推成很大的负数（第二项退化为常数），停在错误的地方；
列文伯格–马夸特法收敛到正确的参数。"""
import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

rng = np.random.default_rng(23051)
anchors = np.array([[0.0, 0.0], [30.0, 0.0], [30.0, 20.0], [0.0, 20.0]])
p_true = np.array([22.0, 6.0])
d = np.linalg.norm(anchors - p_true, axis=1)
rng.normal(0, 0.05, 4)                                        # 与程序 23.5.1 相同的随机数序列
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.1, 1]})
X, Y = np.meshgrid(np.linspace(-2, 32, 240), np.linspace(-2, 22, 170))
F = sum((di - np.hypot(X - a[0], Y - a[1])) ** 2 for a, di in zip(anchors, d))
a1.contour(X, Y, np.log10(F + 1e-3), levels=18, colors=MUTED, linewidths=0.6)
p = np.array([15.0, 10.0])
pts = [p.copy()]
for _ in range(4):
    diff = p - anchors
    rr = np.linalg.norm(diff, axis=1)
    p = p + np.linalg.lstsq(diff / rr[:, None], d - rr, rcond=None)[0]
    pts.append(p.copy())
pts = np.array(pts)
a1.plot(pts[:, 0], pts[:, 1], "o-", color=RED, ms=5, lw=1.5, label=T("高斯–牛顿迭代点", "Gauss–Newton iterates"))
a1.plot(*anchors.T, "^", color=BLUE, ms=10, label=T("UWB 基站", "UWB anchors"))
a1.plot(*p_true, "*", color=INK, ms=13, label=T("AGV 真实位置", "true AGV position"))
a1.set_aspect("equal")
a1.set_xlabel("x / m")
a1.set_ylabel("y / m")
a1.legend(frameon=False, fontsize=8.5, loc="center left")
a1.set_title(T("(a) UWB 定位的高斯–牛顿迭代", "(a) Gauss–Newton for UWB positioning"), fontsize=10)
t = np.linspace(0, 1200, 121)
pt = np.array([25.0, 22.0, 35.0, 550.0])
f = lambda q, tt=t: q[0] * np.exp(-tt / q[1]) + q[2] * np.exp(-tt / q[3])
yv = f(pt) + rng.normal(0, 0.2, t.size)


def jac(q):
    e1, e2 = np.exp(-t / q[1]), np.exp(-t / q[3])
    return np.column_stack([e1, q[0] * t / q[1] ** 2 * e1, e2, q[2] * t / q[3] ** 2 * e2])


q = np.array([50.0, 5.0, 10.0, 2000.0])
for _ in range(12):
    q = q + np.linalg.lstsq(jac(q), yv - f(q), rcond=None)[0]
qg = q
q, mu, Fq = np.array([50.0, 5.0, 10.0, 2000.0]), 1e-2, None
Fq = np.sum((yv - f(q)) ** 2)
for _ in range(100):
    Jk = jac(q)
    H = Jk.T @ Jk
    dq = np.linalg.solve(H + mu * np.diag(np.diag(H)), Jk.T @ (yv - f(q)))
    Fn = np.sum((yv - f(q + dq)) ** 2)
    if Fn < Fq:
        q, Fq, mu = q + dq, Fn, mu / 3
    else:
        mu *= 4
tt = np.linspace(0, 1200, 600)
a2.plot(t, yv, ".", color=MUTED, ms=4, label=T("绕组温升的测量值", "measured winding temperature rise"))
a2.plot(tt, f(np.array([50.0, 5.0, 10.0, 2000.0]), tt), color=INK, lw=1, ls=":", label=T("初值", "initial guess"))
a2.plot(tt, f(qg, tt), color=BLUE, lw=1.5, ls="--", label=T("高斯–牛顿（停在错误处）", "Gauss–Newton (stuck)"))
a2.plot(tt, f(q, tt), color=RED, lw=1.8, label=T("列文伯格–马夸特", "Levenberg–Marquardt"))
a2.set_xlabel(T("停机后的时间 / s", "time after stop / s"))
a2.set_ylabel(T("温升 / K", "temperature rise / K"))
a2.legend(frameon=False, fontsize=8.5)
a2.set_title(T("(b) 两指数冷却曲线的拟合", "(b) Fitting a two-exponential cooling curve"), fontsize=10)
for a in (a1, a2):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig23_5_1")
