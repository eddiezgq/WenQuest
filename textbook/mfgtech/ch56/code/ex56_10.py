"""算例 56.10.1、56.10.2：工艺路线方案的比较。
56.10.1 三个方案：A 棒料 + 现有设备分散加工（本章路线）；B 棒料 + 车铣复合集中加工（56.8 节）；C 模锻件 + 现有设备（56.3 节）。
         比较单件的机床与人工成本、毛坯成本、瓶颈与节拍、装夹次数；
56.10.2 粗车、精车用普通车床还是数控车床：单件成本 = a + S/批量，临界批量（hub/route.py critical_batch）。
普通车床、车铣复合中心的工时与费率是示意值；数控车床等的费率取工厂数据。画图 56.10.2、56.10.3。"""
import copy
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

R = M.route()
P = M.part101()
A = M.route101()["operations"]
TM, LATHE = "车铣复合中心 TM-01", "普通车床 CA-01"
R.EXTRA_WS[TM] = (95.0, 1)
R.EXTRA_WS[LATHE] = (32.0, 2)                    # 普通车床（示意）：小时费率 32 元/h，2 台
B = [copy.deepcopy(o) for o in A if o["seq"] not in (20, 30, 50)]
B.insert(1, {"seq": 20, "operation": "车铣复合 Turn-mill", "workstation": TM, "minutes": 27.0, "setup_min": 45})
C = copy.deepcopy(A)
next(o for o in C if o["seq"] == 20)["minutes"] = 7.0          # 锻件余量小，粗车约一半（同 ex56_3）
C = [o for o in C if o["seq"] != 10]                            # 锻件不用锯
batch = P["batch"]
rho, price = 7.85e-6, M.F.ITEMS["RM-20CR-D60"][3]
m_bar = math.pi / 4 * 60 ** 2 * M.route101()["blank"]["length_mm"] * rho
blank_cost = {"A": m_bar * price, "B": m_bar * price}
# 锻件：毛坯 1.59 kg（含飞边、烧损，见 ex56_3）、锻造加工费 4 元/件、锻模 36 000 元/年（示意）
m_forg_in = 1.5916
blank_cost["C"] = m_forg_in * price + 4.0 + 36000.0 / P["annual_volume"]
res = {}
for k, ops in (("A", A), ("B", B), ("C", C)):
    r = R.route_cost(ops, batch)
    res[k] = {"mach": r["cost"], "blank": blank_cost[k], "total": r["cost"] + blank_cost[k], "neck": r["bottleneck"].split(" ")[0], "takt": r["takt"]}
setups = {"A": 7, "B": 4, "C": 7}
# 按整条路线算的棒料/锻件临界年产量（锻模费按年产量分摊；56.3 节只比较了毛坯和粗车）
N_crit_full = 36000.0 / (res["A"]["total"] - (res["C"]["total"] - 36000.0 / P["annual_volume"]))
# ---- 56.10.2 粗车、精车：普通车床 vs 数控车床
turn_cnc = [o for o in A if o["seq"] in (20, 30)]
turn_lathe = [{"operation": o["operation"], "workstation": LATHE, "minutes": o["minutes"] * 1.9, "setup_min": 10} for o in turn_cnc]
Nc = R.critical_batch(turn_cnc, turn_lathe)
a1, s1 = R.cost_line(turn_cnc)
a2, s2 = R.cost_line(turn_lathe)

plt = style()
lab = {"A": T("A 棒料 + 分散", "A bar, dispersed"), "B": T("B 棒料 + 车铣复合", "B bar, turn-mill"), "C": T("C 模锻件 + 分散", "C forging, dispersed")}

# ---- 图 56.10.1：三个方案的比较表
HEAD = [T("比较项", "item"), lab["A"], lab["B"], lab["C"]]
rows = [[T("毛坯", "blank"), T("Ø60 圆钢", "Ø60 bar"), T("Ø60 圆钢", "Ø60 bar"), T("模锻件（锻模 36 000 元/年，示意）", "die forging")],
        [T("车、铣键槽", "turning, keyway"), T("数控车床 ×2 道、键槽铣床", "CNC lathe, keyway mill"), T("车铣复合中心一道", "one turn-mill op"), T("同 A，粗车工时约减半", "as A, half roughing time")],
        [T("质量保证", "quality"), T("中心孔统一基准；淬火前滚齿、铣键槽，淬火后磨", "centres throughout"), T("同 A；车与键槽一次装夹，对称度更稳", "as A; one setup"), T("同 A；锻件流线好，粗基准避开飞边", "as A; grain flow")],
        [T("装夹次数", "setups"), str(setups["A"]), str(setups["B"]), str(setups["C"])],
        [T("瓶颈（每件 min）", "bottleneck"), f"{res['A']['neck']} {res['A']['takt']:.1f}", f"{res['B']['neck']} {res['B']['takt']:.1f}", f"{res['C']['neck']} {res['C']['takt']:.1f}"],
        [T("单件成本粗估 / 元", "cost / CNY"), f"{res['A']['total']:.1f}", f"{res['B']['total']:.1f}", f"{res['C']['total']:.1f}"],
        [T("投资与风险", "investment, risk"), T("无新增投资", "none"), T("新购车铣复合中心；单机故障停线", "new machine; single point"), T("开锻模；依赖锻件供应商", "die; supplier")],
        [T("适用", "suits"), T(f"现在（年产 {P['annual_volume']}）", "now"), T("产量大、同轴度要求更高", "high volume, tighter runout"), T(f"年产明显超过 {N_crit_full:.0f}", "well above break-even")]]
M.table_fig(plt, HEAD, rows, [0.16, 0.28, 0.28, 0.28], "fig56_10_1", fontsize=6.8)
# ---- 图 56.10.2：三个方案的单件成本构成与节拍
fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.6, 2.5), gridspec_kw={"width_ratios": [1.3, 1]})
ks = ["A", "B", "C"]
ax.bar(range(3), [res[k]["blank"] for k in ks], color=M.MUTED, label=T("毛坯", "blank"))
ax.bar(range(3), [res[k]["mach"] for k in ks], bottom=[res[k]["blank"] for k in ks], color=M.ACCENT, label=T("机床与人工", "machines & labour"))
for i, k in enumerate(ks):
    ax.text(i, res[k]["total"] + 1.5, f"{res[k]['total']:.1f}", ha="center", fontsize=7.5)
ax.set_xticks(range(3)); ax.set_xticklabels([lab[k] for k in ks], fontsize=6.8)
ax.set_ylabel(T("单件成本 / 元", "cost per part / CNY")); ax.legend(fontsize=7, loc="upper left"); ax.set_ylim(0, max(res[k]["total"] for k in ks) * 1.25)
bx.bar(range(3), [res[k]["takt"] for k in ks], color=M.WARM)
for i, k in enumerate(ks):
    bx.text(i, res[k]["takt"] + 0.6, res[k]["neck"], ha="center", fontsize=6.8)
bx.set_xticks(range(3)); bx.set_xticklabels(ks); bx.set_ylabel(T("瓶颈处每件 / min", "bottleneck min/part")); bx.set_ylim(0, max(res[k]["takt"] for k in ks) * 1.2)
for a in (ax, bx):
    a.grid(lw=0.3, alpha=0.5, axis="y")
figure(fig, "fig56_10_2")

# ---- 图 56.10.3：单件成本与批量
fig, ax = plt.subplots(figsize=(5.6, 2.7))
n = np.linspace(1, 60, 300)
ax.plot(n, a1 + s1 / n, color=M.ACCENT, lw=1.4, label=T("数控车床 CNC-L01（工厂数据）", "CNC lathe (factory data)"))
ax.plot(n, a2 + s2 / n, color=M.WARM, lw=1.4, label=T("普通车床（示意）", "engine lathe (illustr.)"))
if Nc:
    ax.axvline(Nc, color=M.MUTED, ls="--", lw=0.8)
    ax.text(Nc + 1.2, 52, T(f"临界批量 ≈ {Nc:.0f} 件", f"break-even ≈ {Nc:.0f}"), fontsize=7.5, color=M.MUTED)
ax.set_ylim(0, 60)
ax.set_xlabel(T("批量 / 件", "batch size")); ax.set_ylabel(T("粗车 + 精车的单件成本 / 元", "turning cost per part / CNY"))
ax.grid(lw=0.3, alpha=0.5); ax.legend(fontsize=7)
figure(fig, "fig56_10_3")

out(**{f"{k}_{x}": res[k][x] for k in ks for x in ("mach", "blank", "total", "takt")}, **{f"{k}_neck": res[k]["neck"] for k in ks},
    **{f"{k}_setups": setups[k] for k in ks}, Nc=Nc, a_cnc=a1, s_cnc=s1, a_lathe=a2, s_lathe=s2, lathe_rate=R.EXTRA_WS[LATHE][0],
    tm_rate=R.EXTRA_WS[TM][0], batch=batch, N_crit_full=N_crit_full)
