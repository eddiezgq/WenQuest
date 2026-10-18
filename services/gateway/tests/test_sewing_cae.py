"""第 41 轮：缝纫机设计软件接入问渠 CAE（网关一侧）。数字工厂用假服务代替，真算的部分在 factory/digital/tests/test_design_sw.py。"""
import json
import math
import struct

import httpx
import numpy as np
import pytest

from app import main
from app.moodle import MoodleClient
from app.sewcore import cae_setup as CS
from app.sewcore import optimize as OPT
from tests.test_course_pack import client  # noqa: F401
from tests.test_materials import login
from tests.test_sewing_api import UID
from tests.test_sewing_api import moodle as sew_moodle

KEY = "k" * 32


class FakeFactory:
    """只模拟“设计软件接口”的形状：/api/design-sw/…"""

    def __init__(self):
        self.jobs, self.desc, self.n = {}, None, 0
        self.posted = []

    def faces(self):
        hs = CS._holes3d(self.desc)
        out = [dict(id=i, kind="cylinder", axis=h["axis"], axis_origin=h["center"], radius_mm=h["r"]) for i, h in enumerate(hs)]
        out += [dict(id=10, kind="plane", normal=[0, 0, 1], center=[0, 0, 0]), dict(id=11, kind="plane", normal=[0, 0, -1], center=[0, 0, 50])]
        return out

    def __call__(self, req: httpx.Request) -> httpx.Response:
        assert req.headers["authorization"] == "Bearer " + KEY
        path, q = req.url.path.removeprefix("/api/design-sw"), dict(req.url.params)
        if path == "/geometry":
            return httpx.Response(200, json={"sha": "abc", "faces": self.faces() if self.desc else
                                             [dict(id=10, kind="plane", normal=[0, 0, 1], center=[0, 0, 0]),
                                              dict(id=11, kind="plane", normal=[0, 0, 1], center=[0, 0, 80])]})
        if path == "/jobs" and req.method == "POST":
            b = json.loads(req.content)
            self.posted.append(b)
            if len([j for j in self.jobs.values() if j["org"] == b["org"]]) >= 3:
                return httpx.Response(429, json={"detail": "本单位今天的计算次数已用完"})
            self.n += 1
            jid = f"j{self.n}"
            self.jobs[jid] = dict(id=jid, org=b["org"], kind=b["kind"], status="queued", position=1, body=b)
            return httpx.Response(200, json={"id": jid, "status": "queued"})
        if path == "/jobs":
            js = [j for j in self.jobs.values() if j["org"] == q["org"]]
            return httpx.Response(200, json={"jobs": js, "used_today": len(js), "daily_limit": 3})
        if path == "/motors":
            return httpx.Response(200, json={"motors": [dict(name="伺服 0.55 kW", power_w=550, rated_nm=1.0, peak_nm=3.0, max_rpm=6000, inertia_kgm2=1e-4),
                                                        dict(name="伺服 1.5 kW", power_w=1500, rated_nm=6.0, peak_nm=18.0, max_rpm=6000, inertia_kgm2=4e-4)],
                                             "source": "测试"})
        parts = path.strip("/").split("/")
        if parts[0] == "jobs":
            j = self.jobs.get(parts[1])
            if not j or j["org"] != q.get("org"):
                return httpx.Response(404, json={"detail": "没有这个任务"})
            tail = parts[2] if len(parts) > 2 else ""
            if tail == "":
                return httpx.Response(200, json=dict(j, stats={"safety_factor": 6.5, "vm_max_mpa": 55.0, "u_max_mm": 0.01, "elements": 9000}))
            if tail == "fatigue":
                return httpx.Response(200, json={"summary": {"infinite": False, "life_hours": 4800 * 12}})
            if tail == "modal":
                return httpx.Response(200, json={"freqs": [{"mode": 1, "hz": 210.0}, {"mode": 2, "hz": 400.0}]})
            if tail == "series.bin":
                # 30 r/min 跑 3 转：曲柄转矩 = 峰值 1e-3 的正弦（换算后看是否乘了转速比的平方）
                n = 1200
                t = np.linspace(0, 6, n)
                head = json.dumps({"n": n, "names": ["t", "drive.crank"]}).encode()
                arr = np.stack([t, 1e-3 * np.sin(2 * math.pi * t / 2)], 1).astype("<f4")
                return httpx.Response(200, content=struct.pack("<4sI", b"WQC1", len(head)) + head + arr.tobytes())
            if tail == "surface.bin":
                P = np.array([[0, 0, 0], [10, 0, 0], [0, 10, 0], [0, 0, 10]], "<f4")
                T = np.array([[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]], "<u4")
                raw = struct.pack("<4sII", b"WQS1", 4, 4) + P.tobytes() + np.array([1, 2, 3, 4], "<f4").tobytes() + np.zeros(12, "<f4").tobytes() + T.tobytes()
                return httpx.Response(200, content=raw)
            if tail == "report":
                return httpx.Response(200, content=b"PK\x03\x04docx")
        return httpx.Response(404, json={"detail": "?"})


@pytest.fixture
def cae(client, monkeypatch):  # noqa: F811
    fk = FakeFactory()

    def route(req):
        return fk(req) if req.url.host == "factory.test" else sew_moodle(req)
    main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(route))
    main.state.moodle = MoodleClient("http://moodle.test", "moodle_mobile_app", main.state.http)
    monkeypatch.setattr(main.state.settings, "factory_url", "http://factory.test")
    monkeypatch.setattr(main.state.settings, "factory_cae_key", KEY)

    def part_step(d):
        fk.desc = d
        return b"ISO-10303-21;"
    monkeypatch.setattr(CS, "part_step", part_step)
    admin, user = login(client), login(client, "s")
    UID["s"] = client.get("/api/v1/me", headers=user).json()["id"]
    client.post("/api/v1/admin/sewing/licenses", json={"username": "s", "org": "甲缝纫机厂"}, headers=admin)
    return client, user, fk


def done(c, h, fk, jid):
    fk.jobs[jid]["status"] = "done"
    return c.get(f"/api/v1/sewing/cae/jobs/{jid}", headers=h).json()


def test_guest_and_unlicensed_cannot_use_cae(client):  # noqa: F811
    assert client.get("/api/v1/sewing/cae/options").status_code == 401
    assert client.post("/api/v1/sewing/cae/fea", json={"part": "ConnectingRod"}).status_code == 401
    h = login(client, "s")
    assert client.get("/api/v1/sewing/cae/options", headers=h).status_code == 403
    assert client.post("/api/v1/sewing/optimize", json={"goal": "balance"}, headers=h).status_code == 403


def test_fea_fatigue_contour_report_and_calc_report(cae):
    c, h, fk = cae
    o = c.get("/api/v1/sewing/cae/options", headers=h).json()
    assert o["connected"] and o["quota"] == {"used": 0, "limit": 3}
    assert [p["key"] for p in o["parts"]] == ["ConnectingRod", "NeedleCrank"] and o["kinds"]["mbd"]
    r = c.post("/api/v1/sewing/cae/fea", json={"machine": "lockstitch", "params": {"n": 5000, "mat": "40Cr-QT"}, "part": "ConnectingRod"}, headers=h).json()
    b = fk.posted[-1]
    assert b["org"] == "甲缝纫机厂" and b["kind"] == "fea" and b["setup"]["material_id"] == "40Cr-QT"
    sup, frc = b["setup"]["loads"]
    assert sup["type"] == "cyl_support" and sup["faces"] == [0] and frc["faces"] == [1]
    assert abs(math.hypot(*frc["vector_n"]) - abs(CS.fea_case("lockstitch", {"n": 5000}, "ConnectingRod")["ref_load"])) < 0.5
    lst = c.get("/api/v1/sewing/cae/jobs", headers=h).json()["jobs"]
    assert lst[0]["status"] == "queued" and lst[0]["position"] == 1
    j = done(c, h, fk, r["id"])
    ck = {x["key"]: x for x in j["result"]["checks"]}
    assert ck["sf"]["state"] == "ok" and ck["life"]["value"].startswith("12.0") and ck["life"]["state"] == "ok"
    png = c.get(f"/api/v1/sewing/cae/jobs/{r['id']}/image.png", headers=h)
    assert png.status_code == 200 and png.content[:4] == b"\x89PNG"
    assert c.get(f"/api/v1/sewing/cae/jobs/{r['id']}/report.docx", headers=h).content[:2] == b"PK"
    # 算完的结果进计算书
    rep = c.post("/api/v1/sewing/export/report", json={"machine": "lockstitch", "params": {"n": 5000, "mat": "40Cr-QT"}}, headers=h)
    assert rep.status_code == 200
    import io
    import zipfile
    xml = zipfile.ZipFile(io.BytesIO(rep.content)).read("word/document.xml").decode()
    assert "CAE 分析结果" in xml
    # 别的单位看不到
    assert c.get(f"/api/v1/sewing/cae/jobs/{r['id']}", headers=login(c)).status_code in (403, 404)


def test_frame_mbd_motor_quota(cae):
    c, h, fk = cae
    fk.desc = None
    r = c.post("/api/v1/sewing/cae/frame", files={"file": ("frame.step", b"ISO-10303-21;", "application/step")},
               data={"machine": "lockstitch", "params": json.dumps({"n": 5000})}, headers=h).json()
    loads = fk.posted[-1]["setup"]["loads"]
    assert loads[0] == {"type": "fixed", "faces": [10]} and loads[1]["faces"] == [11]
    j = done(c, h, fk, r["id"])
    assert j["result"]["f1"] == 210.0 and j["result"]["apply"] == {"fn": 210}
    assert j["result"]["checks"][0]["state"] == "ok"            # 2 × 5000/60 / 210 = 0.79
    r = c.post("/api/v1/sewing/cae/mbd", json={"machine": "overlock", "params": {"n": 6000}}, headers=h).json()
    st = fk.posted[-1]["setup"]
    assert st["gravity"] is False and st["drives"][0]["value"] == round(2 * math.pi * CS.N_SIM / 60, 5)
    j = done(c, h, fk, r["id"])
    assert abs(j["result"]["torque_peak_mbd"] - 1e-3 * (6000 / CS.N_SIM) ** 2) < 1e-3     # 乘了转速比的平方
    m = c.post("/api/v1/sewing/cae/motor", json={"machine": "lockstitch", "params": {"n": 5000}}, headers=h).json()
    assert m["pick"]["name"] == "伺服 1.5 kW" and m["peak_nm"] > 1
    # 每天上限：假服务第 3 个之后回 429
    assert c.post("/api/v1/sewing/cae/mbd", json={"machine": "lockstitch", "params": {}}, headers=h).status_code == 200
    r = c.post("/api/v1/sewing/cae/mbd", json={"machine": "lockstitch", "params": {}}, headers=h)
    assert r.status_code == 429


def test_not_connected(cae, monkeypatch):
    c, h, _ = cae
    monkeypatch.setattr(main.state.settings, "factory_url", "")
    assert c.get("/api/v1/sewing/cae/options", headers=h).json()["connected"] is False
    assert c.post("/api/v1/sewing/cae/mbd", json={"params": {}}, headers=h).status_code == 503
    # 公式优化不靠数字工厂
    assert c.post("/api/v1/sewing/optimize", json={"machine": "lockstitch", "goal": "balance"}, headers=h).status_code == 200


def test_optimize_goals():
    r = OPT.run("lockstitch", {}, "balance")
    assert 0.35 <= r["candidates"][0]["params"]["k"] <= 0.55 and r["candidates"][0]["bad"] == 0
    r = OPT.run("lockstitch", {}, "speed")
    assert r["candidates"][0]["params"]["n"] >= 4500
    r = OPT.run("overlock", {}, "upper")
    assert r["candidates"] and r["candidates"][0]["note"]["gamma_min"] >= 40
    r = OPT.run("cover", {}, "timing")
    assert r["candidates"][0]["value"] > 0
    assert OPT.run("lockstitch", {}, "takeup")["candidates"]


def test_cae_setup_formulas():
    p = {"n": 5000}
    case = CS.fea_case("lockstitch", p, "ConnectingRod")
    assert len(case["series"]) == 360 and case["block_seconds"] == pytest.approx(0.012)
    assert CS.fea_case("cover", p, "ConnectingRod") is None and CS.parts("cover") == []
    assert CS.fea_case("overlock", p, "LL_Rocker")["ref_load"] != 0
    T = CS.spindle_torque("lockstitch", p)
    assert len(T) == 360 and max(T) > CS.analytic_torque_peak(sewcore_clean("lockstitch", p), 5000, 0.12) * 0.5
    assert CS.life_years({"infinite": True}) == math.inf and CS.life_years({"life_hours": 4800}) == 1
    with pytest.raises(ValueError):
        CS.frame_setup([{"id": 1, "kind": "cylinder"}])


def sewcore_clean(machine, p):
    from app import sewcore
    return sewcore.get(machine).clean(p)
