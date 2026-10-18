# -*- coding: utf-8 -*-
"""平面件拓扑优化（第 14 轮 H6）：SIMP 方法（固体各向同性材料惩罚），按 Andreassen 等 2011《Efficient topology optimization in
MATLAB using 88 lines of code》的经典算法用 numpy / scipy 重写。目标：给定材料用量（体积比）下刚度最大（柔度最小）。

单元：平面应力四节点正方形单元，网格 nelx × nely；材料插值 E = Emin + x^p (E0 − Emin)；灵敏度过滤（半径 rmin）；
更新：最优准则法（OC），每步变化不超过 0.2。结果：每个单元的密度 0–1（1 = 有材料），柔度随迭代的变化，以及按密度 0.5 取轮廓
拉伸成板件的 STEP（可以送“仿真与分析”校核）。"""
import math

import numpy as np

PRESETS = {
    "mbb": {"label": "MBB 梁（简支梁的一半，经典算例）", "nelx": 60, "nely": 20,
            "note": "左边是对称面（只限制水平），右下角滚动支座，左上角向下的力"},
    "cantilever": {"label": "悬臂梁（左边固定，右端中点向下的力）", "nelx": 64, "nely": 32, "note": "机械臂连杆、支架"},
    "bridge": {"label": "桥 / 简支梁（两端支承，下边中点向下的力）", "nelx": 80, "nely": 30, "note": "看材料怎么长成拱"},
    "bracket": {"label": "支架（左边固定，右下角向下的力）", "nelx": 60, "nely": 40, "note": "常见的电机、轴承座支架"},
}
MAX_ELEMENTS = 6000


def _ke(nu=0.3):
    k = np.array([1 / 2 - nu / 6, 1 / 8 + nu / 8, -1 / 4 - nu / 12, -1 / 8 + 3 * nu / 8,
                  -1 / 4 + nu / 12, -1 / 8 - nu / 8, nu / 6, 1 / 8 - 3 * nu / 8])
    return 1 / (1 - nu ** 2) * np.array([
        [k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7]],
        [k[1], k[0], k[7], k[6], k[5], k[4], k[3], k[2]],
        [k[2], k[7], k[0], k[5], k[6], k[3], k[4], k[1]],
        [k[3], k[6], k[5], k[0], k[7], k[2], k[1], k[4]],
        [k[4], k[5], k[6], k[7], k[0], k[1], k[2], k[3]],
        [k[5], k[4], k[3], k[2], k[1], k[0], k[7], k[6]],
        [k[6], k[3], k[4], k[1], k[2], k[7], k[0], k[5]],
        [k[7], k[2], k[1], k[4], k[3], k[6], k[5], k[0]]])


def _bc(preset, nelx, nely):
    """节点编号：列优先，节点 (i, j)（i 向右 0..nelx，j 向下 0..nely）号 = i·(nely+1) + j；自由度 2n（x）、2n+1（y）"""
    n = lambda i, j: i * (nely + 1) + j  # noqa: E731
    ndof = 2 * (nelx + 1) * (nely + 1)
    F = np.zeros(ndof)
    if preset == "mbb":
        fixed = [2 * n(0, j) for j in range(nely + 1)] + [2 * n(nelx, nely) + 1]
        F[2 * n(0, 0) + 1] = -1
    elif preset == "cantilever":
        fixed = [d for j in range(nely + 1) for d in (2 * n(0, j), 2 * n(0, j) + 1)]
        F[2 * n(nelx, nely // 2) + 1] = -1
    elif preset == "bridge":
        fixed = [2 * n(0, nely), 2 * n(0, nely) + 1, 2 * n(nelx, nely) + 1]
        F[2 * n(nelx // 2, nely) + 1] = -1
    elif preset == "bracket":
        fixed = [d for j in range(nely + 1) for d in (2 * n(0, j), 2 * n(0, j) + 1)]
        F[2 * n(nelx, nely) + 1] = -1
    else:
        raise ValueError("不认识的算例 {}".format(preset))
    return np.array(sorted(set(fixed))), F


def run(preset="mbb", nelx=None, nely=None, volfrac=0.5, penal=3.0, rmin=1.5, max_iter=200, tol=0.01, frames=24):
    if preset not in PRESETS:
        raise ValueError("不认识的算例 {}".format(preset))
    nelx = int(nelx or PRESETS[preset]["nelx"])
    nely = int(nely or PRESETS[preset]["nely"])
    if nelx * nely > MAX_ELEMENTS or nelx < 8 or nely < 4:
        raise ValueError("网格 {}×{} 不合适：单元数在 32–{} 之间".format(nelx, nely, MAX_ELEMENTS))
    if not 0.1 <= volfrac <= 0.9:
        raise ValueError("材料用量（体积比）要在 0.1–0.9 之间")
    fixed, F = _bc(preset, nelx, nely)
    r = _solve(nelx, nely, fixed, F, volfrac, penal, rmin, max_iter, tol, frames)
    return dict(r, preset=preset, label=PRESETS[preset]["label"])


def _solve(nelx, nely, fixed, F, volfrac, penal, rmin, max_iter=200, tol=0.01, frames=24, solid=None, void=None):
    """SIMP 主循环。solid / void：单元布尔数组（按 el = ely + elx·nely 编号），始终有材料 / 始终没材料；体积比只按其余单元算"""
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import spsolve
    Emin, E0 = 1e-9, 1.0
    KE = _ke()
    nel = nelx * nely
    ndof = 2 * (nelx + 1) * (nely + 1)
    edof = np.zeros((nel, 8), dtype=int)
    for elx in range(nelx):
        for ely in range(nely):
            el = ely + elx * nely
            n1 = (nely + 1) * elx + ely
            n2 = (nely + 1) * (elx + 1) + ely
            edof[el] = [2 * n1 + 2, 2 * n1 + 3, 2 * n2 + 2, 2 * n2 + 3, 2 * n2, 2 * n2 + 1, 2 * n1, 2 * n1 + 1]
    iK = np.kron(edof, np.ones((8, 1), dtype=int)).ravel()
    jK = np.kron(edof, np.ones((1, 8), dtype=int)).ravel()
    # 灵敏度过滤矩阵
    rr = int(math.ceil(rmin)) - 1
    ih, jh, sh = [], [], []
    for i1 in range(nelx):
        for j1 in range(nely):
            e1 = i1 * nely + j1
            for i2 in range(max(i1 - rr, 0), min(i1 + rr + 1, nelx)):
                for j2 in range(max(j1 - rr, 0), min(j1 + rr + 1, nely)):
                    e2 = i2 * nely + j2
                    ih.append(e1)
                    jh.append(e2)
                    sh.append(max(0.0, rmin - math.hypot(i1 - i2, j1 - j2)))
    Hf = coo_matrix((sh, (ih, jh)), shape=(nel, nel)).tocsc()
    Hs = np.asarray(Hf.sum(1)).ravel()
    free = np.setdiff1d(np.arange(ndof), fixed)
    solid = np.zeros(nel, bool) if solid is None else np.asarray(solid, bool)
    void = np.zeros(nel, bool) if void is None else (np.asarray(void, bool) & ~solid)
    act = ~(solid | void)
    if not act.any():
        raise ValueError("没有可以优化的区域")
    x = np.full(nel, volfrac)
    x[solid], x[void] = 1.0, 0.0
    hist, snaps = [], []
    change, it = 1.0, 0
    U = np.zeros(ndof)
    while change > tol and it < max_iter:
        it += 1
        sK = (KE.ravel()[None, :] * (Emin + x ** penal * (E0 - Emin))[:, None]).ravel()
        K = coo_matrix((sK, (iK, jK)), shape=(ndof, ndof)).tocsc()
        K = (K + K.T) / 2
        U[:] = 0
        U[free] = spsolve(K[free][:, free], F[free])
        ue = U[edof]
        ce = np.einsum("ij,jk,ik->i", ue, KE, ue)
        c = float(((Emin + x ** penal * (E0 - Emin)) * ce).sum())
        dc = -penal * x ** (penal - 1) * (E0 - Emin) * ce
        dc = np.asarray(Hf @ (x * dc)).ravel() / Hs / np.maximum(1e-3, x)
        # 最优准则法（二分找拉格朗日乘子）
        l1, l2, move = 0.0, 1e9, 0.2
        while (l2 - l1) / (l1 + l2) > 1e-3:
            lm = (l1 + l2) / 2
            xn = np.clip(x * np.sqrt(np.maximum(-dc, 0) / lm), np.maximum(0, x - move), np.minimum(1, x + move))
            xn[solid], xn[void] = 1.0, 0.0
            if xn[act].mean() > volfrac:
                l1 = lm
            else:
                l2 = lm
        change = float(np.abs(xn - x).max())
        x = xn
        hist.append([it, round(c, 4), round(float(x[act].mean()), 4), round(change, 4)])
        snaps.append(x.copy())
    pick = sorted(set(np.linspace(0, len(snaps) - 1, min(frames, len(snaps))).round().astype(int)))
    grey = float(((x[act] > 0.1) & (x[act] < 0.9)).mean())
    return {"nelx": nelx, "nely": nely, "volfrac": volfrac, "penal": penal,
            "rmin": rmin, "iterations": it, "converged": change <= tol, "compliance": hist[-1][1], "history": hist, "grey": round(grey, 4),
            "density": x.reshape(nelx, nely).T.round(4).tolist(),          # [行（向下）][列（向右）]
            "frames": [{"it": int(k + 1), "density": (snaps[k].reshape(nelx, nely).T * 255).round().astype(np.uint8).tolist()} for k in pick]}


# ---------- 两孔平板（学习平台第 41 轮：设计软件的曲柄、连杆、摆杆减重） ----------
MAX_PLATE_ELEMENTS = 6000
MIN_CUT_R = 1.6                     # 减重孔最窄处的一半：最小立铣刀 Ø3 的半径再留 0.1 mm


def plate_spec(p):
    """检查并整理平板说明（单位 mm，y 向上，零件自己的平面坐标）：
    domain 设计区域（多边形，现在的零件外形）；solid 保留的实心圆 [x, y, r]（孔周围的毂、平衡块）；holes 孔 [x, y, r]；
    support 支承孔（[x, y, r]，孔里的节点全固定，相当于销轴）；load {at: [x, y, r], f: [fx, fy]}（N，均分到孔里的节点）；cell_mm 单元边长"""
    from shapely.geometry import Polygon
    dom = Polygon([tuple(map(float, q)) for q in p["domain"]])
    if not dom.is_valid or dom.area <= 0:
        raise ValueError("设计区域不是有效的多边形")
    c = float(p.get("cell_mm") or 0) or max(0.3, math.sqrt(dom.area / 4000))
    x0, y0, x1, y1 = dom.bounds
    nelx, nely = int(math.ceil((x1 - x0) / c)) + 2, int(math.ceil((y1 - y0) / c)) + 2
    if nelx * nely > MAX_PLATE_ELEMENTS:
        c *= math.sqrt(nelx * nely / MAX_PLATE_ELEMENTS) * 1.02
        nelx, nely = int(math.ceil((x1 - x0) / c)) + 2, int(math.ceil((y1 - y0) / c)) + 2
    circ = lambda q: [float(q[0]), float(q[1]), float(q[2])]  # noqa: E731
    out = {"domain": [list(map(float, q)) for q in dom.exterior.coords[:-1]], "cell_mm": round(c, 4), "origin": [x0 - c, y0 - c],
           "nelx": nelx, "nely": nely, "solid": [circ(q) for q in p.get("solid") or []], "holes": [circ(q) for q in p.get("holes") or []],
           "support": circ(p["support"]), "load": {"at": circ(p["load"]["at"]), "f": [float(p["load"]["f"][0]), float(p["load"]["f"][1])]},
           "thickness_mm": float(p.get("thickness_mm") or 6)}
    if not (out["load"]["f"][0] or out["load"]["f"][1]):
        raise ValueError("载荷是零")
    return out


def _plate_grid(ps):
    c, (x0, y0), nelx, nely = ps["cell_mm"], ps["origin"], ps["nelx"], ps["nely"]
    ex = x0 + (np.arange(nelx) + 0.5) * c                     # 单元中心
    ey = y0 + (nely - np.arange(nely) - 0.5) * c
    EX, EY = np.meshgrid(ex, ey, indexing="ij")               # [elx, ely] → el = ely + elx·nely 与 ravel() 一致
    nx_ = x0 + np.arange(nelx + 1) * c
    ny_ = y0 + (nely - np.arange(nely + 1)) * c
    NX, NY = np.meshgrid(nx_, ny_, indexing="ij")             # 节点 i·(nely+1) + j
    return EX.ravel(), EY.ravel(), NX.ravel(), NY.ravel()


def run_plate(spec, volfrac=0.5, penal=3.0, rmin=1.5, max_iter=200, tol=0.01, frames=24):
    from shapely import vectorized
    from shapely.geometry import Polygon
    ps = plate_spec(spec)
    if not 0.1 <= volfrac <= 0.9:
        raise ValueError("材料用量（体积比）要在 0.1–0.9 之间")
    nelx, nely, c = ps["nelx"], ps["nely"], ps["cell_mm"]
    EX, EY, NX, NY = _plate_grid(ps)
    inside = vectorized.contains(Polygon(ps["domain"]).buffer(c * 0.3), EX, EY)
    solid = np.zeros(EX.size, bool)
    for x, y, r in ps["solid"] + ps["holes"] + [ps["support"], ps["load"]["at"]]:
        solid |= np.hypot(EX - x, EY - y) <= r + 0.5 * c        # 毂、孔（当作销轴）一直实心
    void = ~inside & ~solid
    ndof = 2 * (nelx + 1) * (nely + 1)
    sx, sy, sr = ps["support"]
    fix_n = np.nonzero(np.hypot(NX - sx, NY - sy) <= sr + 1e-9)[0]
    lx, ly, lr = ps["load"]["at"]
    ld_n = np.nonzero(np.hypot(NX - lx, NY - ly) <= lr + 1e-9)[0]
    if len(fix_n) < 2 or len(ld_n) < 1:
        raise ValueError("单元太粗，孔里落不下节点（单元边长 {:.2f} mm）".format(c))
    fixed = np.sort(np.concatenate([2 * fix_n, 2 * fix_n + 1]))
    F = np.zeros(ndof)
    F[2 * ld_n] = ps["load"]["f"][0] / len(ld_n)
    F[2 * ld_n + 1] = ps["load"]["f"][1] / len(ld_n)
    r = _solve(nelx, nely, fixed, F, volfrac, penal, rmin, max_iter, tol, frames, solid=solid, void=void)
    keep = (np.asarray(r["density"]).T.ravel() >= 0.5) & inside
    r.update(preset="plate", label="两孔平板减重", plate=ps,
             mass_ratio=round(float(keep.sum() / max(1, (inside | solid).sum())), 4))
    return r


def plate_polygon(ps, density, holes=True):
    """平板结果 → 零件轮廓（mm，零件平面坐标）：密度 ≥ 0.5 的单元 ∪ 保留的实心圆，裁到设计区域里，再挖掉孔（holes=False 时不挖）"""
    from shapely.geometry import Point, Polygon
    from shapely.ops import unary_union
    c = ps["cell_mm"]
    g = to_polygon(density, c)
    from shapely import affinity
    g = affinity.translate(g, ps["origin"][0], ps["origin"][1])
    keep = [Point(x, y).buffer(r, 64) for x, y, r in ps["solid"]]
    dom = Polygon(ps["domain"])
    # 圆顺网格台阶：先闭（补小缺口）再开（去小毛刺），各一格多，然后按半格简化——轮廓点少，图纸和数控刀路都干净
    g = g.buffer(c * 1.2).buffer(-c * 2.4).buffer(c * 1.2)
    g = unary_union([g] + keep).intersection(dom.buffer(1e-6))
    parts = sorted(getattr(g, "geoms", [g]), key=lambda q: -q.area)
    g = parts[0]                                               # 只要和孔连着的那一大块
    # 减重孔太窄、最小立铣刀（Ø3）放不进的填回去：做不出来的孔没有用，填回去只是多一点质量
    keep_in = [h for h in g.interiors if Polygon(h).buffer(-MIN_CUT_R).area > 0]
    g = Polygon(g.exterior, keep_in)
    if holes:
        for x, y, r in ps["holes"]:
            g = g.difference(Point(x, y).buffer(r, 64))
    return g.simplify(c * 0.5)


def plate_step(ps, density):
    """STEP 里的孔是真正的圆柱面（有限元按圆柱面找支承孔、受力孔，数控按圆柱面认钻孔）；板厚沿 z 从 −t 到 0（上表面在 Z0，
    数控的工件零点）；返回 (STEP, 带孔的轮廓)"""
    import build123d as bd
    from cae.thermal_parts import tempfile_step
    g0 = plate_polygon(ps, density, holes=False)
    t = ps["thickness_mm"]
    face = bd.Face(bd.Wire.make_polygon([bd.Vector(x, y, 0) for x, y in list(g0.exterior.coords)[:-1]], close=True),
                   [bd.Wire.make_polygon([bd.Vector(x, y, 0) for x, y in list(h.coords)[:-1]], close=True) for h in g0.interiors])
    shape = bd.Pos(0, 0, -t) * bd.extrude(face, t)
    for x, y, r in ps["holes"]:
        shape = shape - bd.Pos(x, y, -t / 2) * bd.Cylinder(r, t * 2)
    return tempfile_step(shape), plate_polygon(ps, density)


def layout(preset, density, length_mm):
    """做有限元校核用的平面布置（mm，y 向上，原点在左下角）：MBB 梁按对称面镜像成整根简支梁；支承和载荷处各加一小块“垫块”，
    这样约束、载荷落在一个独立的面上，不会出现一个点上的奇异应力。返回 (密度, 单元边长, 垫块列表, 说明)"""
    d = np.asarray(density, float)
    if preset == "mbb":
        d = np.hstack([d[:, ::-1], d])
    ny, nx = d.shape
    c = float(length_mm) / nx
    W, H = nx * c, ny * c
    a, t = 3 * c, 1.5 * c                     # 垫块：沿边 3 格长、1.5 格厚
    pads = []

    def pad(role, side, x, y):              # 垫块向零件里多伸一格，保证和零件连成一体
        if side == "top":
            r, f = (x - a / 2, H - c, x + a / 2, H + t), (x, H + t, 0, 1)
        elif side == "bottom":
            r, f = (max(0.0, x - a / 2), -t, min(W, x + a / 2), c), (x, -t, 0, -1)
        else:                                  # right
            r, f = (W - c, max(0.0, y - a / 2), W + t, y + a / 2), (W + t, y, 1, 0)
        pads.append({"role": role, "rect": list(r), "face": f})
    if preset in ("mbb", "bridge"):
        pad("support", "bottom", a / 2, 0)
        pad("support", "bottom", W - a / 2, 0)
        pad("load", "top" if preset == "mbb" else "bottom", W / 2, 0)
        note = ("两端支座下的垫块底面按“固定”（比真正的简支——一端可以水平滑动——略刚一点，下弦拉力会小一些）；"
                + ("MBB 梁是简支梁的一半，这里已按对称面镜像成整根梁，载荷加在梁顶中间的垫块上" if preset == "mbb" else "载荷加在下边中间的垫块上"))
    else:
        y = H / 2 if preset == "cantilever" else a / 2
        pad("load", "right", 0, y)
        note = "左边整个端面固定；载荷加在{}的垫块上".format("右端中间" if preset == "cantilever" else "右下角")
    return d, c, pads, note


def fea_part(preset, density, length_mm, thickness_mm):
    """拓扑结果 → 带垫块的板件 STEP，外加垫块外表面的位置（读入后按位置找面号）"""
    from shapely.geometry import box
    d, c, pads, note = layout(preset, density, length_mm)
    g = to_polygon(d, c)
    for p in pads:
        g = g.union(box(*p["rect"]))
    step = _extrude(g, thickness_mm)
    return step, pads, note, {"area_mm2": round(g.area, 1), "volume_mm3": round(g.area * thickness_mm, 1),
                              "width_mm": round(d.shape[1] * c, 1), "height_mm": round(d.shape[0] * c, 1), "cell_mm": round(c, 3)}


def fea_rows(preset, pads, faces, force_n):
    """按位置找垫块的外表面和（悬臂、支架）左端面，排成“仿真与分析”的约束 / 载荷行"""
    def at(px, py, nx_, ny_):
        out = []
        for f in faces:
            n = f.get("normal") or [0, 0, 0]
            if f["kind"] != "plane" or abs(n[0] - nx_) > 1e-3 or abs(n[1] - ny_) > 1e-3:
                continue
            b = f["bbox"]
            if b[0] - 1e-3 <= px <= b[3] + 1e-3 and b[1] - 1e-3 <= py <= b[4] + 1e-3:
                out.append(f["id"])
        return out
    rows = []
    if preset in ("cantilever", "bracket"):
        left = [f["id"] for f in faces if f["kind"] == "plane" and (f.get("normal") or [0])[0] < -0.999 and abs(f["bbox"][0]) < 1e-3]
        rows.append({"kind": "fixed", "faces": left})
    for p in pads:
        fx, fy, nx_, ny_ = p["face"]
        ids = at(fx, fy, nx_, ny_)
        if not ids:
            raise ValueError("没找到垫块的面")
        rows.append({"kind": "fixed", "faces": ids} if p["role"] == "support" else
                    {"kind": "force", "faces": ids, "fx": 0, "fy": -float(force_n), "fz": 0})
    return rows


def to_polygon(density, cell_mm, threshold=0.5):
    """密度 ≥ 0.5 的单元合成多边形（mm，y 向上），去掉很小的碎块"""
    from shapely.geometry import box
    from shapely.ops import unary_union
    d = np.asarray(density)
    ny, nx = d.shape
    cells = [box(i * cell_mm, (ny - 1 - j) * cell_mm, (i + 1) * cell_mm, (ny - j) * cell_mm)
             for j in range(ny) for i in range(nx) if d[j, i] >= threshold]
    g = unary_union(cells).buffer(cell_mm * 0.01).buffer(-cell_mm * 0.01)
    parts = [p for p in getattr(g, "geoms", [g]) if p.area >= 4 * cell_mm * cell_mm]
    return unary_union(parts).simplify(cell_mm * 0.05)


def _extrude(g, thickness_mm):
    import build123d as bd
    from cae.thermal_parts import tempfile_step
    solids = []
    for p in getattr(g, "geoms", [g]):
        if p.is_empty:
            continue
        face = bd.Face(bd.Wire.make_polygon([bd.Vector(x, y, 0) for x, y in list(p.exterior.coords)[:-1]], close=True),
                       [bd.Wire.make_polygon([bd.Vector(x, y, 0) for x, y in list(h.coords)[:-1]], close=True) for h in p.interiors])
        solids.append(bd.extrude(face, thickness_mm))
    if not solids:
        raise ValueError("没有剩下材料")
    shape = solids[0]
    for s in solids[1:]:
        shape = shape + s
    return tempfile_step(shape)
