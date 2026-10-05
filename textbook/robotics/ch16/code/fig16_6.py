"""16.6 节的示意图。

图 16.6.1：平面 2R 臂的各向同性。(a) L1 = √2 L2、θ2 = 135°：两列 j1 = ẑ × p、j2 = ẑ × (p − p_e) 互相垂直、长度相等，
           末端三角形在末端处为直角，速度椭圆是圆；(b) 不同长度比 λ = L2/L1 下条件数随 θ2 的变化：只有 λ = 1/√2 能降到 1。
图 16.6.2：(a) 全局条件指标 GCI 随 λ 的变化（总长 0.817 m），最优 λ = 1/√2，本书 2R 臂（0.425、0.392 m）也标出；
           (b) UR5e 法兰盘竖直朝下时，过 θ* 的竖直半平面 (ρ, z) 上姿态保持线速度椭球的局部条件指标 1/κ，θ* 处的手臂与最灵巧处。
"""
import math

import numpy as np

from _fig16 import C, arm_pts, base_mark, draw_arm, plane, ur_chain
from _jac import D4, TH_STAR, held_ellipsoid, jac_2r, svals, ur_down, ur_fk
from bookout import T, figure, style

plt = style()


def kap(J):
    s = svals(J)
    return s[0] / s[-1]


# ---------------------------------------------------------------- 图 16.6.1
fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.6), gridspec_kw={"width_ratios": [1.0, 1.1]})
ax = axs[0]
L2 = 0.3
L1 = math.sqrt(2) * L2
th = np.radians([20, 135])
pts = arm_pts(th, (L1, L2))
plane(ax, (-0.12, 0.62), (-0.08, 0.62))
base_mark(ax)
draw_arm(ax, pts, C["z"], lw=6)
p, pe = pts[2], pts[1]
ax.plot([0, p[0]], [0, p[1]], color=C["muted"], lw=1.0, ls="--")
J = jac_2r(th, (L1, L2))
for k, (col, nm) in enumerate(((C["x"], r"$j_1 = \hat z\times p$"), (C["y"], r"$j_2 = \hat z\times(p - p_e)$"))):
    d = J[:, k] * 0.5
    ax.annotate("", xy=p + d, xytext=p, arrowprops=dict(arrowstyle="-|>", color=col, lw=2.0, mutation_scale=12))
    ax.text(*(p + d * 1.12 + (np.array([-0.06, 0.015]) if k == 0 else np.array([-0.2, -0.05]))), nm, fontsize=10, color=col)
t = np.linspace(0, 2 * math.pi, 200)
U, s, _ = np.linalg.svd(J)
E = U @ np.diag(s) @ np.vstack([np.cos(t), np.sin(t)]) * 0.5
ax.plot(p[0] + E[0], p[1] + E[1], color=C["accent"], lw=1.8)
# 末端处的直角
u1 = -p / np.linalg.norm(p)
u2 = (pe - p) / np.linalg.norm(pe - p)
q = p + 0.03 * u1
ax.plot([q[0], q[0] + 0.03 * u2[0], p[0] + 0.03 * u2[0]], [q[1], q[1] + 0.03 * u2[1], p[1] + 0.03 * u2[1]], color=C["ink"], lw=0.8)
ax.text(*(pe + np.array([0.02, 0.0])), "135°", fontsize=10)
ax.text(*(pts[0] + 0.5 * (pe - pts[0]) + np.array([0.01, -0.05])), r"$L_1 = \sqrt{2}\,L_2$", fontsize=10)
ax.text(*(pe + 0.5 * (p - pe) + np.array([0.02, 0.0])), r"$L_2$", fontsize=10)
ax.text(-0.11, 0.59, T("(a) 各向同性：L₁ = √2 L₂，θ₂ = 135°，椭圆是圆", "(a) isotropic: L₁ = √2 L₂, θ₂ = 135°, the ellipse is a circle"), fontsize=10.5)
ax.text(-0.11, 0.545, T("|p| = L₂，且 p ⊥ (p − pₑ)：两列等长、互相垂直", "|p| = L₂ and p ⊥ (p − pₑ): equal, perpendicular columns"), fontsize=9, color=C["muted"])

ax = axs[1]
t2 = np.radians(np.linspace(2, 178, 400))
for lam, col, ls in ((0.5, C["muted"], ":"), (1 / math.sqrt(2), C["accent"], "-"), (0.392 / 0.425, C["z"], "-"), (1.2, C["x"], "--")):
    k = [kap(jac_2r([0, x], (1.0, lam))) for x in t2]
    name = {0.5: "λ = 0.5", 1.2: "λ = 1.2"}.get(lam, None)
    if name is None:
        name = "λ = 1/√2" if abs(lam - 0.7071) < 1e-3 else T("λ = 0.392/0.425（本书 2R 臂）", "λ = 0.392/0.425 (the book's 2R arm)")
    ax.plot(np.degrees(t2), k, color=col, lw=2.0, ls=ls, label=name)
ax.axhline(1, color=C["ink"], lw=0.6)
ax.set_yscale("log")
ax.set_ylim(0.9, 60)
ax.set_xlabel(T("肘角 θ₂ / (°)", "elbow angle θ₂ / (°)"))
ax.set_ylabel(T("条件数 κ（对数坐标）", "condition number κ (log scale)"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(fontsize=9, frameon=False, loc="upper center")
ax.set_title(T("(b) 只有 λ = L₂/L₁ = 1/√2 时，κ 能降到 1（θ₂ = 135°）", "(b) only λ = L₂/L₁ = 1/√2 brings κ down to 1 (θ₂ = 135°)"), fontsize=10.5, loc="left")
fig.tight_layout()
figure(fig, "fig16_6_1")
plt.close(fig)


# ---------------------------------------------------------------- 图 16.6.2
def gci(l1, l2, n=2001):
    tt = np.linspace(0, math.pi, n)
    c = np.cos(tt)
    a, b, d = l1 * l1 + l2 * l2 + 2 * l1 * l2 * c, l2 * l2 + l1 * l2 * c, l2 * l2
    tr, det = a + d, a * d - b * b
    disc = np.sqrt(np.maximum(tr * tr / 4 - det, 0))
    lci = np.sqrt(np.maximum(tr / 2 - disc, 0) / (tr / 2 + disc))
    w = np.abs(np.sin(tt))
    return float(np.trapezoid(lci * w, tt) / np.trapezoid(w, tt))


fig, axs = plt.subplots(1, 2, figsize=(11.8, 4.8), gridspec_kw={"width_ratios": [1.0, 1.15]})
ax = axs[0]
lams = np.linspace(0.15, 2.0, 300)
g = [gci(0.817 / (1 + x), 0.817 * x / (1 + x)) for x in lams]
ax.plot(lams, g, color=C["z"], lw=2.0)
ls_ = 1 / math.sqrt(2)
ax.plot(ls_, gci(0.817 / (1 + ls_), 0.817 * ls_ / (1 + ls_)), "o", color=C["accent"], ms=7)
ax.annotate(T("最优 λ = 1/√2", "best λ = 1/√2"), (ls_, gci(0.817 / (1 + ls_), 0.817 * ls_ / (1 + ls_))), xytext=(0.95, 0.445), fontsize=9.5,
            arrowprops=dict(arrowstyle="-", color=C["muted"], lw=0.7))
lo = 0.392 / 0.425
ax.plot(lo, gci(0.425, 0.392), "s", color=C["x"], ms=6)
ax.annotate(T("本书 2R 臂", "the book's 2R arm"), (lo, gci(0.425, 0.392)), xytext=(1.15, 0.36), fontsize=9.5, arrowprops=dict(arrowstyle="-", color=C["muted"], lw=0.7))
ax.set_xlabel(T("长度比 λ = L₂ / L₁（总长 0.817 m）", "length ratio λ = L₂ / L₁ (total 0.817 m)"))
ax.set_ylabel(T("全局条件指标 GCI", "global conditioning index GCI"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_title(T("(a) 平面 2R 臂的全局条件指标", "(a) global conditioning index of the planar 2R arm"), fontsize=10.5, loc="left")

ax = axs[1]
RH = np.linspace(0.14, 0.95, 109)
ZS = np.linspace(-0.45, 0.95, 141)
M = np.full((len(ZS), len(RH)), np.nan)
for i, z in enumerate(ZS):
    for j, r in enumerate(RH):
        q = ur_down(r, z)
        if q is not None:
            a, _ = held_ellipsoid(q)
            M[i, j] = a[-1] / a[0]
im = ax.imshow(M, origin="lower", extent=(RH[0], RH[-1], ZS[0], ZS[-1]), cmap="viridis", vmin=0, vmax=0.75, aspect="equal", interpolation="bilinear")
cs = ax.contour(RH, ZS, np.nan_to_num(M, nan=0.0), levels=[0.5], colors="white", linewidths=1.0)
ax.clabel(cs, fmt={0.5: "0.5"}, fontsize=8)
cb = fig.colorbar(im, ax=ax, shrink=0.85)
cb.set_label(T("局部条件指标 1/κ（姿态保持）", "local conditioning index 1/κ (orientation held)"))
p0 = ur_fk(TH_STAR)[:3, 3]
er = np.array([p0[0], p0[1], 0]) / math.hypot(p0[0], p0[1])
P = ur_chain(TH_STAR)
ax.plot(P @ er, P[:, 2], color="white", lw=3.0, solid_capstyle="round")
ax.plot(P @ er, P[:, 2], color=C["x"], lw=1.6, solid_capstyle="round")
ax.plot(math.hypot(p0[0], p0[1]), p0[2], "o", color=C["x"], ms=5)
ax.text(math.hypot(p0[0], p0[1]) + 0.02, p0[2] - 0.07, "θ*", color="white", fontsize=10)
ib = np.unravel_index(np.nanargmax(M), M.shape)
ax.plot(RH[ib[1]], ZS[ib[0]], "*", color="white", ms=11)
ax.text(RH[ib[1]] - 0.08, ZS[ib[0]] + 0.06, T("最灵巧", "most dexterous"), color="white", fontsize=9)
ax.axvline(D4, color="white", lw=0.8, ls="--")
ax.text(D4 + 0.01, 0.85, "ρ = d₄", color="white", fontsize=8.5)
ax.set_xlabel(T("到基座轴线的水平距离 ρ / m", "horizontal distance ρ from the base axis / m"))
ax.set_ylabel(T("法兰盘中心高度 z / m", "height z of the flange centre / m"))
ax.set_title(T("(b) UR5e 法兰盘朝下时的灵巧性地图", "(b) dexterity map of the UR5e, flange pointing down"), fontsize=10.5, loc="left")
ax.set_facecolor("#eeeeee")
fig.tight_layout()
figure(fig, "fig16_6_2")
plt.close(fig)
