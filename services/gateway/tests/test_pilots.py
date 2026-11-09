"""第 97 轮：问渠质量 ERP 试点企业——邀请、验证码、排队开通、账号邮件、Caddy 办证书前的询问。"""
import asyncio
import json
import time

import pytest

from app import main
from tests.test_accounts import client  # noqa: F401  (the fixture: fake Moodle accounts)
from tests.test_orgs import admin, login


@pytest.fixture
def pc(client, tmp_path, monkeypatch):  # noqa: F811
    monkeypatch.setattr(main.state.settings, "region", "cn")
    monkeypatch.setattr(main.state.settings, "data_dir", str(tmp_path / "data"))
    monkeypatch.setattr(main.state.settings, "site_domain", "wenquestech.online")
    monkeypatch.setattr(main.state.settings, "public_url", "https://learn.wenquestech.online")
    monkeypatch.setenv("WQ_PILOT_QUEUE", str(tmp_path / "queue"))
    monkeypatch.setenv("WQ_PILOT_MAX", "2")
    (tmp_path / "queue").mkdir()
    client.queue = tmp_path / "queue"
    return client


def heartbeat(q, mb=3000, age=0):
    (q / "host.json").write_text(json.dumps({"mem_free_mb": mb, "ts": time.time() - age}))


def last_mail(to):
    return [x for x in main.state.mailer.outbox if x["to"] == to][-1]


def invite(c, email="boss@acme.cn"):
    r = c.post("/api/v1/admin/pilots/invite", json={"email": email, "company": "艾克米五金"}, headers=admin(c))
    assert r.status_code == 200, r.text
    link = r.json()["link"]
    assert link.startswith("https://wenquestech.online/pilot/?t=") and link in last_mail(email)["text"]
    return link.split("t=")[1]


def code_for(c, token, email="boss@acme.cn"):
    assert c.post(f"/api/v1/public/pilot/{token}/code").status_code == 200
    return last_mail(email)["subject"][-6:]


def test_only_admins_invite(pc):
    assert pc.post("/api/v1/admin/pilots/invite", json={"email": "a@b.cn"}).status_code in (401, 403)
    assert pc.post("/api/v1/admin/pilots/invite", json={"email": "a@b.cn"}, headers=login(pc, "t@school.org")).status_code == 403
    assert pc.post("/api/v1/admin/pilots/invite", json={"email": "nope"}, headers=admin(pc)).status_code == 400


def test_invite_register_and_open(pc):
    q = pc.queue
    heartbeat(q)
    token = invite(pc)
    info = pc.get(f"/api/v1/public/pilot/{token}").json()
    assert info["email"] == "bo***@acme.cn" and info["company"] == "艾克米五金" and not info["used"]
    code = code_for(pc, token)
    assert pc.post(f"/api/v1/public/pilot/{token}/code").status_code == 429          # one code a minute
    body = {"company": "艾克米五金有限公司", "id": "acme", "contact": "王老板", "code": "000000" if code != "000000" else "111111"}
    assert pc.post(f"/api/v1/public/pilot/{token}/apply", json=body).json()["error"] == "bad_code"
    for bad in ("Ab", "demo", "sewing", "1acme", "acme-"):
        r = pc.post(f"/api/v1/public/pilot/{token}/apply", json=body | {"code": code, "id": bad})
        assert r.status_code in (400, 422), (bad, r.text)
    r = pc.post(f"/api/v1/public/pilot/{token}/apply", json=body | {"code": code})
    assert r.status_code == 200 and r.json()["status"] == "queued"
    req = json.loads((q / "req-acme.json").read_text())
    assert req == req | {"id": "acme", "name": "艾克米五金有限公司", "contact": "王老板", "email": "boss@acme.cn", "lang": "zh"}
    assert pc.post(f"/api/v1/public/pilot/{token}/apply", json=body | {"code": code}).status_code == 409   # used once
    # no certificate before it is open
    assert pc.get("/api/v1/caddy/ask", params={"domain": "acme.qms.wenquestech.online"}).status_code == 404
    # the server installs it and hands back the sign-in
    (q / "state-acme.json").write_text(json.dumps({"id": "acme", "status": "installing"}))
    asyncio.run(main.pilots_collect())
    assert pc.get(f"/api/v1/public/pilot/{token}/status").json() == {"status": "installing", "url": None}
    (q / "res-acme.json").write_text(json.dumps({"id": "acme", "email": "boss@acme.cn", "password": "Xy7-abc-def-12",
                                                 "url": "https://acme.qms.wenquestech.online",
                                                 "erp_url": "https://acme.qms-erp.wenquestech.online"}))
    asyncio.run(main.pilots_collect())
    mail = last_mail("boss@acme.cn")
    assert "Xy7-abc-def-12" in mail["text"] and "acme.qms.wenquestech.online" in mail["text"] and "王老板" in mail["text"]
    assert not (q / "res-acme.json").exists()                                        # the password is only in the email
    assert pc.get(f"/api/v1/public/pilot/{token}/status").json()["url"] == "https://acme.qms.wenquestech.online"
    for d in ("acme.qms.wenquestech.online", "acme.qms-erp.wenquestech.online"):
        assert pc.get("/api/v1/caddy/ask", params={"domain": d}).status_code == 200
    for d in ("sewing.qms.wenquestech.online", "sewing.qms-erp.wenquestech.online"):      # the demo company (26f)
        assert pc.get("/api/v1/caddy/ask", params={"domain": d}).status_code == 200
    for d in ("other.qms.wenquestech.online", "acme.qms.example.com", "x.acme.qms.wenquestech.online",
              "sewing.qms.example.com"):
        assert pc.get("/api/v1/caddy/ask", params={"domain": d}).status_code == 404
    lst = pc.get("/api/v1/admin/pilots", headers=admin(pc)).json()
    assert lst["used"] == 1 and lst["max"] == 2 and lst["host"]["fresh"] and lst["tenants"][0]["status"] == "active"
    assert "token" not in lst["tenants"][0] and "password" not in json.dumps(lst)
    # stop and start go to the server as commands
    assert pc.post("/api/v1/admin/pilots/acme/stop", headers=admin(pc)).json()["status"] == "stopped"
    assert json.loads((q / "cmd-acme.json").read_text())["cmd"] == "stop"


def test_full_and_busy(pc):
    q = pc.queue
    token = invite(pc, "a@one.cn")
    code = code_for(pc, token, "a@one.cn")
    body = {"company": "一号厂", "id": "one", "contact": "甲", "code": code}
    heartbeat(q, mb=800)                                                             # too little memory
    assert pc.post(f"/api/v1/public/pilot/{token}/apply", json=body).json()["error"] == "server_busy"
    heartbeat(q, age=3600)                                                           # the runner is not running
    assert pc.post(f"/api/v1/public/pilot/{token}/apply", json=body).json()["error"] == "server_busy"
    heartbeat(q)
    assert pc.post(f"/api/v1/public/pilot/{token}/apply", json=body).status_code == 200
    t2 = invite(pc, "b@two.cn")
    c2 = code_for(pc, t2, "b@two.cn")
    assert pc.post(f"/api/v1/public/pilot/{t2}/apply", json=body | {"code": c2}).json()["error"] == "id_taken"
    assert pc.post(f"/api/v1/public/pilot/{t2}/apply", json=body | {"code": c2, "id": "two"}).status_code == 200
    r = pc.post("/api/v1/admin/pilots/invite", json={"email": "c@three.cn"}, headers=admin(pc))
    assert r.status_code == 409 and r.json()["error"] == "pilot_full"
    # a failed installation tells the administrator and frees nothing silently
    (q / "state-two.json").write_text(json.dumps({"id": "two", "status": "failed", "error": "disk full"}))
    asyncio.run(main.pilots_collect())
    assert pc.get(f"/api/v1/public/pilot/{t2}/status").json()["status"] == "failed"


def test_bad_invite_link(pc):
    assert pc.get("/api/v1/public/pilot/nonsense").status_code == 404
    assert pc.post("/api/v1/public/pilot/nonsense/code").status_code == 404
