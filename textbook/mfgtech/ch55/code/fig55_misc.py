"""第 55 章的原理图与示意图（数值取自 hub/surface.py 的函数，标“示意”的为教学用典型值）：
图 55.0.2：SH-101 那一批的检验记录（尺寸、粗糙度合格，表面硬度下降、酸洗发现烧伤）；
图 55.2.1：车削残留面积的形成（三维）；图 55.2.3：尖刀与圆弧刀尖的残留面积几何；图 55.2.6：没有振动与有振动的车削表面（三维）；
图 55.4.1：残余应力的三种成因（示意）；图 55.5.1：磨削区的热量去向（示意）；图 55.5.9：巴克豪森噪声与表层硬度（示意）；
图 55.6.4：初期磨损与粗糙度（示意）；图 55.7.2：滚压前后的粗糙度与滚压力（示意）。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

S = M.surf()
plt = style()
m20 = S.STEELS["20CrMnTi-CQ"]
G = M.errs().GRIND
de101 = S.equivalent_diameter(25, G["ds"])
ap_fast, A_fast = 0.005, 2.0                    # 55.0：赶产量——精磨横进给 0.002 → 0.005，砂轮超期未修整（磨粒磨平面积约 2%）
g0 = S.grinding_temperature(m20, G["vs"], G["vw"], ap_fast, de101, A_fast)
b0 = S.burn_state(m20, g0["theta"], g0["t_ms"])
ra0 = S.grinding_ra(g0["heq"], 2, wear_flat_pct=A_fast)

# ---- 图 55.0.2：检验记录
fig, axs = plt.subplots(1, 3, figsize=(7.6, 2.6), gridspec_kw={"wspace": 0.45})
d = [25.009, 25.011, 25.008, 25.010, 25.012, 25.009]
axs[0].plot(range(1, 7), d, "o-", color=M.ACCENT, ms=4)
for y in (25.002, 25.015):
    axs[0].axhline(y, color=M.RED, ls="--", lw=0.7)
axs[0].set_title(T("(a) 轴承位直径 Ø25 k6：合格", "(a) journal Ø25 k6: OK"), fontsize=8); axs[0].set_ylim(25.0, 25.017); axs[0].set_ylabel("mm", fontsize=7)
axs[1].bar(range(1, 7), [ra0 * f for f in (0.95, 1.02, 0.98, 1.05, 1.0, 0.97)], color=M.ACCENT, width=0.6)
axs[1].axhline(0.8, color=M.RED, ls="--", lw=0.7)
axs[1].set_title(T("(b) 粗糙度 Ra：合格", "(b) Ra: OK"), fontsize=8); axs[1].set_ylim(0, 1.0); axs[1].set_ylabel("µm", fontsize=7)
hrc = [60, 61, 52, 51, 60, 53]
axs[2].bar(range(1, 7), hrc, color=[M.GREEN if h >= 58 else M.RED for h in hrc], width=0.6)
axs[2].axhline(58, color=M.RED, ls="--", lw=0.7)
axs[2].set_ylim(40, 64); axs[2].set_title(T("(c) 表面硬度 HRC（抽检剖开、示意）：3 件偏低", "(c) surface HRC (sectioned, illustr.): 3 low"), fontsize=8)
for a in axs:
    a.set_xlabel(T("零件", "part"), fontsize=7.5); a.grid(lw=0.3, alpha=0.4); a.tick_params(labelsize=7)
figure(fig, "fig55_0_2")

# ---- 图 55.2.1：残留面积的形成（三维）
fig = plt.figure(figsize=(6.4, 3.4))
ax = fig.add_subplot(projection="3d")
f, r = 0.3, 0.8
xs = np.linspace(0, 1.2, 300)
xc = (xs % f) - f / 2
zz = r - np.sqrt(r * r - xc ** 2)
ys = np.linspace(0, 1.0, 30)
Xg, Yg = np.meshgrid(xs, ys)
ax.plot_surface(Xg, Yg, np.tile(zz, (30, 1)) * 10, cmap="copper", linewidth=0, alpha=0.95)
for k in range(5):
    c = k * f
    t = np.linspace(-math.pi / 2 - 0.2, -math.pi / 2 + 0.2, 40)
    ax.plot(c + r * np.cos(t), np.full_like(t, 1.0), (r + r * np.sin(t)) * 10, color=M.RED if k == 4 else M.MUTED, lw=1.2 if k == 4 else 0.6)
ax.text(4 * f, 1.05, 0.9, T("刀尖圆弧（每转前进 f）", "tool nose (advances f per rev)"), fontsize=7.5, color=M.RED)
ax.set_xlabel(T("进给方向 / mm", "feed / mm"), fontsize=7.5); ax.set_ylabel(T("切削速度方向", "cutting dir."), fontsize=7.5)
ax.set_zlabel(T("残留高度（×10）", "height (×10)"), fontsize=7.5); ax.view_init(26, -70); ax.tick_params(labelsize=6.5)
ax.set_box_aspect((1.2, 1.0, 0.4))
ax.set_title(T("相邻两转刀尖圆弧之间留下的“残留面积”（f、h 放大画出）", "the scallops between successive passes of the nose (exaggerated)"), fontsize=8)
figure(fig, "fig55_2_1")

# ---- 图 55.2.3：残留面积的几何
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 2.7))
f = 1.0
kr, kr2 = 60, 30
for k in range(3):
    x0 = k * f
    a1.plot([x0 - 0.0, x0 + 0.5 * f * 0, x0], [0, 0, 0], color=M.INK)
h = S.residual_height_sharp(f, kr, kr2)
pts = []
for k in range(3):
    x0 = k * f
    xa = x0 + h / math.tan(math.radians(kr2))
    pts += [(x0, 0), (xa, h)]
pts.append((3 * f, 0))
a1.fill([p[0] for p in pts] + [3 * f, 0], [p[1] for p in pts] + [-0.15, -0.15], color="#f0d9bf")
a1.plot([p[0] for p in pts], [p[1] for p in pts], color=M.INK, lw=1)
a1.annotate("", (1, -0.08), (2, -0.08), arrowprops={"arrowstyle": "<->", "lw": 0.7}); a1.text(1.5, -0.13, "f", ha="center", va="top", fontsize=9)
a1.annotate("", (2 + h / math.tan(math.radians(kr2)) + 0.05, 0), (2 + h / math.tan(math.radians(kr2)) + 0.05, h), arrowprops={"arrowstyle": "<->", "lw": 0.7})
a1.text(2 + h / math.tan(math.radians(kr2)) + 0.1, h / 2, "h", fontsize=9)
a1.text(0.05, 0.62, T(f"尖刀：h = f/(cot κr + cot κr′)\n（κr = {kr}°，κr′ = {kr2}°）", f"sharp tool: h = f/(cot κr + cot κr′)"), fontsize=7.5)
a1.set_xlim(-0.1, 3.1); a1.set_ylim(-0.3, 0.9); a1.set_aspect("equal"); a1.axis("off")
a1.set_title(T("(a) 尖刀：h 与 f 成正比", "(a) sharp tool: h ∝ f"), fontsize=8.5)
r = 1.2
xs = np.linspace(0, 3, 400)
xc = (xs % f) - f / 2
zz = r - np.sqrt(r * r - xc ** 2)
a2.fill_between(xs, -0.15, zz, color="#f0d9bf")
a2.plot(xs, zz, color=M.INK, lw=1)
t = np.linspace(math.pi * 1.25, math.pi * 1.75, 50)
a2.plot(1.5 + r * np.cos(t), r + r * np.sin(t), color=M.RED, lw=1.2)
a2.text(0.75, 0.38, T("刀尖圆弧 r", "nose radius r"), fontsize=7.5, color=M.RED, ha="center")
h2 = S.residual_height(f, r)
a2.plot([2.0, 2.6], [h2, h2], color=M.MUTED, lw=0.5)
a2.annotate("", (2.55, 0), (2.55, h2), arrowprops={"arrowstyle": "<->", "lw": 0.7}); a2.text(2.62, h2 / 2, "h", fontsize=9, va="center")
a2.text(0.05, 0.72, T("圆弧刀尖：h = r − √(r² − f²/4) ≈ f²/(8r)", "nose radius: h ≈ f²/(8r)"), fontsize=7.5)
a2.set_xlim(-0.1, 3.1); a2.set_ylim(-0.3, 0.9); a2.set_aspect("equal"); a2.axis("off")
a2.set_title(T("(b) 圆弧刀尖：h 与 f² 成正比、与 r 成反比", "(b) nose radius: h ∝ f²/r"), fontsize=8.5)
figure(fig, "fig55_2_3")

# ---- 图 55.2.6：没有振动与有振动的车削表面
fig = plt.figure(figsize=(7.4, 2.9))
for i, (wave, title) in enumerate(((0.0, T("(a) 工艺系统刚度好：只有刀尖残留", "(a) stiff system: scallops only")),
                                   (3.0, T("(b) 振动：叠加沿切削方向的振纹（3 µm）", "(b) chatter: marks along the cut (3 µm)")))):
    ax = fig.add_subplot(1, 2, i + 1, projection="3d")
    hm = S.surface_map(0.15, 0.4, vc_m_min=150, wave_um=wave, wave_mm=0.4, width=1.2, length=0.9, n=120)
    Xg, Yg = np.meshgrid(np.linspace(0, 1.2, 120), np.linspace(0, 0.9, 120))
    ax.plot_surface(Xg, Yg, hm, cmap="copper", linewidth=0, rstride=1, cstride=1)
    ax.set_zlim(-9, 9); ax.view_init(36, -58); ax.set_axis_off(); ax.set_box_aspect((1.2, 0.9, 0.35))
    ax.set_title(title, fontsize=8)
figure(fig, "fig55_2_6")

# ---- 图 55.4.1：残余应力的三种成因（示意）
fig, axs = plt.subplots(1, 3, figsize=(7.6, 2.7))
titles = [T("(a) 冷态塑性变形\n表层被挤压、延展 → 压应力", "(a) cold plastic deformation\nsurface stretched → compression"),
          T("(b) 热态塑性变形\n表层受热时被压缩屈服 → 冷却后拉应力", "(b) hot plastic deformation\n→ tension after cooling"),
          T("(c) 金相组织变化\n比容变大 → 压应力，变小 → 拉应力", "(c) phase change\nvolume up → compression, down → tension")]
for a, ttl, sign, c in zip(axs, titles, (-1, 1, -1), (M.ACCENT, M.RED, M.ACCENT)):
    a.fill_between([0, 4], [-3, -3], [0, 0], color="#f0d9bf")
    a.fill_between([0, 4], [-0.6, -0.6], [0, 0], color="#f6e7e5" if sign > 0 else "#dfe8f0")
    for xa in (0.8, 2.0, 3.2):
        if sign < 0:
            a.annotate("", (xa - 0.35, -0.3), (xa + 0.35, -0.3), arrowprops={"arrowstyle": "<->", "lw": 0.8, "color": c})
        else:
            a.annotate("", (xa + 0.35, -0.3), (xa - 0.35, -0.3), arrowprops={"arrowstyle": "<->", "lw": 0.8, "color": c})
    zz = np.linspace(0, 3, 50)
    prof = sign * 1.2 * np.exp(-zz / 0.5) - sign * 0.25 * np.exp(-((zz - 1.2) / 0.6) ** 2)
    a.plot(4.6 + prof * 0.6, -zz, color=c, lw=1.3)
    a.axvline(4.6, color=M.MUTED, lw=0.5)
    a.text(4.6, 0.25, "σ", ha="center", fontsize=8)
    a.set_xlim(-0.1, 5.6); a.set_ylim(-3.1, 0.6); a.axis("off"); a.set_title(ttl, fontsize=7.5)
figure(fig, "fig55_4_1")

# ---- 图 55.5.1：磨削区的热量去向（示意）
fig, ax = plt.subplots(figsize=(6.2, 3.2))
t = np.linspace(math.pi * 1.05, math.pi * 1.95, 100)
R = 4.0
ax.fill(np.r_[R * np.cos(t), 0], np.r_[R + 0.05 + R * np.sin(t) + 0.0, 4.2], color="#b8c7d9", ec=M.INK, lw=0.8)
ax.text(0, 1.6, T("砂轮 vs", "wheel vs"), ha="center", fontsize=8)
ax.fill_between([-5, 5], [-2.5, -2.5], [0.05, 0.05], color="#f0d9bf")
ax.fill_between([-1.1, 1.1], [-0.5, -0.5], [0.05, 0.05], color=M.RED, alpha=0.35)
ax.text(-4.9, -2.2, T("工件 vw →", "work vw →"), fontsize=8)
shares = [(T(f"进入工件 ε ≈ {S.EPS_WET:.0%}", f"into the work ε ≈ {S.EPS_WET:.0%}"), (0.0, -0.4), (2.2, -1.6), M.RED),
          (T("砂轮", "wheel"), (0.3, 0.4), (2.4, 1.6), M.ACCENT),
          (T("切屑（磨屑）", "chips"), (-0.8, 0.15), (-5.1, 1.6), M.WARM),
          (T("冷却液（主要在接触区外）", "coolant (mostly outside the contact)"), (-1.6, 0.25), (-5.1, 0.7), M.GREEN)]
for lab, p0, p1, c in shares:
    ax.annotate(lab, p0, p1, fontsize=7.5, color=c, arrowprops={"arrowstyle": "<-", "lw": 0.8, "color": c})
ax.annotate("", (1.1, -0.05), (-1.1, -0.05), arrowprops={"arrowstyle": "<->", "lw": 0.6})
ax.text(0, -0.85, T("接触弧长 lc = √(ap·de)", "contact length lc = √(ap·de)"), ha="center", fontsize=7.5)
ax.set_xlim(-5.2, 5); ax.set_ylim(-2.5, 2.4); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig55_5_1")

# ---- 图 55.5.9：巴克豪森噪声与表层硬度（示意）
fig, ax = plt.subplots(figsize=(5.6, 2.8))
hv = np.linspace(450, 800, 50)
mp = 100 * (800 / hv) ** 2.2 - 60
ax.plot(hv, mp, color=M.ACCENT, lw=1.4)
ax.axvspan(450, 640, color="#f6e7e5"); ax.text(470, max(mp) * 0.9, T("回火软化：信号变强", "softened: stronger signal"), fontsize=7.5, color=M.RED)
ax.set_xlabel(T("表层显微硬度 HV", "surface microhardness HV")); ax.set_ylabel(T("巴克豪森噪声幅值（相对值，示意）", "Barkhausen noise (relative)"))
ax.grid(lw=0.3, alpha=0.5)
ax.set_title(T("硬度越低、拉应力越大，磁畴越容易翻转，噪声越强——不破坏零件就能 100% 检查", "softer, more tensile surfaces give stronger noise: 100% non-destructive"), fontsize=8)
figure(fig, "fig55_5_9")

# ---- 图 55.6.4：初期磨损量与表面粗糙度（示意）
fig, ax = plt.subplots(figsize=(5.6, 2.8))
ra = np.linspace(0.05, 3.2, 100)
for load, c, lab in ((1.0, M.ACCENT, T("轻载", "light load")), (1.8, M.RED, T("重载", "heavy load"))):
    opt = 0.3 * load
    w = load * (0.25 * (ra / opt) + 0.25 * (opt / ra)) + 0.2
    ax.plot(ra, w, color=c, lw=1.4, label=lab)
    ax.plot(opt, load * 0.5 + 0.2, "o", color=c, ms=4)
ax.set_xlabel("Ra / µm"); ax.set_ylabel(T("初期磨损量（相对值，示意）", "running-in wear (relative)"))
ax.set_ylim(0, 4); ax.grid(lw=0.3, alpha=0.5); ax.legend(fontsize=7)
ax.set_title(T("太粗：峰尖压溃快；太光：存不住油、易粘着——有一个最佳值，载荷越大越靠右", "too rough wears fast, too smooth seizes: an optimum"), fontsize=8)
figure(fig, "fig55_6_4")

# ---- 图 55.7.2：滚压前后的粗糙度（示意）
fig, ax = plt.subplots(figsize=(5.6, 2.8))
F = np.linspace(0, 3000, 60)
ra_in = 1.6
ax.plot(F, ra_in * (0.18 + 0.82 * np.exp(-F / 700)) + 0.08 * (F / 3000) ** 3, color=M.ACCENT, lw=1.4, label=T("滚压后 Ra（原始 Ra 1.6）", "Ra after rolling (from 1.6)"))
ax2 = ax.twinx()
ax2.plot(F, 1 + 0.25 * (1 - np.exp(-F / 1200)), color=M.RED, lw=1.2, ls="--", label=T("表层硬度比", "surface hardness ratio"))
ax.set_xlabel(T("滚压力 / N（示意）", "rolling force / N (illustrative)")); ax.set_ylabel("Ra / µm"); ax2.set_ylabel(T("HV表 / HV₀", "HV / HV₀"))
ax.set_ylim(0, 1.8); ax2.set_ylim(0.9, 1.4); ax.grid(lw=0.3, alpha=0.5)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, fontsize=7, loc="upper right")
ax.set_title(T("滚压把峰“压平”填进谷里：粗糙度降、表层硬化；力过大则表面起皮", "rolling flattens the peaks; too much force flakes the surface"), fontsize=8)
figure(fig, "fig55_7_2")

out(ap_fast=ap_fast, A_fast=A_fast, th0=g0["theta"], b0=b0["name"], ra0=ra0, onset20=b0["onset"])
