# -*- coding: utf-8 -*-
"""问渠缝纫机工作台：在 FreeCAD 本机做零件有限元（第 49 轮，帮助“复杂 CAE 快速上手”的本机算例）。

用 FreeCAD 自带的 Gmsh（网格）和 CalculiX（求解）——和问渠服务器上“CAE 分析”页签是同一类开源求解器。
零件、支承孔、受力孔、力的大小和方向，和网页版“CAE 分析 → 零件强度”完全一样（同一份 cae_setup.fea_case）：
一转里连杆力最大的那一刻，轴孔固定，销孔加力。建好后是一套普通的 FreeCAD 有限元分析（模型树里的“分析”），
可以切到 FEM 工作台自己改约束、载荷、网格再算。

控制台用法（先选中或新建一个平缝机 / 包缝机设计）：
    import wqsew_fem
    r = wqsew_fem.run()                          # 针杆曲柄（平缝机）
    r = wqsew_fem.run(part="ConnectingRod")      # 针杆连杆
"""
import math

import FreeCAD as App

import wqsew_feature as F
from sewcore import cad, cae_setup as CS

# 材料：E（MPa）、泊松比、密度（kg/m³）、屈服强度（MPa）——与问渠数字工厂材料库一致
MAT = {"45-QT": ("45 钢（调质）", 210000, 0.30, 7850, 355), "40Cr-QT": ("40Cr（调质）", 210000, 0.30, 7850, 540),
       "QT500-7": ("QT500-7 球墨铸铁", 169000, 0.275, 7100, 320), "6061-T6": ("6061-T6 铝合金", 68900, 0.33, 2700, 276),
       "7075-T6": ("7075-T6 铝合金", 71700, 0.33, 2810, 503)}


def _hole_face(shape, h):
    """零件上与这个孔（圆心、半径）对应的圆柱面名"""
    ax = [abs(x) for x in h["axis"]]
    k = ax.index(max(ax))                      # 孔轴沿哪个坐标轴
    for i, f in enumerate(shape.Faces):
        s = f.Surface
        if s.__class__.__name__ == "Cylinder" and abs(s.Radius - h["r"]) < 0.05:
            c = [s.Center.x, s.Center.y, s.Center.z]
            if all(abs(c[j] - h["center"][j]) < 0.05 for j in range(3) if j != k):
                return "Face%d" % (i + 1)
    raise ValueError("没找到孔面（半径 %.2f）" % h["r"])


def run(obj=None, part="", mesh_mm=1.2, solve=True, workdir=None):
    """返回 dict：最大等效应力、最大位移、安全系数、节点数、单元数；FreeCAD 里新开一个文档放这套分析"""
    import ObjectsFem
    obj = obj or _design()
    M = F.SewDesign.machine(obj)
    p = obj.Proxy.params(obj)
    part = part or ("NeedleCrank" if M.MACHINE == "lockstitch" else "OL_NeedleCrank")
    case = CS.fea_case(M.MACHINE, p, part)
    if not case:
        raise ValueError("这个机型没有这个零件的有限元算例：" + part)
    mid = p.get("mat", "45-QT")
    mname, E, nu, rho, sy = MAT.get(mid, MAT["45-QT"])
    doc = App.newDocument("FEM_" + part)
    name, zh, shape, _c = cad.freecad_shapes({"parts": [case["descriptor"]]})[0]
    body = doc.addObject("Part::Feature", part)
    body.Shape = shape
    body.Label = zh
    doc.recompute()
    an = ObjectsFem.makeAnalysis(doc, "Analysis")
    an.Label = "分析：" + zh
    sol = ObjectsFem.makeSolverCalculiXCcxTools(doc)
    an.addObject(sol)
    mat = ObjectsFem.makeMaterialSolid(doc, "Material")
    mat.Material = {"Name": mname, "YoungsModulus": "%g MPa" % E, "PoissonRatio": str(nu), "Density": "%g kg/m^3" % rho}
    an.addObject(mat)
    fix = ObjectsFem.makeConstraintFixed(doc, "Support")
    fix.References = [(body, _hole_face(body.Shape, case["support"]))]
    fix.Label = "支承孔固定"
    an.addObject(fix)
    v = case["vector_n"]
    L = math.sqrt(sum(x * x for x in v)) or 1.0
    ln = doc.addObject("Part::Line", "ForceDirection")
    ln.X2, ln.Y2, ln.Z2 = 10 * v[0] / L, 10 * v[1] / L, 10 * v[2] / L
    ln.Visibility = False
    doc.recompute()
    fo = ObjectsFem.makeConstraintForce(doc, "Load")
    fo.References = [(body, _hole_face(body.Shape, case["load"]))]
    fo.Force = "%.3f N" % L
    fo.Direction = (ln, ["Edge1"])
    fo.Label = "受力孔：%.0f N（一转里最大，主轴转角 %d°）" % (L, case["phi"])
    an.addObject(fo)
    me = ObjectsFem.makeMeshGmsh(doc, "Mesh")
    me.Shape = body
    me.CharacteristicLengthMax = mesh_mm
    me.ElementOrder = "2nd"
    me.HighOrderOptimize = "Optimization"    # 二阶网格优化：薄件、小孔也不出现畸形单元
    an.addObject(me)
    doc.recompute()
    from femmesh.gmshtools import GmshTools
    GmshTools(me).create_mesh()
    out = {"part": zh, "force_n": round(L, 1), "phi": case["phi"], "material": mname, "nodes": me.FemMesh.NodeCount,
           "elements": me.FemMesh.VolumeCount}
    if not solve:
        return out
    from femtools import ccxtools
    fea = ccxtools.FemToolsCcx(an, sol)
    fea.purge_results()
    fea.update_objects()
    fea.setup_working_dir(workdir) if workdir else fea.setup_working_dir()
    fea.setup_ccx()
    msg = fea.check_prerequisites()
    if msg:
        raise RuntimeError(msg)
    fea.write_inp_file()
    fea.ccx_run()
    fea.load_results()
    res = [o for o in doc.Objects if o.isDerivedFrom("Fem::FemResultObject")][0]
    smax = max(res.vonMises)
    out.update(vm_max_mpa=round(smax, 1), disp_max_mm=round(max(res.DisplacementLengths), 5), yield_mpa=sy,
               sf=round(sy / smax, 1) if smax > 0 else None)
    try:
        import FreeCADGui as Gui
        import femresult.resulttools as rt  # noqa: F401
        me.ViewObject.setNodeColorByScalars(list(res.NodeNumbers), list(res.vonMises))
        me.ViewObject.Visibility = True
        body.ViewObject.Visibility = False
        Gui.SendMsgToActiveView("ViewFit")
    except Exception:  # noqa: BLE001
        pass
    return out


def _design():
    doc = App.ActiveDocument
    for o in (doc.Objects if doc else []):
        if getattr(o, "Proxy", None).__class__.__name__ == "SewDesign":
            return o
    raise ValueError("先新建一个平缝机或包缝机设计")
