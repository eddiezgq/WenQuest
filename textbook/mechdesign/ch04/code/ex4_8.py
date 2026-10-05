"""4.8 尺寸链：WQR-105 输出轴系的轴向游隙。两个 6207 两端固定（各由端盖压住外圈），轴向游隙是封闭环。
极值法、统计法（方和根）、蒙特卡洛法三种算法对照；完全互换做不到时，用调整垫片作补偿环（算例 4.8.1–4.8.3，图 4.8.1）。

轴上的尺寸取第 33 章 SH-301 B 版（_shaft.py）；箱体两端面的距离 W、端盖止口长 c 是本书设定（数字工厂的箱体 HSG-001 还没有这几个尺寸）。"""
import math

import numpy as np

import _ch4 as H
from bookout import T, figure, out, style

S = H.S
lay = S.LAY_B
B = H.BRG["B"]
B_LO = H.BRG_TOL["B_lo"] / 1000                  # 轴承宽度偏差 0 / −0.12（GB/T 307.1）
C_SH = lay[4][0] - lay[2][0]                      # 轴上：齿轮定位面（轴环左侧）到右轴承轴肩，25（第 3.3 节的功能尺寸）
REQ = (0.20, 0.40)                                # 两端固定的深沟球轴承留的轴向游隙（常用推荐值，见正文）
W = 152.0                                         # 箱体两端面（装端盖的面）之间的距离（本书设定）


def zone_mm(d, code):
    lo, hi = H.zone(d, code)
    return lo / 1000, hi / 1000


# 组成环：(名称, 名义, 下偏差, 上偏差, 增环 +1 / 减环 −1)
def links(c):
    return [
        (T("箱体两端面距离 W", "Housing faces W"), W, *zone_mm(W, "js11"), +1),
        (T("闷盖止口 c₁", "Blind-cap spigot c₁"), c, *zone_mm(c, "js11"), -1),
        (T("透盖止口 c₂", "Through-cap spigot c₂"), c, *zone_mm(c, "js11"), -1),
        (T("左轴承宽 B", "Left bearing B"), B, B_LO, 0.0, -1),
        (T("套筒", "Sleeve"), S.SLEEVE, *zone_mm(S.SLEEVE, "h11"), -1),
        (T("齿轮毂宽", "Gear hub"), S.HUB_GEAR, *zone_mm(S.HUB_GEAR, "h11"), -1),
        (T("轴：定位面到轴肩", "Shaft: face to shoulder"), C_SH, *zone_mm(C_SH, "js11"), -1),
        (T("右轴承宽 B", "Right bearing B"), B, B_LO, 0.0, -1),
    ]


S_NOM = 2 * B + S.SLEEVE + S.HUB_GEAR + C_SH       # 两轴承外圈外侧面之间的距离 132
C_NAIVE = round((W - S_NOM - sum(REQ) / 2) / 2, 3)  # 按名义尺寸凑：名义游隙 0.3
STEP = 0.05                                          # 垫片厚度组合的最小台阶（0.05、0.1、0.2、0.5 mm 几种组合）


def worst_case(L):
    nom = sum(k * n for _, n, lo, hi, k in L)
    gmax = nom + sum(hi if k > 0 else -lo for _, n, lo, hi, k in L)
    gmin = nom + sum(lo if k > 0 else -hi for _, n, lo, hi, k in L)
    return nom, gmin, gmax


def rss(L):
    """统计法：各环正态、对称分布在公差带中间，σ = T/6"""
    mean = sum(k * (n + (lo + hi) / 2) for _, n, lo, hi, k in L)
    sd = math.sqrt(sum(((hi - lo) / 6) ** 2 for _, n, lo, hi, k in L))
    return mean, sd


def monte_carlo(L, n=200000, seed=48, brg_mean=-0.05, brg_sd=0.015):
    """蒙特卡洛：机加工尺寸取正态（中心在公差带中间，σ = T/6）；轴承宽度取正态 N(−0.05, 0.015)——轴承厂的实际分布比公差带窄，中心比公差带中间（−0.06）略偏大（本书设定）"""
    rng = np.random.default_rng(seed)
    g = np.zeros(n)
    for name, nom, lo, hi, k in L:
        if hi == 0.0 and lo == B_LO:
            x = nom + rng.normal(brg_mean, brg_sd, n)
        else:
            x = nom + rng.normal((lo + hi) / 2, (hi - lo) / 6, n)
        g += k * x
    return g


# 方案一（完全互换）：按各环的“中间尺寸”（名义 + 中间偏差）定止口长度，使游隙的平均值落在要求的中间
mu_naive = sum(k * (n + (lo + hi) / 2) for _, n, lo, hi, k in links(C_NAIVE))
C1 = round(round((C_NAIVE + (mu_naive - sum(REQ) / 2) / 2) / 0.05) * 0.05, 3)     # 止口长度取到 0.05 mm
L1 = links(C1)
nom1, wmin1, wmax1 = worst_case(L1)
T_wc = wmax1 - wmin1
mu1, sd1 = rss(L1)
T_rss = 6 * sd1
p_rss = 0.5 * (math.erf((REQ[1] - mu1) / (sd1 * math.sqrt(2))) - math.erf((REQ[0] - mu1) / (sd1 * math.sqrt(2))))
g1 = monte_carlo(L1)
p_mc = float(np.mean((g1 >= REQ[0]) & (g1 <= REQ[1])))
T_brg = 2 * (-B_LO)                                  # 两个轴承宽度的公差之和，已经超过要求的游隙范围
T_req = REQ[1] - REQ[0]

# ---------------------------------------------------------------- 方案二：调整垫片（补偿环）
# 方案二（垫片补偿）：止口加长，使不加垫片时游隙的极值上限也不超过“要求上限 − 一个台阶”——垫片只能把游隙加大，不能减小
C2 = round(C1 + math.ceil((wmax1 - (REQ[1] - STEP)) / 2 / 0.05 - 1e-9) * 0.05, 3)
MEAS_SD = 0.01                                       # 测量误差（深度尺、塞尺）σ
TARGET = sum(REQ) / 2
L2 = links(C2)
nom2, wmin2, wmax2 = worst_case(L2)
rng = np.random.default_rng(49)
g0 = monte_carlo(L2, seed=50)                        # 不加垫片时的“游隙”（负值即装不进去、要加垫片）
meas = g0 + rng.normal(0, MEAS_SD, g0.size)
shim = np.maximum(0, np.round((TARGET - meas) / STEP) * STEP)
g2 = g0 + shim
p_shim = float(np.mean((g2 >= REQ[0]) & (g2 <= REQ[1])))
shim_max = float(shim.max())
shim_wc = TARGET - wmin2                             # 极值法算出垫片最厚要多厚（再加半个台阶）
shim_wc_min = TARGET - wmax2
# 热伸长核对：轴比箱体温度高 ΔT 时两轴承外圈之间伸长
ALPHA, DT = 11.5e-6, 20.0
d_thermal = ALPHA * S_NOM * DT
# 若不用垫片、想完全互换：去掉轴承后其余 6 个环可用的公差只剩 T_req − T_brg（负数说明做不到）
left_for_parts = T_req - T_brg

# ---------------------------------------------------------------- 图
plt = style()
fig = plt.figure(figsize=(7.6, 4.6))
gs = fig.add_gridspec(2, 2, height_ratios=[0.7, 1.15], hspace=0.45, wspace=0.25)
a0 = fig.add_subplot(gs[0, :])
# (a) 尺寸链简图：上面一行是箱体与端盖，下面一行是轴上的零件
y_top, y_bot = 1.0, 0.0
xs = 0.0
segs_bot = [(T("轴承", "brg"), B), (T("套筒", "sleeve"), S.SLEEVE), (T("齿轮毂", "gear hub"), S.HUB_GEAR), (T("轴", "shaft"), C_SH), (T("轴承", "brg"), B)]
GD = 9.0                                            # 图上把游隙画成 9 mm 宽（放大）
ks = (W - 2 * C1 - GD) / S_NOM
x = C1
for nm, ln in segs_bot:
    a0.annotate("", xy=(x + ln * ks, y_bot), xytext=(x, y_bot), arrowprops=dict(arrowstyle="<->", lw=0.7, color="#c0392b"))
    a0.text(x + ln * ks / 2, y_bot - 0.18, f"{nm} {ln:g}", ha="center", va="top", fontsize=6.4, color="#c0392b")
    x += ln * ks
a0.annotate("", xy=(W, y_top), xytext=(0, y_top), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#1f77b4"))
a0.text(W / 2, y_top + 0.12, T(f"箱体 W = {W:g}（增环）", f"housing W = {W:g} (increasing)"), ha="center", fontsize=6.8, color="#1f77b4")
for x0, x1, nm in ((0, C1, "c₁"), (W - C1, W, "c₂")):
    a0.annotate("", xy=(x1, 0.5), xytext=(x0, 0.5), arrowprops=dict(arrowstyle="<->", lw=0.7, color="#c0392b"))
    a0.text((x0 + x1) / 2, 0.58, nm, ha="center", fontsize=6.6, color="#c0392b")
a0.annotate("", xy=(W - C1, y_bot), xytext=(x, y_bot), arrowprops=dict(arrowstyle="<->", lw=0.9, color="#2ca02c"))
a0.text(W - C1 - GD / 2, y_bot - 0.18, T("游隙\n（封闭环）", "end play\n(closing link)"), fontsize=6.4, color="#2ca02c", ha="center", va="top")
for xx in (0, W):
    a0.plot([xx, xx], [-0.3, 1.2], color=H.MUTED, lw=0.6)
a0.set_xlim(-5, W + 5)
a0.set_ylim(-0.8, 1.35)
a0.axis("off")
a0.set_title(T("(a) 轴向尺寸链：蓝色增环，红色减环（下排是轴上的零件，示意，游隙放大）",
               "(a) Axial chain: blue increasing, red decreasing links (shaft parts below; schematic, play enlarged)"), fontsize=7.8)
a1 = fig.add_subplot(gs[1, 0])
bins = np.linspace(-0.4, 1.0, 120)
a1.hist(g1, bins=bins, color="#9ecae1", density=True)
for v, ls, lab in ((wmin1, "-", T("极值", "worst case")), (wmax1, "-", None), (mu1 - 3 * sd1, "--", T("方和根 ±3σ", "RSS ±3σ")), (mu1 + 3 * sd1, "--", None)):
    a1.axvline(v, color=H.INK, lw=0.8, ls=ls, label=lab)
a1.axvspan(*REQ, color="#2ca02c", alpha=0.15, label=T("要求 0.2–0.4", "required 0.2–0.4"))
a1.set_xlabel(T("游隙 / mm", "End play / mm"), fontsize=7.5)
a1.set_yticks([])
a1.tick_params(labelsize=6.5)
a1.legend(fontsize=6.2, frameon=False, loc="upper right")
a1.set_title(T(f"(b) 方案一 完全互换：合格 {100 * p_mc:.0f}%", f"(b) Option 1, full interchange: {100 * p_mc:.0f}% OK"), fontsize=7.8)
a2 = fig.add_subplot(gs[1, 1])
a2.hist(g0, bins=bins, color="#fdd0a2", density=True, label=T("不加垫片", "no shims"))
a2.hist(g2, bins=bins, color="#74c476", density=True, label=T("按测量值加垫片", "shimmed to measurement"))
a2.axvspan(*REQ, color="#2ca02c", alpha=0.15)
a2.set_xlabel(T("游隙 / mm", "End play / mm"), fontsize=7.5)
a2.set_yticks([])
a2.tick_params(labelsize=6.5)
a2.legend(fontsize=6.2, frameon=False, loc="upper left")
a2.set_title(T(f"(c) 方案二 调整垫片：合格 {100 * p_shim:.1f}%", f"(c) Option 2, shims: {100 * p_shim:.1f}% OK"), fontsize=7.8)
figure(fig, "fig4_8_1")

rows = [(nm, n, lo, hi, k) for nm, n, lo, hi, k in L1]
out(W=W, S_nom=S_NOM, c_naive=C_NAIVE, mu_naive=mu_naive, c1=C1, c2=C2, B=B, B_lo=B_LO, sleeve=S.SLEEVE, hub=S.HUB_GEAR, C_sh=C_SH, req_lo=REQ[0], req_hi=REQ[1],
    tol_W=zone_mm(W, "js11")[1], tol_c=zone_mm(C1, "js11")[1], tol_sl=-zone_mm(S.SLEEVE, "h11")[0], tol_hub=-zone_mm(S.HUB_GEAR, "h11")[0],
    tol_C=zone_mm(C_SH, "js11")[1],
    nom1=nom1, wmin1=wmin1, wmax1=wmax1, T_wc=T_wc, mu1=mu1, sd1=sd1, T_rss=T_rss, p_rss=100 * p_rss, p_mc=100 * p_mc,
    mc_mean=float(g1.mean()), mc_sd=float(g1.std()), T_brg=T_brg, T_req=T_req, left_for_parts=left_for_parts,
    nom2=nom2, wmin2=wmin2, wmax2=wmax2, step=STEP, meas_sd=MEAS_SD, p_shim=100 * p_shim, shim_max=shim_max,
    shim_mean=float(shim.mean()), shim_wc=shim_wc, shim_wc_min=shim_wc_min, d_thermal=d_thermal, dT=DT, n_mc=g1.size,
    n_links=len(L1), tol_c2=zone_mm(C2, "js11")[1])
