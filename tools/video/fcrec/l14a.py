"""第 14 课 片段 A：曲面到实体——交集 + 圆角已经是封闭实体；选底面，Part“抽壳”4 mm（铸件壁厚）。真操作。（“检查几何”问渠 CAD 和官方结果不同，按规矩不录屏，课文里讲。）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FreeCAD as App, FreeCADGui as Gui, Part
from director import Director, boot, log, Qt, QtWidgets, L, model_file
import steps


def script(d):
    doc = App.openDocument(model_file("机头曲面.FCStd", "HeadSurface.FCStd"))
    fil = [o for o in doc.Objects if o.TypeId == "Part::Fillet"][-1]
    sh = fil.Shape
    log("closed", sh.ShapeType, len(sh.Solids), len(sh.Shells), sh.Shells[0].isClosed(), sh.isValid(), round(sh.Volume, 1))
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit")
    yield 1200
    yield from steps.pick_workbench(d, "Part", "Part")
    yield d.say("曲面到实体：上一课修剪、过渡以后，这些面已经缝成一个封闭的壳，围成了一个实体（软件算得出体积）")
    yield 2500
    yield d.say("真机头是铸件：壁厚 4 mm、底下开口。翻到底面，选中它，点 Part 的“抽壳”")
    Gui.runCommand("Std_ViewBottom"); Gui.SendMsgToActiveView("ViewFit"); yield 1200
    bi = [i for i, f in enumerate(sh.Faces) if f.Surface.TypeId == "Part::GeomPlane" and abs(f.Surface.Axis.z) > 0.99
          and f.BoundBox.ZMax < 125][0]
    c = sh.Faces[bi].CenterOfMass
    p = d.model_pt(c.x, c.y, c.z)
    yield d.move(p, 900)
    d.click(p); yield 700
    log("sel", [s.SubElementNames for s in Gui.Selection.getSelectionEx()], "want", f"Face{bi + 1}")
    if not Gui.Selection.getSelectionEx() or f"Face{bi + 1}" not in Gui.Selection.getSelectionEx()[0].SubElementNames:
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(doc.Name, fil.Name, f"Face{bi + 1}")
    yield d.tool("Part_CompOffsetTools", "Part_Thickness") if d.action_widget("Part_CompOffsetTools") else d.tool("Part_Thickness")
    yield from d.until(lambda: any(isinstance(w, QtWidgets.QAbstractSpinBox) and w.isVisible() and w.window() is d.mw and "ffset" in w.objectName()
                                   for w in QtWidgets.QApplication.allWidgets()), 10000)
    yield 1200
    log("thick widgets", [(w.objectName(), w.text() if hasattr(w, "text") else "") for w in QtWidgets.QApplication.allWidgets()
                          if w.isVisible() and w.objectName() and isinstance(w, (QtWidgets.QAbstractSpinBox, QtWidgets.QCheckBox, QtWidgets.QComboBox))][:15])
    w = [w for w in QtWidgets.QApplication.allWidgets() if isinstance(w, QtWidgets.QAbstractSpinBox) and w.isVisible() and "ffset" in w.objectName()][0]
    yield from steps.type_into(d, w, "-4 mm")
    yield 1500
    yield from steps.task_ok(d, gone=w.objectName())
    th = [o for o in doc.Objects if o.TypeId == "Part::Thickness"]
    doc.recompute()
    log("thickness", len(th), th and [th[-1].Value, round(th[-1].Shape.Volume, 1), th[-1].Shape.isValid()])
    Gui.runCommand("Std_ViewBottom"); Gui.SendMsgToActiveView("ViewFit"); yield 1500
    yield d.say("向里抽了 4 mm 的壳，底面开口。负的厚度是向里长，外形尺寸不变")
    yield 2500
    Gui.runCommand("Std_ViewIsometric"); Gui.SendMsgToActiveView("ViewFit"); yield 800
    yield d.say("交给别人加工、做模具之前，再用“检查几何”查一遍有没有坏面和缝隙（见课文）")
    yield 2500
    doc.save()
    yield 300


def main():
    d = Director()
    d.run(script(d))


boot(main)
