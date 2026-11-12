"""WQ-LS G4.7 面线路径检查：一转里面线（frames.json 的 thread 折线）不碰零件和机壳。在 FreeCAD 里运行：

    WQ_MECH=<零件目录> WQ_HOUSING=<上件> WQ_HOUSING_LOWER=<下件> [WQ_STEP=6] freecadcmd -c "exec(open('tools/wqls/cad/thread_check.py').read())"

线在折点处本来就贴着零件（夹线盘、挑线簧钩、过线点、挑线杆线眼、针杆线钩、针眼），所以每段两头各让开 2 mm，只查中间；
线按 Ø0.3 的细圆柱算。输出 <零件目录>/thread_check.json：每段的最小距离、在哪个零件、哪个转角。
"""
import json
import os

import FreeCAD as App
import Part

V = App.Vector
D = os.environ["WQ_MECH"]
STEP = int(os.environ.get("WQ_STEP", "6"))
FR = json.load(open(os.path.join(D, "frames.json")))["frames"]
parts = {k: Part.read(os.path.join(D, k + ".step")) for k in json.load(open(os.path.join(D, "parts.json")))["parts"]}
cast = Part.read(os.environ["WQ_HOUSING"])
if os.environ.get("WQ_HOUSING_LOWER"):
    cast = cast.fuse(Part.read(os.environ["WQ_HOUSING_LOWER"]))
parts["casting"] = cast


def mat(m):
    return App.Matrix(*m)


worst = {}
for f in FR[:: max(1, STEP // 2)]:
    pts = [V(*p) for p in f["thread"]]
    segs = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        d = b - a
        if d.Length < 5.0:
            continue
        u = V(d)
        u.normalize()
        segs.append((i, Part.makeCylinder(0.15, d.Length - 4.0, a + u * 2.0, u)))
    for k, s0 in parts.items():
        s = s0.copy()
        m = f["M"].get(k)
        if m:
            s.transformShape(mat(m), True)
        bb = s.BoundBox
        for i, seg in segs:
            sb = App.BoundBox(seg.BoundBox)
            sb.enlarge(3.0)
            if not bb.intersect(sb):                     # 离得远的不算距离（只关心 3 mm 以内）
                continue
            dist = s.distToShape(seg)[0]
            key = f"{i}|{k}"
            if key not in worst or dist < worst[key][0]:
                worst[key] = (round(dist, 3), f["phi"])
rows = sorted(([k.split("|")[0], k.split("|")[1], v[0], v[1]] for k, v in worst.items()), key=lambda r: r[2])
out = dict(step_deg=STEP, note="面线每段两头各让开 2 mm；距离 0 = 线穿过零件", closest=rows[:15], touching=[r for r in rows if r[2] <= 0.0])
json.dump(out, open(os.path.join(D, "thread_check.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(dict(touching=out["touching"], closest=rows[:8]), ensure_ascii=False))
