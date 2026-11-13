"""第 112 轮：问渠贴片（工厂端）接口。模型用替身；上传的文件算完就删。"""

import glob
import io
import os
import sys
import tempfile
import zipfile

os.environ.setdefault("EDA_SIM", "0")
os.environ.setdefault("EDA_THERMAL", "0")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402
import yaml  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app as A  # noqa: E402

REPO = A.REPO
GERBER = REPO / "factory" / "designs" / "drv-joint" / "out" / "gerber.zip"
DEMO = REPO / "eda" / "examples" / "pcba-demo"


@pytest.fixture
def client():
    return TestClient(A.app)


def _files(bom=DEMO / "bom.csv", cpl=DEMO / "pos.csv"):
    return [("gerber", ("gerber.zip", GERBER.read_bytes(), "application/zip")),
            ("bom", ("bom.csv", bom.read_bytes(), "text/csv")), ("cpl", ("pos.csv", cpl.read_bytes(), "text/csv"))]


def _left():
    return glob.glob(os.path.join(tempfile.gettempdir(), "wq-pcba-*"))


def test_factories(client):
    f = client.get("/api/factory/factories").json()
    keys = {x["key"] for x in f["factories"]}
    assert {"example-smt", "example-smt-economy"} <= keys and all(x["fictional"] for x in f["factories"])
    assert "top copper" in f["layers"]


def test_check_demo_package_and_nothing_kept(client):
    before = set(_left())
    r = client.post("/api/factory/check", data={"factory": "example-smt"}, files=_files())
    assert r.status_code == 200, r.text
    j = r.json()
    d1 = next(x for x in j["results"] if x["key"] == "D1")
    assert d1["status"] == "fail" and d1["refs"] == ["C47"] and d1["id"] == "R1"
    assert {x["key"]: x["status"] for x in j["results"]}["T1"] == "unknown"
    q = {x["name"]: x["value"] for x in j["quantity"]["rows"]}
    assert q["贴片元件"] + q["通孔元件"] == 89 and q["物料种类"] == 39
    assert j["layers"]["drv-joint-F_Cu.gtl"] == "top copper" and j["svg"]["top"].startswith("<?xml")
    assert j["guessed"]["cpl"]["x"] == "PosX"
    assert set(_left()) == before                                     # 临时文件夹删掉了


def test_other_column_names_and_economy_factory(client, tmp_path):
    """换一套列名（英文、顺序不同）照样读对；经济线查出板子太大、引脚太密、焊盘太小"""
    import csv
    rows = list(csv.DictReader(open(DEMO.parent.parent.parent / "factory/designs/drv-joint/out/pos.csv")))
    p = tmp_path / "cpl.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Layer", "Designator", "Rotation", "Mid X", "Mid Y"])
        for r in rows:
            w.writerow([r["Side"], r["Ref"], r["Rot"], r["PosX"] + "mm", r["PosY"] + "mm"])
    fixed_bom = REPO / "factory" / "designs" / "drv-joint" / "out" / "bom.csv"
    j = client.post("/api/factory/check", data={"factory": "example-smt-economy"},
                    files=_files(bom=fixed_bom, cpl=p)).json()
    st = {x["key"]: x["status"] for x in j["results"]}
    assert st["D1"] == st["D4"] == "pass" and st["P1"] == st["P2"] == st["P3"] == "fail"
    assert j["maps"]["cpl"]["ref"] == "Designator"


def test_unrecognised_layers_ask_for_mapping(client):
    files = [("gerber", ("a.txt", b"G04 nothing*\nM02*\n", "text/plain"))]
    r = client.post("/api/factory/check", data={"factory": "example-smt"}, files=files)
    assert r.status_code == 422 and r.json()["detail"]["files"] == ["a.txt"]


def test_bad_inputs(client):
    assert client.post("/api/factory/check", data={"factory": "nope"}, files=_files()).status_code == 400
    bad = [("gerber", ("../../evil.zip", b"x", "application/zip"))]
    assert client.post("/api/factory/check", data={"factory": "example-smt"}, files=bad).status_code == 400
    xl = _files()[:1] + [("bom", ("bom.xlsx", b"PK", "application/octet-stream"))]
    assert client.post("/api/factory/check", data={"factory": "example-smt"}, files=xl).status_code == 400


def test_issues_draft_cites_checked_results(client, monkeypatch):
    j = client.post("/api/factory/check", data={"factory": "example-smt"}, files=_files()).json()
    sent = []

    class FakeResp:
        status_code = 200

        def __init__(self, body):
            self.body = body

        def json(self):
            return self.body

    class FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, url, headers=None, json=None):
            sent.append(json)
            return FakeResp({"draft": {"issues": [
                {"cites": ["R1"], "question": "C47 在坐标里有、物料清单里没有，要贴吗？", "options": ["贴", "不贴"],
                 "reply_required": True},
                {"cites": ["R2"], "question": "编出来的", "options": [], "reply_required": False}]}, "run": 5})

    monkeypatch.setattr(A, "_client", lambda: FakeClient())
    body = {"results": j["results"], "factory": j["factory"], "package": "demo"}
    assert client.post("/api/factory/issues", json=body).status_code == 401
    r = client.post("/api/factory/issues", json=body, headers={"cookie": "wq_sso=x"}).json()
    assert [i["refs"] for i in r["issues"]["issues"]] == [["C47"]]
    assert r["rejected"][0]["reason"].startswith("引用的 R2")          # R2 已通过：退回
    assert all(x["status"] != "pass" for x in sent[0]["results"])     # 只交没通过的结果
    assert "svg" not in str(sent[0]) and "PosX" not in str(sent[0])   # 不交文件
    doc = yaml.safe_load(r["yaml"])
    assert doc["format"] == "wqeda.issues/1" and doc["issues"][0]["cites"] == ["R1"]
    doc["issues"][0]["question"] = "改过的问题"
    out = client.post("/api/factory/issues/render", json={"issues": doc}).json()
    assert "改过的问题" in out["markdown"]
    doc["issues"][0]["cites"] = ["R77"]
    assert client.post("/api/factory/issues/render", json={"issues": doc}).status_code == 400


def test_zip_slip_is_flattened(client):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        with zipfile.ZipFile(GERBER) as src:
            for n in src.namelist():
                z.writestr("../../" + n, src.read(n))
    files = [("gerber", ("g.zip", buf.getvalue(), "application/zip"))]
    r = client.post("/api/factory/check", data={"factory": "example-smt"}, files=files)
    assert r.status_code == 200 and not os.path.exists(os.path.join(tempfile.gettempdir(), "drv-joint-F_Cu.gtl"))


def test_demo_package_button(client):
    j = client.post("/api/factory/check", data={"factory": "example-smt", "demo": "1"}).json()
    assert next(x for x in j["results"] if x["key"] == "D1")["refs"] == ["C47"]


def test_demo_package_returns_merged_bom_rows(client):
    """第 158 轮：检查结果回物料清单（合并行），给页面做“到外部库查”；不参与判定"""
    import csv
    j = client.post("/api/factory/check", data={"factory": "example-smt", "demo": "1"}).json()
    rows = j["bom"]
    src = list(csv.DictReader((DEMO / "bom.csv").open(encoding="utf-8")))
    want = {}
    for r in src:
        k = (r["物料编号"], r["数值"], r["封装"])
        want[k] = want.get(k, 0) + int(r["数量"])
    assert {(r["item"], r["value"], r["package"]): r["qty"] for r in rows} == want
    gdr = next(r for r in rows if r["value"] == "IR2101S")
    assert gdr["item"] == "IC-GDRV" and gdr["qty"] == 3


def test_ctrl_ls_package_button(client):
    """第 159 轮 159d3：“用平缝机控制器 CTRL-LS 的资料包”——本板生成的真文件，结果照实回来（不改判）"""
    import csv
    j = client.post("/api/factory/check", data={"factory": "example-smt", "demo": "ctrl-ls"}).json()
    assert j["results"]
    src = REPO / "factory" / "designs" / "ctrl-ls" / "out" / "bom.csv"
    n = sum(int(r["数量"]) for r in csv.DictReader(src.open(encoding="utf-8")))
    assert sum(r["qty"] for r in j["bom"]) == n
    # 不认得的名字不当资料包
    r = client.post("/api/factory/check", data={"factory": "example-smt", "demo": "../x"})
    assert r.status_code == 400
