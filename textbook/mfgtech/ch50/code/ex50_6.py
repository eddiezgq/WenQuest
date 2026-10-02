"""50.6 节：加工余量与工序尺寸（算例 50.6.1 轴承位、50.6.2 齿轮位）——分析计算法从最后一道往前推，核对与工厂工艺规程一致；
图 50.6.1 各道工序的公差带与余量（轴承位）。"""
from matplotlib.patches import Rectangle

import _calc50 as C
import _mfg as M
from bookout import T, figure, out, style

b = C.sheet(35.0, 0.018, 0.002, "轴承位")
g = C.sheet(40.0, 0.018, 0.002, "齿轮位")
assert b.ok and g.ok
p = M.plan()
size = {(o["operation"].split(" ")[0], f["name"]): f["size_mm"] for o in p["operations"] for f in o.get("features") or []}
assert size[("精车", "轴承位")] == b.vals["a2"] and size[("粗车", "轴承位")] == b.vals["a1"]          # 与工厂工艺规程一致
assert size[("精车", "齿轮位")] == g.vals["a2"] and size[("粗车", "齿轮位")] == g.vals["a1"]
v = b.vals
# 实验 50.6 里嵌的标准公差与数字化标准表一致（实验页不能读文件，只能把数抄进程序；这里核对）
import json, re
from pathlib import Path
import stdtab
js = (Path(__file__).resolve().parents[1] / "lab" / "lab50_6.js").read_text(encoding="utf-8")
raw = re.search(r"const IT50 = (\{.*?\n\});", js, re.S).group(1)
lab_it = json.loads(re.sub(r",\s*}", "}", re.sub(r"(\d+):", r'"\1":', raw)))
itab = stdtab.table("it_grades")
for rng, grades in lab_it.items():
    lo_, hi_ = map(float, rng.split("-"))
    row = itab.find(size_over_mm=lo_, size_to_mm=hi_)
    for gr, val in grades.items():
        assert row[f"IT{gr}_um"] == val, (rng, gr)
rz1, ha1, rho1 = C.WQ_PS_01["精车后铣键槽"]
rz2, ha2, rho2 = C.WQ_PS_01["粗车后调质"]
out(**{k: v[k] for k in v}, **{"g_" + k: g.vals[k] for k in ("a1", "a2", "g3min", "g3max", "g2min", "g2max")},
    a2_raw=35.018 + v["z3"] + v["T2"], a1_raw=v["a2"] + v["z2"] + v["T1"], d_max=35.018, d_min=35.002,
    rz1=rz1, ha1=ha1, rho1=rho1, rz2=rz2, ha2=ha2, rho2=rho2, bar_d=50.0, rough_total=50.0 - v["a1"], gear_rough_from_bar=50.0 - g.vals["a1"])

# ---- 图 50.6.1：轴承位各道工序的直径公差带（横轴为直径），相邻两带之间的空隙就是余量
plt = style()
fig, ax = plt.subplots(figsize=(6.8, 2.8))
rows = [(T("粗车 A₁", "rough A₁"), v["a1"] - v["T1"], v["a1"], M.STAGE_COLOR["rough"]),
        (T("精车 A₂", "finish A₂"), v["a2"] - v["T2"], v["a2"], M.STAGE_COLOR["finish"]),
        (T("磨削 Ø35k6", "grind Ø35k6"), 35.002, 35.018, M.STAGE_COLOR["grind"])]
for i, (lab, lo, hi, c) in enumerate(rows):
    y = 2 - i
    ax.add_patch(Rectangle((lo, y - 0.25), hi - lo, 0.5, fc=c, ec="none", alpha=0.85))
    ax.text(34.93, y, lab, ha="right", va="center", fontsize=9.5, color=M.INK)
    ax.text(hi + 0.02, y, f"{lo:.3f}–{hi:.3f}", va="center", fontsize=8.5, color=M.MUTED)
for (y0, lo0, hi0), (y1, lo1, hi1), txt in (((1, v["a2"] - v["T2"], v["a2"]), (0, 35.002, 35.018), T("磨削余量", "grinding")),
                                            ((2, v["a1"] - v["T1"], v["a1"]), (1, v["a2"] - v["T2"], v["a2"]), T("精车余量", "finish turning"))):
    ax.annotate("", (lo0, (y0 + y1) / 2), (hi1, (y0 + y1) / 2), arrowprops=dict(arrowstyle="<->", color=M.INK, lw=0.8))
    ax.text((lo0 + hi1) / 2, (y0 + y1) / 2 + 0.12, txt + T("（最小）", " (min)"), ha="center", fontsize=8.5, color=M.INK)
ax.set_xlim(34.6, 36.75); ax.set_ylim(-0.6, 2.6)
ax.set_yticks([]); ax.set_xlabel(T("直径 / mm", "diameter / mm"), fontsize=9.5)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
figure(fig, "fig50_6_1")
