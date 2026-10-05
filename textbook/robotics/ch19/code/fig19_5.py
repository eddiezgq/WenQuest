"""19.5 节的示意图。

图 19.5.1：(a) 一个采样周期内的三种更新：欧拉法沿起始方向走 Δs，中点法沿平均方向走 Δs，圆弧精确沿平均方向走弦长；
           (b) 沿半径 0.5 m 的圆左转 90° 后的终点误差随采样周期的变化（双对数）。
图 19.5.2：系统误差：(a) 两轮半径相差 0.1% 时“直行”10 m，真实路径与里程计以为的直线；
           (b) 4 m 正方形测试，标定前逆时针、顺时针两个方向的路径（真实），标定后的路径。
图 19.5.3：随机误差：(a) 直行 10 m 后 2000 次仿真的终点（香蕉形）与线性化的 2σ 椭圆；(b) 横向、纵向标准差与航向标准差随距离的增长。
"""
import math

import numpy as np

from _fig19 import C, arrow
from _mob import diff_cart
from bookout import T, figure, style

plt = style()
P = diff_cart()
r, b = P["r"], P["b"]


def upd(q, dsR, dsL, bb, method):
    ds, dphi = (dsR + dsL) / 2, (dsR - dsL) / bb
    x, y, f = q
    if method == "euler":
        return np.array([x + ds * math.cos(f), y + ds * math.sin(f), f + dphi])
    if method == "mid":
        return np.array([x + ds * math.cos(f + dphi / 2), y + ds * math.sin(f + dphi / 2), f + dphi])
    if abs(dphi) < 1e-12:
        return np.array([x + ds * math.cos(f), y + ds * math.sin(f), f])
    return np.array([x + ds / dphi * (math.sin(f + dphi) - math.sin(f)), y - ds / dphi * (math.cos(f + dphi) - math.cos(f)), f + dphi])


# ---------------------------------------------------------------- 图 19.5.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.6))
a1.set_aspect("equal")
a1.axis("off")
ds, dphi = 1.0, 1.0
Rr = ds / dphi
t = np.linspace(0, dphi, 60)
a1.plot(Rr * np.sin(t), Rr * (1 - np.cos(t)), color=C["ink"], lw=2.0)
pe = np.array([ds, 0])
pm = ds * np.array([math.cos(dphi / 2), math.sin(dphi / 2)])
px = np.array([Rr * math.sin(dphi), Rr * (1 - math.cos(dphi))])
for p, col, nm, off in ((pe, C["red"], T("欧拉", "Euler"), (0.03, -0.08)), (pm, C["orange"], T("中点", "midpoint"), (-0.06, 0.07)),
                        (px, C["blue"], T("圆弧精确", "exact arc"), (0.05, -0.06))):
    arrow(a1, (0, 0), p, col, 1.8)
    a1.text(p[0] + off[0], p[1] + off[1], nm, color=col, fontsize=10)
a1.plot([0, 1.25], [0, 0], color=C["muted"], lw=0.6, ls=":")
tt = np.linspace(0, dphi / 2, 20)
a1.plot(0.35 * np.cos(tt), 0.35 * np.sin(tt), color=C["accent"], lw=1.0)
a1.text(0.38, 0.06, r"$\Delta\varphi/2$", color=C["accent"], fontsize=11)
a1.text(0.18, 0.5, T("真实路径：长 Δs 的圆弧", "true path: an arc of length Δs"), fontsize=9.5)
a1.text(-0.05, -0.22, T("起点，车头沿 x 轴；Δs = 1，Δφ = 1 rad（为看清，取得很大）", "start, heading along x; Δs = 1, Δφ = 1 rad (exaggerated)"),
        fontsize=9, color=C["muted"])
a1.set_xlim(-0.1, 1.4)
a1.set_ylim(-0.3, 0.75)
a1.set_title(T("(a) 一个周期内的三种更新", "(a) three updates over one period"), fontsize=10.5)
Ts = np.array([0.005, 0.01, 0.02, 0.05, 0.1, 0.2])
for m, col, nm in (("euler", C["red"], T("欧拉法", "Euler")), ("mid", C["orange"], T("中点法", "midpoint")),
                   ("exact", C["blue"], T("圆弧精确", "exact arc"))):
    e = []
    for h in Ts:
        n = int(round(math.pi / 2 / h))
        hh = math.pi / 2 / n
        q = np.zeros(3)
        for _ in range(n):
            q = upd(q, (0.5 + 0.13) * hh, (0.5 - 0.13) * hh, b, m)
        e.append(max(math.hypot(q[0] - 0.5, q[1] - 0.5), 1e-16))
    a2.loglog(Ts * 1000, np.array(e) * 1000, "o-", color=col, lw=1.4, ms=4, label=nm)
a2.set_xlabel(T("采样周期 / ms", "sampling period / ms"))
a2.set_ylabel(T("终点误差 / mm", "end error / mm"))
a2.legend(fontsize=9, frameon=False)
a2.grid(True, which="both", lw=0.3, alpha=0.5)
a2.set_title(T("(b) 半径 0.5 m、v = 0.5 m/s，左转 90°", "(b) radius 0.5 m, v = 0.5 m/s, a 90° left turn"), fontsize=10.5)
fig.subplots_adjust(wspace=0.25)
figure(fig, "fig19_5_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 19.5.2
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.8), gridspec_kw=dict(width_ratios=[1.25, 1]))
eps, D = 0.001, 10.0
kap = eps / b
s = np.linspace(0, D, 200)
a1.plot(s, np.zeros_like(s), color=C["orange"], lw=1.6, ls="--", label=T("里程计以为的路径", "path according to odometry"))
a1.plot(np.sin(kap * s) / kap, (1 - np.cos(kap * s)) / kap, color=C["blue"], lw=1.8, label=T("真实路径", "true path"))
yend = (1 - math.cos(kap * D)) / kap
a1.annotate("", xy=(math.sin(kap * D) / kap, yend), xytext=(math.sin(kap * D) / kap, 0), arrowprops=dict(arrowstyle="<->", color=C["red"]))
a1.text(9.0, yend / 2, f"{yend * 100:.1f} cm", color=C["red"], fontsize=10, ha="right")
a1.set_xlabel("x / m")
a1.set_ylabel("y / m")
a1.set_ylim(-0.05, 0.3)
a1.legend(fontsize=9, frameon=False, loc="upper left")
a1.set_title(T("(a) 两轮半径相差 0.1%，按编码器“直行”10 m", "(a) radii differ by 0.1%: 10 m “straight” by the encoders"), fontsize=10.5)
rR_t, rL_t, b_t = 0.05003, 0.04997, 0.2626


def square_path(rRc, rLc, bc, sgn, n=400):
    q = np.zeros(3)
    pts = [q[:2].copy()]
    for _ in range(4):
        thR, thL = 4.0 / rRc, 4.0 / rLc
        for _ in range(n):
            q = upd(q, rR_t * thR / n, rL_t * thL / n, b_t, "exact")
            pts.append(q[:2].copy())
        ang = sgn * math.pi / 2
        thR, thL = ang * bc / 2 / rRc, -ang * bc / 2 / rLc
        for _ in range(n // 4):
            q = upd(q, rR_t * thR / (n // 4), rL_t * thL / (n // 4), b_t, "exact")
    pts.append(q[:2].copy())
    return np.array(pts)


a2.set_aspect("equal")
sq = np.array([[0, 0], [4, 0], [4, 4], [0, 4], [0, 0]])
a2.plot(sq[:, 0], sq[:, 1], color=C["muted"], lw=0.8, ls=":")
a2.plot(sq[:, 0], -sq[:, 1], color=C["muted"], lw=0.8, ls=":")
pc = square_path(r, r, b, 1)
pw = square_path(r, r, b, -1)
a2.plot(pc[:, 0], pc[:, 1], color=C["blue"], lw=1.4, label=T("标定前，逆时针", "before, anticlockwise"))
a2.plot(pw[:, 0], pw[:, 1], color=C["red"], lw=1.4, label=T("标定前，顺时针", "before, clockwise"))
a2.plot(*pw[-1], "o", color=C["red"], ms=4)
a2.plot(*pc[-1], "o", color=C["blue"], ms=4)
a2.plot(0, 0, "s", color=C["ink"], ms=5)
a2.text(0.15, 0.25, T("起点，也是应回到的终点", "start = intended end"), fontsize=8.5)
a2.set_xlim(-0.8, 4.8)
a2.set_ylim(-4.8, 4.8)
a2.set_xlabel("x / m")
a2.set_ylabel("y / m")
a2.legend(fontsize=8.5, frameon=False, loc="center", bbox_to_anchor=(0.5, 0.68))
a2.set_title(T("(b) 4 m 正方形双向测试（标定前）", "(b) 4 m square, both directions (before calibration)"), fontsize=10.5)
fig.subplots_adjust(wspace=0.22)
figure(fig, "fig19_5_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 19.5.3
k_n, Dr, nst, M = 1e-6, 10.0, 1000, 2000
ds = Dr / nst
rng = np.random.default_rng(1905)
Q = np.zeros((M, 3))
for _ in range(nst):
    nR = rng.normal(0, math.sqrt(k_n * ds), M)
    nL = rng.normal(0, math.sqrt(k_n * ds), M)
    dsR, dsL = ds + nR, ds + nL
    dsm, dph = (dsR + dsL) / 2, (dsR - dsL) / b
    Q[:, 0] += dsm * np.cos(Q[:, 2] + dph / 2)
    Q[:, 1] += dsm * np.sin(Q[:, 2] + dph / 2)
    Q[:, 2] += dph
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.6))
a1.plot((Q[:, 0] - Dr) * 1000, Q[:, 1] * 1000, ".", ms=2, color=C["blue"], alpha=0.5)
Pxy = np.array([[k_n * Dr / 2, 0], [0, 2 * k_n * Dr ** 3 / (3 * b * b)]]) * 1e6
ev, evec = np.linalg.eigh(Pxy)
tt = np.linspace(0, 2 * math.pi, 200)
ell = evec @ np.diag(2 * np.sqrt(ev)) @ np.array([np.cos(tt), np.sin(tt)])
a1.plot(ell[0], ell[1], color=C["red"], lw=1.4, label=T("线性化的 2σ 椭圆", "linearised 2σ ellipse"))
a1.set_xlabel(T("纵向误差 x − 10 m / mm", "along-track error x − 10 m / mm"))
a1.set_ylabel(T("横向误差 y / mm", "cross-track error y / mm"))
a1.legend(fontsize=9, frameon=False, loc="upper left")
a1.set_xlim(-40, 15)
a1.set_title(T("(a) 直行 10 m 后的终点（2000 次仿真）", "(a) end points after 10 m straight (2000 runs)"), fontsize=10.5)
a1.text(-39, 250, T("横向远大于纵向，\n且两端向后弯：香蕉形", "cross-track ≫ along-track,\nends bent backwards: a banana"), fontsize=9, color=C["muted"])
Ds = np.linspace(0, 10, 100)
a2.plot(Ds, np.sqrt(2 * k_n * Ds ** 3 / (3 * b * b)) * 1000, color=C["blue"], lw=1.6, label=T("横向", "cross-track") + r" $\sigma_y \propto D^{3/2}$")
a2.plot(Ds, np.sqrt(k_n * Ds / 2) * 1000, color=C["green"], lw=1.6, label=T("纵向", "along-track") + r" $\sigma_x \propto D^{1/2}$")
a2.axhline(5, color=C["muted"], lw=0.7, ls=":")
Dl = (3 * b * b * 0.005 ** 2 / (2 * k_n)) ** (1 / 3)
a2.plot(Dl, 5, "o", color=C["red"], ms=5)
a2.annotate(r"$\sigma_y$ = 5 mm" + T("：", ": ") + f"D = {Dl:.2f} m", xy=(Dl, 5), xytext=(2.0, 30), fontsize=9,
            arrowprops=dict(arrowstyle="-", color=C["muted"], lw=0.6))
a2.set_xlabel(T("行驶距离 D / m", "distance D / m"))
a2.set_ylabel(T("标准差 / mm", "standard deviation / mm"))
a3 = a2.twinx()
a3.plot(Ds, np.degrees(np.sqrt(2 * k_n * Ds / b ** 2)), color=C["orange"], lw=1.2, ls="--", label=T("航向", "heading") + r" $\sigma_\varphi$" + T("（右轴）", " (right axis)"))
a3.set_ylabel(T("航向标准差 / (°)", "heading s.d. / (°)"), color=C["orange"])
h1, l1 = a2.get_legend_handles_labels()
h2, l2 = a3.get_legend_handles_labels()
a2.legend(h1 + h2, l1 + l2, fontsize=8.5, frameon=False, loc="upper left")
a2.set_title(T("(b) 误差随行驶距离增长（k = 10⁻⁶ m）", "(b) growth with distance (k = 10⁻⁶ m)"), fontsize=10.5)
fig.subplots_adjust(wspace=0.32)
figure(fig, "fig19_5_3")
plt.close(fig)
