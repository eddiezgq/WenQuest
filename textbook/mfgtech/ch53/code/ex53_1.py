"""53.1 节：尺寸链图与增环、减环的判别（回路法）。图 53.1.1：左，SH-301 键槽深度 d − t₁ 的尺寸链（铣键槽后再磨外圆）；
右，SH-301 齿轮位长度 60 的轴向尺寸链（工序 40 以左、右端面为基准车轴肩）。程序按回路法判断增减环，并与工艺规程登记的尺寸链核对。"""
import _mfg as M
from bookout import T, figure, out, style

TL = M.tol()
p = M.plan()
ch = p["chains"][0]
links = {l["name"]: l for l in ch["links"]}

# 回路法：沿回路给每个环画一个箭头，与封闭环箭头同向的是减环，反向的是增环
# 键槽链：从槽底出发，向下 H 到精车外圆下母线（↓），向上精车半径到轴心（↑），向下磨削半径到磨后下母线（↓），封闭环从磨后下母线回到槽底（↑）
loop = [("H", -1), ("精车半径", +1), ("磨削半径", -1)]
closing_dir = +1
sense = {nm: (+1 if d != closing_dir else -1) for nm, d in loop}
assert sense["H"] == links["槽底尺寸 H（工序 50）"]["sense"] and sense["精车半径"] == links["精车齿轮位半径（工序 40）"]["sense"] \
    and sense["磨削半径"] == links["磨削齿轮位半径（工序 60）"]["sense"], "回路法的结论与工艺规程登记的增减环不一致"

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.6), gridspec_kw={"width_ratios": [1, 1.4]})
ax = axs[0]
yb1, yb2, yc, ys = 0.0, 4.0, 15.0, 27.0               # 精车下母线、磨后下母线、轴心、槽底（示意位置，磨削量放大画）
for y, lab, col in ((yb1, T("精车外圆下母线", "turned bottom line"), M.MUTED), (yc, T("轴心", "axis"), M.MUTED),
                    (ys, T("键槽底", "keyway bottom"), M.INK), (yb2, T("磨后下母线", "ground bottom line"), M.ACCENT)):
    ax.plot([-0.4, 3.6], [y, y], color=col, lw=0.7, ls="--" if col == M.MUTED else "-")
    ax.text(3.7, y, lab, fontsize=7, va="center", color=col)


def arr(ax, x, y0, y1, col, txt, lw=1.4):
    ax.annotate("", xy=(x, y1), xytext=(x, y0), arrowprops=dict(arrowstyle="-|>", color=col, lw=lw))
    ax.text(x + 0.08, (y0 + y1) / 2, txt, fontsize=7.5, color=col, va="center")


arr(ax, 0.2, ys, yb1, M.RED, "H ↓")
arr(ax, 1.0, yb1, yc, M.ACCENT, T("$r_1$ ↑", "$r_1$ ↑"))
arr(ax, 1.8, yc, yb2, M.RED, T("$r_2$ ↓", "$r_2$ ↓"))
arr(ax, 2.7, yb2, ys, M.INK, T("$A_0$ ↑", "$A_0$ ↑"), lw=2.0)
ax.text(-0.3, 32, T("红：与 $A_0$ 反向 → 增环\n蓝：与 $A_0$ 同向 → 减环", "red: against $A_0$ → increasing\nblue: with $A_0$ → decreasing"),
        fontsize=7, va="top")
ax.set_xlim(-0.5, 6.2); ax.set_ylim(-2, 33); ax.axis("off")
ax.set_title(T("(a) 键槽深度 d − t₁（放大，非比例）", "(a) keyway depth d − t₁ (schematic)"), fontsize=8)

ax = axs[1]
tc = p["tolerance_chart"]
pos = {"L": 0, "S1": 40, "S2": 52, "S3": 112, "S4": 137, "R": 167}
for k, x in pos.items():
    ax.plot([x, x], [0, 4.2], color=M.MUTED, lw=0.7)
    ax.text(x, 4.35, k, ha="center", fontsize=7.5)


def harr(ax, x0, x1, y, col, txt, lw=1.3):
    ax.annotate("", xy=(x1, y), xytext=(x0, y), arrowprops=dict(arrowstyle="-|>", color=col, lw=lw))
    ax.text((x0 + x1) / 2, y + 0.15, txt, fontsize=7.5, color=col, ha="center")


harr(ax, 0, 52, 3.2, M.ACCENT, T("52（工序 40，从 L 量）→", "52 (op 40, from L) →"))
harr(ax, 167, 0, 2.4, M.RED, T("← 167（总长）", "← 167 (overall)"))
harr(ax, 112, 167, 1.6, M.ACCENT, T("55（S3–R，从 R 量起）→", "55 (S3–R, from R) →"))
harr(ax, 52, 112, 0.6, M.INK, T("$A_0$ = 60 →", "$A_0$ = 60 →"), lw=2.0)
ax.set_xlim(-8, 178); ax.set_ylim(0, 4.8); ax.axis("off")
ax.set_title(T("(b) 齿轮位长度 60：沿回路 $A_0$ → 55 → 167 → 52 回到起点", "(b) gear-seat length 60: loop $A_0$ → 55 → 167 → 52"), fontsize=8)
fig.tight_layout()
figure(fig, "fig53_1_1")

# 齿轮位 60 的链：用跟踪图程序取出组成环；某环对封闭环的贡献 sense·nominal 为正是增环，为负是减环（与图中回路法一致）
r = TL.chart_from_plan(tc)
d60 = next(d for d in r["drawing"] if d["nominal"] == 60)
c60 = r["chart"].chain("S2", "S3")
out(n_links=len(links), H=links["槽底尺寸 H（工序 50）"]["nominal"], r1=links["精车齿轮位半径（工序 40）"]["nominal"],
    r2=links["磨削齿轮位半径（工序 60）"]["nominal"], A0=TL.extreme([M.link(l["name"], l["nominal"], l["es"], l["ei"], l["sense"])
                                                                                 for l in ch["links"]]).nominal,
    n60=len(c60), inc60="、".join(l.name for l in c60 if l.sense * l.nominal > 0), dec60="、".join(l.name for l in c60 if l.sense * l.nominal < 0))
assert [abs(l.nominal) for l in c60 if l.sense * l.nominal > 0] == [167]
