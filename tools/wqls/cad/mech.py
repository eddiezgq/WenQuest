"""WQ-LS 刺布与挑线机构零件（第 138 轮 G4.1），在 FreeCAD 里运行：

    WQ_OUT=<目录> freecadcmd -c "exec(open('tools/wqls/cad/mech.py').read())"

零件都按 φ = 0（针杆上止点）的位置画在整机坐标里（与 spec.py 相同：原点在针板上表面、机针中心线上；X 向右、Y 向后、Z 向上，mm）。
机构是平面的，端视坐标 u = −Y（向前为正）、v = Z − ZU（上轴中心为 0）。
沿 X 的排布（从面板往里）：针杆 x = 0 → 针杆连杆 x 6–12（摇杆也在这个平面）→ 挑线杆 x 13.5–18.5 → 曲柄（带平衡块）x 20–30 → 前轴承 6202 x 32–43。
挑线杆和针杆连杆套在同一根曲柄销上（真机做法，四连杆由 tools/wqls/g4_takeup.py 综合，结果在 docs/设计/WQ-LS/G4/挑线机构.json）。
平衡块的大小在这里按平衡率 k（spec.SEW["k"]）算出：曲柄连同平衡块的质心矩 = 全部回转质量 × r + k × 往复质量 × r。

输出：<目录>/<零件>.step、<零件>.stl，<目录>/parts.json（每个零件的质量、质心、绕质心的惯量、所在平面）。
"""
import json
import math
import os
import sys

import FreeCAD as App
import MeshPart
import Part

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.path.join(os.getcwd(), "tools", "wqls", "cad")
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "tools", "wqls")]
import spec as S  # noqa: E402

OUT = os.environ.get("WQ_OUT", "/tmp/wqls_mech")
os.makedirs(OUT, exist_ok=True)
TK = json.load(open(os.path.join(ROOT, "docs", "设计", "WQ-LS", "G4", "挑线机构.json")))["lk"]
RHO_STEEL = 7.85e-6          # kg/mm³
ZU, R, L = S.ZU, S.SEW["r"], S.SEW["l"]
DEG = math.pi / 180
X = S.MECH_X


def W(u, v):
    """端视坐标 → 整机坐标（只给 Y、Z）"""
    return -u, ZU + v


def disc(u, v, rad, x0, t):
    y, z = W(u, v)
    return Part.makeCylinder(rad, t, V(x0, y, z), V(1, 0, 0))


def link2(c1, r1, c2, r2, x0, t):
    """两圆的外公切线包络（杆件的轮廓），c 为端视坐标"""
    (u1, v1), (u2, v2) = c1, c2
    d = math.hypot(u2 - u1, v2 - v1)
    th = math.atan2(v2 - v1, u2 - u1)
    be = math.acos(max(-1.0, min(1.0, (r1 - r2) / d)))
    pts = []
    for s_ in (1, -1):
        a = th + s_ * be
        pts.append((u1 + r1 * math.cos(a), v1 + r1 * math.sin(a), u2 + r2 * math.cos(a), v2 + r2 * math.sin(a)))
    quad = [W(pts[0][0], pts[0][1]), W(pts[0][2], pts[0][3]), W(pts[1][2], pts[1][3]), W(pts[1][0], pts[1][1])]
    w = Part.makePolygon([V(x0, y, z) for y, z in quad] + [V(x0, quad[0][0], quad[0][1])])
    body = Part.Face(w).extrude(V(t, 0, 0))
    return body.fuse(disc(u1, v1, r1, x0, t)).fuse(disc(u2, v2, r2, x0, t)).removeSplitter()


def hole(u, v, rad, x0, t):
    return disc(u, v, rad, x0 - 1, t + 2)


def pocket(c1, r1, c2, r2, x0, t):
    return link2(c1, r1, c2, r2, x0, t)


def rounded(s, r):
    try:
        es = [e for e in s.Edges if e.BoundBox.YLength < 1e-6 and e.BoundBox.ZLength < 1e-6]   # 平行于 X 的棱（轮廓的角）
        s2 = s.makeFillet(r, es)
        return s2 if s2.isValid() else s
    except Exception:  # noqa: BLE001
        return s


def solid(s):
    """布尔运算有时返回 Compound：取出实体，多于一个就合成一个多实体的 Compound 再求质量特性"""
    if s.ShapeType == "Solid":
        return s
    sol = s.Solids
    if len(sol) == 1:
        return sol[0]
    return Part.makeCompound(sol)


def props(s):
    s = solid(s)
    if s.ShapeType == "Compound":
        vol = sum(x.Volume for x in s.Solids)
        cx = sum((x.CenterOfMass * x.Volume for x in s.Solids), V(0, 0, 0)) * (1 / vol)
        return dict(mass_kg=round(vol * RHO_STEEL, 5), com=[round(cx.x, 3), round(cx.y, 3), round(cx.z, 3)], solids=len(s.Solids))
    m = s.Volume * RHO_STEEL
    c = s.CenterOfMass
    I = s.MatrixOfInertia          # 单位密度、绕质心
    return dict(mass_kg=round(m, 5), com=[round(c.x, 3), round(c.y, 3), round(c.z, 3)],
                Ixx_kgmm2=round(I.A11 * RHO_STEEL, 4), Iyy_kgmm2=round(I.A22 * RHO_STEEL, 4), Izz_kgmm2=round(I.A33 * RHO_STEEL, 4))


# ---------------------------------------------------------------- φ = 0 的位置
PHI0 = 0.0
C0 = (0.0, R)                                  # 曲柄销（端视）
B0v = R - L                                    # 针杆连接销（端视 v）
NB_BOT0 = B0v - X["nb_below"]                  # 针杆下端
parts, mats = {}, {}

# 针杆：Ø8，从连接销往下 nb_below、往上 nb_above；下端装针夹
y, zb = W(0, NB_BOT0)
nb = Part.makeCylinder(4.0, X["nb_below"] + X["nb_above"], V(0, 0, zb), V(0, 0, 1))
nb = nb.makeChamfer(0.5, [e for e in nb.Edges])
parts["needle_bar"], mats["needle_bar"] = nb, "chrome"

# 针夹（套在针杆下端）和机针 DB×1：针尖到针杆下端 tip_below
# 针夹做短（针杆下端 −4…+4）：上止点时针夹顶只进到机头底孔里 0.5 mm；紧针螺钉在针夹中部朝前，线钩在下面
clamp = Part.makeCylinder(5.5, 8, V(0, 0, zb - 4), V(0, 0, 1)).cut(Part.makeCylinder(4.0, 10, V(0, 0, zb - 5), V(0, 0, 1)))
clamp = clamp.fuse(Part.makeCylinder(2.0, 4, V(0, -5, zb), V(0, -1, 0)))                                   # 紧针螺钉 M4
clamp = clamp.fuse(Part.makeBox(3, 3, 3.5, V(-1.5, -7.5, zb - 4)).cut(Part.makeCylinder(0.9, 5, V(-2, -6, zb - 2.2), V(1, 0, 0))))  # 针杆线钩
parts["needle_clamp"], mats["needle_clamp"] = clamp, "metal"
tip_z = zb - X["tip_below"]
shank = Part.makeCylinder(0.81, 10.0, V(0, 0, zb - 0.0), V(0, 0, 1))
blade = Part.makeCylinder(0.45, (zb - tip_z) - 2.0, V(0, 0, tip_z + 2.0), V(0, 0, 1))
taper = Part.makeCone(0.81, 0.45, 1.5, V(0, 0, zb - 1.5), V(0, 0, 1))
point = Part.makeCone(0.02, 0.45, 2.0, V(0, 0, tip_z), V(0, 0, 1))
eye = Part.makeBox(4, 0.5, 1.6, V(-2, -0.25, tip_z + 2.0 + 0.4))
needle = shank.fuse(blade).fuse(taper).fuse(point).cut(eye).removeSplitter()
parts["needle"], mats["needle"] = needle, "chrome"

# 针杆连接块（夹在针杆上）+ 连接销（伸到连杆小头）
yB, zB = W(0, B0v)
blk = Part.makeBox(12, 14, 16, V(-6, -7, zB - 8)).cut(Part.makeCylinder(4.0, 20, V(0, 0, zB - 10), V(0, 0, 1)))
blk = rounded(blk, 1.5) if False else blk
blk = blk.fuse(Part.makeCylinder(3.0, X["rod"][1] - 6 + 1.5, V(6, 0, zB), V(1, 0, 0)))
blk = blk.fuse(Part.makeCylinder(2.5, 8, V(0, 4, zB), V(0, 1, 0)).cut(Part.makeCylinder(4.0, 20, V(0, 0, zB - 10), V(0, 0, 1))))  # 夹紧螺钉
parts["nb_link"], mats["nb_link"] = blk, "metal"

# 针杆连杆：大头 Ø22（内装 Ø8/Ø12 滚针轴承），小头 Ø13（Ø6 连接销），两面各挖 1.5 深的减重槽
x0, t = X["rod"][0], X["rod"][1] - X["rod"][0]
rod = link2(C0, 11.0, (0.0, B0v), 6.5, x0, t)
for xs in (x0 - 0.01, X["rod"][1] - 1.5):
    rod = rod.cut(pocket((0.0, C0[1] - 14.5), 3.2, (0.0, B0v + 9.5), 2.4, xs, 1.51))
rod = rod.cut(hole(*C0, 6.0, x0, t)).cut(hole(0.0, B0v, 3.0, x0, t))
parts["rod"], mats["rod"] = rod, "metal"

# 挑线杆：P 套在曲柄销上（Ø18 毂，内装滚针轴承），M 接摇杆（Ø12 毂、Ø5 销），向前伸出到线眼（Ø3 眼、末端倒圆）
import importlib.util  # noqa: E402

spec_ = importlib.util.spec_from_file_location("tk", os.path.join(ROOT, "tools", "wqls", "g4_takeup.py"))
tkm = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(tkm)
MK = tkm.Mech2(r=R, l=L, mr=S.SEW["mr"], lk=TK)
p0 = MK.link_pose(PHI0, MK.LK0)
Pp, Mp, Ep, Qp = (tuple(p0[k]) for k in ("P", "M", "E", "Q"))
x0, t = X["lever"]
# G4.2 减重：杆身改 3 mm 钢板（居中），只在 P、M 两个毂处保留 5 mm；杆身收窄（真机挑线杆 15–25 g）
tp = 3.0
xp = x0 + (t - tp) / 2
lever = disc(*Pp, 9.0, x0, t).fuse(disc(*Mp, 5.5, x0, t))
lever = lever.fuse(link2(Pp, 6.5, Mp, 4.5, xp, tp)).fuse(link2(Pp, 5.5, Ep, 3.0, xp, tp)).removeSplitter()
lever = lever.cut(hole(*Pp, 6.0, x0, t)).cut(hole(*Mp, 2.5, x0, t)).cut(hole(*Ep, 1.5, x0, t))
parts["lever"], mats["lever"] = lever, "chrome"

# 摇杆（挑线连杆）：M–Q，两端 Ø12 毂；Q 的销固定在机壳凸台上
x0, t = X["rocker_in"] if TK.get("side", "in") == "in" else X["rocker_out"]
rocker = link2(Mp, 6.0, Qp, 6.0, x0, t).cut(hole(*Mp, 2.5, x0, t)).cut(hole(*Qp, 3.0, x0, t))
parts["rocker"], mats["rocker"] = rocker, "metal"
xs0 = min(X["lever"][0], x0) - 0.5
xs1 = max(X["lever"][0] + X["lever"][1], x0 + t) + 0.5
parts["pin_M"], mats["pin_M"] = disc(*Mp, 2.5, xs0, xs1 - xs0), "chrome"
if TK.get("side", "in") == "in":            # 摇杆在内侧：销从轴承隔板上的销座伸出来
    parts["stud_Q"], mats["stud_Q"] = disc(*Qp, 3.0, x0 - 0.5, 32.0 - (x0 - 0.5)), "chrome"
else:                                        # 摇杆在外侧：销从机头顶上吊下来的销座（x −10…5）伸出来
    parts["stud_Q"], mats["stud_Q"] = disc(*Qp, 3.0, -10.0, x0 + t + 0.5 + 10.0), "chrome"

# 曲柄销 Ø8：从曲柄面穿过挑线杆、连杆
pin_x0 = X["rod"][0] - 0.5
parts["crank_pin"], mats["crank_pin"] = disc(*C0, 4.0, pin_x0, X["web"][0] - pin_x0 + 4), "chrome"

# 上轴（C 版轴段）
shaft = None
for a, b, d, _n in S.UPPER_SEGS:
    c_ = Part.makeCylinder(d / 2, b - a, V(a, 0, ZU), V(1, 0, 0))
    shaft = c_ if shaft is None else shaft.fuse(c_)
shaft = shaft.removeSplitter()
parts["shaft"], mats["shaft"] = shaft, "metal"

# 前轴承 6202（15 × 35 × 11）
xb = S.X_BRG[0]
brg = Part.makeCylinder(17.5, 11, V(xb - 5.5, 0, ZU), V(1, 0, 0)).cut(Part.makeCylinder(7.5, 13, V(xb - 6.5, 0, ZU), V(1, 0, 0)))
brg = brg.cut(Part.makeCylinder(14.6, 1.2, V(xb - 6.1, 0, ZU), V(1, 0, 0)).cut(Part.makeCylinder(10.2, 2, V(xb - 6.5, 0, ZU), V(1, 0, 0))))
parts["bearing_front"], mats["bearing_front"] = brg, "metal"


# 曲柄（带平衡块）：毂 Ø30 夹在轴端，销座 Ø20；平衡块是销对面的一块扇形，半径 R_CW，张角由平衡要求定
def crank(half_deg):
    x0, x1 = X["web"]
    t = x1 - x0
    hub = disc(0, 0, 16.5, x0, t)
    boss = link2((0, 0), 16.5, C0, 10.0, x0, t)
    # 扇形：圆心在轴心，半径 R_CW，方向朝下（销在上），张角 ±half
    pts = [(0.0, 0.0)]
    for i in range(41):
        a = -math.pi / 2 + (i / 40 - 0.5) * 2 * half_deg * DEG
        pts.append((X["R_cw"] * math.cos(a), X["R_cw"] * math.sin(a)))
    w = Part.makePolygon([V(x0, *W(u, v)) for u, v in pts] + [V(x0, *W(*pts[0]))])
    sec = Part.Face(w).extrude(V(t, 0, 0))
    body = hub.fuse(boss).fuse(sec).removeSplitter()
    body = rounded(body, 3.0)
    body = body.cut(Part.makeCylinder(7.5, t + 2, V(x0 - 1, 0, ZU), V(1, 0, 0)))          # 轴孔 Ø15
    body = body.cut(hole(*C0, 4.0, x0, t))                                                 # 销孔 Ø8 压配
    body = body.cut(Part.makeCylinder(2.5, 16, V((x0 + x1) / 2, 0, ZU - 17), V(0, 0, 1)))  # 紧定螺钉 M5 ×2
    body = body.cut(Part.makeCylinder(2.5, 16, V((x0 + x1) / 2, -17 * math.sin(60 * DEG), ZU - 17 * math.cos(60 * DEG)),
                                      V(0, math.sin(60 * DEG), math.cos(60 * DEG))))
    return body


def moment_about_axis(s):
    """质心矩在端视 v 方向（kg·mm），+ = 销那边"""
    s = solid(s)
    c = s.CenterOfMass
    return s.Volume * RHO_STEEL * (c.z - ZU), s.Volume * RHO_STEEL * (-c.y)


# 平衡要求：曲柄组件对轴心的质心矩 M_req（kg·mm，指向销的反方向）
pr = {k: props(v) for k, v in parts.items()}
m_rod = pr["rod"]["mass_kg"]
# 连杆质心离曲柄销的距离（沿杆）→ 两质量等效：销处回转 m_rod(1 − g/l)、往复 m_rod·g/l
g_rod = abs(pr["rod"]["com"][2] - (ZU + C0[1]))
m_rod_rot, m_rod_rec = m_rod * (1 - g_rod / L), m_rod * g_rod / L
m_recip = sum(pr[k]["mass_kg"] for k in ("needle_bar", "needle_clamp", "needle", "nb_link")) + m_rod_rec
m_rot = m_rod_rot + pr["crank_pin"]["mass_kg"] + 0.010     # 销上两只滚针轴承约 10 g（挑线杆的惯性力由 dyn.py 按真实运动算，平衡率 k 已经把它算进去）
K = S.SEW["k"]
M_req = (m_rot + K * m_recip) * R                    # 平衡块要提供的矩（kg·mm），方向与销相反
lo, hi = 10.0, 89.0
for _ in range(30):
    mid = (lo + hi) / 2
    mv, _mu = moment_about_axis(crank(mid))
    if -mv < M_req:
        lo = mid
    else:
        hi = mid
cr = crank(hi)
mv, mu_ = moment_about_axis(cr)
parts["crank"], mats["crank"] = cr, "metal"
bal = dict(k=K, m_recip_kg=round(m_recip, 4), m_rot_kg=round(m_rot, 4), g_rod_mm=round(g_rod, 2), M_req_kgmm=round(M_req, 3),
           crank_moment_kgmm=round(-mv, 3), sector_half_deg=round(hi, 2), equiv_at_r_g=round(1000 * (-mv) / R, 1))

out = dict(lk=TK, x=X, balance=bal, parts={})
for k, s in parts.items():
    s.exportStep(os.path.join(OUT, f"{k}.step"))
    mesh = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.2)
    mesh.write(os.path.join(OUT, f"{k}.stl"))
    out["parts"][k] = dict(material=mats[k], valid=s.isValid(), **props(s))
json.dump(out, open(os.path.join(OUT, "parts.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(dict(balance=bal, mass={k: v["mass_kg"] for k, v in out["parts"].items()}), ensure_ascii=False))
