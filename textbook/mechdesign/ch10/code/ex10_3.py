"""10.4 应力集中与应力集中系数；有限元里的应力集中：网格收敛与尖角奇异。

算例 10.4.1  带孔板（钢，长 400、宽 200、厚 5，中间孔 Ø20，本书设定）一端固定、一端均匀拉伸，名义应力 50 MPa。用数字工厂 CAE 的同一套
            程序，整体网格 16 mm 不变，只把孔边的网格从 8 mm 逐级加密到 0.5 mm，孔边最大正应力趋近多少；与基尔施的无限大板解 Kt = 3、
            有限宽板的海伍德公式比较；
算例 10.4.2  WQ-CR5 大臂的管与法兰相接的内角（J3 端）：数字工厂示例零件是尖角（圆角半径 0），本书另做圆角 2 mm、4 mm 两种（同样的形状），
            整体网格 7 mm 不变，只把内角顶部附近的网格从 4 mm 逐级加密到 0.5 mm，看内角附近的最大冯·米塞斯应力：尖角随网格加密一直涨
            （奇异，没有极限），有圆角的趋于一个确定的值（用最后三级做艾特肯外推估计它）；管中段的应力始终不变。
            求解、加载与 CAE 相同；网格生成另写了一个只在局部加密的版本（local_mesh），CAE 网页只能整体加密；
图 10.4.1。
"""
import math
import os
import tempfile

import numpy as np

import _ch10 as H
from bookout import T, figure, out, style
from cae import solve as S, struct_parts as SP
from cae.geometry import _LOCK, _gmsh

ST = H.mat("45-QT")
AL = H.mat("6061-T6")
_mesh0 = S.mesh


def local_mesh(where, hmin):
    """把 CAE 的 mesh() 换成“整体尺寸不变、where 附近加密到 hmin”的版本（gmsh 的 Distance + Threshold 场，与 CAE 加密载荷面的写法相同）。
    where(gmsh, field, h, hmin) 建好加密用的场，返回场的编号"""
    def mesh(gmsh, size_mm, fine_faces=()):
        h = size_mm
        gmsh.option.setNumber("Mesh.MeshSizeMax", h)
        gmsh.option.setNumber("Mesh.MeshSizeMin", hmin / 2)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        gmsh.option.setNumber("Mesh.ElementOrder", 2)
        gmsh.option.setNumber("Mesh.HighOrderOptimize", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 10)
        gmsh.option.setNumber("Mesh.MaxNumThreads3D", 1)
        f = gmsh.model.mesh.field
        t = where(gmsh, f, h, hmin)
        f.setAsBackgroundMesh(t)
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.model.mesh.generate(3)
        etypes, _, enodes = gmsh.model.mesh.getElements(3)
        k = list(etypes).index(11)
        tets = np.asarray(enodes[k], np.int64).reshape(-1, 10)
        ntags, xyz, _ = gmsh.model.mesh.getNodes()
        return np.asarray(ntags, np.int64), np.asarray(xyz, float).reshape(-1, 3), tets
    return mesh


def solve_local(step, loads, h, material, where, hmin):
    S.mesh = local_mesh(where, hmin)
    try:
        return H.fe_solve(step, loads, h, material)
    finally:
        S.mesh = _mesh0


def circles_near(r0, z0, tol=1.0):
    """半径 r0、位于 z = z0 附近的圆边（以 z 为轴）：到它们的距离 < 2·hmin 的地方网格为 hmin，向外渐变到 h"""
    def where(gmsh, f, h, hmin):
        out = []
        for _, e in gmsh.model.getEntities(1):
            bb = gmsh.model.getBoundingBox(1, e)
            if abs(bb[2] - z0) < tol + 1e-6 and abs(bb[5] - z0) < tol + 1e-6 and abs((bb[3] - bb[0]) / 2 - r0) < tol + 1e-6:
                out.append(e)
        d = f.add("Distance")
        f.setNumbers(d, "CurvesList", out)
        f.setNumber(d, "Sampling", 400)
        t = f.add("Threshold")
        f.setNumber(t, "InField", d)
        f.setNumber(t, "SizeMin", hmin)
        f.setNumber(t, "SizeMax", h)
        f.setNumber(t, "DistMin", 2 * hmin)
        f.setNumber(t, "DistMax", 2 * hmin + 3 * h)
        return t
    return where


def ball_at(c, rad):
    """以 c 为心、半径 rad 的球内网格为 hmin，外面一层渐变到 h（只在最危险的那一点附近加密，单元数可控）"""
    def where(gmsh, f, h, hmin):
        b = f.add("Ball")
        f.setNumber(b, "XCenter", c[0])
        f.setNumber(b, "YCenter", c[1])
        f.setNumber(b, "ZCenter", c[2])
        f.setNumber(b, "Radius", rad)
        f.setNumber(b, "Thickness", 2 * h)
        f.setNumber(b, "VIn", hmin)
        f.setNumber(b, "VOut", h)
        return b
    return where


# ---------------------------------------------------------------- 算例 10.4.1：带孔板
PL, PW, PT, PD, SNOM = 400.0, 200.0, 5.0, 20.0, 50.0


def plate_step():
    with _LOCK, tempfile.TemporaryDirectory() as tmp:
        g = _gmsh()
        g.clear()
        g.model.add("plate")
        occ = g.model.occ
        b = occ.addBox(-PL / 2, -PW / 2, 0, PL, PW, PT)
        c = occ.addCylinder(0, 0, 0, 0, 0, PT, PD / 2)
        occ.cut([(3, b)], [(3, c)])
        occ.synchronize()
        f = os.path.join(tmp, "plate.step")
        g.write(f)
        g.clear()
        return open(f, "rb").read()


pstep = plate_step()
pf = H.faces_of(pstep)
left = [f["id"] for f in pf if f["kind"] == "plane" and abs(f["center"][0] + PL / 2) < 1e-6]
right = [f["id"] for f in pf if f["kind"] == "plane" and abs(f["center"][0] - PL / 2) < 1e-6]
ploads = [{"type": "fixed", "faces": left}, {"type": "force", "faces": right, "vector_n": [SNOM * PW * PT, 0.0, 0.0]}]
kt_rows = []
for hmin in (8.0, 4.0, 2.0, 1.0, 0.5):
    st, _, P, STR = solve_local(pstep, ploads, 16.0, ST, circles_near(PD / 2, PT / 2, PT / 2 + 0.1), hmin)
    near = [n for n in STR if np.hypot(P[n][0], P[n][1]) < PD / 2 + 0.01]
    smax = max(STR[n][0] for n in near)                      # σx：孔边上下两点最大
    kt_rows.append((hmin, st["elements"], smax / SNOM))
    print("# plate", hmin, st["elements"], round(smax / SNOM, 4), flush=True)
kt_kirsch = 3.0
kt_heywood_net = 2 + (1 - PD / PW) ** 3                     # 海伍德：按净截面名义应力
kt_heywood = kt_heywood_net / (1 - PD / PW)                 # 换算到按毛截面（与上面一致）

# ---------------------------------------------------------------- 算例 10.4.2：大臂内角
def arm_step(p, rf):
    """与示例零件同样的形状（铝管 + 两端法兰 + 线缆孔），只多一步：管腔两端的内角倒圆角 rf。
    rf = 0 时直接用 struct_parts.build；否则把 r–z 截面（含两段圆弧）绕管轴旋转一周生成"""
    if rf <= 0:
        return SP.build("wqcr5_upper", p)
    L, D, t, ft, b = p["L"], p["D"], p["t"], p["flange_t"], p["bore"]
    R0, ri, rb = D / 2, D / 2 - t, b / 2
    with _LOCK, tempfile.TemporaryDirectory() as tmp:
        g = _gmsh()
        g.clear()
        g.model.add("arm")
        occ = g.model.occ
        P = lambda r, z: occ.addPoint(r, 0, z)                                   # noqa: E731
        pts = [P(rb, 0), P(R0, 0), P(R0, L), P(rb, L), P(rb, L - ft), P(ri - rf, L - ft), P(ri, L - ft - rf),
               P(ri, ft + rf), P(ri - rf, ft), P(rb, ft)]
        c1, c2 = P(ri - rf, L - ft - rf), P(ri - rf, ft + rf)
        cur = [occ.addLine(pts[0], pts[1]), occ.addLine(pts[1], pts[2]), occ.addLine(pts[2], pts[3]), occ.addLine(pts[3], pts[4]),
               occ.addLine(pts[4], pts[5]), occ.addCircleArc(pts[5], c1, pts[6]), occ.addLine(pts[6], pts[7]),
               occ.addCircleArc(pts[7], c2, pts[8]), occ.addLine(pts[8], pts[9]), occ.addLine(pts[9], pts[0])]
        sf = occ.addPlaneSurface([occ.addCurveLoop(cur)])
        occ.revolve([(2, sf)], 0, 0, 0, 0, 0, 1, 2 * math.pi)
        occ.synchronize()
        f = os.path.join(tmp, "arm.step")
        g.write(f)
        g.clear()
        return open(f, "rb").read()


p0 = SP.params_of("wqcr5_upper")
L, D, t, ft = p0["L"], p0["D"], p0["t"], p0["flange_t"]
ri = D / 2 - t
MESH = (4.0, 2.0, 1.0, 0.5)                # 内角附近（只在顶部最危险的那一段）的网格尺寸
FIL = (0.0, 2.0, 4.0)
corner = {}
for rf in FIL:
    step = arm_step(p0, rf)
    fcs = H.faces_of(step)
    ex = SP.example("wqcr5_upper", p0, fcs)
    R = ex["rows"]
    loads = [{"type": "fixed", "faces": R[0]["faces"]},
             {"type": "force", "faces": R[1]["faces"], "vector_n": [R[1]["fx"], R[1]["fy"], R[1]["fz"]]},
             {"type": "moment", "faces": R[2]["faces"], "vector_nmm": [R[2]["mx"] * 1e3, R[2]["my"] * 1e3, R[2]["mz"] * 1e3]}]
    rows = []
    for hm in MESH:
        h = hm
        st, _, P, STR = solve_local(step, loads, 7.0, AL, ball_at((0.0, ri, L - ft), max(rf + 3.0, 3 * hm)), hm)
        zc = L - ft
        # 内角附近：离 (r = ri, z = L − ft) 这一圈不超过 rf + 3 mm 的节点
        cn = [n for n in STR if math.hypot(math.hypot(P[n][0], P[n][1]) - ri, P[n][2] - zc) < rf + 3.0 and P[n][1] > 0 and abs(P[n][0]) < rf + 3.0]
        vmc = max(H.vm_of(H.principal(STR[n])) for n in cn)
        mid = [n for n in STR if abs(P[n][2] - L / 2) < 7.0 and np.hypot(P[n][0], P[n][1]) > D / 2 - 0.01]
        vmm = max(H.vm_of(H.principal(STR[n])) for n in mid)
        rows.append((h, st["elements"], vmc, vmm))
        print("# arm", rf, hm, st["elements"], round(vmc, 3), round(vmm, 3), flush=True)
    corner[rf] = rows

plt = style()
fig, (a0, a2) = plt.subplots(1, 2, figsize=(7.4, 3.0))
hs = [r[0] for r in kt_rows]
a0.semilogx(hs, [r[2] for r in kt_rows], "o-", color="#1f77b4", lw=1.3, ms=3.5, label=T("有限元（CAE 同一套程序）", "FE (same CAE code)"))
a0.axhline(kt_heywood, color="#d62728", lw=0.9, ls="--", label=T(f"海伍德公式 {kt_heywood:.2f}", f"Heywood {kt_heywood:.2f}"))
a0.axhline(kt_kirsch, color=H.MUTED, lw=0.8, ls=":", label=T("基尔施（无限大板）3", "Kirsch (infinite plate) 3"))
a0.invert_xaxis()
a0.set_xticks(hs)
a0.set_xticklabels([f"{x:g}" for x in hs])
a0.minorticks_off()
a0.set_ylim(2.8, 3.3)
a0.set_xlabel(T("孔边的网格尺寸 / mm（对数坐标）", "Mesh size at the hole / mm (log)"), fontsize=7.0)
a0.set_ylabel(T("孔边 σx / 名义应力", "Hole-edge σx / nominal"), fontsize=7.0)
a0.legend(fontsize=5.9, frameon=False, loc="lower right")
a0.tick_params(labelsize=6.2)
a0.set_title(T("(a) 带孔板：孔边加密，收敛到 Kt", "(a) Plate with hole: refine at the hole, converges to Kt"), fontsize=7.2)
for rf, c in zip(FIL, ("#d62728", "#ff7f0e", "#2ca02c")):
    rows = corner[rf]
    a2.semilogx([r[0] for r in rows], [r[2] for r in rows], "o-", color=c, lw=1.3, ms=3.5,
                label=T("尖角（示例零件）", "sharp (sample part)") if rf == 0 else T(f"圆角 {rf:g} mm", f"fillet {rf:g} mm"))
a2.semilogx([r[0] for r in corner[0.0]], [r[3] for r in corner[0.0]], "s--", color=H.MUTED, lw=1.0, ms=3,
            label=T("管中段顶部（不受影响）", "mid-tube top (unaffected)"))
a2.invert_xaxis()
a2.set_xticks(list(MESH))
a2.set_xticklabels([f"{x:g}" for x in MESH])
a2.minorticks_off()
a2.set_ylim(0, None)
a2.set_xlabel(T("内角处的网格尺寸 / mm（对数坐标）", "Mesh size at the corner / mm (log)"), fontsize=7.0)
a2.set_ylabel(T("最大冯·米塞斯应力 / MPa", "Max von Mises / MPa"), fontsize=7.0)
a2.legend(fontsize=5.9, frameon=False, loc="upper left")
a2.tick_params(labelsize=6.2)
a2.set_title(T("(b) WQ-CR5 大臂：管与法兰的内角", "(b) WQ-CR5 arm: tube–flange inner corner"), fontsize=7.2)
fig.tight_layout()
figure(fig, "fig10_4_1")

sharp, f2, f4 = corner[0.0], corner[2.0], corner[4.0]


def aitken(a, b, c):
    """三级（加密比相同）的结果外推到网格趋于零：c + (c − b)² / ((b − a) − (c − b))"""
    d1, d2 = b - a, c - b
    return c + d2 * d2 / (d1 - d2) if abs(d1 - d2) > 1e-9 and d2 / d1 < 0.9 else float("nan")


f2_ext = aitken(f2[-3][2], f2[-2][2], f2[-1][2])
f4_ext = aitken(f4[-3][2], f4[-2][2], f4[-1][2])
# 数字工厂网页上同一个零件（尖角）、整体 7 mm 网格的结果，作为“这里所用网格”的基准
_, _, _, ld0, _ = H.upper_arm()
st7, _, _, _ = H.fe_solve(SP.build("wqcr5_upper", p0), ld0, 7.0, AL)
vm7 = st7["vm_max_mpa"]
out(PL=PL, PW=PW, PT=PT, PD=PD, SNOM=SNOM,
    kt_a=kt_rows[0][2], kt_b=kt_rows[2][2], kt_c=kt_rows[-1][2], el_c=kt_rows[-1][1], h_a=kt_rows[0][0], h_c=kt_rows[-1][0],
    kt_heywood=kt_heywood, kt_heywood_net=kt_heywood_net, err_kt=abs(kt_rows[-1][2] / kt_heywood - 1) * 100,
    s_a=sharp[0][2], s_c=sharp[-1][2], s_grow=sharp[-1][2] / sharp[0][2],
    f2_a=f2[0][2], f2_c=f2[-1][2], f2_ch=abs(f2[-1][2] / f2[-2][2] - 1) * 100,
    f4_a=f4[0][2], f4_c=f4[-1][2], f4_ch=abs(f4[-1][2] / f4[-2][2] - 1) * 100,
    mid_a=sharp[0][3], mid_c=sharp[-1][3], el_arm=sharp[-1][1], hm_a=MESH[0], hm_c=MESH[-1], ri=ri, ft=ft,
    f2_ext=f2_ext, f4_ext=f4_ext, vm7=vm7, r_f2=f2_ext / vm7, H_PLATE=16.0, H_ARM=7.0, fil_a=FIL[1], fil_b=FIL[2])
