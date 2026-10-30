"""第 39 轮第 7 步（7a）：问渠凸轮的云端项目——开通企业授权的单位才能用；同单位共享，别的单位看不到；
每次保存留一版，只留最近 20 版；两人同时改时后存的人收到冲突，不会悄悄覆盖；恢复旧版成为新的一版；留痕。"""
import sqlite3
from pathlib import Path

from app import cam_projects as CP
from app import main
from tests.test_course_pack import client  # noqa: F401
from tests.test_materials import login
from tests.test_sewing_api import UID, sc  # noqa: F401  (sc: 假 Moodle，"s" = 张工)

CAM = {"kind": "cam", "segments": [{"kind": "rise", "deg": 120, "h": 30, "law": "cycloidal"}], "rb": 40}


def test_projects_need_login_and_a_license(sc):  # noqa: F811
    c = sc
    assert c.get("/api/v1/cam/projects").status_code == 401
    h = login(c, "s")                                         # 登录了、没开通
    assert c.get("/api/v1/cam/projects", headers=h).status_code == 403
    assert c.post("/api/v1/cam/projects", json={"name": "x", "body": CAM}, headers=h).status_code == 403


def test_share_versions_conflicts_and_isolation(sc):  # noqa: F811
    c = sc
    admin, s = login(c), login(c, "s")                  # 管理员当作“问渠”单位
    UID["s"] = c.get("/api/v1/me", headers=s).json()["id"]
    assert c.post("/api/v1/admin/sewing/licenses", json={"username": "s", "org": "甲凸轮厂"}, headers=admin).json()["ok"]

    # 甲凸轮厂的张工建一个；问渠单位（管理员）看不到、打不开
    p = c.post("/api/v1/cam/projects", json={"name": "送料凸轮", "body": CAM}, headers=s).json()
    assert p["version"] == 1 and p["created_name"] == "张工" and p["history"][0]["version"] == 1
    assert [x["name"] for x in c.get("/api/v1/cam/projects", headers=s).json()["projects"]] == ["送料凸轮"]
    assert c.get("/api/v1/cam/projects", headers=admin).json()["projects"] == []
    assert c.get(f"/api/v1/cam/projects/{p['id']}", headers=admin).status_code == 404
    assert c.put(f"/api/v1/cam/projects/{p['id']}", json={"body": CAM, "base": 1}, headers=admin).status_code == 404

    # 张工调到“问渠”单位：两人同单位，共享同一个项目（单位跟着开通走）
    assert c.post("/api/v1/admin/sewing/licenses", json={"username": "s", "org": "问渠"}, headers=admin).json()["ok"]
    q = c.post("/api/v1/cam/projects", json={"name": "凸轮系统 A", "kind": "system", "body": {"cams": []}},
                    headers=s).json()
    assert {x["name"] for x in c.get("/api/v1/cam/projects", headers=admin).json()["projects"]} == {"凸轮系统 A"}
    a = c.get(f"/api/v1/cam/projects/{q['id']}", headers=admin).json()
    b = c.get(f"/api/v1/cam/projects/{q['id']}", headers=s).json()
    assert a["opened"] == b["opened"] == 1 and a["body"] == {"cams": []} and a["kind"] == "system"

    # 管理员先存（第 2 版）；张工手里还是第 1 版，再存被拦下，告诉他谁、第几版
    r = c.put(f"/api/v1/cam/projects/{q['id']}", json={"body": {"cams": [1]}, "base": 1}, headers=admin)
    assert r.status_code == 200 and r.json()["version"] == 2
    r = c.put(f"/api/v1/cam/projects/{q['id']}", json={"body": {"cams": [2]}, "base": 1}, headers=s)
    assert r.status_code == 409
    cf = r.json()
    assert cf["error"] == "conflict" and cf["version"] == 2 and cf["updated_by"] != UID["s"]
    assert c.get(f"/api/v1/cam/projects/{q['id']}", headers=s).json()["body"] == {"cams": [1]}   # 没被覆盖
    # 他看了对方的版本后基于第 2 版再存，成功；也可以把自己的另存一份
    assert c.put(f"/api/v1/cam/projects/{q['id']}", json={"body": {"cams": [2]}, "base": 2},
                      headers=s).json()["version"] == 3
    copy = c.post("/api/v1/cam/projects", json={"name": "凸轮系统 A（张工的）", "kind": "system",
                                                     "body": {"cams": [2]}}, headers=s).json()
    assert copy["id"] != q["id"]

    # 恢复第 1 版：成为新的第 4 版，内容是第 1 版的
    r = c.post(f"/api/v1/cam/projects/{q['id']}/restore", json={"version": 1, "base": 3}, headers=admin).json()
    assert r["version"] == 4 and r["body"] == {"cams": []} and r["history"][0]["note"] == "restored v1"
    assert c.post(f"/api/v1/cam/projects/{q['id']}/restore", json={"version": 1, "base": 3},
                       headers=admin).status_code == 409                                   # 基于旧版恢复也被拦下

    # 只留最近 20 版
    v = 4
    for i in range(25):
        v = c.put(f"/api/v1/cam/projects/{q['id']}", json={"body": {"cams": [i]}, "base": v},
                       headers=s).json()["version"]
    h = c.get(f"/api/v1/cam/projects/{q['id']}", headers=s).json()["history"]
    assert len(h) == CP.KEEP == 20 and h[0]["version"] == v == 29 and h[-1]["version"] == 10
    assert c.get(f"/api/v1/cam/projects/{q['id']}?version=3", headers=s).status_code == 404   # 早就不留了
    old = c.get(f"/api/v1/cam/projects/{q['id']}?version=10", headers=s).json()
    assert old["opened"] == 10 and old["version"] == 29                                            # 看旧版，当前仍是 29

    # 太大的项目、空名字被拒
    big = {"x": "a" * (CP.MAX_BYTES + 10)}
    assert c.put(f"/api/v1/cam/projects/{q['id']}", json={"body": big, "base": v}, headers=s).status_code == 413
    assert c.post("/api/v1/cam/projects", json={"name": "", "body": CAM}, headers=s).status_code == 422

    # 删除：列表里没了；谁建、谁存、谁恢复、谁删都有记录
    assert c.delete(f"/api/v1/cam/projects/{copy['id']}", headers=admin).json()["ok"]
    assert copy["id"] not in [x["id"] for x in c.get("/api/v1/cam/projects", headers=s).json()["projects"]]
    with sqlite3.connect(str(Path(main.state.settings.data_dir) / "cam.db")) as db:
        acts = [r[0] for r in db.execute("select action from log where project=? order by id", (q["id"],))]
        assert acts[:4] == ["create", "save", "save", "restore v1"] and len(acts) == 4 + 25
        assert db.execute("select action from log where project=?", (copy["id"],)).fetchall()[-1][0] == "delete"


def test_cookie_works_like_the_cam_service_sends_it(sc):  # noqa: F811
    c = sc
    admin = login(c)
    tok = admin["Authorization"].split(" ", 1)[1]
    c.cookies.set("wq_sso", tok)
    try:
        r = c.post("/api/v1/cam/projects", json={"name": "从凸轮服务存的", "body": CAM})
        assert r.status_code == 200 and r.json()["version"] == 1
    finally:
        c.cookies.clear()
