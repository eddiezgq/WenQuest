"""54.4 节的三维图：两顶尖车削时头架、尾座、工件三部分的变形（图 54.4.1）；三种形状误差的工件（图 54.4.3，由算例 54.4.1、54.4.2 的
让刀量曲线放大生成）；三爪卡盘夹薄壁套车孔，松开后成三棱形（图 54.4.5）；生产法测刚度的台阶毛坯（图 54.4.6）。变形量放大画出。"""
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
r0 = 20.0
ghost = "#9aa3ab"


def centers_and_tool(x_tool, head_dy=0.0, tail_dy=0.0):
    q = A("两顶尖")
    lt = X.lathe_between_centers(L=L, r_work=r0, tool_x=x_tool)
    for p in lt.parts:
        if p.name == "前顶尖":
            q.add(P(p.name, S.move(p.shape, dy=head_dy), p.color))
        elif p.name == "后顶尖":
            q.add(P(p.name, S.move(p.shape, dy=tail_dy), p.color))
        elif p.name == "车刀":
            q.add(p)
    return q


# ---- 图 54.4.1：(a) 刀在头架附近：头架顶尖让开；(b) 刀在尾座附近：尾座顶尖让开；(c) 刀在中间：工件弯曲（让开量放大画出，背向力把工件推离刀具，+y）
D = 9.0
xs = [L * i / 12 for i in range(13)]
panels = []
for case, xt in (("head", 15.0), ("tail", L - 15.0), ("work", L / 2)):
    if case == "head":
        q = centers_and_tool(xt, head_dy=D)
        ys = [D * (1 - x / L) for x in xs]
    elif case == "tail":
        q = centers_and_tool(xt, tail_dy=D)
        ys = [D * x / L for x in xs]
    else:
        q = centers_and_tool(xt)
        ys = [D * math.sin(math.pi * x / L) for x in xs]
    q.add(P("原来的位置", S.cyl("x", (0, 0), r0 - 0.4, 0.5, L - 0.5), blue, opacity=0.3))
    q.add(P("工件（让开后）", X.bent_shaft(L=L, r=r0, n=13, ys=ys), "work"))
    tip = (xt, -r0 + (ys[round(xt / L * 12)] if case != "work" else D), 0)
    pp = R.render_png(q, 520, 420, camera={"dir": [0.1, -0.3, 1], "up": [0, 1, 0], "fit": [[-30, -45, -25], [L + 30, 35, 25]]}, fontSize=19,
                      arrows=[{"from": (xt, -r0 - 30, 26), "to": (xt, -r0 - 6, 26), "color": red, "text": "Fp", "textAt": "start", "dx": 8, "dy": 0}],
                      dims=[{"a": (xt, -r0, 26), "b": (xt, tip[1] if case != "work" else -r0 + D, 26), "off": (14, 0, 0), "text": "y", "color": blue}])
    panels.append(pp)
R.compose("fig54_4_1", panels, 3, titles=["(a) 刀具在头架附近：头架让开", "(b) 刀具在尾座附近：尾座让开", "(c) 刀具在中间：工件弯曲"])

# ---- 图 54.4.3：三种形状误差（让刀量曲线来自 hub/accuracy.py profile_between_centers，放大画出）
kh, kt, kk = 20000.0, 20000.0, 50000.0
Fp = Acc.kienzle_turning(0.3, 0.15)["Fp"]
cases = [("saddle", Acc.profile_between_centers(Fp, L, 40.0, kh, kt, kk), 4000.0, "(a) 工件刚、头尾架软：鞍形（放大 4000 倍）"),
         ("drum", Acc.profile_between_centers(Acc.kienzle_turning(0.5, 0.2)["Fp"], 500.0, 20.0, kh, kt, kk), 25.0, "(b) 细长轴：鼓形（放大 25 倍）"),
         ("taper", Acc.profile_between_centers(Fp, L, 40.0, kh, kh / 4, kk), 800.0, "(c) 尾座刚度只有头架的 1/4：锥形（放大 800 倍）")]
pn = []
for lab, pr, k, ttl in cases:
    LL = pr["x"][-1]
    sc = L / LL                                   # 统一画成 167 长
    rs = [r0 + k * (d - pr["dd"][0]) / 2 for d in pr["dd"]]
    q = A(lab)
    q.add(P("工件", X.profile_shaft([x * sc for x in pr["x"]], rs), "work"))
    q.add(P("理想圆柱", S.cyl("x", (0, 0), r0, -0.5, L + 0.5), ghost, opacity=0.25))
    pn.append(R.render_png(q, 520, 360, camera={"dir": [0.1, -1, 0.15], "fit": [[-5, -30, -30], [L + 5, 30, 30]]}, fontSize=19))
R.compose("fig54_4_3", pn, 3, titles=[c[3] for c in cases])

# ---- 图 54.4.5：生产法测刚度：毛坯上车出三个台阶（切深差 1 mm），一次走刀后台阶变小（放大画出）
def stepped(rs):
    pts = [(0, 0)]
    for i, rr in enumerate(rs):
        pts += [(i * 50.0, rr), ((i + 1) * 50.0, rr)]
    pts += [(150.0, 0)]
    return S.revolve(pts, "x", (0, 0))


q1 = A("台阶毛坯")
q1.add(P("台阶毛坯", stepped([20.0, 21.0, 22.0]), "work"))
q2 = A("一次走刀后")
q2.add(P("一次走刀后（台阶放大 40 倍）", stepped([18.0, 18.0 + 40 * 0.0125, 18.0 + 80 * 0.0125]), "work"))
q2.add(P("原毛坯", stepped([20.0, 21.0, 22.0]), ghost, opacity=0.25))
cam = {"dir": [0.1, -1, 0.35], "fit": [[-5, -25, -25], [155, 25, 25]]}
d1 = [{"a": (50, -23, 21), "b": (50, -23, 22), "off": (0, -12, 0), "text": "1 mm"}]
pa = R.render_png(q1, 600, 360, camera=cam, fontSize=19)
pb = R.render_png(q2, 600, 360, camera=cam, fontSize=19)
R.compose("fig54_4_6", [pa, pb], 2, titles=["(a) 车前：三个台阶，切深依次差 1 mm", "(b) 按同一刀位车一刀：台阶没有车平，剩下的台阶（放大画出）反映刚度"])

# ---- 图 54.4.6：三爪卡盘夹薄壁套车孔（变形放大 10 倍）：(a) 夹紧时外圆被夹成三棱，内孔车圆；(b) 松开后外圆弹回，内孔成三棱
Ro, Ri, Lr, a = 40.0, 32.0, 30.0, 1.5
ph = math.pi / 2                                   # 卡爪在 θ = 90°、210°、330°（machines.chuck3）
outer_c = X.section_shaft(lambda t: Ro - a * math.cos(3 * (t - ph)), L=Lr, x0=0.0)
inner_c = X.section_shaft(lambda t: Ri, L=Lr + 2, x0=-1.0)
ring_c = outer_c - inner_c
outer_r = X.section_shaft(lambda t: Ro, L=Lr, x0=0.0)
inner_r = X.section_shaft(lambda t: Ri + a * math.cos(3 * (t - ph)), L=Lr + 2, x0=-1.0)
ring_r = outer_r - inner_r
qa = MA.chuck3(D=200, grip=2 * (Ro - a), face_x=0.0)
qa.add(P("薄壁套（夹紧、车孔）", ring_c, "work"))
qb = A("松开后")
qb.add(P("薄壁套（松开后）", ring_r, "work"))
qb.add(P("理想内孔", S.tube("x", (0, 0), Ri + 0.3, Ri, -0.5, Lr + 0.5), red, opacity=0.5))
camr = {"dir": [1, -0.25, 0.2], "fit": [[0, -110, -110], [30, 110, 110]]}
pa = R.render_png(qa, 560, 520, camera=camr, fontSize=19)
pb = R.render_png(qb, 560, 520, camera={"dir": [1, -0.25, 0.2], "fit": [[0, -50, -50], [30, 50, 50]]}, fontSize=19,
                  labels=[{"at": (Lr, 0, Ri + a), "text": "卡爪处孔变大", "style": "text", "pos": [0.5, 0.06], "part": "薄壁套"}])
R.compose("fig54_4_5", [pa, pb], 2, titles=["(a) 夹紧：外圆被三个卡爪压成三棱，在这个状态下把孔车圆", "(b) 松开：外圆弹回成圆，孔变成三棱形（变形放大 10 倍）"])
out(n_fig3d=4)
