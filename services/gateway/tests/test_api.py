"""API tests against a fake Moodle (httpx.MockTransport)."""
import json
import os
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("WQ_MOODLE_URL", "http://moodle.test")
os.environ.setdefault("WQ_SECRET_KEY", "unit-test-secret")

from app import main  # noqa: E402
from app.content import clean  # noqa: E402
from app.moodle import MoodleClient, _flatten  # noqa: E402
from app.session import Session, SessionCodec  # noqa: E402

BASE = "http://moodle.test"
ML = lambda zh, en: f'<span lang="zh_cn" class="multilang">{zh}</span><span lang="en" class="multilang">{en}</span>'  # noqa: E731

COURSES = [{"id": 2, "shortname": "ROB101", "fullname": ML("机器人学导论", "Intro to Robotics"),
            "summary": ML("<p>简介</p>", "<p>Summary</p>"), "visible": 1, "lastaccess": 10,
            "courseimage": f"{BASE}/pluginfile.php/1/course/overviewfiles/a.png"},
           {"id": 3, "shortname": "HIDDEN", "fullname": "Hidden", "visible": 0}]
CONTENTS = [
    {"id": 10, "section": 0, "name": "General", "summary": "", "modules": []},
    {"id": 11, "section": 1, "name": ML("第 1 章", "Chapter 1"), "summary": "",
     "modules": [
         {"id": 5, "modname": "page", "name": ML("页面", "Page"), "uservisible": True, "completion": 1,
          "completiondata": {"state": 1}},
         {"id": 6, "modname": "label", "description": '<p>Note</p><script>x()</script>'},
         {"id": 7, "modname": "resource", "name": "File", "uservisible": False,
          "contents": [{"type": "file", "filename": "a.pdf", "filesize": 3, "mimetype": "application/pdf",
                        "fileurl": f"{BASE}/webservice/pluginfile.php/9/mod_resource/content/0/a.pdf"}]},
     ]},
]


def fake_moodle(request: httpx.Request) -> httpx.Response:
    url = urlparse(str(request.url))
    if url.path == "/login/token.php":
        form = parse_qs(request.content.decode())
        if form["password"] == ["good"]:
            return httpx.Response(200, json={"token": "mtok"})
        return httpx.Response(200, json={"error": "Invalid login", "errorcode": "invalidlogin"})
    if url.path.startswith("/webservice/pluginfile.php/"):
        assert parse_qs(url.query)["token"] == ["mtok"]
        if url.path.endswith(".mp4"):
            return httpx.Response(200, content=b"0123456789", headers={"content-type": "video/mp4"})
        if url.path.endswith(".html"):
            return httpx.Response(200, content=b"<script>steal()</script>", headers={
                "content-type": "text/html", "content-disposition": 'inline; filename="x.html"'})
        return httpx.Response(200, content=b"PNG", headers={"content-type": "image/png"})
    q = parse_qs(url.query)
    fn = q["wsfunction"][0]
    if q["wstoken"] != ["mtok"]:
        return httpx.Response(200, json={"exception": "x", "errorcode": "invalidtoken", "message": "bad"})
    body = parse_qs(request.content.decode())
    if fn == "core_webservice_get_site_info":
        return httpx.Response(200, json={"userid": 3, "fullname": "小明", "username": "s1", "lang": "zh_cn"})
    if fn == "core_enrol_get_users_courses":
        return httpx.Response(200, json=COURSES)
    if fn == "core_course_get_contents":
        return httpx.Response(200, json=CONTENTS)
    if fn == "core_course_get_course_module":
        cmid = int(body["cmid"][0])
        kind = {5: "page", 7: "resource", 8: "forum"}[cmid]
        return httpx.Response(200, json={"cm": {"id": cmid, "course": 2, "instance": 1, "modname": kind,
                                                "name": ML("页面", "Page")}})
    if fn == "mod_page_get_pages_by_courses":
        assert body["courseids[0]"] == ["2"]
        return httpx.Response(200, json={"pages": [{"id": 1, "intro": "", "content":
            ML('<p>内容<img src="' + BASE + '/webservice/pluginfile.php/4/mod_page/content/1/x.png"></p>',
               '<p onclick="evil()">Body</p>')}]})
    if fn == "core_course_get_courses_by_field":
        return httpx.Response(200, json={"courses": [{**COURSES[0], "contacts": [{"fullname": "王老师"}],
                                                       "startdate": 100, "enddate": 0}]})
    if fn == "core_course_get_user_administration_options":
        return httpx.Response(200, json={"courses": [{"id": 2, "options": [{"name": "update", "available": False}]}]})
    if fn == "mod_page_view_page":
        return httpx.Response(200, json={"status": True})
    return httpx.Response(200, json={"exception": "x", "errorcode": "invalidrecord", "message": fn})


@pytest.fixture
def client():
    with TestClient(main.app) as c:
        main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(fake_moodle))
        main.state.moodle = MoodleClient(BASE, "moodle_mobile_app", main.state.http)
        yield c


def login(c, lang="zh"):
    r = c.post("/api/v1/auth/login", json={"username": "s1", "password": "good", "lang": lang})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["token"]}


def test_login_and_me(client):
    h = login(client)
    me = client.get("/api/v1/me", headers=h).json()
    assert me == {"id": 3, "fullname": "小明", "username": "s1", "avatar": None, "lang": "zh",
                  "can_create_courses": False, "classic_url": "http://moodle.test"}


def test_bad_password_is_401_with_code(client):
    r = client.post("/api/v1/auth/login", json={"username": "s1", "password": "bad"})
    assert r.status_code == 401 and r.json()["error"] == "invalid_login"


def test_session_token_never_contains_moodle_token(client):
    r = client.post("/api/v1/auth/login", json={"username": "s1", "password": "good"})
    assert "mtok" not in r.text


def test_requires_login(client):
    assert client.get("/api/v1/courses").status_code == 401
    r = client.get("/api/v1/courses", headers={"Authorization": "Bearer nonsense"})
    assert r.status_code == 401 and r.json()["error"] == "session_expired"


def test_courses_language_and_hidden(client):
    h = login(client)
    zh = client.get("/api/v1/courses", headers=h).json()["courses"]
    assert [c["name"] for c in zh] == ["机器人学导论"]
    assert zh[0]["summary"] == "简介"
    assert zh[0]["image"].startswith("/api/v1/files/")
    en = client.get("/api/v1/courses?lang=en", headers=h).json()["courses"]
    assert en[0]["name"] == "Intro to Robotics"


def test_outline(client):
    h = login(client, "en")
    secs = client.get("/api/v1/courses/2/outline", headers=h).json()["sections"]
    assert len(secs) == 1  # empty general section dropped
    mods = secs[0]["modules"]
    assert secs[0]["name"] == "Chapter 1"
    assert mods[0] == {"id": 5, "type": "page", "name": "Page", "locked": False, "hidden": False,
                       "completed": True, "has_completion": True}
    assert mods[1]["type"] == "label" and "script" not in mods[1]["html"]
    assert mods[2]["locked"] is True
    assert mods[2]["file"] == {"name": "a.pdf", "size": 3, "mimetype": "application/pdf", "kind": "pdf"}


def test_page_is_sanitized_and_files_proxied(client):
    h = login(client)
    zh = client.get("/api/v1/activities/5", headers=h).json()
    assert zh["name"] == "页面"
    assert 'src="/api/v1/files/' in zh["html"] and "pluginfile" not in zh["html"]
    en = client.get("/api/v1/activities/5?lang=en", headers=h).json()
    assert "onclick" not in en["html"] and "Body" in en["html"]
    img = zh["html"].split('src="')[1].split('"')[0]
    r = client.get(img)
    assert r.status_code == 200 and r.content == b"PNG"


def test_resource_files_and_classic_fallback(client):
    h = login(client)
    res = client.get("/api/v1/activities/7", headers=h).json()
    assert res["files"][0]["name"] == "a.pdf" and res["files"][0]["url"].startswith("/api/v1/files/")
    forum = client.get("/api/v1/activities/8", headers=h).json()
    assert forum["classic_url"] == f"{BASE}/mod/forum/view.php?id=8"


def test_tampered_file_link(client):
    assert client.get("/api/v1/files/not-a-token").status_code == 410


def test_file_proxy_refuses_foreign_urls(client):
    tok = main.state.codec.fernet.encrypt(json.dumps({"u": "http://evil.test/x", "t": "mtok"}).encode()).decode()
    assert client.get(f"/api/v1/files/{tok}").status_code == 403


def test_flatten_nested_params():
    assert _flatten({"courseids": [2, 3], "options": [{"name": "a", "value": True}]}) == [
        ("courseids[0]", "2"), ("courseids[1]", "3"), ("options[0][name]", "a"), ("options[0][value]", "1")]


def test_session_expiry():
    codec = SessionCodec("k", days=0)
    tok = codec.issue(Session("m", 1, "en"))
    import time
    time.sleep(1.1)
    assert codec.read(tok) is None
    assert SessionCodec("k", 1).read(tok).user_id == 1


def test_clean_keeps_external_links_and_iframes_sandboxed():
    out = clean('<a href="https://x.org">x</a><iframe src="https://sim.org"></iframe><img src="javascript:1">',
                BASE, lambda u: "SIGNED")
    assert 'href="https://x.org"' in out and 'sandbox="' in out and "javascript" not in out


def test_connect_url_sends_public_host():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["host"] = request.headers["host"]
        seen["proto"] = request.headers.get("x-forwarded-proto")
        return httpx.Response(200, json={"token": "t"})

    import asyncio
    mc = MoodleClient("https://classic.example.com", "svc", httpx.AsyncClient(transport=httpx.MockTransport(handler)),
                      connect_url="http://moodle")
    assert asyncio.run(mc.login("u", "p")) == "t"
    assert seen == {"url": "http://moodle/login/token.php", "host": "classic.example.com", "proto": "https"}
    assert mc._url("https://classic.example.com/webservice/pluginfile.php/1/a.png") == \
        "http://moodle/webservice/pluginfile.php/1/a.png"


def test_proxied_html_cannot_run_on_app_domain(client):
    login(client)
    tok = main.state.codec.fernet.encrypt(json.dumps(
        {"u": f"{BASE}/webservice/pluginfile.php/9/mod_resource/content/0/x.html", "t": "mtok"}).encode()).decode()
    r = client.get(f"/api/v1/files/{tok}")
    assert r.headers["content-disposition"].startswith("attachment")
    assert "sandbox" in r.headers["content-security-policy"]
    assert r.headers["x-content-type-options"] == "nosniff"
    img = main.state.codec.fernet.encrypt(json.dumps(
        {"u": f"{BASE}/webservice/pluginfile.php/4/mod_page/content/1/x.png", "t": "mtok"}).encode()).decode()
    assert client.get(f"/api/v1/files/{img}").headers["content-disposition"].startswith("inline;")


def sign(url):
    return main.state.codec.fernet.encrypt(json.dumps({"u": url, "t": "mtok"}).encode()).decode()


def test_course_info_and_role(client):
    h = login(client)
    c = client.get("/api/v1/courses/2", headers=h).json()
    assert c["name"] == "机器人学导论" and c["teachers"] == ["王老师"] and c["role"] == "student"
    assert c["image"].startswith("/api/v1/files/") and c["classic_url"].endswith("/course/view.php?id=2")


def test_video_supports_byte_ranges(client):
    tok = sign(f"{BASE}/webservice/pluginfile.php/9/mod_resource/content/0/v.mp4")
    r = client.get(f"/api/v1/files/{tok}", headers={"Range": "bytes=2-5"})
    assert r.status_code == 206 and r.content == b"2345" and r.headers["content-range"] == "bytes 2-5/10"
    assert client.get(f"/api/v1/files/{tok}", headers={"Range": "bytes=-3"}).content == b"789"
    full = client.get(f"/api/v1/files/{tok}")
    assert full.status_code == 200 and full.headers["accept-ranges"] == "bytes"


def test_lab_runs_in_its_own_origin(client):
    tok = sign(f"{BASE}/webservice/pluginfile.php/9/mod_resource/content/0/lab.html")
    r = client.get(f"/api/v1/labs/{tok}")
    csp = r.headers["content-security-policy"]
    assert r.status_code == 200 and "allow-scripts" in csp and "allow-same-origin" not in csp
    # The ordinary file proxy never runs HTML.
    assert "sandbox" in client.get(f"/api/v1/files/{tok}").headers["content-security-policy"]
    png = sign(f"{BASE}/webservice/pluginfile.php/9/mod_resource/content/0/a.png")
    assert client.get(f"/api/v1/labs/{png}").status_code == 415


def test_file_kinds():
    from app.content import file_kind
    assert [file_kind(n) for n in ["a.MP4", "b.pptx", "c.html", "d.docx", "e.xlsx", "f.pdf", "g.zip"]] == \
        ["video", "slides", "lab", "doc", "sheet", "pdf", "file"]
    assert file_kind("noext", "video/mp4") == "video"


def test_chinese_file_names_are_served(client):
    tok = sign(f"{BASE}/webservice/pluginfile.php/9/mod_resource/content/0/%E8%AE%B2%E4%B9%89.png")
    r = client.get(f"/api/v1/files/{tok}")
    assert r.status_code == 200
    cd = r.headers["content-disposition"]
    assert cd.startswith("inline;") and "filename*=UTF-8''%E8%AE%B2%E4%B9%89.png" in cd and 'filename="file.png"' in cd
    doc = sign(f"{BASE}/webservice/pluginfile.php/9/mod_resource/content/0/a.html")
    assert client.get(f"/api/v1/files/{doc}").headers["content-disposition"] == \
        'attachment; filename="a.html"; filename*=UTF-8\'\'a.html'


def test_health_reports_ai_provider_without_secrets(client):
    r = client.get("/api/health").json()
    assert r["ok"] is True and r["ai"] in ("claude", "deepseek", "fake", "none")
    assert "key" not in str(r).lower()
