"""Round 6: course committee — AI pre-review, submission with the opinion, return with comments, revision, approval
by the chair (publishing), self-review rule, committee pages and administration."""
from app import main
from tests.test_materials import login
from tests.test_studio import _write_first_lesson, client, settle  # noqa: F401 - the fixture


def student_login(client):
    r = client.post("/api/v1/auth/login", json={"username": "s", "password": "p"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_the_whole_review_flow(client):
    h = login(client)
    pid, p = _write_first_lesson(client, h)
    les = p["outline"]["chapters"][0]["lessons"][0]
    base = f"/api/v1/studio/projects/{pid}/lessons/{les['id']}"
    # no committee yet: the pre-review works, submitting to the committee does not
    client.post(f"{base}/submit", headers=h)
    p = settle(client, h, pid)
    les = p["outline"]["chapters"][0]["lessons"][0]
    op = les["review_flow"]["prereview"]
    assert les["review_flow"]["state"] == "prereviewed" and op["verdict"] in ("approve", "revise") and op["items"]
    assert "AI 预审完成" in p["messages"][-1]["text"]
    r = client.post(f"{base}/to-committee", headers=h, json={"comment": "请主任看一下例题"})
    assert r.status_code == 409 and r.json()["error"] == "no_committee"
    # the committee: the student account (user 6) is the chair; the teacher may not approve
    main._studio().committee.save({"members": [{"id": 6, "name": "主任", "email": ""}], "chair": 6, "self_review": True})
    p = client.post(f"{base}/to-committee", headers=h, json={"comment": "请主任看一下例题"}).json()
    assert p["outline"]["chapters"][0]["lessons"][0]["review_flow"]["state"] == "submitted"
    assert client.post(f"{base}/approve", headers=h).status_code == 403                      # not the chair
    assert client.post(f"{base}/write", headers=h, json={"note": "x"}).status_code == 409   # locked while the committee has it
    hs = student_login(client)
    me = client.get("/api/v1/committee/me", headers=hs).json()
    assert me["member"] and me["chair"] and me["waiting"] == 1
    assert client.get("/api/v1/committee/queue", headers=h).status_code == 403              # the teacher is not a member
    q = client.get("/api/v1/committee/queue", headers=hs).json()["items"]
    assert q[0]["lid"] == les["id"] and q[0]["verdict"] == op["verdict"]
    item = client.get(f"/api/v1/committee/items/{pid}/{les['id']}", headers=hs).json()
    assert item["flow"]["note"] == "请主任看一下例题" and item["lesson"]["content"]["zh"] and item["flow"]["prereview"]
    # returned with comments
    assert client.post(f"/api/v1/committee/items/{pid}/{les['id']}/return", headers=hs, json={"comment": ""}).status_code == 422
    client.post(f"/api/v1/committee/items/{pid}/{les['id']}/return", headers=hs, json={"comment": "例题 2 的数值不对，请重算"})
    p = client.get(f"/api/v1/studio/projects/{pid}", headers=h).json()
    les = p["outline"]["chapters"][0]["lessons"][0]
    assert les["review_flow"]["state"] == "returned" and "例题 2 的数值不对" in p["messages"][-1]["text"]
    # revised by the lecturer with the comments, reviewed again, approved by the chair → published
    client.post(f"{base}/revise-from-review", headers=h)
    p = settle(client, h, pid, 30)
    les = p["outline"]["chapters"][0]["lessons"][0]
    assert "例题 2 的数值不对" in les["notes"] and les["review_flow"]["state"] == ""
    client.post(f"{base}/submit", headers=h)
    settle(client, h, pid)
    client.post(f"{base}/to-committee", headers=h, json={"comment": "已按意见改"})
    r = client.post(f"/api/v1/committee/items/{pid}/{les['id']}/approve", headers=hs, json={"comment": "可以发布"})
    assert r.status_code == 200
    p = client.get(f"/api/v1/studio/projects/{pid}", headers=h).json()
    les = p["outline"]["chapters"][0]["lessons"][0]
    assert les["status"] == "published" and les["review_flow"]["state"] == "approved"
    assert [x["action"] for x in les["review_flow"]["history"]] == [
        "submit", "prereview", "to_committee", "return", "revise", "submit", "prereview", "to_committee", "approve"]
    assert "主任意见：可以发布" in p["messages"][-1]["text"]
    assert client.get("/api/v1/committee/queue?done=true", headers=hs).json()["items"][0]["state"] == "approved"


def test_own_lesson_needs_another_member_unless_self_review(client):
    h = login(client)
    pid, p = _write_first_lesson(client, h)
    les = p["outline"]["chapters"][0]["lessons"][0]
    base = f"/api/v1/studio/projects/{pid}/lessons/{les['id']}"
    main._studio().committee.save({"members": [{"id": 5, "name": "T", "email": ""}], "chair": 5, "self_review": False})
    client.post(f"{base}/submit", headers=h)
    settle(client, h, pid)
    client.post(f"{base}/to-committee", headers=h, json={"comment": ""})
    r = client.post(f"{base}/approve", headers=h)
    assert r.status_code == 403 and r.json()["error"] == "own_lesson"
    main._studio().committee.save({"members": [{"id": 5, "name": "T", "email": ""}], "chair": 5, "self_review": True})
    p = client.post(f"{base}/approve", headers=h).json()
    les = p["outline"]["chapters"][0]["lessons"][0]
    assert les["status"] == "published" and "本人审核" in les["review_flow"]["history"][-1]["who"]


def test_only_administrators_set_the_committee(client):
    h = login(client)
    assert client.put("/api/v1/admin/committee", headers=h, json={"members": ["t"], "chair": "t"}).status_code == 403
