"""China server: a trial request with a verified email is opened at once; the owner adds colleagues (round 96)."""
import re
import sqlite3
from pathlib import Path

import pytest

from app import main
from tests.test_accounts import (  # noqa: F401  (the fixture: fake Moodle accounts)
    USERS,
    client,
)


@pytest.fixture
def cn(client, tmp_path, monkeypatch):  # noqa: F811
    s = main.state.settings
    monkeypatch.setattr(s, "region", "cn")
    monkeypatch.setattr(s, "data_dir", str(tmp_path / "data"))
    monkeypatch.setattr(s, "site_domain", "wenquestech.online")
    main.state.sms = None
    main.state.mailer.skip = "@m.wenquestech.online"
    return client


def mail_code(email):
    for msg in reversed(main.state.mailer.outbox):
        if msg["to"] == email and "验证码" in msg["subject"]:
            return re.search(r"\b(\d{6})\b", msg["text"]).group(1)
    raise AssertionError("no code mail")


def apply(c, org="杰克科技股份有限公司", name="郑吉", phone="13800138000", email="zj@qq.com", code=None, ip="1.1.1.1", **kw):
    h = {"x-forwarded-for": ip}
    Path(main.state.settings.data_dir).mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(main.state.settings.data_dir + "/demo-request.db")
    db.execute("create table if not exists vcode(email text, hash text, expires real, tries integer default 0, created real)")
    db.execute("update vcode set created = created - 120")          # past the one-a-minute gap
    db.commit()
    if code is None:
        assert c.post("/api/v1/public/demo-request/code", json={"email": email}, headers=h).json() == {"sent": True}
        code = mail_code(email)
    body = {"org": org, "name": name, "phone": phone, "email": email, "consent": True, "trial": True, "seats": 3,
            "code": code, **kw}
    return c.post("/api/v1/public/demo-request", json=body, headers=h)


def bearer(c, user, pw):
    r = c.post("/api/v1/auth/login", json={"username": user, "password": pw})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["token"]}


def admin(c):
    return bearer(c, "admin@wq.com", "Passw0rd")


def test_verified_request_opens_at_once_and_owner_adds_colleagues(cn):
    r = apply(cn, code="", ip="9.9.9.1")
    assert r.json()["error"] == "code_required"
    r = apply(cn, code="000000", email="x@qq.com", ip="9.9.9.1")
    assert r.json()["error"] == "code_wrong"
    r = apply(cn, ip="9.9.9.1")
    assert r.json() == {"ok": True, "opened": True, "manual": ""}
    sent = main.state.mailer.outbox[-1]
    assert sent["to"] == "zj@qq.com" and "已开通" in sent["subject"]
    pw = re.search(r"初始密码：(\S+)", sent["text"]).group(1)
    h = bearer(cn, "13800138000", pw)                              # the phone signs in too
    o = cn.get("/api/v1/my/org", headers=h).json()
    assert o["name"] == "杰克科技股份有限公司" and o["seats"] == 3 and o["auto"] == 1 and o["members"][0]["owner"] == 1
    # the owner adds two colleagues, the second without an email
    a = cn.post("/api/v1/my/org/members", json={"name": "王工", "phone": "13900139000", "email": "wang@qq.com"}, headers=h).json()
    b = cn.post("/api/v1/my/org/members", json={"name": "李工", "phone": "13700137000"}, headers=h).json()
    assert a["login"] == "wang@qq.com" and b["login"] == "13700137000"
    full = cn.post("/api/v1/my/org/members", json={"name": "赵工", "phone": "13600136000"}, headers=h)
    assert full.status_code == 409 and full.json()["error"] == "seats_full"
    # stop, restore, new password; not the owner's own account
    assert cn.put(f"/api/v1/my/org/members/{b['userid']}", json={"stopped": True}, headers=h).json() == {"ok": True}
    assert USERS[b["userid"]]["suspended"] is True
    assert cn.put(f"/api/v1/my/org/members/{b['userid']}", json={"stopped": False}, headers=h).json() == {"ok": True}
    me = o["members"][0]["userid"]
    assert cn.put(f"/api/v1/my/org/members/{me}", json={"stopped": True}, headers=h).status_code == 403
    npw = cn.post(f"/api/v1/my/org/members/{a['userid']}/password", headers=h).json()
    assert npw["login"] == "wang@qq.com"
    # a colleague is not an owner
    ha = bearer(cn, "wang@qq.com", npw["password"])
    assert cn.get("/api/v1/my/org", headers=ha).status_code == 404
    # the administrator sees it marked
    lst = cn.get("/api/v1/admin/orgs", headers=admin(cn)).json()
    assert lst["auto"] is True and lst["orgs"][0]["auto"] == 1


def test_repeats_and_limits_go_to_the_administrator(cn, monkeypatch):
    assert apply(cn).json()["opened"] is True
    # the same organisation, the same email, the same phone
    assert apply(cn, phone="13900139001", email="other@qq.com", ip="3.3.3.1").json() == {"ok": True, "opened": False, "manual": "known_org"}
    assert apply(cn, org="别的公司", phone="13900139002", email="zj@qq.com", ip="3.3.3.2").json()["manual"] == "known_person"
    assert apply(cn, org="第三家公司", phone="13800138000", email="third@qq.com", ip="3.3.3.3").json()["manual"] == "known_person"
    # a landline cannot sign in by phone: by hand
    assert apply(cn, org="座机公司", phone="0571-88888888", email="tel@qq.com", ip="3.3.3.4").json()["manual"] == "not_mobile"
    # two openings an hour per network address
    assert apply(cn, org="二号公司", phone="13500135000", email="b@qq.com").json()["opened"] is True
    assert apply(cn, org="三号公司", phone="13500135001", email="c@qq.com").json()["manual"] == "ip_hourly"
    # a day's limit
    monkeypatch.setattr(main.state.settings, "cn_auto_daily", 2)
    assert apply(cn, org="四号公司", phone="13500135002", email="d@qq.com", ip="2.2.2.2").json()["manual"] == "daily"
    # every request is still kept for the administrator
    rows = cn.get("/api/v1/admin/demo-request", headers=admin(cn)).json()["rows"]
    assert len(rows) == 8


def test_switch_off_sends_requests_to_the_administrator(cn):
    h = admin(cn)
    assert cn.put("/api/v1/admin/orgs-auto", json={"on": False}, headers=h).json() == {"auto": False}
    r = cn.post("/api/v1/public/demo-request", json={"org": "某学院", "name": "张老师", "phone": "13800138000",
                                                     "consent": True, "trial": True, "seats": 2})
    assert r.json() == {"ok": True}                                    # no code needed, nothing opened
    assert cn.get("/api/v1/admin/orgs", headers=h).json()["orgs"] == []
    assert cn.put("/api/v1/admin/orgs-auto", json={"on": True}, headers=h).json() == {"auto": True}


def test_administrator_makes_an_owner(cn):
    h = admin(cn)
    o = cn.post("/api/v1/admin/orgs", json={"name": "杰克科技", "kind": "company"}, headers=h).json()
    a = cn.post(f"/api/v1/admin/orgs/{o['id']}/members", json={"name": "郑吉", "phone": "13800138000"}, headers=h).json()
    hz = bearer(cn, "13800138000", a["password"])
    assert cn.get("/api/v1/my/org", headers=hz).status_code == 404
    assert cn.put(f"/api/v1/admin/orgs/{o['id']}/members/{a['userid']}", json={"owner": True}, headers=h).json() == {"ok": True}
    assert cn.get("/api/v1/my/org", headers=hz).json()["id"] == o["id"]


def test_quality_erp_trial_account_in_the_demo_company(cn, tmp_path, monkeypatch):
    """ops ADR-0027: asking for the quality ERP as well queues an account in the shared demo company; the runner's
    answer is emailed once, with the warning that the company is shared and reset every night."""
    import asyncio
    import json

    q = tmp_path / "queue"
    monkeypatch.setenv("WQ_PILOT_QUEUE", str(q))
    r = apply(cn, org="宁波某机械", phone="13512345670", email="erp@qq.com", ip="7.7.7.7", products=["问渠质量 ERP"])
    assert r.json()["opened"] is True
    assert "另发一封" in [x for x in main.state.mailer.outbox if x["to"] == "erp@qq.com"][-1]["text"]
    reqs = list(q.glob("trial-*.json"))
    assert len(reqs) == 1
    req = json.loads(reqs[0].read_text())
    assert req["email"] == "erp@qq.com" and req["name"] == "郑吉"
    (q / f"res-trial-{req['id']}.json").write_text(json.dumps({"id": req["id"], "email": "erp@qq.com",
                                                               "password": "Abc123def456", "expires": "2026-12-07",
                                                               "url": "https://qms.wenquestech.online"}))
    asyncio.run(main.pilots_collect())
    sent = main.state.mailer.outbox[-1]
    assert sent["subject"] == "问渠质量 ERP 体验账号" and "Abc123def456" in sent["text"] and "每晚还原" in sent["text"]
    assert not list(q.glob("res-trial-*"))
