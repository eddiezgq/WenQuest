"""China server: trial accounts for organisations, not individuals (round 50)."""
import time

import pytest

from app import main
from tests.test_accounts import USERS, client  # noqa: F401  (the fixture: fake Moodle accounts)


def login(c, who):
    r = c.post("/api/v1/auth/login", json={"username": who, "password": "Passw0rd"})
    return {"Authorization": "Bearer " + r.json()["token"]}


@pytest.fixture
def cn(client, tmp_path, monkeypatch):  # noqa: F811
    monkeypatch.setattr(main.state.settings, "region", "cn")
    monkeypatch.setattr(main.state.settings, "data_dir", str(tmp_path / "data"))
    monkeypatch.setattr(main.state.settings, "cn_max_orgs", 2)
    return client


def admin(c):
    return login(c, "admin@wq.com")


def test_not_on_us_server(client, tmp_path, monkeypatch):  # noqa: F811
    monkeypatch.setattr(main.state.settings, "data_dir", str(tmp_path / "d"))
    assert client.get("/api/v1/admin/orgs", headers=login(client, "admin@wq.com")).status_code == 404
    assert client.get("/api/v1/public/site").json() == {"region": "us"}


def test_signup_closed_on_cn(cn):
    r = cn.post("/api/v1/auth/code", json={"email": "a@b.cn", "purpose": "register"})
    assert r.status_code == 403 and r.json()["error"] == "signup_closed"
    r = cn.post("/api/v1/auth/register", json={"email": "a@b.cn", "code": "123456", "password": "abc12345", "firstname": "三",
                                               "lastname": "张", "role": "student", "agree": True})
    assert r.status_code == 403 and r.json()["error"] == "signup_closed"
    assert cn.get("/api/v1/public/site").json()["signup"] is False


def test_orgs_seats_limits_and_expiry(cn):
    h = admin(cn)
    assert cn.post("/api/v1/admin/orgs", json={"name": "某某缝纫机有限公司"}, headers=login(cn, "t@school.org")).status_code == 403
    o = cn.post("/api/v1/admin/orgs", json={"name": "某某缝纫机有限公司", "kind": "company", "contact": "王工", "phone": "13800138000"},
                headers=h).json()
    assert o["seats"] == 5 and o["live"] and o["days_left"] == 90
    assert cn.post("/api/v1/admin/orgs", json={"name": "某某缝纫机有限公司"}, headers=h).json()["error"] == "org_exists"
    o2 = cn.post("/api/v1/admin/orgs", json={"name": "某某职业技术学院", "kind": "school", "seats": 2}, headers=h).json()
    r = cn.post("/api/v1/admin/orgs", json={"name": "第三家"}, headers=h)          # the limit (2 here, 100 in production)
    assert r.status_code == 409 and r.json()["error"] == "org_limit"
    assert cn.post("/api/v1/admin/orgs", json={"name": "太多账号", "seats": 21}, headers=h).status_code in (400, 409)
    # accounts: a Moodle account that may create courses, a generated password shown once
    a = cn.post(f"/api/v1/admin/orgs/{o2['id']}/members", json={"name": "李老师", "phone": "13900139000", "email": "li@school.cn"},
                headers=h).json()
    assert a["login"] == "li@school.cn" and len(a["password"]) == 12 and USERS[a["userid"]]["teacher"]
    cn.post(f"/api/v1/admin/orgs/{o2['id']}/members", json={"name": "赵老师", "phone": "13900139001", "email": "zhao@school.cn"}, headers=h)
    r = cn.post(f"/api/v1/admin/orgs/{o2['id']}/members", json={"name": "钱老师", "phone": "13900139002", "email": "qian@school.cn"},
                headers=h)
    assert r.status_code == 409 and r.json()["error"] == "seats_full"
    # the account signs in while the trial is live
    r = cn.post("/api/v1/auth/login", json={"username": "li@school.cn", "password": a["password"]})
    assert r.status_code == 200
    tok = {"Authorization": "Bearer " + r.json()["token"]}
    assert cn.get("/api/v1/me", headers=tok).status_code == 200
    # the trial ends: sign-in and the open session are refused; the sweep suspends the account in Moodle
    import sqlite3
    db = sqlite3.connect(main.state.settings.data_dir + "/orgs.db")
    db.execute("update org set expires=? where id=?", (int(time.time()) - 10, o2["id"]))
    db.commit()
    assert cn.get("/api/v1/me", headers=tok).json()["error"] == "org_expired"
    assert cn.post("/api/v1/auth/login", json={"username": "li@school.cn", "password": a["password"]}).json()["error"] == "org_expired"
    import asyncio
    asyncio.run(main.orgs_sweep())
    assert USERS[a["userid"]]["suspended"]
    lst = cn.get("/api/v1/admin/orgs", headers=h).json()
    assert lst["live"] == 1 and lst["max"] == 2
    # extend: works again
    o2b = cn.put(f"/api/v1/admin/orgs/{o2['id']}", json={"extend_days": 30}, headers=h).json()
    assert o2b["live"] and o2b["days_left"] == 30 and not USERS[a["userid"]]["suspended"]
    assert cn.post("/api/v1/auth/login", json={"username": "li@school.cn", "password": a["password"]}).status_code == 200
    # one account stopped; a new password
    cn.put(f"/api/v1/admin/orgs/{o2['id']}/members/{a['userid']}", json={"stopped": True}, headers=h)
    assert USERS[a["userid"]]["suspended"]
    cn.put(f"/api/v1/admin/orgs/{o2['id']}/members/{a['userid']}", json={"stopped": False}, headers=h)
    p = cn.post(f"/api/v1/admin/orgs/{o2['id']}/members/{a['userid']}/password", headers=h).json()
    assert cn.post("/api/v1/auth/login", json={"username": "li@school.cn", "password": p["password"]}).status_code == 200
    # seats cannot drop below the accounts in use; the administrator is never gated
    assert cn.put(f"/api/v1/admin/orgs/{o2['id']}", json={"seats": 1}, headers=h).json()["error"] == "seats_below_used"
    assert cn.get("/api/v1/me", headers=h).status_code == 200
