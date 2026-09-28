"""AI course workshop: outline, lesson, publish (fake Moodle + fake or mocked models)."""
import asyncio
import json
import os
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("WQ_MOODLE_URL", "http://moodle.test")
os.environ.setdefault("WQ_SECRET_KEY", "unit-test-secret")

from app import course_builder as cb  # noqa: E402
from app import main  # noqa: E402
from app.ai import AIError, ModelGateway  # noqa: E402
from app.moodle import MoodleClient  # noqa: E402

BASE = "http://moodle.test"
CREATED = {}


def fake_moodle(request: httpx.Request) -> httpx.Response:
    url = urlparse(str(request.url))
    if url.path == "/login/token.php":
        form = parse_qs(request.content.decode())
        return httpx.Response(200, json={"token": "teacher" if form["username"] == ["t"] else "student"})
    q = parse_qs(url.query)
    fn, tok = q["wsfunction"][0], q["wstoken"][0]
    if fn == "core_webservice_get_site_info":
        return httpx.Response(200, json={"userid": 5, "fullname": "T", "username": "t", "lang": "en"})
    if fn == "local_wenquest_get_permissions":
        return httpx.Response(200, json={"cancreatecourses": tok == "teacher", "issiteadmin": False})
    if fn == "local_wenquest_create_course":
        CREATED.clear()
        CREATED.update(parse_qs(request.content.decode()))
        return httpx.Response(200, json={"courseid": 42, "shortname": "ITR-202609", "activities": 3})
    return httpx.Response(200, json={"exception": "x", "errorcode": "invalidrecord", "message": fn})


@pytest.fixture
def client():
    with TestClient(main.app) as c:
        main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(fake_moodle))
        main.state.moodle = MoodleClient(BASE, "moodle_mobile_app", main.state.http)
        main.state.ai = ModelGateway("fake", main.state.http)
        yield c


def login(c, who="t"):
    r = c.post("/api/v1/auth/login", json={"username": who, "password": "x"})
    return {"Authorization": "Bearer " + r.json()["token"]}, r.json()["user"]


def test_login_reports_creator_flag(client):
    assert login(client, "t")[1]["can_create_courses"] is True
    assert login(client, "s")[1]["can_create_courses"] is False


def test_students_cannot_use_the_workshop(client):
    h, _ = login(client, "s")
    assert client.post("/api/v1/ai/outline", json={"topic": "PID"}, headers=h).status_code == 403
    assert client.post("/api/v1/courses", json={"title": {"zh": "x"}, "sections": [{"title": {"zh": "a"}}]},
                       headers=h).status_code == 403


def test_outline_shape_and_languages(client):
    h, _ = login(client)
    r = client.post("/api/v1/ai/outline", headers=h, json={
        "topic": "PID 控制", "sections": 3, "lessons_per_section": 2, "languages": "both"})
    assert r.status_code == 200, r.text
    o = r.json()
    assert len(o["sections"]) == 3 and len(o["sections"][0]["lessons"]) == 2
    assert set(o["title"]) == {"zh", "en"} and o["sections"][0]["assignment"]["title"]["en"]
    one = client.post("/api/v1/ai/outline", headers=h, json={"topic": "PID", "languages": "en",
                                                                "assignments": False}).json()
    assert set(one["title"]) == {"en"} and one["sections"][0]["assignment"] is None


def test_lesson_is_sanitized(client):
    h, _ = login(client)
    main.state.ai = ModelGateway("fake", main.state.http)
    orig = cb.fake_lesson
    cb.fake_lesson = lambda r: {"content": {"zh": "<h3>目标</h3><script>alert(1)</script><p onclick='x'>正文</p>"}}
    try:
        r = client.post("/api/v1/ai/lesson", headers=h, json={
            "course_title": "c", "section_title": "s", "lesson_title": "l", "languages": "zh"})
    finally:
        cb.fake_lesson = orig
    html = r.json()["content"]["zh"]
    assert "script" not in html and "onclick" not in html and "<h3>目标</h3>" in html


def test_publish_builds_bilingual_course(client):
    h, _ = login(client)
    draft = {
        "title": {"zh": "机器人入门", "en": "Intro to Robotics"}, "summary": {"zh": "简介", "en": "About"},
        "languages": "both",
        "sections": [{
            "title": {"zh": "第 1 章", "en": "Chapter 1"}, "summary": {"zh": "", "en": ""},
            "lessons": [{"title": {"zh": "1.1 课", "en": "1.1 Lesson"},
                         "content": {"zh": "<p>中文</p><script>x()</script>", "en": "<p>English</p>"}}],
            "assignment": {"title": {"zh": "作业", "en": "Homework"}, "brief": {"zh": "做<b>题", "en": "Do it"}},
        }],
    }
    r = client.post("/api/v1/courses", headers=h, json=draft)
    assert r.json() == {"course_id": 42, "shortname": "ITR-202609", "activities": 3}
    sent = {k: v[0] for k, v in CREATED.items()}
    assert sent["fullname"] == ('<span lang="zh_cn" class="multilang">机器人入门</span>'
                                '<span lang="en" class="multilang">Intro to Robotics</span>')
    assert sent["shortname"].startswith("IR-")  # "to" is skipped
    assert sent["sections[0][activities][0][type]"] == "page"
    assert "script" not in sent["sections[0][activities][0][content]"]
    assert sent["sections[0][activities][1][type]"] == "assign"
    assert "&lt;b&gt;" in sent["sections[0][activities][1][intro]"]  # plain text brief is escaped


def test_single_language_names_have_no_markup():
    d = cb.Draft(title=cb.Text(zh="课程"), languages="zh",
                 sections=[cb.DraftSection(title=cb.Text(zh="第一章"),
                                           lessons=[cb.DraftLesson(title=cb.Text(zh="一"), content=cb.Text(zh="<p>x</p>"))])])
    p = cb.to_moodle(d, lambda h: h)
    assert p["fullname"] == "课程" and p["sections"][0]["activities"][0]["name"] == "一"
    assert p["shortname"].startswith("WQ-")


def test_norm_outline_tolerates_messy_model_output():
    b = cb.Brief(topic="xx", languages="both")
    o = cb.norm_outline({"title": "只给了字符串", "sections": [{"title": {"zh": "a"}, "lessons": ["bad", {"title": "b"}]}]}, b)
    assert o["title"] == {"zh": "只给了字符串", "en": ""}
    assert len(o["sections"][0]["lessons"]) == 1 and o["sections"][0]["assignment"] is None


def test_ai_unavailable_without_keys(client):
    h, _ = login(client)
    main.state.ai = ModelGateway("auto", main.state.http)
    r = client.post("/api/v1/ai/outline", headers=h, json={"topic": "PID"})
    assert r.status_code == 503 and r.json()["error"] == "ai_unavailable"


def _gateway(handler, **kw):
    return ModelGateway(kw.pop("provider"), httpx.AsyncClient(transport=httpx.MockTransport(handler)), **kw)


def test_claude_tool_use_parsing():
    seen = {}

    def handler(req):
        seen["body"] = json.loads(req.content)
        seen["key"] = req.headers["x-api-key"]
        return httpx.Response(200, json={"content": [{"type": "tool_use", "name": "output", "input": {"ok": 1}}]})

    g = _gateway(handler, provider="auto", anthropic_key="sk-test", claude_model="claude-sonnet-5")
    assert g.provider == "claude"
    assert asyncio.run(g.json(system="s", prompt="p", schema={"type": "object"})) == {"ok": 1}
    assert seen["key"] == "sk-test" and seen["body"]["tool_choice"] == {"type": "tool", "name": "output"}


def test_deepseek_json_parsing_and_errors():
    g = _gateway(lambda r: httpx.Response(200, json={"choices": [{"message": {"content": '{"a": 2}'}}]}),
                 provider="auto", deepseek_key="dk")
    assert g.provider == "deepseek" and asyncio.run(g.json(system="s", prompt="p", schema={})) == {"a": 2}
    bad = _gateway(lambda r: httpx.Response(401, json={}), provider="deepseek", deepseek_key="dk")
    with pytest.raises(AIError) as e:
        asyncio.run(bad.json(system="s", prompt="p", schema={}))
    assert e.value.code == "ai_key_invalid"


def test_bilingual_html_uses_mlang_and_resolves():
    from app.multilang import resolve
    d = cb.Draft(title=cb.Text(zh="课", en="C"), summary=cb.Text(zh="简介", en="About"), languages="both",
                 sections=[cb.DraftSection(title=cb.Text(zh="章", en="S"), summary=cb.Text(zh="一句", en="One"),
                                           lessons=[cb.DraftLesson(title=cb.Text(zh="一", en="One"),
                                                                   content=cb.Text(zh="<p>中</p>", en="<p>E</p>"))])])
    p = cb.to_moodle(d, lambda h: h)
    assert p["summary"] == "{mlang zh_cn}<p>简介</p>{mlang}{mlang en}<p>About</p>{mlang}"
    html = p["sections"][0]["activities"][0]["content"]
    assert resolve(html, "zh") == "<p>中</p>" and resolve(html, "en") == "<p>E</p>"
    assert p["fullname"].startswith('<span lang="zh_cn"')  # names keep span markup
