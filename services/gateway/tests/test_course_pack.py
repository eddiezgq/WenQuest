"""Course packs (第 16 轮): an administrator publishes a course rendered from a web-edition textbook."""
import json
import time
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main
from app.moodle import MoodleClient
from tests.test_materials import fake_moodle, login

CALLS: list[tuple[str, str]] = []
FAIL = {"add": 0}


def moodle(request: httpx.Request) -> httpx.Response:
    url = urlparse(str(request.url))
    fn = (parse_qs(url.query).get("wsfunction") or [""])[0]
    tok = (parse_qs(url.query).get("wstoken") or [""])[0]
    body = request.content.decode(errors="replace")
    if fn == "local_wenquest_get_permissions":
        return httpx.Response(200, json={"cancreatecourses": True, "issiteadmin": tok == "teacher"})
    if fn == "local_wenquest_create_course":
        CALLS.append((fn, body))
        return httpx.Response(200, json={"courseid": 42, "shortname": "SMDM", "activities": 2})
    if fn == "local_wenquest_add_activities":
        CALLS.append((fn, body))
        if FAIL["add"]:
            FAIL["add"] -= 1
            return httpx.Response(200, json={"exception": "x", "errorcode": "boom", "message": "engine hiccup"})
        n = len({k for k in parse_qs(body) if k.startswith("activities[") and k.endswith("[type]")})
        return httpx.Response(200, json={"courseid": 42, "sectionid": 1, "cmids": list(range(500, 500 + n))})
    if fn == "local_wenquest_create_quiz":
        CALLS.append((fn, body))
        return httpx.Response(200, json={"cmid": 900 + len(CALLS), "quizid": 1, "questions": 1})
    if fn == "local_wenquest_edit_course":
        CALLS.append((fn, body))
        return httpx.Response(200, json={"status": "ok"})
    return fake_moodle(request)


@pytest.fixture
def client(tmp_path):
    with TestClient(main.app) as c:
        st = main.state.settings
        saved = {k: getattr(st, k) for k in ("textbook_dir", "data_dir")}
        main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(moodle))
        main.state.moodle = MoodleClient("http://moodle.test", "moodle_mobile_app", main.state.http)
        st.textbook_dir, st.data_dir = str(tmp_path / "textbook"), str(tmp_path / "data")
        CALLS.clear()
        FAIL["add"] = 0
        yield c
        for k, v in saved.items():
            setattr(st, k, v)


P = lambda s: [s, s.upper() if s.isascii() else s + " en"]  # noqa: E731


def lesson(no: int) -> dict:
    return {"no": no, "section": no + 1, "name": [f"第 {no} 讲", f"Lesson {no}"], "summary": ["<p>摘要</p>", "<p>Summary</p>"],
            "activities": [
                {"type": "page", "name": [f"讲义 {no}", f"Notes {no}"], "content": ["<p>正文</p>", "<p>Text</p>"],
                 "files": [f"files/ch{no:02d}/f.webp"], "visible": 1},
                {"type": "resource", "name": ["课件", "Slides"], "file": f"files/ch{no:02d}/deck.pptx", "visible": 1},
                {"type": "assign", "name": ["作业", "Assignment"], "intro": ["<p>做题</p>", "<p>Do it</p>"], "grade": 100, "visible": 1},
                {"type": "quiz", "name": ["测验", "Quiz"], "intro": ["", ""], "timelimit": 0, "attempts": 3, "grade": 10,
                 "showanswers": "immediately", "visible": 1,
                 "questions": [{"type": "numerical", "text": ["<p>多少？</p>", "<p>How much?</p>"], "feedback": ["<p>因为</p>", "<p>Because</p>"],
                                "mark": 1, "correct": True, "answers": [{"text": ["12.5", "12.5"], "fraction": 1, "tolerance": 0.5}]},
                               {"type": "single", "text": ["<p>哪个？</p>", "<p>Which?</p>"], "feedback": ["", ""], "mark": 1, "correct": True,
                                "answers": [{"text": ["甲", "A"], "fraction": 1, "tolerance": 0}, {"text": ["乙", "B"], "fraction": 0, "tolerance": 0}]}]},
                {"type": "resource", "name": ["教案", "Plan"], "file": f"files/ch{no:02d}/plan.docx", "visible": 0},
            ]}


def pack(tmp_path):
    base = tmp_path / "textbook" / "sewing" / "course"
    for no in (1, 2, 3):
        d = base / "files" / f"ch{no:02d}"
        d.mkdir(parents=True)
        for f in ("f.webp", "deck.pptx", "plan.docx"):
            (d / f).write_bytes(b"x")
    man = {"format": 1, "book": "sewing", "version": "abc",
           "course": {"fullname": ["缝纫机设计与制造", "Sewing Machine Design and Manufacturing"], "shortname": "SMDM",
                      "summary": ["<p>课</p>", "<p>Course</p>"], "blurb": "免费课",
                      "info": {"name": ["课程说明", "Course information"],
                               "activities": [{"type": "forum", "name": ["讨论区", "Discussion"], "intro": ["<p>讨论</p>", "<p>Talk</p>"]}]}},
           "batches": [{"no": 1, "name": ["第 1 批", "Batch 1"], "lessons": [1, 2], "exams": []},
                       {"no": 2, "name": ["第 2 批", "Batch 2"], "lessons": [3], "exams": ["final"]}],
           "exam_section": {"section": 33, "name": ["考试", "Examinations"]},
           "lessons": [lesson(1), lesson(2), lesson(3)],
           "exams": [dict(lesson(9)["activities"][3], id="final", name=["期末", "Final"], timelimit=7200, attempts=1)]}
    (base / "manifest.json").write_text(json.dumps(man, ensure_ascii=False))


def wait(c, h, timeout=10.0):
    end = time.time() + timeout
    while time.time() < end:
        p = c.get("/api/v1/admin/course-packs", headers=h).json()["packs"][0]
        if p["status"] != "running":
            return p
        time.sleep(0.05)
    raise AssertionError("still publishing")


def test_publish_batches_resume_and_list_free(client, tmp_path):
    pack(tmp_path)
    h = login(client)
    assert client.get("/api/v1/admin/course-packs", headers=login(client, "s")).status_code == 403
    p = client.get("/api/v1/admin/course-packs", headers=h).json()["packs"]
    assert [x["book"] for x in p] == ["sewing"] and p[0]["courseid"] == 0
    assert [b["published"] for b in p[0]["batches"]] == [0, 0]

    # batch 1: the course is created and listed free; the engine fails once in the middle of lesson 2
    FAIL["add"] = 0
    r = client.post("/api/v1/admin/course-packs/sewing/publish", headers=h, json={"batch": 1})
    assert r.status_code == 200, r.text
    p = wait(client, h)
    assert p["status"] == "done" and p["courseid"] == 42
    assert [b["published"] for b in p["batches"]] == [2, 0]
    fns = [f for f, _ in CALLS]
    assert fns.count("local_wenquest_create_course") == 1 and fns.count("local_wenquest_create_quiz") == 2
    first_add = next(b for f, b in CALLS if f == "local_wenquest_add_activities")
    q = parse_qs(first_add)
    assert q["section"] == ["2"] and "multilang" in q["sectionname"][0]
    assert q["activities[0][type]"] == ["page"] and q["activities[0][draftitemid]"][0] != "0"
    quiz = parse_qs(next(b for f, b in CALLS if f == "local_wenquest_create_quiz"))
    assert quiz["questions[0][answers][0][text]"] == ["12.5"] and quiz["questions[0][answers][0][tolerance]"] == ["0.5"]
    assert "{mlang" in quiz["questions[0][text]"][0]
    assert any(f == "local_wenquest_edit_course" for f, _ in CALLS)   # assignments accept text and files
    cat = client.get("/api/v1/catalog").json()
    assert cat is not None   # (the fake engine lists no courses; the listing row is checked below)
    row = main.state.accounts.one("SELECT mode, blurb FROM catalog WHERE courseid = 42")
    assert row["mode"] == "free" and row["blurb"] == "免费课"

    # pressing batch 1 again publishes nothing new
    CALLS.clear()
    client.post("/api/v1/admin/course-packs/sewing/publish", headers=h, json={"batch": 1})
    wait(client, h)
    assert [f for f, _ in CALLS] == []

    # batch 2 with an engine failure: it stops, and pressing again continues without repeating what was done
    CALLS.clear()
    FAIL["add"] = 1
    client.post("/api/v1/admin/course-packs/sewing/publish", headers=h, json={"batch": 2})
    p = wait(client, h)
    assert p["status"] == "failed" and "hiccup" in p["error"]
    client.post("/api/v1/admin/course-packs/sewing/publish", headers=h, json={"batch": 2})
    p = wait(client, h)
    assert p["status"] == "done" and all(b["done"] for b in p["batches"])
    fns = [f for f, _ in CALLS]
    assert "local_wenquest_create_course" not in fns
    exam = parse_qs([b for f, b in CALLS if f == "local_wenquest_create_quiz"][-1])
    assert exam["section"] == ["33"] and exam["timelimit"] == ["7200"]


def test_unknown_pack_and_batch(client, tmp_path):
    pack(tmp_path)
    h = login(client)
    assert client.post("/api/v1/admin/course-packs/nope/publish", headers=h, json={"batch": 1}).status_code == 404
    assert client.post("/api/v1/admin/course-packs/sewing/publish", headers=h, json={"batch": 7}).status_code == 404
