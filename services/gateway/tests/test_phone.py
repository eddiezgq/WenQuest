"""China server: phone number + text-message code, accounts without email, WeChat sign-in (round 108)."""
import sqlite3
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from app import main
from app.phone import norm_phone
from app.sms import Sms, signature
from tests.test_accounts import (  # noqa: F401  (the fixture: fake Moodle accounts)
    USERS,
    client,
    moodle,
    user,
)


def test_signature_matches_alibaba_cloud_example():
    # The worked example in Alibaba Cloud's RPC signature (v1.0) documentation.
    p = {"Timestamp": "2016-02-23T12:46:24Z", "Format": "XML", "AccessKeyId": "testid", "Action": "DescribeRegions",
         "SignatureMethod": "HMAC-SHA1", "SignatureNonce": "3ee8c1b8-83d3-44af-a94f-4e0ad82fd6cf", "Version": "2014-05-26",
         "SignatureVersion": "1.0"}
    assert signature(p, "testsecret") == "OLeaidS1JvxuMvnyHOwuJ+uX5qY="
    sms = Sms("id", "secret", "问渠科技", "SMS_1", "https://dysmsapi.aliyuncs.com/", None)
    q = sms.params("13800138000", "123456", datetime(2026, 11, 6, tzinfo=timezone.utc), "n1")
    assert q["Action"] == "SendSms" and q["TemplateParam"] == '{"code": "123456"}' and q["Signature"]


def test_norm_phone():
    assert norm_phone("+86 138-0013-8000") == "13800138000"
    assert norm_phone("8613800138000") == "13800138000"
    assert norm_phone("12345") == "" and norm_phone("23800138000") == ""


@pytest.fixture
def cn(client, tmp_path, monkeypatch):  # noqa: F811
    s = main.state.settings
    monkeypatch.setattr(s, "region", "cn")
    monkeypatch.setattr(s, "data_dir", str(tmp_path / "data"))
    monkeypatch.setattr(s, "sms_log_only", True)
    monkeypatch.setattr(s, "site_domain", "wenquestech.online")
    main.state.sms = None
    main.state.mailer.skip = "@m.wenquestech.online"
    return client


def code_for(phone):
    for msg in reversed(main.state.sms.outbox):
        if msg["to"] == phone:
            return msg["code"]
    raise AssertionError("no text message")


def admin(c):
    r = c.post("/api/v1/auth/login", json={"username": "admin@wq.com", "password": "Passw0rd"})
    return {"Authorization": "Bearer " + r.json()["token"]}


def test_not_on_us_server(client, tmp_path, monkeypatch):  # noqa: F811
    monkeypatch.setattr(main.state.settings, "data_dir", str(tmp_path / "d"))
    assert client.post("/api/v1/auth/sms/code", json={"phone": "13800138000", "purpose": "login"}).status_code == 404
    assert client.get("/api/v1/auth/methods").json()["phone"] is False


def test_member_without_email_signs_in_by_phone(cn):
    h = admin(cn)
    o = cn.post("/api/v1/admin/orgs", json={"name": "杰克科技股份有限公司", "kind": "company"}, headers=h).json()
    r = cn.post(f"/api/v1/admin/orgs/{o['id']}/members", json={"name": "郑吉", "phone": "138 0013 8000"}, headers=h)
    assert r.status_code == 200, r.text
    a = r.json()
    assert a["login"] == "13800138000"
    assert USERS[a["userid"]]["email"] == "13800138000@m.wenquestech.online"
    # the same phone cannot be given to a second person
    r = cn.post(f"/api/v1/admin/orgs/{o['id']}/members", json={"name": "张三", "phone": "13800138000"}, headers=h)
    assert r.json()["error"] == "phone_taken"

    # the phone and the generated password work in the password form
    r = cn.post("/api/v1/auth/login", json={"username": "13800138000", "password": a["password"]})
    assert r.status_code == 200 and r.json()["user"]

    # a text-message code
    assert cn.post("/api/v1/auth/sms/code", json={"phone": "13800138000", "purpose": "login"}).json() == {"sent": True}
    again = cn.post("/api/v1/auth/sms/code", json={"phone": "13800138000", "purpose": "login"})
    assert again.status_code == 429 and again.json()["error"] == "code_too_soon"
    wrong = "000000" if code_for("13800138000") != "000000" else "111111"
    assert cn.post("/api/v1/auth/sms/login", json={"phone": "13800138000", "code": wrong}).json()["error"] == "code_wrong"
    r = cn.post("/api/v1/auth/sms/login", json={"phone": "13800138000", "code": code_for("13800138000")})
    assert r.status_code == 200 and r.json()["token"]
    # used once only
    r = cn.post("/api/v1/auth/sms/login", json={"phone": "13800138000", "code": code_for("13800138000")})
    assert r.json()["error"] == "code_expired"

    # an unknown phone
    r = cn.post("/api/v1/auth/sms/code", json={"phone": "13900000000", "purpose": "login"})
    assert r.status_code == 404 and r.json()["error"] == "phone_unknown"


def test_administrator_never_signs_in_by_phone(cn):
    main.phone_map(2, "13300133000")
    assert cn.post("/api/v1/auth/sms/code", json={"phone": "13300133000", "purpose": "login"}).json() == {"sent": True}
    r = cn.post("/api/v1/auth/sms/login", json={"phone": "13300133000", "code": code_for("13300133000")})
    assert r.status_code == 403 and r.json()["error"] == "phone_login_refused"


def test_no_mail_to_internal_names(cn):
    import asyncio
    assert asyncio.run(main.state.mailer.send("13800138000@m.wenquestech.online", "s", "t")) is True


def test_five_wrong_codes_void_it(cn, monkeypatch):
    monkeypatch.setattr(main.state.settings, "public_signup_cn", True)
    assert cn.post("/api/v1/auth/sms/code", json={"phone": "13700137000", "purpose": "register"}).json() == {"sent": True}
    right = code_for("13700137000")
    wrong = "111111" if right != "111111" else "222222"
    for _ in range(5):
        assert cn.post("/api/v1/auth/sms/register", json={"phone": "13700137000", "code": wrong, "name": "王小明",
                                                           "agree": True}).json()["error"] == "code_wrong"
    r = cn.post("/api/v1/auth/sms/register", json={"phone": "13700137000", "code": right, "name": "王小明", "agree": True})
    assert r.json()["error"] == "code_expired"


def test_public_signup_is_a_student_and_reset_by_text(cn):
    assert cn.get("/api/v1/public/site").json()["signup"] is True
    assert cn.post("/api/v1/auth/sms/code", json={"phone": "13600136000", "purpose": "register"}).json() == {"sent": True}
    r = cn.post("/api/v1/auth/sms/register", json={"phone": "13600136000", "code": code_for("13600136000"),
                                                    "name": "李雷", "agree": True})
    assert r.status_code == 200, r.text
    uid = max(USERS)
    assert USERS[uid]["teacher"] is False and USERS[uid]["lastname"] == "李" and USERS[uid]["firstname"] == "雷"
    # signing up twice with the same phone is refused
    r = cn.post("/api/v1/auth/sms/code", json={"phone": "13600136000", "purpose": "register"})
    assert r.status_code == 409

    # forgot the password: a code to the phone, a new password, signed in
    db = sqlite3.connect(str(main.state.settings.data_dir) + "/logins.db")
    db.execute("update code set created = created - 120")    # past the one-a-minute gap
    db.commit()
    assert cn.post("/api/v1/auth/sms/code", json={"phone": "13600136000", "purpose": "reset"}).json() == {"sent": True}
    r = cn.post("/api/v1/auth/sms/reset", json={"phone": "13600136000", "code": code_for("13600136000"),
                                                 "password": "newpass99"})
    assert r.status_code == 200, r.text
    assert USERS[uid]["password"] == "newpass99"
    assert cn.post("/api/v1/auth/login", json={"username": "13600136000", "password": "newpass99"}).status_code == 200


def test_signup_waits_for_sms_settings(cn, monkeypatch):
    monkeypatch.setattr(main.state.settings, "sms_log_only", False)
    assert cn.get("/api/v1/auth/methods").json() == {"phone": False, "wechat": False, "signup_phone": False,
                                                     "signup_email": False}
    assert cn.get("/api/v1/public/site").json()["signup"] is False
    r = cn.post("/api/v1/auth/sms/code", json={"phone": "13600136000", "purpose": "register"})
    assert r.status_code == 503


def test_wechat_first_scan_binds_then_signs_in(cn, monkeypatch):
    s = main.state.settings
    monkeypatch.setattr(s, "wechat_web_appid", "wxapp")
    monkeypatch.setattr(s, "wechat_web_secret", "wxsecret")
    USERS[9] = user(9, "13500135000@m.wenquestech.online", "吉", "郑")
    main.phone_map(9, "13500135000")

    def fake(request: httpx.Request) -> httpx.Response:
        if request.url.host == "api.weixin.qq.com":
            q = parse_qs(request.url.query.decode())
            assert q["appid"] == ["wxapp"] and q["secret"] == ["wxsecret"]
            return httpx.Response(200, json={"openid": "o-" + q["code"][0], "unionid": "u-" + q["code"][0]})
        return moodle(request)
    main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(fake))
    main.state.moodle.http = main.state.http

    url = cn.get("/api/v1/auth/wechat/url", params={"back": "/pages/courses/courses"}).json()["url"]
    st = parse_qs(urlparse(url).query)["state"][0]
    assert parse_qs(urlparse(url).query)["redirect_uri"] == ["https://learn.wenquestrobotics.com/api/v1/auth/wechat/callback"]
    # a forged state is refused
    r = cn.get("/api/v1/auth/wechat/callback", params={"code": "c1", "state": "forged"}, follow_redirects=False)
    assert "wx_error=expired" in r.headers["location"]
    # first scan: not bound yet -> back to the login page with a ticket
    r = cn.get("/api/v1/auth/wechat/callback", params={"code": "c1", "state": st}, follow_redirects=False)
    loc = urlparse(r.headers["location"])
    ticket = parse_qs(loc.query)["wx"][0]
    assert loc.path == "/pages/login/login"
    # the state is used once
    r = cn.get("/api/v1/auth/wechat/callback", params={"code": "c1", "state": st}, follow_redirects=False)
    assert "wx_error=expired" in r.headers["location"]
    # bind with the phone
    assert cn.post("/api/v1/auth/sms/code", json={"phone": "13500135000", "purpose": "bind"}).json() == {"sent": True}
    r = cn.post("/api/v1/auth/wechat/bind", json={"ticket": ticket, "phone": "13500135000",
                                                  "code": code_for("13500135000")})
    assert r.status_code == 200, r.text
    h = {"Authorization": "Bearer " + r.json()["token"]}
    assert cn.get("/api/v1/me/logins", headers=h).json() == {"phone": "13500135000", "wechat": True, "wechat_ready": True}
    # next scan signs in at once (the sign-in cookie is set, the login page picks it up)
    st2 = parse_qs(urlparse(cn.get("/api/v1/auth/wechat/url").json()["url"]).query)["state"][0]
    r = cn.get("/api/v1/auth/wechat/callback", params={"code": "c1", "state": st2}, follow_redirects=False)
    assert r.status_code == 302 and "wx=" not in r.headers["location"] and "wq_sso=" in r.headers.get("set-cookie", "")
    # unbind
    assert cn.delete("/api/v1/me/wechat", headers=h).json() == {"ok": True}
    assert cn.get("/api/v1/me/logins", headers=h).json()["wechat"] is False
