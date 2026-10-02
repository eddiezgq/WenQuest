"""50.2 节：SH-301 图纸的工艺分析——各主要表面的公差等级、粗糙度，以及最后一道工序必须用的加工方法（算例 50.2.1）；
图 50.2.1 SH-301 零件简图。"""
import math

from matplotlib.patches import Polygon, Rectangle

import _mfg as M
import stdtab
from bookout import T, figure, out, style
from hub import process

p = M.plan()
it = stdtab.table("it_grades")
econ = stdtab.table("econ_accuracy")
finish = econ.row("od_finish_turn")
res = {}
for d in p["drawing"]:
    tol = d["es_mm"] - d["ei_mm"]
    g = process.it_grade(d["size_mm"], tol)
    row = it.find(size_over_mm__lt=d["size_mm"], size_to_mm__ge=d["size_mm"])
    res[d["name"]] = dict(tol_um=round(tol * 1000), it=g, it_um=row[f"IT{g}_um"], lo=d["size_mm"] + d["ei_mm"], hi=d["size_mm"] + d["es_mm"], Ra=d["Ra_um"])
    assert res[d["name"]]["it_um"] == res[d["name"]]["tol_um"]          # k6 的公差带宽度正好是 IT6
    assert g < finish["IT_min"]                                         # 精车达不到：最后一道必须是磨削
b = res["轴承位"]; gsea = res["齿轮位"]
# 键槽宽 12N9：取自工厂检验模板（零件检验-输出轴）
kw = next(x for x in M.F.inspection_templates()["零件检验-输出轴"] if x["parameter"].startswith("键槽宽"))
kw_tol = kw["max"] - kw["min"]
kw_it = process.it_grade(12, kw_tol)
assert kw_it == 9
hb = next(x for x in M.F.inspection_templates()["零件检验-输出轴"] if "硬度" in x["parameter"])
out(b_lo=b["lo"], b_hi=b["hi"], b_it=b["it"], b_tol=b["tol_um"], g_lo=gsea["lo"], g_hi=gsea["hi"], g_it=gsea["it"],
    Ra=b["Ra"], fin_it_min=finish["IT_min"], fin_it_max=finish["IT_max"], fin_Ra_min=finish["Ra_min_um"], fin_Ra_max=finish["Ra_max_um"],
    kw_lo=kw["min"], kw_hi=kw["max"], kw_it=kw_it, kw_tol_um=round(kw_tol * 1000), hb_lo=hb["min"], hb_hi=hb["max"],
    econ_cite=econ.label(), it_cite=it.standard["code"])

# ---- 图 50.2.1：SH-301 零件简图（示意，不按比例标全部尺寸）
segs, key = M.segments()
plt = style()
fig, ax = plt.subplots(figsize=(7.0, 2.8))
z = 0
names = [T("密封位", "seal"), T("轴承位", "bearing"), T("齿轮位", "gear"), T("轴承位", "bearing"), T("联轴器位", "coupling")]
for i, (dd, L) in enumerate(segs):
    col = "#cfe3d6" if i in (1, 2, 3) else M.STEEL
    ax.add_patch(Rectangle((z, -dd / 2), L, dd, fc=col, ec=M.INK, lw=1.2))
    ax.text(z + L / 2 - (6 if i == 2 else 0), dd / 2 + 3.2, f"Ø{dd}" + ("k6" if i in (1, 2, 3) else ""), ha="center", fontsize=9.5, color=M.INK)
    ax.text(z + L / 2, -25, names[i], ha="center", fontsize=9, color=M.MUTED)
    if i == key["segment"]:
        k0 = z + (L - key["L"]) / 2
        ax.add_patch(Rectangle((k0, dd / 2 - key["t"]), key["L"], key["t"], fc="white", ec=M.INK, lw=1, hatch="///"))
        ax.annotate(T("键槽 12N9", "keyway 12N9"), (k0 + key["L"] * 0.8, dd / 2 - 1), (k0 + key["L"] * 0.55, dd / 2 + 11), fontsize=8.5,
                    color=M.INK, arrowprops=dict(arrowstyle="-", color=M.INK, lw=0.6))
    z += L
for x0 in (0, z):           # 两端中心孔（示意）
    s = 1 if x0 == 0 else -1
    ax.add_patch(Polygon([[x0, -2.5], [x0 + s * 5, 0], [x0, 2.5]], fc="white", ec=M.INK, lw=0.8))
ax.plot([-8, z + 8], [0, 0], color=M.MUTED, lw=0.8, ls=(0, (8, 3, 2, 3)))
ax.annotate("", (0, -30), (z, -30), arrowprops=dict(arrowstyle="<->", color=M.INK, lw=0.8))
ax.text(z / 2, -35.5, f"{z}", ha="center", fontsize=9, color=M.INK)
ax.text(z + 10, 14, T("调质 217–255 HB\n轴承位、齿轮位 Ra 0.8", "Q&T 217–255 HB\nbearing & gear seats Ra 0.8"), fontsize=9, color=M.INK, va="center")
ax.set_xlim(-12, z + 70); ax.set_ylim(-38, 36); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig50_2_1")
