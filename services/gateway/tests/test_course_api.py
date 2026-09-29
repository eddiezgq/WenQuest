"""Course menus in WenQuest's own UI (step B1): announcements, discussions, sessions, people and groups."""
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient

from app import course_api as ca
from app import main
from app.ai import ModelGateway
from app.moodle import MoodleClient
from tests.test_materials import BASE, fake_moodle, login

CALLS: list[tuple[str, dict]] = []
USERS = [
    {"id": 5, "fullname": "张老师", "email": "t@x.cn", "roles": [{"shortname": "editingteacher"}], "groups": []},
    *[{"id": 10 + i, "fullname": f"学生{i}", "email": f"s{i}@x.cn", "roles": [{"shortname": "student"}],
       "groups": [{"id": 1, "name": "A"}] if i < 2 else []} for i in range(9)],
]


def moodle(request: httpx.Request) -> httpx.Response:
    q = parse_qs(urlparse(str(request.url)).query)
    fn = (q.get("wsfunction") or [""])[0]
    body = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
    tok = (q.get("wstoken") or [""])[0]
    CALLS.append((fn, body))
    teacher = tok == "teacher"
    if fn == "mod_forum_get_forums_by_courses":
        return httpx.Response(200, json=[
            {"id": 1, "course": 7, "type": "news", "name": "公告", "cancreatediscussions": teacher},
            {"id": 2, "course": 7, "type": "general", "name": "答疑区", "intro": "<p>提问</p>", "numdiscussions": 1,
             "cancreatediscussions": True}])
    if fn == "mod_forum_get_forum_discussions":
        return httpx.Response(200, json={"discussions": [
            {"id": 30, "discussion": 3, "subject": "第一周安排", "message": "<p>周一上课</p><script>x</script>",
             "userfullname": "张老师", "created": 100, "numreplies": 0, "pinned": True, "canreply": True}]})
    if fn == "mod_forum_add_discussion":
        return httpx.Response(200, json={"discussionid": 4})
    if fn == "mod_forum_get_discussion_posts":
        return httpx.Response(200, json={"forumid": 2, "courseid": 7, "posts": [
            {"id": 30, "parentid": 0, "subject": "问题", "message": "<p>怎么求导？</p>", "author": {"id": 11, "fullname": "学生1"},
             "timecreated": 100, "capabilities": {"reply": True, "edit": False, "delete": False}},
            {"id": 31, "parentid": 30, "subject": "Re: 问题", "message": "<p>用定义</p>", "author": {"id": 5, "fullname": "张老师"},
             "timecreated": 200, "capabilities": {"reply": True, "edit": True, "delete": True}}]})
    if fn == "mod_forum_get_discussion_post":
        return httpx.Response(200, json={"post": {"id": 30, "replysubject": "Re: 问题"}})
    if fn == "mod_forum_add_discussion_post":
        return httpx.Response(200, json={"postid": 32})
    if fn in ("mod_forum_view_forum_discussion", "mod_forum_set_lock_state", "mod_forum_set_pin_state"):
        return httpx.Response(200, json={"status": True})
    if fn == "core_course_get_user_administration_options":
        return httpx.Response(200, json={"courses": [{"id": 7, "options": [{"name": "update", "available": teacher}]}]})
    if fn == "core_enrol_get_enrolled_users":
        return httpx.Response(200, json=USERS)
    if fn == "core_group_get_course_groups":
        return httpx.Response(200, json=[{"id": 1, "name": "A"}])
    if fn == "gradereport_user_get_grade_items":
        return httpx.Response(200, json={"usergrades": [
            {"userid": 10 + i, "gradeitems": [{"itemtype": "course", "graderaw": 60 + 4 * i}]} for i in range(9)]})
    if fn == "local_wenquest_manage_groups":
        return httpx.Response(200, json={"groups": [{"id": 9, "name": "第1组", "members": [10, 11]}], "skipped": []})
    if fn == "local_wenquest_manage_members":
        return httpx.Response(200, json={"added": ["s9"], "already": [], "notfound": ["nobody"], "removed": 0})
    if fn == "local_wenquest_get_meetings":
        return httpx.Response(200, json={"meetings": [], "canmanage": teacher})
    if fn == "local_wenquest_save_meeting":
        return httpx.Response(200, json={"id": 1, **{k: body.get(k, "") for k in ("name", "provider", "url")}})
    return fake_moodle(request)


@pytest.fixture
def client():
    with TestClient(main.app) as c:
        main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(moodle))
        main.state.moodle = MoodleClient(BASE, "moodle_mobile_app", main.state.http)
        main.state.ai = ModelGateway("fake", main.state.http)
        CALLS.clear()
        yield c


def test_announcements_and_posting(client):
    h = login(client)
    r = client.get("/api/v1/courses/7/announcements", headers=h).json()
    assert r["can_post"] and r["items"][0]["subject"] == "第一周安排" and "<script>" not in r["items"][0]["message"]
    assert client.post("/api/v1/courses/7/announcements", headers=h, json={"subject": "", "message": "x"}).status_code == 400
    r = client.post("/api/v1/courses/7/announcements", headers=h, json={"subject": "考试", "message": "第一行\n第二行\n\n新段落"})
    assert r.json()["id"] == 4
    sent = dict(CALLS)["mod_forum_add_discussion"]
    assert sent["forumid"] == "1" and sent["message"] == "<p>第一行<br>第二行</p><p>新段落</p>"
    s = login(client, "s")
    assert not client.get("/api/v1/courses/7/announcements", headers=s).json()["can_post"]


def test_discussions_reply_and_lock(client):
    h = login(client, "s")
    f = client.get("/api/v1/courses/7/forums", headers=h).json()["forums"]
    assert [x["name"] for x in f] == ["答疑区"]
    d = client.get("/api/v1/discussions/3", headers=h).json()
    assert d["subject"] == "问题" and d["posts"][1]["parent"] == 30
    assert client.post("/api/v1/posts/30/reply", headers=h, json={"message": "谢谢"}).json()["id"] == 32
    assert dict(CALLS)["mod_forum_add_discussion_post"]["subject"] == "Re: 问题"
    client.put("/api/v1/discussions/3/lock", headers=h, json={"on": True})
    assert dict(CALLS)["mod_forum_set_lock_state"]["targetstate"] == "0"


def test_people_privacy_and_ai_groups(client):
    s = login(client, "s")
    p = client.get("/api/v1/courses/7/people", headers=s).json()
    assert not p["can_manage"] and all(u["email"] == "" for u in p["members"])
    assert p["groups"][0]["members"] == [10, 11]
    assert client.post("/api/v1/courses/7/groups/ai", headers=s, json={"request": ""}).status_code == 403

    h = login(client)
    p = client.get("/api/v1/courses/7/people", headers=h).json()
    assert p["can_manage"] and p["members"][0]["role"] == "teacher" and p["members"][1]["email"]
    plan = client.post("/api/v1/courses/7/groups/ai", headers=h, json={"request": "3人一组，成绩均衡"}).json()
    assert plan["has_grades"] and len(plan["groups"]) == 3
    everyone = sorted(u for g in plan["groups"] for u in g["members"])
    assert everyone == list(range(10, 19))  # every student exactly once
    r = client.post("/api/v1/courses/7/groups/apply", headers=h,
                    json={"groups": [{"name": g["name"], "members": g["members"]} for g in plan["groups"]], "replace": True})
    assert r.status_code == 200
    sent = dict(CALLS)["local_wenquest_manage_groups"]
    assert sent["action"] == "applyplan" and sent["replace"] == "1" and sent["plan[0][userids][0]"]
    r = client.post("/api/v1/courses/7/people", headers=h, json={"identifiers": ["s9", "nobody", " "]}).json()
    assert r["added"] == ["s9"] and r["notfound"] == ["nobody"]


def test_meetings_need_a_link_or_number(client):
    h = login(client)
    body = {"name": "第3周答疑", "provider": "tencent", "timestart": 1790000000, "duration": 60}
    assert client.post("/api/v1/courses/7/meetings", headers=h, json=body).status_code == 400
    r = client.post("/api/v1/courses/7/meetings", headers=h, json={**body, "url": "meeting.tencent.com/dm/abc"})
    assert r.status_code == 200 and dict(CALLS)["local_wenquest_save_meeting"]["url"] == "https://meeting.tencent.com/dm/abc"


def test_plan_repair():
    plan = ca.validate_plan([{"name": "A", "members": [1, 2, 2, 99]}, {"name": "", "members": ["x", 3]}], [1, 2, 3, 4])
    assert plan[0]["members"] == [1, 2] and plan[1]["name"] == "第2组" and sorted(plan[1]["members"]) == [3, 4]
