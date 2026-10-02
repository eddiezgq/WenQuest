"""11.4 节的示意图。

图 11.4.1：平面 3R 臂（0.425、0.392、0.1 m）的可达工作空间（浅）与灵巧工作空间（深）；
          灵巧区内一点可以取任意朝向（画出 8 个朝向的手臂），外缘附近一点只能取很窄的一段朝向。
图 11.4.2：(a) UR5e 法兰中心的工作空间，过基座轴线的竖直截面：灵巧（深蓝）、可达（浅蓝）、法兰朝下可达（橙色轮廓）；
          (b) SCARA 工具中心的水平可达区域（关节 1 ±140°、关节 2 ±145°）。数据算法同程序 11.4.1。
"""
import math

import numpy as np

from _ch11 import H1, SC_L1, SC_L2, scara_limits, scara_reach_xy, sphere_dirs, ur_reachable
from _fig11 import C, plane
from bookout import T, figure, style

plt = style()
L1, L2, L3 = 0.425, 0.392, 0.1


def ik3(p, phi, elbow=1):
    w = np.array(p) - L3 * np.array([math.cos(phi), math.sin(phi)])
    c2 = (w @ w - L1 ** 2 - L2 ** 2) / (2 * L1 * L2)
    if abs(c2) > 1:
        return None
    t2 = elbow * math.acos(c2)
    t1 = math.atan2(w[1], w[0]) - math.atan2(L2 * math.sin(t2), L1 + L2 * math.cos(t2))
    e = L1 * np.array([math.cos(t1), math.sin(t1)])
    return np.array([[0, 0], e, w, p])


# ---------------------------------------------------------------- 图 11.4.1
fig, ax = plt.subplots(figsize=(6.4, 6.0))
plane(ax, (-1.0, 1.0), (-1.32, 1.28))
r_out, dex_out, g0, g1 = L1 + L2 + L3, L1 + L2 - L3, L3 - abs(L1 - L2), L3 + abs(L1 - L2)
ax.add_patch(plt.Circle((0, 0), r_out, facecolor="#d6e6f5", edgecolor=C["z"], lw=1))
ax.add_patch(plt.Circle((0, 0), dex_out, facecolor="#7fb0dc", edgecolor=C["z"], lw=1))
ax.add_patch(plt.Circle((0, 0), g1, facecolor="#d6e6f5", edgecolor=C["z"], lw=0.8))
ax.add_patch(plt.Circle((0, 0), g0, facecolor="#7fb0dc", edgecolor=C["z"], lw=0.8))
pA = np.array([-0.45, 0.25])
for k in range(8):
    arm = ik3(pA, k * math.pi / 4, 1)
    if arm is not None:
        ax.plot(arm[:, 0], arm[:, 1], color=C["ink"], lw=1.4, alpha=0.55)
ax.plot(*pA, "o", color=C["x"], ms=6, zorder=5)
ax.text(pA[0] - 0.05, pA[1] + 0.06, "A", fontsize=12, color=C["x"], weight="bold", ha="right")
pB = np.array([0.6, -0.6]) * 0.86 / math.hypot(0.6, 0.6)
okphi = [ph for ph in np.linspace(-math.pi, math.pi, 721) if ik3(pB, ph) is not None]
for ph in (okphi[0], okphi[len(okphi) // 2], okphi[-1]):
    arm = ik3(pB, ph, 1)
    ax.plot(arm[:, 0], arm[:, 1], color=C["accent"], lw=1.6)
ax.plot(*pB, "o", color=C["x"], ms=6, zorder=5)
ax.text(pB[0] + 0.04, pB[1] - 0.06, "B", fontsize=12, color=C["x"], weight="bold")
ax.plot(0, 0, "s", color=C["dark"], ms=7)
for r, lab, ang in ((r_out, f"{r_out:.3f}", 100), (dex_out, f"{dex_out:.3f}", 50), (g1, f"{g1:.3f}", 30)):
    a = math.radians(ang)
    ax.annotate("", xy=(r * math.cos(a), r * math.sin(a)), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=C["dark"], lw=0.8))
    ax.text(r * math.cos(a) * 1.02, r * math.sin(a) * 1.02 + 0.02, lab + " m", fontsize=9, color=C["dark"])
ax.text(-0.98, -1.25, T("浅蓝：可达工作空间（末端能到）\n深蓝：灵巧工作空间（能以任意朝向到达）",
                        "light: reachable workspace (the tip gets there)\ndark: dexterous workspace (in every orientation)"), fontsize=9.5)
ax.text(-0.98, 1.06, T("A：灵巧区内，8 个朝向都行\nB：外缘附近，只有一小段朝向",
                     "A: inside, all 8 orientations work\nB: near the rim, only a narrow range"), fontsize=9.5, color=C["ink"])
figure(fig, "fig11_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 11.4.2
h = 0.02
rho = np.arange(h / 2, 1.06, h)
zz = np.arange(-0.88, 1.16, h) + h / 2
RR, ZZ = np.meshgrid(rho, zz, indexing="ij")
pts = np.stack([RR.ravel(), np.zeros(RR.size), ZZ.ravel()], 1)
cnt = np.zeros(len(pts), int)
for d in sphere_dirs(100):
    cnt += ur_reachable(pts, np.repeat(d[None], len(pts), 0))
down = ur_reachable(pts, np.repeat(np.array([[0, 0, -1.0]]), len(pts), 0)).reshape(RR.shape)
cat = np.where(cnt == 100, 2, np.where(cnt > 0, 1, 0)).reshape(RR.shape)
full = np.concatenate([cat[::-1], cat], 0)                 # 左右对称地画出整个截面
dfull = np.concatenate([down[::-1], down], 0)
xs = np.concatenate([-rho[::-1], rho])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.6, 4.9), gridspec_kw=dict(width_ratios=[1.15, 1]))
from matplotlib.colors import ListedColormap
a1.imshow(full.T, origin="lower", extent=(xs[0] - h / 2, xs[-1] + h / 2, zz[0] - h / 2, zz[-1] + h / 2),
          cmap=ListedColormap(["white", "#d6e6f5", "#5b93c9"]), vmin=0, vmax=2, interpolation="nearest")
a1.contour(xs, zz, dfull.T.astype(float), levels=[0.5], colors=[C["orange"]], linewidths=1.6)
a1.axvline(0, color=C["muted"], lw=0.8, ls="--")
a1.axhline(0, color=C["dark"], lw=1.2)
a1.plot([-0.075, 0.075], [0, 0], color=C["dark"], lw=6)
a1.plot([0, 0], [0, H1], color=C["dark"], lw=4)
a1.plot([0, -0.817], [H1, H1], color=C["dark"], lw=3)
a1.set_aspect("equal")
a1.set_xlabel(T("到基座轴线的水平距离（左右对称画出）/ m", "horizontal distance from the base axis (mirrored) / m"))
a1.set_ylabel(T("高度 z / m", "height z / m"))
a1.text(-1.0, 1.0, T("深蓝：灵巧\n浅蓝：可达\n橙线内：法兰可朝下", "dark: dexterous\nlight: reachable\ninside orange: flange can face down"), fontsize=9,
        va="top", bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=2))
a1.set_title(T("(a) UR5e 法兰中心（零位手臂画在左侧）", "(a) UR5e flange centre (arm at home drawn on the left)"), fontsize=10)

lim = scara_limits()
hs = 0.004
g = np.arange(-0.65, 0.65, hs) + hs / 2
X, Y = np.meshgrid(g, g)
ok = scara_reach_xy(X, Y, lim["J1"], lim["J2"])
a2.imshow(ok, origin="lower", extent=(g[0], g[-1], g[0], g[-1]), cmap=ListedColormap(["white", "#5b93c9"]), interpolation="nearest")
tt = np.linspace(0, 2 * math.pi, 300)
rmin = math.sqrt(SC_L1 ** 2 + SC_L2 ** 2 + 2 * SC_L1 * SC_L2 * math.cos(lim["J2"][1]))
for r, ls in ((SC_L1 + SC_L2, "-"), (rmin, "--"), (abs(SC_L1 - SC_L2), ":")):
    a2.plot(r * np.cos(tt), r * np.sin(tt), color=C["dark"], lw=0.9, ls=ls)
for a in (lim["J1"][0], lim["J1"][1]):
    a2.plot([0, 0.6 * math.cos(a)], [0, 0.6 * math.sin(a)], color=C["x"], lw=1, ls="--")
a2.plot(0, 0, "s", color=C["dark"], ms=7)
a2.text(0.32, 0.5, "0.6 m", fontsize=9)
a2.text(rmin * 0.72 - 0.02, -rmin * 0.72 - 0.04, f"{rmin:.3f} m", fontsize=9, color=C["dark"])
a2.text(-0.64, 0.3, T("关节 1 ±140°\n的限位", "joint 1 limit\n±140°"), fontsize=8.5, color=C["x"],
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1), zorder=6)
a2.text(-0.62, -0.62, T("点线：L₁ − L₂ = 0.1 m（无限位时的内径）", "dotted: L₁ − L₂ = 0.1 m (inner radius without limits)"), fontsize=8.5)
a2.set_aspect("equal")
a2.set_xlabel("x / m")
a2.set_ylabel("y / m")
a2.set_title(T("(b) SCARA 工具中心的水平可达区域", "(b) SCARA tool centre: horizontal reach"), fontsize=10)
fig.subplots_adjust(wspace=0.22, left=0.07, right=0.99, top=0.93, bottom=0.11)
figure(fig, "fig11_4_2")
plt.close(fig)
