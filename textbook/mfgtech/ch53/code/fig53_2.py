"""53.2–53.6 节的三维图：测 H 与 d − t₁（图 53.2.1）、测量基准不重合与深度尺（图 53.4.1）、GR-203 插键槽后磨孔（图 53.5.1）、
渗碳层与镀层（图 53.6.1）。
模型：factory/digital/models3d；量具、齿轮等是简化的示意模型，与算例的尺寸一致；余量、层深按需要放大画出，图注写明。"""
import math

import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
A, P = C.Assembly, C.Part
blue, red, green, orange = "#4f7fb8", "#c0504d", "#5a9e6f", "#d98c3a"
k = W.plan()["part"]["keyway"]
xk = 52.0 + float(k["offset_mm"]) + float(k["L"]) / 2
b, z_bot = float(k["b"]), 20.0 - float(k["t"])


def micrometer(z_lo, z_hi, x, y=0.0, blade=False):
    """外径千分尺（竖直放置，简化）：固定测砧端面在 z_lo（向上），测微螺杆端面在 z_hi（向下）。blade：刀口形测杆（伸进键槽）。"""
    q = A("千分尺")
    g = 18.0
    frame = S.box(x - 5, x + 5, y + 48, y + 60, z_lo - g - 12, z_hi + g + 25) + S.box(x - 5, x + 5, y, y + 60, z_lo - g - 12, z_lo - g) \
        + S.box(x - 5, x + 5, y, y + 60, z_hi + g + 13, z_hi + g + 25)
    q.add(P("尺架", frame, "#c9a24a", tags=("nocut",)))
    q.add(P("测砧", S.cyl("z", (x, y), 3.2, z_lo - g, z_lo), "hardened", tags=("nocut",)))
    sp = S.box(x - 1.0, x + 1.0, y - 4, y + 4, z_hi, z_hi + g) if blade else S.cyl("z", (x, y), 3.2, z_hi, z_hi + g)
    q.add(P("测微螺杆", sp + S.cyl("z", (x, y), 3.2, z_hi + g, z_hi + g + 13), "hardened", tags=("nocut",)))
    q.add(P("微分筒", S.cyl("z", (x, y), 8, z_hi + g + 13, z_hi + g + 60), "steel", tags=("nocut",)))
    return q


# ---- 图 53.2.1：(a) 工序 50 用键槽深度专用量规 G07 测 H（C 形量规：测砧顶精车外圆下母线，测头伸进槽底，示意）；
# (b) 检验 C5 用深度千分尺 G11 测槽深 t₁（底座跨在键槽两侧的外圆上），d − t₁ = 实测外圆直径 d − t₁
def meas_H():
    q = A("测 H")
    q.add(W.sh301("op50"))
    for p in micrometer(-20.15, z_bot, xk, blade=True).parts:
        q.add(p)
    return q
def meas_t():
    q = A("测 t1")
    q.add(W.sh301("op60"))
    zb = (20.0 ** 2 - (b / 2) ** 2) ** 0.5             # 键槽两侧外圆的最高点
    q.add(P("深度千分尺底座（跨在键槽两侧的外圆上）", S.box(xk - 6, xk + 6, -22, 22, zb, zb + 8), "#c9a24a", tags=("nocut",)))
    q.add(P("测杆", S.cyl("z", (xk, 0), 1.5, z_bot, zb + 8), "hardened", tags=("nocut",)))
    q.add(P("测微头", S.cyl("z", (xk, 0), 6, zb + 8, zb + 30) + S.cyl("z", (xk, 0), 9, zb + 30, zb + 60), "steel", tags=("nocut",)))
    return q, zb
cm = {"dir": [0.35, -1.0, 0.3], "fit": [[xk - 60, -20, -60], [xk + 60, 60, 120]]}
pa = R.render_png(meas_H(), 640, 560, camera=cm, section=((0, 0, 0), (0, -1, 0)), fontSize=19,
                  dims=[{"a": (xk - 20, 0, -20.15), "b": (xk - 20, 0, z_bot), "off": (-8, 0, 0), "text": "H"}],
                  labels=[{"at": (xk, 0, z_bot + 2), "text": "测头伸进槽底", "style": "text", "pos": [0.7, 0.1], "part": "测微螺杆"},
                          {"at": (xk, 0, -20.15 - 1), "text": "测砧顶精车外圆下母线", "style": "text", "pos": [0.7, 0.9], "part": "测砧"}])
qt, zb = meas_t()
cm2 = {"dir": [0.35, -1.0, 0.3], "fit": [[xk - 60, -20, -40], [xk + 60, 30, 100]]}
pb = R.render_png(qt, 640, 560, camera=cm2, section=((0, 0, 0), (0, -1, 0)), fontSize=19,
                  dims=[{"a": (xk - 20, 0, z_bot), "b": (xk - 20, 0, 20.0), "off": (-8, 0, 0), "text": "t₁"},
                        {"a": (xk + 28, 0, -20.0), "b": (xk + 28, 0, 20.0), "off": (10, 0, 0), "text": "d（实测）"}],
                  labels=[{"at": (xk + 5, -22, zb + 4), "text": "底座跨在键槽两侧的外圆上", "style": "text", "pos": [0.5, 0.1], "part": "深度千分尺底座"}])
R.compose("fig53_2_1", [pa, pb], 2, titles=["(a) 工序 50：键槽深度专用量规 G07 测 H（示意，剖开）", "(b) 检验 C5：深度千分尺 G11 测 t1，d − t1 = 实测 d − t1（剖开）"])

# ---- 图 53.4.1：轴套：总长 A1 = 50，孔内台阶到内端面 A0 = 10 不好测，用深度尺从外端面测 A2 = 40
sl = A("轴套")
body = S.cyl("z", (0, 0), 30, 0, 50) - S.cyl("z", (0, 0), 20, 10, 51) - S.cyl("z", (0, 0), 12, -1, 11)
sl.add(P("轴套", body, "work"))
dg = S.box(-45, 45, -6, 6, 50, 58) - S.box(-19.5, -12.5, -2.5, 2.5, 49, 59)            # 尺框：靠在外端面上
sl.add(P("深度尺尺框（靠外端面）", dg, "#c9a24a"))
sl.add(P("深度尺尺身（穿过尺框，下端碰台阶）", S.box(-19, -13, -2, 2, 10, 120), "hardened"))
p4 = R.render_png(sl, 900, 640, camera={"dir": [0, -1, 0.25], "fit": [[-55, 0, -25], [45, 0, 125]]}, section=((0, 0, 0), (0, -1, 0)), fontSize=19,
                  dims=[{"a": (32, 0, 0), "b": (32, 0, 50), "off": (14, 0, 0), "text": "A₁ = 50（0/−0.17）"},
                        {"a": (-30, 0, 0), "b": (-30, 0, 10), "off": (-14, 0, 0), "text": "A₀ = 10（0/−0.36）", "color": red},
                        {"a": (-13, 0, 10), "b": (-13, 0, 50), "off": (8, 0, 0), "text": "A₂（深度尺）", "color": blue}],
                  labels=[{"at": (-20, 0, 10), "text": "孔内台阶", "style": "text", "pos": [0.15, 0.5], "part": "轴套"}])
R.save_figure("fig53_4_1", p4, 900, 640)

# ---- 图 53.5.1：GR-203 孔与键槽：精车孔 Ø34.6、插键槽 A、磨孔 Ø35（磨削余量放大）；齿轮简化成 20 个齿的齿圈
def gear_outline(z=20, ra=48.0, rf=40.0):
    pts = []
    for i in range(z):
        a0 = 2 * math.pi * i / z
        for da, r in ((-0.30, rf), (-0.14, ra), (0.14, ra), (0.30, rf)):
            a = a0 + da * 2 * math.pi / z
            pts.append((r * math.cos(a), r * math.sin(a)))
    return pts
g = A("GR-203")
R1d, R2d = 15.5, 17.5                      # 画出来的精车孔、磨后孔半径（放大）
gear = S.prism("yz", gear_outline(), -12, 12) - S.cyl("x", (0, 0), R1d, -13, 13) - S.box(-13, 13, -5, 5, 0, R2d + 3.8)
core = gear - S.cyl("x", (0, 0), R2d, -14, 14)
g.add(P("齿轮（插键槽后、磨孔后）", core, "work"))
g.add(P("磨去的一层（放大画出）", gear & S.cyl("x", (0, 0), R2d, -14, 14), red, opacity=0.55))
p5 = R.render_png(g, 760, 640, camera={"dir": [-1, 0, 0], "fit": [[0, -50, -50], [0, 50, 50]]}, section=((0, 0, 0), (1, 0, 0)), fontSize=18,
                  dims=[{"a": (0, 2, -R1d), "b": (0, 2, R2d + 3.8), "off": (0, 0, 0), "text": "A（插键槽）"},
                        {"a": (0, -2, -R2d), "b": (0, -2, R2d + 3.8), "off": (0, -6, 0), "text": "d + t₂（封闭环）", "color": red}],
                  points=[{"at": (0, 0, 0), "r": 4, "color": "#1d2327"}, {"at": (0, 0, -R1d), "r": 5, "color": blue, "text": "精车孔对面母线", "dx": -175, "dy": 6},
                          {"at": (0, 0, -R2d), "r": 5, "color": red, "text": "磨后孔对面母线", "dx": 10, "dy": 22}])
R.save_figure("fig53_5_1", p5, 760, 640)

# ---- 图 53.6.1：(a) SH-101 轴承位渗碳层：渗碳后（层深 t₁）、磨后（t₀）；(b) 活塞杆镀铬
def case(r_out, layer_in, L=40):
    q = A("渗碳层")
    q.add(P("心部", S.cyl("x", (0, 0), layer_in, 0, L), "work"))
    q.add(P("渗碳层", S.cyl("x", (0, 0), r_out, 0, L) - S.cyl("x", (0, 0), layer_in, -1, L + 1), "#7a5c8f"))
    return q
cc = {"dir": [0.6, -1.0, 0.5], "fit": [[0, -15, -15], [40, 15, 15]]}
# 放大：半径 12.7 → 画成 12.7；层深 1.2（磨前）→ 磨去 0.2 后 1.0。为看清，层深和磨削量都放大 2.5 倍
s_ = 2.5
r_pre, r_post, inner = 12.7, 12.7 - 0.2 * s_, 12.7 - 1.2 * s_
c1 = R.render_png(case(r_pre, inner), 560, 460, camera=cc, section=((0, 0, 0), (0, -1, 0)), fontSize=18,
                  labels=[{"at": (20, 0, (inner + r_pre) / 2), "text": "渗碳层 t1（磨前，层深放大画出）", "style": "text", "pos": [0.5, 0.1], "part": "渗碳层"}])
c2 = R.render_png(case(r_post, inner), 560, 460, camera=cc, section=((0, 0, 0), (0, -1, 0)), fontSize=18,
                  labels=[{"at": (20, 0, (inner + r_post) / 2), "text": "磨后层深 t0：变薄了", "style": "text", "pos": [0.5, 0.1], "part": "渗碳层"}])
rod = A("镀铬")
rod.add(P("活塞杆（镀前磨削）", S.cyl("x", (0, 0), 10.0 - 0.6, -20, 40), "steel"))
rod.add(P("镀铬层（放大画出）", S.cyl("x", (0, 0), 10.0, 0, 40) - S.cyl("x", (0, 0), 9.4, -1, 41), "#3f7fbf"))
c3 = R.render_png(rod, 560, 460, camera={"dir": [0.6, -1.0, 0.5]}, section=((0, 0, 0), (0, -1, 0)), fontSize=18,
                  dims=[{"a": (40, 0, -10), "b": (40, 0, 10), "off": (8, 0, 0), "text": "D"}, {"a": (-20, 0, -9.4), "b": (-20, 0, 9.4), "off": (-8, 0, 0), "text": "D₁"}],
                  labels=[{"at": (30, 0, 9.7), "text": "镀层厚度的变动直接进入镀后直径", "style": "text", "pos": [0.5, 0.1], "part": "镀铬层"}])
R.compose("fig53_6_1", [c1, c2, c3], 3, titles=["(a) SH-101 轴承位渗碳后：层深 t1", "(b) 磨削后：层深 t0 = t1 − 磨去量", "(c) 活塞杆镀铬：镀后直径 = 镀前 + 2 × 镀层"])
out(n_fig3d=5)
