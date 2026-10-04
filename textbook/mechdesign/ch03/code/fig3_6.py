"""3.6 标准件与常用件的规定画法：螺纹（GB/T 4459.1）、齿轮（GB/T 4459.2）、滚动轴承（GB/T 4459.7）、弹簧（GB/T 4459.4），
尺寸取零件库（M12 螺栓、6207 轴承、1.6 × 14 × 40 压缩弹簧）与数字工厂（小齿轮 GR-203），图 3.6.1。"""
import csv
import math

import numpy as np

import _ch3 as H
import mdstd
from bookout import T, figure, out, style

LIB = H.ROOT / "library" / "catalog" / "A"


def spec(pid, size):
    with (LIB / pid / "specs.csv").open(encoding="utf-8") as f:
        return next(r for r in csv.DictReader(f) if r["size"] == size)


blt = spec("A-BLT-HEX", "M12x50")
spr = spec("A-SPR-CMP", "1.6x14x40")
d, P = float(blt["d_mm"]), float(blt["P_mm"])
d1 = d - 1.0825 * P                              # 外螺纹小径（GB/T 196：d1 = d − 1.0825P）
brg = mdstd.bearing("6207")
g = H.F.GEARS["GR-203"]
m, z = g["m"], g["z"]
dp, da, df = m * z, m * (z + 2), m * (z - 2.5)
th = np.linspace(0, 2 * math.pi, 120)

plt = style()
fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.6))
cap = dict(size=7.2, va="top")

# (a) 螺纹：外螺纹（不剖）与内螺纹（剖开的螺孔）
sh = H.Sheet(axs[0, 0])
L_ = 30.0
sh.polys([[(0, d / 2), (L_, d / 2)], [(0, -d / 2), (L_, -d / 2)], [(L_, -d / 2), (L_, d / 2)]], "thick")        # 大径：粗实线
sh.polys([[(4, d1 / 2), (L_ - 1, d1 / 2)], [(4, -d1 / 2), (L_ - 1, -d1 / 2)]], "thin")                           # 小径：细实线，画到螺纹终止线为止
sh.polys([[(4, -d / 2), (4, d / 2)]], "thick")                                                                     # 螺纹终止线
sh.line((-3, 0), (L_ + 3, 0), "center")
cx = L_ + 14                                                                                                       # 端视图：小径画约 3/4 圈细实线
sh.polys([[(cx + d / 2 * math.cos(t), d / 2 * math.sin(t)) for t in th]], "thick")
tt = np.linspace(math.radians(10), math.radians(280), 90)
sh.polys([[(cx + d1 / 2 * math.cos(t), d1 / 2 * math.sin(t)) for t in tt]], "thin")
sh.line((cx - d / 2 - 2, 0), (cx + d / 2 + 2, 0), "center")
sh.line((cx, -d / 2 - 2), (cx, d / 2 + 2), "center")
# 内螺纹：剖开的盲孔，小径粗实线、大径细实线，剖面线画到小径；钻孔底部 120° 锥
ox, oy = 0.0, -36.0
W_, D_ = 34.0, 22.0
dep_t, dep_d = 16.0, 20.0
blk = [(ox, oy - W_ / 2 + 0), (ox + D_, oy - W_ / 2), (ox + D_, oy + W_ / 2), (ox, oy + W_ / 2)]
cone = (d1 / 2) / math.tan(math.radians(60))
for k in (1, -1):
    reg = [(ox, oy + k * d1 / 2), (ox + dep_d, oy + k * d1 / 2), (ox + dep_d + cone, oy), (ox + D_, oy), (ox + D_, oy + k * W_ / 2), (ox, oy + k * W_ / 2)]
    sh.hatch([[reg]], spacing=1.6)
sh.polys([blk + [blk[0]]], "thick")
sh.polys([[(ox, oy + d1 / 2), (ox + dep_d, oy + d1 / 2), (ox + dep_d + cone, oy), (ox + dep_d, oy - d1 / 2), (ox, oy - d1 / 2)]], "thick")
sh.polys([[(ox + dep_t, oy - d1 / 2), (ox + dep_t, oy + d1 / 2)]], "thick")
sh.polys([[(ox, oy + d / 2), (ox + dep_t, oy + d / 2)], [(ox, oy - d / 2), (ox + dep_t, oy - d / 2)]], "thin")
sh.line((ox - 3, oy), (ox + D_ + 3, oy), "center")
sh.text(15, d / 2 + 2, T("外螺纹：大径粗、小径细", "external: major thick, minor thin"), size=6.5, va="bottom")
sh.text(cx, -d / 2 - 3, T("端视：小径约 3/4 圈", "end view: minor ≈ 3/4 circle"), size=6.5, va="top")
sh.text(ox + D_ + 4, oy, T("内螺纹（剖开）：\n小径粗、大径细，\n剖面线画到小径", "internal (in section):\nminor thick, major thin,\nhatch to the minor"), size=6.5, ha="left", va="center")
axs[0, 0].set_title(T(f"(a) 螺纹 M{d:g}（GB/T 4459.1）", f"(a) Thread M{d:g} (GB/T 4459.1)"), fontsize=8)

# (b) 齿轮：剖视（轮齿不剖）与端视（齿顶圆粗、分度圆点画线、齿根圆细或省略）
sh = H.Sheet(axs[0, 1])
bw, bore_ = 30.0, 20.0
for k in (1, -1):
    body = [(0, k * bore_ / 2), (bw, k * bore_ / 2), (bw, k * df / 2), (0, k * df / 2)]
    sh.hatch([[body]], spacing=2.2)
    sh.polys([body + [body[0]]], "thick")
    sh.polys([[(0, k * df / 2), (0, k * da / 2), (bw, k * da / 2), (bw, k * df / 2)]], "thick")
    sh.line((-3, k * dp / 2), (bw + 3, k * dp / 2), "center")
sh.line((-4, 0), (bw + 4, 0), "center")
cx = bw + 18 + da / 2
sh.polys([[(cx + da / 2 * math.cos(t), da / 2 * math.sin(t)) for t in th]], "thick")
sh.polys([[(cx + dp / 2 * math.cos(t), dp / 2 * math.sin(t)) for t in th]], "center")
sh.polys([[(cx + bore_ / 2 * math.cos(t), bore_ / 2 * math.sin(t)) for t in th]], "thick")
sh.line((cx - da / 2 - 3, 0), (cx + da / 2 + 3, 0), "center")
sh.line((cx, -da / 2 - 3), (cx, da / 2 + 3), "center")
sh.text(bw / 2, -da / 2 - 3, T("剖视：轮齿按不剖", "section: teeth not hatched"), size=6.5, va="top")
sh.text(cx, -da / 2 - 3, T("端视：齿根圆可省略", "end view: root circle omitted"), size=6.5, va="top")
axs[0, 1].set_title(T(f"(b) 齿轮 GR-203，m = {m}，z = {z}（GB/T 4459.2）", f"(b) Gear GR-203, m = {m}, z = {z} (GB/T 4459.2)"), fontsize=8)

# (c) 滚动轴承 6207：规定画法（上半）与通用画法（下半）
sh = H.Sheet(axs[1, 0])
dd, DD, BB = brg["d"], brg["D"], brg["B"]
t_r = (DD - dd) / 2 * 0.28
for r0, r1 in ((dd / 2, dd / 2 + t_r), (DD / 2 - t_r, DD / 2)):
    reg = [(0, r0), (BB, r0), (BB, r1), (0, r1)]
    sh.hatch([[reg]], spacing=1.6)
    sh.polys([reg + [reg[0]]], "thick")
rb = (DD - dd) / 4 * 0.75
ym = (dd + DD) / 4
H.ball(sh, BB / 2, ym, rb)
sh.polys([[(0, dd / 2), (0, DD / 2)], [(BB, dd / 2), (BB, DD / 2)]], "thick")
box = [(0, -dd / 2), (BB, -dd / 2), (BB, -DD / 2), (0, -DD / 2)]
sh.polys([box + [box[0]]], "thick")
sh.raw_line((BB / 2 - BB * 0.3, -ym), (BB / 2 + BB * 0.3, -ym), "thick")
sh.raw_line((BB / 2, -ym - (DD - dd) / 2 * 0.3), (BB / 2, -ym + (DD - dd) / 2 * 0.3), "thick")
sh.line((-5, 0), (BB + 5, 0), "center")
sh.polys([[(-6, dd / 2), (BB + 6, dd / 2)], [(-6, -dd / 2), (BB + 6, -dd / 2)]], "thin", color=H.MUTED)
sh.text(BB + 4, ym, T("规定画法：内外圈剖面线同向，滚动体画圆", "specified: rings hatched alike, ball as a circle"), size=6.5, ha="left", va="center")
sh.text(BB + 4, -ym, T("通用画法：矩形线框 + 正十字", "general: outline box + upright cross"), size=6.5, ha="left", va="center")
axs[1, 0].set_title(T(f"(c) 滚动轴承 6207（GB/T 4459.7）", "(c) Rolling bearing 6207 (GB/T 4459.7)"), fontsize=8)

# (d) 压缩弹簧：剖视，两端支承圈并紧磨平，中间各圈省略，用通过簧丝中心的点画线连起来
sh = H.Sheet(axs[1, 1])
dw, Dm, H0, n = float(spr["d_mm"]), float(spr["D_mm"]), float(spr["H0_mm"]), float(spr["n"])
n_tot = n + 2                                    # 两端各 1 圈支承圈（GB/T 4459.4 的画法按两端各 1.25 圈画，这里按 1 圈示意）
# 剖视（剖切面过轴线，拿走前半）：簧丝在上、下两处被剖到。按圈数 s 计，上面的截面在 s = 0, 1, 2…，下面的在 s = 0.5, 1.5…；
# 两端各 1 圈支承圈并紧（节距 = 簧丝直径）、端面磨平，中间是有效圈。看得见的是后半圈：从上面 s = k 连到下面 s = k + 0.5，斜向处处一致。
pitch = (H0 - 3 * dw) / n
s_end = n + 2


def xs_(s_):
    if s_ <= 1:
        return dw / 2 + dw * s_
    if s_ <= 1 + n:
        return 1.5 * dw + pitch * (s_ - 1)
    return 1.5 * dw + pitch * n + dw * (s_ - 1 - n)


shown = [k / 2 for k in range(int(2 * s_end) + 1) if k / 2 <= 2.5 or k / 2 >= s_end - 2.5]
for s_ in shown:
    yc = Dm / 2 if abs(s_ - round(s_)) < 1e-9 else -Dm / 2
    circ = [(xs_(s_) + dw / 2 * math.cos(t), yc + dw / 2 * math.sin(t)) for t in th]
    sh.hatch([[circ]], spacing=0.55)
    sh.polys([circ], "thick")
for s_ in shown:
    if abs(s_ - round(s_)) < 1e-9 and s_ + 0.5 in shown:
        for e in (-dw / 2, dw / 2):
            sh.raw_line((xs_(s_) + e, Dm / 2), (xs_(s_ + 0.5) + e, -Dm / 2), "thick")
tops = [x for x in shown if abs(x - round(x)) < 1e-9]
bots = [x for x in shown if abs(x - round(x)) > 1e-9]
gap_t = [a for a, b in zip(tops, tops[1:]) if b - a > 1]
gap_b = [a for a, b in zip(bots, bots[1:]) if b - a > 1]
for g, yc, lst in ((gap_t, Dm / 2, tops), (gap_b, -Dm / 2, bots)):
    for a in g:
        b = lst[lst.index(a) + 1]
        sh.line((xs_(a) + dw, yc), (xs_(b) - dw, yc), "center")
sh.line((-3, 0), (H0 + 3, 0), "center")
sh.dim((0, -Dm / 2 - dw), (H0, -Dm / 2 - dw), -4, f"H₀ = {H0:g}", size=6.5)
sh.text(H0 / 2, Dm / 2 + 4, T("中间各圈省略，用点画线连接簧丝中心", "middle coils omitted; centres joined by chain lines"), size=6.5)
axs[1, 1].set_title(T(f"(d) 压缩弹簧 {spr['size'].replace('x', '×')}（GB/T 4459.4）", f"(d) Compression spring {spr['size'].replace('x', '×')} (GB/T 4459.4)"), fontsize=8)
for a in axs.flat:
    a.autoscale()
    a.margins(0.06)
fig.tight_layout()
figure(fig, "fig3_6_1")

out(d=d, P=P, d1=d1, m=m, z=z, dp=dp, da=da, df=df, spr_d=dw, spr_D=Dm, spr_H0=H0, spr_n=n, spr_nt=n_tot)
