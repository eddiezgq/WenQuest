"""WQ-LS G8.0 第 7 步：润滑油路（第 10 项）。

油泵（G4.6，feed.py）→ Ø4 × 1 铜管上立柱 → 机臂顶分油块（顶盖下面，顶盖上有透明观油窗）
    ├─ 中间含油轴套：油芯穿过机臂顶 Ø3 孔（中间横隔板里）压在轴套外圆上
    ├─ Ø2 尼龙管顺机臂内顶到机头油毡盒（从机头顶外面用两个 SM 螺钉吊住）
    │     ├─ 油芯铜管 W1 → 上导套座顶上的油毡杯（油毡贴着针杆，针杆把油带进上导套）
    │     ├─ 油芯铜管 W2 → 下导套座顶上的油毡杯（同上，下导套）
    │     └─ 油毡头 W3 → 滴在曲柄销、连杆和挑线杆毂上（曲柄转起来把油甩到滚针和滑块导轨上）
    └─ 溢流：Ø4 铜管回到机座，滴回油盘
上轴前、后轴承改用 2RS 终身润滑脂，不送油。

坐标同 mech.py（x 沿上轴，z 向上，针杆轴线 x = y = 0）。housing.py 用 HSG 里的数在机壳上做孔和座。
"""
import Part
from FreeCAD import Vector as V

import importlib.util as _iu
import os as _os

_sp = _iu.spec_from_file_location("wq_oil_geo", _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "oil_geo.py"))
_g = _iu.module_from_spec(_sp)
_sp.loader.exec_module(_g)
BLOCK, WICK_MID, RES, CUP_UP, CUP_LOW = _g.BLOCK, _g.WICK_MID, _g.RES, _g.CUP_UP, _g.CUP_LOW
RISER, RETURN, LINE_HEAD, W1, W2 = _g.RISER, _g.RETURN, _g.LINE_HEAD, _g.W1, _g.W2
R_CU, R_RET, R_NY, R_W, HEAD_TOP, PASS = _g.R_CU, _g.R_RET, _g.R_NY, _g.R_W, _g.HEAD_TOP, _g.PASS


def pipe(pts, r):
    s = None
    for a, b in zip(pts[:-1], pts[1:]):
        a, b = V(*a), V(*b)
        d = b - a
        c = Part.makeCylinder(r, d.Length, a, d)
        s = c if s is None else s.fuse(c)
    for p in pts[1:-1]:
        s = s.fuse(Part.makeSphere(r, V(*p)))
    return s.removeSplitter()


def box(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cup(c):
    ring = Part.makeCylinder(c["r_out"], c["h"], V(0, 0, c["z"])).cut(Part.makeCylinder(c["r_in"], c["h"] + 2, V(0, 0, c["z"] - 1)))
    return ring.common(Part.makeBox(40, 40, c["h"] + 2, V(-3.5, -20, c["z"] - 1)))


def build():
    P = {}
    blk = box(BLOCK["x"], BLOCK["y"], BLOCK["z"])
    for x_, y_ in BLOCK["screws"]:                                           # M4 通孔 Ø4.5、沉孔 Ø8 × 4.5
        blk = blk.cut(Part.makeCylinder(2.25, 10, V(x_, y_, 251), V(0, 0, 1))).cut(Part.makeCylinder(4.0, 5, V(x_, y_, 255.5), V(0, 0, 1)))
    P["oil_block"] = (blk, "metal", "alu", None)
    P["oil_tubes"] = (pipe(RISER, R_CU).fuse(pipe(RETURN, R_RET)), "metal", "copper", None)
    P["oil_line"] = (pipe(LINE_HEAD, R_NY), "black", "nylon", None)
    res = box(RES["x"], RES["y"], RES["z"])
    scr = None
    for x_, y_ in RES["screws"]:                                             # SMP 9/64-40 × 12（Q/WQ 001），螺孔攻穿油毡盒
        res = res.cut(Part.makeCylinder(2.95 / 2, 10, V(x_, y_, RES["z"][0] - 1), V(0, 0, 1)))
        s_ = Part.makeCylinder(3.5719 / 2, 12.0, V(x_, y_, HEAD_TOP - 12.0), V(0, 0, 1)).fuse(Part.makeCylinder(3.4, 2.1, V(x_, y_, HEAD_TOP)))
        scr = s_ if scr is None else scr.fuse(s_)
    for x_, y_ in BLOCK["screws"]:                                           # 内六角圆柱头螺钉 M4 × 10（GB/T 70.1），头沉在分油块里
        scr = scr.fuse(Part.makeCylinder(2.0, 10.0, V(x_, y_, 245.5), V(0, 0, 1)).fuse(Part.makeCylinder(3.5, 4.0, V(x_, y_, 255.5))))
    P["oil_screws"] = (scr, "black", "steel", None)
    P["oil_box"] = (res, "metal", "alu", None)
    wk = pipe(W1, R_W).fuse(pipe(W2, R_W))
    mid = Part.makeCylinder(1.4, BLOCK["z"][0] - WICK_MID[2], V(WICK_MID[0], WICK_MID[1], WICK_MID[2]), V(0, 0, 1))
    tip = Part.makeBox(6, 4, 3, V(17.0, 16.0, RES["z"][0] - 3.0))           # 油毡头 W3（曲柄上方）
    P["oil_wicks"] = (wk.fuse(mid).fuse(tip), "black", "felt", None)
    P["oil_cups"] = (cup(CUP_UP).fuse(cup(CUP_LOW)), "black", "felt", None)
    return P


RHO = dict(alu=2.75e-6, copper=8.9e-6, nylon=1.14e-6, felt=0.4e-6, steel=7.85e-6)
