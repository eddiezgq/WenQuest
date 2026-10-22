"""问渠凸轮 FreeCAD 页的本地验收（第 39 轮第 5 步）：不在 CI 里跑，要装了 FreeCAD 的机器。

    python tools/check_freecad.py /path/to/FreeCADCmd [示例名 …]

对每个示例：把 wq_cam.py 和 camkit 按工作台的样子摆进临时文件夹，用 FreeCADCmd 打开项目、算校核、建实体、导出；
再在本机 Python 里用同一个项目算一遍，逐项比校核结论和数值（相对差 ≤ 1e-9），并检查每个实体有效。
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(HERE), str(HERE / "freecad")]

import wq_cam  # noqa: E402

RUNNER = """
import os, sys, json, time, traceback
sys.path.insert(0, os.environ["WQ_PACK"])
try:
    import wq_cam
    t = time.time()
    r = wq_cam.run_headless(os.environ["WQ_CAM_PROJECT"], os.environ["WQ_CAM_OUT"])
    r["seconds"] = round(time.time() - t, 1)
    import FreeCAD
    doc = FreeCAD.ActiveDocument
    if os.environ.get("WQ_CAM_ANGLES") and doc.getObject("CamSystem"):
        p = wq_cam.load(os.environ["WQ_CAM_PROJECT"])
        got = {}
        for a in json.loads(os.environ["WQ_CAM_ANGLES"]):
            doc.getObject("CamSystem").Angle = a
            doc.recompute()
            got[str(a)] = {o.Name: [list(o.Placement.Base), list(o.Placement.Rotation.Q)] for o in doc.Objects
                           if hasattr(o, "Placement") and o.TypeId == "Part::Feature"}
            cam, tur = doc.getObject("GloboidalCam"), doc.getObject("Turret")
            if cam and tur:  # rollers and the cam at this angle: they touch, they must not overlap
                got[str(a)]["overlap_mm3"] = cam.Shape.common(tur.Shape).Volume
                got[str(a)]["gap_mm"] = cam.Shape.distToShape(tur.Shape)[0]
        r["placements"] = got
    print("RESULT " + json.dumps(r, ensure_ascii=False))
except Exception:
    print("FAILED " + traceback.format_exc())
"""


def same(a, b):
    if a is None or b is None or isinstance(a, str) or isinstance(b, str):
        return a == b
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def main(fc, names):
    names = names or sorted(f.stem for f in (HERE / "examples").glob("*.json") if not f.name.endswith(".cae.json"))
    tmp = Path(tempfile.mkdtemp(prefix="wqcam-fc-"))
    pack = tmp / "WenQuest"
    pack.mkdir()
    for f in (HERE / "freecad").glob("*.py"):
        shutil.copy(f, pack)
    shutil.copytree(HERE / "camkit", pack / "camkit", ignore=shutil.ignore_patterns("__pycache__"))
    (tmp / "run.py").write_text(RUNNER, encoding="utf-8")
    ok = True
    for name in names:
        proj = HERE / "examples" / f"{name}.json"
        out = tmp / name
        env = dict(os.environ, WQ_PACK=str(pack), WQ_CAM_PROJECT=str(proj), WQ_CAM_OUT=str(out), LANG="C.UTF-8",
                   QT_QPA_PLATFORM="offscreen", WQ_CAM_ANGLES="[0, 37, 90, 160, 200, 275, 330]")
        r = subprocess.run([fc, str(tmp / "run.py")], env=env, capture_output=True, text=True, timeout=1800)
        line = next((x for x in r.stdout.splitlines() if x.startswith(("RESULT ", "FAILED "))), None)
        if not line or line.startswith("FAILED"):
            print(f"{name}: FreeCAD run failed\n{r.stdout[r.stdout.find('FAILED'):][-3000:]}\n{r.stderr[-1000:]}")
            ok = False
            continue
        res = json.loads(line[7:])
        fc_rows = json.loads((out / "checks.json").read_text(encoding="utf-8"))
        py_rows = wq_cam.check_rows(wq_cam.analyse(wq_cam.load(proj)))
        diff = [(a, b) for a, b in zip(fc_rows, py_rows, strict=False)
                if a[:3] != list(b[:3]) or not same(a[3], b[3])]
        good = len(fc_rows) == len(py_rows) and not diff and all(res["valid"].values())
        ok &= good
        print(f"{name}: {'OK' if good else 'DIFFERENT'} — {len(fc_rows)} checks equal to the web kernel, "
              f"solids valid {res['valid']}, {res['seconds']} s, files {[Path(f).name for f in res['files']]}")
        for n in res["notes"]:
            print("   ", n)
        for a, b in diff[:10]:
            print("    FreeCAD", a, "web", b)
        if res.get("placements"):
            (tmp / f"{name}-placements.json").write_text(json.dumps(res["placements"]), encoding="utf-8")
            ov = {a: round(v.get("overlap_mm3", 0.0), 4) for a, v in res["placements"].items()}
            gap = {a: round(v.get("gap_mm", 0.0), 4) for a, v in res["placements"].items()}
            print(f"    smallest gap rollers–cam (mm, 0 = touching): {gap}")
            good_ov = all(v < 1.0 for v in ov.values()) and all(v < 0.01 for v in gap.values())
            ok &= good_ov
            print(f"    rollers in the cam's grooves, overlap by camshaft angle (mm³): {ov}",
                  "OK" if good_ov else "TOO MUCH")
    print("all OK" if ok else "SOME DIFFERENT", "— outputs in", tmp)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2:]))
