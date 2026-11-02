"""10.5 断裂力学入门：应力强度因子与断裂韧度；用有限元求 K。

算例 10.5.1  单边裂纹板（钢，宽 W = 100、高 2H = 400，裂纹长 a，远处拉应力 σ = 100 MPa）。平面应力有限元：gmsh 二阶三角形网格、
            裂纹尖端加密，CalculiX 求解（与 CAE 同一个求解器），取上半板（对称），由裂纹面张开位移 v(r) 外推求 K：
            K = (E v / 4)·√(2π / r)，r → 0；a/W = 0.1–0.5 五种，与手册的 Y(a/W) 公式（Tada）对照；
算例 10.5.2  “先屈服还是先断裂”：表面裂纹 Y ≈ 1.12，应力达到屈服强度时会断的裂纹深度 a_t = (K_IC / (1.12 σs))² / π，比较
            6061-T6、7075-T6、45 钢调质、40Cr 调质、HT200（K_IC 取手册典型值，材料库没有）；再看 WQ-CR5 大臂在 5 kg 静载下的最大应力
            （程序 10.2.1 的同一次有限元）、RJ-201 在瞬时允许最大转矩下花键段的表面切应力（按主应力 σ1 = τ），临界裂纹深度、
            裂纹穿透大臂壁厚（3 mm）或在 RJ-201 表面深 1 mm 时的 K 与 K_IC 之比；
图 10.5.1。
"""
import math
import os
import subprocess
import tempfile

import numpy as np

import _ch10 as H
from bookout import T, figure, out, style
from cae.geometry import _LOCK, _gmsh

ST = H.mat("45-QT")
E, NU = ST["E_mpa"], ST["nu"]
W, HH, SIG = 100.0, 200.0, 100.0


def y_tada(al):
    """单边裂纹板（H/W ≥ 1）的形状系数，Tada《应力分析手册》，a/W ≤ 0.6 误差约 0.5%"""
    return 1.12 - 0.231 * al + 10.55 * al ** 2 - 21.72 * al ** 3 + 30.39 * al ** 4


def k_fe(a, h_tip=None):
    """上半板：y = 0 上 x < a 为裂纹面（自由），x > a 为对称面（v = 0）；顶边 y = HH 均匀拉伸 SIG。返回 (K, 外推用的 r, K(r))"""
    h_tip = h_tip or a / 200
    with _LOCK, tempfile.TemporaryDirectory() as tmp:
        g = _gmsh()
        g.clear()
        g.model.add("crack")
        occ = g.model.occ
        p = [occ.addPoint(0, 0, 0), occ.addPoint(a, 0, 0), occ.addPoint(W, 0, 0), occ.addPoint(W, HH, 0), occ.addPoint(0, HH, 0)]
        ln = [occ.addLine(p[0], p[1]), occ.addLine(p[1], p[2]), occ.addLine(p[2], p[3]), occ.addLine(p[3], p[4]), occ.addLine(p[4], p[0])]
        occ.addPlaneSurface([occ.addCurveLoop(ln)])
        occ.synchronize()
        f = g.model.mesh.field
        d = f.add("Distance")
        f.setNumbers(d, "PointsList", [p[1]])
        th = f.add("Threshold")
        f.setNumber(th, "InField", d)
        f.setNumber(th, "SizeMin", h_tip)
        f.setNumber(th, "SizeMax", W / 15)
        f.setNumber(th, "DistMin", a / 40)
        f.setNumber(th, "DistMax", 0.8 * a + 5)
        f.setAsBackgroundMesh(th)
        g.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        g.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        g.option.setNumber("Mesh.ElementOrder", 2)
        g.option.setNumber("Mesh.MaxNumThreads2D", 1)
        g.model.mesh.generate(2)
        nt, xyz, _ = g.model.mesh.getNodes()
        xyz = np.asarray(xyz).reshape(-1, 3)
        P = {int(t): xyz[i] for i, t in enumerate(nt)}
        et, _, en = g.model.mesh.getElements(2)
        tri = np.asarray(en[list(et).index(9)], np.int64).reshape(-1, 6)

        def edge_nodes(line):
            return {int(x) for x in g.model.mesh.getNodes(1, line, includeBoundary=True)[0]}
        crack, lig, top = edge_nodes(ln[0]), edge_nodes(ln[1]), ln[3]
        _, _, ten = g.model.mesh.getElements(1, top)
        top3 = np.asarray(ten[0], np.int64).reshape(-1, 3)                  # 二阶线单元：两端点 + 中点
        g.clear()
    F = {}
    for e in top3:
        L = abs(P[int(e[0])][0] - P[int(e[1])][0])
        for n, w in zip(e, (1 / 6, 1 / 6, 4 / 6)):
            F[int(n)] = F.get(int(n), 0.0) + SIG * L * w                    # 厚度取 1
    corner = min(lig, key=lambda n: -P[n][0])                                # x = W、y = 0 的节点：限制 x 向刚体移动
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "k.inp"), "w") as w:
            w.write("*NODE\n")
            for n, q in P.items():
                w.write(f"{n},{q[0]:.9g},{q[1]:.9g}\n")
            w.write("*ELEMENT,TYPE=CPS6,ELSET=E\n")
            for i, e in enumerate(tri, 1):
                w.write(f"{i}," + ",".join(str(int(x)) for x in e) + "\n")
            w.write(f"*MATERIAL,NAME=M\n*ELASTIC\n{E},{NU}\n*SOLID SECTION,ELSET=E,MATERIAL=M\n1.\n")
            w.write("*BOUNDARY\n" + "".join(f"{n},2,2,0.\n" for n in sorted(lig)) + f"{corner},1,1,0.\n")
            w.write("*STEP\n*STATIC\n*CLOAD\n" + "".join(f"{n},2,{v:.9g}\n" for n, v in F.items()) + "*NODE FILE\nU\n*END STEP\n")
        subprocess.run([H.S.CCX, "-i", "k"], cwd=tmp, capture_output=True, text=True, timeout=600)
        disp, _ = H.S.read_frd(os.path.join(tmp, "k.frd"))
    rs, ks = [], []
    for n in crack:
        r = a - P[n][0]
        if 0.02 * a < r < 0.25 * a:
            v = disp[n][1]
            rs.append(r)
            ks.append(E * v / 4 * math.sqrt(2 * math.pi / r))
    rs, ks = np.array(rs), np.array(ks)
    c = np.polyfit(rs, ks, 1)                                                # K(r) ≈ K + c·r，外推到 r = 0
    return c[1], rs, ks, len(tri)


ALS = [0.1, 0.2, 0.3, 0.4, 0.5]
res = []
for al in ALS:
    a = al * W
    K, rs, ks, n_el = k_fe(a)
    Y_fe = K / (SIG * math.sqrt(math.pi * a))
    res.append((al, a, K, Y_fe, y_tada(al), n_el, rs, ks))
err = max(abs(r[3] / r[4] - 1) for r in res) * 100

# ---------------------------------------------------------------- 算例 10.5.2
KIC = {"6061-T6": 29.0, "7075-T6": 27.0, "45-QT": 60.0, "40Cr-QT": 70.0, "HT200": 18.0}    # MPa·√m，手册典型值（量级），本书取值
NAMES = {"6061-T6": T("6061-T6 铝", "6061-T6 Al"), "7075-T6": T("7075-T6 铝", "7075-T6 Al"), "45-QT": T("45 钢调质", "1045 Q&T"),
         "40Cr-QT": T("40Cr 调质", "40Cr Q&T"), "HT200": T("HT200 铸铁", "HT200 cast iron")}
at = {}
for k, kic in KIC.items():
    m = H.mat(k)
    sref = m["yield_mpa"] or m["ultimate_mpa"]
    at[k] = (kic / (1.12 * sref)) ** 2 / math.pi * 1e3          # mm
# WQ-CR5 大臂、RJ-201 的临界裂纹深度（工作应力下）
_, step, _, loads, _ = H.upper_arm()
st, _, _, _ = H.fe_solve(step, loads, 7.0, H.mat("6061-T6"))
sig_arm = st["vm_max_mpa"]
a_arm = (KIC["6061-T6"] / (1.12 * sig_arm)) ** 2 / math.pi * 1e3
import _rj as RJ  # noqa: E402
tau_rj = RJ.harmonic("25-100")["momentary"] * 1e3 / (2 * RJ.W_hollow(RJ.spline(RJ.SEAT)["D_ie"]))   # 花键段小径（第 33 章 33.10 节）
a_rj = (KIC["40Cr-QT"] / (1.12 * tau_rj)) ** 2 / math.pi * 1e3
# 换一个角度：裂纹一直长到穿透壁厚（大臂 3 mm）、RJ-201 表面 1 mm 深时的 K，与 K_IC 比
K_arm3 = 1.12 * sig_arm * math.sqrt(math.pi * 3e-3)
K_rj1 = 1.12 * tau_rj * math.sqrt(math.pi * 1e-3)

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
al_f = np.linspace(0.05, 0.6, 100)
a0.plot(al_f, y_tada(al_f), color="#d62728", lw=1.3, label=T("手册公式（Tada）", "handbook (Tada)"))
a0.plot([r[0] for r in res], [r[3] for r in res], "o", color="#1f77b4", ms=4, label=T("有限元（位移外推）", "FE (displacement extrapolation)"))
a0.set_xlabel("a / W", fontsize=7.0)
a0.set_ylabel(T("形状系数 Y = K / (σ√(πa))", "Geometry factor Y = K / (σ√(πa))"), fontsize=7.0)
a0.legend(fontsize=6.0, frameon=False, loc="lower right")
a0.tick_params(labelsize=6.2)
a0.set_title(T("(a) 单边裂纹板：有限元求 K", "(a) Single-edge crack: K by FE"), fontsize=7.2)
ins = a0.inset_axes([0.12, 0.40, 0.38, 0.30])
r2 = res[1]
ins.plot(r2[6] / r2[1], r2[7] / (SIG * math.sqrt(math.pi * r2[1])), ".", ms=2, color="#1f77b4")
ins.axhline(r2[3], color="#1f77b4", lw=0.6, ls="--")
ins.set_xlim(0, None)
ins.tick_params(labelsize=5.0)
ins.set_title(T("a/W = 0.2：K(r) 外推到 r = 0", "a/W = 0.2: K(r) extrapolated to r = 0"), fontsize=5.4)
ks_ = list(KIC)
a1.barh(range(len(ks_)), [at[k] for k in ks_], color=["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728", "#7f7f7f"])
for i, k in enumerate(ks_):
    a1.text(at[k] * 1.05, i, f"{at[k]:.1f} mm", va="center", fontsize=6.2)
a1.set_yticks(range(len(ks_)))
a1.set_yticklabels([NAMES[k] for k in ks_], fontsize=6.4)
a1.invert_yaxis()
a1.set_xscale("log")
a1.set_xlim(0.1, max(at.values()) * 6)
a1.set_xlabel(T("应力达到屈服（铸铁：抗拉）强度时的临界裂纹深度 / mm", "Critical depth at yield (cast iron: tensile) strength / mm"), fontsize=6.6)
a1.tick_params(labelsize=6.2)
a1.set_title(T("(b) 先屈服还是先断裂", "(b) Yield first or fracture first"), fontsize=7.2)
fig.tight_layout()
figure(fig, "fig10_5_1")

out(W=W, H2=2 * HH, SIG=SIG, err=err, n_el=res[1][5],
    Y1=res[0][3], Y2=res[1][3], Y3=res[2][3], Y4=res[3][3], Y5=res[4][3],
    Yt1=res[0][4], Yt2=res[1][4], Yt3=res[2][4], Yt4=res[3][4], Yt5=res[4][4], K2=res[1][2] / math.sqrt(1000),
    kic_61=KIC["6061-T6"], kic_75=KIC["7075-T6"], kic_45=KIC["45-QT"], kic_40=KIC["40Cr-QT"], kic_ht=KIC["HT200"],
    at_61=at["6061-T6"], at_75=at["7075-T6"], at_45=at["45-QT"], at_40=at["40Cr-QT"], at_ht=at["HT200"],
    sig_arm=sig_arm, a_arm=a_arm / 1e3, tau_rj=tau_rj, a_rj=a_rj / 1e3, t_arm=3.0, K_arm3=K_arm3, K_rj1=K_rj1,
    r_arm3=KIC["6061-T6"] / K_arm3, r_rj1=KIC["40Cr-QT"] / K_rj1)
