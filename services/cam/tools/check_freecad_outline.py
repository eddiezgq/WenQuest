# -*- coding: utf-8 -*-
"""FreeCAD 里“用草图当凸轮廓线”的验收（第 179 轮）：在官方 FreeCAD 的 freecadcmd 里运行（CI：cam.yml 的 freecad 作业）。

    freecadcmd tools/check_freecad_outline.py        （在 services/cam 下；WQ_OUT 指输出文件夹）

做法：用网页版同一个内核算出两个已知运动的凸轮廓线（直动滚子、摆动平底），在 FreeCAD 里画成草图（廓线是穿过
点的 B 样条，再加一个轴孔圆；草图转 25°、平移、放在斜的平面里），用 wq_cam_outline.run_headless 反求运动、
建实体，逐项核对：基圆半径、行程、反求校验合格、建出的实体有效。全部通过时打印 ALL OK，否则退出码 1。
"""
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [HERE, os.path.join(HERE, "freecad")]

import FreeCAD  # noqa: E402
import Part  # noqa: E402
import Sketcher  # noqa: E402, F401  (loads the sketch object type)
import numpy as np  # noqa: E402

from camkit import disk as D  # noqa: E402
from camkit.analyze import mechanism  # noqa: E402
from camkit.program import Program  # noqa: E402

CASES = [
    ("TrRoller", {"follower": "translating", "contact": "roller", "rb": 40, "rr": 10, "e": 4, "sigma": 1},
     {"unit": "mm", "segments": [{"kind": "rise", "deg": 120, "h": 12, "law": "cycloidal"},
                                 {"kind": "dwell", "deg": 60},
                                 {"kind": "return", "deg": 120, "h": 12, "law": "poly345"},
                                 {"kind": "dwell", "deg": 60}]}, 12.0),
    ("OsFlat", {"follower": "oscillating", "contact": "flat", "rb": 40, "a": 100, "sigma": -1},
     {"unit": "rad", "segments": [{"kind": "rise", "deg": 120, "h_deg": 15, "law": "cycloidal"},
                                  {"kind": "dwell", "deg": 60},
                                  {"kind": "return", "deg": 120, "h_deg": 15, "law": "poly345"},
                                  {"kind": "dwell", "deg": 60}]}, 15.0),
]


def sketch_of(doc, name, m, prog):
    P = np.asarray(D.analyse(mechanism(m), Program.from_dict(prog), 3600)["profile"])[:, ::5]  # every 0.5°
    sk = doc.addObject("Sketcher::SketchObject", name)
    pts = [FreeCAD.Vector(float(x), float(y), 0) for x, y in P.T]
    bs = Part.BSplineCurve()
    bs.interpolate(pts, PeriodicFlag=True)
    sk.addGeometry(bs, False)
    sk.addGeometry(Part.Circle(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), 8.0), False)  # the bore
    # the sketch somewhere in space: turned in its own plane, moved, and on a tilted plane
    sk.Placement = FreeCAD.Placement(FreeCAD.Vector(30, -20, 15),
                                     FreeCAD.Rotation(FreeCAD.Vector(1, 1, 0), 35).multiply(
                                         FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 25)))
    doc.recompute()
    return sk


def main():
    import wq_cam_outline as O

    out = os.environ.get("WQ_OUT") or "wq-outline-out"
    doc = FreeCAD.newDocument("OutlineCheck")
    bad = []
    for name, m, prog, lift in CASES:
        try:
            sk = sketch_of(doc, name, m, prog)
            mech = {k: v for k, v in m.items() if k != "rb"}
            r = O.run_headless(sk, mech, os.path.join(out, name))
            rep = r["report"]
            lift_got = rep["lift"]
            ok = {
                "rb": abs(rep["rb"] - m["rb"]) < 2e-3,
                "lift": abs(lift_got - lift) < 2e-3,
                "check": rep["check"]["ok"],
                "valid": all(r["valid"].values()),
                "project": os.path.isfile(r["project"]),
            }
            print(name, json.dumps({"rb": rep["rb"], "lift": lift_got, "shift": rep["shift_deg"],
                                    "check_um": rep["check"]["max_dev"] * 1e3, "ok": ok}, ensure_ascii=False))
            if not all(ok.values()):
                bad.append(name)
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            bad.append(name)
    # nothing selected / no closed loop: a clear message
    line = doc.addObject("Part::Feature", "OpenLine")
    line.Shape = Part.makeLine(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(10, 0, 0))
    try:
        O.outline_points(line)
        bad.append("open line accepted")
    except ValueError as exc:
        print("open line:", exc)
    print("ALL OK" if not bad else "FAILED: " + ", ".join(bad))
    return 0 if not bad else 1


rc = main()
if rc:
    sys.exit(rc)
