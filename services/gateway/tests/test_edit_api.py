"""Teachers edit their course in WenQuest (step B3)."""
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient

from app import edit_api as ea
from app import main
from app.ai import ModelGateway
from app.moodle import MoodleClient
from tests.test_materials import BASE, fake_moodle, login

CALLS: list[tuple[str, dict]] = []


def moodle(request: httpx.Request) -> httpx.Response:
    q = parse_qs(urlparse(str(request.url)).query)
    fn = (q.get("wsfunction") or [""])[0]
    tok = (q.get("wstoken") or [""])[0]
    body = {k: v[0] for k, v in parse_qs(request.content.decode(errors="ignore")).items()} if fn else {}
    CALLS.append((fn, body))
    if fn == "core_course_get_user_administration_options":
        return httpx.Response(200, json={"courses": [{"id": 7, "options": [{"name": "update", "available": tok == "teacher"}]}]})
    if fn == "core_course_get_courses_by_field":
        return httpx.Response(200, json={"courses": [{"id": 7, "fullname": '<span lang="zh_cn" class="multilang">力学</span><span lang="en" class="multilang">Mechanics</span>',
                                                      "summary": "<p>x</p>", "visible": 1}]})
    if fn == "core_course_get_contents":
        return httpx.Response(200, json=[{"id": 30, "section": 1, "name": "第1章", "summary": "", "visible": 1,
                                          "modules": [{"id": 90, "modname": "page", "name": "1.1", "visible": 1, "instance": 4}]}])
    if fn == "mod_page_get_pages_by_courses":
        return httpx.Response(200, json={"pages": [{"id": 4, "coursemodule": 90, "name": "1.1 参考系", "content": "<p>参考系是描述运动的参照物。</p>"}]})
    if fn == "local_wenquest_edit_course":
        return httpx.Response(200, json={"ok": True, "sectionid": 31, "cmid": 0})
    if fn == "local_wenquest_create_quiz":
        return httpx.Response(200, json={"cmid": 91, "quizid": 5, "questions": int(sum(1 for k in body if k.endswith("][type]")))})
    return fake_moodle(request)


@pytest.fixture
def client():
    with TestClient(main.app) as c:
        main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(moodle))
        main.state.moodle = MoodleClient(BASE, "moodle_mobile_app", main.state.http)
        main.state.ai = ModelGateway("fake", main.state.http)
        CALLS.clear()
        yield c


def test_structure_is_for_teachers_and_keeps_both_languages(client):
    assert client.get("/api/v1/courses/7/structure", headers=login(client, "s")).status_code == 403
    h = login(client)
    s = client.get("/api/v1/courses/7/structure", headers=h).json()
    assert s["course"]["name"] == {"zh": "力学", "en": "Mechanics"}
    assert s["sections"][0]["modules"][0]["cmid"] == 90
    client.put("/api/v1/courses/7/settings", headers=h, json={"name": {"zh": "力学", "en": "Mechanics!"}})
    sent = dict(CALLS)["local_wenquest_edit_course"]
    assert sent["action"] == "course" and "Mechanics!" in sent["name"] and "multilang" in sent["name"]


def test_ai_questions_are_checked_and_quiz_saved(client):
    h = login(client)
    r = client.post("/api/v1/courses/7/quizzes/ai", headers=h, json={"section": 1, "count": 5}).json()
    assert len(r["questions"]) == 5 and r["title"] == "第1章"
    bad = {"section": 1, "name": "小测", "questions": [{"type": "single", "text": "q", "answers": [{"text": "a", "fraction": 0}, {"text": "b", "fraction": 0}]}]}
    assert client.post("/api/v1/courses/7/quizzes", headers=h, json=bad).json()["error"] == "question_invalid"
    ok = client.post("/api/v1/courses/7/quizzes", headers=h, json={"section": 1, "name": "小测", "questions": r["questions"]}).json()
    assert ok["cmid"] == 91


def test_check_questions_drops_broken_ones():
    qs = [{"type": "single", "text": "x", "answers": [{"text": "a", "fraction": 1}, {"text": "b", "fraction": 1}]},
          {"type": "numerical", "text": "x", "answers": [{"text": "about three", "fraction": 1}]},
          {"type": "truefalse", "text": "x", "answers": [], "correct": False, "mark": 50},
          {"type": "essay", "text": "x", "answers": []}]
    out = ea.check_questions(qs)
    assert [q["type"] for q in out] == ["truefalse"] and out[0]["mark"] == 10


def test_ai_assignment_has_rubric_and_answer_key(client):
    h = login(client)
    r = client.post("/api/v1/courses/7/assignments/ai", headers=h, json={"section": 1, "note": "3 道计算题"}).json()
    assert r["name"] and "评分标准" in r["intro"] and "<table>" in r["intro"] and r["answers"] and 1 <= r["days"] <= 60
    assert client.post("/api/v1/courses/7/assignments/ai", headers=login(client, "s"), json={"section": 1}).status_code == 403
