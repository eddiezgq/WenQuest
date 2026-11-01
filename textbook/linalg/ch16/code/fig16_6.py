"""图 16.6.1：关节伺服的状态反馈（程序 16.6.1）。(a) 从 0 转到 1 rad 的阶跃响应：连续控制、T = 5 ms 与 T = 40 ms 的数字控制（零阶保持）；
(b) 数字控制闭环矩阵 A_d − B_dK 的特征值的最大模随采样周期 T 的变化，T 超过约 63 ms 时大于 1，系统失稳。"""
import numpy as np
import scipy.linalg as sl

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

J, b = 0.01, 0.1
A = np.array([[0.0, 1], [0, -b / J]]); B = np.array([[0.0], [1 / J]])
K = np.array([[8.0, 0.3]])


def zoh(Ts):
    Mb = np.zeros((3, 3)); Mb[:2, :2], Mb[:2, 2:] = A, B
    E = sl.expm(Mb * Ts)
    return E[:2, :2], E[:2, 2:]


fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.0))
xr = np.array([1.0, 0])
tc = np.linspace(0, 0.4, 400)
Acl = A - B @ K
a1.plot(tc, [(sl.expm(Acl * t) @ (-xr) + xr)[0] for t in tc], color=INK, lw=2, label=T("连续控制", "continuous"))
for Ts, col in ((0.005, BLUE), (0.04, RED)):
    Ad, Bd = zoh(Ts)
    x, th, tt = np.zeros(2), [], []
    for k in range(int(0.4 / Ts) + 1):
        th.append(x[0]); tt.append(k * Ts)
        x = Ad @ x + (Bd @ (-K @ (x - xr)))
    a1.step(tt, th, where="post", color=col, lw=1.4, label=T(f"数字控制 T = {Ts * 1000:.0f} ms", f"digital T = {Ts * 1000:.0f} ms"))
a1.axhline(1, color=MUTED, lw=0.6, ls=":")
a1.set_xlabel(T("t / s", "t / s")); a1.set_ylabel(T("θ / rad", "θ / rad")); a1.legend(frameon=False, fontsize=9, loc="lower right")
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.set_title(T("(a) 阶跃响应", "(a) Step response"), fontsize=11)
Ts = np.linspace(0.001, 0.09, 300)
rho = [max(abs(np.linalg.eigvals(zoh(t)[0] - zoh(t)[1] @ K))) for t in Ts]
a2.plot(1000 * Ts, rho, color=BLUE, lw=2)
a2.axhline(1, color=RED, lw=1)
a2.plot(1000 * Ts, np.exp(-20 * Ts), color=MUTED, lw=1.2, ls="--", label=T("连续极点映射 |e^(λT)| = e^(−20T)", "continuous poles mapped |e^(λT)| = e^(−20T)"))
a2.set_xlabel(T("采样周期 T / ms", "sampling period T / ms")); a2.set_ylabel(T("闭环特征值的最大模", "largest closed-loop |eigenvalue|"))
a2.legend(frameon=False, fontsize=9, loc="upper left")
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
a2.set_title(T("(b) 采样周期与稳定性", "(b) Sampling period and stability"), fontsize=11)
fig.tight_layout()
figure(fig, "fig16_6_1")
