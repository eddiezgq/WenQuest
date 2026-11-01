"""54.1 节的三维图：SH-301 的尺寸、形状、位置精度（图 54.1.1）；获得尺寸精度的四种方法（图 54.1.2）；
车床两顶尖车外圆时的误差敏感方向（图 54.1.3）。
模型：factory/digital/models3d（SH-301 由工艺规程数据生成；车床、磨床、量具是简化的示意模型）。"""
import math

import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
X = M.x3d()
R = M.r3d()
A, P = C.Assembly, C.Part
blue, red, green, orange = "#4f7fb8", "#c0504d", "#5a9e6f", "#d98c3a"
ISO = M.ISO

# ---- 图 54.1.1：SH-301 磨后（工序 60）：尺寸 Ø35 k6、形状（圆柱度）、位置（径向圆跳动对 A–B）
w = A("SH-301")
w.add(W.sh301("op60"))
xl, xr = 46.0, 124.5                      # 左、右轴承位中点（与 sim/errors.py 的 Z_LEFT、Z_RIGHT 相同）
R.figure3d("fig54_1_1", w, 1400, 620, camera={"dir": [0.25, -1, 0.45], "fit": [[-5, -30, -40], [172, 30, 40]]}, fontSize=17,
           dims=[{"a": (xl, 0, -17.5), "b": (xl, 0, 17.5), "off": (0, -60, 0), "text": "尺寸：Ø35 k6", "color": blue}],
           labels=[{"at": (xl - 3, -12, 12), "text": "形状：圆度、圆柱度（轴承位）", "style": "text", "pos": [0.18, 0.12], "part": "SH-301"},
                   {"at": (xr, -14, 10), "text": "位置：径向圆跳动 0.012（对公共轴线 A–B）", "style": "text", "pos": [0.72, 0.12], "part": "SH-301"},
                   {"at": (82, -20, 0), "text": "齿轮位 Ø40 k6", "style": "text", "pos": [0.5, 0.92], "part": "SH-301"}])

# ---- 图 54.1.2：获得尺寸精度的四种方法
def micrometer_y(x, r, z=0.0):
    """外径千分尺（测砧和测微螺杆沿 y 方向夹住直径），尺架在 −z 一侧。"""
    q = A("千分尺")
    g = 14.0
    frame = S.box(x - 5, x + 5, -r - g - 10, r + g + 10, z - r - 60, z - r - 48) + S.box(x - 5, x + 5, -r - g - 10, -r - g, z - r - 60, z) \
        + S.box(x - 5, x + 5, r + g, r + g + 10, z - r - 60, z)
    q.add(P("尺架", frame, "#3d5a80", tags=("nocut",)))
    q.add(P("测砧", S.cyl("y", (x, z), 3.2, -r - g, -r), "hardened", tags=("nocut",)))
    q.add(P("测微螺杆", S.cyl("y", (x, z), 3.2, r, r + g) + S.cyl("y", (x, z), 7, r + g + 10, r + g + 55), "steel", tags=("nocut",)))
    return q


# (a) 试切法：车一小段、量、调刀、再车（只画两顶尖、工件、车刀和千分尺）
L = 167.0
lt = X.lathe_between_centers(L=L, r_work=20.15, tool_x=148.0)
wk = A("试切")
for p in lt.parts:
    if p.name in ("前顶尖", "后顶尖", "车刀"):
        wk.add(p)
body = S.cyl("x", (0, 0), 21.0, 0, 150) + S.cyl("x", (0, 0), 20.15, 150, L)
wk.add(P("工件（右端试切了一小段）", body, "work"))
for p in micrometer_y(160.0, 20.15).parts:
    wk.add(p)
cam_a = {"dir": [0.35, -1, 0.5], "fit": [[60, -60, -90], [L + 30, 60, 40]]}
pa = R.render_png(wk, 700, 520, camera=cam_a, fontSize=19,
                  labels=[{"at": (160, 0, -82), "text": "千分尺量试切的直径", "style": "text", "pos": [0.66, 0.9], "part": "尺架"},
                          {"at": (155, -14, 15), "text": "试切一小段", "style": "text", "pos": [0.55, 0.12], "part": "工件"},
                          {"at": (148, -40, 0), "text": "车刀：按读数调刀，再车全长", "style": "text", "pos": [0.42, 0.78], "part": "车刀"}])

# (b) 调整法：按样件或首件调好刀具位置（行程挡块、刀补），整批不再试切
wb = A("调整法")
lt2 = X.lathe_between_centers(L=L, r_work=20.15, tool_x=82.0)
for p in lt2.parts:
    if p.name in ("床身", "导轨", "导轨（后）", "前顶尖", "后顶尖", "拨盘", "尾座", "床鞍", "中滑板", "刀架", "车刀"):
        wb.add(p)
wb.add(P("工件", S.cyl("x", (0, 0), 20.15, 0, L), "work"))
wb.add(P("横向挡块（调好后锁紧）", S.box(40, 124, -268, -238, -215, -185), red))
wb.add(P("纵向挡块", S.box(L + 10, L + 40, -230, -160, -270, -230), red))
pb = R.render_png(wb, 700, 520, camera={"dir": [0.6, -1, 0.75], "fit": [[-60, -280, -300], [L + 120, 120, 60]]}, fontSize=19,
                  labels=[{"at": (100, -250, -190), "text": "挡块：首件调好，整批不再调", "style": "text", "pos": [0.5, 0.92], "part": "横向挡块"}])

# (c) 定尺寸刀具法：孔的尺寸由铰刀的尺寸保证
wc = A("定尺寸刀具法")
blk = S.box(-40, 40, -40, 40, -30, 0) - S.cyl("z", (0, 0), 10, -31, 1)
wc.add(P("工件（剖开）", blk, "work"))
ream = S.cyl("z", (0, 0), 10, -26, 60) + S.cyl("z", (0, 0), 7, 60, 120)
for k in range(6):
    a0 = 2 * math.pi * k / 6
    ream = ream - S.rot(S.box(9.0, 12, -1.2, 1.2, -27, 58), az=math.degrees(a0))
wc.add(P("铰刀 Ø20 H7", ream, "tool", tags=("nocut",)))
pc = R.render_png(wc, 700, 520, camera={"dir": [0.7, -1, 0.6], "fit": [[-50, -50, -40], [50, 50, 125]]}, section=((0, 0, 0), (0, -1, 0)), fontSize=19,
                  labels=[{"at": (8, 0, 90), "text": "孔径由刀具尺寸决定", "style": "text", "pos": [0.75, 0.15], "part": "铰刀"}])

# (d) 自动控制法：外圆磨床上的主动测量（两点测头在线量直径，到尺寸自动停止进给）
wd = MA.cylindrical_grinder(L=L, wheel_x=124.5, r_work=17.5)
wd.add(W.sh301("op60"))
for sgn in (1, -1):                       # 两个测爪从前方（−y）伸过来，上下夹住直径
    zt = sgn * 17.5
    wd.add(P("测爪" + ("上" if sgn > 0 else "下"), S.box(122, 127, -3, 3, min(zt, zt + sgn * 10), max(zt, zt + sgn * 10))
             + S.box(122, 127, -70, 3, min(zt + sgn * 10, zt + sgn * 16), max(zt + sgn * 10, zt + sgn * 16)), "hardened"))
wd.add(P("主动测量仪", S.box(116, 133, -120, -70, -45, 45), "#3d5a80"))
pd = R.render_png(wd, 700, 520, camera={"dir": [0.55, -1, 0.5], "fit": [[20, -160, -120], [230, 260, 140]]}, fontSize=19,
                  labels=[{"at": (124.5, -95, 40), "text": "主动测量仪：测爪在线量直径，到尺寸停止进给", "style": "text", "pos": [0.5, 0.95], "part": "主动测量仪"},
                          {"at": (124.5, 150, 120), "text": "砂轮", "style": "text", "pos": [0.88, 0.12], "part": "砂轮"}])
R.compose("fig54_1_2", [pa, pb, pc, pd], 2, titles=["(a) 试切法：试切—测量—调刀—再试切", "(b) 调整法：按首件调好刀具位置，整批加工",
                                                  "(c) 定尺寸刀具法：铰孔（剖开）", "(d) 自动控制法：外圆磨床的主动测量"])

# ---- 图 54.1.3：车床两顶尖车外圆，刀尖在法向（y，水平面）与切向（z，垂直面）的偏移
lt3 = X.lathe_between_centers(L=L, r_work=20.15, tool_x=120.0)
lt3.add(P("工件", S.cyl("x", (0, 0), 20.15, 0, L), "work"))
tip = lt3.anchors["tip"]
R.figure3d("fig54_1_3", lt3, 1400, 760, camera={"dir": [0.55, -1, 0.6], "fit": [[50, -110, -70], [190, 30, 60]]}, fontSize=18,
           arrows=[{"from": tip, "to": (tip[0], tip[1] - 45, 0), "color": red, "text": "y：法向（误差敏感方向）", "textAt": "end", "dx": -10, "dy": 26, "anchor": "end"},
                   {"from": tip, "to": (tip[0], tip[1], 45), "color": blue, "text": "z：切向（非敏感方向）", "textAt": "end"},
                   {"from": (tip[0] + 6, tip[1] - 6, -16), "to": (tip[0] + 50, tip[1] - 6, -16), "color": green, "text": "x：纵向进给", "textAt": "end", "dy": 22}],
           labels=[{"at": (60, -14, 14), "text": "工件（两顶尖装夹）", "style": "text", "pos": [0.15, 0.12], "part": "工件"},
                   {"at": (120, -50, 8), "text": "车刀", "style": "text", "pos": [0.2, 0.8], "part": "车刀"}])
out(n_fig3d=3)
