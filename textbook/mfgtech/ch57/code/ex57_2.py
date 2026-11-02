"""算例 57.2.1、57.2.2：SH-101 三个磨削外圆（轴承位 Ø25 k6、密封轴颈 Ø24 h8、轴伸 Ø20 j6）的工序尺寸与余量——分析计算法从最后一道
往前推（_calc57.py），逐一核对与数字工厂的 SH-101 工艺规程（std/SH-101_process.yaml）一致。画图 57.2.1（轴承位各道的公差带）、
57.2.2（三个外圆的工序尺寸表）。"""
from matplotlib.patches import Rectangle

import _calc57 as C
import _mfg as M
from bookout import T, figure, out, style

P = M.plan101()
D = {d["name"]: d for d in P["drawing"]}
NAMES = ["轴承位", "密封轴颈", "轴伸"]
sh = {n: C.sheet(D[n]["size_mm"], D[n]["es_mm"], D[n]["ei_mm"], n) for n in NAMES}
assert all(s.ok for s in sh.values())
size = {(o["seq"], f["name"]): f for o in P["operations"] for f in o.get("features") or []}
for n, s in sh.items():                                   # 与工厂工艺规程一致
    assert abs(size[(30, n)]["size_mm"] - s.vals["a2"]) < 1e-9 and abs(size[(20, n)]["size_mm"] - s.vals["a1"]) < 1e-9, n
v = sh["轴承位"].vals
d = D["轴承位"]
dmax, dmin = d["size_mm"] + d["es_mm"], d["size_mm"] + d["ei_mm"]

plt = style()
fig, ax = plt.subplots(figsize=(6.8, 2.7))
rows = [(T("粗车 A₁（工序 20）", "rough A₁ (op 20)"), v["a1"] - v["T1"], v["a1"], "#8aa4bd"),
        (T("半精车 A₂（工序 30）", "semi A₂ (op 30)"), v["a2"] - v["T2"], v["a2"], M.ACCENT),
        (T("磨削 Ø25 k6（工序 70）", "grind Ø25 k6 (op 70)"), dmin, dmax, M.WARM)]
for i, (lab, lo, hi, c) in enumerate(rows):
    y = 2 - i
    ax.add_patch(Rectangle((lo, y - 0.25), hi - lo, 0.5, fc=c, ec="none", alpha=0.9))
    ax.text(24.93, y, lab, ha="right", va="center", fontsize=8.5, color=M.INK)
    ax.text(hi + 0.02, y, f"{lo:.3f}–{hi:.3f}", va="center", fontsize=7.5, color=M.MUTED)
for (y0, lo0), (y1, hi1), txt, need in (((1, v["a2"] - v["T2"]), (0, dmax), T("磨削余量", "grinding"), v["z3"]),
                                         ((2, v["a1"] - v["T1"]), (1, v["a2"]), T("半精车余量", "semi-finishing"), v["z2"])):
    ax.annotate("", (lo0, (y0 + y1) / 2), (hi1, (y0 + y1) / 2), arrowprops=dict(arrowstyle="<->", color=M.INK, lw=0.8))
    ax.text((lo0 + hi1) / 2, (y0 + y1) / 2 + 0.12, txt + T(f" 最小 {lo0 - hi1:.3f}（需 {need:.3f}）", f" min {lo0 - hi1:.3f} (need {need:.3f})"),
            ha="center", fontsize=7.5, color=M.INK)
ax.set_xlim(24.2, 26.75); ax.set_ylim(-0.6, 2.6)
ax.set_yticks([]); ax.set_xlabel(T("直径 / mm", "diameter / mm"))
for s_ in ("top", "right", "left"):
    ax.spines[s_].set_visible(False)
figure(fig, "fig57_2_1")

FIT = {"轴承位": "k6", "密封轴颈": "h8", "轴伸": "j6"}


def dev(x):
    return "0" if abs(x) < 1e-12 else f"{x:+g}".replace("-", "−")


HEAD = [T("外圆", "surface"), T("粗车 A₁（工序 20）", "rough A₁"), T("半精车 A₂（工序 30）", "semi A₂"), T("磨削（图纸）", "grind (drawing)"),
        T("磨削余量", "grind stock"), T("半精车余量", "semi stock")]
rows = []
for n in NAMES:
    s = sh[n].vals
    dd = D[n]
    rows.append([n, f"Ø{s['a1']:g} 0/−{s['T1']:g}", f"Ø{s['a2']:g} 0/−{s['T2']:g}",
                 f"Ø{dd['size_mm']:g} {FIT[n]}（{dev(dd['es_mm'])}/{dev(dd['ei_mm'])}）", f"{s['g3min']:.3f}–{s['g3max']:.3f}", f"{s['g2min']:.2f}–{s['g2max']:.2f}"])
M.table_fig(plt, HEAD, rows, [0.12, 0.17, 0.18, 0.2, 0.17, 0.16], "fig57_2_2", fontsize=7)

out(**v, dmax=dmax, dmin=dmin, a2_raw=dmax + v["z3"] + v["T2"], a1_raw=v["a2"] + v["z2"] + v["T1"], bar_d=60.0,
    rough_total=60.0 - v["a1"], **{f"{k}_{i}": sh[n].vals[k] for i, n in enumerate(NAMES) for k in ("a1", "a2", "g3min", "g3max", "g2min", "g2max")})
