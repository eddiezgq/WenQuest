"""18.4 节的示意图。

图 18.4.1：Delta 的速度能力地图：电机转速不超过 10.47 rad/s 时，平台在任何方向都能达到的速度 v_g（式 (18.4.5)）。
           (a) z = −0.42 m 的水平截面（俯视）；(b) y = 0 的竖直截面。白色为工作空间以外。
图 18.4.2：25/305/25 mm 拾放循环。(a) 中心 (0, 0)、拾放高度 −0.45 m、沿 x 方向时，一次往返中三台电机的转速
           （每段按电机转速限制下的最大匀速走）；(b) 沿 y 方向、中心在 y = 0 时，节拍下限随中心 x 坐标和拾放高度的变化。
"""
import math

import numpy as np

from _ch18 import D_WMAX, delta_J, delta_ok, v_along, v_guaranteed
from _fig18 import C
from bookout import T, figure, style

plt = style()
plt.rcParams["axes.unicode_minus"] = True
CM = "YlGnBu"

# ---------------------------------------------------------------- 图 18.4.1
h = 0.006
gx = np.arange(-0.45, 0.45 + h / 2, h)
top = np.full((len(gx), len(gx)), np.nan)
for i, y in enumerate(gx):
    for j, x in enumerate(gx):
        p = np.array([x, y, -0.42])
        th = delta_ok(p)
        if th is not None:
            top[i, j] = v_guaranteed(delta_J(p, th))
gz = np.arange(-0.76, -0.16 + h / 2, h)
side = np.full((len(gz), len(gx)), np.nan)
for i, z in enumerate(gz):
    for j, x in enumerate(gx):
        p = np.array([x, 0.0, z])
        th = delta_ok(p)
        if th is not None:
            side[i, j] = v_guaranteed(delta_J(p, th))
vmin, vmax = 0.6, 2.35
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.8, 4.6), gridspec_kw={"width_ratios": [1.0, 1.25]})
im = a1.imshow(top, origin="lower", extent=(gx[0] - h / 2, gx[-1] + h / 2, gx[0] - h / 2, gx[-1] + h / 2), cmap=CM, vmin=vmin, vmax=vmax,
               interpolation="nearest")
a1.contour(gx, gx, np.nan_to_num(top, nan=0), levels=[1.9], colors=[C["accent"]], linewidths=1.2)
for k in range(3):
    f = 2 * math.pi * k / 3
    a1.plot(0.15 * math.cos(f), 0.15 * math.sin(f), "s", color=C["ink"], ms=5)
    a1.text(0.21 * math.cos(f) - 0.02, 0.21 * math.sin(f) - 0.02, str(k + 1), fontsize=9)
a1.plot([-0.1525, 0.1525], [0, 0], color=C["x"], lw=2.2)
a1.plot(0, 0, "o", color=C["x"], ms=4)
a1.set_aspect("equal")
a1.set_xlabel("x / m")
a1.set_ylabel("y / m")
a1.set_title(T("(a) z = −0.42 m 的水平截面", "(a) horizontal section z = −0.42 m"), fontsize=10, loc="left")
a1.text(-0.43, -0.43, T("方块：主动臂铰点；红线：305 mm 行程", "squares: arm hinges; red: the 305 mm stroke"), fontsize=8, color=C["muted"])
im2 = a2.imshow(side, origin="lower", extent=(gx[0] - h / 2, gx[-1] + h / 2, gz[0] - h / 2, gz[-1] + h / 2), cmap=CM, vmin=vmin,
                vmax=vmax, interpolation="nearest")
a2.contour(gx, gz, np.nan_to_num(side, nan=0), levels=[1.9], colors=[C["accent"]], linewidths=1.2)
a2.plot([-0.1525, -0.1525, 0.1525, 0.1525], [-0.45, -0.425, -0.425, -0.45], color=C["x"], lw=2.2)
a2.axhline(-0.42, color=C["muted"], lw=0.8, ls=":")
a2.text(-0.44, -0.41, "z = −0.42 m", fontsize=8.5, color=C["muted"])
a2.set_aspect("equal")
a2.set_xlabel("x / m")
a2.set_ylabel("z / m")
a2.set_title(T("(b) y = 0 的竖直截面，红线为拾放循环；橙线为 1.9 m/s", "(b) section y = 0, red: pick cycle; orange: 1.9 m/s"), fontsize=10, loc="left")
cb = fig.colorbar(im2, ax=[a1, a2], shrink=0.85, pad=0.02)
cb.set_label(T(r"保证速度 $v_g$ / (m/s)", r"guaranteed speed $v_g$ / (m/s)"))
cb.ax.axhline(1.9, color=C["accent"], lw=1.5)
figure(fig, "fig18_4_1")
plt.close(fig)


# ---------------------------------------------------------------- 图 18.4.2
def cycle(c, ax, zp, n=121):
    a = np.zeros(3)
    a[ax] = 0.1525
    c3 = np.array([c[0], c[1], zp])
    pts = [c3 - a, c3 - a + [0, 0, 0.025], c3 + a + [0, 0, 0.025], c3 + a]
    t0, rows = 0.0, []
    for S0, S1 in zip(pts[:-1], pts[1:]):
        L = np.linalg.norm(S1 - S0)
        d = (S1 - S0) / L
        ss = np.linspace(0, 1, n)
        Js = []
        for s in ss:
            p = S0 + s * (S1 - S0)
            th = delta_ok(p)
            if th is None:
                return None, None
            Js.append(delta_J(p, th))
        vm = min(v_along(J, d) for J in Js)
        for s, J in zip(ss, Js):
            rows.append((t0 + s * L / vm, np.linalg.solve(J, vm * d)))
        t0 += L / vm
    return t0 * 2, rows


tc, rows = cycle((0, 0), 0, -0.45)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.8, 4.2), gridspec_kw={"width_ratios": [1.15, 1.0]})
t = np.array([r[0] for r in rows])
w = np.array([r[1] for r in rows])
tt = np.r_[t, tc - t[::-1]]                      # 返回：原路倒走，转速反号
ww = np.r_[w, -w[::-1]]
for k, col in enumerate((C["x"], C["y"], C["z"])):
    a1.plot(tt * 1000, ww[:, k], color=col, lw=1.6, label=T(f"电机 {k + 1}", f"motor {k + 1}"))
for v in (D_WMAX, -D_WMAX):
    a1.axhline(v, color=C["muted"], lw=1.1, ls="--")
a1.text(5, D_WMAX + 0.4, T("转速上限 ±10.47 rad/s", "speed limit ±10.47 rad/s"), fontsize=8.5, color=C["muted"])
a1.set_xlabel(T("时间 / ms", "time / ms"))
a1.set_ylabel(T("电机转速 / (rad/s)", "motor speed / (rad/s)"))
a1.set_ylim(-13, 13)
a1.grid(alpha=0.3)
a1.legend(fontsize=8.5, frameon=False, loc="lower right", ncol=3)
a1.set_title(T(f"(a) 中心 (0, 0)、高度 −0.45 m、沿 x：一次往返 {tc * 1000:.0f} ms", f"(a) centre (0, 0), z = −0.45 m, along x: {tc * 1000:.0f} ms"),
             fontsize=10, loc="left")
cxs = np.arange(-0.12, 0.12 + 1e-9, 0.02)
zs = np.arange(-0.62, -0.38 + 1e-9, 0.02)
grid = np.full((len(zs), len(cxs)), np.nan)
for i, z in enumerate(zs):
    for j, cx in enumerate(cxs):
        tcy, _ = cycle((cx, 0.0), 1, z, n=31)
        if tcy is not None:
            grid[i, j] = tcy * 1000
im = a2.imshow(grid, origin="lower", extent=(cxs[0] - 0.01, cxs[-1] + 0.01, zs[0] - 0.01, zs[-1] + 0.01), cmap="YlOrRd", aspect="auto",
               interpolation="nearest")
cb = fig.colorbar(im, ax=a2, pad=0.02)
cb.set_label(T("节拍下限 / ms", "lower bound of the cycle time / ms"))
k = np.nanargmin(grid)
a2.plot(cxs[k % len(cxs)], zs[k // len(cxs)], "*", color=C["ink"], ms=12)
a2.set_xlabel(T("循环中心的 x 坐标 / m", "x of the cycle centre / m"))
a2.set_ylabel(T("拾放高度 z / m", "pick height z / m"))
a2.set_title(T("(b) 沿 y 方向、中心 y = 0 时的节拍下限", "(b) cycle-time bound, along y, centre y = 0"), fontsize=10, loc="left")
figure(fig, "fig18_4_2")
plt.close(fig)
