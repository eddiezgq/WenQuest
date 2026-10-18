# -*- coding: utf-8 -*-
"""问渠缝纫机工作台：“平缝机设计”参数化对象（不依赖图形界面，freecadcmd 里也能用）。

对象的属性就是设计参数（分组同网页版）；重新计算时调用计算核心 sewcore.analyze()，
把校核结果写进只读属性，并按 sewcore.cad.parts3d() 更新各零件（Part::Feature 子对象）的形状。
"""
import json
import os
import sys

import FreeCAD as App

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import sewcore  # noqa: E402
from sewcore import cad  # noqa: E402

PROP = "App::PropertyFloat"


def _pname(k):
    return "P_" + k


def add_design(doc=None, params=None, label=None, machine="lockstitch"):
    doc = doc or App.ActiveDocument or App.newDocument("WenQuestSewing")
    obj = doc.addObject("App::FeaturePython", "SewDesign")
    SewDesign(obj, params, machine)
    obj.Label = label or (sewcore.get(machine).NAME[0] + "设计")
    try:
        import FreeCADGui  # noqa: F401
        ViewProviderSewDesign(obj.ViewObject)
    except Exception:
        pass
    doc.recompute()
    return obj


class SewDesign:
    def __init__(self, obj, params=None, machine="lockstitch"):
        M = sewcore.get(machine)
        p = M.clean(params)
        obj.addProperty("App::PropertyString", "Machine", "机型", "lockstitch 平缝机 / overlock 包缝机 / cover 绷缝机")
        obj.Machine = M.MACHINE
        obj.setEditorMode("Machine", 1)
        for g, gzh, gen, items in M.GROUPS:
            for k, zh, en, unit, d, lo, hi, st in items:
                tip = "{}（{}）{}".format(zh, en, " 单位 " + unit if unit else "")
                if k in M.CHOICES:
                    obj.addProperty("App::PropertyEnumeration", _pname(k), gzh, tip)
                    setattr(obj, _pname(k), [c[0] for c in M.CHOICES[k]])
                    setattr(obj, _pname(k), p[k])
                else:
                    obj.addProperty(PROP, _pname(k), gzh, tip)
                    setattr(obj, _pname(k), float(p[k]))
        obj.addProperty("App::PropertyAngle", "Phi", "显示", "零件摆放时的主轴转角（0° = 针杆上止点）")
        obj.addProperty("App::PropertyLinkList", "Parts", "零件", "机构零件")
        obj.addProperty("App::PropertyString", "Status", "结果", "校核结论")
        obj.addProperty("App::PropertyString", "ResultJson", "结果", "计算结果（JSON）")
        obj.setEditorMode("ResultJson", 2)
        obj.setEditorMode("Status", 1)
        obj.setEditorMode("Parts", 1)
        obj.Proxy = self

    @staticmethod
    def machine(obj):
        return sewcore.get(getattr(obj, "Machine", "lockstitch") or "lockstitch")

    def params(self, obj):
        M = self.machine(obj)
        p = {}
        for k in M.PARAMS:
            v = getattr(obj, _pname(k), None)
            if v is not None:
                p[k] = v
        return M.clean(p)

    def execute(self, obj):
        p = self.params(obj)
        R = self.machine(obj).analyze(p)
        bad = [c for c in R["checks"] if c["state"] == "bad"]
        warn = [c for c in R["checks"] if c["state"] == "warn"]
        obj.Status = "全部合格" if not bad and not warn else "不合格 {} 项，注意 {} 项".format(len(bad), len(warn))
        keep = {k: R[k] for k in ("machine", "params", "results", "checks", "timing", "trial", "chain", "tables", "ok", "version", "key") if k in R}
        obj.ResultJson = json.dumps(keep, ensure_ascii=False)
        self.update_parts(obj, p, float(obj.Phi.Value if hasattr(obj.Phi, "Value") else obj.Phi))

    def update_parts(self, obj, p, phi):
        doc = obj.Document
        if self.machine(obj).MACHINE not in ("lockstitch", "overlock"):
            return                      # 绷缝机第一期只有计算与校核，没有零件（第 40 轮 Q2）
        model = cad.parts3d(p, phi, self.machine(obj).MACHINE)
        have = {getattr(o, "SewKey", ""): o for o in (obj.Parts or [])}
        out = []
        for name, zh, shape, color in cad.freecad_shapes(model):
            o = have.get(name)
            if o is None or o.Document is None:
                o = doc.addObject("Part::Feature", "Sew_" + name)
                o.addProperty("App::PropertyString", "SewKey", "问渠", "零件代号")
                o.SewKey = name
                o.setEditorMode("SewKey", 1)
                o.Label = zh
                try:
                    o.ViewObject.ShapeColor = color
                except Exception:
                    pass
            o.Shape = shape
            o.purgeTouched()
            out.append(o)
        if [x.Name for x in out] != [x.Name for x in (obj.Parts or [])]:
            obj.Parts = out

    def onChanged(self, obj, prop):
        pass

    def dumps(self):
        return None

    def loads(self, state):
        return None


class ViewProviderSewDesign:
    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        self.Object = vobj.Object

    def claimChildren(self):
        return list(getattr(self.Object, "Parts", []) or [])

    def getIcon(self):
        return os.path.join(HERE, "wqsew.svg")

    def doubleClicked(self, vobj):
        try:
            import wqsew_gui
            wqsew_gui.show_checks(vobj.Object)
        except Exception as e:  # noqa: BLE001
            App.Console.PrintError("问渠缝纫机：{}\n".format(e))
        return True

    def dumps(self):
        return None

    def loads(self, state):
        return None


def result(obj):
    return json.loads(obj.ResultJson or "{}")


def export_params(obj, path):
    p = obj.Proxy.params(obj)
    M = SewDesign.machine(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"format": "wenquest-sewing", "machine": M.MACHINE, "version": M.VERSION, "project": obj.Label, "params": p},
                  f, ensure_ascii=False, indent=1)


def import_params(obj, path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    M = SewDesign.machine(obj)
    if d.get("machine", "lockstitch") != M.MACHINE:
        raise ValueError("参数文件是{}的，这个设计是{}的。请先新建对应机型的设计再导入。".format(
            sewcore.get(d.get("machine")).NAME[0], M.NAME[0]))
    p = M.clean(d.get("params") or d)
    for k, v in p.items():
        setattr(obj, _pname(k), v if k in M.CHOICES else float(v))
    if d.get("project"):
        obj.Label = d["project"]
    obj.Document.recompute()


def export_step(obj, path):
    import Import
    Import.export(list(obj.Parts), path)
