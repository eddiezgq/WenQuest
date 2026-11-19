"""第 175 轮：问渠软件测试版下载包 → site/download/files/，版本清单 site/download/versions.json。

    python3 tools/wqlicense/pack.py [--version 2026.11.19]

三个 FreeCAD 工作台（问渠缝纫机、问渠轴承、问渠凸轮）：取各服务现有的打包函数（和网页上“下载 FreeCAD 版”同一份），再
  ① 我们自己的 .py 编译成 Python 3.11 字节码 .pyc、不放源码（FreeCAD 1.1 用 Python 3.11）；InitGui.py / Init.py 留源码（FreeCAD 只认源码），
  ② 加授权：wq_license（校验授权码、检查更新）、wq_gate（没授权就弹窗要码，不加载工作台），InitGui 里注册工作台前先过 wq_gate，
  ③ 使用说明里加“授权”一节。
问渠 CAD 安装包由 wenquest-cad 仓库的 Actions 出（GitHub 发布版），这里只登记它的版本和下载地址（--wqcad 版本 网址 大小 校验码）。
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "site" / "download"
PY311 = "python3.11"

LICENSE_NOTE = """

—— 授权（测试版）——
装好后第一次启动 FreeCAD 会弹窗要“测试授权码”：登录问渠官网下载页，点“领取一年测试授权”，把授权码粘贴进去。
授权一年有效，存在本机（Windows：%APPDATA%\\WenQuest\\license.txt）；到期后在下载页续期。软件联网时会提示有没有新版本。

—— Licence (beta) ——
The first time FreeCAD starts after installing, it asks for a beta licence code: sign in on the WenQuest download page, click
"Get a one-year beta licence" and paste the code. It is valid for one year and stored on this computer; renew it on the download page.
"""


def _run(cwd: Path, code: str) -> bytes:
    """各服务的打包函数各在自己的进程里跑（几个服务都叫 app、ai_api，放一个进程里会串）"""
    return subprocess.run([sys.executable, "-c", code], cwd=cwd, check=True, capture_output=True).stdout


def sources():
    out = {"sewing": ("问渠缝纫机", "WenQuest Sewing",
                      _run(ROOT / "services" / "gateway", "import sys;from app import sewing;sys.stdout.buffer.write(sewing.workbench_zip())"))}
    for svc, zh, en in (("bearing", "问渠轴承", "WenQuest Bearing"), ("cam", "问渠凸轮", "WenQuest Cam")):
        out[svc] = (zh, en, _run(ROOT / "services" / svc, "import sys;sys.path.insert(0,'.');import app;sys.stdout.buffer.write(app.freecad_pack())"))
    return out


def compile_pyc(src: bytes, name: str) -> bytes:
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / name
        p.write_bytes(src)
        subprocess.run([PY311, "-c", "import py_compile,sys;py_compile.compile(sys.argv[1],cfile=sys.argv[2],doraise=True,"
                        "invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)", str(p), str(p) + "c"], check=True)
        return (Path(str(p) + "c")).read_bytes()


def gate_initgui(src: str, wb_name: str) -> str:
    if "wq_workbench.register()" in src:
        new = src.replace("wq_workbench.register()", f"import wq_gate  # noqa: E402\nif wq_gate.licensed({wb_name!r}):\n    wq_workbench.register()")
    else:
        m = re.search(r"^(FreeCADGui|Gui)\.addWorkbench\((.+)\)\s*$", src, flags=re.M)
        assert m, "InitGui 里找不到 addWorkbench"
        new = src[:m.start()] + f"import wq_gate  # noqa: E402\nif wq_gate.licensed({wb_name!r}):\n    {m.group(0).strip()}\n" + src[m.end():]
    assert new != src
    return new


def protect(raw: bytes, wb_name: str) -> tuple[bytes, dict]:
    zin = zipfile.ZipFile(io.BytesIO(raw))
    buf = io.BytesIO()
    n_pyc = 0
    mod_root = None
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for info in zin.infolist():
            name, data = info.filename, zin.read(info)
            base = name.rsplit("/", 1)[-1]
            if base == "InitGui.py":
                mod_root = name[: -len(base)]
                z.writestr(name, gate_initgui(data.decode("utf-8"), wb_name))
            elif base == "Init.py":
                z.writestr(name, data)
            elif name.endswith(".py"):
                z.writestr(name + "c", compile_pyc(data, base))
                n_pyc += 1
            elif base.endswith("使用说明.txt"):
                z.writestr(name, data.decode("utf-8") + LICENSE_NOTE)
            else:
                z.writestr(info, data)
        assert mod_root is not None
        for m in ("wq_license", "wq_gate"):
            z.writestr(mod_root + m + ".pyc", compile_pyc((HERE / f"{m}.py").read_bytes(), m + ".py"))
    return buf.getvalue(), {"pyc": n_pyc + 2}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default=dt.date.today().strftime("%Y.%m.%d"))
    ap.add_argument("--wqcad", nargs=4, metavar=("VERSION", "URL", "SIZE_MB", "SHA256"))
    a = ap.parse_args()
    files = OUT / "files"
    files.mkdir(parents=True, exist_ok=True)
    vf = OUT / "versions.json"
    versions = json.loads(vf.read_text(encoding="utf-8")) if vf.exists() else {}
    for old in files.glob("*-freecad-*.zip*"):
        old.unlink()
    for key, (zh, en, raw) in sources().items():
        data, st = protect(raw, zh)
        fn = f"wenquest-{key}-freecad-{a.version}.zip"
        (files / fn).write_bytes(data)
        sha = hashlib.sha256(data).hexdigest()
        (files / (fn + ".sha256")).write_text(f"{sha}  {fn}\n", encoding="ascii")
        versions[f"{key}-freecad"] = {"version": a.version, "url": f"files/{fn}", "size": len(data), "sha256": sha, "name": [zh, en],
                                     "date": dt.date.today().isoformat(), "pyc": st["pyc"]}
        print(fn, round(len(data) / 1024), "KB", st)
    if a.wqcad:
        ver, url, mb, sha = a.wqcad
        versions["wqcad"] = {"version": ver, "url": url, "size": int(float(mb) * 1024 * 1024), "sha256": sha, "name": ["问渠 CAD", "WenQuest CAD"],
                             "date": dt.date.today().isoformat()}
    vf.write_text(json.dumps(versions, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
