"""32.1 节的计算：齿轮传动基础——减速器厂的 WQR-105。

(1) 算例 32.1.1：传动比、转速、转矩、效率：两级圆柱齿轮 (72/24)·(70/20)；效率按每级齿轮 0.97、每对轴承 0.99（与问渠 CAE 热分析示例同一组数）；
    输出 350 N·m 时的输入转矩、功率与损耗。
(2) 算例 32.1.2：啮合：中心距、分度圆、基圆、重合度 ε_α（标准齿轮，α = 20°，齿顶高系数 1）。
(3) 算例 32.1.3：背隙从哪里来：减速器厂零件检验的公法线长度偏差（factory/factory/data.py 的检验模板）→ 每对齿的法向侧隙 →
    圆周侧隙 → 换到输出轴的角度背隙（第一级的背隙经第二级缩小 3.5 倍）。不计中心距公差和轴承游隙。
"""
import math

import numpy as np

from _ch32 import ARCMIN, gearbox
from bookout import out

D, G = gearbox()
alpha = math.radians(20.0)
g = D.GEARS
# ---------------------------------------------------------------- (1) 传动比、效率
i1 = g["GR-202"]["z"] / g["SH-101"]["z"]
i2 = g["GR-302"]["z"] / g["GR-203"]["z"]
i = i1 * i2
assert abs(i - D.ratio()) < 1e-12 and abs(i - G["ratio"]) < 1e-12
eta = G["eta_gear"] ** G["stages"] * G["eta_bearing"] ** G["bearing_pairs"]
n_in = D.INPUT_SPEED_RPM
n_out = n_in / i
T_out = G["T_out_nm"]
T_in = T_out / (i * eta)
P_out = T_out * n_out * 2 * math.pi / 60
P_in = P_out / eta
out(i1=i1, i2=i2, i=i, eta=eta, n_in=n_in, n_out=n_out, T_out=T_out, T_in=T_in, P_out=P_out / 1000, P_in=P_in / 1000,
    loss=P_in - P_out, T_ideal=T_out / i)

# ---------------------------------------------------------------- (2) 啮合
def mesh(m, z1, z2):
    r1, r2 = m * z1 / 2, m * z2 / 2
    rb1, rb2 = r1 * math.cos(alpha), r2 * math.cos(alpha)
    ra1, ra2 = r1 + m, r2 + m
    a = r1 + r2
    eps = (math.sqrt(ra1 ** 2 - rb1 ** 2) + math.sqrt(ra2 ** 2 - rb2 ** 2) - a * math.sin(alpha)) / (math.pi * m * math.cos(alpha))
    return {"a": a, "d1": 2 * r1, "d2": 2 * r2, "db1": 2 * rb1, "db2": 2 * rb2, "eps": eps}


s1 = mesh(g["SH-101"]["m"], g["SH-101"]["z"], g["GR-202"]["z"])
s2 = mesh(g["GR-203"]["m"], g["GR-203"]["z"], g["GR-302"]["z"])
assert abs(s1["a"] - D.center_distance(2, 24, 72)) < 1e-12 and 1.2 < s1["eps"] < 2 and 1.2 < s2["eps"] < 2
out(**{f"s1_{k}": v for k, v in s1.items()}, **{f"s2_{k}": v for k, v in s2.items()})

# ---------------------------------------------------------------- (3) 背隙
# 公法线长度偏差（mm，上偏差、下偏差），与 data.inspection_templates() 里的 gear_w 调用相同
DEV = {"SH-101": (-0.05, -0.10), "GR-202": (-0.05, -0.12), "GR-203": (-0.05, -0.12), "GR-302": (-0.06, -0.14)}
for code, (up, lo) in DEV.items():                               # 核对：检验模板的公法线范围就是名义值加这组偏差
    k, wlo, whi = D.gear_w(code, up, lo)
    kk, w0 = D.base_tangent_length(g[code]["m"], g[code]["z"])
    assert abs(whi - round(w0 + lo, 3)) < 1e-9 or abs(wlo - round(w0 + lo, 3)) < 1e-9


def backlash(p, q, r_driven):
    """一对齿：法向侧隙 = 两齿公法线的减薄之和（取上偏差得最小、下偏差得最大），圆周侧隙 = 法向 / cos α，被动轮转角 = 圆周侧隙 / 分度圆半径"""
    jn = np.array([-(DEV[p][0] + DEV[q][0]), -(DEV[p][1] + DEV[q][1])])
    jt = jn / math.cos(alpha)
    return jn, jt, jt / r_driven


jn1, jt1, th1 = backlash("SH-101", "GR-202", s1["d2"] / 2)
jn2, jt2, th2 = backlash("GR-203", "GR-302", s2["d2"] / 2)
out_1 = th1 / i2                                                   # 第一级的背隙出现在中间轴上，到输出轴再除以第二级的传动比
total = out_1 + th2
out(jn1_min=jn1[0], jn1_max=jn1[1], jt1_min=jt1[0], jt1_max=jt1[1], th1_min=th1[0] / ARCMIN, th1_max=th1[1] / ARCMIN,
    o1_min=out_1[0] / ARCMIN, o1_max=out_1[1] / ARCMIN, jn2_min=jn2[0], jn2_max=jn2[1], th2_min=th2[0] / ARCMIN, th2_max=th2[1] / ARCMIN,
    bl_min=total[0] / ARCMIN, bl_max=total[1] / ARCMIN, in_deg_min=total[0] * i * 180 / math.pi, in_deg_max=total[1] * i * 180 / math.pi)
assert 3 < total[0] / ARCMIN < total[1] / ARCMIN < 20                # 普通齿轮减速器：几角分到十几角分

# ---------------------------------------------------------------- 图 32.1.1
from bookout import COLORS as C, T, figure, style  # noqa: E402
plt = style()
fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.2), gridspec_kw={"width_ratios": [1.15, 1.0]})
ax = axs[0]
x0 = 0.0
gears = [("SH-101", 0.0, 0.0, C["x"]), ("GR-202", s1["a"], 0.0, C["z"]), ("GR-203", s1["a"], 0.0, C["y"]),
         ("GR-302", s1["a"] + s2["a"], 0.0, C["accent"])]
for code, cx, cy, col in gears:
    r = g[code]["m"] * g[code]["z"] / 2
    ls = "-" if code != "GR-203" else "--"
    ax.add_patch(plt.Circle((cx, cy if code not in ("GR-203", "GR-302") else -0.0), r, fill=False, color=col, lw=1.6, ls=ls))
    ax.text(cx, (r + 8) * (1 if code in ("SH-101", "GR-302") else -1), f"{code}\nm{g[code]['m']} z{g[code]['z']}", ha="center",
            va="bottom" if code in ("SH-101", "GR-302") else "top", fontsize=8, color=col)
ax.annotate("", xy=(s1["a"], 0), xytext=(0, 0), arrowprops=dict(arrowstyle="<->", color=C["muted"]))
ax.text(s1["a"] / 2, 4, f"a₁ = {s1['a']:.0f}", ha="center", fontsize=8, color=C["muted"])
ax.annotate("", xy=(s1["a"] + s2["a"], 0), xytext=(s1["a"], 0), arrowprops=dict(arrowstyle="<->", color=C["muted"]))
ax.text(s1["a"] + s2["a"] / 2, 4, f"a₂ = {s2['a']:.0f}", ha="center", fontsize=8, color=C["muted"])
ax.set_xlim(-40, s1["a"] + s2["a"] + 120)
ax.set_ylim(-150, 165)
ax.set_aspect("equal")
ax.set_xlabel("mm")
ax.set_yticks([])
ax.set_title(T("(a) WQR-105 的两级齿轮（分度圆，侧视展开）", "(a) WQR-105's two stages (pitch circles)"), fontsize=11)
ax = axs[1]
labs = [T("第一级（换到输出轴）", "stage 1 (at the output)"), T("第二级", "stage 2"), T("合计", "total")]
lo = [out_1[0] / ARCMIN, th2[0] / ARCMIN, total[0] / ARCMIN]
hi = [out_1[1] / ARCMIN, th2[1] / ARCMIN, total[1] / ARCMIN]
y = np.arange(3)
ax.barh(y, hi, color=C["z"], alpha=0.35, label=T("公法线取下偏差（侧隙最大）", "lower W deviation (largest play)"))
ax.barh(y, lo, color=C["z"], alpha=0.9, label=T("公法线取上偏差（侧隙最小）", "upper W deviation (smallest play)"))
ax.axvline(1.0, color=C["x"], lw=1, ls="--")
ax.text(1.1, -0.5, T("谐波、RV：≤ 1′", "strain wave, RV: ≤ 1′"), fontsize=8, color=C["x"], va="center")
ax.set_yticks(y, labs)
ax.set_ylim(2.6, -0.8)
ax.set_xlabel(T("输出轴的角度背隙 / 角分", "angular backlash at the output / arcmin"))
ax.legend(fontsize=8, frameon=False, loc="lower right")
ax.set_title(T("(b) 背隙从哪里来", "(b) where the backlash comes from"), fontsize=11)
fig.tight_layout()
figure(fig, "fig32_1_1")
