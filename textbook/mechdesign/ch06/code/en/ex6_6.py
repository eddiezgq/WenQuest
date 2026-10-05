"""Section 6.6 Design for manufacture: two designs of the servo bracket, machined and sheet metal (draft and revision), checked rule
by rule (Example 6.6.1, Figure 6.6.1). The rules are common empirical values (DFM handbooks and job-shop design guides), as taken in
this book; the values vary with the shop's equipment, so ask the shop before using them.
Set-ups for milling: blank lying flat, tool axis normal to the base plate; the inside (top face of the base plate, inner face of
the upright) is milled first, then the part is turned over for the outside. The inside corner between the two plates is a
"floor-to-wall" corner, whose radius is set by the corner radius of the tool (bull-nose or ball-nose cutter), so rule M1 requires
a corner radius that the tool library stocks."""
import _ch6 as H
from bookout import T, figure, out, style

CORNER_R = (0.5, 1.0, 2.0, 4.0)        # tool library set by this book: corner radii of bull-nose cutters, mm
CLEAR_M25 = (2.7, 2.9, 3.1)            # GB/T 5277: clearance holes for M2.5 screws (fine, medium, coarse)
t_m, t_s = 4.0, 2.0
D0 = {"r": 1.0}                        # sheet-metal draft: inner bend radius
D1 = {"r": H.sheet()["r"]}             # revision
# each rule: (code, rule, quantity, draft value, revised value, test function(value, design) -> (satisfied?, text of the limit))
MILL = [
    ("M1", T("底面与侧壁的内角 = 刀具库的刀尖圆角", "floor-to-wall corner = a stocked tool corner radius"), "r / mm", 2.5, H.milled()["r_in"],
     lambda v, d: (v in CORNER_R, "0.5/1/2/4")),
    ("M2", T("壁厚 ≥ 1 mm（铝）", "wall ≥ 1 mm (Al)"), "t / mm", t_m, t_m, lambda v, d: (v >= 1.0, "≥ 1")),
    ("M3", T("孔深 ≤ 4 倍孔径", "hole depth ≤ 4 × diameter"), "L/d", t_m / H.D_HOLE_UP, t_m / H.D_HOLE_UP, lambda v, d: (v <= 4, "≤ 4")),
    ("M4", T("螺钉通孔按 GB/T 5277", "clearance holes per GB/T 5277"), "Ø / mm", 2.6, H.D_HOLE_UP, lambda v, d: (v in CLEAR_M25, "2.7/2.9/3.1")),
    ("M5", T("装夹次数 ≤ 2（特征集中在两个方向）", "≤ 2 set-ups (features from two directions)"), T("次", "set-ups"), 3, H.milled()["setups"],
     lambda v, d: (v <= 2, "≤ 2")),
    ("M6", T("不注不必要的严公差（一般公差 m 级）", "no needless tight tolerances (general class m)"), T("严公差个数", "tight tols"), 6, 1,
     lambda v, d: (v <= 2, "≤ 2")),
]
SHEET = [
    ("S1", T("折弯内半径 ≥ 板厚", "inner bend radius ≥ thickness"), "r / mm", D0["r"], D1["r"], lambda v, d: (v >= t_s, f"≥ {t_s:g}")),
    ("S2", T("翻边长 ≥ 4t（按下模 V 口定）", "flange ≥ 4t (set by the die opening)"), "mm", 4.0, None, lambda v, d: (v >= 4 * t_s, f"≥ {4 * t_s:g}")),
    ("S3", T("孔到折弯线 ≥ 2t + r", "hole to bend line ≥ 2t + r"), "mm", 4.0, 10.0, lambda v, d: (v >= 2 * t_s + d["r"], f"≥ {2 * t_s + d['r']:g}")),
    ("S4", T("孔径 ≥ 板厚", "hole Ø ≥ thickness"), "Ø / mm", H.D_HOLE_UP, H.D_HOLE_UP, lambda v, d: (v >= t_s, f"≥ {t_s:g}")),
    ("S5", T("孔到边 ≥ 2t", "hole to edge ≥ 2t"), "mm", 3.0, 6.0, lambda v, d: (v >= 2 * t_s, f"≥ {2 * t_s:g}")),
    ("S6", T("所有折弯同一内半径（少换模）", "one inner radius for all bends"), T("种数", "radii"), 1, 1, lambda v, d: (v <= 1, "1")),
]


def run(rules, d0, d1):
    rows = []
    for c, name, unit, a, b, f in rules:
        oa, ca = f(a, d0)
        ob, cb = (True, "") if b is None else f(b, d1)          # None: the revision removed this feature
        rows.append((c, name, unit, a, b, oa, ob, ca, cb))
    return rows


rm, rs = run(MILL, {}, {}), run(SHEET, D0, D1)
n_fail_m0 = sum(not r[5] for r in rm)
n_fail_s0 = sum(not r[5] for r in rs)
n_fail_m1 = sum(not r[6] for r in rm)
n_fail_s1 = sum(not r[6] for r in rs)

plt = style()
fig, axs = plt.subplots(2, 1, figsize=(7.2, 4.6))
for ax, rows, ttl in ((axs[0], rm, T("(a) 铣削件", "(a) Machined bracket")), (axs[1], rs, T("(b) 钣金件", "(b) Sheet-metal bracket"))):
    ax.axis("off")
    cells = [[c, n, u, f"{a:.3g}", ca, "✓" if oa else "✗", T("取消", "removed") if b is None else f"{b:.3g}", cb, "✓" if ob else "✗"]
             for c, n, u, a, b, oa, ob, ca, cb in rows]
    tab = ax.table(cellText=cells, colLabels=["", T("规则", "Rule"), T("量", "Quantity"), T("初稿", "Draft"), T("判据", "Limit"), "",
                                              T("修改稿", "Revised"), T("判据", "Limit"), ""],
                   loc="center", cellLoc="center", colWidths=[0.05, 0.38, 0.1, 0.07, 0.11, 0.04, 0.09, 0.11, 0.04])
    tab.auto_set_font_size(False)
    tab.set_fontsize(6.0)
    tab.scale(1, 1.3)
    for (i, j), cell in tab.get_celld().items():
        cell.set_linewidth(0.3)
        if i > 0 and j in (5, 8):
            cell.get_text().set_color("#2ca02c" if cell.get_text().get_text() == "✓" else "#d62728")
    ax.set_title(ttl, fontsize=7.8)
fig.tight_layout()
figure(fig, "fig6_6_1")

out(n_m=len(rm), n_s=len(rs), n_fail_m0=n_fail_m0, n_fail_s0=n_fail_s0, n_fail_m1=n_fail_m1, n_fail_s1=n_fail_s1,
    t_s=t_s, flange_min=4 * t_s, hole_bend0=2 * t_s + D0["r"], hole_bend1=2 * t_s + D1["r"], r_in_m=H.milled()["r_in"], r_draft=1.0)
