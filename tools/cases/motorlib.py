"""第 161d 轮：电机类案例共用——集中绕组（齿绕）的槽电势星形图与绕组系数、二维静磁场有限元（Gmsh 网格 + scikit-fem 求解，线性铁心）。

二维静磁场：只算 z 向矢量磁位 A，∫ν∇A·∇v = ∫J v + ∫(M_x ∂v/∂y − M_y ∂v/∂x)，外圆 A = 0。磁钢按 μr ≈ 1 处理（钕铁硼回复磁导率约 1.05），
磁钢的磁化 M = Br/μ0 沿径向，N、S 交替；转子转动 = 磁化分布跟着转（磁钢环的几何不变，网格不用重划）。
铁心按线性材料（μr 常数）——空载、额定电流下铁心不饱和时可以这样近似；饱和要非线性迭代，案例里写明。
"""
from __future__ import annotations

import math

import numpy as np

MU0 = 4e-7 * math.pi


# ---------------------------------------------------------------- 绕组
def slot_star(Q, p):
    """槽电势星形图：第 k 槽（0 起）的导体电势相位 = k · p · 360/Q（电角度）"""
    return [(k, (k * p * 360.0 / Q) % 360.0) for k in range(Q)]


def tooth_winding(Q, p):
    """双层集中绕组（每齿一个线圈，线圈跨一个齿）：用槽电势星形图把 Q 个线圈分成 A、B、C 三相，返回 [(齿号, 相, 方向 ±1)]。
    线圈 k 的电势相位 = k·α（α = p·360/Q 电角度）；每个线圈归到最近的六个相轴之一（+A、−C、+B、−A、+C、−B，间隔 60°），
    整体转一个角度使三相线圈数相等、基波绕组系数最大。"""
    alpha = p * 360.0 / Q
    axes = [(0, "A", 1), (60, "C", -1), (120, "B", 1), (180, "A", -1), (240, "C", 1), (300, "B", -1)]
    best = None
    for off in np.arange(0, 60, 0.5):
        coils = []
        for k in range(Q):
            ph = (k * alpha + off) % 360
            ax = min(axes, key=lambda a_: abs(((ph - a_[0]) + 180) % 360 - 180))
            coils.append((k, ax[1], ax[2], ph))
        cnt = {x: sum(1 for c in coils if c[1] == x) for x in "ABC"}
        if len(set(cnt.values())) != 1:
            continue
        sA = abs(sum(c[2] * np.exp(1j * math.radians(c[3])) for c in coils if c[1] == "A"))
        if best is None or sA > best[0] + 1e-9:
            best = (sA, [c[:3] for c in coils])
    return best[1]


def winding_factor(Q, p, nu=1):
    """集中绕组第 nu 次谐波的绕组系数：k_w = k_p · k_d；节距系数 k_p = sin(ν·p·π/Q)（线圈跨一个齿），分布系数由每相线圈相量求和"""
    coils = tooth_winding(Q, p)
    ang = 2 * math.pi / Q * p * nu
    kp = abs(math.sin(nu * p * math.pi / Q))          # 线圈跨一个槽距：节距系数 = sin(ν·α/2)
    ph = [c for c in coils if c[1] == "A"]
    s = sum(sgn * np.exp(1j * k * ang) for k, _, sgn in ph)
    kd = abs(s) / len(ph)
    return kp * kd, kp, kd, len(ph)


def cogging_order(Q, p):
    """齿槽转矩每圈的基本周期数 = LCM(2p, Q)；越大，单次幅值一般越小"""
    return 2 * p * Q // math.gcd(2 * p, Q)


# ---------------------------------------------------------------- 二维有限元
def build_mesh(g, h_gap=0.25, h=1.2):
    """g：几何（mm）R_so、R_si、Q、b0（槽口宽）、h0（齿靴高）、bt（齿宽）、h_yoke（轭厚）、gap、t_m（磁钢厚）、R_ro（转子铁心外径）、R_shaft。
    返回 (节点 xy m, 三角形, 每个三角形的区域名, 槽区（槽号, 半边）)"""
    import gmsh
    if not gmsh.isInitialized():
        gmsh.initialize(["-noenv"], readConfigFiles=False)
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.clear()
    gmsh.model.add("m")
    occ = gmsh.model.occ
    Q = g["Q"]
    R_so, R_si = g["R_so"], g["R_si"]
    R_m_out = R_si - g["gap"]
    R_ro = R_m_out - g["t_m"]
    R_gap_mid = R_si - g["gap"] / 2
    disk = lambda r: occ.addDisk(0, 0, 0, r, r)  # noqa: E731
    stator = occ.cut([(2, disk(R_so))], [(2, disk(R_si))])[0]
    # 槽：齿靴下的槽口（宽 b0，高 h0）+ 槽身（两齿之间，到轭内径）
    r_slot_in = R_si + g["h0"]
    r_slot_out = R_so - g["h_yoke"]
    slots, polys = [], []
    for k in range(Q):
        th = 2 * math.pi * (k + 0.5) / Q                              # 槽中心（齿 k 在 2πk/Q）
        pts = []
        # 槽身：两边平行于各自的齿（齿宽 bt 平行齿），用多边形近似
        pitch = 2 * math.pi / Q
        def edge(r, side):
            # 齿中心线在 th ∓ pitch/2；槽边 = 齿边（离齿中心线 bt/2 的平行线）在半径 r 处的角度
            tc = th - side * pitch / 2
            return tc + side * math.asin(min(1.0, g["bt"] / 2 / r))
        rs = np.linspace(r_slot_in, r_slot_out, 6)
        left = [(r * math.cos(edge(r, 1)), r * math.sin(edge(r, 1))) for r in rs]
        right = [(r * math.cos(edge(r, -1)), r * math.sin(edge(r, -1))) for r in rs[::-1]]
        pts = left + right
        P = [occ.addPoint(x, y, 0) for x, y in pts]
        Ls = [occ.addLine(P[i], P[(i + 1) % len(P)]) for i in range(len(P))]
        body = occ.addPlaneSurface([occ.addCurveLoop(Ls)])
        a0 = math.asin(g["b0"] / 2 / R_si)
        mouth_pts = [(R_si * 0.999 * math.cos(th - a0), R_si * 0.999 * math.sin(th - a0)), ((r_slot_in + 0.01) * math.cos(th - a0 * R_si / r_slot_in), (r_slot_in + 0.01) * math.sin(th - a0 * R_si / r_slot_in)),
                     ((r_slot_in + 0.01) * math.cos(th + a0 * R_si / r_slot_in), (r_slot_in + 0.01) * math.sin(th + a0 * R_si / r_slot_in)), (R_si * 0.999 * math.cos(th + a0), R_si * 0.999 * math.sin(th + a0))]
        P2 = [occ.addPoint(x, y, 0) for x, y in mouth_pts]
        L2 = [occ.addLine(P2[i], P2[(i + 1) % 4]) for i in range(4)]
        mouth = occ.addPlaneSurface([occ.addCurveLoop(L2)])
        slots.append((body, mouth, th))
        polys.append(np.array(pts))
        polys.append(np.array(mouth_pts))
    occ.synchronize()
    gap = occ.cut([(2, disk(R_si))], [(2, disk(R_m_out))])[0]
    mag = occ.cut([(2, disk(R_m_out))], [(2, disk(R_ro))])[0]
    rot = occ.cut([(2, disk(R_ro))], [(2, disk(g["R_shaft"]))])[0]
    shaft = [(2, disk(g["R_shaft"]))]
    # 气隙中间加一个圆，把气隙分成两层（算麦克斯韦应力的圆在这里）
    occ.synchronize()
    tools_ = [(2, s[0]) for s in slots] + [(2, s[1]) for s in slots] + gap + mag + rot + shaft
    out, omap = occ.fragment(stator, tools_)
    occ.synchronize()
    gmsh.option.setNumber("Mesh.MeshSizeMax", h)
    fld = gmsh.model.mesh.field
    th_f = fld.add("MathEval")
    fld.setString(th_f, "F", f"{h_gap} + {h - h_gap} * Min(1, Abs(Sqrt(x*x+y*y) - {R_gap_mid}) / {3 * g['gap'] + 1.0})")
    fld.setAsBackgroundMesh(th_f)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MaxNumThreads2D", 1)
    gmsh.model.mesh.generate(2)
    nt, xyz, _ = gmsh.model.mesh.getNodes()
    xy = np.asarray(xyz).reshape(-1, 3)[:, :2] / 1000.0
    idx = {int(t): i for i, t in enumerate(nt)}
    tris, region = [], []
    for dim, tag in gmsh.model.getEntities(2):
        et, _, en = gmsh.model.mesh.getElements(2, tag)
        for t, e in zip(et, en):
            if t != 2:
                continue
            T = np.asarray(e, np.int64).reshape(-1, 3)
            c = gmsh.model.occ.getCenterOfMass(2, tag)
            r = math.hypot(c[0], c[1])
            ang = math.atan2(c[1], c[0])
            if r > R_si + 1e-6:
                # 槽还是铁？看质心是否在某个槽多边形里：用面积判断，铁的面积大
                area = gmsh.model.occ.getMass(2, tag)
                name = "iron_s" if area > 0.3 * math.pi * (R_so ** 2 - R_si ** 2) else "slot"
            elif r > R_m_out:
                name = "gap"
            elif r > R_ro or (abs(r) < 1e-9 and False):
                name = "mag"
            elif r > g["R_shaft"]:
                name = "iron_r"
            else:
                name = "shaft"
            for row in T:
                tris.append([idx[int(n)] for n in row])
                region.append(name)
    tris = np.array(tris)
    # 以三角形质心再分一次（gmsh 实体质心对环形区域会落在原点）
    cen = xy[tris].mean(axis=1) * 1000
    rr = np.hypot(cen[:, 0], cen[:, 1])
    region = np.array(region, dtype=object)
    from matplotlib.path import Path as _P
    inslot = np.zeros(len(tris), bool)
    for poly in polys:
        inslot |= _P(poly).contains_points(cen[:, :2])
    region[(rr > R_si)] = np.where(inslot[rr > R_si], "slot", "iron_s")
    region[(rr <= R_si) & (rr > R_m_out)] = "gap"
    region[(rr <= R_m_out) & (rr > R_ro)] = "mag"
    region[(rr <= R_ro) & (rr > g["R_shaft"])] = "iron_r"
    region[rr <= g["R_shaft"]] = "shaft"
    return xy, tris, region


def solve(xy, tris, region, mag_angle, g, mu_r_iron=2000.0, Br=1.2, J=None):
    """mag_angle：转子转过的机械角 rad；J：每个三角形的电流密度 A/m²（None 为空载）。返回每个节点的 A（Wb/m）"""
    from skfem import Basis, BilinearForm, ElementTriP1, LinearForm, MeshTri, condense, solve as fsolve
    from skfem.helpers import dot, grad
    m = MeshTri(xy.T.copy(), tris.T.copy())
    e = ElementTriP1()
    basis = Basis(m, e)
    p = g["p"]
    nu_el = np.where(np.isin(region, ["iron_s", "iron_r"]), 1.0 / (MU0 * mu_r_iron), 1.0 / MU0)
    cen = xy[tris].mean(axis=1)
    th = np.arctan2(cen[:, 1], cen[:, 0])
    rel = (th - mag_angle) % (2 * math.pi)
    pole = np.floor(rel / (math.pi / p)).astype(int)
    frac = (rel / (math.pi / p)) - pole
    arc = g.get("arc", 0.85)                                          # 磁钢极弧系数
    inmag = (region == "mag") & (np.abs(frac - 0.5) <= arc / 2)
    sgn = np.where(pole % 2 == 0, 1.0, -1.0)
    Mx = np.where(inmag, sgn * Br / MU0 * np.cos(th), 0.0)
    My = np.where(inmag, sgn * Br / MU0 * np.sin(th), 0.0)
    Jz = np.zeros(len(tris)) if J is None else J
    nu_q = basis.interpolate(basis.zeros())                          # 占位：用分片常数
    from skfem import ElementTriP0
    b0 = basis.with_element(ElementTriP0())
    nu_f = b0.interpolate(nu_el)
    mx_f, my_f, j_f = b0.interpolate(Mx), b0.interpolate(My), b0.interpolate(Jz)
    del nu_q

    @BilinearForm
    def a(u, v, w):
        return w["nu"] * dot(grad(u), grad(v))

    @LinearForm
    def f(v, w):
        return w["j"] * v + w["mx"] * grad(v)[1] - w["my"] * grad(v)[0]

    A = a.assemble(basis, nu=nu_f)
    b = f.assemble(basis, mx=mx_f, my=my_f, j=j_f)
    r_all = np.hypot(xy[:, 0], xy[:, 1])
    D = np.where(r_all > g["R_so"] / 1000 - 1e-7)[0]
    x = fsolve(*condense(A, b, D=D))
    return x


def gap_field(xy, tris, region, A, r):
    """半径 r（m）圆上的 B_r、B_θ（取包含该点的三角形的常数梯度）"""
    from matplotlib.tri import Triangulation, TrapezoidMapTriFinder
    tri = Triangulation(xy[:, 0], xy[:, 1], tris)
    finder = TrapezoidMapTriFinder(tri)
    th = np.linspace(0, 2 * math.pi, 720, endpoint=False)
    X, Y = r * np.cos(th), r * np.sin(th)
    ids = finder(X, Y)
    Br_, Bt_ = np.zeros_like(th), np.zeros_like(th)
    for k, (t, a_) in enumerate(zip(ids, th)):
        P = xy[tris[t]]
        M = np.array([[P[1, 0] - P[0, 0], P[1, 1] - P[0, 1]], [P[2, 0] - P[0, 0], P[2, 1] - P[0, 1]]])
        dA = np.array([A[tris[t][1]] - A[tris[t][0]], A[tris[t][2]] - A[tris[t][0]]])
        gx, gy = np.linalg.solve(M, dA)
        Bx, By = gy, -gx
        Br_[k] = Bx * math.cos(a_) + By * math.sin(a_)
        Bt_[k] = -Bx * math.sin(a_) + By * math.cos(a_)
    return th, Br_, Bt_


def slot_side_flux(xy, tris, region, A, g, Lstk):
    """每个槽分左右两半（左半属齿 k+1 的线圈、右半属齿 k 的线圈），返回各半边 A 的面积平均 × 叠厚（Wb·匝⁻¹ 的“每匝磁链”贡献）"""
    cen = xy[tris].mean(axis=1)
    th = np.arctan2(cen[:, 1], cen[:, 0]) % (2 * math.pi)
    P = xy[tris]
    area = 0.5 * np.abs((P[:, 1, 0] - P[:, 0, 0]) * (P[:, 2, 1] - P[:, 0, 1]) - (P[:, 2, 0] - P[:, 0, 0]) * (P[:, 1, 1] - P[:, 0, 1]))
    Aavg = A[tris].mean(axis=1)
    Q = g["Q"]
    out = np.zeros((Q, 2))
    insl = region == "slot"
    for k in range(Q):
        c = 2 * math.pi * (k + 0.5) / Q
        d = ((th - c + math.pi) % (2 * math.pi)) - math.pi
        for side, msk in ((0, d < 0), (1, d >= 0)):
            sel = insl & msk & (np.abs(d) < math.pi / Q)
            out[k, side] = (Aavg[sel] * area[sel]).sum() / max(area[sel].sum(), 1e-12) * Lstk
    return out, insl, th, area


def phase_flux(side_flux, coils, Nc):
    """线圈 k 绕在齿 k 上：两条边在槽 k−1 的右半（side 1）和槽 k 的左半（side 0）。每相磁链 = Σ sgn·Nc·(A_去 − A_回)"""
    Q = len(side_flux)
    lam = {"A": 0.0, "B": 0.0, "C": 0.0}
    for k, ph, sgn in coils:
        a_go = side_flux[(k - 1) % Q, 1]
        a_back = side_flux[k, 0]
        lam[ph] += sgn * Nc * (a_go - a_back)
    return lam


def maxwell_torque(xy, tris, region, A, r, Lstk):
    th, Br_, Bt_ = gap_field(xy, tris, region, A, r)
    return Lstk * r ** 2 / MU0 * np.mean(Br_ * Bt_) * 2 * math.pi, th, Br_


def arkkio_torque(xy, tris, region, A, g, Lstk):
    """阿尔基奥法：在整个气隙环上对 r·B_r·B_θ 做面积分，T = L/(μ0 (r₂ − r₁)) ∫ r B_r B_θ dS——比在一个圆上积麦克斯韦应力稳定得多"""
    sel = np.where(region == "gap")[0]
    P = xy[tris[sel]]
    a = A[tris[sel]]
    M = np.stack([P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]], axis=1)          # n×2×2
    dA = np.stack([a[:, 1] - a[:, 0], a[:, 2] - a[:, 0]], axis=1)
    gr = np.linalg.solve(M, dA[..., None])[..., 0]                       # ∂A/∂x, ∂A/∂y
    Bx, By = gr[:, 1], -gr[:, 0]
    c = P.mean(axis=1)
    r = np.hypot(c[:, 0], c[:, 1])
    th = np.arctan2(c[:, 1], c[:, 0])
    Br_ = Bx * np.cos(th) + By * np.sin(th)
    Bt_ = -Bx * np.sin(th) + By * np.cos(th)
    area = 0.5 * np.abs(M[:, 0, 0] * M[:, 1, 1] - M[:, 0, 1] * M[:, 1, 0])
    r1, r2 = (g["R_si"] - g["gap"]) / 1000, g["R_si"] / 1000
    return Lstk / (MU0 * (r2 - r1)) * np.sum(area * r * Br_ * Bt_)
