"""第 20 课的练习文件（中英两套）：
  圆角练习 / FilletTest：实体（Body）里一个 20 mm 方块
  草图冗余 / SketchRedundant：30×20 矩形，两边各一个竖直尺寸（第二个是多余的）
  失败重算 / RecomputeAfterFail：方块 20 → 圆角 2（Part 工作台）→ 挖一个 ⌀6 孔
WQ_REC=… freecadcmd prep_l20.py"""
import os

import FreeCAD as App
import Part
import Sketcher

V = App.Vector
R = os.environ["WQ_REC"]

for sub, names in (("model", ("圆角练习", "草图冗余", "失败重算")), ("model_en", ("FilletTest", "SketchRedundant", "RecomputeAfterFail"))):
    d = App.newDocument("FilletTest")
    body = d.addObject("PartDesign::Body", "Body")
    bx = body.newObject("PartDesign::AdditiveBox", "Box")
    bx.Length = bx.Width = bx.Height = 20
    d.recompute()
    d.saveAs(os.path.join(R, sub, names[0] + ".FCStd"))
    App.closeDocument(d.Name)

    d = App.newDocument("SketchRedundant")
    sk = d.addObject("Sketcher::SketchObject", "Sketch")
    pts = [V(0, 0, 0), V(30, 0, 0), V(30, 20, 0), V(0, 20, 0)]
    for i in range(4):
        sk.addGeometry(Part.LineSegment(pts[i], pts[(i + 1) % 4]))
    for i in range(4):
        sk.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % 4, 1))
    for c in (("Horizontal", 0), ("Horizontal", 2), ("Vertical", 1), ("Vertical", 3)):
        sk.addConstraint(Sketcher.Constraint(*c))
    sk.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 0, 2, 30))
    sk.addConstraint(Sketcher.Constraint("DistanceY", 1, 1, 1, 2, 20))
    sk.addConstraint(Sketcher.Constraint("DistanceY", 3, 2, 3, 1, 20))     # 多余的：左右两边一样高，已经由水平、竖直保证
    sk.addConstraint(Sketcher.Constraint("Coincident", 0, 1, -1, 1))
    d.recompute()
    d.saveAs(os.path.join(R, sub, names[1] + ".FCStd"))
    App.closeDocument(d.Name)

    d = App.newDocument("RecomputeAfterFail")
    bx = d.addObject("Part::Box", "Box")
    bx.Length = bx.Width = bx.Height = 20
    fl = d.addObject("Part::Fillet", "Fillet")
    fl.Base = bx
    fl.Edges = [(i + 1, 2.0, 2.0) for i in range(12)]
    hole = d.addObject("Part::Cylinder", "Hole")
    hole.Radius = 3
    hole.Height = 30
    hole.Placement.Base = V(10, 10, -5)
    cut = d.addObject("Part::Cut", "Cut")
    cut.Base = fl
    cut.Tool = hole
    d.recompute()
    d.saveAs(os.path.join(R, sub, names[2] + ".FCStd"))
    App.closeDocument(d.Name)
    print(sub, "ok")
