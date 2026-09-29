"""Course work in WenQuest's own UI (step B2): quiz questions, assignments and grading."""
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main
from app import quiz_parse as qp
from app.ai import ModelGateway
from app.moodle import MoodleClient
from tests.test_materials import BASE, fake_moodle, login

FIX = Path(__file__).parent / "fixtures" / "quiz"
TYPES = ["multichoice", "multichoice", "truefalse", "shortanswer", "numerical"]


def parsed(kind: str, i: int) -> dict:
    return qp.parse_question({"html": (FIX / f"{kind}_{i}.html").read_text(), "type": TYPES[i if kind == "attempt" else i - 1],
                              "slot": i + 1 if kind == "attempt" else i}, lambda h: h)


def test_questions_become_plain_data():
    single, multi, tf, fill, num = (parsed("attempt", i) for i in range(5))
    assert single["kind"] == "choice" and len(single["options"]) == 4 and single["input"] == "q1:1_answer"
    assert "指向圆心" in [o["label"] for o in single["options"]]
    assert multi["kind"] == "multi" and multi["options"][0]["name"] == "q1:2_choice0"
    assert [o["label"] for o in tf["options"]] == ["true", "false"]
    assert fill["kind"] == "text" and fill["inline"] and "＿＿＿＿" in fill["text"] and "<input" not in fill["text"]
    assert num["numeric"] and num["sequence"] == {"name": "q1:5_:sequencecheck", "value": "1"}


def test_answers_become_moodle_form_fields():
    qs = [parsed("attempt", i) for i in range(5)]
    data = qp.form_data(qs, {"1": "1", "2": ["q1:2_choice2"], "3": "0", "4": "参考系", "5": "40"})
    d = {x["name"]: x["value"] for x in data}
    assert d["q1:1_answer"] == "1" and d["q1:2_choice2"] == "1" and d["q1:2_choice0"] == "0"
    assert d["q1:4_answer"] == "参考系" and d["q1:5_:sequencecheck"] == "1"


def test_review_shows_results_and_right_answers():
    single, multi, tf = parsed("review", 1), parsed("review", 2), parsed("review", 3)
    assert single["result"] == "correct" and "指向圆心" in single["rightanswer"]
    assert next(o for o in single["options"] if o["checked"])["feedback"].startswith("对")
    assert multi["result"] == "incorrect" and multi["rightanswer"] == "速度, 加速度"
    assert tf["rightanswer"] == "false"


CALLS: list[tuple[str, dict]] = []
STATE = {"status": "new", "drafts": 0}


def moodle(request: httpx.Request) -> httpx.Response:
    q = parse_qs(urlparse(str(request.url)).query)
    fn = (q.get("wsfunction") or [""])[0]
    tok = (q.get("wstoken") or [""])[0]
    body = {k: v[0] for k, v in parse_qs(request.content.decode(errors="ignore")).items()} if fn else {}
    CALLS.append((fn, body))
    if fn == "core_course_get_course_module":
        return httpx.Response(200, json={"cm": {"id": 50, "modname": "assign", "course": 7, "instance": 3, "name": "作业1"}})
    if fn == "mod_assign_get_assignments":
        return httpx.Response(200, json={"courses": [{"id": 7, "assignments": [{
            "id": 3, "cmid": 50, "name": "作业1", "intro": "<p>评分：步骤 60，结果 40</p>", "grade": 100, "duedate": 0,
            "submissiondrafts": STATE["drafts"],
            "configs": [{"plugin": "onlinetext", "subtype": "assignsubmission", "name": "enabled", "value": "1"},
                        {"plugin": "file", "subtype": "assignsubmission", "name": "enabled", "value": "1"},
                        {"plugin": "file", "subtype": "assignsubmission", "name": "maxfilesubmissions", "value": "2"}]}]}]})
    if fn == "mod_assign_get_submission_status":
        return httpx.Response(200, json={"lastattempt": {"canedit": True, "cansubmit": True, "submission": {
            "status": STATE["status"], "timemodified": 5,
            "plugins": [{"type": "onlinetext", "editorfields": [{"text": "<p>a = 4 m/s²</p>"}]},
                        {"type": "file", "fileareas": [{"files": [{"filename": "old.pdf", "fileurl": BASE + "/webservice/pluginfile.php/1/x/old.pdf"}]}]}]}},
            "gradingsummary": {"participantcount": 3}})
    if fn == "mod_assign_save_submission":
        STATE["status"] = "draft" if STATE["drafts"] else "submitted"
        return httpx.Response(200, json=[])
    if fn == "mod_assign_submit_for_grading":
        STATE["status"] = "submitted"
        return httpx.Response(200, json=[])
    if fn in ("mod_assign_save_grade", "mod_assign_view_assign"):
        return httpx.Response(200, content=b"null", headers={"content-type": "application/json"})
    if fn == "core_course_get_user_administration_options":
        return httpx.Response(200, json={"courses": [{"id": 7, "options": [{"name": "update", "available": tok == "teacher"}]}]})
    if "/webservice/pluginfile.php/" in str(request.url):
        return httpx.Response(200, content=b"%PDF old", headers={"content-type": "application/pdf"})
    return fake_moodle(request)


@pytest.fixture
def client():
    with TestClient(main.app) as c:
        main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(moodle))
        main.state.moodle = MoodleClient(BASE, "moodle_mobile_app", main.state.http)
        main.state.ai = ModelGateway("fake", main.state.http)
        CALLS.clear()
        STATE.update(status="new", drafts=0)
        yield c


def test_submitting_keeps_or_replaces_files(client):
    s = login(client, "s")
    # text only, keeping the existing file: the file area is left alone
    r = client.post("/api/v1/assignments/50/submission", headers=s, data={"text": "a = 4", "keep": '["old.pdf"]', "submit": "true"})
    assert r.status_code == 200 and r.json()["status"] == "submitted"
    sent = dict(CALLS)["mod_assign_save_submission"]
    assert "plugindata[files_filemanager]" not in sent and sent["plugindata[onlinetext_editor][text]"] == "<p>a = 4</p>"
    assert "mod_assign_submit_for_grading" not in dict(CALLS)   # no drafts: saving is handing in
    # a new file next to the kept one: both go into one draft area
    CALLS.clear()
    r = client.post("/api/v1/assignments/50/submission", headers=s, data={"keep": '["old.pdf"]'},
                    files=[("files", ("new.txt", b"hello", "text/plain"))])
    assert r.status_code == 200 and dict(CALLS)["mod_assign_save_submission"]["plugindata[files_filemanager]"]
    # more files than allowed
    r = client.post("/api/v1/assignments/50/submission", headers=s, data={"keep": '["old.pdf"]'},
                    files=[("files", ("a.txt", b"1", "text/plain")), ("files", ("b.txt", b"2", "text/plain"))])
    assert r.status_code == 400 and r.json()["error"] == "too_many_files"


def test_drafts_then_hand_in(client):
    STATE["drafts"] = 1
    s = login(client, "s")
    assert client.post("/api/v1/assignments/50/submission", headers=s, data={"text": "x", "keep": "[]"}).json()["status"] == "draft"
    assert client.post("/api/v1/assignments/50/submission", headers=s, data={"keep": "[]", "submit": "true"}).json()["status"] == "submitted"
    assert "mod_assign_submit_for_grading" in dict(CALLS)


def test_grading_and_ai_suggestion(client):
    h = login(client)
    assert client.put("/api/v1/assignments/50/grades/9", headers=h, json={"grade": 120}).status_code == 400
    assert client.put("/api/v1/assignments/50/grades/9", headers=h, json={"grade": 85, "feedback": "很好"}).status_code == 200
    sent = dict(CALLS)["mod_assign_save_grade"]
    assert sent["grade"] == "85.0" and sent["plugindata[assignfeedbackcomments_editor][text]"] == "<p>很好</p>"
    ai = client.post("/api/v1/assignments/50/submissions/9/ai", headers=h).json()
    assert ai["max_grade"] == 100 and 0 <= ai["grade"] <= 100 and ai["comment"]
    s = login(client, "s")
    assert client.post("/api/v1/assignments/50/submissions/9/ai", headers=s).status_code == 403
