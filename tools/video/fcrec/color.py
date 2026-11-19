import os
import FreeCAD as App, FreeCADGui as Gui
from PySide import QtCore, QtGui
R=os.environ.get("WQ_REC", ".") + "/"
COL = {"机壳": (0.80,0.82,0.80), "主轴与挑线": (0.72,0.74,0.78), "勾线与下轴": (0.85,0.65,0.25), "送布与抬牙": (0.35,0.55,0.80),
       "压脚": (0.55,0.75,0.45), "剪线与拨线": (0.80,0.40,0.35), "电机": (0.25,0.27,0.30), "润滑": (0.90,0.80,0.35)}
def go():
  try:
    doc = App.openDocument(R+"model/WQ-LS.FCStd")
    for g in doc.Objects:
        if g.TypeId == "App::DocumentObjectGroup":
            c = COL[g.Label]; g.Visibility = True
            for o in g.Group:
                o.Visibility = True
                vo = o.ViewObject
                vo.ShapeColor = c
                if o.Name in ("bed", "head"):
                    vo.Transparency = 55; vo.DisplayMode = "Shaded"
    doc.save()
    QtCore.QTimer.singleShot(1500, lambda: os._exit(0))
    return
    v = Gui.ActiveDocument.ActiveView; v.viewIsometric(); Gui.SendMsgToActiveView("ViewFit")
    QtCore.QTimer.singleShot(2500, lambda: (Gui.getMainWindow().grab().save(R+"model.png"), QtGui.QApplication.instance().quit()))
  except Exception:
    import traceback; traceback.print_exc(); App.closeDocument('WQ_LS'); QtGui.QApplication.instance().quit()
QtCore.QTimer.singleShot(8000, go)
