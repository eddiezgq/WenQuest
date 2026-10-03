"""50.1 节：一份工艺规程给工厂里的谁用、用什么。读数字工厂里 SH-301 的工艺路线、BOM 和费率，算出图 50.1.1 里各部门拿到的数。"""
import _mfg as M
from bookout import T, figure, out, style

p = M.plan()
F = M.F
rt = F.BOMS["SH-301"][0]
route = F.ROUTINGS[rt]
assert [o["operation"] for o in p["operations"]] == [op for op, _ in route]          # 工艺规程与 ERPNext 的工艺路线是同一套工序
assert [o["minutes"] for o in p["operations"]] == [m for _, m in route]
mat_item, mat_qty = F.BOMS["SH-301"][1][0]
unit_price = F.ITEMS[mat_item][3]
rate = {o["workstation"]: sum(F.WORKSTATIONS[o["workstation"]][1]) for o in p["operations"]}
labour = sum(o["minutes"] / 60 * rate[o["workstation"]] for o in p["operations"])
mach = [o for o in p["operations"] if o.get("steps") and not o.get("final_inspection")]
batch = p["doc"]["batch"]
hours = {}
for o in p["operations"]:
    hours[o["workstation"]] = hours.get(o["workstation"], 0) + (o["minutes"] * batch + o.get("setup_min", 0)) / 60
out(routing=rt, n_ops=len(route), n_mach=len(mach), total_min=sum(m for _, m in route), mat_item=mat_item, mat_qty=mat_qty,
    mat_cost=mat_qty * unit_price, unit_price=unit_price, labour=labour, batch=batch,
    cnc_hours=hours["数控车床 CNC-L01"], n_tools=len(p["tool_list"]), n_gauges=len(p["gauges"]),
    n_chars=len(p["characteristics"]), n_insp=sum(len(o.get("inspect") or []) for o in p["operations"]))

# ---- 图 50.1.1：一份工艺数据，各部门各取所需
plt = style()
fig, ax = plt.subplots(figsize=(7.2, 4.2))
ax.set_xlim(-5, 5); ax.set_ylim(-3.2, 3.2); ax.axis("off")


def box(x, y, w, h, title, lines, color):
    ax.add_patch(plt.Rectangle((x - w / 2, y - h / 2), w, h, fc="white", ec=color, lw=1.4))
    ax.text(x, y + h / 2 - 0.28, title, ha="center", va="center", fontsize=9.5, color=color, weight="bold")
    for i, s in enumerate(lines):
        ax.text(x, y + h / 2 - 0.62 - 0.3 * i, s, ha="center", va="center", fontsize=7.6, color=M.INK)


box(0, 0, 3.0, 1.6, T("工艺规程（一份数据）", "Process plan (one dataset)"),
    [T("工序、工步、切削用量", "operations, steps, cutting data"), T("工装、刀具、量具、检验项目", "tooling, tools, gauges, checks"),
     T("工时定额、毛坯、版本与签署", "times, blank, revision, sign-off")], M.ACCENT)
users = [
    (-3.4, 2.1, T("计划", "Planning"), [T("工序与工时 → 排产、交期", "ops & times → schedule")]),
    (0, 2.45, T("采购与仓库", "Purchasing"), [T("毛坯规格与用量 → 订料", "blank & quantity → order")]),
    (3.4, 2.1, T("车间", "Shop floor"), [T("工步、用量、装夹 → 加工", "steps, data, setup → make")]),
    (-3.4, -2.1, T("财务", "Finance"), [T("工时 × 费率 → 成本", "time × rate → cost")]),
    (0, -2.45, T("质检", "Quality"), [T("检验项目、量具、频次 → 检验", "checks, gauges, frequency")]),
    (3.4, -2.1, T("工装与刀具", "Tooling"), [T("夹具、刀具、量具 → 准备", "fixtures, tools → prepare")]),
]
for x, y, t, ls in users:
    box(x, y, 2.6, 0.95, t, ls, M.INK)
    ax.annotate("", xy=(x * 0.62, y * 0.62), xytext=(x * 0.28, y * 0.28),
                arrowprops=dict(arrowstyle="-|>", color=M.MUTED, lw=1.0))
figure(fig, "fig50_1_1")
