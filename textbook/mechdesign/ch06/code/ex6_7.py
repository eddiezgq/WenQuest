"""6.7 面向装配的设计（布思罗伊德–迪赫斯特方法）：机器人关节后端盖组件的 DFA 分析，原设计与改进设计；
WQR-105 输出轴组件 SA-300（数字工厂 BOM）的最少零件数分析。算例 6.7.1、6.7.2，图 6.7.1。

手工装配时间 = 拿取时间 + 插入（装上、紧固）时间，按布思罗伊德–迪赫斯特手工装配表的典型值估取（本书取值，待核对）；
装配设计效率 E = 3 s × 理论最少零件数 / 总装配时间（3 s 是一个理想零件的装配时间）。
理论最少零件数：对每个零件问三个问题——工作时它与已装的零件有相对运动吗？必须用不同的材料（或与之隔离）吗？
为了装拆其他零件必须分开吗？有一个“是”，它就是必需的。"""
import _ch6 as H
from bookout import T, figure, out, style

F = H.F

# 典型时间（s）：(拿取, 插入)
TIMES = {
    "cap": (1.95, 1.5),           # 较大、易抓的盖：放上去、对准
    "oring": (2.25, 5.0),         # O 形圈：柔软、要撑开套进槽里
    "screw": (1.8, 6.0),          # 小螺钉：取、对孔、用螺丝刀拧紧
    "washer": (1.8, 1.5),         # 垫圈：薄、小，不好拿
    "pin": (1.5, 3.0),            # 定位销：压入
    "holder": (1.5, 2.6),         # 磁铁座：压到轴端
    "magnet": (2.6, 4.0),         # 磁铁：小、有磁性、要粘
    "gland": (1.95, 8.0),         # 电缆密封接头：穿线、拧紧
    "label": (2.0, 3.0),          # 铭牌：撕、贴
    "snapcap": (1.95, 2.5),       # 带卡扣的盖：对准、旋进卡住
    "magsub": (1.5, 2.6),         # 磁铁组件（供应商粘好磁铁的座）
}
# (名称, 数量, 时间类型, 是否必需（三个问题）, 理由)
ORIG = [
    (T("端盖", "cap"), 1, "cap", True, T("要能拆下来维修编码器", "must come off to service the encoder")),
    (T("O 形圈", "O-ring"), 1, "oring", True, T("材料不同（橡胶）", "different material (rubber)")),
    (T("M3 螺钉", "M3 screw"), 6, "screw", False, T("紧固件", "fastener")),
    (T("垫圈", "washer"), 6, "washer", False, T("紧固件", "fastener")),
    (T("定位销", "dowel pin"), 2, "pin", False, T("只为对准，可做成盖上的止口", "only for alignment; a spigot on the cap can do it")),
    (T("磁铁座", "magnet holder"), 1, "holder", True, T("随轴转，相对端盖运动", "turns with the shaft")),
    (T("磁铁", "magnet"), 1, "magnet", True, T("材料不同", "different material")),
    (T("电缆密封接头", "cable gland"), 1, "gland", False, T("可做成盖上的密封套", "can be a sleeve moulded on the cap")),
    (T("铭牌", "label"), 1, "label", False, T("可激光打标在盖上", "can be laser-marked on the cap")),
]
NEW = [
    (T("卡扣式端盖（止口、密封套一体）", "snap-fit cap (spigot, cable sleeve integral)"), 1, "snapcap", True, ""),
    (T("O 形圈", "O-ring"), 1, "oring", True, ""),
    (T("M3 螺钉（防松）", "M3 screw (anti-loosening)"), 2, "screw", False, ""),
    (T("磁铁组件（供应商粘好）", "magnet assembly (bonded by supplier)"), 1, "magsub", True, ""),
]


def analyse(parts):
    n = sum(q for _, q, *_ in parts)
    nmin = sum(q for _, q, _, ess, _ in parts if ess)
    tt = sum(q * sum(TIMES[k]) for _, q, k, _, _ in parts)
    rows = [(nm, q, q * sum(TIMES[k])) for nm, q, k, _, _ in parts]
    return n, nmin, tt, 3 * nmin / tt, rows


n0, nmin0, t0, e0, rows0 = analyse(ORIG)
n1, nmin1, t1, e1, rows1 = analyse(NEW)
LABOUR = sum(F.WORKSTATIONS["装配工位 ASM-01"][1])          # 数字工厂装配工位费率 美元/小时
c0, c1 = t0 / 3600 * LABOUR, t1 / 3600 * LABOUR
Q_YEAR = 20000                                               # 任务单 TS-6-1 的年产量（本书设定）

# 算例 6.7.2：SA-300（数字工厂 BOM）
ESS = {"SH-301": (True, T("基体零件", "base part")),
       "GR-302": (False, T("三个“否”：40Cr 与 45 钢都是钢，原理上可做成齿轮轴", "three noes: both steels; could be one gear shaft")),
       "BRG-6207": (True, T("内外圈相对转动", "rings rotate relative to each other"))}
sa = []
for code, q in F.BOMS["SA-300"][1]:
    ess, why = ESS.get(code, (False, T("键：可用过盈或花键代替（要另算强度）", "key: interference or spline could replace it (check strength)")))
    sa.append((code, F.ITEMS[code][0].split(" ")[0], int(q), ess, why))
n_sa = sum(r[2] for r in sa)
nmin_sa = sum(r[2] for r in sa if r[3])

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.25, 1.0]})
for ax, rows, ttl in ((a0, rows0, T(f"(a) 原设计：{n0} 个零件，{t0:.0f} s，E = {e0:.0%}", f"(a) Original: {n0} parts, {t0:.0f} s, E = {e0:.0%}")),
                      (a1, rows1, T(f"(b) 改进设计：{n1} 个零件，{t1:.0f} s，E = {e1:.0%}", f"(b) Redesign: {n1} parts, {t1:.0f} s, E = {e1:.0%}"))):
    y = range(len(rows))
    ax.barh(list(y), [r[2] for r in rows], color=H.C_MILL)
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"{r[0]} × {r[1]}" for r in rows], fontsize=6.2)
    ax.invert_yaxis()
    ax.set_xlim(0, max(r[2] for r in rows0) * 1.1)
    ax.set_xlabel(T("装配时间 / s", "Assembly time / s"), fontsize=7.2)
    ax.tick_params(labelsize=6.3)
    ax.set_title(ttl, fontsize=7.4)
fig.tight_layout()
figure(fig, "fig6_7_1")

out(n0=n0, nmin0=nmin0, t0=t0, e0=100 * e0, n1=n1, nmin1=nmin1, t1=t1, e1=100 * e1, t_saved=100 * (1 - t1 / t0),
    labour=LABOUR, c0=c0, c1=c1, t_screw=sum(TIMES["screw"]), t_screws0=6 * sum(TIMES["screw"]) + 6 * sum(TIMES["washer"]),
    share_fast0=100 * (6 * sum(TIMES["screw"]) + 6 * sum(TIMES["washer"])) / t0,
    n_sa=n_sa, nmin_sa=nmin_sa, n_kinds_sa=len(sa), q_year=Q_YEAR, save_year=(c0 - c1) * Q_YEAR, save_h=(t0 - t1) * Q_YEAR / 3600)
