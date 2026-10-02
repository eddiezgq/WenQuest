"""第 33 章的有限元计算（Gmsh 二阶四面体 + CalculiX），网格写入与结果读取用数字工厂有限元服务的同一套代码
（factory/digital/cae/solve.py），书里的数与工厂“仿真与分析”算出的数同源。"""
from __future__ import annotations

import math
import os
os.environ.setdefault("WQ_CCX_SOLVER", "SPOOLES")       # 直接法：带柱坐标约束的模型用迭代法收敛很慢
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "factory" / "digital"))
from cae import solve as S  # noqa: E402


def _gmsh():
    import gmsh
    if not gmsh.isInitialized():
        gmsh.initialize(["-noenv"], readConfigFiles=False)
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.clear()
    gmsh.model.add("m")
    return gmsh


def _solve(xyz, ntags, tets, fixed, forces, E=210000.0, nu=0.3):
    mat = {"E_mpa": E, "nu": nu, "density_t_mm3": 7.85e-9}
    with tempfile.TemporaryDirectory() as d:
        inp = os.path.join(d, "job.inp")
        S.write_inp(inp, ntags, xyz, tets, fixed, [], forces, mat)
        r = subprocess.run([S.CCX, "-i", "job"], cwd=d, capture_output=True, text=True, timeout=280,
                           env={**os.environ, "OMP_NUM_THREADS": "2"})
        if r.returncode != 0 or not os.path.exists(os.path.join(d, "job.frd")):
            raise RuntimeError("CalculiX 失败：" + (r.stdout + r.stderr)[-400:])
        return S.read_frd(os.path.join(d, "job.frd"))


def principal(s):
    sxx, syy, szz, sxy, syz, szx = s[:6]
    A = np.array([[sxx, sxy, szx], [sxy, syy, syz], [szx, syz, szz]])
    return np.linalg.eigvalsh(A)          # ascending


def stepped_bar_kt(d: float, D: float, r: float, h_mesh: float | None = None, fine: int = 10) -> dict:
    """阶梯圆轴（小径 d、大径 D、过渡圆角 r）在纯弯和纯扭下的理论应力集中系数 α_σ、α_τ。
    大径端面固定，小径端面加端部力矩（按 σ = My/I 分布）或转矩（按 τ = Tr/J 分布）；名义应力按小径。"""
    gmsh = _gmsh()
    occ = gmsh.model.occ
    Ld, LD = 2.5 * d, 1.5 * D
    a = occ.addCylinder(0, 0, 0, 0, 0, Ld, d / 2)
    b = occ.addCylinder(0, 0, Ld, 0, 0, LD, D / 2)
    out, _ = occ.fuse([(3, a)], [(3, b)])
    occ.synchronize()
    vol = out[0][1]
    # 两段交界处的内凹圆边（半径 d/2、z = Ld）加圆角
    edges = [e for _, e in gmsh.model.getBoundary(out, combined=False, oriented=False, recursive=True) if _ == 1] if False else []
    for dim, tag in gmsh.model.getEntities(1):
        bb = gmsh.model.getBoundingBox(dim, tag)
        if abs(bb[2] - Ld) < 1e-6 and abs(bb[5] - Ld) < 1e-6 and abs((bb[3] - bb[0]) / 2 - d / 2) < 1e-6:
            edges.append(tag)
    occ.fillet([vol], edges, [r])
    occ.synchronize()
    h = h_mesh or d / 8
    gmsh.option.setNumber("Mesh.MeshSizeMax", h)
    gmsh.option.setNumber("Mesh.MeshSizeMin", r / (fine + 2))
    gmsh.option.setNumber("Mesh.ElementOrder", 2)
    gmsh.option.setNumber("Mesh.Algorithm3D", 10)
    gmsh.option.setNumber("Mesh.MaxNumThreads3D", 1)      # 单线程：网格每次相同，书中的数字可以复现
    f = gmsh.model.mesh.field
    box = f.add("Ball")
    f.setNumber(box, "Radius", 1.5 * r + d / 40)
    f.setNumber(box, "Thickness", d / 4)
    f.setNumber(box, "VIn", r / fine)
    f.setNumber(box, "VOut", h)
    f.setNumber(box, "XCenter", 0); f.setNumber(box, "YCenter", d / 2 + r * 0.3); f.setNumber(box, "ZCenter", Ld - r * 0.3)   # 弯曲受拉侧（+y）
    ring = f.add("Distance")
    fil = [t for (dm, t) in gmsh.model.getEntities(2) if gmsh.model.getType(2, t) not in ("Plane", "Cylinder")]   # 圆角面（环面）
    f.setNumbers(ring, "SurfacesList", fil)
    th = f.add("Threshold")
    f.setNumber(th, "InField", ring); f.setNumber(th, "SizeMin", r / fine); f.setNumber(th, "SizeMax", h)
    f.setNumber(th, "DistMin", r / 4); f.setNumber(th, "DistMax", 2 * r + d / 10)
    mn = f.add("Min")
    f.setNumbers(mn, "FieldsList", [box])
    f.setAsBackgroundMesh(mn)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.model.mesh.generate(3)
    et, _, en = gmsh.model.mesh.getElements(3)
    tets = np.asarray(en[list(et).index(11)], np.int64).reshape(-1, 10)
    ntags, xyz, _ = gmsh.model.mesh.getNodes()
    ntags = np.asarray(ntags, np.int64); xyz = np.asarray(xyz, float).reshape(-1, 3)
    P = {int(t): p for t, p in zip(ntags, xyz)}
    end_small = [t for (dm, t) in gmsh.model.getEntities(2) if abs(gmsh.model.getBoundingBox(2, t)[5]) < 1e-6]
    end_big = [t for (dm, t) in gmsh.model.getEntities(2) if abs(gmsh.model.getBoundingBox(2, t)[2] - (Ld + LD)) < 1e-6]
    fixed = set()
    for t in end_big:
        fixed |= {int(n) for n in gmsh.model.mesh.getNodes(2, t, includeBoundary=True)[0]}
    tris = np.concatenate([S.face_tris(gmsh, t) for t in end_small])
    Pi = {k: v for k, v in P.items()}
    I = math.pi * d ** 4 / 64; J = 2 * I
    M = 1.0e5; T = 1.0e5                                  # N·mm，线弹性，名义应力按比例
    res = {"n_elements": int(len(tets))}
    zone = [(n, p) for n, p in P.items() if Ld - 2 * r - 1 < p[2] < Ld + 1]
    for case in ("bend", "torsion"):
        if case == "bend":
            fn = lambda c, n: np.array([0.0, 0.0, M * c[1] / I])           # 端面上 σ_z = M y / I（端面外法向 −z，力沿 +z 为拉）
        else:
            fn = lambda c, n: np.array([-T * c[1] / J, T * c[0] / J, 0.0])  # τ = T r / J，切向
        forces = S.consistent_loads(tris, Pi, lambda c, n: -fn(c, n) if case == "bend" else fn(c, n))
        _, stress = _solve(xyz, ntags, tets, fixed, forces)
        if case == "bend":
            nom = M * (d / 2) / I
            peak = max(principal(stress[n])[2] if abs(principal(stress[n])[2]) >= abs(principal(stress[n])[0]) else abs(principal(stress[n])[0]) for n, _ in zone if n in stress)
            res["alpha_sigma"] = peak / nom
        else:
            nom = T * (d / 2) / J
            peak = max((principal(stress[n])[2] - principal(stress[n])[0]) / 2 for n, _ in zone if n in stress)
            res["alpha_tau"] = peak / nom
    return res


if __name__ == "__main__":
    import time
    t = time.time()
    print(stepped_bar_kt(40, 48, 1.6), time.time() - t)


def shaft_fea(lay, fillets, seats, F_xy, T_nmm, h=4.0, fine_r=4):
    """整根阶梯轴的有限元：lay [(z0, z1, d, ...)]；fillets {z: r}；
    seats：{"A": (z0, z1), "B": (z0, z1), "gear": (z0, z1), "cpl": (z0, z1)} 圆柱面的轴向范围；
    F_xy：齿轮对轴的横向力 (Fx, Fy)，N，均布在齿轮位圆柱面上；T_nmm：齿轮输入的转矩，由联轴器位限制转动来平衡。
    两个轴承位限制径向位移（A 兼限轴向）。返回表面节点的 (z, 半径, θ, 冯·米塞斯应力)、单元数。"""
    gmsh = _gmsh()
    occ = gmsh.model.occ
    vols = [(3, occ.addCylinder(0, 0, z0, 0, 0, z1 - z0, d / 2)) for z0, z1, d, *_ in lay]
    out, _ = occ.fuse(vols[:1], vols[1:])
    occ.removeAllDuplicates()
    occ.synchronize()
    vol = gmsh.model.getEntities(3)[0][1]
    edges, radii = [], []
    for z, r in fillets.items():
        dm = min(d for z0, z1, d, *_ in lay if abs(z0 - z) < 1e-6 or abs(z1 - z) < 1e-6)
        for dim, tag in gmsh.model.getEntities(1):
            bb = gmsh.model.getBoundingBox(dim, tag)
            if abs(bb[2] - z) < 1e-6 and abs(bb[5] - z) < 1e-6 and abs((bb[3] - bb[0]) / 2 - dm / 2) < 1e-4:
                edges.append(tag); radii.append(r)
    for e, r in zip(edges, radii):              # 一次一条边，圆角半径各不相同
        pass
    occ.fillet([vol], edges, radii, removeVolume=True)
    occ.synchronize()
    gmsh.option.setNumber("Mesh.MeshSizeMax", h)
    gmsh.option.setNumber("Mesh.MeshSizeMin", min(fillets.values()) / (fine_r + 2))
    gmsh.option.setNumber("Mesh.ElementOrder", 2)
    gmsh.option.setNumber("Mesh.Algorithm3D", 10)
    gmsh.option.setNumber("Mesh.MaxNumThreads3D", 1)      # 单线程：网格每次相同，书中的数字可以复现
    f = gmsh.model.mesh.field
    tori = [t for (dm, t) in gmsh.model.getEntities(2) if gmsh.model.getType(2, t) not in ("Plane", "Cylinder")]
    dist = f.add("Distance")
    f.setNumbers(dist, "SurfacesList", tori)
    th = f.add("Threshold")
    f.setNumber(th, "InField", dist); f.setNumber(th, "SizeMin", min(fillets.values()) / fine_r); f.setNumber(th, "SizeMax", h)
    f.setNumber(th, "DistMin", 0.3); f.setNumber(th, "DistMax", 6.0)
    f.setAsBackgroundMesh(th)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.model.mesh.generate(3)
    et, _, en = gmsh.model.mesh.getElements(3)
    tets = np.asarray(en[list(et).index(11)], np.int64).reshape(-1, 10)
    ntags, xyz, _ = gmsh.model.mesh.getNodes()
    ntags = np.asarray(ntags, np.int64); xyz = np.asarray(xyz, float).reshape(-1, 3)
    P = {int(t): p for t, p in zip(ntags, xyz)}

    def cyl_faces(z0, z1):
        out_ = []
        for dm, t in gmsh.model.getEntities(2):
            if gmsh.model.getType(2, t) != "Cylinder":
                continue
            bb = gmsh.model.getBoundingBox(2, t)
            if bb[2] < z1 - 1e-6 and bb[5] > z0 + 1e-6:          # 与该轴向范围重叠的圆柱面（节点再按 z 筛）
                out_.append(t)
        return out_

    def nodes_in(z0, z1, faces):
        ns = set()
        for t in faces:
            ns |= {int(n) for n in gmsh.model.mesh.getNodes(2, t, includeBoundary=True)[0]}
        return {n for n in ns if z0 - 1e-6 <= P[n][2] <= z1 + 1e-6}

    sup = []
    for key, dofs in (("A", [1]), ("B", [1])):
        z0, z1 = seats[key]
        sup.append((nodes_in(z0, z1, cyl_faces(z0 - 0.01, z1 + 0.01)), [0, 0, 0], [0, 0, 1], dofs))
    # 刚体转动与轴向平移：转矩由联轴器位上的反向面力平衡，不加支承；用两个方程“左轴承环上各节点的切向位移之和为 0”
    # “轴向位移之和为 0”消去它们。若把整圈节点的轴向位移都固定，截面就不能转动，轴承变成了固定端（第 13 章）；
    # 限制个别节点的切向位移，又会挡住横向平移，相当于多了一个支承。
    ring = sorted(sup[0][0])
    # 齿轮位：横向力均布 + 转矩按切向均布（圆柱面上 τ 均匀，合力矩 = T）
    z0, z1 = seats["gear"]
    gf = cyl_faces(z0 - 0.01, z1 + 0.01)
    tris = np.concatenate([S.face_tris(gmsh, t) for t in gf])
    tris = np.array([tr for tr in tris if all(z0 - 1e-6 <= P[int(n)][2] <= z1 + 1e-6 for n in tr)])
    area = 0.0
    for tri in tris:
        a, b, c = P[tri[0]], P[tri[1]], P[tri[2]]
        area += np.linalg.norm(np.cross(b - a, c - a)) / 2
    rg = np.mean([math.hypot(*P[n][:2]) for n in tris[:, 0]])
    Fx, Fy = F_xy

    def balanced(fs):
        """转矩的切向面力在网格疏密不均时会有一点合力，把它平均扣掉（各节点扣同一个力，对轴线的力矩为零）。"""
        net = sum(fs.values()) / len(fs)
        return {n: f - net for n, f in fs.items()}

    def ttrac(c, nrm):
        th_ = math.atan2(c[1], c[0])
        t_tan = T_nmm / (rg * area)                  # 切向面力
        return np.array([-t_tan * math.sin(th_), t_tan * math.cos(th_), 0.0])
    forces = balanced(S.consistent_loads(tris, P, ttrac))
    for n, f in S.consistent_loads(tris, P, lambda c, nrm: np.array([Fx / area, Fy / area, 0.0])).items():
        forces[n] = forces.get(n, 0) + f
    # 联轴器位：大小相等、方向相反的转矩，按切向面力均布
    c0, c1 = seats["cpl"]
    ctris = np.concatenate([S.face_tris(gmsh, t) for t in cyl_faces(c0 - 0.01, c1 + 0.01)])
    ctris = np.array([tr for tr in ctris if all(c0 - 1e-6 <= P[int(n)][2] <= c1 + 1e-6 for n in tr)])
    carea = sum(np.linalg.norm(np.cross(P[tr[1]] - P[tr[0]], P[tr[2]] - P[tr[0]])) / 2 for tr in ctris)
    rc = np.mean([math.hypot(*P[n][:2]) for n in ctris[:, 0]])

    def ctrac(c, nrm):
        th_ = math.atan2(c[1], c[0])
        t_tan = -T_nmm / (rc * carea)
        return np.array([-t_tan * math.sin(th_), t_tan * math.cos(th_), 0.0])
    for n, f in balanced(S.consistent_loads(ctris, P, ctrac)).items():
        forces[n] = forces.get(n, 0) + f
    if os.environ.get("WQ_FEA_DEBUG"):
        F = np.array([forces[k] for k in forces]); Z = np.array([P[k][2] for k in forces])
        print("elements", len(tets), "nodes", len(ntags), "F", F.sum(0), "z_c", (F[:, 1] * Z).sum() / F[:, 1].sum(), "ntris", len(tris), flush=True)
    mat = {"E_mpa": 210000.0, "nu": 0.3, "density_t_mm3": 7.85e-9}
    with tempfile.TemporaryDirectory() as d:
        inp = os.path.join(d, "job.inp")
        S.write_inp(inp, ntags, xyz, tets, set(), sup, forces, mat)
        eq = ""
        for dof in (2, 3):                                 # 节点在柱坐标系里：2 切向（消去绕轴转动），3 轴向（消去轴向平移）
            terms = [f"{n},{dof},1." for n in ring]
            eq += "*EQUATION\n" + f"{len(terms)}\n" + "".join(",".join(terms[i:i + 4]) + "\n" for i in range(0, len(terms), 4))
        txt = open(inp).read()
        txt = txt.replace("*STEP", eq + "*STEP", 1)
        # 两个轴承环的支反力合力（.dat 文件），用来与手算的支反力核对
        txt = txt.replace("*NODE FILE", "*NODE PRINT, NSET=CYL1, TOTALS=ONLY\nRF\n*NODE PRINT, NSET=CYL2, TOTALS=ONLY\nRF\n*NODE FILE")
        open(inp, "w").write(txt)
        r = subprocess.run([S.CCX, "-i", "job"], cwd=d, capture_output=True, text=True, timeout=280,
                           env={**os.environ, "OMP_NUM_THREADS": "2"})
        if not os.path.exists(os.path.join(d, "job.frd")):
            raise RuntimeError("CalculiX 失败：" + (r.stdout + r.stderr)[-400:])
        _, stress = S.read_frd(os.path.join(d, "job.frd"))
        dat = open(os.path.join(d, "job.dat")).read().split("total force")[1:]
        reactions = [np.array([float(x) for x in b.splitlines()[2].split()]) for b in dat[:2]]
        if os.environ.get("WQ_FEA_DEBUG"):
            import shutil
            shutil.copytree(d, "/tmp/claude-0/-home-claude-wenquest/649b9060-6d10-5ae5-ac04-a799ea7157ff/scratchpad/feadbg", dirs_exist_ok=True)
    surf = set()
    for dm, t in gmsh.model.getEntities(2):
        bb = gmsh.model.getBoundingBox(2, t)
        if gmsh.model.getType(2, t) == "Plane" and (abs(bb[5]) < 1e-6 or abs(bb[2] - lay[-1][1]) < 1e-6):
            continue                                    # 两端面不算
        surf |= {int(n) for n in gmsh.model.mesh.getNodes(2, t, includeBoundary=True)[0]}
    rows = []
    for n in sorted(surf):
        if n in stress:
            p = P[n]
            rows.append((p[2], math.hypot(p[0], p[1]), math.atan2(p[1], p[0]), S.von_mises(stress[n])))
    return np.array(rows), int(len(tets)), reactions
