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
from sewcore import hotspot  # noqa: E402

RED, ORANGE = (0.86, 0.20, 0.16), (0.95, 0.55, 0.15)
SEQ = hotspot.SEQ                       # 花样机、刺绣机按针走，横机按趟走：进度角每 360° 一针 / 一趟（第 89 轮）；存在 Progress 角（Phi 是角度属性，FreeCAD 夹在 360° 以内）

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


FILE_MACHINES = ("embroid", "flatknit")


def _add_stitch_props(obj, machine="embroid"):
    tip = ("刺绣花样文件（DST 或 CSV 针位表）；“花样从哪里来”选“上传花样文件”时用" if machine == "embroid" else
           "横机意匠图（文字表 CSV / TXT，或提花色码图 PNG）；“花型从哪里来”选“上传意匠图”时用")
    if not hasattr(obj, "StitchFile"):
        obj.addProperty("App::PropertyFile", "StitchFile", "花样", tip)
        obj.StitchFile = ""
    if not hasattr(obj, "StitchData"):
        obj.addProperty("App::PropertyString", "StitchData", "花样", "从网页版导入的花样（JSON）；选了文件时以文件为准")
        obj.setEditorMode("StitchData", 2)


def _set_stitch_data(obj, p):
    keep = {k: p[k] for k in ("dst", "pts", "knit", "kpng", "fname") if k in p}
    obj.StitchData = json.dumps(keep) if keep else ""


def _stitch_params(obj, machine="embroid"):
    """花样文件路径优先；没有就用导入时存下的花样"""
    import base64
    path = getattr(obj, "StitchFile", "") or ""
    if path and os.path.isfile(path):
        with open(path, "rb") as f:
            raw = f.read()
        name = os.path.basename(path)
        low = path.lower()
        if machine == "flatknit":
            if low.endswith(".png"):
                return {"kpng": base64.b64encode(raw).decode(), "fname": name}
            return {"knit": raw.decode("utf-8", "replace"), "fname": name}
        if low.endswith(".dst"):
            return {"dst": base64.b64encode(raw).decode(), "fname": name}
        return {"pts": raw.decode("utf-8", "replace"), "fname": name}
    try:
        return json.loads(getattr(obj, "StitchData", "") or "{}")
    except ValueError:
        return {}


PHI_TIP = {"lockstitch": "零件摆放时的主轴转角（0° = 针杆上止点）",
           "pattern": "这一针里的转角（第几针见“进度”；改“进度角”跳到别的针）",
           "embroid": "这一针里的转角（第几针见“进度”；改“进度角”跳到别的针）",
           "flatknit": "这一趟里的进度（第几趟见“进度”；改“进度角”跳到别的趟）"}


def get_phi(obj):
    """零件摆放的位置：主轴机型是主轴转角；花样、刺绣、横机是进度角（可以远大于 360°）"""
    if getattr(obj, "Machine", "") in SEQ and hasattr(obj, "ProgressAngle"):
        return float(obj.ProgressAngle)
    return float(obj.Phi.Value if hasattr(obj.Phi, "Value") else obj.Phi)


def set_phi(obj, phi):
    if getattr(obj, "Machine", "") in SEQ:
        _ensure_props(obj)
        obj.ProgressAngle = float(phi)
    obj.Phi = float(phi) % 360.0


def _ensure_props(obj):
    """第 94 轮新加的属性：老文件打开时补上"""
    if not hasattr(obj, "HotJson"):
        obj.addProperty("App::PropertyString", "HotJson", "结果", "红黄灯对应的部件、停的地方（JSON）")
        obj.setEditorMode("HotJson", 2)
    if getattr(obj, "Machine", "") in SEQ and not hasattr(obj, "Progress"):
        obj.addProperty("App::PropertyString", "Progress", "显示", "现在走到第几针 / 第几趟")
        obj.setEditorMode("Progress", 1)
    if getattr(obj, "Machine", "") in SEQ and not hasattr(obj, "ProgressAngle"):
        obj.addProperty("App::PropertyFloat", "ProgressAngle", "显示", "进度角：每 360° 一针 / 一趟（第 k 针从 k×360° 开始，从 0 数）")
        obj.ProgressAngle = float(obj.Phi.Value if hasattr(obj.Phi, "Value") else obj.Phi)


def span(obj, p=None):
    """转一圈的进度角：主轴机型 360°；花样、刺绣 = 针数 × 360°，横机 = 趟数 × 360°"""
    m = getattr(obj, "Machine", "lockstitch")
    if m not in SEQ:
        return 360.0
    from sewcore import cad_seq
    p = p if p is not None else obj.Proxy.params(obj)
    return max(360.0, cad_seq.cfg_of(m, p)[0]["n"] * 360.0)


def progress_text(obj, p, phi):
    m = getattr(obj, "Machine", "lockstitch")
    if m not in SEQ:
        return "{:.0f}°".format(phi % 360)
    from sewcore import cad_seq
    D = cad_seq.cfg_of(m, p)[0]
    k = max(0, min(D["n"] - 1, int(phi // 360)))
    idx = (D["idx"][k] if D.get("idx") else k) + 1
    unit = "趟" if m == "flatknit" else "针"
    return "第 {} {}（共 {} {}）· {:.0f}°".format(idx, unit, D.get("N", D["n"]), unit, phi % 360)


class SewDesign:
    def __init__(self, obj, params=None, machine="lockstitch"):
        M = sewcore.get(machine)
        p = M.clean(params)
        obj.addProperty("App::PropertyString", "Machine", "机型", "lockstitch 平缝机 / overlock 包缝机 / cover 绷缝机 / pattern 花样机 / embroid 刺绣机 / flatknit 横机")
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
        if "pts" in p:                          # 花样机上传的针位表（第 42 轮）：不在参数表里，存成一个 JSON 文字
            obj.addProperty("App::PropertyString", "PatternPoints", "花样", "上传的针位表（JSON：[[x, y], …]，mm）")
            obj.PatternPoints = json.dumps(p["pts"])
        if M.MACHINE in FILE_MACHINES:          # 第 69 轮刺绣花样文件、第 70 轮横机意匠图（“从哪里来”选上传时用）
            _add_stitch_props(obj, M.MACHINE)
            _set_stitch_data(obj, p)
        obj.addProperty("App::PropertyAngle", "Phi", "显示", PHI_TIP.get(M.MACHINE, PHI_TIP["lockstitch"]))
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
        if getattr(obj, "PatternPoints", ""):
            try:
                p["pts"] = json.loads(obj.PatternPoints)
            except ValueError:
                pass
        if M.MACHINE in FILE_MACHINES:
            p.update(_stitch_params(obj, M.MACHINE))
        return M.clean(p)

    def execute(self, obj):
        p = self.params(obj)
        M = self.machine(obj)
        R = M.analyze(p)
        bad = [c for c in R["checks"] if c["state"] == "bad"]
        warn = [c for c in R["checks"] if c["state"] == "warn"]
        obj.Status = "全部合格" if not bad and not warn else "不合格 {} 项，注意 {} 项".format(len(bad), len(warn))
        keep = {k: R[k] for k in ("machine", "params", "results", "checks", "timing", "trial", "chain", "tables", "ok", "version", "key") if k in R}
        obj.ResultJson = json.dumps(keep, ensure_ascii=False)
        # 第 94 轮：红黄灯 → 出问题的部件、停在哪里（同网页版讲解片，sewcore/hotspot.py）
        _ensure_props(obj)
        try:
            hs = hotspot.hotspots(M.MACHINE, p, R)
        except Exception as e:  # noqa: BLE001  标红是辅助，算不出不影响零件和校核
            App.Console.PrintWarning("问渠缝纫机：标红没算出来（{}）\n".format(e))
            hs = []
        if getattr(self, "_painted", None) is None:      # 刚打开的文件：上次涂过的就是上次的红黄灯部件（灯灭了要还回本色）
            self._hot = None
            self._painted = {}
            names = {getattr(o, "SewKey", ""): o.Name for o in (obj.Parts or []) if o is not None}
            for n, c in self.hot_colors(obj).items():
                if n in names:
                    self._painted[names[n]] = tuple(c)
        obj.HotJson = json.dumps(hs, ensure_ascii=False)
        self._hot = None
        self.update_parts(obj, p, get_phi(obj))

    def hot_colors(self, obj):
        """零件名 → 颜色：红灯的部件红、黄灯的橙（同一个零件红黄都有算红）"""
        if getattr(self, "_hot", None) is None:
            try:
                hs = json.loads(getattr(obj, "HotJson", "") or "[]")
            except ValueError:
                hs = []
            col = {}
            for h in hs:
                if h.get("whole"):                  # 整机的项（机壳共振……）不涂：整台都红就看不出是哪个机构了
                    continue
                for n in h.get("names") or []:
                    if h["state"] == "bad" or n not in col:
                        col[n] = RED if h["state"] == "bad" else ORANGE
            self._hot = col
        return self._hot

    def update_parts(self, obj, p, phi):
        doc = obj.Document
        M = self.machine(obj)
        model = cad.parts3d(p, phi, M.MACHINE)
        hot = self.hot_colors(obj)
        have = {getattr(o, "SewKey", ""): o for o in (obj.Parts or []) if o is not None}
        sig = getattr(self, "_sig", None)
        if sig is None:
            sig = self._sig = {}
        out = []
        for d in model["parts"]:
            name = d["name"]
            o = have.get(name)
            fresh = o is None or o.Document is None
            if fresh:
                o = doc.addObject("Part::Feature", "Sew_" + name)
                o.addProperty("App::PropertyString", "SewKey", "问渠", "零件代号")
                o.SewKey = name
                o.setEditorMode("SewKey", 1)
                o.Label = d["zh"]
                sig.pop(o.Name, None)
            key = json.dumps({k: v for k, v in d.items() if k not in ("color", "zh")}, sort_keys=True)
            if sig.get(o.Name) != key:              # 只重建动了的零件：转动时快得多（横机一百多根针，大多不动）
                o.Shape = cad.freecad_shapes({"parts": [d]})[0][2]
                sig[o.Name] = key
            # 只动我们涂过的颜色：新零件给本色；红黄灯涂红 / 橙；灯灭了还回本色。用户自己改过的颜色不碰
            painted = getattr(self, "_painted", None)
            if painted is None:
                painted = self._painted = {}
            want = hot.get(name)
            color = None
            if fresh:
                color = tuple(want or d["color"])
            elif want is not None and painted.get(o.Name) != tuple(want):
                color = tuple(want)
            elif want is None and o.Name in painted:
                color = tuple(d["color"])
            if color is not None:
                try:
                    o.ViewObject.ShapeColor = color
                except Exception:  # noqa: BLE001  命令行里没有 ViewObject
                    pass
                if want is not None:
                    painted[o.Name] = tuple(want)
                else:
                    painted.pop(o.Name, None)
            o.purgeTouched()
            out.append(o)
        keep = {x.Name for x in out}
        for o in obj.Parts or []:                   # 换了机型参数后不再有的零件（例如针数变了）：删掉，不留在文档里
            if o is not None and o.Document is not None and o.Name not in keep:
                try:
                    doc.removeObject(o.Name)
                except Exception:  # noqa: BLE001
                    pass
        if [x.Name for x in out] != [x.Name for x in (obj.Parts or []) if x is not None]:
            obj.Parts = out
        if hasattr(obj, "Progress"):
            obj.Progress = progress_text(obj, p, phi)

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


def hotspots(obj):
    try:
        return json.loads(getattr(obj, "HotJson", "") or "[]")
    except ValueError:
        return []


def hotspot_of(obj, key):
    """红黄灯项 key 对应的部件、停的地方（重新计算时算好的）"""
    for h in hotspots(obj):
        if h.get("key") == key:
            return h
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
        if k not in M.PARAMS:
            continue
        setattr(obj, _pname(k), v if k in M.CHOICES else float(v))
    if M.MACHINE in FILE_MACHINES:
        _add_stitch_props(obj, M.MACHINE)
        _set_stitch_data(obj, p)
    elif "pts" in p:
        if not hasattr(obj, "PatternPoints"):
            obj.addProperty("App::PropertyString", "PatternPoints", "花样", "上传的针位表（JSON：[[x, y], …]，mm）")
        obj.PatternPoints = json.dumps(p["pts"])
    if d.get("project"):
        obj.Label = d["project"]
    obj.Document.recompute()


def export_step(obj, path):
    import Import
    Import.export(list(obj.Parts), path)


def apply_params(obj, changes):
    """第 49 轮：AI 助手“采用”、插入本单位零件“用到设计”——把几个参数写进设计对象并重算（夹到范围里）"""
    M = SewDesign.machine(obj)
    p = M.clean(dict(obj.Proxy.params(obj), **{k: v for k, v in (changes or {}).items() if k in M.PARAMS}))
    done = {}
    for k in changes or {}:
        if k in M.PARAMS:
            setattr(obj, _pname(k), p[k] if k in M.CHOICES else float(p[k]))
            done[k] = p[k]
    obj.Document.recompute()
    return done


# ---------- 第 62 轮：电控箱 ----------
EBOX_IPM = (60.0, 45.0, 12.0)          # 功率模块简化成实心块（长、宽、高 mm），贴在顶板里面正中——和数字工厂 CAE 复核用的同一只外壳


def ebox_shape(q):
    """参数化电控箱外壳：铝盒（外壳兼散热器）+ 顶面沿宽度方向的翅片 + 功率模块块。q 是计算核心 ebox 的参数（mm）"""
    import Part
    L, W, H, t = float(q["L"]), float(q["W"]), float(q["H"]), float(q["wall"])
    V = App.Vector
    sh = Part.makeBox(L, W, H, V(-L / 2, -W / 2, 0)).cut(Part.makeBox(L - 2 * t, W - 2 * t, H - 2 * t, V(-L / 2 + t, -W / 2 + t, t)))
    il, iw, ih = EBOX_IPM
    sh = sh.fuse(Part.makeBox(il, iw, ih, V(-il / 2, -iw / 2, H - t - ih)))
    n = int(q.get("fins") or 0)
    if n:
        pitch, ft, fh = L / n, float(q["fin_t"]), float(q["fin_h"])
        for i in range(n):
            sh = sh.fuse(Part.makeBox(ft, W, fh, V(-L / 2 + pitch * (i + 0.5) - ft / 2, -W / 2, H)))
    return sh.removeSplitter()


def ebox_analyze(obj, q):
    """这台设计的电控箱：电流取设计（同网页版“CAE 分析 → 电控箱”）"""
    from sewcore import ebox as EB
    M = SewDesign.machine(obj)
    return EB.analyze(q, M.MACHINE, obj.Proxy.params(obj))


def add_ebox(obj, q):
    """在文档里建（或更新）电控箱外壳，返回 Part::Feature"""
    doc = obj.Document
    name = "WQS_Ebox"
    f = doc.getObject(name) or doc.addObject("Part::Feature", name)
    f.Label = "电控箱外壳 {:g}×{:g}×{:g}".format(float(q["L"]), float(q["W"]), float(q["H"]))
    f.Shape = ebox_shape(q)
    doc.recompute()
    return f
