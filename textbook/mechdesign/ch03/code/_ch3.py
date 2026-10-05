"""第 3 章共用：三维模型（码垛输送线的轴承座、协作机器人关节空心轴 RJ-201、减速器输出轴 SH-301 B 版），
由模型投影出视图、剖视图和断面图，以及按国标线型、尺寸注法画图的小工具。

图都由三维模型投影生成（与零件库出图同一种办法，library/tools/svg2d.py），不手画轮廓。
坐标：X 向右、Y 向后（远离看图的人）、Z 向上；主视图从前（−Y）往后看。
数据来源：轴承尺寸取本书数字化标准表（GB/T 276）；RJ-201 的结构取数字工厂案例件（hub/case_parts.py，与第 33.10 节一致）；
SH-301 B 版取第 33 章（ch33/code/_shaft.py）；物料与 BOM 取数字工厂（factory/factory/data.py）。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (ROOT / "factory", ROOT / "factory" / "digital", HERE.parents[1] / "conventions", HERE.parents[1] / "ch33" / "code"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import mdstd                            # noqa: E402
from factory import data as F           # noqa: E402
from hub import case_parts as CP        # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

from bookout import COLORS, T           # noqa: E402

INK, MUTED = COLORS["ink"], COLORS["muted"]
R20 = [10, 11.2, 12.5, 14, 16, 18, 20, 22.4, 25, 28, 31.5, 35.5, 40, 45, 50, 56, 63, 71, 80, 90, 100, 112, 125, 140, 160]

# ---------------------------------------------------------------- 线型（GB/T 4457.4、GB/T 17450）：粗线宽 d，细线 d/2
# 图在书里约缩小一半印出，线宽按印出后的效果取（单位 pt）
LW = {"thick": 1.1, "thin": 0.45}
DASH = (0, (4.0, 1.6))                  # 细虚线：不可见轮廓
CHAIN = (0, (9.0, 1.6, 1.4, 1.6))       # 细点画线：轴线、对称中心线
FS = 6.0                                # 尺寸数字的字高（pt）


# ---------------------------------------------------------------- 三维模型
def r20_up(x):
    return next(v for v in R20 if v >= x - 1e-9)


def pillow_params(brg="6207"):
    """轴承座（整体式，带台阶孔：一侧装轴承，另一侧台阶挡住外圈）。尺寸都由轴承型号推出来（本书的设计规则，3.8 节）。"""
    b = mdstd.bearing(brg)
    D, B = b["D"], b["B"]
    wall = math.floor(0.12 * D + 3 + 0.5)                         # 轴承孔的壁厚
    Ro = D / 2 + wall                                  # 上部圆弧半径
    H = r20_up(Ro + 2)                                 # 中心高取 R20 优先数
    bolt, dh = (("M8", 9.0) if D <= 52 else ("M10", 11.0) if D <= 72 else ("M12", 13.5))   # 地脚螺栓与通孔（GB/T 5277 中等）
    W = B + 14                                         # 座宽：轴承宽 + 端盖止口 4 + 台阶 10
    Wb = W + 12                                        # 底板宽
    tb = math.floor(0.25 * H + 0.5)                               # 底板厚（轴承孔底比底板顶面高，孔不切到底板）
    Lh = 2 * (Ro + dh + 2)                             # 两地脚孔中心距
    L = math.ceil(Lh + 3 * dh)                         # 底板长（取整）
    return {"brg": brg, "d": b["d"], "D": D, "B": B, "wall": wall, "Ro": Ro, "H": H, "bolt": bolt, "dh": dh, "W": W, "Wb": Wb,
            "tb": tb, "Lh": Lh, "L": L, "D2": D - 8, "seat": B + 4, "Lr": Lh - 2 * dh - 10, "hr": 2.0, "dg": 6.0}


def pillow_block(p):
    import build123d as bd
    L, W, Wb, H, Ro, tb = p["L"], p["W"], p["Wb"], p["H"], p["Ro"], p["tb"]
    s = bd.Pos(0, 0, tb / 2) * bd.Box(L, Wb, tb)
    s = s + bd.Pos(0, 0, H / 2) * bd.Box(2 * Ro, W, H)
    s = s + bd.Pos(0, 0, H) * bd.Rot(90, 0, 0) * bd.Cylinder(Ro, W)
    s = s - bd.Pos(0, 0, H) * bd.Rot(90, 0, 0) * bd.Cylinder(p["D2"] / 2, W + 2)                        # 台阶孔（小）贯通
    y0 = -W / 2 + p["seat"] / 2 - 0.5                                                                     # 轴承孔从前端面开
    s = s - bd.Pos(0, y0, H) * bd.Rot(90, 0, 0) * bd.Cylinder(p["D"] / 2, p["seat"] + 1)
    for x in (-p["Lh"] / 2, p["Lh"] / 2):
        s = s - bd.Pos(x, 0, tb / 2) * bd.Cylinder(p["dh"] / 2, tb + 2)
    s = s - bd.Pos(0, 0, p["hr"] / 2 - 0.5) * bd.Box(p["Lr"], Wb + 2, p["hr"] + 1)                      # 底面中间挖空，两端着地
    hg = Ro - p["D"] / 2 + 2
    s = s - bd.Pos(0, 0, H + p["D"] / 2 - 1 + hg / 2) * bd.Cylinder(p["dg"] / 2, hg)                     # 顶部注油孔
    return s.clean()


RJ_HOLES = {"减速器法兰": (6, 5.5, 60.0), "大臂法兰": (6, 6.6, 68.0)}   # 本章补的螺钉通孔：个数、孔径、分布圆直径（M5、M6，GB/T 5277 中等）


def rj201(holes=False, axis="x"):
    """协作机器人肩关节空心轴 RJ-201（第 33.10 节修改后的结构，与数字工厂案例件相同：花键段、螺纹段简化成圆柱）。
    holes=True 时补上两个法兰的螺钉通孔——这是出零件图时补全的细节，第 33 章算强度时没有考虑。轴线沿 X。"""
    import build123d as bd
    segs, bore, fil = CP.CASES["RJ-201"]
    z, s, steps = 0.0, None, []
    for k, (D, L, _) in enumerate(segs):
        c = bd.Pos(0, 0, z) * bd.Cylinder(D / 2, L, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        s = c if s is None else s + c
        z += L
        if k + 1 < len(segs) and abs(segs[k + 1][0] - D) / 2 > 1.5 * fil:      # 台阶够高才倒圆
            steps.append(z)
    s = s.clean()
    sel = []
    for zz in steps:
        es = [e for e in s.edges() if e.geom_type == bd.GeomType.CIRCLE and abs(e.center().Z - zz) < 1e-6]
        if len(es) == 2:
            sel.append(min(es, key=lambda e: e.radius))
    s = s.fillet(fil, sel)
    s = s - bd.Pos(0, 0, -1) * bd.Cylinder(bore / 2, z + 2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    if holes:
        z0 = 0.0
        for D, L, name in segs:
            if name in RJ_HOLES:
                n, dh, pcd = RJ_HOLES[name]
                for k in range(n):
                    a = 2 * math.pi * k / n                         # 有两个孔正好在主视图的剖切面上（轴线转到 X 后在正上、正下）
                    s = s - bd.Pos(pcd / 2 * math.cos(a), pcd / 2 * math.sin(a), z0 + L / 2) * bd.Cylinder(dh / 2, L + 2)
            z0 += L
    if axis == "x":                                                  # 轴线转到 X（零件图按加工位置把轴线横放）
        s = bd.Rot(0, 90, 0) * s
    return s


def rj_layout():
    segs, bore, fil = CP.CASES["RJ-201"]
    out, z = [], 0.0
    for D, L, name in segs:
        out.append((z, z + L, D, name))
        z += L
    return out, z, bore, fil


def sh301b():
    """SH-301 B 版（第 33 章）：沿 X 叠圆柱 → 台阶圆角 → 两个 A 型键槽（键槽朝 +Z，主视图里看得到）。"""
    import build123d as bd
    import _shaft as S
    z, s = 0.0, None
    for d, L, *_ in S.SEG_B:
        c = bd.Pos(0, 0, z) * bd.Cylinder(d / 2, L, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        s = c if s is None else s + c
        z += L
    s = s.clean()
    for zz, r in S.FILLET_B.items():
        es = [e for e in s.edges() if e.geom_type == bd.GeomType.CIRCLE and abs(e.center().Z - zz) < 1e-6]
        if len(es) == 2:
            s = s.fillet(r, [min(es, key=lambda e: e.radius)])
    for z0, z1, d, kind in sh301_keyways():
        k = mdstd.key_for(d)
        b, t = k["b"], k["t"]
        if kind == "C":
            z1 = z1 + b                                # 开口键槽：铣出轴端
        Hc = 10.0
        yc = -(d / 2 - t + Hc / 2)                     # 键槽朝 −Y，即朝着看主视图的人（GB 的习惯画法）
        cut = bd.Pos(0, yc, (z0 + z1) / 2) * bd.Box(b, Hc, z1 - z0 - b)
        for zc in ((z0 + b / 2,) if kind == "C" else (z0 + b / 2, z1 - b / 2)):
            cut = cut + bd.Pos(0, yc, zc) * bd.Rot(90, 0, 0) * bd.Cylinder(b / 2, Hc)
        s = s - cut
    return bd.Rot(0, 90, 0) * s            # 轴线由 Z 转到 X，Y 不变


def sh301_keyways():
    """键槽位置与键型（第 33.2 节，ch33/code/_shaft.py 的 KEYWAYS）：[(z0, z1, 轴径, 键型)]"""
    import _shaft as S
    return S.KEYWAYS


# ---------------------------------------------------------------- 投影（第一角画法）
EYE = {  # 视图：(视点方向, 视图的“上”)；视图坐标 u 向右、v 向上（看图人看到的）
    "front": ((0, -1, 0), (0, 0, 1)), "top": ((0, 0, 1), (0, 1, 0)), "left": ((-1, 0, 0), (0, 0, 1)),
    "right": ((1, 0, 0), (0, 0, 1)), "iso": ((1, -1, 0.82), (0, 0, 1)), "iso2": ((-1, -1, 0.82), (0, 0, 1)), "bottom": ((0, 0, -1), (0, -1, 0)), "back": ((0, 1, 0), (0, 0, 1)),
}


def _polys(edges):
    out = []
    for e in edges:
        try:
            n = 1 if e.geom_type.name == "LINE" else max(12, min(96, int(e.length / 0.6) + 2))
            out.append([((e @ (i / n)).X, (e @ (i / n)).Y) for i in range(n + 1)])
        except Exception:  # noqa: BLE001
            continue
    return out


def _hlr(shape, d, up):
    """隐藏线消除（OpenCascade HLRBRep，与 build123d 的 project_to_viewport 相同），但不要光滑过渡边：
    圆角与平面、圆柱相切处的边按国标不画线（GB/T 4458.1“过渡线”另有画法，本章不画）。"""
    import build123d as bd
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
    from OCP.HLRAlgo import HLRAlgo_Projector
    from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp_Explorer
    from OCP.BRepLib import BRepLib
    BRepLib.EncodeRegularity_s(shape.wrapped, 1e-4)      # 标出相切连续的边，HLR 才会把它们归入“光滑边”
    algo = HLRBRep_Algo()
    algo.Add(shape.wrapped)
    ax = gp_Ax2(gp_Pnt(*(1e5 * c for c in d)), gp_Dir(*d))
    ax.SetYDirection(gp_Dir(*_ortho(up, d)))
    algo.Projector(HLRAlgo_Projector(ax))
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)

    def edges(comps):
        out = []
        for c in comps:
            if c.IsNull():
                continue
            ex = TopExp_Explorer(c, TopAbs_EDGE)
            while ex.More():
                out.append(bd.Edge(ex.Current()))
                ex.Next()
        return out
    return edges([h.VCompound(), h.OutLineVCompound()]), edges([h.HCompound(), h.OutLineHCompound()])


def _ortho(up, d):
    import numpy as np
    d = np.array(d, float) / np.linalg.norm(d)
    u = np.array(up, float)
    u = u - u.dot(d) * d
    return tuple(u / np.linalg.norm(u))


def project(shape, view):
    """→ (可见轮廓, 不可见轮廓)，都是折线列表 [(u, v), ...]"""
    d, up = EYE[view]
    vis, hid = _hlr(shape, d, up)
    return _polys(vis), _polys(hid)


def _face_polys(f, view):
    """平面上的剖面区域 → 视图坐标的多边形（外轮廓 + 内孔，分别返回）"""
    d, up = EYE[view]
    u_ax = _cross(d, up)
    u_ax = tuple(-c for c in u_ax)
    res = []
    for w in [f.outer_wire()] + list(f.inner_wires()):
        pts = []
        for e in w.edges():
            n = 1 if e.geom_type.name == "LINE" else max(12, int(e.length / 0.6) + 2)
            for i in range(n):
                p = e @ (i / n)
                pts.append((_dot((p.X, p.Y, p.Z), u_ax), _dot((p.X, p.Y, p.Z), up)))
        res.append(pts)
    return res


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def section(shape, view="front", keep=None, plane_at=0.0, local=None):
    """剖视：用过 plane_at 的剖切面剖开，拿走靠近看图人的部分。
    keep：None = 全剖；"half" = 半剖（只拿走右前四分之一，主视图右半剖开）；local = (u0, u1, v0, v1) 局部剖的范围。
    → (可见轮廓, 不可见轮廓, 剖面区域[多边形列表])"""
    import build123d as bd
    bb = shape.bounding_box()
    big = 4 * max(bb.size.X, bb.size.Y, bb.size.Z) + 10
    d, up = EYE[view]
    n = d                                           # 视线方向（指向看图人）
    # 拿走的部分：在剖切面靠看图人一侧的半空间
    c = tuple(plane_at * abs(k) + k * big / 2 for k in n)
    cutter = bd.Pos(*c) * bd.Box(big, big, big)
    if keep == "half":
        u_ax = tuple(-x for x in _cross(d, up))
        cu = tuple(k * big / 2 for k in u_ax)
        cutter = cutter & (bd.Pos(*cu) * bd.Box(big, big, big))
    if local is not None:                           # 局部剖：只在主视图 (u = X, v = Z) 的一个矩形范围里剖开
        u0, u1, v0, v1 = local
        cutter = cutter & (bd.Pos((u0 + u1) / 2, 0, (v0 + v1) / 2) * bd.Box(u1 - u0, big, v1 - v0))
    part = shape - cutter
    vis, hid = project(part, view)
    if keep == "half":                              # 半剖：外形与剖视的分界画点画线（对称中心线），不画剖开处的直边
        vis = [p for p in vis if not all(abs(u) < 1e-3 for u, _ in p)]
    if local is not None:                           # 局部剖的分界画波浪线，不画剖开处的直边
        def on_edge(p):
            return all(abs(u - u0) < 1e-3 or abs(u - u1) < 1e-3 for u, _ in p)
        vis = [p for p in vis if not on_edge(p)]
        hid = [p for p in hid if not on_edge(p)]
    regions = []
    for f in part.faces():
        cc = f.center()
        try:
            nn = f.normal_at(cc)
        except Exception:  # noqa: BLE001
            continue
        if abs(abs(_dot((nn.X, nn.Y, nn.Z), n)) - 1) < 1e-6 and abs(_dot((cc.X, cc.Y, cc.Z), n) - plane_at) < 1e-6:
            regions.append(_face_polys(f, view))
    return vis, hid, regions


def cross_section(shape, x, view="left"):
    """断面图：在 X = x 处的截面（只画断面本身）→ 剖面区域"""
    import build123d as bd
    bb = shape.bounding_box()
    big = 4 * max(bb.size.X, bb.size.Y, bb.size.Z) + 10
    slab = bd.Pos(x - big / 2, 0, 0) * bd.Box(big, big, big)
    part = shape & slab
    regs = []
    for f in part.faces():
        cc = f.center()
        if abs(cc.X - x) < 1e-6:
            regs.append(_face_polys(f, view))
    return regs


# ---------------------------------------------------------------- 画图
class Sheet:
    """在 matplotlib 的坐标轴上按毫米画工程图：粗实线、细实线、虚线、点画线、剖面线、尺寸、粗糙度、标题栏。"""

    def __init__(self, ax, scale=1.0):
        self.ax, self.k = ax, scale
        ax.set_aspect("equal")
        ax.axis("off")

    def P(self, pts, dx=0.0, dy=0.0):
        return [(dx + u * self.k, dy + v * self.k) for u, v in pts]

    def polys(self, polys, kind="thick", dx=0.0, dy=0.0, color=None):
        for p in polys:
            q = self.P(p, dx, dy)
            self.ax.plot([a for a, _ in q], [b for _, b in q], color=color or INK, solid_capstyle="round",
                         lw=LW["thick" if kind == "thick" else "thin"], ls=DASH if kind == "hidden" else (CHAIN if kind == "center" else "-"))

    def line(self, p, q, kind="thin", color=None):
        self.polys([[p, q]], kind, color=color)

    def raw_line(self, p, q, kind="thin", color=None):
        self.ax.plot([p[0], q[0]], [p[1], q[1]], color=color or INK, lw=LW["thick" if kind == "thick" else "thin"],
                     ls=DASH if kind == "hidden" else (CHAIN if kind == "center" else "-"))

    def hatch(self, regions, dx=0.0, dy=0.0, angle=45, spacing=2.2):
        """剖面线：45° 细实线，间距按印出后约 1–1.5 mm；区域内的孔不画"""
        from matplotlib.path import Path as MPath
        for reg in regions:
            verts, codes = [], []
            for ring in reg:
                q = self.P(ring, dx, dy)
                verts += q + [q[0]]
                codes += [MPath.MOVETO] + [MPath.LINETO] * (len(q) - 1) + [MPath.CLOSEPOLY]
            path = MPath(verts, codes)
            xs = [a for a, _ in verts]
            ys = [b for _, b in verts]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            from matplotlib.patches import PathPatch
            clip = PathPatch(path, transform=self.ax.transData, fc="none", ec="none")
            self.ax.add_patch(clip)
            t = math.tan(math.radians(angle))
            c0, c1 = (y0 - t * x1, y1 - t * x0) if t > 0 else (y0 - t * x0, y1 - t * x1)
            c = c0 - (c0 % spacing)
            while c <= c1:
                ln, = self.ax.plot([x0 - 5, x1 + 5], [c + t * (x0 - 5), c + t * (x1 + 5)], color=INK, lw=LW["thin"] * 0.85)
                ln.set_clip_path(clip)
                c += spacing / math.cos(math.radians(angle))

    def text(self, x, y, s, size=FS, ha="center", va="bottom", rot=0, color=None, **kw):
        self.ax.text(x, y, s, fontsize=size, ha=ha, va=va, rotation=rot, color=color or INK, **kw)

    def arrow(self, p, q, size=2.6):
        """箭头：尖在 q"""
        a = math.atan2(q[1] - p[1], q[0] - p[0])
        w = math.radians(10)
        tri = [q, (q[0] - size * math.cos(a - w), q[1] - size * math.sin(a - w)), (q[0] - size * math.cos(a + w), q[1] - size * math.sin(a + w))]
        self.ax.add_patch(Polygon(tri, closed=True, fc=INK, ec=INK, lw=0.2))

    def dim(self, p, q, off, text, size=FS, ext=True, tside=1, tpos=0.5):
        """线性尺寸：p、q 为两尺寸界线的端点（图上坐标），off 为尺寸线到 pq 连线的距离（正负表示在哪一侧）。
        水平或竖直尺寸都用它；数字写在尺寸线上方（竖直尺寸写在左侧、字头朝左，GB/T 4458.4）。"""
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        a = (p[0] + nx * off, p[1] + ny * off)
        b = (q[0] + nx * off, q[1] + ny * off)
        if ext:
            s = 1 if off > 0 else -1
            self.raw_line((p[0] + nx * s * 0.8, p[1] + ny * s * 0.8), (a[0] + nx * s * 2, a[1] + ny * s * 2))
            self.raw_line((q[0] + nx * s * 0.8, q[1] + ny * s * 0.8), (b[0] + nx * s * 2, b[1] + ny * s * 2))
        self.raw_line(a, b)
        if L > 7:
            self.arrow(b, a)
            self.arrow(a, b)
        else:                                      # 位置不够：箭头画在外面
            ux, uy = dx / L, dy / L
            self.raw_line((a[0] - ux * 5, a[1] - uy * 5), a)
            self.raw_line(b, (b[0] + ux * 5, b[1] + uy * 5))
            self.arrow((a[0] - ux * 5, a[1] - uy * 5), a)
            self.arrow((b[0] + ux * 5, b[1] + uy * 5), b)
        ang = math.degrees(math.atan2(dy, dx))
        if ang > 90.1 or ang < -89.9:
            ang += 180
        mx, my = a[0] + (b[0] - a[0]) * tpos, a[1] + (b[1] - a[1]) * tpos
        ox, oy = -math.sin(math.radians(ang)) * 0.6 * tside, math.cos(math.radians(ang)) * 0.6 * tside
        self.ax.text(mx + ox, my + oy, text, fontsize=size, ha="center", va="bottom" if tside > 0 else "top",
                     rotation=ang, rotation_mode="anchor", color=INK, zorder=6,
                     bbox=dict(boxstyle="square,pad=0.08", fc="white", ec="none"))   # 尺寸数字不被任何图线穿过（GB/T 4458.4）

    def ra(self, x, y, value, ang=0, size=FS * 0.9, leader=None):
        """表面粗糙度（GB/T 131-2006，去除材料）：尖点在 (x, y) 的表面上，符号朝外；ang 为表面外法线方向（度，0 = 向上）"""
        import numpy as np
        h = 3.2
        R = np.array([[math.cos(math.radians(ang)), -math.sin(math.radians(ang))], [math.sin(math.radians(ang)), math.cos(math.radians(ang))]])
        pts = [(0, 0), (-h * 0.577, h), (h * 0.577, h), (0, 0), (2 * h * 0.577 * 1.0 + 0.2, 2 * h), (2 * h * 0.577 + 7.5, 2 * h)]
        q = [tuple(np.array([x, y]) + R @ np.array(pp)) for pp in pts]
        self.ax.plot([a for a, _ in q[:4]], [b for _, b in q[:4]], color=INK, lw=LW["thin"])
        self.ax.plot([q[0][0], q[4][0], q[5][0]], [q[0][1], q[4][1], q[5][1]], color=INK, lw=LW["thin"])
        mid = R @ np.array([2 * h * 0.577 + 3.9, 2 * h - 0.2])
        self.ax.text(x + mid[0], y + mid[1], "Ra " + value, fontsize=size, ha="center", va="top", rotation=ang, rotation_mode="anchor", color=INK)

    def ra_leader(self, p, t, value, cast=False):
        """粗糙度注在引线上：从表面上的点 p 引线（带箭头）到 t，再画一段水平线，符号立在水平线上（GB/T 131-2006）"""
        self.raw_line(p, t)
        self.arrow(t, p, size=2.2)
        self.raw_line(t, (t[0] + 14, t[1]))
        if cast:
            self.ra_cast(t[0] + 7, t[1])
        else:
            self.ra(t[0] + 5, t[1], value)

    def ra_cast(self, x, y, size=3.2):
        """不去除材料的表面（铸造面）：基本符号的 V 形里加一个小圆"""
        from matplotlib.patches import Circle
        h = size
        self.ax.plot([x - h * 0.577, x, x + 2 * h * 0.577 + 0.2], [y + h, y, y + 2 * h], color=INK, lw=LW["thin"])
        self.ax.add_patch(Circle((x, y + h * 0.62), h * 0.3, fill=False, ec=INK, lw=LW["thin"]))

    def frame(self, W, H, bind=25.0, c=5.0):
        """图框（GB/T 14689，留装订边）：外框细实线，内框粗实线"""
        self.ax.add_patch(Polygon([(0, 0), (W, 0), (W, H), (0, H)], closed=True, fill=False, lw=LW["thin"], ec=INK))
        self.ax.add_patch(Polygon([(bind, c), (W - c, c), (W - c, H - c), (bind, H - c)], closed=True, fill=False, lw=LW["thick"] * 1.3, ec=INK))
        self.ax.set_xlim(-1, W + 1)
        self.ax.set_ylim(-1, H + 1)

    def title_block(self, x1, y0, rows):
        """标题栏（学校制图作业常用的简化格式，内容按 GB/T 10609.1：名称、图号、材料、比例、数量、设计、审核、日期、版本、单位）。
        右下角对齐 (x1, y0)。rows = dict。尺寸 140 × 32。"""
        w, h = 140.0, 32.0
        x0 = x1 - w
        ax = self.ax
        ax.add_patch(Polygon([(x0, y0), (x1, y0), (x1, y0 + h), (x0, y0 + h)], closed=True, fill=False, lw=LW["thick"] * 1.3, ec=INK))
        for yy in (8, 16, 24):
            self.raw_line((x0, y0 + yy), (x0 + 75 if yy != 16 else x1, y0 + yy))
        for xx in (15, 45, 60, 75):
            self.raw_line((x0 + xx, y0), (x0 + xx, y0 + (32 if xx != 75 else 32)))
        self.raw_line((x0 + 105, y0 + 16), (x0 + 105, y0 + 32))
        self.raw_line((x0 + 75, y0 + 24), (x1, y0 + 24))
        s = FS * 0.95
        cells = [((x0 + 7.5, y0 + 28), T("名称", "Name")), ((x0 + 7.5, y0 + 20), T("材料", "Matl.")), ((x0 + 7.5, y0 + 12), T("设计", "Drawn")),
                 ((x0 + 7.5, y0 + 4), T("审核", "Chkd.")), ((x0 + 52.5, y0 + 28), T("比例", "Scale")), ((x0 + 52.5, y0 + 20), T("数量", "Qty")),
                 ((x0 + 52.5, y0 + 12), T("日期", "Date")), ((x0 + 52.5, y0 + 4), T("版本", "Rev.")),
                 ((x0 + 90, y0 + 28), T("图号", "Dwg no.")), ((x0 + 90, y0 + 20), T("单位", "Org."))]
        for (cx, cy), t in cells:
            ax.text(cx, cy, t, fontsize=s, ha="center", va="center", color=MUTED)
        vals = [((x0 + 30, y0 + 28), rows.get("name", "")), ((x0 + 30, y0 + 20), rows.get("material", "")),
                ((x0 + 30, y0 + 12), rows.get("drawn", "")), ((x0 + 30, y0 + 4), rows.get("checked", "")),
                ((x0 + 67.5, y0 + 28), rows.get("scale", "")), ((x0 + 67.5, y0 + 20), rows.get("qty", "")),
                ((x0 + 67.5, y0 + 12), rows.get("date", "")), ((x0 + 67.5, y0 + 4), rows.get("rev", "")),
                ((x0 + 122.5, y0 + 28), rows.get("no", "")), ((x0 + 122.5, y0 + 20), rows.get("org", "")),
                ((x0 + 107.5, y0 + 8), rows.get("title", ""))]
        for (cx, cy), t in vals:
            ax.text(cx, cy, t, fontsize=s * (1.5 if (cx, cy) == (x0 + 107.5, y0 + 8) else 0.85), ha="center", va="center", color=INK,
                    weight="bold" if (cx, cy) == (x0 + 107.5, y0 + 8) else "normal")


def ball(sh, x, y, r):
    """滚动体：白底圆，盖住内外圈的剖面线（规定画法）"""
    from matplotlib.patches import Circle
    sh.ax.add_patch(Circle((x, y), r, fc="white", ec=INK, lw=LW["thick"], zorder=5))


def sa300_rows():
    """SA-300 输出轴组件 B 版的明细栏：数字工厂 BOM（现行版）+ 第 33 章 B 版的更改（联轴器键加长、新增套筒）。
    返回 [{no, code, qty, name: (中, 英), mat, std, chg}]，序号按装配图上的位置顺时针排。"""
    import re
    import _shaft as S
    kw = sh301_keyways()
    key_c = mdstd.key_for(30)
    L_kc = kw[1][1] - kw[1][0]

    def zh_en(s):
        tok = s.split()
        k = next((i for i, t in enumerate(tok) if i > 0 and re.fullmatch(r"[A-Za-z][a-z]+", t)), len(tok))
        return " ".join(tok[:k]), " ".join(tok[k:]) + (" " + tok[1] if k > 1 and re.search(r"\d", tok[1]) else "")

    rows = [{"code": c, "qty": q} for c, q in F.BOMS["SA-300"][1]]
    key_c_code = f"KEY-C{key_c['b']}x{key_c['h']}x{L_kc:g}"          # 外伸段开口键槽用 C 型（单圆头）平键
    for r in rows:
        if r["code"] == "KEY-8x7x36":
            r["old"], r["code"], r["chg"] = "KEY-8x7x36", key_c_code, T("改", "chg.")
    rows.append({"code": T("（新）", "(new)"), "qty": 1, "chg": T("新", "new"), "name": ("套筒", "Sleeve"), "mat": "Q235"})
    MAT = {"SH-301": T("40Cr 调质", "40Cr, Q&T"), "GR-302": T("40Cr 调质", "40Cr, Q&T"), "BRG-6207": "", "KEY": "45"}
    STD = {"BRG-6207": "GB/T 276", "KEY": "GB/T 1096"}
    for r in rows:
        c = r["code"]
        if "name" not in r:
            zh, en = zh_en((F.ITEMS.get(c) or F.ITEMS["KEY-8x7x36"])[0])
            if c.startswith("KEY-"):
                b_, h_, l_ = c[4:].split("x")
                zh, en = f"平键 {b_}×{h_}×{l_}", f"Parallel key {b_}×{h_}×{l_}"         # 如“平键 C8×7×63”
            r["name"] = (zh.replace("深沟球轴承 ", "轴承 "), en)
            r["mat"] = MAT.get(c, MAT["KEY"] if c.startswith("KEY") else "")
        r["std"] = STD.get(c, STD["KEY"] if c.startswith("KEY") else "")
    order = ["GR-302", "SH-301", key_c_code, "BRG-6207", "KEY-12x8x45"]
    rows.sort(key=lambda r: order.index(r["code"]) if r["code"] in order else 99)
    for i, r in enumerate(rows, 1):
        r["no"] = i
    return rows


def bbox(polys):
    xs = [x for p in polys for x, _ in p]
    ys = [y for p in polys for _, y in p]
    return min(xs), min(ys), max(xs), max(ys)
