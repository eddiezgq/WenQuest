"""第 62 轮：电控箱的热与流体（网关一侧）：参数表、公式计算（来宾能算）、CAE 复核链（流体 → 温度场 → 热阻代回公式）。
数字工厂用假服务代替；真算的自然对流和电控箱零件见 factory/digital/tests/test_cfd.py、test_design_sw.py。"""
import json

import httpx
import pytest

from app import main
from app.sewing_cae import ebox_thermal_rows
from tests.test_course_pack import client  # noqa: F401
from tests.test_sewing_cae import FakeFactory, cae  # noqa: F401

EXAMPLE = {"thermal": [{"type": "heat_flux", "faces": [37, 38], "power_w": 18.0}, {"type": "heat_flux", "faces": [35], "power_w": 8.0},
                       {"type": "convection", "faces": [1, 2, 3, 4, 5, 6], "h_w_m2k": 10.0, "t_inf_c": 40}],
           "groups": {"ipm": [37, 38], "inner_bottom": [35], "inner": [31], "outer": [1, 2, 3, 4, 5, 6]}, "mesh_mm": 4.5}
CFD_FACES = [dict(id=i, area_mm2=a, h_w_m2k=h, heat_w=1.0) for i, a, h in
             ((1, 14400, 4.6), (6, 14400, 4.6), (2, 23400, 4.5), (4, 23400, 4.5), (3, 41600, 2.9), (5, 41600, 2.4))]


class EboxFactory(FakeFactory):
    def __init__(self, t_shell=56.0):
        super().__init__()
        self.t_shell = t_shell

    def __call__(self, req):
        path, q = req.url.path.removeprefix("/api/design-sw"), dict(req.url.params)
        if path == "/ebox/geometry":
            b = json.loads(req.content)
            self.posted.append(b)
            return httpx.Response(200, json={"sha": "ebox-sha", "faces": [], "params": b["params"], "example": EXAMPLE})
        if path == "/geometry":                          # 上传的外壳：六个面（和流体结果的面号对得上）
            return httpx.Response(200, json={"sha": "own-sha", "faces": [dict(id=i, kind="plane") for i in range(1, 7)]})
        if path.startswith("/cfd/") and path.endswith("/result"):
            return httpx.Response(200, json={"stats": {"mode": "natural", "wall_t_c": 56.0, "h_mean": 3.5, "heat_w": 9.0, "converged": True},
                                             "faces": CFD_FACES})
        parts = path.strip("/").split("/")
        if parts[0] == "jobs" and len(parts) == 2 and req.method == "GET":
            j = self.jobs.get(parts[1])
            if j and j["org"] == q.get("org") and j["kind"] == "fea" and j["body"]["setup"].get("analysis") == "thermal":
                fg = [{"load": 2, "area_m2": 0.159, "mean_c": self.t_shell, "heat_w": 26.0}]
                return httpx.Response(200, json=dict(j, stats={"t_max_c": self.t_shell + 3, "film_groups": fg, "elements": 30000}))
        return super().__call__(req)


@pytest.fixture
def ebox(cae):  # noqa: F811
    c, h, _ = cae
    fk = EboxFactory()
    old = main.state.http._transport

    def route(req):
        return fk(req) if req.url.host == "factory.test" else old.handle_request(req)
    main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(route))
    return c, h, fk


def test_schema_and_guest_formula(client):  # noqa: F811
    s = client.get("/api/v1/sewing/ebox/schema?machine=pattern").json()
    keys = {p["key"] for g in s["groups"] for p in g["params"]}
    assert {"Irun", "Ipk", "tsw", "clog", "L", "fins", "air", "Tjmax"} <= keys and s["defaults"]["Rhs"] == 0.6
    assert client.get("/api/v1/sewing/ebox/schema?machine=nope").status_code == 400
    r = client.post("/api/v1/sewing/ebox/analyze", json={"machine": "lockstitch", "params": {"n": 6000}, "ebox": {"Ta": 38, "clog": 0.5}}).json()
    assert not r["ok"] and r["drives"][0]["Irun"] == pytest.approx(4.31, abs=0.02) and r["variants"]["rows"]
    assert {c["key"] for c in r["checks"] if c["state"] == "bad"} >= {"ths", "tj", "life"}
    r2 = client.post("/api/v1/sewing/ebox/analyze", json={"machine": "lockstitch", "ebox": {}, "rbox": 0.3}).json()
    assert r2["thermal"]["Rbox"] == 0.3


def test_thermal_rows_from_cfd():
    rows = ebox_thermal_rows(EXAMPLE, CFD_FACES, 6.0, 40)
    heat = [r for r in rows if r["type"] == "heat_flux"]
    conv = [r for r in rows if r["type"] == "convection"]
    assert sum(r["power_w"] for r in heat) == 26 and sorted(f for r in conv for f in r["faces"]) == [1, 2, 3, 4, 5, 6]
    assert min(r["h_w_m2k"] for r in conv) == pytest.approx(2.5 + 6.0) and all(r["t_inf_c"] == 40 for r in conv)


def test_cae_chain_cfd_then_thermal_then_resistance(ebox):
    c, h, fk = ebox
    assert c.get("/api/v1/sewing/cae/options", headers=h).json()["kinds"]["ebox"]
    r = c.post("/api/v1/sewing/cae/ebox", json={"machine": "lockstitch", "params": {}, "ebox": {"fins": 4}}, headers=h).json()
    jid = r["id"]
    geo = next(b for b in fk.posted if "params" in b and "p_ipm" in b["params"])
    assert geo["params"]["fins"] == 4 and geo["params"]["p_ipm"] == pytest.approx(18.0, abs=0.2) and geo["params"]["t_air"] == 40
    cfd = fk.posted[-1]
    assert cfd["kind"] == "cfd" and cfd["setup"]["flow"]["mode"] == "natural" and cfd["setup"]["heat"]["wall_t_c"] > 41
    # 流体还在排队
    assert c.get(f"/api/v1/sewing/cae/jobs/{jid}", headers=h).json()["stage"] == "cfd"
    # 流体算完 → 自动交温度场
    fk.jobs[jid]["status"] = "done"
    s = c.get(f"/api/v1/sewing/cae/jobs/{jid}", headers=h).json()
    assert s["stage"] == "thermal" and s["status"] == "running"
    th = fk.posted[-1]
    assert th["kind"] == "fea" and th["setup"]["analysis"] == "thermal" and th["setup"]["material_id"] == "6061-T6"
    assert any(t["type"] == "convection" and t["h_w_m2k"] > 8 for t in th["setup"]["thermal"])
    lst = c.get("/api/v1/sewing/cae/jobs", headers=h).json()["jobs"]
    assert next(x for x in lst if x["jid"] == jid)["status"] in ("queued", "running")
    # 温度场算完 → 外壳平均 56 °C、总发热 26 W → 箱子热阻约 0.61 K/W，和按尺寸的公式（约 0.58）对得上
    tjid = next(k for k, v in fk.jobs.items() if v["kind"] == "fea")
    fk.jobs[tjid]["status"] = "done"
    s = c.get(f"/api/v1/sewing/cae/jobs/{jid}", headers=h).json()
    res = s["result"]
    assert s["status"] == "done" and res["R_cae"] == pytest.approx(16 / res["Ptot"], rel=1e-3)
    assert res["checks"][0]["key"] == "ebox_r" and res["checks"][0]["state"] == "ok" and abs(res["diff"]) < 0.15
    assert res["with_cae"]["Ths"] > 0 and any(k["key"] == "cae_tj" for k in res["checks"])
    # 结果缓存：再打开不再问工厂
    n = len(fk.posted)
    assert c.get(f"/api/v1/sewing/cae/jobs/{jid}", headers=h).json()["result"]["R_cae"] == res["R_cae"] and len(fk.posted) == n


def test_cae_needs_license(client):  # noqa: F811
    assert client.post("/api/v1/sewing/cae/ebox", json={"machine": "lockstitch"}).status_code == 401


def test_exports_carry_the_control_box_and_step(ebox):
    """计算书、参数表带上“电控箱”一节（网页看过电控箱才带）；外壳 STEP 由数字工厂按尺寸现做"""
    import io
    import zipfile
    c, h, fk = ebox
    body = {"machine": "lockstitch", "params": {"n": 6000}, "project": "LS", "ebox": {"Ta": 38, "clog": 0.5}}
    r = c.post("/api/v1/sewing/export/report", json=body, headers=h)
    assert r.status_code == 200
    xml = zipfile.ZipFile(io.BytesIO(r.content)).read("word/document.xml").decode()
    assert "电控箱：热、电容寿命、开关时间" in xml and "定期清理" in xml
    r0 = c.post("/api/v1/sewing/export/report", json=dict(body, ebox=None), headers=h)
    assert "电控箱：热" not in zipfile.ZipFile(io.BytesIO(r0.content)).read("word/document.xml").decode()
    x = c.post("/api/v1/sewing/export/params", json=dict(body, lang="en"), headers=h)
    assert b"Control box" in zipfile.ZipFile(io.BytesIO(x.content)).read("xl/workbook.xml")
    s = c.post("/api/v1/sewing/cae/ebox/step", json={"machine": "lockstitch", "ebox": {"L": 300, "fins": 6}}, headers=h)
    assert s.status_code == 200 and s.content.startswith(b"ISO-10303-21") and "300x160x90" in s.headers["content-disposition"]
    assert fk.posted[-1]["params"]["fins"] == 6


def test_ai_drafts_control_box_changes(ebox, monkeypatch):
    """一句话改电控箱参数（规则版）：“车间 40 度、飞絮堵塞 0.5”→ Ta、clog；假如题照算照给，红灯列出来，不退回"""
    c, h, _ = ebox
    monkeypatch.setattr(main.state.ai, "provider", "none")
    r = c.post("/api/v1/sewing/ai/draft", json={"machine": "lockstitch", "params": {"n": 6000}, "target": "ebox", "ebox": {},
                                                 "sentence": "车间夏天 40 度，飞絮堵塞 0.5，电控箱会不会报过热"}, headers=h).json()
    assert r["status"] == "ok" and {x["key"]: x["new"] for x in r["changes"]} == {"Ta": 40, "clog": 0.5}
    assert r["params"]["Ta"] == 40 and {x["key"] for x in r["after_bad"]} >= {"ths", "tj"}


def test_freecad_package_has_the_control_box(ebox):
    import io
    import zipfile
    c, h, _ = ebox
    z = zipfile.ZipFile(io.BytesIO(c.get("/api/v1/sewing/freecad.zip", headers=h).content))
    names = z.namelist()
    assert "Mod/WenQuestSewing/sewcore/ebox.py" in names
    assert "WQS_Ebox" in z.read("Mod/WenQuestSewing/wqsew_gui.py").decode()


def test_chain_submits_thermal_once_and_reports_failures(ebox):
    """流体算完后连着两次打开：温度场只交一次；温度场失败 → 任务标失败、写明原因（不再一直“计算中”）"""
    c, h, fk = ebox
    jid = c.post("/api/v1/sewing/cae/ebox", json={"machine": "lockstitch", "ebox": {}}, headers=h).json()["id"]
    fk.jobs[jid]["status"] = "done"
    c.get(f"/api/v1/sewing/cae/jobs/{jid}", headers=h)
    c.get(f"/api/v1/sewing/cae/jobs/{jid}", headers=h)
    thermal = [k for k, v in fk.jobs.items() if v["kind"] == "fea"]
    assert len(thermal) == 1
    fk.jobs[thermal[0]].update(status="failed", error="网格划不出来")
    s = c.get(f"/api/v1/sewing/cae/jobs/{jid}", headers=h).json()
    assert s["status"] == "failed" and "网格划不出来" in s["error"]
    assert next(x for x in c.get("/api/v1/sewing/cae/jobs", headers=h).json()["jobs"] if x["jid"] == jid)["status"] == "failed"


def test_report_takes_cae_only_for_the_same_box(ebox):
    """计算书的“CAE 分析结果”只带电控箱参数一样的那次复核（换了外壳、车间温度，旧结果不算数）"""
    import io
    import zipfile
    c, h, fk = ebox
    box = {"fins": 4}
    jid = c.post("/api/v1/sewing/cae/ebox", json={"machine": "lockstitch", "params": {}, "ebox": box}, headers=h).json()["id"]
    fk.jobs[jid]["status"] = "done"
    c.get(f"/api/v1/sewing/cae/jobs/{jid}", headers=h)
    fk.jobs[next(k for k, v in fk.jobs.items() if v["kind"] == "fea")]["status"] = "done"
    assert c.get(f"/api/v1/sewing/cae/jobs/{jid}", headers=h).json()["status"] == "done"

    def doc(e):
        r = c.post("/api/v1/sewing/export/report", json={"machine": "lockstitch", "params": {}, "ebox": e}, headers=h)
        return zipfile.ZipFile(io.BytesIO(r.content)).read("word/document.xml").decode()
    assert "箱子到车间热阻：CAE 与按尺寸公式对照" in doc(box)
    assert "箱子到车间热阻：CAE 与按尺寸公式对照" not in doc({"fins": 8})
    assert "箱子到车间热阻：CAE 与按尺寸公式对照" not in doc(None)


def test_own_enclosure_step(ebox):
    """企业自己的外壳 STEP：读入、流体、温度场按整体均匀发热"""
    import json as js
    c, h, fk = ebox
    r = c.post("/api/v1/sewing/cae/ebox/upload", headers=h, files={"file": ("box.step", b"ISO-10303-21;", "application/step")},
               data={"machine": "lockstitch", "params": js.dumps({}), "ebox": js.dumps({"Ta": 38})}).json()
    jid = r["id"]
    assert fk.posted[-1]["kind"] == "cfd" and fk.posted[-1]["setup"]["flow"]["air_t_c"] == 38
    fk.jobs[jid]["status"] = "done"
    c.get(f"/api/v1/sewing/cae/jobs/{jid}", headers=h)
    th = fk.posted[-1]
    assert th["setup"]["thermal"][0]["type"] == "heat_body" and th["setup"]["thermal"][0]["power_w"] > 20
    assert c.post("/api/v1/sewing/cae/ebox/upload", headers=h, files={"file": ("x.step", b"", "application/step")},
                  data={"machine": "lockstitch"}).status_code == 400


def test_thermal_rows_need_matching_faces():
    with pytest.raises(ValueError):
        ebox_thermal_rows(EXAMPLE, [dict(id=99, area_mm2=1, h_w_m2k=3.0)], 6.0, 40)
