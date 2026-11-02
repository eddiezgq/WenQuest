"""算例 57.6.1–57.6.3：SH-101 的时间定额与生产率。
57.6.1 各道机械加工工序的单件时间 t_d = (t_b + t_a)(1 + (α + β)/100)，单件计算时间 t_c = t_d + T_z/n（式 57.6.1–57.6.3）：
        机动时间 t_b 由各工步的切削用量算出（hub/cards.step_values，与工序卡同一个函数），辅助时间 t_a = 工步里写的辅助时间 + 装卸工件、
        测量、换刀等（下表 TA，教学设计值），布置工作地 α = 3%、休息与生理需要 β = 5%；准备与终结时间 T_z 取工艺规程，批量 100。
        单件时间按 0.5 min 往上取整，就是工艺规程里的单件工时（逐道核对）；热处理按炉次计划，不定单件定额。
57.6.2 各工作中心的负荷与瓶颈（hub/route.py route_cost）、年产能，与第 56 章的粗估（按路线文件的工时）比较；
57.6.3 年产量增加到 2 万件，瓶颈在哪里、要加几台。画图 57.6.1、57.6.2。"""
import math

import _mfg as M
from bookout import T, figure, out, style

P = M.plan101()
CD = M.cards
RT = M.route()
ALPHA, BETA = 3.0, 5.0
TA = {   # 工步里没有写的辅助时间（min）：装卸工件、测量、换刀与对刀、顶尖或鸡心夹头（教学设计值，量级同常用工时定额手册）
    10: [("装卸工件", 0.3)],
    20: [("装卸工件（两次安装）", 1.2), ("测量（6 处）", 0.9), ("换刀、对刀", 0.4), ("顶尖进退", 0.4)],
    30: [("装卸工件、鸡心夹头（两次）", 1.6), ("换半缺顶尖（两次）", 0.6), ("测量（8 处）", 1.6)],
    40: [("装卸工件", 0.6)],
    50: [("测量", 0.3)],
    70: [("装卸工件、鸡心夹头", 0.8), ("测量（4 处）", 1.2)],
}
rows = []
for o in P["operations"]:
    if o["seq"] not in TA:
        continue
    tb = sum((CD.step_values(s)["tb"] or 0) for s in o.get("steps") or [])
    ta = sum(s.get("ta_min") or 0 for s in o.get("steps") or []) + sum(v for _, v in TA[o["seq"]])
    td = (tb + ta) * (1 + (ALPHA + BETA) / 100)
    tq = math.ceil(td * 2 - 1e-9) / 2
    assert abs(tq - o["minutes"]) < 1e-9, (o["seq"], tq, o["minutes"])        # 与工艺规程的单件工时一致
    tc = o["minutes"] + o["setup_min"] / P["batch"]
    rows.append({"seq": o["seq"], "op": o["operation"].split(" ")[0], "tb": tb, "ta": ta, "ab": td - tb - ta, "td": td, "tq": tq,
                 "tz": o["setup_min"], "tc": tc, "ws": o["workstation"]})
cost = RT.route_cost(P["operations"], P["batch"])
rough = RT.route_cost(M.route101()["operations"], P["batch"])
N = M.part101()["annual_volume"]
need = M.FE_MIN / N
cap = M.FE_MIN / cost["takt"]
cap56 = M.FE_MIN / rough["takt"]
N2 = 20000
need2 = M.FE_MIN / N2
add = {k: math.ceil(v / need2 - 1e-9) for k, v in cost["load"].items()}          # 每个工作中心按负荷需要的台数（现有台数见工厂数据）
have = {k: RT.rate_per_hour(k)[1] for k in cost["load"]}
extra = {k: add[k] * (1 if "热处理" in k else 1) - (1 if "热处理" in k else have[k]) for k in cost["load"] if "热处理" not in k}

plt = style()
fig, ax = plt.subplots(figsize=(6.4, 2.6))
xs = range(len(rows))
b1 = [r["tb"] for r in rows]
b2 = [r["ta"] for r in rows]
b3 = [r["ab"] for r in rows]
b4 = [r["tz"] / P["batch"] for r in rows]
ax.bar(xs, b1, color=M.ACCENT, label=T("机动时间 t_b", "machining t_b"))
ax.bar(xs, b2, bottom=b1, color=M.WARM, label=T("辅助时间 t_a", "handling t_a"))
ax.bar(xs, b3, bottom=[a + b for a, b in zip(b1, b2)], color=M.MUTED, label=T("布置工作地、休息与生理 (α+β)", "allowances (α+β)"))
ax.bar(xs, b4, bottom=[r["td"] for r in rows], color=M.GREEN, label=T("准备与终结 T_z/n", "set-up T_z/n"))
for i, r in enumerate(rows):
    ax.text(i, r["td"] + b4[i] + 0.3, f"{r['tc']:.1f}", ha="center", fontsize=7)
ax.set_xticks(list(xs)); ax.set_xticklabels([f"{r['seq']} {r['op']}" for r in rows], fontsize=7)
ax.set_ylabel(T("每件 / min", "min per part")); ax.legend(fontsize=6.5, loc="upper left"); ax.grid(lw=0.3, alpha=0.4, axis="y")
ax.set_ylim(0, 20)
figure(fig, "fig57_6_1")

fig, ax = plt.subplots(figsize=(6.4, 2.5))
ks = [k for k in cost["load"]]
lab = [k.split(" ")[0] for k in ks]
w = 0.38
ax.bar([i - w / 2 for i in range(len(ks))], [rough["load"].get(k, 0) for k in ks], w, color=M.MUTED, label=T("第 56 章路线的工时（粗估）", "Ch. 56 route (rough)"))
ax.bar([i + w / 2 for i in range(len(ks))], [cost["load"][k] for k in ks], w, color=M.ACCENT, label=T("本章的时间定额", "this chapter's standards"))
for lvl, col, txt in ((need, M.RED, T(f"年产 {N}：需求节拍 {need:.0f}", f"{N}/yr: takt {need:.0f}")), (need2, M.WARM, T(f"年产 {N2}：{need2:.1f}", f"{N2}/yr: {need2:.1f}"))):
    ax.axhline(lvl, color=col, ls="--", lw=0.9)
    ax.text(len(ks) - 0.5, lvl + 0.5, txt, fontsize=7, color=col, ha="right")
ax.set_xticks(range(len(ks))); ax.set_xticklabels(lab, fontsize=7)
ax.set_ylabel(T("每件占用 / min（按台数分摊）", "min per part (per machine count)")); ax.legend(fontsize=6.8, loc="upper left")
ax.grid(lw=0.3, alpha=0.4, axis="y"); ax.set_ylim(0, 38)
figure(fig, "fig57_6_2")

HEAD = [T("工序", "op"), T("机动 t_b", "t_b"), T("辅助 t_a", "t_a"), T("单件 t_d", "t_d"), T("定额（取整）", "standard"), T("准终 T_z", "T_z"), T("单件计算 t_c", "t_c")]
trows = [[f"{r['seq']} {r['op']}", f"{r['tb']:.2f}", f"{r['ta']:.2f}", f"{r['td']:.2f}", f"{r['tq']:g}", f"{r['tz']:g}", f"{r['tc']:.2f}"] for r in rows]
M.table_fig(plt, HEAD, trows, [0.2, 0.12, 0.12, 0.12, 0.16, 0.12, 0.16], "fig57_6_4", fontsize=7, width_in=6.4)

r20 = next(r for r in rows if r["seq"] == 20)
out(alpha=ALPHA, beta=BETA, batch=P["batch"], **{f"tb_{r['seq']}": r["tb"] for r in rows}, **{f"ta_{r['seq']}": r["ta"] for r in rows},
    **{f"td_{r['seq']}": r["td"] for r in rows}, **{f"tq_{r['seq']}": r["tq"] for r in rows}, **{f"tc_{r['seq']}": r["tc"] for r in rows},
    neck=cost["bottleneck"].split(" ")[0], takt=cost["takt"], neck56=rough["bottleneck"].split(" ")[0], takt56=rough["takt"],
    need=need, cap=cap, cap56=cap56, N=N, N2=N2, need2=need2, t_total=sum(r["tc"] for r in rows), t_total_b=sum(r["tb"] for r in rows),
    share_tb=sum(r["tb"] for r in rows) / sum(r["tc"] for r in rows) * 100, extra_grd=extra.get("外圆磨床 GRD-01", 0),
    extra_list="、".join(f"{k.split(' ')[0]} {v} 台" for k, v in extra.items() if v > 0), rough_step3=CD.step_values(M.op(P, 20)["steps"][2])["tb"])
