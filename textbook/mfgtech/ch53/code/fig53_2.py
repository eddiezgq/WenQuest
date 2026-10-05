"""53.2–53.6 节的三维图：测 H 与 d − t₁（图 53.2.1）、测量基准不重合与深度尺（图 53.4.1）、GR-203 插键槽后磨孔（图 53.5.1）、
SH-301 调头车左端面同时影响两个尺寸（图 53.5.2）、渗碳层与镀层（图 53.6.1）。
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


# ---- 图 53.2.1：(a) 工序 50 测 H：轴放在 V 形块上，刀口千分尺测杆伸进槽底，测砧顶下母线；(b) 工序 60 后测 d − t₁
def meas(state, r):
    q = A("测量")
    w = W.sh301(state)
    q.add(w)
    for p in micrometer(-r, z_bot, xk, blade=True).parts:
        q.add(p)
    return q
cm = {"dir": [0.35, -1.0, 0.3], "fit": [[xk - 60, -20, -60], [xk + 60, 60, 120]]}
pa = R.render_png(meas("op50", 20.15), 640, 560, camera=cm, section=((0, 0, 0), (0, -1, 0)), fontSize=19,
                  labels=[{"at": (xk, 0, z_bot + 2), "text": "刀口测杆压在槽底", "style": "text", "pos": [0.7, 0.1], "part": "测微螺杆"},
                          {"at": (xk, 0, -20.15 - 1), "text": "测砧顶精车外圆下母线", "style": "text", "pos": [0.7, 0.9], "part": "测砧"}])
pb = R.render_png(meas("op60", 20.0), 640, 560, camera=cm, section=((0, 0, 0), (0, -1, 0)), fontSize=19,
                  labels=[{"at": (xk, 0, -20.0 - 1), "text": "磨后外圆下母线", "style": "text", "pos": [0.7, 0.9], "part": "测砧"}])
R.compose("fig53_2_1", [pa, pb], 2, titles=["(a) 工序 50 测 H = 35.15（−0.03/−0.20）（剖开）", "(b) 工序 60 后测 d − t1 = 35（0/−0.2）（剖开）"])

# ---- 图 53.4.1：轴套：总长 A1 = 50，孔内台阶到内端面 A0 = 10 不好测，用深度尺从外端面测 A2 = 40
sl = A("轴套")
body = S.cyl("z", (0, 0), 30, 0, 50) - S.cyl("z", (0, 0), 20, 10, 51) - S.cyl("z", (0, 0), 12, -1, 11)
sl.add(P("轴套", body, "work"))
dg = S.box(-45, 45, -6, 6, 50, 58) + S.box(-19, -13, -2, 2, 10, 50) + S.box(30, 36, -4, 4, 58, 120)
sl.add(P("深度尺（尺身靠外端面，测杆伸到台阶）", dg, "#c9a24a"))
p4 = R.render_png(sl, 900, 640, camera={"dir": [0, -1, 0.25], "fit": [[-45, 0, -5], [45, 0, 125]]}, section=((0, 0, 0), (0, -1, 0)), fontSize=19,
                  dims=[{"a": (32, 0, 0), "b": (32, 0, 50), "off": (14, 0, 0), "text": "A₁ = 50（0/−0.17）"},
                        {"a": (-30, 0, 0), "b": (-30, 0, 10), "off": (-14, 0, 0), "text": "A₀ = 10", "color": red},
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
rod.add(P("镀铬层（放大画出）", S.cyl("x", (0, 0), 10.0, 0, 40) - S.cyl("x", (0, 0), 9.4, -1, 41), "#d8dde8"))
c3 = R.render_png(rod, 560, 460, camera={"dir": [0.6, -1.0, 0.5]}, section=((0, 0, 0), (0, -1, 0)), fontSize=18,
                  labels=[{"at": (30, 0, 9.7), "text": "镀层厚度的变动直接进入镀后直径", "style": "text", "pos": [0.5, 0.1], "part": "镀铬层"}])
R.compose("fig53_6_1", [c1, c2, c3], 3, titles=["(a) SH-101 轴承位渗碳后：层深 t1", "(b) 磨削后：层深 t0 = t1 − 磨去量", "(c) 活塞杆镀铬：镀后直径 = 镀前 + 2 × 镀层"])
out(n_fig3d=5)
