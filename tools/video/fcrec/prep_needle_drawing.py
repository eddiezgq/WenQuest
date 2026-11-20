"""第 17 课的零件文件：整机的针杆 STEP，下端放到原点（model/针杆零件.FCStd、model_en/NeedleBarPart.FCStd）。  LC_ALL=C.UTF-8 freecadcmd prep_needle_drawing.py"""
import FreeCAD as App, Part, os
R=os.environ["WQ_REC"]; D=os.environ["WQLS_TE"]
s=Part.read(D+"/needle_bar.step")
s.translate(App.Vector(0,0,-42.5))   # 下端放到原点
for sub,lab,fn in (("model","针杆","针杆零件"),("model_en","NeedleBar","NeedleBarPart")):
    doc=App.newDocument("NB"); o=doc.addObject("Part::Feature","NeedleBar"); o.Label=lab; o.Shape=s
    doc.saveAs(f"{R}/{sub}/{fn}.FCStd"); App.closeDocument(doc.Name)
print("ok", s.BoundBox)
