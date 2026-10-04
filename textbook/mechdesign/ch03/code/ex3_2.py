"""3.2 剖视图与断面图：都由三维模型剖切生成——协作机器人关节空心轴 RJ-201（第 33.10 节的结构）的全剖视图，轴承座的半剖视图和局部剖视图，
SH-301 B 版键槽处的移出断面（图 3.2.1、3.2.2）。"""
import math

import numpy as np

import _ch3 as H
from bookout import T, figure, out, style

plt = style()
p = H.pillow_params("6207")
pb = H.pillow_block(p)
rj = H.rj201()
lay, Lrj, bore, _ = H.rj_layout()


def draw_section(sh, vis, hid, regs, dx=0.0, dy=0.0, hidden=False):
    sh.hatch(regs, dx, dy)
    if hidden:
        sh.polys(hid, "hidden", dx, dy)
    sh.polys(vis, "thick", dx, dy)


def wave(sh, x, z0, z1, amp=1.2, dx=0.0, dy=0.0):
    """波浪线（局部剖的分界，细实线）"""
    zz = np.linspace(z0, z1, 40)
    sh.polys([[(x + amp * math.sin((z - z0) / (z1 - z0) * 3 * math.pi), z) for z in zz]], "thin", dx, dy)


fig, ax = plt.subplots(figsize=(7.4, 2.1))
sh = H.Sheet(ax)                                         # 三个图画在同一个坐标系里，比例相同
# (a) RJ-201 全剖：剖切面过轴线，内孔和台阶都显出来
ya = p["H"]
v, h, r = H.section(rj, "front")
draw_section(sh, v, h, r, 0, ya)
sh.line((-5, ya), (Lrj + 5, ya), "center")
cap = dict(size=7.5, va="top")
sh.text(Lrj / 2, -8, T("(a) 全剖：RJ-201", "(a) Full section: RJ-201"), **cap)
# (b) 轴承座半剖：左半画外形，右半画剖视；分界是对称中心线
xb = Lrj + 60 + p["L"] / 2
v, h, r = H.section(pb, "front", keep="half")
draw_section(sh, v, h, r, xb, 0)
sh.line((xb, p["H"] - p["Ro"] - 4), (xb, p["H"] + p["Ro"] + 4), "center")
sh.line((xb - p["Ro"] - 4, p["H"]), (xb + p["Ro"] + 4, p["H"]), "center")
sh.text(xb, -8, T("(b) 半剖：轴承座", "(b) Half section: pillow block"), **cap)
# (c) 局部剖：只剖开右边的地脚孔，看到通孔；其余画外形
xc_ = xb + p["L"] + 25
x = p["Lh"] / 2
loc = (x - 12, p["L"] / 2 + 2, -1, p["tb"] + 1)
v, h, r = H.section(pb, "front", local=loc)
draw_section(sh, v, h, r, xc_, 0)
wave(sh, x - 12, 0, p["tb"], dx=xc_)
for xx in (-x, x):
    sh.line((xc_ + xx, -3), (xc_ + xx, p["tb"] + 3), "center")
sh.line((xc_, p["H"] - p["Ro"] - 4), (xc_, p["H"] + p["Ro"] + 4), "center")
sh.line((xc_ - p["Ro"] - 4, p["H"]), (xc_ + p["Ro"] + 4, p["H"]), "center")
sh.text(xc_, -8, T("(c) 局部剖：地脚孔", "(c) Local section: bolt hole"), **cap)
ax.autoscale()
ax.margins(0.02)
fig.tight_layout()
figure(fig, "fig3_2_1")

# ---- 图 3.2.2：SH-301 B 版的主视图（键槽朝向看图的人）与两个移出断面
sh301 = H.sh301b()
kw = H.sh301_keyways()
fig, ax = plt.subplots(figsize=(7.2, 2.5))
sh = H.Sheet(ax)
vis, hid = H.project(sh301, "front")
sh.polys(vis, "thick")
Ls = max(x for p_ in vis for x, _ in p_)
sh.line((-5, 0), (Ls + 5, 0), "center")
ydown = -60.0
names = ["A", "B"]
for (z0, z1, d, *_), nm in zip(kw, names):
    xc = (z0 + z1) / 2
    regs = H.cross_section(sh301, xc, view="left")
    # 断面在剖切位置的正下方（移出断面放在剖切线的延长线上，可以省略标注字母；这里仍标出以便对照）
    sh.hatch(regs, xc, ydown)
    for reg in regs:
        sh.polys([ring + [ring[0]] for ring in reg], "thick", xc, ydown)
    sh.line((xc - d / 2 - 3, ydown), (xc + d / 2 + 3, ydown), "center")
    sh.line((xc, ydown - d / 2 - 3), (xc, ydown + d / 2 + 3), "center")
    for k in (-1, 1):                                    # 剖切符号：剖切面两端的粗短画，外端的箭头指明投影方向（从左往右看），注字母
        y0_, y1_ = k * (d / 2 + 2), k * (d / 2 + 7)
        sh.raw_line((xc, y0_), (xc, y1_), "thick")
        sh.raw_line((xc, y1_), (xc + 6, y1_))
        sh.arrow((xc, y1_), (xc + 6, y1_), size=2.4)
        sh.text(xc + 7, y1_ + k * 1.2, nm, size=7.5, ha="left", va="bottom" if k > 0 else "top")
    sh.raw_line((xc, -d / 2 - 7), (xc, ydown + d / 2 + 8), "center")   # 剖切线的延长线：断面画在它上面
    sh.text(xc - 2, ydown + d / 2 + 2, f"{nm}–{nm}", size=7.5, ha="right", va="bottom")
ax.set_title(T("SH-301 B 版：主视图（键槽朝前）与键槽处的移出断面", "SH-301 rev. B: front view (keyseats facing the viewer) and removed sections"), fontsize=8.5)
ax.autoscale()
ax.margins(0.04)
fig.tight_layout()
figure(fig, "fig3_2_2")

out(rj_len=Lrj, rj_bore=bore, kg_L=kw[0][1] - kw[0][0], kc_L=kw[1][1] - kw[1][0])
