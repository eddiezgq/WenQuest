"""6.2 切削加工：SH-301 的工艺路线（数字工厂 factory/factory/data.py）逐工序的工时与成本（数字工厂标准成本 hub/mrp.py 的同一个函数）；
粗车的纯切削时间与工艺路线工时对比；各加工方法的经济精度（数字工厂经济精度表 std/econ_accuracy.yaml）与 SH-301 的要求对照。
算例 6.2.1、6.2.2，图 6.2.1。"""
import math

import yaml

import _ch6 as H
from bookout import T, figure, out, style

from hub import kpi, mrp     # noqa: E402

ITEM = "SH-301"
mat, ops = mrp.std_unit_cost(ITEM)
route = mrp.routing_for(ITEM)
rows = []
for op, mins in route:
    r = kpi.rate_per_hour(mrp.OP_UNITS[op][0])
    rows.append((op, mins, r, mins / 60 * r))
total = mat + ops
t_total = sum(m for _, m, _, _ in rows)

# 算例 6.2.2：粗车的纯切削时间（现行 A 版：Ø50 棒料车成五段）
from freecad import wq_shaft                    # noqa: E402
segs = wq_shaft.PARAMS["segments"]
D0 = 50.0
V_removed = sum(math.pi / 4 * (D0 ** 2 - d ** 2) * L for d, L in segs)          # mm³
VC, FEED, AP = 150.0, 0.3, 2.5                  # 粗车 45 钢：切削速度 m/min、进给 mm/r、背吃刀量 mm（本书设定的常用值）
MRR = VC * 1000 * FEED * AP                     # mm³/min
t_cut = V_removed / MRR
t_rough = dict((op, m) for op, m in route)["粗车 Rough turning"]

# 经济精度
econ = yaml.safe_load((H.ROOT / "factory" / "digital" / "std" / "econ_accuracy.yaml").read_text(encoding="utf-8"))
erows = [r for r in econ["rows"] if "IT_min" in r]

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.6, 3.2), gridspec_kw={"width_ratios": [1.0, 1.15]})
names = [op.split(" ")[0] for op, *_ in rows]
a0.barh(range(len(rows)), [c for *_, c in rows], color=H.C_MILL)
for i, (op, m, r, c) in enumerate(rows):
    a0.text(c + 0.3, i, f"{m:g} min × {r:g} " + T("美元/h", "USD/h"), va="center", fontsize=6.2)
a0.set_yticks(range(len(rows)))
a0.set_yticklabels(names, fontsize=6.8)
a0.invert_yaxis()
a0.set_xlabel(T("每件加工费 / 美元", "Cost per part / USD"), fontsize=7.5)
a0.set_xlim(0, max(c for *_, c in rows) * 1.6)
a0.tick_params(labelsize=6.5)
a0.set_title(T(f"(a) SH-301 各工序（材料 {mat:.2f} + 加工 {ops:.2f} 美元）", f"(a) SH-301 by operation (material {mat:.2f} + ops {ops:.2f} USD)"), fontsize=7.6)
for i, r in enumerate(erows):
    lab = T(f"{r['feature']}：{r['method_zh']}", r["method_en"])
    a1.plot([r["IT_min"], r["IT_max"]], [i, i], lw=6, color=H.C_SHEET if r["feature"] == "外圆" else H.C_AM, solid_capstyle="butt")
    a1.text(r["IT_max"] + 0.2, i, lab, va="center", fontsize=6.2)
for it, lab in ((6, T("轴承位等 k6、r6", "seats k6, r6")), (9, T("密封段 f9", "seal f9")), (14, T("一般公差 m", "general tol. m")),):
    a1.axvline(it, color=H.MUTED, lw=0.7, ls="--")
    a1.text(it + 0.1, -0.75, lab, fontsize=6.2, color=H.MUTED, ha="left")
a1.set_xlim(4.5, 17)
a1.set_ylim(len(erows) - 0.5, -1.1)
a1.set_yticks([])
a1.set_xlabel(T("经济加工精度（IT 等级）", "Economic accuracy (IT grade)"), fontsize=7.5)
a1.tick_params(labelsize=6.5)
a1.set_title(T("(b) 经济精度（数字工厂经济精度表）与 SH-301 的要求", "(b) Economic accuracy (factory table) vs SH-301"), fontsize=7.6)
fig.tight_layout()
figure(fig, "fig6_2_1")

grind = next(c for op, m, r, c in rows if op.startswith("磨外圆"))
out(mat=mat, ops=ops, total=total, t_total=t_total, n_ops=len(rows), grind=grind,
    rate_cnc=kpi.rate_per_hour(mrp.OP_UNITS["粗车 Rough turning"][0]), rate_grd=kpi.rate_per_hour(mrp.OP_UNITS["磨外圆 Cylindrical grinding"][0]),
    V_cm3=V_removed / 1000, vc=VC, f=FEED, ap=AP, mrr=MRR / 1000, t_cut=t_cut, t_rough=t_rough, cut_share=100 * t_cut / t_rough,
    D0=D0, n_seg=len(segs))
