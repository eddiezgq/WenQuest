"""54.8 节的三维图：误差放大的工件形状（图 54.8.1）——锥形、鼓形、鞍形、弯曲、椭圆、三棱形，形状由 factory/digital/models3d/errors3d.py
按轮廓数据生成（误差都放大画出）；数字工厂截图包成的图（图 54.8.5、54.8.6）由 fig54_shots.py 生成。"""
import math

import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
X = M.x3d()
R = M.r3d()
A, P = C.Assembly, C.Part
L, r = 120.0, 20.0
ghost = "#4f7fb8"
shapes = [("taper", X.shape_shaft("taper", L=L, r=r, amount=5.0)), ("drum", X.shape_shaft("drum", L=L, r=r, amount=4.0)),
          ("saddle", X.shape_shaft("saddle", L=L, r=r, amount=4.0)), ("bent", S.rot(X.bent_shaft(L=L, r=r, bow=4.0), ax=90)),
          ("ellipse", X.section_shaft(X.lobed(r, 2, 2.0), L=L)), ("lobe3", X.section_shaft(X.lobed(r, 3, 1.6), L=L))]
cam_side = {"dir": [0.0, -1, 0.0], "fit": [[-5, -26, -26], [L + 5, 26, 26]]}
cam_end = {"dir": [1, -0.35, 0.3], "fit": [[0, -26, -26], [L, 26, 26]]}
panels = []
for name, shp in shapes:
    q = A(name)
    q.add(P("工件", shp, "work"))
    if name in ("ellipse", "lobe3"):
        q.add(P("理想圆", S.tube("x", (0, 0), r + 0.3, r, L, L + 0.6), ghost))
    else:                                         # 理想圆柱的上、下母线（蓝线）
        for zz in (r, -r):
            q.add(P("理想母线", S.cyl("x", (-27, zz), 0.3, -3, L + 3), ghost))
    panels.append(R.render_png(q, 480, 330, camera=cam_end if name in ("ellipse", "lobe3") else cam_side, fontSize=18))
R.compose("fig54_8_1", panels, 3, titles=["(a) 锥形", "(b) 鼓形（中间大）", "(c) 鞍形（中间小）", "(d) 弯曲（轴线弯）", "(e) 椭圆（二阶）", "(f) 三棱形（三阶）"])
out(n=len(shapes))
