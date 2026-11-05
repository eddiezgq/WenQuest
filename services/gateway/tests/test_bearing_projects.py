"""第 64 轮第 7 步（7a）：问渠轴承的云端项目——开通企业授权的单位才能用；设计项目和工艺模板两类、可按类型筛；
同单位共享，别的单位看不到；只留最近 20 版；两人同时改时后存的人收到冲突，内容不被覆盖；恢复旧版成为新的一版；留痕；
与凸轮的库分开。"""
import sqlite3
from pathlib import Path

from app import bearing_projects as BP
from app import main
from tests.test_course_pack import client  # noqa: F401
from tests.test_materials import login
from tests.test_sewing_api import UID, sc  # noqa: F401  (sc: 假 Moodle，"s" = 张工)

DESIGN = {"type": "deep_groove", "size": {"d": 30, "D": 58, "B": 16}, "inner": {"Dw": 8.5, "Z": 10}}
PROCESS = {"rings": {"inner": {"ops": [{"no": 10, "kind": "turn", "features": {}}]}}}
URL = "/api/v1/bearing/projects"


def test_projects_need_login_and_a_license(sc):  # noqa: F811
    c = sc
    assert c.get(URL).status_code == 401
    h = login(c, "s")                                         # 登录了、没开通
    assert c.get(URL, headers=h).status_code == 403
    assert c.post(URL, json={"name": "x", "body": DESIGN}, headers=h).status_code == 403


def test_two_kinds_share_versions_conflicts_and_isolation(sc):  # noqa: F811
    c = sc
    admin, s = login(c), login(c, "s")
    UID["s"] = c.get("/api/v1/me", headers=s).json()["id"]
    assert c.post("/api/v1/admin/sewing/licenses", json={"username": "s", "org": "甲轴承厂"}, headers=admin).json()["ok"]

    d = c.post(URL, json={"name": "6206 减速器", "body": DESIGN}, headers=s).json()
    t = c.post(URL, json={"name": "深沟球套圈工艺", "kind": "process", "body": PROCESS}, headers=s).json()
    assert d["kind"] == "design" and t["kind"] == "process" and d["created_name"] == "张工"
    assert c.post(URL, json={"name": "x", "kind": "cam", "body": DESIGN}, headers=s).status_code == 422
    assert {x["name"] for x in c.get(URL, headers=s).json()["projects"]} == {"6206 减速器", "深沟球套圈工艺"}
    assert [x["name"] for x in c.get(URL + "?kind=process", headers=s).json()["projects"]] == ["深沟球套圈工艺"]
    assert [x["name"] for x in c.get(URL + "?kind=design", headers=s).json()["projects"]] == ["6206 减速器"]
    # the third kind: the company's own product catalogue (plan section 十七 K3), listed apart from the others
    k = c.post(URL, json={"name": "本厂产品目录", "kind": "catalog", "body": {"rows": [{"model": "X1"}]}}, headers=s).json()
    assert k["kind"] == "catalog"
    assert [x["name"] for x in c.get(URL + "?kind=catalog", headers=s).json()["projects"]] == ["本厂产品目录"]
    assert c.delete(f"{URL}/{k['id']}", headers=s).status_code == 200
    assert c.get(URL + "?kind=cam", headers=s).status_code == 400
    # 别的单位（管理员 = 问渠）看不到、打不开、存不了；凸轮的项目库里也没有
    assert c.get(URL, headers=admin).json()["projects"] == []
    assert c.get(f"{URL}/{d['id']}", headers=admin).status_code == 404
    assert c.put(f"{URL}/{d['id']}", json={"body": DESIGN, "base": 1}, headers=admin).status_code == 404
    assert all(x["name"] != "6206 减速器" for x in c.get("/api/v1/cam/projects", headers=s).json()["projects"])

    # 同单位：张工调到“问渠”，与管理员共享
    assert c.post("/api/v1/admin/sewing/licenses", json={"username": "s", "org": "问渠"}, headers=admin).json()["ok"]
    q = c.post(URL, json={"name": "主轴成对", "body": DESIGN}, headers=s).json()
    assert [x["name"] for x in c.get(URL, headers=admin).json()["projects"]] == ["主轴成对"]
    r = c.put(f"{URL}/{q['id']}", json={"body": {**DESIGN, "type": "angular"}, "base": 1}, headers=admin)
    assert r.status_code == 200 and r.json()["version"] == 2
    r = c.put(f"{URL}/{q['id']}", json={"body": {**DESIGN, "type": "tapered"}, "base": 1}, headers=s)
    assert r.status_code == 409 and r.json()["version"] == 2 and r.json()["updated_by"] != UID["s"]
    assert c.get(f"{URL}/{q['id']}", headers=s).json()["body"]["type"] == "angular"          # 没被覆盖
    r = c.post(f"{URL}/{q['id']}/restore", json={"version": 1, "base": 2}, headers=s).json()
    assert r["version"] == 3 and r["body"] == DESIGN and r["history"][0]["note"] == "restored v1"

    v = 3
    for i in range(22):
        v = c.put(f"{URL}/{q['id']}", json={"body": {**DESIGN, "n": i}, "base": v}, headers=s).json()["version"]
    h = c.get(f"{URL}/{q['id']}", headers=s).json()["history"]
    assert len(h) == BP.KEEP == 20 and h[0]["version"] == v == 25
    big = {"x": "a" * (BP.MAX_BYTES + 10)}
    assert c.put(f"{URL}/{q['id']}", json={"body": big, "base": v}, headers=s).status_code == 413

    assert c.delete(f"{URL}/{q['id']}", headers=admin).json()["ok"]
    assert c.get(URL, headers=s).json()["projects"] == []
    with sqlite3.connect(str(Path(main.state.settings.data_dir) / "bearing.db")) as db:
        acts = [r[0] for r in db.execute("select action from log where project=? order by id", (q["id"],))]
        assert acts[:4] == ["create", "save", "restore v1", "save"] and acts[-1] == "delete"


def test_cookie_works_like_the_bearing_service_sends_it(sc):  # noqa: F811
    c = sc
    admin = login(c)
    c.cookies.set("wq_sso", admin["Authorization"].split(" ", 1)[1])
    try:
        r = c.post(URL, json={"name": "从轴承服务存的", "body": DESIGN})
        assert r.status_code == 200 and r.json()["version"] == 1
    finally:
        c.cookies.clear()
