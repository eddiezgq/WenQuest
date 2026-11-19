"""英文版整机：model/WQ-LS.FCStd → model_en/WQ-LS.FCStd，部件组名和文件标签换成英文（录英文界面的录屏用）。"""
import os
import FreeCAD as App
R = os.environ["WQ_REC"]
EN = {"机壳": "Housing", "主轴与挑线": "Upper shaft & take-up", "勾线与下轴": "Hook & lower shaft", "送布与抬牙": "Feed & lift",
      "压脚": "Presser", "剪线与拨线": "Trimmer & wiper", "电机": "Motor", "润滑": "Lubrication"}
os.makedirs(os.path.join(R, "model_en"), exist_ok=True)
doc = App.openDocument(os.path.join(R, "model", "WQ-LS.FCStd"))
doc.Label = "WQ-LS lockstitch machine"
for o in doc.Objects:
    if o.TypeId == "App::DocumentObjectGroup":
        o.Label = EN[o.Label]
doc.saveAs(os.path.join(R, "model_en", "WQ-LS.FCStd"))
print("OK", [o.Label for o in doc.Objects if o.TypeId == "App::DocumentObjectGroup"])
