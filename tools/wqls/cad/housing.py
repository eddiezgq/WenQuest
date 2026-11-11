"""WQ-LS 机壳铸件与外观件（第 138 轮 G3），在 FreeCAD 里运行：

    WQ_VARIANT=A WQ_OUT=<目录> freecadcmd -c "exec(open('tools/wqls/cad/housing.py').read())"

铸件（HT250）按铸件做：机座、立柱、机臂、机头一体；截面渐变（放样），交接处大圆角，立柱和机头上小下大（相当于拔模）。
外观件：面板、顶盖、手轮与直驱电机、夹线器、挑线杆、针杆与压脚杆、压脚、针板与滑板、针距旋钮与倒缝扳手、操作面板、绕线器。
三个外观方案（WQ_VARIANT）：
  A 稳重：截面圆角中等，机臂顶面平直，机头圆角方正；
  B 流线：机臂顶面从立柱向机头下斜成一条弧，截面圆角大，机头前缘大圆弧；
  C 硬朗：截面以倒角为主，平面分明，机臂下沿一条棱线。
坐标与 tools/wqls/spec.py 一致：原点在针板上表面、机针中心线上；X 向右（手轮），Y 向后，Z 向上；单位 mm。
输出：<目录>/<材料>.stl（按材料分组的网格，给 Blender 渲染）和 <目录>/housing.step（铸件实体，给有限元模态）。
"""
import json
import math
import os

import FreeCAD as App
import MeshPart
import Part

V = App.Vector
VAR = os.environ.get("WQ_VARIANT", "A")
OUT = os.environ.get("WQ_OUT", "/tmp/wqls_g3")
os.makedirs(OUT, exist_ok=True)

P = dict(
    A=dict(top=(258, 258, 0), r_out=20, r_head=26, r_arch=34, r_hj=16, plan=(30, 22), edge=(10, 8, 6), chamfer=False),
    B=dict(top=(262, 242, 0), r_out=44, r_head=38, r_arch=46, r_hj=24, plan=(46, 34), edge=(14, 12, 10, 8), chamfer=False),
    C=dict(top=(258, 256, 0), r_out=14, r_head=12, r_arch=26, r_hj=10, plan=(14, 12), edge=(8, 6, 5), chamfer=True),
)[VAR]
WALL = float(os.environ.get("WQ_WALL", 5.8))
ARM_Y = (float(os.environ.get("WQ_AY0", -38.0)), float(os.environ.get("WQ_AY1", 60.0)))          # 机臂前后（G4.4：机臂补上底壁后刚度富余，回到 −38…60）
RIBS = os.environ.get("WQ_RIBS", "1") == "1"
HEADWALL = float(os.environ.get("WQ_HEADWALL", 4.5))
FRONT_COVER = os.environ.get("WQ_FRONTCOVER", "1") == "1"
FC_WIN = (-40.0, 34.0, 118.0, 236.0)       # 机头前盖板窗口 x0, x1, z0, z1（G3）
X_BRG_REAR = 380.0                         # 后轴承 6201 中心（spec.X_BRG[1]）
LIP_W_F = 14.0                             # 面板口法兰宽（端面外圆角 R14 占掉约 10 mm，法兰要宽些面板才有贴合面）
LIP_W, LIP_T, WIN_LIP_D = 8.0, 8.0, 8.0          # G4.3 面板口法兰宽、厚（沿 x），前窗口法兰宽、深（沿 y）（加宽加厚试过：频率不升反降，只是加了机头质量）
MOTOR_SEAT_X = 408.0                       # G4.3 电机座端面（后轴承座伸出立柱右壁 12 mm）
FEA_SIMPLE = os.environ.get("WQ_FEA_SIMPLE") == "1"   # 有限元模型的特征简化：不倒内圆角、根部圆角，不打小螺孔（网格划分才稳）
if FEA_SIMPLE:
    os.environ["WQ_NOHOLES"] = "1"
SPLIT = os.environ.get("WQ_SPLIT", "1") == "1"   # G4.4 机壳分上下两件（上件：机头、机臂、立柱；下件：机座），接合面 z = 0
SPLIT_PARTS = {}
DETAIL = os.environ.get("WQ_DETAIL", "0" if os.environ.get("WQ_NOEDGE") else "1") == "1"   # G4.3 铸件细节：内圆角、拔模筋、法兰、加工面
if DETAIL:
    # G4.3：窗口和前盖板都放在机头前面的平面区（外圆角 R14 以内），盖板 x −46…36、z 112…232
    # 窗口上沿到 z 234（挑线杆、摇杆在前壁附近要摆到 z 230 左右），前盖板随形包到机头顶的圆角上（z 240）
    FC_WIN = (-38.0, 28.0, 120.0, 234.0)
FC_PLATE = (FC_WIN[0] - 8, FC_WIN[1] + 8, FC_WIN[2] - 8, min(FC_WIN[3] + 8, 240.0))
X_TAKEUP = 16.0                            # 挑线杆平面（G4.1 起与针杆连杆共用曲柄销，见 tools/wqls/g4_takeup.py）
TK_SLOT = (152.0, 214.0)                   # 前盖板上挑线杆竖槽的上下端；G4.1 起按挑线机构的线眼轨迹自动定（下面 TK_JSON）
TK_POSE = [(-2.5, 20.6), (31.9, -5.9), (51.5, -17.0)]   # 外观件里的示意挑线杆（没有 G4 零件时用）：P、M、线眼，端视坐标 mm
BOSSES = os.environ.get("WQ_BOSSES", "0" if os.environ.get("WQ_NOEDGE") else "1") == "1"   # 机头内的凸台（针杆导套、前轴承座、摇杆销座）；优化试算（不倒圆）默认不带，要带就 WQ_BOSSES=1
_tkj = os.path.join(os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.path.join(os.getcwd(), "tools", "wqls", "cad"),
                    "..", "..", "..", "docs", "设计", "WQ-LS", "G4", "挑线机构.json")
TK_JSON = json.load(open(_tkj)) if os.path.exists(_tkj) else None
TK_JSON_EXISTS = TK_JSON is not None
REALMECH = os.environ.get("WQ_REALMECH", "1" if TK_JSON_EXISTS else "0") == "1"   # 有 G4 实体机构时，外观件里不再画示意的针杆、挑线杆
if TK_JSON:
    _ev = TK_JSON["result"]["E_v"]
    TK_SLOT = (round(200.0 + _ev[0] - 8), round(200.0 + _ev[1] + 8))
    try:                                                # G4.3：槽按挑线杆穿过前壁处的上下范围开（加杆宽一半和间隙 7 mm）
        import sys as _sys
        _sys.path[:0] = [os.path.join(os.path.dirname(_tkj), "..", "..", "..", "..", "tools", "wqls")]
        import g4_takeup as _T
        _m = _T.Mech2(lk=TK_JSON["lk"])
        _zs = []
        for _f in range(360):
            _p = _m.link_pose(_f, _m.LK0)
            for _u0 in (43.5, 48.0):                    # 机头前壁内面、外面（端视 u = −y）
                if (_p["P"][0] - _u0) * (_p["E"][0] - _u0) < 0:
                    _t = (_u0 - _p["P"][0]) / (_p["E"][0] - _p["P"][0])
                    _zs.append(200.0 + _p["P"][1] + _t * (_p["E"][1] - _p["P"][1]))
        if _zs:
            TK_SLOT = (math.floor(min(_zs) - 7), math.ceil(max(_zs) + 7))
    except Exception as _exc:  # noqa: BLE001
        print("slot from linkage skipped", _exc)
BEDWALL = float(os.environ.get("WQ_BEDWALL", 5.6))
ROOTWALL = float(os.environ.get("WQ_ROOTWALL", 5.8))   # G4.4：机臂根部不再加厚，与机臂同壁厚
ROOT_X = float(os.environ.get("WQ_ROOTX", 183.0))
BED_RIB_H = float(os.environ.get("WQ_BEDRIB", 0.0))       # 机座纵筋高（从机座顶面往下）
RIB_T = 7.0
RIB_X = tuple(float(v) for v in os.environ.get("WQ_RIBX", "").split(",") if v)
S_BELT_X = 352.0
ARMB = float(os.environ.get("WQ_ARMB", 120.0))                   # 机臂下沿（机臂空间高度 135；G1 的 160 在 G3 为比例改小，见细则）

ZU = 200.0
BED = dict(x0=-105.0, x1=412.0, y0=-62.0, y1=116.0, z0=-62.0)
# 立柱深 178（G4 优化定 168；G4.3 机头开面板口、加法兰和凸台后，前后摆一阶由 125 降到 122.7 Hz，立柱加深 10 回到 126 Hz）
# G4.4 分上下两件：立柱脚整个落在机座上，立柱前后与机座前后壁齐平（y −62…116，深 178，与机座同深）
PIL = dict(x0=300.0, x1=396.0, y0=float(os.environ.get("WQ_PY0", -62.0)), y1=float(os.environ.get("WQ_PY1", 116.0)))
HEAD = dict(x0=-62.0, x1=52.0, y0=float(os.environ.get("WQ_HY0", -48.0)), y1=70.0, z0=46.0)


# ---------------------------------------------------------------- 截面
def rrect_yz(x, y0, y1, z0, z1, r, chamfer=False):
    """x 平面上的圆角（或倒角）矩形线框"""
    r = min(r, (y1 - y0) / 2 - 0.1, (z1 - z0) / 2 - 0.1)
    pts = []
    corners = [(y1, z1, 1, 1), (y0, z1, -1, 1), (y0, z0, -1, -1), (y1, z0, 1, -1)]
    edges = []
    for i, (cy, cz, sy, sz) in enumerate(corners):
        a0 = [0, 90, 180, 270][i]
        c = V(x, cy - sy * r, cz - sz * r)
        p0 = c + V(0, r * math.cos(math.radians(a0)), r * math.sin(math.radians(a0)))
        pm = c + V(0, r * math.cos(math.radians(a0 + 45)), r * math.sin(math.radians(a0 + 45)))
        p1 = c + V(0, r * math.cos(math.radians(a0 + 90)), r * math.sin(math.radians(a0 + 90)))
        pts.append((p0, pm, p1))
    for i in range(4):
        p0, pm, p1 = pts[i]
        edges.append(Part.LineSegment(p0, p1).toShape() if chamfer else Part.Arc(p0, pm, p1).toShape())
        q0 = pts[(i + 1) % 4][0]
        edges.append(Part.LineSegment(p1, q0).toShape())
    return Part.Wire(Part.__sortEdges__(edges))


def rrect_xy(z, x0, x1, y0, y1, r, chamfer=False):
    w = rrect_yz(0, x0, x1, y0, y1, r, chamfer)          # 先在 YZ 画，再转到 XY
    m = App.Matrix()
    m.A11, m.A12, m.A13 = 0, 1, 0
    m.A21, m.A22, m.A23 = 0, 0, 1
    m.A31, m.A32, m.A33 = 1, 0, 0
    w = w.transformGeometry(m)
    w.translate(V(0, 0, z))
    return w


def loft(wires):
    return Part.makeLoft(wires, True, False)


def try_fillet(shape, edges, radii):
    for r in radii:
        try:
            s = shape.makeFillet(r, edges)
            if s.isValid():
                return s, r
        except Exception:  # noqa: BLE001
            pass
    return shape, 0


def seam_edges(fused, a, b, tol=0.05):
    out = []
    for e in fused.Edges:
        p = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        if a.distToShape(Part.Vertex(p))[0] < tol and b.distToShape(Part.Vertex(p))[0] < tol:
            out.append(e)
    return out


M4_TAP, M5_TAP, M6_TAP = 3.3, 4.2, 5.0          # 攻丝底孔（GB/T 20330）


def tap_holes(shape, pts, d, depth, axis):
    """在 pts（孔口中心）沿 axis（指向材料里面）钻攻丝底孔，深 depth"""
    if os.environ.get("WQ_NOHOLES") == "1":          # 有限元模型去掉小螺孔（常规的特征简化）
        return shape
    for q in pts:
        shape = shape.cut(Part.makeCylinder(d / 2, depth, V(*q) - axis * 1.0, axis))
    return shape


def section_x(shape, x):
    """shape 在平面 x 上的截面（面），用来做与机头端面同形的面板"""
    sl = shape.common(Part.makeBox(0.02, 600, 600, V(x, -300, -300)))
    fs = []
    for f in sl.Faces:
        try:
            if f.Surface.__class__.__name__ == "Plane" and abs(f.Surface.Axis.x) > 0.99 and abs(f.CenterOfMass.x - x) < 0.015:
                fs.append(f)
        except Exception:  # noqa: BLE001
            continue
    fs.sort(key=lambda f: -f.Area)
    return fs[0] if fs else None


def details(solid, hollow, info):
    """G4.3 铸件的装配和加工结构（2026-11-10 Eddie：“哪里像个铸件，机头要有前盖板，上轴哪里装电机”）：
    ① 机头左端敞开，内侧一圈 8 mm 宽的法兰（端面加工），6 个 M4 螺孔，装面板；
    ② 机头前窗口内侧一圈法兰，6 个 M4 螺孔，装前盖板；
    ③ 立柱里的后轴承座（6201，Ø32 H7）伸出立柱右壁成“电机座”：外圆 Ø52 h7 是电机止口、端面加工，4 个 M5 螺孔；
    ④ 机座顶面：针板座（沉 2.5）、滑板座（沉 1.5），针板下开口（送布牙、旋梭从这里伸上来），滑板下开口（换梭芯）；
    ⑤ 机座底边一圈向内的法兰（加工面，与油盘贴合），后面两个铰链耳；
    ⑥ 机臂顶面两个清砂工艺孔（顶盖盖住）。"""
    hw = HEADWALL
    x0 = HEAD["x0"]
    zlo, zhi = -10.0, 300.0

    def inner(k):                                       # 外形向里收 k 的实体（前视、俯视两个轮廓相交）
        f_ = Part.Face(outline(k)).extrude(V(0, 300, 0))
        f_.translate(V(0, -150, 0))
        t_ = Part.Face(plan(k)).extrude(V(0, 0, zhi - zlo))
        t_.translate(V(0, 0, zlo))
        return f_.common(t_)

    # ① 面板口：机头左端开 (壁厚 + 8) 以内的口子；法兰 = 壁厚以内、(壁厚 + 8) 以外的一圈，厚 8（沿 x）
    # inner(k) 在 x 方向也收了 k，所以要取机头里面某一截（x0 + 25）的轮廓，再沿 x 拉伸到端头
    xs_ = x0 + 25
    pw, pf = section_x(inner(hw), xs_), section_x(inner(hw + LIP_W_F), xs_)
    if pw is not None and pf is not None:
        ring_f = pw.cut(pf)
        ring_f.translate(V(x0 + hw - 0.2 - xs_, 0, 0))
        hollow = fuse_fillet(hollow, ring_f.extrude(V(LIP_T - hw + 0.2, 0, 0)).common(solid))   # 只留在外形里面（机头下部“鼻子”处不伸出去）
        if os.environ.get("WQ_NOFACEOPEN") != "1":
            op_ = pf.copy()
            op_.translate(V(x0 - 1 - xs_, 0, 0))
            hollow = hollow.cut(op_.extrude(V(LIP_T + 1.5, 0, 0)))
    # （试过在面板口里加一圈隔框：一阶反而降——这一阶是机臂连机头在立柱上前后摆，机头上加质量就降，不是截面走形）
    ring_pts = []                                       # 6 × M4：在法兰中线上（离机头内壁 LIP_W / 2）
    if pw is not None:
        bb = pw.BoundBox
        m_ = LIP_W_F - 4                                # 端面外圆角 R14 吃掉约 10 mm，螺孔放在离外形约 14.5 mm 处（端面平面区里）
        yc, zc = (bb.YMin + bb.YMax) / 2, (bb.ZMin + bb.ZMax) / 2
        cand = [(bb.YMin + m_, zc - 30), (bb.YMin + m_, zc + 30), (bb.YMax - m_, zc - 30), (bb.YMax - m_, zc + 30),
                (yc, bb.ZMax - m_), (yc, bb.ZMin + m_)]
        for y_, z_ in cand:
            if hollow.isInside(V(x0 + LIP_T - 1, y_, z_), 0.01, True) and hollow.isInside(V(x0 + 1, y_, z_), 0.01, True):
                ring_pts.append((x0, y_, z_))
        hollow = tap_holes(hollow, ring_pts, M4_TAP, 10, V(1, 0, 0))
    info["faceplate_holes"] = ring_pts
    # ② 前窗口：内侧法兰（窗口外扩 8，y 从内壁到 y0 + 8），窗口四角 R10；6 个 M4 螺孔沿 +y 打进法兰
    fx0, fx1, fz0, fz1 = FC_WIN
    y0 = HEAD["y0"]
    fr = Part.makeBox(fx1 - fx0 + 2 * LIP_W, WIN_LIP_D - hw + 0.2, fz1 - fz0 + 2 * LIP_W, V(fx0 - LIP_W, y0 + hw - 0.2, fz0 - LIP_W))
    win = Part.makeBox(fx1 - fx0, 20, fz1 - fz0, V(fx0, y0 - 10, fz0))
    win = win.makeFillet(10, [e for e in win.Edges if abs(e.BoundBox.YLength - 20) < 1e-6])
    fr = fr.cut(Part.makeBox(fx1 - fx0 + 20, 20, 30, V(fx0 - 10, y0, fz1 - 2)))   # 上边不要法兰：挑线杆、摇杆从这里摆过，上边又在顶圆角里
    hollow = fuse_fillet(hollow, fr.cut(win).common(solid))
    hollow = hollow.cut(win)
    zm = (fz0 + fz1) / 2 - 8
    wpts = [(fx0 - 4, y0, fz0 + 12), (fx0 - 4, y0, zm), (fx0 - 4, y0, 220.0),
            (fx1 + 4, y0, fz0 + 12), (fx1 + 4, y0, zm), (fx1 + 4, y0, 220.0)]       # 左右两边各 3 个（上边是圆角，不打孔）
    hollow = tap_holes(hollow, wpts, M4_TAP, 10, V(0, 1, 0))
    info["front_window"] = FC_WIN
    info["window_holes"] = wpts
    # ③ 后轴承座与电机座：Ø52 的筒从立柱里 x 372 伸到立柱外 x 408；里面四条筋接立柱四壁
    xr0, xr1 = 372.0, MOTOR_SEAT_X
    tube = Part.makeCylinder(26, xr1 - xr0, V(xr0, 0, ZU), V(1, 0, 0))
    # 只在立柱右壁里面加 4 块短三角筋托住轴承座（原来 4 条通到立柱四壁的长筋约 0.7 kg 在立柱顶上，前后摆一阶降了 5 Hz）
    ribs = []
    for a in (45, 135, 225, 315):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        tri = Part.makePolygon([V(PIL["x1"] - 1, 25 * ca, ZU + 25 * sa), V(PIL["x1"] - 1, 52 * ca, ZU + 52 * sa),
                                V(xr0 + 2, 25 * ca, ZU + 25 * sa), V(PIL["x1"] - 1, 25 * ca, ZU + 25 * sa)])
        nrm = V(0, -sa, ca)
        f_ = Part.Face(tri)
        f_.translate(nrm * -3)
        ribs.append(f_.extrude(nrm * 6))
    inner_ribs = None
    for r_ in ribs:
        inner_ribs = r_ if inner_ribs is None else inner_ribs.fuse(r_)
    hollow = fuse_fillet(hollow, inner_ribs.common(solid).cut(Part.makeCylinder(25, 40, V(xr0 - 1, 0, ZU), V(1, 0, 0))))
    hollow = fuse_fillet(hollow, tube)
    hollow = hollow.cut(Part.makeCylinder(16, 10, V(X_BRG_REAR - 5, 0, ZU), V(1, 0, 0)))                     # 6201 外圈 Ø32 H7
    hollow = hollow.cut(Part.makeCylinder(10, xr1 - xr0 + 4, V(xr0 - 2, 0, ZU), V(1, 0, 0)))                 # 轴、油封过孔 Ø20
    mpts = [(xr1, 20 * math.cos(a), ZU + 20 * math.sin(a)) for a in (math.radians(45 + 90 * i) for i in range(4))]
    hollow = tap_holes(hollow, mpts, M5_TAP, 12, V(-1, 0, 0))
    info["motor_seat"] = dict(x=xr1, spigot_d=52, holes=mpts)
    # ④ 机座顶面：针板座、滑板座（沉孔），针板下、滑板下开口
    hollow = hollow.cut(Part.makeBox(64, 44, 2.5, V(-32, -22, -2.5)))
    hollow = hollow.cut(Part.makeBox(46, 36, 1.5, V(-23, -58, -1.5)))
    op = Part.makeBox(50, 36, 20, V(-22, -18, -15)).fuse(Part.makeBox(40, 34, 20, V(-20, -52, -15)))
    op = op.removeSplitter()
    op, _ = try_fillet(op, [e for e in op.Edges if e.BoundBox.ZLength > 19], (4.0, 3.0, 2.0))
    hollow = hollow.cut(op)
    npts = [(-27, -17, -2.5), (27, -17, -2.5), (-27, 17, -2.5), (27, 17, -2.5)]
    hollow = tap_holes(hollow, npts, 2.5, 8, V(0, 0, -1))                                    # 针板螺钉 M3
    # ⑤ 机座底边法兰（内侧一圈，宽 10、厚 6，底面加工）和后面两个铰链耳
    bw = BEDWALL
    outer = Part.makeBox(BED["x1"] - BED["x0"] - 2 * bw + 0.4, BED["y1"] - BED["y0"] - 2 * bw + 0.4, 6, V(BED["x0"] + bw - 0.2, BED["y0"] + bw - 0.2, BED["z0"]))
    inn = Part.makeBox(BED["x1"] - BED["x0"] - 2 * bw - 20, BED["y1"] - BED["y0"] - 2 * bw - 20, 8, V(BED["x0"] + bw + 10, BED["y0"] + bw + 10, BED["z0"] - 1))
    inn = inn.makeFillet(6, [e for e in inn.Edges if e.BoundBox.ZLength > 7])
    hollow = fuse_fillet(hollow, outer.cut(inn).common(solid))
    for xh in (20.0, 300.0):
        lug = Part.makeBox(26, 14, 22, V(xh - 13, BED["y1"], -44))
        lug = lug.makeFillet(5, [e for e in lug.Edges if e.BoundBox.ZLength > 21 and e.BoundBox.YMin > BED["y1"] + 1])
        lug = lug.cut(Part.makeCylinder(4.1, 30, V(xh - 15, BED["y1"] + 7, -33), V(1, 0, 0)))             # 铰链销孔 Ø8.2
        hollow = fuse_fillet(hollow, lug)
    # ⑥ 机臂顶面清砂工艺孔 2 × Ø36（顶盖 x 110…260 盖住）
    for xs in (() if os.environ.get("WQ_NOSAND") == "1" else (150.0, 225.0)):
        hollow = hollow.cut(Part.makeCylinder(18, 40, V(xs, 12, 220), V(0, 0, 1)))
    tpts = []                                           # 顶盖螺孔 4 × M4（盲孔深 5，壁厚 5.8）
    for xs_ in (118.0, 252.0):
        for ys_ in (-6.0, 30.0):
            ln = Part.LineSegment(V(xs_, ys_, 300), V(xs_, ys_, 180)).toShape().common(hollow)
            if ln.Vertexes:
                tpts.append((xs_, ys_, max(v.Point.z for v in ln.Vertexes)))
    hollow = tap_holes(hollow, tpts, M4_TAP, 5, V(0, 0, -1))
    if SPLIT and os.environ.get("WQ_NOJOINT") != "1" and not FEA_SIMPLE:   # 有限元模型：接合面按刚性连接，凸台、螺孔、销孔不进网格
        hollow = joint(hollow, solid, info)
    return hollow.removeSplitter()


M10_TAP = 8.5


def joint(hollow, solid, info):
    """G4.4 上下件接合：立柱脚四角 4 个凸台（Ø28，高 32）攻 M10 深 22；机座顶板下对应 4 个凸台（Ø28，z −24…0），
    Ø11 通孔、底下锪平，M10 × 45 内六角螺钉从机座里往上拧；2 个 Ø10 圆柱销（立柱左右壁上的凸台、机座顶板下的凸台）；
    机座顶板在立柱里面开同步带和电线过孔。接合面两面精铣。"""
    w = ROOTWALL
    ix0, ix1, iy0, iy1 = PIL["x0"] + w, PIL["x1"] - w, PIL["y0"] + w, PIL["y1"] - w
    r = 14.0
    bolts = [(ix0 + r, iy0 + r), (ix1 - r, iy0 + r), (ix0 + r, iy1 - r), (ix1 - r, iy1 - r)]
    pins = [(ix0 + 10, (iy0 + iy1) / 2 - 20), (ix1 - 10, (iy0 + iy1) / 2 + 20)]
    feats_u, feats_l = None, None
    for x_, y_ in bolts:
        u = Part.makeCylinder(r, 32, V(x_, y_, 0), V(0, 0, 1))
        l_ = Part.makeCylinder(r, 24, V(x_, y_, -24), V(0, 0, 1))
        feats_u = u if feats_u is None else feats_u.fuse(u)
        feats_l = l_ if feats_l is None else feats_l.fuse(l_)
    for x_, y_ in pins:
        u = Part.makeCylinder(10, 26, V(x_, y_, 0), V(0, 0, 1))
        l_ = Part.makeCylinder(10, 16, V(x_, y_, -16), V(0, 0, 1))
        feats_u, feats_l = feats_u.fuse(u), feats_l.fuse(l_)
    hollow = fuse_fillet(hollow, feats_u.common(solid))
    hollow = fuse_fillet(hollow, feats_l.common(Part.makeBox(600, 400, 30, V(-200, -200, -30))))
    for x_, y_ in ([] if FEA_SIMPLE else bolts):        # 有限元模型不打这些孔（网格划分在接合面的孔口处失败）
        hollow = hollow.cut(Part.makeCylinder(M10_TAP / 2, 22, V(x_, y_, 0), V(0, 0, 1)))                # 上件 M10 螺孔
        hollow = hollow.cut(Part.makeCylinder(5.5, 26, V(x_, y_, -25), V(0, 0, 1)))                       # 下件 Ø11 通孔
        hollow = hollow.cut(Part.makeCylinder(9, 1.5, V(x_, y_, -25), V(0, 0, 1)))                         # 锪平 Ø18
    for x_, y_ in ([] if FEA_SIMPLE else pins):
        hollow = hollow.cut(Part.makeCylinder(5, 24, V(x_, y_, -12), V(0, 0, 1)))                          # Ø10 H7 销孔（两件同钻铰）
    belt = Part.makeBox(44, 60, 20, V(S_BELT_X - 22, -25, -15))
    belt = belt.makeFillet(6, [e for e in belt.Edges if e.BoundBox.ZLength > 19])
    hollow = hollow.cut(belt)                                                                                  # 同步带、电线过孔
    info["joint"] = dict(bolts=bolts, pins=pins, plane_z=0.0)
    return hollow


def split(hollow):
    """在接合面 z = 0 把铸件分成上件、下件"""
    def cut_at(h):
        up = h.common(Part.makeBox(1000, 600, 600, V(-300, -300, 0)))
        lo = h.common(Part.makeBox(1000, 600, 300, V(-300, -300, -300)))
        return up.removeSplitter(), lo.removeSplitter()
    try:
        return cut_at(hollow)
    except Exception as e:                       # 倒圆后个别面朝向不一致（OCC 报 Unorientable）：修复后再分
        print("split: 修复后重试", e)
        h = hollow.copy()
        h.fix(1e-4, 1e-5, 1e-3)
        try:
            return cut_at(h)
        except Exception:
            sh = Part.Shell(h.Faces)
            sh.sewShape()
            h = Part.Solid(sh)
            h.fix(1e-4, 1e-5, 1e-3)
            return cut_at(h)


def machined_faces(shape):
    """加工面：面板、前盖板法兰面，电机座端面和止口，轴承孔、针杆孔、销孔、螺孔，针板座、滑板座，机座底面。用来单独上色（亮金属）"""
    out = []
    x0, y0 = HEAD["x0"], HEAD["y0"]
    for f in shape.Faces:
        s = f.Surface
        c = f.CenterOfMass
        try:
            n = f.normalAt(*f.Surface.parameter(c)) if hasattr(f.Surface, "parameter") else f.normalAt(0, 0)
        except Exception:  # noqa: BLE001
            n = f.normalAt(0, 0)
        name = type(s).__name__
        if name == "Plane":
            if abs(c.x - x0) < 0.05 and abs(n.x) > 0.99:
                out.append(f)
            elif abs(c.y - y0) < 0.05 and abs(n.y) > 0.99 and FC_PLATE[0] - 1 < c.x < FC_PLATE[1] + 1:
                out.append(f)
            elif abs(c.x - MOTOR_SEAT_X) < 0.05 and abs(n.x) > 0.99:
                out.append(f)
            elif abs(c.z - BED["z0"]) < 0.05 and abs(n.z) > 0.99:
                out.append(f)
            elif SPLIT and abs(c.z) < 0.05 and abs(n.z) > 0.99 and PIL["x0"] - 30 < c.x < PIL["x1"] + 30 and n.z < 0:
                out.append(f)                                                      # 上件立柱脚接合面
            elif SPLIT and abs(c.z + 25) < 0.05 and abs(n.z) > 0.99:
                out.append(f)                                                      # 下件螺钉锪平面
            elif abs(n.z) > 0.99 and (abs(c.z + 2.5) < 0.05 or abs(c.z + 1.5) < 0.05) and -33 < c.x < 33 and -59 < c.y < 23:
                out.append(f)
        elif name == "Cylinder":
            r = s.Radius
            if any(abs(r - v) < 0.02 for v in (1.65, 2.1, 1.25, 16.0, 17.5, 6.0, 3.0, 4.1, 4.25, 5.5, 5.0, 9.0)):
                out.append(f)
            elif abs(r - 26.0) < 0.02 and c.x > PIL["x1"] - 0.5:                 # 电机止口 Ø52
                out.append(f)
    return out


def sharp_edges(shape, min_deg=10.0):
    """真正有棱角的棱（两侧面法向夹角 > min_deg）。圆角轮廓生出的相切棱不算（对它们倒圆一定失败）"""
    out = []
    for e in shape.Edges:
        try:
            fs = shape.ancestorsOfType(e, Part.Face)
            if len(fs) != 2:
                continue
            p_ = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
            n = []
            for f in fs:
                u, v = f.Surface.parameter(p_)
                n.append(f.normalAt(u, v))
            if math.degrees(n[0].getAngle(n[1])) > min_deg:
                out.append(e)
        except Exception:  # noqa: BLE001
            continue
    return out


def fillet_what_you_can(shape, radius):
    """内腔倒圆：逐条试，能倒的一起倒。两个轮廓相交生出的 B 样条棱 OCC 倒不了，留着（图纸“未注铸造圆角 R3–R5”覆盖）"""
    ok = []
    for e in sharp_edges(shape):
        try:
            if shape.makeFillet(radius, [e]).isValid():
                ok.append(e)
        except Exception:  # noqa: BLE001
            pass
    if not ok:
        return shape, 0, 0
    s, r = try_fillet(shape, ok, (radius, radius - 1, radius - 2))
    return s, r, len(ok)


def fuse_fillet(base, feat, radii=(3.0, 2.0)):
    """把凸台、筋并到铸件上，并在相接处倒根部圆角（铸件不能有尖内角）。只在 feat 附近找新生成的相接棱，失败就不倒"""
    new = base.fuse(feat)
    if not DETAIL or FEA_SIMPLE or feat.isNull() or feat.Volume < 1:
        return new
    bb = App.BoundBox(feat.BoundBox)
    bb.enlarge(0.5)
    es = []
    for e in new.Edges:
        try:
            if not bb.isInside(e.BoundBox.Center):
                continue
        except Exception:  # noqa: BLE001
            continue
        p_ = Part.Vertex(e.valueAt((e.FirstParameter + e.LastParameter) / 2))
        if feat.isInside(p_.Point, 0.05, True) and base.isInside(p_.Point, 0.05, True):
            es.append(e)
    if not es:
        return new
    s2, r_ = try_fillet(new, es, radii)
    return s2 if r_ else new


# ---------------------------------------------------------------- 铸件
def rounded_polygon_xz(pts, radii, chamfer=False):
    """XZ 平面（y = 0）上的多边形，每个顶点给一个圆角半径（0 = 尖角）；chamfer 时圆角改为等长倒角"""
    keep = []                                            # 去掉重合点和共线点（它们会生出零长边）
    for i in range(len(pts)):
        a_, b_, c_ = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
        cr = (b_[0] - a_[0]) * (c_[1] - b_[1]) - (b_[1] - a_[1]) * (c_[0] - b_[0])
        if abs(cr) > 1e-6 and math.dist(a_, b_) > 1e-6:
            keep.append(i)
    pts, radii = [pts[i] for i in keep], [radii[i] for i in keep]
    n = len(pts)
    P2 = [App.Vector(x, 0, z) for x, z in pts]
    segs = []
    tangent = []
    for i in range(n):
        a, b, c = P2[i - 1], P2[i], P2[(i + 1) % n]
        r = radii[i]
        if r <= 0:
            tangent.append((b, b, None))
            continue
        u, w = (a - b), (c - b)
        u.normalize()
        w.normalize()
        ang = math.acos(max(-1, min(1, u.dot(w))))
        d = r / math.tan(ang / 2)
        p1, p2 = b + u * d, b + w * d
        bis = u + w
        bis.normalize()
        mid = b + bis * (r / math.sin(ang / 2) - r)
        tangent.append((p1, p2, mid))
    edges = []
    for i in range(n):
        p1, p2, mid = tangent[i]
        if mid is not None:
            edges.append(Part.LineSegment(p1, p2).toShape() if chamfer else Part.Arc(p1, mid, p2).toShape())
        q1 = tangent[(i + 1) % n][0]
        if (q1 - p2).Length > 1e-6:
            edges.append(Part.LineSegment(p2, q1).toShape())
    return Part.Wire(edges)


def outline(inset=0.0):
    """前视轮廓（XZ）：机头—机臂—立柱。inset > 0 时为内腔"""
    t0, t1, crown = P["top"]
    k = inset
    nl, nr, nz = HEAD["x0"] + 22, HEAD["x1"] - 16, 96.0       # 机头下部收窄（针杆、压脚杆所在的“鼻子”）
    pts = [(nr - k, HEAD["z0"] + k), (nl + k, HEAD["z0"] + k), (nl + k, nz - k), (HEAD["x0"] + k, nz + 34 - k),
           (HEAD["x0"] + k, t1 - k), (140, (t0 + t1) / 2 + crown - k), (PIL["x1"] - k, t0 - k),
           (PIL["x1"] - k, (0.0 if SPLIT else -10.0) if k else 0.0), (PIL["x0"] + k, (0.0 if SPLIT else -10.0) if k else 0.0), (PIL["x0"] + k, ARMB + k),
           (HEAD["x1"] - k, ARMB + k), (HEAD["x1"] - k, ARMB - P["r_hj"] - 18 - k), (nr - k, max(ARMB - P["r_hj"] - 38, HEAD["z0"] + 26) - k)]
    # ↑ 机臂下沿是内腔往“上”收（ARMB + k）。G3–G4.3 这里误写成 ARMB − k，机臂底面一直没有壁（2026-11-11 Eddie 看剖视图发现）
    rr = [8, 8, 24, 24, P["r_head"], 1200 if crown else 0, P["r_out"], 0, 0, P["r_arch"], P["r_hj"], 10, 10]
    if k:
        rr = [max(r - k, 0) if 0 < r < 900 else r for r in rr]
        rr[0] = rr[1] = 0
        rr[-4], rr[-3] = P["r_arch"] + k, P["r_hj"] + k    # 机臂与立柱、机头相接的两个内凹角：内腔圆角 = 外圆角 + 壁厚（壁厚均匀）
    if not crown:                                       # 机臂顶面平直时去掉中间那个共线点（否则生出碎边）
        del pts[5], rr[5]
    return rounded_polygon_xz(pts, rr, P["chamfer"])


def plan(inset=0.0):
    """俯视轮廓（XY）：机头深 114；机臂中段深 98；靠立柱的一段（肩）加深到与立柱同深 128。
    前视、俯视两个轮廓的过渡段错开，避免两组圆角挤在一起（会生出碎边，倒不了圆角）。"""
    k = inset
    ra, rb = 0, 0                                         # 俯视的四个外角不倒：由整体倒圆处理（两个视向都倒会生碎边或退化）
    hx = 100 + (P["r_hj"] - 16)                         # 机头→机臂的收窄从这里开始（离开前视的过渡圆弧）
    sx = PIL["x0"] - P["r_arch"] - 76                     # 机臂→肩的加宽
    ay0, ay1 = ARM_Y
    pts = [(HEAD["x0"] + k, HEAD["y0"] + k), (hx, HEAD["y0"] + k), (hx + 40, ay0 + k), (sx, ay0 + k), (sx + 50, PIL["y0"] + k),
           (PIL["x1"] - k, PIL["y0"] + k), (PIL["x1"] - k, PIL["y1"] - k), (sx + 50, PIL["y1"] - k), (sx, ay1 - k),
           (hx + 40, ay1 - k), (hx, HEAD["y1"] - k), (HEAD["x0"] + k, HEAD["y1"] - k)]
    rr = [ra, 40, 40, 50, 50, rb, rb, 50, 50, 40, 40, ra]
    if k:
        rr = [max(r - k, 1) for r in rr]
    w = rounded_polygon_xz([(x, y) for x, y in pts], rr, P["chamfer"])
    m = App.Matrix()                                     # XZ 平面 → XY 平面（z → y）
    m.A22, m.A23, m.A32, m.A33 = 0, 1, -1, 0
    return w.transformGeometry(m)


def casting():
    ch = P["chamfer"]
    zlo, zhi = -10.0, 300.0
    front = Part.Face(outline()).extrude(V(0, 300, 0))
    front.translate(V(0, -150, 0))
    top = Part.Face(plan()).extrude(V(0, 0, zhi - zlo))
    top.translate(V(0, 0, zlo))
    body = front.common(top).removeSplitter()
    info = {"body_valid": body.isValid()}
    # 除了坐在机座上的底边，全部倒圆（或倒角），从大到小试
    es = [e for e in body.Edges if not (abs(e.BoundBox.ZMax) < 1e-6)]
    radii = () if os.environ.get("WQ_NOEDGE") else (*P["edge"], 5, 4, 3)   # 有限元用的简化模型不倒外圆角（常规做法，对刚度影响很小）
    for r in radii:
        try:
            b2 = body.makeChamfer(r, es) if ch else body.makeFillet(r, es)
            if b2.isValid():
                body = b2
                info["edge"] = r
                break
        except Exception:  # noqa: BLE001
            continue
    else:
        info["edge"] = 0
    # 机座
    bed = Part.makeBox(BED["x1"] - BED["x0"], BED["y1"] - BED["y0"], -BED["z0"], V(BED["x0"], BED["y0"], BED["z0"]))
    vert = [e for e in bed.Edges if abs(e.BoundBox.ZLength - (-BED["z0"])) < 1e-6]
    bed = bed.makeChamfer(10, vert) if ch else bed.makeFillet(16, vert)
    tope = [e for e in bed.Edges if abs(e.BoundBox.ZMin) < 1e-6 and abs(e.BoundBox.ZMax) < 1e-6]
    bed = bed.makeChamfer(3, tope) if ch else bed.makeFillet(4, tope)
    # 立柱根部喇叭口
    y0, y1 = PIL["y0"], PIL["y1"]
    ped = loft([rrect_xy(0.0, PIL["x0"] - 16, PIL["x1"] + 12, y0 - 16, y1 + 12, 26, ch),
                rrect_xy(12.0, PIL["x0"] - 5, PIL["x1"] + 3, y0 - 5, y1 + 3, 18, ch),
                rrect_xy(30.0, PIL["x0"] + 1.5, PIL["x1"] - 1.5, y0 + 1.5, y1 - 1.5, 13, ch)])
    boss = Part.makeCylinder(9, 8, V(-16, 6, HEAD["z0"] - 8), V(0, 0, 1))      # 压脚杆导套座（针杆导套座 G4.1 移进机头里，见 BOSSES）
    if not BOSSES:
        boss = boss.fuse(Part.makeCylinder(9, 8, V(0, 0, HEAD["z0"] - 8), V(0, 0, 1)))
    solid = body.fuse(bed).fuse(ped).fuse(boss).removeSplitter()
    # 空心：内腔 = 两个内轮廓相交；机座底面敞开
    cf = Part.Face(outline(WALL)).extrude(V(0, 300, 0))
    cf.translate(V(0, -150, 0))
    ct = Part.Face(plan(WALL)).extrude(V(0, 0, zhi - zlo))
    ct.translate(V(0, 0, zlo))
    cav = cf.common(ct)
    # 根部加厚：立柱和机臂靠立柱一段（x ≥ ROOT_X）弯矩最大，壁厚 ROOTWALL；其余 WALL。内腔在 ROOT_X 处分两段，一次挖出
    if ROOTWALL > WALL:
        rf = Part.Face(outline(ROOTWALL)).extrude(V(0, 300, 0))
        rf.translate(V(0, -150, 0))
        rt = Part.Face(plan(ROOTWALL)).extrude(V(0, 0, zhi - zlo))
        rt.translate(V(0, 0, zlo))
        left = Part.makeBox(600, 400, 400, V(ROOT_X - 600, -200, -50))
        right = Part.makeBox(600, 400, 400, V(ROOT_X, -200, -50))
        cav = cav.common(left).fuse(rf.common(rt).common(right)).removeSplitter()
        info["rootwall"] = ROOTWALL
    if DETAIL and not FEA_SIMPLE:                       # G4.3 内圆角：内腔的棱倒圆 = 铸件内角 R5（铸造内角不能是尖角）
        cav, r_, n_ = fillet_what_you_can(cav, 5.0)
        info["inner_fillet"] = dict(r=r_, edges=n_)
    bw = BEDWALL
    bcav = Part.makeBox(BED["x1"] - BED["x0"] - 2 * bw, BED["y1"] - BED["y0"] - 2 * bw, -BED["z0"] - bw + 1,
                        V(BED["x0"] + bw, BED["y0"] + bw, BED["z0"] - 1))
    if DETAIL and not FEA_SIMPLE:
        bcav, info["bed_inner_fillet"] = try_fillet(bcav, [e for e in bcav.Edges if e.BoundBox.ZMin > BED["z0"] + 0.5], (5.0, 4.0))
    hollow = solid.cut(cav).cut(bcav)
    # 机头壁薄一些（机头在悬臂端，越轻固有频率越高）：机头区域按 HEADWALL 再挖一次
    if HEADWALL < WALL:
        hf = Part.Face(outline(HEADWALL)).extrude(V(0, 300, 0))
        hf.translate(V(0, -150, 0))
        ht = Part.Face(plan(HEADWALL)).extrude(V(0, 0, zhi - zlo))
        ht.translate(V(0, 0, zlo))
        hbox = Part.makeBox(HEAD["x1"] - HEAD["x0"] - 2 * HEADWALL, 400, 400, V(HEAD["x0"] + HEADWALL, -200, HEAD["z0"] + HEADWALL))
        try:
            hc = hf.common(ht).common(hbox)
            if DETAIL and not FEA_SIMPLE:
                hc, r_, n_ = fillet_what_you_can(hc, 4.0)
                info["head_inner_fillet"] = dict(r=r_, edges=n_)
            hollow = hollow.cut(hc)
            info["headwall"] = HEADWALL
        except Exception as exc:  # noqa: BLE001
            info["headwall"] = f"skipped: {str(exc)[:60]}"
    # 筋（G3 模态迭代加的）：机臂横隔板、立柱横隔板、机座纵筋和立柱下的横筋。隔板上开孔：上轴、油管和线、同步带
    if RIBS:
        rb = []
        for x in RIB_X:
            sl = Part.makeBox(RIB_T, 400, 400, V(x - RIB_T / 2, -200, ARMB - 20))
            if DETAIL:                                  # 拔模 1°：分型面 y = 0，筋在分型面处最厚（7），往前后两壁逐渐变薄（到壁约 4.6）
                h0, d_ = RIB_T / 2, 150 * math.tan(math.radians(1.0))
                pts = [(x - h0, 0), (x - h0 + d_, 150), (x + h0 - d_, 150), (x + h0, 0), (x + h0 - d_, -150), (x - h0 + d_, -150)]
                w_ = Part.makePolygon([V(a_, b_, ARMB - 20) for a_, b_ in pts] + [V(pts[0][0], pts[0][1], ARMB - 20)])
                sl = Part.Face(w_).extrude(V(0, 0, 400))
            hole = Part.makeCylinder(20, RIB_T + 2, V(x - RIB_T / 2 - 1, 0, ZU), V(1, 0, 0))
            hole = hole.fuse(Part.makeCylinder(12, RIB_T + 2, V(x - RIB_T / 2 - 1, 30, ARMB + 22), V(1, 0, 0)))
            rb.append(sl.common(cav).cut(hole))
        for z in (55.0, 115.0):
            sl = Part.makeBox(PIL["x1"] - PIL["x0"] + 20, 300, RIB_T, V(PIL["x0"] - 10, -150, z))
            slot = Part.makeBox(34, 60, RIB_T + 2, V(S_BELT_X - 17, -30, z - 1)).fuse(Part.makeCylinder(10, RIB_T + 2, V(330, 45, z - 1), V(0, 0, 1)))
            rb.append(sl.common(cav).cut(slot))
        for y in ((-20.0, 50.0) if BED_RIB_H > 1 else ()):
            sl = Part.makeBox(BED["x1"] - 80, RIB_T, BED_RIB_H, V(80, y - RIB_T / 2, -BED_RIB_H))
            rb.append(sl.common(bcav))
        for x in (PIL["x0"], PIL["x1"] - RIB_T):
            sl = Part.makeBox(RIB_T, BED["y1"] - BED["y0"], -BED["z0"], V(x, BED["y0"], BED["z0"]))
            rb.append(sl.common(bcav))
        for r_ in rb:
            hollow = fuse_fillet(hollow, r_)
        hollow = hollow.removeSplitter()
    # 机头内的凸台（G4.1）：针杆上、下导套座，前轴承座（整块隔板），挑线摇杆销座。与刺布、挑线零件的间隙在 G4.1 的干涉检查里核对
    if BOSSES:
        hw = HEADWALL
        y_back = HEAD["y1"] - hw
        bs = []
        # 针杆下导套座：机头底板上 Ø22 × 28 的凸台，孔 Ø12（含油轴套 Ø8 × Ø12 × 20）
        bs.append(Part.makeCylinder(11, 28, V(0, 0, HEAD["z0"]), V(0, 0, 1)).cut(Part.makeCylinder(6, 40, V(0, 0, HEAD["z0"] - 5), V(0, 0, 1))))
        # 针杆上导套座：x −16…3（不越过连杆平面 x 5），z 170…194，一条筋接到机头后壁；孔 Ø12
        if DETAIL:                                      # G4.3：圆凸台（被 x = 3 平面切成 D 形，让开连杆），一条筋接到后壁
            ub = Part.makeCylinder(11, 24, V(0, 0, 170), V(0, 0, 1)).common(Part.makeBox(40, 40, 40, V(-37, -20, 160)))
            ub = ub.fuse(Part.makeBox(8, y_back + 1, 18, V(-12, 0, 172)))
        else:
            ub = Part.makeBox(19, 20, 24, V(-16, -10, 170)).fuse(Part.makeBox(10, y_back - 8 + 1, 14, V(-14, 8, 175)))
        bs.append(ub.cut(Part.makeCylinder(6, 40, V(0, 0, 160), V(0, 0, 1))))
        # 前轴承座：x 31…44，轴承座圈加四条筋（G4.2 由整块隔板改，见下），中间 Ø35 轴承孔（6202）
        # 原来是一整块隔板：机头上多了约 1.7 kg，机壳一阶从 129 Hz 掉到 93 Hz（靠近 5000 r/min 的 83 Hz），
        # 改成轴承座圈（Ø50 × 13）加四条筋（上、后、前、下，厚 8），接到机头四壁
        ring = Part.makeCylinder(25, 13, V(31, 0, ZU), V(1, 0, 0))
        rbs = [Part.makeBox(13, 8, 60, V(31, -4, ZU)), Part.makeBox(13, 80, 8, V(31, 0, ZU - 4)),
               Part.makeBox(10, 80, 8, V(34, -80, ZU - 4)), Part.makeBox(13, 8, 200, V(31, -4, ZU - 200))]
        wall = ring
        for rb_ in rbs:
            wall = wall.fuse(rb_)
        # 不与内腔 cav 求交：cav 是按机臂壁厚 5.8 挖的，机头壁只有 4.5，求交后筋离机头内壁差 1.3 mm、是悬空的
        # （第一次模态 93 Hz 就是这块悬空的板在晃）。直接与外形 solid 求交，筋伸进壁里和壁连成一体
        wall = wall.cut(Part.makeCylinder(17.5, 15, V(30, 0, ZU), V(1, 0, 0)))   # 6202 外圈 Ø35
        bs.append(wall.removeSplitter())
        if TK_JSON:                                     # 摇杆销座：从轴承隔板伸出的凸台，销 Ø6
            qu, qv = TK_JSON["lk"]["Qz"], TK_JSON["lk"]["Qy"]
            if TK_JSON["lk"].get("side", "in") == "in":       # 摇杆在内侧：销座从轴承隔板往外伸
                qb = Part.makeCylinder(8, 32 - 25.5, V(25.5, -qu, ZU + qv), V(1, 0, 0))
            else:                                             # 摇杆在外侧（与连杆同一平面 x 6–10）：销座从机头顶内壁吊下来，在摇杆外侧 x −10…5
                qb = Part.makeCylinder(8, 15, V(-10, -qu, ZU + qv), V(1, 0, 0)).fuse(
                    Part.makeBox(15, 12, 60, V(-10, -qu - 6, ZU + qv)))
            bs.append(qb.cut(Part.makeCylinder(3, 40, V(-20, -qu, ZU + qv), V(1, 0, 0))))
        for b_ in bs:
            hollow = fuse_fillet(hollow, b_.common(solid))
        hollow = hollow.cut(Part.makeCylinder(6, 200, V(0, 0, 20), V(0, 0, 1)))       # 针杆孔 Ø12 穿过机头底（导套外径）
        hollow = hollow.cut(Part.makeCylinder(7, 14, V(0, 0, 36), V(0, 0, 1)))        # 底下沉孔 Ø14 到 z 50：上止点时针夹进来 0.5 mm
        hollow = hollow.removeSplitter()
        info["bosses"] = len(bs)
    if DETAIL:
        hollow = details(solid, hollow, info)
    # 机头前盖板窗口（Eddie 11-10 14:08）：机头前面开窗，调针杆高度、挑线机构、加油都从这里；窗口四周留 8 mm 法兰装前盖板
    if FRONT_COVER and not DETAIL:
        win = Part.makeBox(FC_WIN[1] - FC_WIN[0], WALL + 4, FC_WIN[3] - FC_WIN[2], V(FC_WIN[0], HEAD["y0"] - 2, FC_WIN[2]))
        win = win.makeFillet(10, [e for e in win.Edges if abs(e.BoundBox.YLength - (WALL + 4)) < 1e-6])
        hollow = hollow.cut(win)
        info["front_window"] = FC_WIN
    info["solid_valid"] = solid.isValid()
    info["hollow_valid"] = hollow.isValid()
    if SPLIT and DETAIL:
        up, lo = split(hollow)
        SPLIT_PARTS["upper"], SPLIT_PARTS["lower"] = up, lo
        info["mass_upper_kg"] = round(up.Volume * 7.2e-6, 2)
        info["mass_lower_kg"] = round(lo.Volume * 7.2e-6, 2)
    return solid, hollow, info


# ---------------------------------------------------------------- 外观件
def cyl(r, h, p, d=V(1, 0, 0)):
    return Part.makeCylinder(r, h, p, d)


def fil(s, r, pick=None):
    """给 s 自己的边倒圆角；pick(edge) 选边，默认全部；失败就原样返回"""
    es = [e for e in s.Edges if pick is None or pick(e)]
    try:
        return s.makeFillet(r, es) if es else s
    except Exception:  # noqa: BLE001
        return s


def circ_far(s, d):
    """回转体远端（沿 d 方向最远）那一圈边"""
    c = s.BoundBox
    def f(e):
        m = e.BoundBox.Center
        return hasattr(e.Curve, "Radius") and (m - c.Center).dot(d) > 0
    return f


def screw_7380(p, axis, d=4):
    """ISO 7380 内六角圆头螺钉的头（M4：头径 7.6、头高 2.2、内六角 2.5），p 是支承面中心，axis 指向头外"""
    dk, k, s = {4: (7.6, 2.2, 2.5), 5: (9.5, 2.75, 3.0), 6: (10.5, 3.3, 4.0)}[d]
    head = Part.makeCylinder(dk / 2, k * 0.45, p, axis).fuse(Part.makeSphere(dk / 2, p + axis * (k * 0.45)).common(
        Part.makeCylinder(dk / 2, k * 0.55, p + axis * (k * 0.45), axis)))
    hexp = [p + axis * (k + 0.1) + _perp(axis, a) * (s / math.sqrt(3)) for a in range(0, 360, 60)]
    hx = Part.Face(Part.makePolygon(hexp + [hexp[0]])).extrude(axis * -(k * 0.6))
    return head.cut(hx)


def _perp(axis, deg):
    a = V(axis)
    u = V(0, 0, 1) if abs(a.z) < 0.9 else V(1, 0, 0)
    e1 = a.cross(u)
    e1.normalize()
    e2 = a.cross(e1)
    return e1 * math.cos(math.radians(deg)) + e2 * math.sin(math.radians(deg))


def covers(hollow, info, solid=None):
    """G4.3 面板、前盖板（铝合金压铸 ADC12，厚 3，黑灰色喷涂）和固定螺钉（ISO 7380 M4，发黑）"""
    out = {"graphite": [], "black": []}
    x0, y0 = HEAD["x0"], HEAD["y0"]
    # 面板：盖住整个机头左端，外形取机头离端头 15 mm 处的截面（圆角以外的全尺寸外形），铝合金压铸厚 3，外缘倒 R2.5
    plate = None
    try:
        sec = section_x(solid.common(Part.makeBox(400, 400, 400, V(x0 - 1, -200, 95))), x0 + 15)
        if sec is not None:
            f_ = Part.Face(sec.OuterWire)
            f_.translate(V(x0 - 3 - (x0 + 15), 0, 0))
            plate = f_.extrude(V(3, 0, 0))
            plate = fil(plate, 2.5, lambda e: e.BoundBox.XMax < x0 - 2.9)
    except Exception as exc:  # noqa: BLE001
        print("face plate skipped", exc)
        plate = None
    if plate is not None:
        for _, y_, z_ in info.get("faceplate_holes", []):
            plate = plate.cut(Part.makeCylinder(2.25, 6, V(x0 - 5, y_, z_), V(1, 0, 0)))
            out["black"].append(screw_7380(V(x0 - 3, y_, z_), V(-1, 0, 0)))
        out["graphite"].append(plate)
    a0, a1, b0, b1 = FC_PLATE
    cv = None
    try:                                              # 随形：取机壳前面（含顶上圆角）这一片外表面，向外加厚 3
        reg = solid.common(Part.makeBox(a1 - a0 + 2, 40, b1 - b0 + 30, V(a0 - 1, y0 - 2, b0 - 1)))
        fs = []
        for f in reg.Faces:
            u_, v_ = f.Surface.parameter(f.CenterOfMass)
            n_ = f.normalAt(u_, v_)
            if n_.y < -0.15 and f.CenterOfMass.y < y0 + 15:
                fs.append(f)
        th = Part.Shell(fs).makeOffsetShape(3.0, 0.01, fill=True)
        prof = Part.makeBox(a1 - a0, 80, b1 - b0, V(a0, y0 - 20, b0))
        prof = prof.makeFillet(10, [e for e in prof.Edges if abs(e.BoundBox.YLength - 80) < 1e-6])
        cv = th.common(prof)
        if cv.Volume < 1000:
            cv = None
    except Exception as exc:  # noqa: BLE001
        print("conforming cover skipped", exc)
    if cv is None:
        cv = Part.makeBox(a1 - a0, 3, b1 - b0, V(a0, y0 - 3, b0))
        cv = cv.makeFillet(10, [e for e in cv.Edges if abs(e.BoundBox.YLength - 3) < 1e-6])
    slot = Part.makeBox(10, 20, TK_SLOT[1] - TK_SLOT[0], V(X_TAKEUP - 5, y0 - 10, TK_SLOT[0]))
    slot = slot.makeFillet(4.9, [e for e in slot.Edges if abs(e.BoundBox.YLength - 20) < 1e-6])
    cv = cv.cut(slot)
    for x_, _, z_ in info.get("window_holes", []):
        cv = cv.cut(Part.makeCylinder(2.25, 5, V(x_, y0 - 4, z_), V(0, 1, 0)))
        out["black"].append(screw_7380(V(x_, y0 - 3, z_), V(0, -1, 0)))
    out["graphite"].append(cv)
    return out


def parts_visible(cast, hollow=None, info=None):
    t0, t1, crown = P["top"]
    g = {"paint": [cast], "graphite": [], "metal": [], "black": [], "blue": [], "chrome": [], "glass": []}
    if DETAIL and hollow is not None:                  # G4.3：外观就是铸件本身（带开口、法兰），面板和前盖板是单独的零件
        body = hollow
        cv = covers(hollow, info, cast)
        g["graphite"] += cv["graphite"]
        g["coverscrew"] = list(cv["black"])            # 盖板螺钉单独一组（网页上拆盖板时一起拆）
    else:
        cut = Part.makeBox(7.0, 400, 400, V(HEAD["x0"] - 1, -200, 90))
        body = cast.cut(cut)
        g["graphite"].append(cast.common(cut))
    if FRONT_COVER and not DETAIL:                                   # 前盖板：机头前面一片（比窗口四周大 8 mm），外形跟机头一样
        fx0, fx1, fz0, fz1 = FC_WIN
        cv = Part.makeBox(fx1 - fx0 + 16, 8.0, fz1 - fz0 + 16, V(fx0 - 8, HEAD["y0"] - 1, fz0 - 8))
        cv = cv.makeFillet(14, [e for e in cv.Edges if abs(e.BoundBox.YLength - 8.0) < 1e-6])
        slot = Part.makeBox(10, 20, TK_SLOT[1] - TK_SLOT[0], V(X_TAKEUP - 5, HEAD["y0"] - 10, TK_SLOT[0]))
        slot = slot.makeFillet(4.9, [e for e in slot.Edges if abs(e.BoundBox.YLength - 20) < 1e-6])
        g["graphite"].append(body.common(cv).cut(slot))
        body = body.cut(cv)
    if DETAIL and hollow is not None:                  # 加工面单独一组（亮金属），其余是铸造面（喷漆）；分两件时下件单独成组
        pieces = [("", SPLIT_PARTS["upper"]), ("_lower", SPLIT_PARTS["lower"])] if SPLIT_PARTS else [("", body)]
        for suf, sh in pieces:
            mf = machined_faces(sh)
            ids = {f.hashCode() for f in mf}
            g["paint" + suf] = [Part.makeCompound([f for f in sh.Faces if f.hashCode() not in ids])]
            g["machined" + suf] = [Part.makeCompound(mf)]
    else:
        g["paint"] = [body]
    tc = None
    if DETAIL:                                          # G4.3 顶盖随形贴在机臂顶面上（盖住两个清砂孔），4 个 M4 螺钉
        try:
            reg = cast.common(Part.makeBox(156, 56, 80, V(107, -16, 200)))
            fs = []
            for f in reg.Faces:
                u_, v_ = f.Surface.parameter(f.CenterOfMass)
                if f.normalAt(u_, v_).z > 0.3:
                    fs.append(f)
            th = Part.Shell(fs).makeOffsetShape(2.5, 0.01, fill=True)
            prof = Part.makeBox(150, 52, 120, V(110, -14, 180))
            prof = prof.makeFillet(8, [e for e in prof.Edges if abs(e.BoundBox.ZLength - 120) < 1e-6])
            tc = th.common(prof)
            for xs_ in (118.0, 252.0):
                for ys_ in (-6.0, 30.0):
                    ln = Part.LineSegment(V(xs_, ys_, 300), V(xs_, ys_, 180)).toShape().common(tc)
                    if ln.Vertexes:
                        ztop = max(v.Point.z for v in ln.Vertexes)
                        g.setdefault("coverscrew", []).append(screw_7380(V(xs_, ys_, ztop), V(0, 0, 1)))
        except Exception as exc:  # noqa: BLE001
            print("conforming top cover skipped", exc)
            tc = None
    if tc is None:
        tc = Part.makeBox(150, 52, 3, V(110, -14, (t0 + t1) / 2 + crown - 1.5))
        tc = tc.makeFillet(6, [e for e in tc.Edges if abs(e.BoundBox.ZLength - 3) < 1e-6])
    g["graphite"].append(tc)
    if not (DETAIL and REALMECH):                       # G4.3 起电机、手轮是实体零件（cad/motor.py）
        # 直驱电机与手轮（立柱外侧）
        mo = cyl(56, 54, V(PIL["x1"], 0, ZU))
        g["black"].append(fil(mo, 4, circ_far(mo, V(1, 0, 0))))
        hw = cyl(52, 20, V(PIL["x1"] + 55, 0, ZU))
        for k in range(36):                                   # 手轮外圈防滑槽
            a = 2 * math.pi * k / 36
            hw = hw.cut(cyl(1.4, 22, V(PIL["x1"] + 54, 52.5 * math.cos(a), ZU + 52.5 * math.sin(a))))
        g["graphite"].append(hw)
        g["chrome"].append(cyl(18, 3, V(PIL["x1"] + 75, 0, ZU)))
        g["blue"].append(cyl(53, 2.0, V(PIL["x1"] + 53.5, 0, ZU)).cut(cyl(49, 3, V(PIL["x1"] + 53, 0, ZU))))
    # 针杆、压脚杆、机针、压脚
    if not REALMECH:
        g["chrome"].append(cyl(4, 32, V(0, 0, HEAD["z0"] - 30), V(0, 0, 1)))                # 针杆（上止点附近）
        g["metal"].append(Part.makeBox(10, 10, 9, V(-5, -5, 14)))                           # 针夹
        g["chrome"].append(cyl(0.9, 20, V(0, 0, -1.5), V(0, 0, 1)).fuse(cyl(1.0, 8, V(0, 0, 13), V(0, 0, 1))))
    g["chrome"].append(cyl(4, 40, V(-16, 6, HEAD["z0"] - 38), V(0, 0, 1)))              # 压脚杆
    foot = Part.makeBox(30, 26, 4, V(-20, -14, 0.2)).fuse(Part.makeBox(8, 8, 18, V(-20, 2, 3)))
    foot = foot.cut(cyl(2.4, 10, V(0, 0, -1), V(0, 0, 1)))
    g["metal"].append(foot)
    # 针板、滑板（嵌在机座顶面）
    g["metal"].append(Part.makeBox(64, 44, 0.6, V(-32, -22, -0.2)).cut(cyl(1.2, 2, V(0, 0, -1), V(0, 0, 1))))
    g["chrome"].append(Part.makeBox(46, 36, 0.6, V(-23, -58, -0.2)))
    # 挑线杆（从机头前面的长槽伸出）、夹线器、过线
    # 挑线杆：位置按设计软件的挑线四连杆算（主轴 φ = TK_PHI 时的姿态），在 x = X_TAKEUP 的平面里摆动，
    # 从前盖板上的竖槽伸出（端视的 u 指向机器前方，即 −Y）。G4 换成真零件、能转动。
    P_, M_, E_ = (V(X_TAKEUP, -u, ZU + v) for u, v in TK_POSE)
    lev = None
    for a_, b_ in ((P_, M_), (M_, E_)):
        d_ = b_ - a_
        seg = Part.makeCylinder(3.0, d_.Length, a_, d_)
        lev = seg if lev is None else lev.fuse(seg)
    eye = Part.makeTorus(4.0, 1.4, E_, V(1, 0, 0))
    if not REALMECH:
        g["chrome"].append(lev.fuse(eye))
    tz, tx = 210, 66
    g["chrome"].append(cyl(3, 22, V(tx, -46, tz), V(0, -1, 0)))
    for dy in (-52, -55.5):
        g["chrome"].append(cyl(11, 1.4, V(tx, dy, tz), V(0, -1, 0)))
    g["chrome"].append(Part.makeTorus(9, 0.6, V(tx, -50, tz), V(0, -1, 0), 0, 360, 200))   # 挑线簧（示意）
    g["chrome"].append(cyl(1.6, 16, V(tx + 22, -46, tz + 14), V(0, -1, 0)))                # 过线钩
    kn = cyl(9, 10, V(tx, -58, tz), V(0, -1, 0))
    g["graphite"].append(fil(kn, 2.5, circ_far(kn, V(0, -1, 0))))
    # 针距旋钮、倒缝扳手、操作面板、照明
    dl = cyl(19, 10, V(340, PIL["y0"] + 2, 170), V(0, -1, 0))
    g["graphite"].append(fil(dl, 2, circ_far(dl, V(0, -1, 0))))
    g["blue"].append(cyl(19.3, 1.2, V(340, PIL["y0"] - 7.2, 170), V(0, -1, 0)).cut(cyl(17, 2, V(340, PIL["y0"] - 6.7, 170), V(0, -1, 0))))
    lev = Part.makeBox(10, 8, 56, V(347, PIL["y0"] - 8, 60)).fuse(cyl(7, 10, V(352, PIL["y0"] + 2, 116), V(0, -1, 0)))
    g["graphite"].append(lev)
    pan = Part.makeBox(76, 9, 46, V(118, -47, 168))
    pan = pan.makeFillet(4, [e for e in pan.Edges if abs(e.BoundBox.YLength) < 1e-6])
    g["black"].append(pan)
    g["glass"].append(Part.makeBox(40, 0.6, 30, V(124, -47.6, 176)))
    for i_ in range(4):                                   # 面板按键
        g["chrome"].append(cyl(3.2, 1.6, V(172 + (i_ % 2) * 12, -47, 182 + (i_ // 2) * 14), V(0, -1, 0)))
    g["glass"].append(Part.makeBox(40, 30, 1.0, V(-20, -32, HEAD["z0"] - 1.0)))          # 机头底下的照明
    # 绕线器（机座顶面右后）
    # 绕线器装在台板上（不在机头上），效果图里不画
    # 铭牌：机臂前面
    try:
        from FreeCAD import Vector as _V  # noqa: F401
        ws = Part.makeWireString("WQ-LS", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12, 0)
        faces = [Part.Face(Part.Wire(w)) for ch_ in ws for w in ch_]
        txt = Part.makeCompound([f.extrude(V(0, 0, 0.8)) for f in faces])
        m = App.Matrix()
        m.rotateX(math.radians(90))
        txt = txt.transformGeometry(m)
        txt.translate(V(-34, HEAD["y0"] + 0.3, 140))
        g["blue"].append(txt)
    except Exception as exc:  # noqa: BLE001
        print("text skipped", exc)
    return g


def main():
    cast, hollow, info = casting()
    hollow.exportStep(os.path.join(OUT, "housing.step"))
    for k_, s_ in SPLIT_PARTS.items():
        s_.exportStep(os.path.join(OUT, f"housing_{k_}.step"))
    g = parts_visible(cast, hollow, info)
    stats = {"variant": VAR, "info": info, "volume_cm3": round(hollow.Volume / 1000, 1), "mass_kg_ht250": round(hollow.Volume * 7.2e-6, 1)}
    for mat, shapes in g.items():
        if not shapes:
            continue
        comp = Part.makeCompound(shapes)
        mesh = MeshPart.meshFromShape(Shape=comp, LinearDeflection=0.08, AngularDeflection=0.12, Relative=False)
        mesh.write(os.path.join(OUT, f"{mat}.stl"))
        stats[mat] = mesh.CountFacets
    with open(os.path.join(OUT, "stats.json"), "w") as f:
        json.dump(stats, f, ensure_ascii=False)
    print(json.dumps(stats, ensure_ascii=False))


if os.environ.get("WQ_NOMAIN") != "1":
    main()
