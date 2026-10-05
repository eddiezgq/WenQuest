"""50.2 节的三维图：SH-301 从毛坯到成品的五个状态，每个状态里本工序加工的面着色（图 50.2.1）；工序 20 的两次安装（图 50.2.2）；
各工序的装夹（图 50.2.3）。模型：factory/digital/models3d（工件各状态由工艺规程的工序简图数据生成；卡盘、顶尖、夹具见 machines.py、jj30150.py）。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
A, P = C.Assembly, C.Part
LEN = 167.0

# ---- 图 50.2.1：五个状态（本工序加工的面着色）
states = [("blank", "(a) 工序 10 下料后：毛坯 Ø50 × 182"), ("op20", "(b) 工序 20 粗车后（调质前）"), ("op40", "(c) 工序 40 精车后（调质后）"),
          ("op50", "(d) 工序 50 铣键槽后"), ("op60", "(e) 工序 60 磨外圆后（成品）")]
pngs = []
for st, _ in states:
    q = A(st)
    q.add(W.sh301(st, highlight=st != "blank"))
    pngs.append(R.render_png(q, 700, 300, camera={"dir": [0.35, -1.2, 0.55], "fit": [[-10, -26, -26], [178, 26, 26]]}))
R.compose("fig50_2_1", pngs, 2, titles=[t for _, t in states])

# ---- 图 50.2.2：工序 20 的两次安装
def setup(n):
    q = A(f"安装{n}")
    if n == 1:
        # 毛坯左端短夹持在卡盘里（夹 20 mm），右端车端面、钻中心孔后用后顶尖顶住，粗车右段外圆
        shape = S.move(W.sh301("blank").shape, 7.0, 0, 0)     # 毛坯 x 从 −7 起，移到 0 起
        grip, D, tail = 20.0, 50.0, 182.0
        q.add(P("毛坯", shape, "work"))
    else:
        # 安装 1 车完后的状态（左段仍是 Ø50），调头：右段的 Ø31.5、Ø36.5 伸进主轴孔，卡爪夹 Ø41.5 外圆
        prof = [(-54.7, 15.75, -24.7), (-24.7, 18.25, 0.0), (0.0, 20.75, 73.6), (73.6, 25.0, 120.3)]
        shape = None
        for x0, r, x1 in prof:
            c = S.cyl("x", (0, 0), r, x0, x1)
            shape = c if shape is None else shape + c
        grip, D, tail = 20.0, 41.5, 120.3
        q.add(P("工件（安装 1 后）", shape, "work"))
    ch = MA.chuck3(D=200, grip=D, face_x=0.0)
    for p in ch.parts:
        if p.name.startswith("卡爪"):
            p.shape = p.shape & S.box(-1, grip, -300, 300, -300, 300)
        q.add(p)
    q.add(P("后顶尖", E.center(at=(tail, 0, 0), toward=-1), "hardened"))
    q.add(P("尾座套筒", S.cyl("x", (0, 0), 22, tail + 70, tail + 150), "cast"))
    q.add(P("车刀", S.box(tail - 40, tail - 28, -60, -18, -4, 4) + S.prism("xy", [(tail - 40, -18), (tail - 28, -18), (tail - 34, -9)], -4, 4), "tool"))
    return q
cam = {"dir": [0.35, -1.2, 0.5], "fit": [[-60, -110, -110], [340, 60, 110]]}
p1 = R.render_png(setup(1), 800, 460, camera=cam, fontSize=19,
                  labels=[{"at": (8, 0, 25), "text": "三爪卡盘短夹持毛坯左端", "style": "text", "pos": [0.03, 0.1], "anchor": "start"},
                          {"at": (182, 0, 0), "text": "车右端面、钻中心孔后顶住", "style": "text", "pos": [0.97, 0.1], "anchor": "end"}])
p2 = R.render_png(setup(2), 800, 460, camera=cam, fontSize=19,
                  labels=[{"at": (8, 0, 21), "text": "调头：夹已车好的 Ø41.5 外圆", "style": "text", "pos": [0.03, 0.1], "anchor": "start"},
                          {"at": (120.3, 0, 0), "text": "车左端面保证总长、钻中心孔后顶住", "style": "text", "pos": [0.97, 0.1], "anchor": "end"}])
R.compose("fig50_2_2", [p1, p2], 2, titles=["安装 1：车右端面、钻右中心孔、粗车右段外圆", "安装 2：调头，车左端面、钻左中心孔、粗车左段外圆"])

# ---- 图 50.2.3：各工序的装夹：(a) 工序 40 两顶尖 + 鸡心夹头；(b) 工序 50 键槽铣夹具；(c) 工序 60 外圆磨床两顶尖
lc = MA.lathe_centers(LEN, 0.0)
lc.add(W.sh301("op40"))
# 弯尾鸡心夹头：夹在左轴端，尾部沿轴向伸到拨盘的拨杆旁，贴住拨杆的侧面（主轴转动时拨杆推尾部带动工件）
dog = S.tube("x", (0, 0), 26, 15, 12, 26) + S.box(12, 26, 14, 58, -20, -8) + S.box(-52, 26, 48, 58, -20, -8) \
    + S.cyl("y", (19, 0), 4, 18, 32)
lc.add(P("鸡心夹头", dog, "steel_dark"))
pa = R.render_png(lc, 700, 420, camera={"dir": [0.45, 1.3, 0.5]})    # 从拨杆一侧看，看得见夹头尾部贴住拨杆
pb = R.render_png(J.assembly("op40", with_cutter=True), 700, 420, camera={"dir": M.ISO})
gr = MA.lathe_centers(LEN, 0.0)
gr.add(W.sh301("op60"))
gr.add(P("鸡心夹头", dog, "steel_dark"))
gr.add(P("砂轮（局部）", S.tube("x", (150 + 20.0, 0), 150, 50, 52, 112), "#9aa3ab"))
pc = R.render_png(gr, 700, 420, camera={"dir": [0.45, -1.3, 0.5], "fit": [[-120, -60, -160], [300, 330, 160]]})
R.compose("fig50_2_3", [pa, pb, pc], 3, titles=["(a) 工序 40 精车：两顶尖 + 鸡心夹头", "(b) 工序 50 铣键槽：键槽铣夹具 JJ-301-50", "(c) 工序 60 磨外圆：两顶尖 + 鸡心夹头，砂轮横向进给"])
out(n_fig3d=3)
