"""Sign-up with email codes, site-wide sign-in, AI pre-review of teachers, one-click approval, catalogue."""
import io
import os
import re
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image

os.environ.setdefault("WQ_MOODLE_URL", "http://moodle.test")
os.environ.setdefault("WQ_SECRET_KEY", "unit-test-secret")

from app import accounts as ac  # noqa: E402
from app import main  # noqa: E402
from app.ai import ModelGateway  # noqa: E402
from app.mailer import Mailer  # noqa: E402
from app.moodle import MoodleClient  # noqa: E402
from tests.test_materials import BASE  # noqa: E402

USERS: dict[int, dict] = {}
CALLS: list[tuple[str, dict]] = []
ENROLLED: set[tuple[int, int]] = set()


def user(uid, email, first, last, teacher=False, admin=False):
    return {"id": uid, "username": email, "firstname": first, "lastname": last, "fullname": f"{last}{first}",
            "email": email, "lang": "zh_cn", "suspended": False, "teacher": teacher, "admin": admin,
            "timecreated": 1, "lastaccess": 0, "password": "Passw0rd"}


def moodle(request: httpx.Request) -> httpx.Response:
    url = urlparse(str(request.url))
    if url.path == "/login/token.php":
        f = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
        for u in USERS.values():
            if f["username"] in (u["username"], u["email"]) and f["password"] == u["password"] and not u["suspended"]:
                return httpx.Response(200, json={"token": f"u{u['id']}"})
        return httpx.Response(200, json={"error": "Invalid login", "errorcode": "invalidlogin"})
    q = parse_qs(url.query)
    fn, tok = q["wsfunction"][0], q["wstoken"][0]
    body = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
    CALLS.append((fn, body))
    if fn.startswith("local_wenquest_account_"):
        assert tok == ac.hashlib.sha256(("wq-accounts:" + main.state.settings.secret_key).encode()).hexdigest()[:32]
        pub = lambda u: {k: v for k, v in u.items() if k != "password"}  # noqa: E731
        if fn.endswith("_find"):
            hits = [u for u in USERS.values() if (body.get("userid") and str(u["id"]) == body["userid"])
                    or (body.get("email") and body["email"].lower() in (u["email"], u["username"]))]
            return httpx.Response(200, json={"found": len(hits) == 1, "many": False, "users": [pub(h) for h in hits][:1]})
        if fn.endswith("_create"):
            if any(u["email"] == body["email"] for u in USERS.values()):
                return httpx.Response(200, json={"exception": "moodle_exception", "errorcode": "emailexists", "message": "x"})
            uid = max(USERS) + 1
            USERS[uid] = {**user(uid, body["email"], body["firstname"], body["lastname"], body.get("teacher") == "1"),
                          "password": body["password"]}
            return httpx.Response(200, json=pub(USERS[uid]))
        if fn.endswith("_update"):
            u = USERS[int(body["userid"])]
            if body.get("password"):
                u["password"] = body["password"]
            if body.get("teacher") in ("0", "1"):
                u["teacher"] = body["teacher"] == "1"
            if body.get("suspended") in ("0", "1"):
                u["suspended"] = body["suspended"] == "1"
            return httpx.Response(200, json=pub(u))
        if fn.endswith("_search"):
            return httpx.Response(200, json={"total": len(USERS), "users": [pub(u) for u in USERS.values()]})
        if fn.endswith("_enrol"):
            key = (int(body["userid"]), int(body["courseid"]))
            already = key in ENROLLED
            ENROLLED.add(key)
            return httpx.Response(200, json={"status": "already" if already else "added"})
        if fn.endswith("_courses"):
            ids = [int(v) for k, v in body.items() if k.startswith("courseids")]
            uid = int(body.get("userid", 0))
            return httpx.Response(200, json={"courses": [
                {"id": i, "fullname": f"课程{i}", "shortname": f"C{i}", "summary": "<p>简介</p>", "visible": i != 99,
                 "startdate": 0, "sections": 8, "students": 3, "teachers": ["张老师"], "enrolled": (uid, i) in ENROLLED}
                for i in ids]})
    uid = int(tok[1:]) if tok.startswith("u") else 0
    u = USERS.get(uid)
    if fn == "core_webservice_get_site_info":
        return httpx.Response(200, json={"userid": uid, "fullname": u["fullname"], "username": u["username"], "lang": "zh_cn"})
    if fn == "local_wenquest_get_permissions":
        return httpx.Response(200, json={"cancreatecourses": bool(u and (u["teacher"] or u["admin"])),
                                         "issiteadmin": bool(u and u["admin"])})
    if fn == "core_course_get_user_administration_options":
        return httpx.Response(200, json={"courses": [{"id": 7, "options": [{"name": "update", "available": bool(u and u["teacher"])}]}]})
    return httpx.Response(200, json={"exception": "x", "errorcode": "invalidrecord", "message": fn})


@pytest.fixture
def client(tmp_path, monkeypatch):
    USERS.clear()
    USERS[2] = user(2, "admin@wq.com", "管理", "员", admin=True)
    USERS[3] = user(3, "t@school.org", "老", "王", teacher=True)
    ENROLLED.clear()
    with TestClient(main.app) as c:
        main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(moodle))
        main.state.moodle = MoodleClient(BASE, "moodle_mobile_app", main.state.http)
        main.state.ai = ModelGateway("fake", main.state.http)
        main.state.accounts = ac.Store(str(tmp_path / "acc"))
        main.state.mailer = Mailer("", 2525, "tls", "", "", "", "WenQuest")
        monkeypatch.setattr(main.state.settings, "admin_email", "boss@wq.com")
        monkeypatch.setattr(main.state.settings, "app_url", "https://learn.wenquestrobotics.com")
        monkeypatch.setattr(main.state.settings, "site_domain", "wenquestrobotics.com")
        CALLS.clear()
        yield c


def last_code(email: str) -> str:
    for m in reversed(main.state.mailer.outbox):
        if m["to"] == email:
            return re.search(r"\b(\d{6})\b", m["text"]).group(1)
    raise AssertionError("no mail")


def signup(c, email, role="student", **extra):
    assert c.post("/api/v1/auth/code", json={"email": email}).json() == {"sent": True}
    body = {"role": role, "email": email, "code": last_code(email), "password": "abc12345",
            "lastname": "李", "firstname": "雷", "agree": True, **extra}
    return c.post("/api/v1/auth/register", json=body)


def bearer(r):
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_student_signup_with_code_and_cookie(client):
    assert client.post("/api/v1/auth/code", json={"email": "not-an-email"}).status_code == 400
    assert client.post("/api/v1/auth/code", json={"email": "admin@wq.com"}).json()["error"] == "email_taken"
    client.post("/api/v1/auth/code", json={"email": "s@qq.com"})
    r = client.post("/api/v1/auth/code", json={"email": "s@qq.com"})
    assert r.status_code == 429 and r.json()["error"] == "code_too_soon"
    code = last_code("s@qq.com")
    base = {"role": "student", "email": "s@qq.com", "password": "abc12345", "lastname": "李", "firstname": "雷", "agree": True}
    assert client.post("/api/v1/auth/register", json={**base, "code": "000000" if code != "000000" else "111111"}).json()["error"] == "code_wrong"
    assert client.post("/api/v1/auth/register", json={**base, "code": code, "password": "short1"}).json()["error"] == "password_length"
    assert client.post("/api/v1/auth/register", json={**base, "code": code, "agree": False}).json()["error"] == "must_agree"
    r = client.post("/api/v1/auth/register", json={**base, "code": code})
    assert r.status_code == 200 and r.json()["user"]["fullname"] == "李雷" and r.json()["teacher_status"] == ""
    cookie = r.headers["set-cookie"]
    assert "wq_sso=" in cookie and "Domain=wenquestrobotics.com" in cookie and "HttpOnly" in cookie and "Secure" in cookie
    assert "欢迎" in main.state.mailer.outbox[-1]["subject"]
    # a code works once
    assert client.post("/api/v1/auth/register", json={**base, "code": code}).json()["error"] == "code_expired"
    # the website sees the sign-in through the cookie; the learning platform gets a session from it
    # (the test client is not on wenquestrobotics.com over HTTPS, so hand it the cookie)
    client.cookies.set("wq_sso", r.json()["token"])
    assert client.get("/api/v1/auth/whoami").json()["user"]["fullname"] == "李雷"
    assert client.get("/api/v1/auth/sso").json()["user"]["fullname"] == "李雷"
    out = client.post("/api/v1/auth/logout")
    assert 'wq_sso=""' in out.headers["set-cookie"] and "Domain=wenquestrobotics.com" in out.headers["set-cookie"]
    client.cookies.clear()
    assert client.get("/api/v1/auth/whoami").json() == {"user": None}


def test_login_by_email_and_reset(client):
    r = client.post("/api/v1/auth/login", json={"username": "t@school.org", "password": "Passw0rd"})
    assert r.status_code == 200 and "wq_sso=" in r.headers["set-cookie"]
    # unknown emails get the same answer (nothing revealed) but no mail
    n = len(main.state.mailer.outbox)
    assert client.post("/api/v1/auth/code", json={"email": "nobody@x.com", "purpose": "reset"}).json() == {"sent": True}
    assert len(main.state.mailer.outbox) == n
    client.post("/api/v1/auth/code", json={"email": "t@school.org", "purpose": "reset"})
    r = client.post("/api/v1/auth/reset", json={"email": "t@school.org", "code": last_code("t@school.org"), "password": "newpass99"})
    assert r.status_code == 200 and USERS[3]["password"] == "newpass99"


def test_school_email_teacher_is_approved_at_once(client):
    r = signup(client, "wang@mail.tsinghua.edu.cn", "teacher", institution="清华大学", title="讲师")
    assert r.json()["teacher_status"] == "approved" and r.json()["user"]["can_create_courses"]
    assert dict(CALLS)["local_wenquest_account_create"]["teacher"] == "1"
    assert "已开通" in main.state.mailer.outbox[-1]["subject"]
    assert ac.is_school_email("a@ox.ac.uk") and ac.is_school_email("b@ufl.edu") and not ac.is_school_email("c@gmail.com")


def test_teacher_ai_asks_for_more_then_admin_approves(client):
    assert signup(client, "li@gmail.com", "teacher").json()["error"] == "institution_required"
    client.post("/api/v1/auth/code", json={"email": "li@gmail.com"})  # too soon: the first code is still usable
    r = client.post("/api/v1/auth/register", json={
        "role": "teacher", "email": "li@gmail.com", "code": last_code("li@gmail.com"), "password": "abc12345",
        "lastname": "李", "firstname": "老师", "agree": True, "institution": "某某职业技术学院", "title": "讲师"})
    assert r.json()["teacher_status"] == "pending" and not r.json()["user"]["can_create_courses"]
    h = bearer(r)
    # submitted without evidence: the AI asks for more, by email, once
    a = client.post("/api/v1/me/application/submit", headers=h).json()["application"]
    assert a["status"] == "need_more" and a["more"]
    assert "补充材料" in main.state.mailer.outbox[-1]["subject"] and "/pages/apply/apply" in main.state.mailer.outbox[-1]["text"]
    # upload a staff card photo and submit again: the AI now recommends approval
    img = io.BytesIO()
    Image.new("RGB", (40, 30), "white").save(img, "PNG")
    r = client.post("/api/v1/me/application/files", headers=h, files={"file": ("工作证.png", img.getvalue(), "image/png")})
    assert r.json()["application"]["evidence"] == ["工作证.png"]
    assert client.post("/api/v1/me/application/files", headers=h, files={"file": ("x.exe", b"MZ", "application/x")}).status_code == 415
    a = client.post("/api/v1/me/application/submit", headers=h).json()["application"]
    assert a["status"] == "pending"
    # the administrator gets one summary email
    main.state.accounts.run("UPDATE applications SET created = 0")
    import asyncio
    asyncio.run(main.accounts_sweep())
    digest = main.state.mailer.outbox[-1]
    assert digest["to"] == "boss@wq.com" and "建议批准" in digest["text"] and "/pages/admin/admin" in digest["text"]
    asyncio.run(main.accounts_sweep())
    assert main.state.mailer.outbox[-1] is digest  # nothing new, no second email
    # only administrators see the list; one click approves
    teacher = bearer(client.post("/api/v1/auth/login", json={"username": "t@school.org", "password": "Passw0rd"}))
    assert client.get("/api/v1/admin/applications", headers=teacher).status_code == 403
    assert client.get("/api/v1/admin/summary", headers=teacher).json() == {"admin": False}
    boss = bearer(client.post("/api/v1/auth/login", json={"username": "admin@wq.com", "password": "Passw0rd"}))
    assert client.get("/api/v1/admin/summary", headers=boss).json()["applications"] == 1
    apps = client.get("/api/v1/admin/applications", headers=boss).json()["applications"]
    assert apps[0]["ai"]["recommendation"] == "approve"
    ev = client.get(urlparse(apps[0]["evidence"][0]["url"]).path)
    assert ev.status_code == 200 and ev.headers["content-type"] == "image/jpeg"
    assert client.post(f"/api/v1/admin/applications/{apps[0]['id']}/decide", headers=boss, json={"approve": True}).json()["ok"]
    uid = max(USERS)
    assert USERS[uid]["teacher"] and "已通过" in main.state.mailer.outbox[-1]["subject"]
    assert client.post(f"/api/v1/admin/applications/{apps[0]['id']}/decide", headers=boss, json={"approve": False}).status_code == 409


def test_reject_uses_the_ai_reason_and_admin_user_tools(client):
    r = signup(client, "x@163.com", "teacher", institution="不存在大学")
    h = bearer(r)
    client.post("/api/v1/me/application/submit", headers=h)
    boss = bearer(client.post("/api/v1/auth/login", json={"username": "admin@wq.com", "password": "Passw0rd"}))
    a = client.get("/api/v1/admin/applications", headers=boss).json()["applications"][0]
    client.post(f"/api/v1/admin/applications/{a['id']}/decide", headers=boss, json={"approve": False})
    assert "没有通过" in main.state.mailer.outbox[-1]["text"] and "工作证" in main.state.mailer.outbox[-1]["text"]
    assert client.get("/api/v1/me/application", headers=h).json()["application"]["status"] == "rejected"
    uid = max(USERS)
    assert client.put(f"/api/v1/admin/users/{uid}", headers=boss, json={"suspended": True}).json()["suspended"]
    assert client.put("/api/v1/admin/users/2", headers=boss, json={"suspended": True}).status_code == 403
    assert client.post(f"/api/v1/admin/users/{uid}/reset", headers=boss).json()["mailed"]
    assert "3 天内有效" in main.state.mailer.outbox[-1]["text"]


def test_catalog_free_and_paid(client):
    teacher = bearer(client.post("/api/v1/auth/login", json={"username": "t@school.org", "password": "Passw0rd"}))
    assert client.put("/api/v1/courses/7/listing", headers=teacher, json={"mode": "paid", "price": 0}).json()["error"] == "price_required"
    assert client.put("/api/v1/courses/7/listing", headers=teacher, json={"mode": "free"}).json()["mode"] == "free"
    s = bearer(signup(client, "s@qq.com"))
    assert client.put("/api/v1/courses/7/listing", headers=s, json={"mode": "free"}).status_code == 403
    cat = client.get("/api/v1/catalog").json()  # visitors too
    assert [c["name"] for c in cat["courses"]] == ["课程7"] and not cat["signed_in"]
    assert client.post("/api/v1/catalog/7/join", headers=s, json={}).json()["status"] == "enrolled"
    assert client.get("/api/v1/catalog", headers=s).json()["courses"][0]["enrolled"]
    # a paid course: ask, the administrator opens it
    main.state.accounts.run("INSERT INTO catalog (courseid, mode, price, currency, updated) VALUES (8, 'paid', 199, 'CNY', 1)")
    assert client.post("/api/v1/catalog/8/join", headers=s, json={"note": "已转账"}).json()["status"] == "requested"
    assert client.post("/api/v1/catalog/5/join", headers=s, json={}).status_code == 404
    boss = bearer(client.post("/api/v1/auth/login", json={"username": "admin@wq.com", "password": "Passw0rd"}))
    reqs = client.get("/api/v1/admin/requests", headers=boss).json()["requests"]
    assert reqs[0]["course"] == "课程8" and reqs[0]["price"] == 199
    client.post(f"/api/v1/admin/requests/{reqs[0]['id']}/decide", headers=boss, json={"approve": True})
    assert (max(USERS), 8) in ENROLLED and "已为你开通" in main.state.mailer.outbox[-1]["subject"]
