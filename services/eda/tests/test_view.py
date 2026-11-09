"""第 113 轮：网页审图接口——示例设计、KiCad 文件、报告里没通过的项（位置换成 KiCad 坐标）。"""

import os
import sys

os.environ.setdefault("EDA_SIM", "0")
os.environ.setdefault("EDA_THERMAL", "0")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

import app as A  # noqa: E402

c = TestClient(A.app)


def test_designs_and_files():
    d = {x["key"]: x for x in c.get("/api/view/designs").json()["designs"]}
    assert set(d) == {"A", "B", "24V"} and "drv-joint.kicad_pcb" in d["A"]["files"]
    assert d["A"]["count"]["fail"] == 7 and "sym-lib-table" not in d["B"]["files"]
    r = c.get("/api/view/file/A/drv-joint.kicad_pcb")
    assert r.status_code == 200 and r.text.startswith("(kicad_pcb")
    for bad in ("../design.yaml", "drv-joint.kicad_pcb.bak", "sym-lib-table", "..%2F..%2Fapp.py"):
        assert c.get("/api/view/file/A/" + bad).status_code == 404
    assert c.get("/api/view/file/Z/drv-joint.kicad_pcb").status_code == 404


def test_report_issues_in_kicad_coordinates():
    r = c.get("/api/view/report/A").json()
    keys = [i["key"] for i in r["issues"]]
    assert "L-near-C27" in keys and all(i["status"] != "pass" for i in r["issues"])
    c27 = next(i for i in r["issues"] if i["key"] == "L-near-C27")
    assert c27["refs"][0] == "C27" and c27["points"][0][1] > 100  # 板子模型 y 向上（负），KiCad y 向下（正）
    assert r["issues"][0]["status"] == "fail"
    assert c.get("/api/view/report/nope").status_code == 404


def test_page_has_no_external_fonts():
    js = (A.WEB / "view" / "vendor" / "kicanvas.js").read_text(encoding="utf-8")
    assert "fonts.googleapis.com" not in js and "vendor/kicanvas-fonts.css" in js
    for f in ("KICANVAS-LICENSE.md", "MATERIAL-SYMBOLS-LICENSE.txt", "NUNITO-LICENSE.txt"):
        assert (A.WEB / "view" / "vendor" / f).exists()


def test_chinese_glyphs_loaded():
    # KiCanvas 自带字形只到 U+4E1F，原理图里的中文显示成“?”（11-08 线上看到）；补上 KiCad 字库其余字形
    import json

    v = A.WEB / "view" / "vendor"
    js = (v / "kicanvas.js").read_text(encoding="utf-8")
    assert "].concat(globalThis.WQ_NEWSTROKE_EXTRA||[]);" in js
    i = js.index("K3=[")
    have = len(json.loads(js[i + 3 : js.index("].concat(globalThis.WQ_NEWSTROKE_EXTRA", i) + 1]))
    extra = (v / "newstroke-extra.js").read_text(encoding="utf-8")
    glyphs = json.loads(extra[extra.index("=[") + 1 : extra.rindex(";")])
    for ch in "关节伺服驱动板相电流采样编码器接口":
        assert glyphs[ord(ch) - 32 - have]
    assert (v / "NEWSTROKE-LICENSE.txt").exists()
    page = (A.WEB / "view" / "index.html").read_text(encoding="utf-8")
    assert page.index("vendor/newstroke-extra.js") < page.index("vendor/kicanvas.js")


def test_plugin_zip():
    import io
    import zipfile

    r = c.get("/api/kicad-plugin.zip")
    assert r.status_code == 200 and r.headers["content-type"] == "application/zip"
    names = zipfile.ZipFile(io.BytesIO(r.content)).namelist()
    for n in ("plugin.json", "check.py", "requirements.txt", "wq_kicad/app.py", "wqeda/readers/kicad_ipc.py",
              "parts/BSC040N08NS5.yaml", "factories/example-smt.yaml", "resources/icon-24.png"):
        assert "wenquest-eda/" + n in names
    assert not any("__pycache__" in n for n in names)
    assert c.get("/api/kicad-plugin.zip").content == r.content  # 每次打出的字节一样
