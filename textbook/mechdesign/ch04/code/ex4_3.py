"""4.3 配合：SH-301 B 版各处的配合（齿轮、轴承内圈、联轴器）、轴承外圈与轴承座孔；
协作机器人肩关节 RJ-201 的轴承外圈装在铝合金壳体里，温升使配合变松（算例 4.3.1、4.3.2，图 4.3.1）。"""
import _ch4 as H
from bookout import T, figure, out, style

mdstd = H.mdstd
b6207 = H.BRG
t6207 = H.BRG_TOL
import _rj                                     # noqa: E402  第 33.10 节：零件库 A-BRG-DG
b6010 = _rj.bearing("6010")
t6010 = mdstd.bearing_tol(b6010["d"], b6010["D"])

# ---------------------------------------------------------------- 算例 4.3.1：SH-301 B 版
inner = (float(t6207["d_lo"]), float(t6207["d_hi"]))          # 轴承内圈相当于“孔”，公差带在零线下方
outer = (float(t6207["D_lo"]), float(t6207["D_hi"]))          # 外圈相当于“轴”
FITS = [
    ("gear", T("齿轮孔 / 齿轮位", "Gear bore / gear seat"), 40, H.zone(40, "H7"), H.zone(40, "r6"), "Ø40 H7/r6"),
    ("brg_in", T("6207 内圈 / 轴承位", "6207 inner ring / seat"), 35, inner, H.zone(35, "k6"), "Ø35 k6"),
    ("brg_out", T("轴承座孔 / 6207 外圈", "Housing bore / 6207 outer ring"), 72, H.zone(72, "H7"), outer, "Ø72 H7"),
    ("cpl", T("联轴器孔 / 外伸段", "Coupling bore / shaft end"), 30, H.zone(30, "H7"), H.zone(30, "k6"), "Ø30 H7/k6"),
]
res = {k: H.fit(h, s) for k, _, _, h, s, _ in FITS}

# 同样的 k6 轴，配普通的 H7 孔与配轴承内圈：轴承内圈公差带在零线下方，k6 配上去成了过盈
h7_k6_35 = H.fit(H.zone(35, "H7"), H.zone(35, "k6"))

# ---------------------------------------------------------------- 算例 4.3.2：RJ-201 的 6010 外圈在铝合金壳体里
ALPHA_ST, ALPHA_AL = 11.5e-6, 23.0e-6       # 线膨胀系数 1/K（轴承钢、铝合金，常用值）
DT = 25.0                                   # 工作温升：壳体和轴承外圈都比装配时（20 °C）高约 25 K（本书估计：电机、减速器发热）
D_o = b6010["D"]
loosen = (ALPHA_AL - ALPHA_ST) * D_o * DT * 1000    # μm：壳体孔比外圈多胀出的量
outer10 = (float(t6010["D_lo"]), 0.0)
cand = {}
for code in ("H7", "K6", "M6"):
    f = H.fit(H.zone(D_o, code), outer10)
    cand[code] = {"cold": f, "warm": (f["Xmin"] + loosen, f["Xmax"] + loosen), "zone": H.zone(D_o, code)}
inner10 = (float(t6010["d_lo"]), 0.0)
k5_50 = H.fit(inner10, H.zone(50, "k5"))

# ---------------------------------------------------------------- 图：配合公差带图
plt = style()
fig, axs = plt.subplots(1, 5, figsize=(7.6, 2.9), sharey=False)
panels = [(lab, h, s, sub) for _, lab, _, h, s, sub in FITS] + [(T("铝壳体孔 / 6010 外圈", "Al housing / 6010 outer ring"), cand["M6"]["zone"], outer10, "Ø80 M6")]
for ax, (lab, h, s, sub) in zip(axs, panels):
    ax.axhline(0, color=H.INK, lw=0.9)
    is_brg_hole = h[1] == 0 and h[0] < 0 and "6207" in lab and T("内圈", "inner") in lab
    H.draw_zone(ax, 0.0, 0.8, h[0], h[1], H.C_BRG if is_brg_hole else H.C_HOLE, T("内圈", "inner ring") if is_brg_hole else T("孔", "hole"))
    s_brg = (s == outer or s == outer10)
    H.draw_zone(ax, 1.0, 0.8, s[0], s[1], H.C_BRG if s_brg else H.C_SHAFT, T("外圈", "outer ring") if s_brg else T("轴", "shaft"))
    f = H.fit(h, s)
    ax.set_xlim(-0.3, 2.1)
    lo, hi = min(h[0], s[0]), max(h[1], s[1])
    ax.set_ylim(lo - 12, hi + 12)
    ax.set_xticks([])
    ax.tick_params(labelsize=6.5)
    for sp in ("top", "right", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.set_title(sub + "\n" + lab, fontsize=6.6)
    ax.text(0.9, lo - 10, H.KIND_ZH[f["kind"]], ha="center", fontsize=6.6, color=H.ACC)
axs[0].set_ylabel(T("偏差 / μm", "Deviation / μm"), fontsize=7.5)
fig.tight_layout()
figure(fig, "fig4_3_1")

g, bi, bo, c = res["gear"], res["brg_in"], res["brg_out"], res["cpl"]
out(H7_40=H.zone(40, "H7"), r6_40=H.zone(40, "r6"),
    gear_Ymax=-g["Xmin"], gear_Ymin=-g["Xmax"], gear_Tf=g["Tf"],
    in_lo=inner[0], k6_35_lo=H.zone(35, "k6")[0], k6_35_hi=H.zone(35, "k6")[1],
    brgin_Ymax=-bi["Xmin"], brgin_Ymin=-bi["Xmax"],
    h7k6_Xmax=h7_k6_35["Xmax"], h7k6_Ymax=-h7_k6_35["Xmin"],
    out_lo=outer[0], H7_72_hi=H.zone(72, "H7")[1], brgout_Xmax=bo["Xmax"], brgout_Xmin=bo["Xmin"],
    cpl_Xmax=c["Xmax"], cpl_Ymax=-c["Xmin"], cpl_kind=H.KIND_ZH[c["kind"]],
    D_o=D_o, dT=DT, loosen=loosen, out10_lo=outer10[0],
    H7_80_hi=cand["H7"]["zone"][1], H7_cold_max=cand["H7"]["cold"]["Xmax"], H7_warm_max=cand["H7"]["warm"][1], H7_warm_min=cand["H7"]["warm"][0],
    K6_lo=cand["K6"]["zone"][0], K6_hi=cand["K6"]["zone"][1], K6_cold_Ymax=-cand["K6"]["cold"]["Xmin"], K6_cold_Xmax=cand["K6"]["cold"]["Xmax"],
    K6_warm_min=cand["K6"]["warm"][0], K6_warm_max=cand["K6"]["warm"][1],
    M6_lo=cand["M6"]["zone"][0], M6_hi=cand["M6"]["zone"][1], M6_cold_Ymax=-cand["M6"]["cold"]["Xmin"], M6_cold_Xmax=cand["M6"]["cold"]["Xmax"],
    M6_warm_min=cand["M6"]["warm"][0], M6_warm_Y=-cand["M6"]["warm"][0], M6_warm_max=cand["M6"]["warm"][1],
    k5_50_Ymax=-k5_50["Xmin"], k5_50_Ymin=-k5_50["Xmax"])
