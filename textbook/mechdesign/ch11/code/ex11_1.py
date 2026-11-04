"""11.2 S–N 曲线与疲劳极限：数字工厂材料库里的 S–N 参数。

算例 11.2.1  材料库（cae/materials.py）给每种材料三个疲劳参数：对称循环弯曲的疲劳极限 σ₋₁（光滑试样）、它对应的循环次数 N_D、
            S–N 曲线的斜率 k（巴斯坎公式 σᵏ·N = 常数）。数字工厂的疲劳程序（cae/fatigue.py）用 pyLife 的 WoehlerCurve 按这三个数
            画曲线：N < N_D 时斜率 k；N > N_D 时原始迈因纳取水平线，海巴赫修正取斜率 2k − 1。
            画出 45 钢（调质）、40Cr（调质）、6061-T6、7075-T6、HT200 五种的曲线；算 10⁵、10⁶ 次时的疲劳强度，疲劳比 σ₋₁ / R_m；
            6061-T6 在 10⁹ 次时，按海巴赫还剩多少；
图 11.2.1；另画图 11.1.1（疲劳断口的示意，不是计算结果）。
"""
import numpy as np
import pandas as pd
import pylife.materiallaws  # noqa: F401 —— 注册 .woehler

import _ch11 as H
from bookout import T, figure, out, style

IDS = [("45-QT", "#d62728"), ("40Cr-QT", "#ff7f0e"), ("7075-T6", "#2ca02c"), ("6061-T6", "#1f77b4"), ("HT200", "#7f7f7f")]
NAME_EN = {"45-QT": "1045 Q&T", "40Cr-QT": "40Cr Q&T", "7075-T6": "7075-T6", "6061-T6": "6061-T6", "HT200": "HT200 gray iron"}


def curve(m, haibach=True):
    return pd.Series({"SD": m["sigma_1"], "ND": float(m["N_D"]), "k_1": float(m["k"]),
                      "k_2": (2 * m["k"] - 1) if haibach else np.inf}).woehler


def strength_at(m, N, haibach=True):
    """N 次对应的应力幅（反过来查 S–N 曲线）"""
    return float(np.asarray(curve(m, haibach).load(np.array([float(N)])))[0])


rows = {}
for mid, _ in IDS:
    m = H.mat(mid)
    rows[mid] = dict(s1=m["sigma_1"], ND=float(m["N_D"]), k=float(m["k"]), Rm=float(m["ultimate_mpa"]),
                     s1e5=strength_at(m, 1e5), s1e6=strength_at(m, 1e6), ratio=m["sigma_1"] / m["ultimate_mpa"])
al = H.mat("6061-T6")
s_al_1e9_h = strength_at(al, 1e9)
s_al_1e10_h = strength_at(al, 1e10)
s_st_1e9_h = strength_at(H.mat("45-QT"), 1e9)
# 寿命对应力的敏感度：应力升高 10%，寿命降到几分之一（N ∝ σ^−k）
sens_steel = 1.1 ** rows["45-QT"]["k"]
sens_al = 1.1 ** rows["6061-T6"]["k"]

plt = style()
fig, ax = plt.subplots(figsize=(6.4, 3.3))
N = np.logspace(4, 10, 400)
for mid, col in IDS:
    m = H.mat(mid)
    nm = T(m["name"], NAME_EN[mid])
    sa = np.asarray(curve(m).load(N))
    ax.loglog(N[sa < m["ultimate_mpa"]], sa[sa < m["ultimate_mpa"]], color=col, lw=1.3, label=nm)     # 高于抗拉强度的部分不画
    Nr = N[N >= m["N_D"]]
    ax.loglog(Nr, np.full_like(Nr, m["sigma_1"]), color=col, lw=0.8, ls=":")
    ax.plot([m["N_D"]], [m["sigma_1"]], "o", color=col, ms=3.5)
ax.set_xlim(1e4, 1e10)
ax.set_ylim(40, 1000)
ax.set_xlabel(T("循环次数 N", "Number of cycles N"), fontsize=7.5)
ax.set_ylabel(T("应力幅 σa / MPa（对称循环，光滑试样）", "Stress amplitude σa / MPa (fully reversed, smooth)"), fontsize=7.5)
ax.text(3e5, 50, T("实线拐点后：海巴赫（斜率 2k − 1）\n点线：原始迈因纳（水平）", "after the knee — solid: Haibach (slope 2k − 1)\ndotted: original Miner (flat)"),
        fontsize=6.0, color=H.MUTED, ha="center")
ax.legend(fontsize=6.3, frameon=False, loc="upper right")
ax.tick_params(labelsize=6.5)
ax.grid(True, which="both", lw=0.3, alpha=0.4)
fig.tight_layout()
figure(fig, "fig11_2_1")

# ---------------------------------------------------------------- 图 11.1.1 断口示意
from matplotlib.patches import Circle, Wedge  # noqa: E402

fig, axs = plt.subplots(1, 2, figsize=(6.4, 3.0))
for ax, frac, ttl in ((axs[0], 0.78, T("(a) 名义应力低：扩展区大", "(a) Low nominal stress: large growth zone")),
                      (axs[1], 0.35, T("(b) 名义应力高：扩展区小", "(b) High nominal stress: small growth zone"))):
    R0 = 1.0
    disk = Circle((0, 0), R0, facecolor="#cfcfcf", edgecolor="#9a9a9a", lw=0.0, hatch="////")
    ax.add_patch(disk)
    src = np.array([0.0, -R0])
    rr = frac * 2 * R0
    wd = Wedge(src, rr, 0, 180, facecolor="#f2efe6", edgecolor="none")
    ax.add_patch(wd)
    wd.set_clip_path(disk)
    ax.add_patch(Circle((0, 0), R0, facecolor="none", edgecolor=H.INK, lw=1.2))
    for k in range(1, 8):                                  # 贝壳纹
        r = rr * k / 8
        th = np.linspace(0, np.pi, 120)
        x, y = src[0] + r * np.cos(th), src[1] + r * np.sin(th)
        m = x * x + y * y <= R0 * R0
        ax.plot(x[m], y[m], color="#8c6d31", lw=0.7)
    ax.plot([src[0]], [src[1] + 0.02], "o", color="#d62728", ms=4)
    ax.annotate(T("裂纹源", "origin"), (src[0], src[1] + 0.02), xytext=(0.55, -1.25), fontsize=6.5, arrowprops=dict(arrowstyle="-", lw=0.5))
    ax.text(0, -R0 + rr * 0.45, T("扩展区\n（贝壳纹）", "growth zone\n(beach marks)"), ha="center", fontsize=6.5)
    ax.text(0, R0 * 0.6 if frac < 0.6 else R0 * 0.75, T("最终断裂区", "final fracture"), ha="center", fontsize=6.5)
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.35, 1.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(ttl, fontsize=7.0)
fig.tight_layout()
figure(fig, "fig11_1_1")

v = {}
for mid, key in (("45-QT", "st"), ("40Cr-QT", "cr"), ("7075-T6", "a7"), ("6061-T6", "al"), ("HT200", "ci")):
    for k_, x in rows[mid].items():
        v[f"{key}_{k_}"] = x
    v[f"{key}_ratio"] = rows[mid]["ratio"] * 100
out(**v, al_1e9=s_al_1e9_h, al_1e10=s_al_1e10_h, st_1e9=s_st_1e9_h, sens_steel=sens_steel, sens_al=sens_al)
