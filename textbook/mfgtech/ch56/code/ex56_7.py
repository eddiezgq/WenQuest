"""56.7 节：加工阶段。SH-101 本章路线（std/SH-101_route.yaml）各阶段切除的余量与达到的公差等级（轴承位），
以及路线的阶段划分（粗加工、半精加工、热处理、精加工）。公差等级按 GB/T 1800.1（hub/process.it_grade）。画图 56.7.1、56.7.2。"""
import _mfg as M
from bookout import T, figure, out, style

proc = M.proc()
ref = M.route101()
P = M.part101()
STAGE = {"下料": ("blank", T("下料", "sawing")), "粗车": ("rough", T("粗加工", "roughing")), "精车": ("semi", T("半精加工", "semi-finishing")),
         "滚齿": ("semi", T("半精加工", "semi-finishing")), "铣键槽": ("semi", T("半精加工", "semi-finishing")),
         "渗碳淬火": ("heat", T("热处理", "heat treatment")), "磨外圆": ("finish", T("精加工", "finishing")), "零件检验": ("insp", T("检验", "inspection"))}
COL = {"blank": M.MUTED, "rough": "#8aa4bd", "semi": M.ACCENT, "heat": M.RED, "finish": M.WARM, "insp": M.GREEN}
d_prev, steps = 60.0, []
for o in ref["operations"]:
    f = next((x for x in o.get("features") or [] if x["name"] == "轴承位"), None)
    if not f:
        continue
    T_ = f["es_mm"] - f["ei_mm"]
    mid = f["size_mm"] + (f["es_mm"] + f["ei_mm"]) / 2
    steps.append({"op": o["operation"].split(" ")[0], "d": mid, "z": d_prev - mid, "it": proc.it_grade(f["size_mm"], T_), "ra": f["Ra_um"]})
    d_prev = mid
z_tot = sum(s["z"] for s in steps)

plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.5))
names = [s["op"] for s in steps]
a1.bar(range(len(steps)), [s["z"] for s in steps], color=[COL[STAGE[n][0]] for n in names])
for i, s in enumerate(steps):
    a1.text(i, s["z"] + 0.6, f"{s['z']:.2f}", ha="center", fontsize=7)
a1.set_yscale("symlog", linthresh=1); a1.set_ylim(0, 60)
a1.set_xticks(range(len(steps))); a1.set_xticklabels([STAGE[n][1] for n in names], fontsize=7)
a1.set_ylabel(T("切除的余量（直径上）/ mm", "stock removed (on diameter) / mm"))
a2.plot(range(len(steps)), [s["it"] for s in steps], "o-", color=M.ACCENT)
for i, s in enumerate(steps):
    a2.text(i + 0.08, s["it"] - 0.3, f"IT{s['it']}，Ra {s['ra']:g}", fontsize=7)
a2.invert_yaxis(); a2.set_xticks(range(len(steps))); a2.set_xticklabels([STAGE[n][1] for n in names], fontsize=7)
a2.set_ylabel(T("达到的公差等级", "grade reached")); a2.set_xlim(-0.3, len(steps) - 0.2)
for a in (a1, a2):
    a.grid(lw=0.3, alpha=0.5)
figure(fig, "fig56_7_1")

# ---- 图 56.7.2：路线的阶段划分
fig, ax = plt.subplots(figsize=(7.0, 1.5))
x = 0
for o in ref["operations"]:
    n = o["operation"].split(" ")[0]
    st, lab = STAGE[n]
    w = max(o["minutes"], 6)
    ax.add_patch(plt.Rectangle((x, 0), w - 0.6, 1, fc=COL[st], alpha=0.25, ec=COL[st]))
    ax.text(x + (w - 0.6) / 2, 0.62, n, ha="center", fontsize=7)
    ax.text(x + (w - 0.6) / 2, 0.25, lab, ha="center", fontsize=6.5, color=COL[st])
    x += w
ax.set_xlim(0, x); ax.set_ylim(0, 1); ax.axis("off")
figure(fig, "fig56_7_2")

out(z_rough=steps[0]["z"], z_semi=steps[1]["z"], z_grind=steps[2]["z"], z_tot=z_tot, pct_rough=steps[0]["z"] / z_tot * 100,
    it_rough=steps[0]["it"], it_semi=steps[1]["it"], it_grind=steps[2]["it"], d_semi=steps[1]["d"])
