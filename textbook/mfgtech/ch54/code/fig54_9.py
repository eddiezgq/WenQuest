"""54.9 节的三维图：外圆磨床的主动测量（在机测量、闭环控制，图 54.9.1）；误差转移——双面导向镗模，孔系的位置精度由镗模保证、
不再取决于机床主轴的精度（图 54.9.2，模型 typical.boring_jig，第 52 章用过）。模型：factory/digital/models3d。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
A, P = C.Assembly, C.Part
red, blue, green = "#c0504d", "#4f7fb8", "#5a9e6f"
L = 167.0
xg = 124.5
g = MA.cylindrical_grinder(L=L, wheel_x=xg - 40, r_work=17.5)
g.add(W.sh301("op60"))
for sgn in (1, -1):
    zt = sgn * 17.5
    g.add(P("测爪" + ("上" if sgn > 0 else "下"), S.box(xg - 2.5, xg + 2.5, -3, 3, min(zt, zt + sgn * 10), max(zt, zt + sgn * 10))
            + S.box(xg - 2.5, xg + 2.5, -70, 3, min(zt + sgn * 10, zt + sgn * 16), max(zt + sgn * 10, zt + sgn * 16)), "hardened"))
g.add(P("主动测量仪", S.box(xg - 8, xg + 8, -120, -70, -45, 45), "#3d5a80"))
pa = R.render_png(g, 900, 620, camera={"dir": [0.45, -1, 0.55], "fit": [[-60, -160, -140], [L + 120, 320, 220]]}, fontSize=19,
                  arrows=[{"from": (xg - 40, 330, 60), "to": (xg - 40, 240, 60), "color": red, "text": "数控系统按测得值控制横进给：到尺寸即停", "textAt": "start", "dx": -10, "dy": -14, "anchor": "end"}],
                  labels=[{"at": (xg, -95, 40), "text": "主动测量仪：两个测爪在线测直径", "style": "text", "pos": [0.42, 0.92], "part": "主动测量仪"},
                          {"at": (xg - 40, 200, 150), "text": "砂轮", "style": "text", "pos": [0.8, 0.1], "part": "砂轮"}])
R.save_figure("fig54_9_3", pa, 900, 620)

bj = TY.boring_jig()
R.figure3d("fig54_9_2", bj, 1300, 820, camera={"dir": [0.9, -1.2, 0.8]}, fontSize=18, explode=0.0,
           labels=[{"at": (50, -120, 60 + 56), "text": "镗套：确定镗杆的位置和方向", "style": "text", "pos": [0.32, 0.1], "part": "镗套"},
                   {"at": (50, -190, 60), "text": "镗杆与机床主轴浮动连接", "style": "text", "pos": [0.32, 0.92], "part": "镗杆"},
                   {"at": (0, 0, 120), "text": "箱体：孔系的位置由镗模保证", "style": "text", "pos": [0.72, 0.1], "part": "工件"}])
out(n_fig3d=2)
