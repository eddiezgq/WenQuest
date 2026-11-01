"""54.5 节的三维图：机床的热变形（图 54.5.1）——(a) 外圆磨床：砂轮架里的主轴轴承、电动机发热，砂轮架向工件伸长，磨出的直径逐件变小；
(b) 车床：主轴箱升温，主轴抬高并在水平面内偏斜，车出锥度。热变形量放大画出；模型：factory/digital/models3d。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
X = M.x3d()
R = M.r3d()
A, P = C.Assembly, C.Part
red, blue, orange = "#c0504d", "#4f7fb8", "#d98c3a"
L = 167.0

g = MA.cylindrical_grinder(L=L, wheel_x=124.5, r_work=17.5)
g.add(W.sh301("op60"))
wx, wy, _ = g.anchors["wheel"]
pa = R.render_png(g, 760, 560, camera={"dir": [0.6, -1, 0.9], "fit": [[-150, -120, -260], [L + 260, 600, 260]]}, fontSize=19,
                  arrows=[{"from": (wx + 180, wy + 60, 120), "to": (wx + 180, wy - 70, 120), "color": red, "text": "砂轮架热伸长：向工件靠近", "textAt": "start", "dx": -10, "dy": -12, "anchor": "end"}],
                  labels=[{"at": (wx + 200, wy + 40, 90), "text": "热源：砂轮主轴轴承、电动机、液压油", "style": "text", "pos": [0.45, 0.94], "part": "砂轮架"},
                          {"at": (60, -15, 0), "text": "直径逐件磨小，到热平衡后稳定", "style": "text", "pos": [0.45, 0.07], "part": "SH-301"}])

lt = X.lathe_between_centers(L=L, r_work=20.15, tool_x=100.0)
q = A("车床热变形")
for p in lt.parts:
    if p.name == "主轴箱":
        q.add(P("主轴箱（升温前）", p.shape, "#d9d3c7", opacity=0.35))
        q.add(P("主轴箱（升温后，放大画）", S.rot(S.move(p.shape, dz=6), az=-1.2, about=(-150, 0, 0)), orange, opacity=0.8))
    elif p.name in ("拨盘", "前顶尖"):
        q.add(P(p.name, S.rot(S.move(p.shape, dz=6), az=-1.2, about=(-150, 0, 0)), p.color))
    elif p.name not in ("车刀", "刀架", "中滑板", "床鞍"):
        q.add(p)
pb = R.render_png(q, 760, 560, camera={"dir": [0.55, -1, 0.7]}, fontSize=19,
                  arrows=[{"from": (-250, 0, 150), "to": (-250, 0, 210), "color": red, "text": "主轴抬高", "textAt": "end"},
                          {"from": (-60, -120, 60), "to": (-60, -60, 60), "color": red, "text": "前端在水平面内偏斜", "textAt": "start", "dx": -10, "dy": 26, "anchor": "end"}],
                  labels=[{"at": (-250, -150, 0), "text": "主轴箱：轴承、齿轮、油池发热", "style": "text", "pos": [0.55, 0.06], "part": "主轴箱（升温后"}])
R.compose("fig54_5_1", [pa, pb], 2, titles=["(a) 外圆磨床：砂轮架热伸长（误差敏感方向）", "(b) 车床：主轴箱热变形，主轴抬高并偏斜（放大画出）"])
out(n_fig3d=1)
