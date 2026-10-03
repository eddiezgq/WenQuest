"""Engineering task sheets in a course (round 11, 2.7 (5)): catalog, issue (a Moodle assignment + the factory task), progress
for the teacher and the student, and writing the graded ones into the gradebook."""
import json
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main
from app.ai import ModelGateway
from app.moodle import MoodleClient
from app.tasks_api import classes, factory_base
from tests.test_materials import BASE, fake_moodle, login

SPEC = {"编号": "TS-33-1", "book": "mechdesign", "no": "33.1", "section": "33.end", "标题": ["SH-301 改版", "SH-301 redesign"],
        "角色": ["设计工程师", "design engineer"], "学时": 8, "工位": ["CAD", "PLM"], "背景": ["改版", "Redesign"],
        "交付物": [{"名称": ["计算书", "Sheet"], "验收": ["齐", "Complete"]}],
        "评分": [{"项": ["计算书", "Sheet"], "分": 60, "标准": ["对", "Right"]}, {"项": ["模型", "Model"], "分": 40, "标准": ["对", "Right"]}]}
MOODLE, FACTORY = [], []
HUB = {"tasks": {}}


def handler(request: httpx.Request) -> httpx.Response:
    url = urlparse(str(request.url))
    if url.netloc.endswith("factory.test"):
        FACTORY.append((request.method, url.netloc, url.path, request.headers.get("authorization")))
        if request.headers.get("authorization") != "Bearer k":
            return httpx.Response(401, json={"detail": "需要钥匙"})
        if url.path == "/api/tasks/course/issue":
            b = json.loads(request.content)
            HUB["tasks"][b["spec"]["编号"]] = dict(b, id="tid1")
            return httpx.Response(200, json={"id": "tid1"})
        if url.path == "/api/tasks/course/7":
            return httpx.Response(200, json=[{"id": "tid1", "code": code, "cmid": t["cmid"], "submissions": [
                {"id": "s1", "author_uid": "6", "name": "学生甲", "status": "graded", "status_zh": "已评分", "rounds": 2,
                 "open_errors": 0, "open_warnings": 1, "suggested": 87, "total": 88.0, "score_items": [52, 36], "score_note": "好",
                 "pushed_at": HUB.get("pushed")},
                {"id": "s2", "author_uid": "9", "name": "学生乙", "status": "submitted", "status_zh": "待老师审阅", "rounds": 1,
                 "open_errors": 2, "open_warnings": 0, "suggested": 77, "total": None, "pushed_at": None}]}
                for code, t in HUB["tasks"].items()])
        if url.path == "/api/tasks/course/7/pushed":
            HUB["pushed"] = "2026-10-02T00:00:00Z"
            return httpx.Response(200, json={"marked": len(json.loads(request.content)["submissions"])})
        return httpx.Response(404, json={"detail": "no"})
    q = parse_qs(url.query)
    fn = (q.get("wsfunction") or [""])[0]
    tok = (q.get("wstoken") or [""])[0]
    body = {k: v[0] for k, v in parse_qs(request.content.decode(errors="ignore")).items()} if fn else {}
    if fn:
        MOODLE.append((fn, body))
    if fn == "core_course_get_user_administration_options":
        return httpx.Response(200, json={"courses": [{"id": 7, "options": [{"name": "update", "available": tok == "teacher"}]}]})
    if fn == "core_course_get_courses_by_field":
        return httpx.Response(200, json={"courses": [{"id": 7, "fullname": "机械设计"}]})
    if fn == "local_wenquest_add_activities":
        return httpx.Response(200, json={"cmids": [77]})
    if fn == "mod_assign_get_assignments":
        return httpx.Response(200, json={"courses": [{"id": 7, "assignments": [{"id": 3, "cmid": 77, "name": "x", "grade": 100}]}]})
    if fn in ("mod_assign_save_grade", "local_wenquest_edit_course"):
        return httpx.Response(200, content=b"null", headers={"content-type": "application/json"})
    return fake_moodle(request)


@pytest.fixture
def client(tmp_path):
    (tmp_path / "books" / "mechdesign" / "task").mkdir(parents=True)
    (tmp_path / "books" / "mechdesign" / "task" / "ts33_1.json").write_text(json.dumps(SPEC, ensure_ascii=False), encoding="utf-8")
    with TestClient(main.app) as c:
        st = main.state.settings
        saved = {k: getattr(st, k) for k in ("textbook_dir", "data_dir", "factory_url", "factory_task_key", "factory_classes")}
        st.textbook_dir, st.data_dir = str(tmp_path / "books"), str(tmp_path / "data")
        st.factory_url, st.factory_task_key, st.factory_classes = "https://factory.test", "k", "pilot:试点班,g2:二班"
        main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        main.state.moodle = MoodleClient(BASE, "moodle_mobile_app", main.state.http)
        main.state.ai = ModelGateway("fake", main.state.http)
        MOODLE.clear(), FACTORY.clear(), HUB.clear(), HUB.update(tasks={})
        yield c
        for k, v in saved.items():
            setattr(st, k, v)


def test_helpers():
    assert classes("pilot:试点班, g2:二班,BAD:x,zz") == [{"id": "pilot", "name": "试点班"}, {"id": "g2", "name": "二班"}]
    assert factory_base("https://factory.example.com/", "pilot") == "https://pilot.factory.example.com"
    assert factory_base("https://factory.example.com", "") == "https://factory.example.com"


def test_issue_follow_and_push_grades(client):
    t, s = login(client, "t"), login(client, "s")
    assert client.get("/api/v1/task-catalog", headers=s).status_code == 403
    cat = client.get("/api/v1/task-catalog", headers=t).json()
    assert cat["tasks"][0]["code"] == "TS-33-1" and [f["id"] for f in cat["factories"]] == ["", "pilot", "g2"] and cat["connected"]

    assert client.post("/api/v1/courses/7/tasks", json={"book": "mechdesign", "no": "33.1", "factory": "pilot"}, headers=s).status_code == 403
    assert client.post("/api/v1/courses/7/tasks", json={"book": "mechdesign", "no": "33.1", "factory": "nope"}, headers=t).status_code == 404
    r = client.post("/api/v1/courses/7/tasks", json={"book": "mechdesign", "no": "33.1", "factory": "pilot", "due": 1792000000}, headers=t)
    assert r.status_code == 200, r.text
    assert r.json() == {"code": "TS-33-1", "tid": "tid1", "cmid": 77, "url": "https://pilot.factory.test/tasks/tid1"}
    add = next(b for fn, b in MOODLE if fn == "local_wenquest_add_activities")
    assert add["activities[0][type]"] == "assign" and add["activities[0][grade]"] == "100" and "TS-33-1" in add["activities[0][name]"]
    issued = HUB["tasks"]["TS-33-1"]
    assert issued["cmid"] == 77 and issued["course_id"] == 7 and issued["course_name"] == "机械设计" and issued["spec"]["评分"]
    assert all(h == "Bearer k" and host == "pilot.factory.test" for _, host, _, h in FACTORY)
    # re-issue with a new due date: same assignment, its due date changed
    MOODLE.clear()
    client.post("/api/v1/courses/7/tasks", json={"book": "mechdesign", "no": "33.1", "factory": "pilot", "due": 1793000000}, headers=t)
    assert [fn for fn, _ in MOODLE if fn.startswith("local_wenquest")] == ["local_wenquest_edit_course"]
    assert client.post("/api/v1/courses/7/tasks", json={"book": "mechdesign", "no": "33.1", "factory": "g2"}, headers=t).status_code == 409

    tv = client.get("/api/v1/courses/7/tasks", headers=t).json()
    task = tv["tasks"][0]
    assert tv["teacher"] and task["factory_name"] == "试点班" and task["counts"]["graded"] == 1 and task["to_push"] == 1
    assert task["submissions"][1]["review_url"] == "https://pilot.factory.test/tasks/review/s2"
    sv = client.get("/api/v1/courses/7/tasks", headers=s).json()       # student 6 sees only his own row
    assert not sv["teacher"] and sv["tasks"][0]["mine"]["total"] == 88.0 and "submissions" not in sv["tasks"][0]

    assert client.post("/api/v1/courses/7/tasks/TS-33-1/push", json={}, headers=s).status_code == 403
    r = client.post("/api/v1/courses/7/tasks/TS-33-1/push", json={}, headers=t).json()
    assert r == {"pushed": 1, "failed": []}
    g = next(b for fn, b in MOODLE if fn == "mod_assign_save_grade")
    assert g["assignmentid"] == "3" and g["userid"] == "6" and g["grade"] == "88.0"
    assert "52" in g["plugindata[assignfeedbackcomments_editor][text]"]
    assert client.post("/api/v1/courses/7/tasks/TS-33-1/push", json={}, headers=t).json()["pushed"] == 0     # already written
    assert client.post("/api/v1/courses/7/tasks/TS-33-1/push", json={"again": True}, headers=t).json()["pushed"] == 1


def test_not_connected(client):
    main.state.settings.factory_task_key = ""
    t = login(client, "t")
    assert client.get("/api/v1/task-catalog", headers=t).json()["connected"] is False
    r = client.post("/api/v1/courses/7/tasks", json={"book": "mechdesign", "no": "33.1"}, headers=t)
    assert r.status_code == 503 and r.json()["error"] == "factory_unavailable"


def test_task_docs_with_the_site_cookie(client, tmp_path):
    (tmp_path / "books" / "mechdesign" / "task" / "ts33_1-rubric.docx").write_bytes(b"PK fake docx")
    assert client.get("/api/v1/task-docs/mechdesign/33.1/rubric").status_code == 401
    tok = login(client, "s")["Authorization"][7:]
    client.cookies.set("wq_sso", tok)
    r = client.get("/api/v1/task-docs/mechdesign/33.1/rubric")
    assert r.status_code == 200 and r.content == b"PK fake docx"
    assert client.get("/api/v1/task-docs/mechdesign/33.1/secret").status_code == 404
    assert client.get("/api/v1/task-docs/..%2Fetc/33.1/rubric").status_code == 404
    client.cookies.clear()
