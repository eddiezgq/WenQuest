"""第 11 章共用（重的那一半）：多体动力学跑标准动作、换算成大臂端面载荷；有限元的单位载荷工况。结果按本文件和数字工厂程序的散列
缓存在临时目录（_ch11.py 改了不必重算）。说明见 _ch11.py。"""
from __future__ import annotations

import hashlib
import math
import os
import pickle
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1]
if str(BOOK / "ch10" / "code") not in sys.path:
    sys.path.insert(0, str(BOOK / "ch10" / "code"))

import numpy as np  # noqa: E402

import _ch10 as H10  # noqa: E402
from cae import mbd, mbd_models as MM, solve as S, struct_parts as SP, wqcr5 as W  # noqa: E402
from cae.geometry import _LOCK, _gmsh  # noqa: E402

AL = H10.mat("6061-T6")
VERSION = "ch11-fe-v1"
FIL = 2.0                         # 法兰内角圆角 mm（第 10 章）
HMIN = 0.6                        # 内角加密处的网格尺寸 mm（球半径 BALL）
BALL = 3.5
HGLOB = 7.0                       # 整体网格 mm


# ---------------------------------------------------------------- 多体动力学：标准动作
def cycle(payload=W.PAYLOAD_KG, seg_s=W.RUNIN_SEG_S, dwell_s=W.RUNIN_DWELL_S, sample_hz=100):
    """返回 t（s）、q（6×N，rad）、rf3、rm3（3×N，N 与 N·m，世界坐标）、驱动峰值"""
    path = MM.robot_path(W.LIB_ID)
    P = [dict(zip(W.JOINTS, np.radians(p))) for p in W.RUNIN_POSES_DEG]
    pay = [{"body": "link6", "mass": payload, "pos": [float(x) for x in W.tcp_local()]}] if payload > 0 else []
    ts, qs, rfs, rms, peaks = [], [], [], [], {}
    t_off = 0.0
    for k in range(len(P) - 1):
        a, b = P[k], P[k + 1]
        dr = [{"joint": j, "kind": "move", "to": float(b[j]), "t0": dwell_s, "t1": dwell_s + seg_s} if abs(b[j] - a[j]) > 1e-9
              else {"joint": j, "kind": "hold"} for j in W.JOINTS]
        dur = dwell_s + seg_s + (dwell_s if k == len(P) - 2 else 0.0)
        info, ch, _ = mbd.simulate(mbd.load_spec(path=path), {"duration_s": dur, "initial": a, "payloads": pay, "drives": dr,
                                                              "sample_hz": sample_hz})
        t = np.asarray(ch["t"])
        keep = slice(None) if k == 0 else slice(1, None)
        ts.append(t[keep] + t_off)
        qs.append(np.array([ch["q." + j] for j in W.JOINTS])[:, keep])
        rfs.append(np.array([ch["rf.link3." + c] for c in "xyz"])[:, keep])
        rms.append(np.array([ch["rm.link3." + c] for c in "xyz"])[:, keep])
        for d in info["drives"]:
            peaks[d["joint"]] = max(peaks.get(d["joint"], 0.0), d["peak"])
        t_off += t[-1]
    return np.concatenate(ts), np.concatenate(qs, axis=1), np.concatenate(rfs, axis=1), np.concatenate(rms, axis=1), peaks


def frames(q):
    """大臂零件坐标（x 沿 J2 轴，z 沿管轴 J2 → J3，y = z × x）在世界坐标里的三个轴，与 wqcr5.upper_arm_end_loads 相同"""
    Tw = W.link_world(q)
    p0 = Tw[1][:3, 3]
    p1 = (Tw[1] @ np.append(W._child_pos(1), 1.0))[:3]
    ez = (p1 - p0) / np.linalg.norm(p1 - p0)
    ex = Tw[1][:3, 2]
    return np.array([ex, np.cross(ez, ex), ez]), p1


def end_loads(t, q, rf3, rm3):
    """大臂 J3 端面上的载荷（零件坐标）：6×N（Fx、Fy、Fz N；Mx、My、Mz N·m）。
    端面受的力 = −rf3 − m_J3 (a − g)；力矩 = −rm3（模组质心在 J3 中心，对它取矩为零）"""
    m3 = W.MODULES[W.JOINT_MODULE[2]]["mass"]
    n = q.shape[1]
    pos = np.zeros((3, n))
    R = np.zeros((n, 3, 3))
    for k in range(n):
        R[k], pos[:, k] = frames(q[:, k])
    dt = np.gradient(t)
    acc = np.gradient(np.gradient(pos, t, axis=1), t, axis=1)
    g = np.array([0.0, 0.0, -W.G0])[:, None]
    Fw = -rf3 - m3 * (acc - g)
    Mw = -rm3
    out = np.zeros((6, n))
    for k in range(n):
        out[:3, k] = R[k] @ Fw[:, k]
        out[3:, k] = R[k] @ Mw[:, k]
    return out


# ---------------------------------------------------------------- 有限元：带圆角的大臂、单位载荷工况
def arm_step(p, rf):
    """与第 10 章程序 10.4.1 相同：r–z 截面（含两段圆弧）绕管轴旋转一周"""
    L, D, t, ft, b = p["L"], p["D"], p["t"], p["flange_t"], p["bore"]
    R0, ri, rb = D / 2, D / 2 - t, b / 2
    with _LOCK, tempfile.TemporaryDirectory() as tmp:
        g = _gmsh()
        g.clear()
        g.model.add("arm")
        occ = g.model.occ
        Pp = lambda r, z: occ.addPoint(r, 0, z)                                  # noqa: E731
        pts = [Pp(rb, 0), Pp(R0, 0), Pp(R0, L), Pp(rb, L), Pp(rb, L - ft), Pp(ri - rf, L - ft), Pp(ri, L - ft - rf),
               Pp(ri, ft + rf), Pp(ri - rf, ft), Pp(rb, ft)]
        c1, c2 = Pp(ri - rf, L - ft - rf), Pp(ri - rf, ft + rf)
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


def ball_mesh(centers, rad, hmin):
    """CAE 的 mesh() 换成“整体 HGLOB、几个小球内 hmin”的版本（只改网格生成，与第 10 章程序 10.4.1 的写法相同）"""
    def mesh(gmsh, size_mm, fine_faces=()):
        h = size_mm
        for k, v in (("Mesh.MeshSizeMax", h), ("Mesh.MeshSizeMin", hmin / 2), ("Mesh.MeshSizeFromCurvature", 0),
                     ("Mesh.ElementOrder", 2), ("Mesh.HighOrderOptimize", 1), ("Mesh.Algorithm3D", 10), ("Mesh.MaxNumThreads3D", 1),
                     ("Mesh.MeshSizeExtendFromBoundary", 0), ("Mesh.MeshSizeFromPoints", 0)):
            gmsh.option.setNumber(k, v)
        f = gmsh.model.mesh.field
        balls = []
        for c in centers:
            bl = f.add("Ball")
            for k, v in zip(("XCenter", "YCenter", "ZCenter"), c):
                f.setNumber(bl, k, v)
            f.setNumber(bl, "Radius", rad)
            f.setNumber(bl, "Thickness", 2 * h)
            f.setNumber(bl, "VIn", hmin)
            f.setNumber(bl, "VOut", h)
            balls.append(bl)
        mn = f.add("Min")
        f.setNumbers(mn, "FieldsList", balls)
        f.setAsBackgroundMesh(mn)
        gmsh.model.mesh.generate(3)
        et, _, en = gmsh.model.mesh.getElements(3)
        tets = np.asarray(en[list(et).index(11)], np.int64).reshape(-1, 10)
        nt, xyz, _ = gmsh.model.mesh.getNodes()
        return np.asarray(nt, np.int64), np.asarray(xyz, float).reshape(-1, 3), tets
    return mesh


def to_cyl(s6, th):
    """直角坐标的应力分量 (sxx, syy, szz, sxy, syz, szx) → 柱坐标 (srr, stt, szz, srt, stz, szr)，th 为该点的方位角"""
    c, s = math.cos(th), math.sin(th)
    sxx, syy, szz, sxy, syz, szx = s6
    srr = c * c * sxx + s * s * syy + 2 * c * s * sxy
    stt = s * s * sxx + c * c * syy - 2 * c * s * sxy
    srt = (syy - sxx) * c * s + sxy * (c * c - s * s)
    szr = szx * c + syz * s
    stz = -szx * s + syz * c
    return np.array([srr, stt, szz, srt, stz, szr])


def to_cart(sc, th):
    """柱坐标分量 → 直角坐标分量（与 to_cyl 互逆）"""
    c, s = np.cos(th), np.sin(th)
    srr, stt, szz, srt, stz, szr = sc
    sxx = c * c * srr + s * s * stt - 2 * c * s * srt
    syy = s * s * srr + c * c * stt + 2 * c * s * srt
    sxy = (srr - stt) * c * s + srt * (c * c - s * s)
    szx = szr * c - stz * s
    syz = szr * s + stz * c
    return np.array([sxx, syy, szz, sxy, syz, szx])


COS, SIN = [0, 1, 2, 5], [3, 4]      # 一阶谐波里随 cos θ 变的分量（rr、θθ、zz、zr）与随 sin θ 变的（rθ、θz）


def unit_cases(p=None, rf=FIL, hmin=HMIN, cases=("Fx", "My", "Fz", "Mz"), ends=("J3", "J2")):
    """零件是回转体，单位载荷工况可以只算四个：横向力 Fx、弯矩 My（应力沿圆周按 cos θ / sin θ 变化，Fy、Mx 由它们转 90° 得到）、
    轴力 Fz、扭矩 Mz（沿圆周不变）。在 θ = 0° 和 90° 两处的内角加密网格，读出圆角表面一排点的柱坐标应力。
    返回 {"J3": 端数据, "J2": 端数据}；端数据 = {"phi": 圆角上各点的位置角（0° 在管壁一侧、90° 在法兰一侧）,
    "rz": 各点 (r, z)，"amp": {工况: (点数, 6) 的幅值}, "elements": 单元数}"""
    p = SP.params_of("wqcr5_upper", p)
    step = arm_step(p, rf)
    faces = H10.faces_of(step)
    z0 = [f["id"] for f in faces if f["kind"] == "plane" and abs(f["center"][2]) < 1e-6]
    z1 = [f["id"] for f in faces if f["kind"] == "plane" and abs(f["center"][2] - p["L"]) < 1e-6]
    L, ft, ri = p["L"], p["flange_t"], p["D"] / 2 - p["t"]
    out = {}
    m0 = S.mesh
    try:
        for end, fixed, loaded, zc in (("J3", z0, z1, L - ft), ("J2", z1, z0, ft)):
            if end not in ends:
                continue
            sgn = -1.0 if end == "J3" else 1.0                 # 圆心在内角的哪一侧
            zf = zc + sgn * rf
            ctr = [(ri - rf / 2, 0.0, zc + sgn * rf / 2), (0.0, ri - rf / 2, zc + sgn * rf / 2)]
            S.mesh = ball_mesh(ctr, BALL, hmin)
            amp, nel, P0 = {}, 0, None
            for case in cases:
                F0 = {"Fx": [1.0, 0, 0], "Fz": [0, 0, 1.0]}.get(case, [0.0, 0, 0])
                M0 = {"My": [0, 1e3, 0], "Mz": [0, 0, 1e3]}.get(case, [0.0, 0, 0])
                if end == "J3":
                    F, M = np.array(F0), np.array(M0)
                else:                                          # 根部：J2 端面受平衡载荷 F_r = −F，M_r = −(M + r × F)，r = (0, 0, L)
                    F = -np.array(F0)
                    M = -(np.array(M0) + np.cross([0.0, 0.0, L], F0))
                loads = [{"type": "fixed", "faces": fixed}]
                if np.linalg.norm(F) > 0:
                    loads.append({"type": "force", "faces": loaded, "vector_n": [float(x) for x in F]})
                if np.linalg.norm(M) > 0:
                    loads.append({"type": "moment", "faces": loaded, "vector_nmm": [float(x) for x in M]})
                st, _, P, STR = H10.fe_solve(step, loads, HGLOB, AL)
                nel = st["elements"]
                if P0 is None:                                 # 取点：圆角表面、管外表面，θ ≈ 0° 与 θ ≈ 90° 两排
                    rows = {0: [], 90: []}
                    for n, x in P.items():
                        r, z, th = math.hypot(x[0], x[1]), x[2], math.atan2(x[1], x[0])
                        for deg in (0, 90):
                            if abs(th - math.radians(deg)) * r > 0.35:
                                continue
                            d = math.hypot(r - (ri - rf), z - zf)
                            if abs(d - rf) < 0.02 and r >= ri - rf - 1e-6 and sgn * (z - zf) <= 1e-6:
                                ph = math.degrees(math.atan2(abs(z - zf), r - (ri - rf)))     # 0° 在管壁一侧，90° 在法兰一侧
                                rows[deg].append((n, ph, r, z, th))
                    # θ = 0° 的点为准；90° 一排取位置最近的点
                    base = sorted(rows[0], key=lambda x: x[1])
                    pair = [min(rows[90], key=lambda c: math.hypot(c[2] - b[2], c[3] - b[3])) for b in base]
                    P0 = (base, pair)
                base, pair = P0
                A = np.zeros((len(base), 6))
                for k, (b, c) in enumerate(zip(base, pair)):
                    s0 = to_cyl(STR[b[0]][:6], b[4])
                    s9 = to_cyl(STR[c[0]][:6], c[4])
                    if case in ("Fx", "My"):                   # 一阶：cos 分量在 0°，sin 分量在 90°（除以 cos θ、sin θ 修正一点角度偏差）
                        A[k, COS] = s0[COS] / math.cos(b[4])
                        A[k, SIN] = s9[SIN] / math.sin(c[4])
                    else:                                      # 零阶：两排平均
                        A[k] = 0.5 * (s0 + s9)
                amp[case] = A
            base = P0[0]
            out[end] = {"phi": [b[1] for b in base], "rz": np.array([(b[2], b[3]) for b in base]), "amp": amp, "elements": nel}
    finally:
        S.mesh = m0
    return out


def tensor_at(U_end, L6, th):
    """方位角 th 处各点的应力张量（直角坐标）时间历程：(点, 时间, 6)。L6：J3 端面载荷（Fx、Fy、Fz N；Mx、My、Mz N·m），
    回转体：Fy 的解 = Fx 的解转 +90°，Mx 的解 = My 的解转 −90°（S(θ) → S(θ ∓ 90°)）"""
    A = U_end["amp"]

    def mode1(Ac, ang):                                         # 一阶谐波工况在 θ = ang 处的柱坐标应力
        s = np.zeros_like(Ac)
        s[:, COS] = Ac[:, COS] * math.cos(ang)
        s[:, SIN] = Ac[:, SIN] * math.sin(ang)
        return s
    cyl = {"Fx": mode1(A["Fx"], th), "Fy": mode1(A["Fx"], th - math.pi / 2),
           "My": mode1(A["My"], th), "Mx": mode1(A["My"], th + math.pi / 2), "Fz": A["Fz"], "Mz": A["Mz"]}
    order = ["Fx", "Fy", "Fz", "Mx", "My", "Mz"]
    Sc = np.stack([cyl[k] for k in order])                     # (6 工况, 点, 6)
    hist_c = np.einsum("kt,knc->ntc", L6, Sc)
    return np.moveaxis(to_cart(np.moveaxis(hist_c, 2, 0), th), 0, 2)


def heavy():
    """多体动力学 + 有限元，缓存在临时目录"""
    src = [Path(__file__)] + [Path(m.__file__) for m in (mbd, S, W, SP, H10)] + [Path(S.__file__).with_name(n) for n in ("geometry.py", "materials.py")]
    key = hashlib.sha1(VERSION.encode() + b"".join(p.read_bytes() for p in src)).hexdigest()[:12]
    f = Path(tempfile.gettempdir()) / f"wq-mechdesign-ch11-{key}.pkl"
    if f.exists():
        return pickle.loads(f.read_bytes())
    t, q, rf3, rm3, peaks = cycle()
    L6 = end_loads(t, q, rf3, rm3)
    # 静止伸直时（第 10 章的预设工况）的同一换算，用来核对
    q0 = np.radians(W.OUTSTRETCHED_DEG)
    _, ch0, _ = mbd.simulate(mbd.load_spec(path=MM.robot_path(W.LIB_ID)),
                             {"duration_s": 0.3, "initial": dict(zip(W.JOINTS, q0)),
                              "payloads": [{"body": "link6", "mass": W.PAYLOAD_KG, "pos": [float(x) for x in W.tcp_local()]}],
                              "drives": [{"joint": j, "kind": "hold"} for j in W.JOINTS], "sample_hz": 200})
    tt = np.asarray(ch0["t"])
    qq = np.array([ch0["q." + j] for j in W.JOINTS])
    L0 = end_loads(tt, qq, np.array([ch0["rf.link3." + c] for c in "xyz"]), np.array([ch0["rm.link3." + c] for c in "xyz"]))[:, -1]
    U = unit_cases()
    res = {"t": t, "q": q, "L6": L6, "peaks": peaks, "L0": L0, "U": U}
    tmp = f.with_suffix(".part")
    tmp.write_bytes(pickle.dumps(res))
    tmp.replace(f)
    return res


