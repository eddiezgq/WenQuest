"""第 39 轮：缝纫机设计软件网页版接口（来宾试算、企业开通、项目、出件、FreeCAD 安装包）。"""
import io
import json
import zipfile
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from app import main
from app.moodle import MoodleClient
from tests.test_course_pack import client  # noqa: F401  (fake Moodle: login(c) = 管理员 "teacher"，login(c, "s") = 普通用户)
from tests.test_course_pack import moodle as pack_moodle
from tests.test_materials import login

UID = {"s": 0}


def moodle(request: httpx.Request) -> httpx.Response:
    q = parse_qs(urlparse(str(request.url)).query)
    if (q.get("wsfunction") or [""])[0] == "core_user_get_users_by_field":
        body = parse_qs(request.content.decode())
        who = (body.get("values[0]") or q.get("values[0]") or [""])[0]
        return httpx.Response(200, json=[{"id": UID["s"], "username": "s", "fullname": "张工"}] if who in ("s", "s@factory.cn") else [])
    return pack_moodle(request)


@pytest.fixture
def sc(client):  # noqa: F811
    main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(moodle))
    main.state.moodle = MoodleClient("http://moodle.test", "moodle_mobile_app", main.state.http)
    return client


def test_guest_can_compute_but_not_export(client):  # noqa: F811
    s = client.get("/api/v1/sewing/schema").json()
    keys = [p["key"] for g in s["groups"] for p in g["params"]]
    assert {"n", "r", "l", "psi", "Td", "k"} <= set(keys)
    r = client.post("/api/v1/sewing/analyze", json={"params": {}}).json()
    assert r["ok"] and abs(r["key"]["F_bdc"] - 654) < 1 and r["proto"]["psi"] == 0
    r = client.post("/api/v1/sewing/analyze", json={"params": {"n": 6000, "psi": -20}}).json()
    assert not r["ok"] and r["trial"]["counts"]["skip"] == 30 and r["proto"]["n"] == 6000
    assert client.get("/api/v1/sewing/me").json() == {"login": False, "licensed": False, "admin": False}
    assert client.post("/api/v1/sewing/export/report", json={"params": {}}).status_code == 401
    h = login(client, "s")
    assert client.get("/api/v1/sewing/me", headers=h).json()["licensed"] is False
    assert client.post("/api/v1/sewing/export/report", json={"params": {}}, headers=h).status_code == 403
    assert client.get("/api/v1/sewing/projects", headers=h).status_code == 403
    assert client.get("/api/v1/sewing/freecad.zip", headers=h).status_code == 403


def test_license_projects_exports(sc):
    client = sc
    admin, user = login(client), login(client, "s")
    uid = UID["s"] = client.get("/api/v1/me", headers=user).json()["id"]
    assert client.post("/api/v1/admin/sewing/licenses", json={"username": "s", "org": "甲缝纫机厂"}, headers=user).status_code == 403
    assert client.post("/api/v1/admin/sewing/licenses", json={"username": "nobody", "org": "甲缝纫机厂"}, headers=admin).status_code == 404
    r = client.post("/api/v1/admin/sewing/licenses", json={"username": "s", "org": "甲缝纫机厂"}, headers=admin).json()
    assert r["ok"] and r["user_id"] == uid and r["name"] == "张工"
    assert client.get("/api/v1/admin/sewing/licenses", headers=admin).json()["licenses"][0]["org"] == "甲缝纫机厂"
    me = client.get("/api/v1/sewing/me", headers=user).json()
    assert me["licensed"] and me["org"] == "甲缝纫机厂"
    # 第 39 轮第 4 步：官网上的问渠凸轮用同一份开通，带全站登录 cookie 或 Bearer 来问
    tok = user["Authorization"].split(" ", 1)[1]
    for kw in ({"headers": user}, {"cookies": {"wq_sso": tok}}):
        im = client.get("/api/v1/industry/me", **kw).json()
        assert im["login"] and im["licensed"] and im["org"] == "甲缝纫机厂" and im["user_id"] == uid
    client.cookies.clear()
    assert client.get("/api/v1/industry/me").json()["login"] is False
    # 项目：存、改、列、删；别的单位看不到
    p = client.post("/api/v1/sewing/projects", json={"name": "GC-01 高速平缝机", "params": {"n": 5500, "zz": 1}}, headers=user).json()
    assert p["params"]["n"] == 5500 and "zz" not in p["params"]
    p2 = client.put(f"/api/v1/sewing/projects/{p['id']}", json={"name": "GC-01", "params": {"n": 5200}}, headers=user).json()
    assert p2["params"]["n"] == 5200 and p2["name"] == "GC-01"
    assert [x["name"] for x in client.get("/api/v1/sewing/projects", headers=user).json()["projects"]] == ["GC-01"]
    assert client.get(f"/api/v1/sewing/projects/{p['id']}", headers=admin).status_code == 404          # 管理员在“问渠”单位
    # 出件
    for kind, magic in (("report", b"PK"), ("card", b"PK"), ("params", b"PK"), ("dxf", b"0\nSECTION"), ("macro", b"# -*- coding")):
        r = client.post(f"/api/v1/sewing/export/{kind}", json={"params": {"n": 5200}, "project": "GC-01"}, headers=user)
        assert r.status_code == 200 and r.content.startswith(magic), kind
        assert "attachment" in r.headers["content-disposition"]
    j = client.post("/api/v1/sewing/export/json", json={"params": {"n": 5200}, "project": "GC-01"}, headers=user).json()
    assert j["format"] == "wenquest-sewing" and j["params"]["n"] == 5200
    r = client.post("/api/v1/sewing/export/step", json={"params": {}}, headers=user)
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        assert b"ISO-10303-21" in r.content[:200]
    z = zipfile.ZipFile(io.BytesIO(client.get("/api/v1/sewing/freecad.zip", headers=user).content))
    names = set(z.namelist())
    assert {"Mod/WenQuestSewing/InitGui.py", "Mod/WenQuestSewing/wqsew_feature.py", "Mod/WenQuestSewing/sewcore/design.py", "使用说明.txt"} <= names
    assert "Mod/WenQuestSewing/sewcore/report.py" not in names
    assert client.delete(f"/api/v1/sewing/projects/{p['id']}", headers=user).json()["ok"]
    assert client.delete(f"/api/v1/admin/sewing/licenses/{uid}", headers=admin).json()["ok"]
    assert client.get("/api/v1/sewing/me", headers=user).json()["licensed"] is False


def test_proto_page_served_from_web_edition(client, tmp_path):  # noqa: F811
    assert client.get("/api/v1/sewing/proto").status_code == 404
    from app import main
    d = tmp_path / "textbook" / "sewing" / "webed" / "labs"
    d.mkdir(parents=True)
    (d / "proto-lockstitch.html").write_text("<html>proto</html>", encoding="utf-8")
    assert main.state.settings.textbook_dir == str(tmp_path / "textbook")
    r = client.get("/api/v1/sewing/proto")
    assert r.status_code == 200 and "proto" in r.text and "frame-ancestors 'self'" in r.headers["content-security-policy"]


def test_bad_input_is_cleaned(client):  # noqa: F811
    r = client.post("/api/v1/sewing/analyze", json={"params": {"n": "abc", "fab": "silk", "r": 1e9, "l": None}}).json()
    assert r["params"]["n"] == 5000 and r["params"]["fab"] == "cotton" and r["params"]["r"] == 25 and r["params"]["l"] == 55
    json.dumps(r)


def test_machines_overlock_and_cover(sc):
    """第 40 轮：包缝机、绷缝机——参数表、计算、项目记机型、出件（绷缝机没有三维零件）"""
    client = sc
    s = client.get("/api/v1/sewing/schema?machine=overlock").json()
    assert [m["key"] for m in s["machines"]] == ["lockstitch", "overlock", "cover", "pattern", "embroid"] and s["machine"] == "overlock"
    assert "ll_r" in [p["key"] for g in s["groups"] for p in g["params"]] and "step" in s["kinds"]
    s = client.get("/api/v1/sewing/schema?machine=cover").json()
    assert "Lcm" in [p["key"] for g in s["groups"] for p in g["params"]] and "step" not in s["kinds"]
    r = client.post("/api/v1/sewing/analyze", json={"machine": "overlock", "params": {}}).json()
    assert r["machine"] == "overlock" and r["view"]["page"] == "model-overlock"
    r = client.post("/api/v1/sewing/analyze", json={"machine": "cover", "params": {"stitch": "602"}}).json()
    assert r["tables"][0]["rows"][-1][-1] == "10" and r["view"]["cfg"]["rr"] == 3.2
    assert client.post("/api/v1/sewing/analyze", json={"machine": "nope", "params": {}}).status_code == 422
    admin = login(client)
    p = client.post("/api/v1/sewing/projects", json={"name": "OL-1", "machine": "overlock", "params": {"D": 1.3}}, headers=admin).json()
    assert p["machine"] == "overlock" and p["params"]["D"] == 1.3 and "ll_r" in p["params"]
    lst = client.get("/api/v1/sewing/projects", headers=admin).json()["projects"]
    assert lst[0]["machine"] == "overlock"
    for kind in ("report", "card", "params", "dxf", "macro"):
        r = client.post(f"/api/v1/sewing/export/{kind}", json={"machine": "overlock", "params": {}, "project": "OL-1"}, headers=admin)
        assert r.status_code == 200, kind
    for kind in ("report", "card", "params"):
        r = client.post(f"/api/v1/sewing/export/{kind}", json={"machine": "cover", "params": {}, "project": "CV-1"}, headers=admin)
        assert r.status_code == 200, kind
    assert client.post("/api/v1/sewing/export/step", json={"machine": "cover", "params": {}}, headers=admin).status_code == 404
    j = client.post("/api/v1/sewing/export/json", json={"machine": "cover", "params": {}}, headers=admin).json()
    assert j["machine"] == "cover"
    assert client.get("/api/v1/sewing/proto?page=../../etc").status_code == 404


def test_machines_pattern_and_embroid(sc, tmp_path):
    """第 42 轮：电子花样机、多头刺绣机——参数表、上传针位表、项目存针位表、出件、样机页"""
    client = sc
    s = client.get("/api/v1/sewing/schema?machine=pattern").json()
    keys = [p["key"] for g in s["groups"] for p in g["params"]]
    assert {"pat", "TxR", "EA"} <= set(keys) and "step" not in s["kinds"] and "dxf" not in s["kinds"]
    csv = "x,y\n0,0\n3,0\n6,0\n9,0\n19,0\n22,0\n"
    r = client.post("/api/v1/sewing/analyze", json={"machine": "pattern", "params": {"pat": "csv", "pts": csv}}).json()
    assert r["params"]["pts"][4] == [19.0, 0.0] and r["view"]["page"] == "model-pattern"
    assert next(c for c in r["charts"] if c["key"] == "speed")["xr"][1] == 6
    r = client.post("/api/v1/sewing/analyze", json={"machine": "embroid", "params": {"n": 800}}).json()
    assert r["view"] == {"page": "embroid", "sync": "A", "cfg": {"H": 8, "F": 800, "s": 7.0, "n": 800}} and not r["ok"]
    admin = login(client)
    p = client.post("/api/v1/sewing/projects", json={"name": "PT-1", "machine": "pattern", "params": {"pat": "csv", "pts": csv}}, headers=admin).json()
    assert p["machine"] == "pattern" and p["params"]["pts"][4] == [19.0, 0.0]
    got = client.get(f"/api/v1/sewing/projects/{p['id']}", headers=admin).json()
    assert got["params"]["pat"] == "csv" and len(got["params"]["pts"]) == 6
    for m in ("pattern", "embroid"):
        for kind, magic in (("report", b"PK"), ("card", b"PK"), ("params", b"PK")):
            r = client.post(f"/api/v1/sewing/export/{kind}", json={"machine": m, "params": {"pat": "csv", "pts": csv} if m == "pattern" else {}, "project": "X"}, headers=admin)
            assert r.status_code == 200 and r.content.startswith(magic), (m, kind)
        assert client.post("/api/v1/sewing/export/step", json={"machine": m, "params": {}}, headers=admin).status_code == 404
        j = client.post("/api/v1/sewing/export/json", json={"machine": m, "params": {}}, headers=admin).json()
        assert j["machine"] == m
    z = zipfile.ZipFile(io.BytesIO(client.get("/api/v1/sewing/freecad.zip", headers=admin).content))
    assert {"Mod/WenQuestSewing/sewcore/pattern.py", "Mod/WenQuestSewing/sewcore/embroid.py"} <= set(z.namelist())
    d = tmp_path / "textbook" / "sewing" / "webed" / "labs"
    d.mkdir(parents=True)
    for page in ("model-pattern", "embroid"):
        (d / f"{page}.html").write_text(f"<html>{page}</html>", encoding="utf-8")
        r = client.get(f"/api/v1/sewing/proto?page={page}")
        assert r.status_code == 200 and page in r.text
