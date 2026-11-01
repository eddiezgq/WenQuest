"""54.3 节的三维图：外圆磨床（图 54.3.1）；车床导轨在水平面、垂直面内的直线度误差与车出的工件（图 54.3.4）；
磨床尾座偏移与磨出的锥度（图 54.3.5）。误差放大画出（倍数写在图注里）；工件形状由 hub/accuracy.py 的公式算出后放大，
模型：factory/digital/models3d（machines.cylindrical_grinder、errors3d.lathe_between_centers、errors3d 的误差形状）。"""
import math

import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
X = M.x3d()
R = M.r3d()
Acc = M.acc()
A, P = C.Assembly, C.Part
blue, red, green = "#4f7fb8", "#c0504d", "#5a9e6f"
L = 167.0

# ---- 图 54.3.1：外圆磨床（工序 60）
g = MA.cylindrical_grinder(L=L, wheel_x=124.5, r_work=17.5)
g.add(W.sh301("op60"))
R.figure3d("fig54_3_1", g, 1400, 820, camera={"dir": [0.75, -1.2, 0.8]}, fontSize=17,
           labels=[{"at": (-150, 0, 20), "text": "头架（带动工件转）", "style": "text", "pos": [0.12, 0.25], "part": "头架"},
                   {"at": (L + 130, 0, 20), "text": "尾座", "style": "text", "pos": [0.5, 0.85], "part": "尾座"},
                   {"at": (0, -90, -230), "text": "工作台（纵向往复）", "style": "text", "pos": [0.15, 0.85], "part": "工作台"},
                   {"at": (124.5, 300, 150), "text": "砂轮", "style": "text", "pos": [0.55, 0.08], "part": "砂轮"},
                   {"at": (300, 250, 90), "text": "砂轮架（横向进给）", "style": "text", "pos": [0.8, 0.2], "part": "砂轮架"},
                   {"at": (60, -10, 10), "text": "工件 SH-301（两顶尖装夹）", "style": "text", "pos": [0.3, 0.12], "part": "SH-301"}])

# ---- 图 54.3.4：导轨直线度误差（放大 300 倍）：(a) 水平面内中凸 0.01 → 车出的工件中间小（鞍形）；(b) 垂直面内中凸 0.01 → 几乎没有影响
k = 300.0
dev = 0.01
n = 13
xs = [L * i / (n - 1) for i in range(n)]
bow = [dev * math.sin(math.pi * x / L) for x in xs]         # 刀尖轨迹偏离直线的量（中间最大）
r0 = 20.15


def guide_case(plane):
    q = A("导轨误差")
    lt = X.lathe_between_centers(L=L, r_work=r0, tool_x=L / 2)
    for p in lt.parts:
        if p.name in ("前顶尖", "后顶尖", "车刀"):
            q.add(p)
    if plane == "h":
        # 刀尖在水平面内向工件轴线靠近（−y 一侧的刀尖向 +y 移动）：半径变小 dev
        rs = [r0 - k * b for b in bow]
        trace_ys = [-r0 - 4 + k * b for b in bow]          # 画在工件外 4 mm，免得被工件挡住
        tr = X.bent_shaft(L=L, r=1.2, n=n, ys=trace_ys)
    else:
        rs = [r0 + k * (math.hypot(r0, b) - r0) for b in bow]   # 垂直面：半径只变 b²/2R，放大后仍看不出
        tr = S.move(S.rot(X.bent_shaft(L=L, r=1.2, n=n, ys=[k * b for b in bow]), ax=90), dy=-r0)
    q.add(P("刀尖轨迹（放大 300 倍）", tr, red))
    q.add(P("车出的工件（误差放大 300 倍）", X.profile_shaft(xs, rs), "work"))
    return q


cam = {"dir": [0.35, -1, 0.9], "fit": [[-10, -60, -40], [L + 10, 40, 60]]}
pa = R.render_png(guide_case("h"), 700, 480, camera={"dir": [0.12, -0.35, 1], "up": [0, 1, 0], "fit": [[-10, -60, -20], [L + 10, 40, 20]]}, fontSize=19,
                  labels=[{"at": (L / 2, -r0 - 4 + k * dev, 0), "text": "刀尖轨迹：在水平面内向轴线靠近 0.01", "style": "text", "pos": [0.5, 0.92], "part": "刀尖轨迹"},
                          {"at": (L / 2, -10, 14), "text": "中间小：Δd = 0.02", "style": "text", "pos": [0.5, 0.1], "part": "车出的工件"}])
pb = R.render_png(guide_case("v"), 700, 480, camera={"dir": [0.12, -1, 0.3], "fit": [[-10, -40, -40], [L + 10, 40, 40]]}, fontSize=19,
                  labels=[{"at": (L / 2, -r0, k * dev), "text": "刀尖轨迹：在垂直面内抬高 0.01", "style": "text", "pos": [0.5, 0.08], "part": "刀尖轨迹"},
                          {"at": (L / 2, -14, -10), "text": "直径几乎不变", "style": "text", "pos": [0.5, 0.92], "part": "车出的工件"}])
R.compose("fig54_3_4", [pa, pb], 2, titles=["(a) 导轨在水平面内弯曲（误差敏感方向）", "(b) 导轨在垂直面内弯曲（非敏感方向）"])

# ---- 图 54.3.5：外圆磨床尾座偏移（俯视）：后顶尖沿 y 离开砂轮 e，两顶尖连线与工作台运动方向不平行，磨出锥度（放大 500 倍）
e = 0.008
k2 = 500.0
xs2 = [L * i / 24 for i in range(25)]
r_head = 18.0                                               # 头架端的半径（放大后，为了看得清取 18）
rs2 = [r_head + k2 * e * x / L for x in xs2]                # 磨出的半径：离尾座越近越大，半径差 = e·x/L（放大）
xw = 124.5
gq = MA.cylindrical_grinder(L=L, wheel_x=xw, r_work=r_head, tail_offset=-k2 * e)   # 砂轮在 +y，走直线 y = r_head；尾座向 −y 偏（离开砂轮）
ang = math.degrees(math.atan2(k2 * e, L))
gq.add(P("磨出的工件（锥度放大 500 倍）", S.rot(X.profile_shaft(xs2, rs2), az=-ang), "work"))
dims = [{"a": (L + 8, 0, 30), "b": (L + 8, -k2 * e, 30), "off": (30, 0, 0), "text": "e", "color": red}]
R.figure3d("fig54_3_5", gq, 1400, 760, camera={"dir": [0.0, 0.0, 1], "up": [0, 1, 0], "fit": [[-70, -70, -30], [L + 70, 110, 30]]}, fontSize=18, dims=dims,
           arrows=[{"from": (-30, -50, 40), "to": (L + 30, -50, 40), "color": green, "text": "工作台运动方向（x），砂轮相对工件走直线", "textAt": "start", "dy": 26},
                   {"from": (-30, 30 * k2 * e / L, 40), "to": (L + 30, -(L + 30) * k2 * e / L, 40), "color": red, "text": "两顶尖连线（尾座偏移 e，放大）", "textAt": "end", "dx": -10, "dy": -12, "anchor": "end"}],
           labels=[{"at": (xw, 70, 30), "text": "砂轮", "style": "text", "pos": [0.62, 0.08], "part": "砂轮"},
                   {"at": (60, 0, 25), "text": "磨出锥形：尾座端大", "style": "text", "pos": [0.25, 0.08], "part": "磨出的工件"}])
out(k_guide=k, k_tail=k2)
