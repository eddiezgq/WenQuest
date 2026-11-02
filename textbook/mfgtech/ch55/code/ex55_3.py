"""算例 55.3.1：加工硬化（hub/surface.py hardness_profile，示意参数）。
45 钢调质（基体 HV 240）在几种条件下的显微硬度分布：锋利刀具精车、磨损刀具（后刀面磨损 VB 大，钝圆挤压）精车、大进给粗车、正常磨削；
硬化程度 N = (HV表 − HV₀)/HV₀ 与硬化层深度 h 取各加工方法的常见范围（示意）。另求离表面 0.05 mm 处的硬度。
画图 55.3.1（刃口钝圆的挤压与弹性恢复，示意）、55.3.2（表层晶粒沿切削方向被拉长，示意）、55.3.3（显微硬度分布）。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

S = M.surf()
hv0 = S.STEELS["45-QT"]["HV"]
cases = [("sharp", T("锋利刀具精车", "finish turning, sharp tool"), 0.20, 0.05, M.ACCENT),
         ("worn", T("磨损刀具精车（VB 大，钝圆挤压）", "finish turning, worn tool"), 0.50, 0.12, M.RED),
         ("rough", T("大进给粗车", "rough turning, heavy feed"), 0.40, 0.25, M.WARM),
         ("ground", T("正常磨削", "normal grinding"), 0.15, 0.03, M.GREEN)]
z = np.linspace(0, 0.4, 300)
at005 = {k: float(S.hardness_profile(hv0, n, h, np.array([0.05]))[0]) for k, _, n, h, _ in cases}
surf_hv = {k: hv0 * (1 + n) for k, _, n, _, _ in cases}

plt = style()
# ---- 图 55.3.1：刃口钝圆的挤压（直角切削，示意：刀具不动、工件向右运动）
fig, ax = plt.subplots(figsize=(6.4, 3.4))
rn, hc = 0.7, 1.6                                   # 刃口钝圆半径、切削厚度（放大画）
ax.fill([-7, 0.2, 0.2, -7], [-3.2, -3.2, hc, hc], color="#f0d9bf", lw=0)          # 刀前：待切的工件
ax.fill([0.2, 7, 7, 0.2], [-3.2, -3.2, 0.12, 0.12], color="#f0d9bf", lw=0)          # 已加工表面（弹性恢复后略高于刃口最低点）
th = np.linspace(math.pi, 1.5 * math.pi, 40)
arc = [(rn * math.cos(t), rn + rn * math.sin(t)) for t in th]
tool = [(-rn, 5.2), (-rn, rn)] + arc + [(5.5, 0.55), (5.5, 5.2)]
ax.fill(*zip(*tool), color="#e0b84f", ec=M.INK, lw=0.8)
chip = [(-rn - 0.02, hc), (-rn - 0.02, 4.8), (-2.6, 5.0), (-4.2, hc + 0.2)]
ax.fill(*zip(*chip), color="#f6e7e5", ec=M.MUTED, lw=0.6)
ax.text(-2.4, 3.3, T("切屑", "chip"), fontsize=8)
sp = (rn * math.cos(math.radians(200)), rn + rn * math.sin(math.radians(200)))
ax.plot(*sp, "o", color=M.RED, ms=4)
ax.annotate(T("分离点：以上成为切屑，以下被挤压", "separation point"), sp, (-6.8, -1.2), fontsize=7.5, color=M.RED,
            arrowprops={"arrowstyle": "->", "lw": 0.6, "color": M.RED})
ax.fill_between([0.0, 7], [-0.35, -0.35], [0.12, 0.12], color=M.ACCENT, alpha=0.35)
ax.annotate(T("被钝圆挤压、熨平的一层：通过刃口后弹性恢复、\n与后刀面摩擦——加工硬化最严重", "squeezed under the edge radius, springs back,\nrubs the flank: most work hardening"),
            (3.5, -0.1), (0.6, -2.5), fontsize=7.5, color=M.ACCENT, arrowprops={"arrowstyle": "->", "lw": 0.6, "color": M.ACCENT})
ax.annotate("", (-3.6, -2.9), (-6.6, -2.9), arrowprops={"arrowstyle": "->", "lw": 0.8})
ax.text(-5.1, -2.75, T("工件运动方向", "work motion"), fontsize=7.5, ha="center")
ax.annotate(T("刃口钝圆半径 rn", "edge radius rn"), (-0.45, 0.2), (1.2, 2.2), fontsize=7.5, arrowprops={"arrowstyle": "->", "lw": 0.6})
ax.annotate("", (-6.2, hc), (-6.2, 0.0), arrowprops={"arrowstyle": "<->", "lw": 0.6})
ax.text(-6.0, hc / 2, T("切削厚度", "uncut thickness"), fontsize=7)
ax.set_xlim(-7, 7); ax.set_ylim(-3.2, 5.3); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig55_3_1")

# ---- 图 55.3.3：显微硬度分布
fig, ax = plt.subplots(figsize=(6.0, 3.0))
for k, lab, n, h, c in cases:
    ax.plot(z, S.hardness_profile(hv0, n, h, z), color=c, lw=1.4, label=T(f"{lab}：N = {n:.0%}，h ≈ {h} mm", f"{lab}: N = {n:.0%}, h ≈ {h} mm"))
ax.axhline(hv0, color=M.MUTED, ls="--", lw=0.8); ax.text(0.33, hv0 + 4, T(f"基体 HV {hv0}", f"bulk HV {hv0}"), fontsize=7.5, color=M.MUTED)
ax.set_xlabel(T("离表面的深度 / mm", "depth below the surface / mm")); ax.set_ylabel(T("显微硬度 HV", "microhardness HV"))
ax.set_ylim(200, 400); ax.grid(lw=0.3, alpha=0.5); ax.legend(fontsize=7, loc="upper right")
ax.set_title(T("45 钢调质：HV(z) = HV₀[1 + N·e^(−3z/h)]（参数为常见范围，示意）", "45 steel Q&T: HV(z) = HV₀[1 + N·e^(−3z/h)] (illustrative)"), fontsize=8.5)
figure(fig, "fig55_3_3")

# ---- 图 55.3.2：表层晶粒被拉长（示意）
fig, ax = plt.subplots(figsize=(6.0, 2.6))
rng = np.random.default_rng(3)
for i in range(300):
    x0, y0 = rng.uniform(0, 10), rng.uniform(-4, 0)
    shear = 2.2 * math.exp(y0 / 0.8)                          # 越靠近表面，被切削方向拖得越长
    w, hgt = 0.45 * (1 + shear), 0.45 / (1 + 0.6 * shear)
    from matplotlib.patches import Ellipse
    ax.add_patch(Ellipse((x0, y0), w, hgt, angle=-12 * shear / 2.2, fc="#f0d9bf", ec="#8a6f52", lw=0.5))
ax.axhline(0, color=M.INK, lw=1.0)
ax.annotate("", (9.8, 1.15), (7.6, 1.15), arrowprops={"arrowstyle": "->", "lw": 0.8})
ax.text(8.7, 1.3, T("切削方向", "cutting direction"), fontsize=7.5, ha="center")
ax.text(0.1, -3.85, T("基体：等轴晶粒", "bulk: equiaxed grains"), fontsize=7.5, color=M.INK, bbox={"fc": "white", "ec": "none", "pad": 1})
ax.text(0.1, 0.35, T("表层：晶粒被拉长、破碎 → 硬度、强度提高，塑性下降", "surface: grains elongated, fragmented → harder"), fontsize=7.5)
ax.set_xlim(0, 10); ax.set_ylim(-4, 1.6); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig55_3_2")

out(hv0=hv0, **{f"hv005_{k}": v for k, v in at005.items()}, **{f"hvs_{k}": v for k, v in surf_hv.items()},
    N_sharp=0.20, N_worn=0.50, h_sharp=0.05, h_worn=0.12)
