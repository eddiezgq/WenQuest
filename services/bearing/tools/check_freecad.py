"""问渠轴承 FreeCAD 页的本地验收（第 64 轮第 6 步）：不在 CI 里跑，要装了 FreeCAD 的机器。

    python tools/check_freecad.py /path/to/FreeCADCmd [示例名 …]

对每个示例：把 wq_bearing.py、wq_bearing_form.py 和 bearingkit 按工作台的样子摆进临时文件夹，用 FreeCADCmd 打开项目、
算校核、建实体、导出（深沟球示例另带工艺模板出工序简图）；再在本机 Python 里用同一个项目算一遍，逐项比校核结论和数值
（相对差 ≤ 1e-9），并检查实体有效、体积与解析值相差 < 0.1%、滚动体与套圈不干涉
（圆锥滚子只允许线接触相切处的求交残差：不超过滚子体积的万分之一）。
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

import wq_bearing  # noqa: E402

RUNNER = """
import os, sys, json, time, traceback
sys.path.insert(0, os.environ["WQ_PACK"])
try:
    import wq_bearing
    t = time.time()
    r = wq_bearing.run_headless(os.environ["WQ_BEARING_PROJECT"], os.environ["WQ_BEARING_OUT"],
                                os.environ.get("WQ_BEARING_PROCESS") or None)
    r["seconds"] = round(time.time() - t, 1)
    print("RESULT " + json.dumps(r, ensure_ascii=False, default=float))
except Exception:
    print("FAILED " + traceback.format_exc())
"""


def pack(dest: Path) -> None:
    for f in ("wq_bearing.py", "wq_bearing_form.py"):
        shutil.copy(HERE / "freecad" / f, dest / f)
    shutil.copytree(HERE / "bearingkit", dest / "bearingkit", ignore=shutil.ignore_patterns("__pycache__"))


def same(a, b) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b or abs(a - b) <= 1e-9 * max(abs(a), abs(b), 1e-12)
    return a == b


def main(fc: str, names: list[str]) -> int:
    names = names or sorted(p.stem for p in (HERE / "examples").glob("*.json"))
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        packdir = tmp / "WenQuest"
        packdir.mkdir()
        pack(packdir)
        runner = tmp / "runner.py"
        runner.write_text(RUNNER, encoding="utf-8")
        for name in names:
            proj = HERE / "examples" / f"{name}.json"
            out = tmp / name
            env = dict(
                os.environ,
                WQ_PACK=str(packdir),
                WQ_BEARING_PROJECT=str(proj),
                WQ_BEARING_OUT=str(out),
                QT_QPA_PLATFORM="offscreen",
            )
            proc_file = HERE / "examples" / "process" / f"{name}.json"
            if proc_file.is_file():
                env["WQ_BEARING_PROCESS"] = str(proc_file)
            run = subprocess.run([fc, str(runner)], capture_output=True, text=True, env=env, timeout=900)
            line = next((ln for ln in run.stdout.splitlines() if ln.startswith(("RESULT ", "FAILED "))), None)
            if not line or line.startswith("FAILED"):
                print(f"{name}: FreeCAD 失败\n{line or run.stdout[-2000:]}\n{run.stderr[-2000:]}")
                bad += 1
                continue
            r = json.loads(line[7:])
            got = json.loads((out / "checks.json").read_text(encoding="utf-8"))
            want = [list(x) for x in wq_bearing.check_rows(wq_bearing.analyse(wq_bearing.load(str(proj))))]
            diff = [
                (a, b)
                for a, b in zip(got, want, strict=False)
                if not all(same(x, y) for x, y in zip(a, b, strict=True))
            ]
            diff += [("count", len(got), len(want))] if len(got) != len(want) else []
            vol_err = {k: abs(r["volumes"][k] - r["analytic"][k]) / r["analytic"][k] for k in r["volumes"]}
            taper = "tapered" in json.loads(proj.read_text(encoding="utf-8")).get("type", "")
            ov_ok = all(v <= (1e-4 * r["analytic"]["element"] if taper else 1e-6) for v in r["overlap"].values())
            ok = not diff and all(r["valid"].values()) and max(vol_err.values()) < 1e-3 and ov_ok
            bad += not ok
            sk = len([f for f in r["files"] if f.endswith("-sketch.svg")])
            print(
                f"{name}: {'通过' if ok else '不通过'}  校核 {len(got)} 项 "
                f"{'一致' if not diff else '不一致 ' + str(diff[:3])}；"
                f"实体有效 {all(r['valid'].values())}；体积相对差 ≤ {max(vol_err.values()):.1e}；"
                f"干涉 内 {r['overlap']['inner']:.4f} 外 {r['overlap']['outer']:.4f} mm³；滚动体 {r['elements']} 个；"
                f"文件 {len(r['files'])} 个（工序简图 {sk}）；{r['seconds']} 秒"
            )
    print("全部通过" if not bad else f"{bad} 个不通过")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2:]))
