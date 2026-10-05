"""6.8 成本估算：同一个 XM540 舵机支架用铣削（6061 铝块）、钣金（5052 铝板）、3D 打印（PA12 激光烧结）三种做法，
单件成本随批量的变化、盈亏平衡批量和工时（算例 6.8.1，图 6.8.1）。成本模型见 _ch6.py：铣削费率取数字工厂 VMC-01，其余为本书设定的教学值。"""
import numpy as np

import _ch6 as H
from bookout import T, figure, out, style

m, s, a = H.milled(), H.sheet(), H.printed()
qs = np.unique(np.round(np.logspace(0, 3.3, 150)).astype(int))
cm = [H.cost_mill(q)["unit"] for q in qs]
cs = [H.cost_sheet(q)["unit"] for q in qs]
ca = [H.cost_print(q)["unit"] for q in qs]
hm = [H.cost_mill(q)["hours"] for q in qs]
hs = [H.cost_sheet(q)["hours"] for q in qs]
ha = [H.cost_print(q)["hours"] for q in qs]
q_sheet_print = H.breakeven(lambda q: H.cost_sheet(q)["unit"], lambda q: H.cost_print(q)["unit"])
best = {q: min((H.cost_mill(q)["unit"], T("铣削", "milling")), (H.cost_sheet(q)["unit"], T("钣金", "sheet metal")),
               (H.cost_print(q)["unit"], T("3D 打印", "3D printing")))[1] for q in (1, 5, 100)}
c1 = {k: f(1) for k, f in (("m", H.cost_mill), ("s", H.cost_sheet), ("a", H.cost_print))}
c100 = {k: f(100) for k, f in (("m", H.cost_mill), ("s", H.cost_sheet), ("a", H.cost_print))}

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
for y, c, lab in ((cm, H.C_MILL, T("铣削（6061 铝块）", "milling (6061 block)")), (cs, H.C_SHEET, T("钣金（5052 铝板）", "sheet metal (5052)")),
                  (ca, H.C_AM, T("3D 打印（PA12 激光烧结）", "3D printing (PA12 SLS)"))):
    a0.loglog(qs, y, color=c, lw=1.2, label=lab)
a0.axvline(q_sheet_print, color=H.MUTED, lw=0.6, ls="--")
a0.text(q_sheet_print * 1.1, 150, str(q_sheet_print), fontsize=6.6, color=H.MUTED)
a0.set_xlabel(T("批量 / 件", "Batch size"), fontsize=7.5)
a0.set_ylabel(T("单件成本 / 美元", "Cost per part / USD"), fontsize=7.5)
a0.legend(fontsize=6.3, frameon=False)
a0.tick_params(labelsize=6.5)
a0.set_title(T("(a) 单件成本", "(a) Cost per part"), fontsize=7.8)
for y, c, lab in ((hm, H.C_MILL, T("铣削", "milling")), (hs, H.C_SHEET, T("钣金", "sheet metal")), (ha, H.C_AM, T("3D 打印", "3D printing"))):
    a1.loglog(qs, y, color=c, lw=1.2, label=lab)
a1.legend(fontsize=6.3, frameon=False)
a1.set_xlabel(T("批量 / 件", "Batch size"), fontsize=7.5)
a1.set_ylabel(T("设备与人工工时 / h", "Machine and labour hours / h"), fontsize=7.5)
a1.tick_params(labelsize=6.5)
a1.set_title(T("(b) 一批的工时（不含排队、运输）", "(b) Hours per batch (no queueing or shipping)"), fontsize=7.8)
fig.tight_layout()
figure(fig, "fig6_8_1")

out(mass_m=m["mass"] * 1000, blank_m=m["blank_mass"] * 1000, util_m=100 * m["mass"] / m["blank_mass"], mass_s=s["mass"] * 1000, mass_a=a["mass"] * 1000,
    c1_m=c1["m"]["unit"], c1_s=c1["s"]["unit"], c1_a=c1["a"]["unit"], c100_m=c100["m"]["unit"], c100_s=c100["s"]["unit"], c100_a=c100["a"]["unit"],
    run_m=H.cost_mill(1)["run_min"], run_s=H.cost_sheet(1)["run_min"], build_a=H.cost_print(1)["build_h"] * 60,
    h1_m=H.cost_mill(1)["hours"], h1_s=H.cost_sheet(1)["hours"], h1_a=H.cost_print(1)["hours"],
    h100_m=H.cost_mill(100)["hours"], h100_s=H.cost_sheet(100)["hours"], h100_a=H.cost_print(100)["hours"],
    q_sp=q_sheet_print, best1=best[1], best5=best[5], best100=best[100], r_vmc=H.R_VMC, servo=H.SERVO["size"],
    W=H.SERVO["W"], Hs=H.SERVO["H"], D=H.SERVO["D"], width=H.B_WIDTH, up=H.UP_H, base=H.BASE_L, **{f"P_{k}": v for k, v in H.P.items()})
