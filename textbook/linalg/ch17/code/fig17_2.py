"""图 17.2.1：无差拍控制（程序 17.2.1）。位置轴每 T = 10 ms 采样，闭环特征多项式 λ²：初始误差 10 mm，两步归零（实心点）；
实际质量比设计值大 1%、5% 时，二重特征值 0 散开到 ±√δ 量级，误差要振荡几步才消失。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

T_ = 0.01
Ad = np.array([[1, T_], [0, 1]]); Bd = np.array([[T_ * T_ / 2], [T_]])
K = np.array([[1 / T_ ** 2, 1.5 / T_]])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.0), gridspec_kw={"width_ratios": [1.4, 1]})
for d, col, mk, lab in ((0.0, BLUE, "o", T("设计值（无差拍）", "nominal (deadbeat)")), (0.01, GREEN, "s", T("质量 +1%", "mass +1%")), (0.05, RED, "^", T("质量 +5%", "mass +5%"))):
    A = Ad - Bd / (1 + d) @ K
    x, e = np.array([0.01, 0.0]), []
    for k in range(9):
        e.append(1000 * x[0]); x = A @ x
    a1.plot(range(9), e, mk + "-", color=col, lw=1.4, ms=6, label=lab)
    ev = np.linalg.eigvals(A)
    a2.plot(ev.real, ev.imag, mk, color=col, ms=9)
a1.axhline(0, color=MUTED, lw=0.6)
a1.set_ylim(-0.35, 0.6)
a1.annotate(T("k = 0、1 时误差为 10 mm、约 5 mm（在图外）", "errors at k = 0, 1 are 10 mm and about 5 mm (off scale)"), xy=(1, 0.58), xytext=(2.2, 0.5), fontsize=9, color=INK, arrowprops=dict(arrowstyle="->", color=MUTED))
a1.set_xlabel(T("采样步 k", "step k")); a1.set_ylabel(T("位置误差 / mm", "position error / mm")); a1.legend(frameon=False, fontsize=9)
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.set_title(T("(a) 误差随采样步（纵轴放大）", "(a) Error per step (zoomed)"), fontsize=11)
th = np.linspace(0, 2 * np.pi, 200)
a2.plot(np.cos(th) * 0.3, np.sin(th) * 0.3, color=MUTED, lw=0.6, ls=":")
a2.axhline(0, color=MUTED, lw=0.6); a2.axvline(0, color=MUTED, lw=0.6)
a2.set_xlim(-0.35, 0.35); a2.set_ylim(-0.35, 0.35); a2.set_aspect("equal")
a2.set_title(T("(b) 闭环特征值（虚线圆半径 0.3）", "(b) Closed-loop eigenvalues (dotted r = 0.3)"), fontsize=11)
fig.tight_layout()
figure(fig, "fig17_2_1")
