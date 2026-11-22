"""第 19 课的零件文件：针杆曲柄（第 178 轮打通紧定螺孔以后的 cad/mech.py 输出 crank.step）+ 两条辅助线
（力的方向：从曲柄销中心指向轴心；转轴：上轴轴线）。  WQ_CRANK=<crank.step> freecadcmd prep_crank_fea.py"""
import FreeCAD as App, Part, os
R = os.environ["WQ_REC"]
src = os.environ.get("WQ_CRANK", f"{R}/crank_r178.step")
shape = Part.read(src)
for sub, name, lab, dlab, alab in (("model", "针杆曲柄", "针杆曲柄", "力的方向", "转轴"),
                                   ("model_en", "NeedleBarCrank", "NeedleBarCrank", "ForceDirection", "SpinAxis")):
    doc = App.newDocument("NeedleBarCrank")
    o = doc.addObject("Part::Feature", "Crank"); o.Label = lab; o.Shape = shape
    d = doc.addObject("Part::Line", "ForceDir"); d.Label = dlab
    d.X1, d.Y1, d.Z1, d.X2, d.Y2, d.Z2 = 32, 0, 215.5, 32, 0, 200          # 曲柄销中心 → 轴心（φ = 0：销在上）
    a = doc.addObject("Part::Line", "Axis"); a.Label = alab
    a.X1, a.Y1, a.Z1, a.X2, a.Y2, a.Z2 = 20, 0, 200, 45, 0, 200              # 上轴轴线（x 向）
    doc.recompute()
    doc.saveAs(f"{R}/{sub}/{name}.FCStd"); App.closeDocument(doc.Name)
    print(sub, name, round(shape.Volume, 1), len(shape.Faces))
