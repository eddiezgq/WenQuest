"""图 23.6.1：UR5e 运动学标定（50 个标定位姿，噪声 0.05 mm）。(a) 另外 30 个验证位姿上的末端位置误差：标定前（灰）与标定后（红），注意纵轴为对数；
(b) 标定后验证误差的均方根随标定位姿个数 N 的变化（三种测量噪声）。"""
import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from _ur5e import NOMINAL, fk_all, jac, measure, poses, true_params

pt = true_params()


def calibrate(Q, y, rank=18, it=8):
    p = NOMINAL.copy()
    F = np.sqrt(np.mean((y - fk_all(p, Q)) ** 2))
    mu = 1e-3
    for _ in range(it):
        J = jac(p, Q)
        r = y - fk_all(p, Q)
        U, s, Vt = np.linalg.svd(J, full_matrices=False)
        dp = Vt[:rank].T @ ((s[:rank] / (s[:rank] ** 2 + mu * s[0] ** 2)) * (U[:, :rank].T @ r))
        Fn = np.sqrt(np.mean((y - fk_all(p + dp, Q)) ** 2))
        if Fn < F:
            p, F, mu = p + dp, Fn, mu / 10
        else:
            mu *= 10
    return p


Q = poses(50)
p_est = calibrate(Q, measure(pt, Q))
Qv = poses(30, seed=23064)
yv = fk_all(pt, Qv)
eb = np.linalg.norm((fk_all(NOMINAL, Qv) - yv).reshape(-1, 3), axis=1) * 1000
ea = np.linalg.norm((fk_all(p_est, Qv) - yv).reshape(-1, 3), axis=1) * 1000
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw={"width_ratios": [1.3, 1]})
x = np.arange(1, 31)
a1.bar(x - 0.2, eb, width=0.4, color=MUTED, label=T("标定前（名义 DH 参数）", "before (nominal DH)"))
a1.bar(x + 0.2, ea, width=0.4, color=RED, label=T("标定后", "after calibration"))
a1.set_yscale("log")
a1.set_ylim(5e-3, 60)
a1.set_xlabel(T("验证位姿序号", "validation pose"))
a1.set_ylabel(T("末端位置误差 / mm", "end-point error / mm"))
a1.legend(frameon=False, fontsize=8.5, loc="upper right")
a1.set_title(T("(a) 验证位姿上的位置误差", "(a) Position errors at validation poses"), fontsize=10)
Ns = [10, 15, 20, 30, 50, 80, 100]
TRIALS = 5                                            # 每个 N 取 5 组不同的位姿与噪声，取均方根的平均
for sig, col in ((1e-5, GREEN), (5e-5, RED), (2e-4, BLUE)):
    vals = []
    for N in Ns:
        e = []
        for tr in range(TRIALS):
            Qn = poses(N, seed=23070 + N + 1000 * tr)
            pn = calibrate(Qn, measure(pt, Qn, sigma=sig, seed=23080 + N + 1000 * tr))
            e.append(np.sqrt(np.mean((fk_all(pn, Qv) - yv) ** 2)) * 1000)
        vals.append(np.mean(e))
    a2.loglog(Ns, vals, "o-", color=col, label=T(f"噪声 {sig * 1000:g} mm", f"noise {sig * 1000:g} mm"))
    a2.loglog(Ns, [sig * 1000 * np.sqrt(18 / (3 * N)) for N in Ns], "--", color=col, lw=1, alpha=0.7)
a2.text(11, 0.0016, T("虚线：σ√(18/3N)", "dashed: σ√(18/3N)"), fontsize=8.5, color=MUTED)
a2.set_xlabel(T("标定位姿个数 N", "number of calibration poses N"))
a2.set_ylabel(T("验证误差的均方根 / mm", "validation RMS error / mm"))
a2.legend(frameon=False, fontsize=8.5)
a2.set_title(T("(b) 位姿个数与测量噪声的影响", "(b) Effect of pose count and noise"), fontsize=10)
for a in (a1, a2):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig23_6_1")
