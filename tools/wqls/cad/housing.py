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
WALL = float(os.environ.get("WQ_WALL", 6.0))
ARM_Y = (-46.0, 70.0)          # 机臂前后（G3 模态迭代：由 −38…60 加深到 −46…70）
RIBS = os.environ.get("WQ_RIBS", "1") == "1"
HEADWALL = float(os.environ.get("WQ_HEADWALL", 5.0))
BEDWALL = float(os.environ.get("WQ_BEDWALL", 6.0))
ROOTWALL = float(os.environ.get("WQ_ROOTWALL", 9.0))
ROOT_X = float(os.environ.get("WQ_ROOTX", 230.0))
BED_RIB_H = float(os.environ.get("WQ_BEDRIB", 30.0))       # 机座纵筋高（从机座顶面往下）
RIB_T = 7.0
RIB_X = (75.0, 150.0, 225.0)
S_BELT_X = 352.0
ARMB = float(os.environ.get("WQ_ARMB", 120.0))                   # 机臂下沿（机臂空间高度 135；G1 的 160 在 G3 为比例改小，见细则）

ZU = 200.0
BED = dict(x0=-105.0, x1=412.0, y0=-62.0, y1=116.0, z0=-62.0)
PIL = dict(x0=300.0, x1=396.0, y0=float(os.environ.get("WQ_PY0", -70.0)), y1=float(os.environ.get("WQ_PY1", 96.0)))
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
           (PIL["x1"] - k, -10.0 if k else 0.0), (PIL["x0"] + k, -10.0 if k else 0.0), (PIL["x0"] + k, ARMB - k),
           (HEAD["x1"] - k, ARMB - k), (HEAD["x1"] - k, ARMB - P["r_hj"] - 18 - k), (nr - k, max(ARMB - P["r_hj"] - 38, HEAD["z0"] + 26) - k)]
    rr = [8, 8, 24, 24, P["r_head"], 1200 if crown else 0, P["r_out"], 0, 0, P["r_arch"], P["r_hj"], 10, 10]
    if k:
        rr = [max(r - k, 0) if 0 < r < 900 else r for r in rr]
        rr[0] = rr[1] = 0
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
    boss = Part.makeCylinder(9, 8, V(0, 0, HEAD["z0"] - 8), V(0, 0, 1)).fuse(Part.makeCylinder(9, 8, V(-16, 6, HEAD["z0"] - 8), V(0, 0, 1)))
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
    bw = BEDWALL
    bcav = Part.makeBox(BED["x1"] - BED["x0"] - 2 * bw, BED["y1"] - BED["y0"] - 2 * bw, -BED["z0"] - bw + 1,
                        V(BED["x0"] + bw, BED["y0"] + bw, BED["z0"] - 1))
    hollow = solid.cut(cav).cut(bcav)
    # 机头壁薄一些（机头在悬臂端，越轻固有频率越高）：机头区域按 HEADWALL 再挖一次
    if HEADWALL < WALL:
        hf = Part.Face(outline(HEADWALL)).extrude(V(0, 300, 0))
        hf.translate(V(0, -150, 0))
        ht = Part.Face(plan(HEADWALL)).extrude(V(0, 0, zhi - zlo))
        ht.translate(V(0, 0, zlo))
        hbox = Part.makeBox(HEAD["x1"] - HEAD["x0"] - 2 * HEADWALL, 400, 400, V(HEAD["x0"] + HEADWALL, -200, HEAD["z0"] + HEADWALL))
        try:
            hollow = hollow.cut(hf.common(ht).common(hbox))
            info["headwall"] = HEADWALL
        except Exception as exc:  # noqa: BLE001
            info["headwall"] = f"skipped: {str(exc)[:60]}"
    # 筋（G3 模态迭代加的）：机臂横隔板、立柱横隔板、机座纵筋和立柱下的横筋。隔板上开孔：上轴、油管和线、同步带
    if RIBS:
        rb = []
        for x in RIB_X:
            sl = Part.makeBox(RIB_T, 400, 400, V(x - RIB_T / 2, -200, ARMB - 20))
            hole = Part.makeCylinder(20, RIB_T + 2, V(x - RIB_T / 2 - 1, 0, ZU), V(1, 0, 0))
            hole = hole.fuse(Part.makeCylinder(12, RIB_T + 2, V(x - RIB_T / 2 - 1, 30, ARMB + 22), V(1, 0, 0)))
            rb.append(sl.common(cav).cut(hole))
        for z in (55.0, 115.0):
            sl = Part.makeBox(PIL["x1"] - PIL["x0"] + 20, 300, RIB_T, V(PIL["x0"] - 10, -150, z))
            slot = Part.makeBox(34, 60, RIB_T + 2, V(S_BELT_X - 17, -30, z - 1)).fuse(Part.makeCylinder(10, RIB_T + 2, V(330, 45, z - 1), V(0, 0, 1)))
            rb.append(sl.common(cav).cut(slot))
        for y in (-20.0, 50.0):
            sl = Part.makeBox(BED["x1"] - 80, RIB_T, BED_RIB_H, V(80, y - RIB_T / 2, -BED_RIB_H))
            rb.append(sl.common(bcav))
        for x in (PIL["x0"], PIL["x1"] - RIB_T):
            sl = Part.makeBox(RIB_T, BED["y1"] - BED["y0"], -BED["z0"], V(x, BED["y0"], BED["z0"]))
            rb.append(sl.common(bcav))
        for r_ in rb:
            hollow = hollow.fuse(r_)
        hollow = hollow.removeSplitter()
    info["solid_valid"] = solid.isValid()
    info["hollow_valid"] = hollow.isValid()
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


def parts_visible(cast):
    t0, t1, crown = P["top"]
    g = {"paint": [cast], "graphite": [], "metal": [], "black": [], "blue": [], "chrome": [], "glass": []}
    # 面板（机头左端）、顶盖
    # 面板：机头左端 7 mm 一片，外形跟机头一样（真机上是可拆的面板，盖住针杆、挑线机构）
    cut = Part.makeBox(7.0, 400, 400, V(HEAD["x0"] - 1, -200, 90))
    g["paint"] = [cast.cut(cut)]
    g["graphite"].append(cast.common(cut))
    tc = Part.makeBox(150, 52, 3, V(110, -14, (t0 + t1) / 2 + crown - 1.5))
    tc = tc.makeFillet(6, [e for e in tc.Edges if abs(e.BoundBox.ZLength - 3) < 1e-6])
    g["graphite"].append(tc)
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
    g["graphite"].append(Part.makeBox(48, 1.2, 10, V(-30, HEAD["y0"] - 1.2, 196)))     # 槽盖
    tk = Part.makeBox(30, 5, 6, V(-34, HEAD["y0"] - 16, 205)).fuse(Part.makeBox(5, 16, 6, V(-34, HEAD["y0"] - 16, 205)))
    tk = tk.cut(cyl(1.8, 10, V(-8, HEAD["y0"] - 14, 204), V(0, 0, 1)))                      # 挑线杆伸出机头，头上有线眼
    g["chrome"].append(tk)
    tz, tx = 210, 66
    g["chrome"].append(cyl(3, 22, V(tx, -46, tz), V(0, -1, 0)))
    for dy in (-52, -55.5):
        g["chrome"].append(cyl(11, 1.4, V(tx, dy, tz), V(0, -1, 0)))
    g["chrome"].append(Part.makeTorus(9, 0.6, V(tx, -50, tz), V(0, -1, 0), 0, 360, 200))   # 挑线簧（示意）
    g["chrome"].append(cyl(1.6, 16, V(tx + 22, -46, tz + 14), V(0, -1, 0)))                # 过线钩
    kn = cyl(9, 10, V(tx, -58, tz), V(0, -1, 0))
    g["graphite"].append(fil(kn, 2.5, circ_far(kn, V(0, -1, 0))))
    # 针距旋钮、倒缝扳手、操作面板、照明
    dl = cyl(19, 10, V(340, -52, 170), V(0, -1, 0))
    g["graphite"].append(fil(dl, 2, circ_far(dl, V(0, -1, 0))))
    g["blue"].append(cyl(19.3, 1.2, V(340, -61.2, 170), V(0, -1, 0)).cut(cyl(17, 2, V(340, -60.7, 170), V(0, -1, 0))))
    lev = Part.makeBox(10, 8, 56, V(347, -62, 60)).fuse(cyl(7, 10, V(352, -52, 116), V(0, -1, 0)))
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
    g = parts_visible(cast)
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


main()
