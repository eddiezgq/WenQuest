"""Importing course materials: extraction, classification, outline, publishing with attachments."""
import io
import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("WQ_MOODLE_URL", "http://moodle.test")
os.environ.setdefault("WQ_SECRET_KEY", "unit-test-secret")

from app import main  # noqa: E402
from app import materials as mt  # noqa: E402
from app.ai import ModelGateway  # noqa: E402
from app.moodle import MoodleClient  # noqa: E402

BASE = "http://moodle.test"
SENT = {}
UPLOADS = []


def docx_bytes(paragraphs):
    import docx
    d = docx.Document()
    for p in paragraphs:
        d.add_paragraph(p)
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


def fake_moodle(request: httpx.Request) -> httpx.Response:
    url = urlparse(str(request.url))
    if url.path == "/login/token.php":
        form = parse_qs(request.content.decode())
        return httpx.Response(200, json={"token": "teacher" if form["username"] == ["t"] else "student"})
    if url.path == "/webservice/upload.php":
        UPLOADS.append(request.content)
        return httpx.Response(200, json=[{"itemid": 1000 + len(UPLOADS), "filename": "x"}])
    q = parse_qs(url.query)
    fn, tok = q["wsfunction"][0], q["wstoken"][0]
    if fn == "core_webservice_get_site_info":
        return httpx.Response(200, json={"userid": 5 if tok == "teacher" else 6, "fullname": "T", "username": "t"})
    if fn == "local_wenquest_get_permissions":
        return httpx.Response(200, json={"cancreatecourses": tok == "teacher", "issiteadmin": False})
    if fn == "local_wenquest_create_course":
        SENT.clear()
        SENT.update({k: v[0] for k, v in parse_qs(request.content.decode()).items()})
        return httpx.Response(200, json={"courseid": 7, "shortname": "X", "activities": 9})
    return httpx.Response(200, json={"exception": "x", "errorcode": "invalidrecord", "message": fn})


@pytest.fixture
def client(tmp_path):
    with TestClient(main.app) as c:
        main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(fake_moodle))
        main.state.moodle = MoodleClient(BASE, "moodle_mobile_app", main.state.http)
        main.state.ai = ModelGateway("fake", main.state.http)
        main.state.store = mt.Store(str(tmp_path))
        yield c


def login(c, who="t"):
    r = c.post("/api/v1/auth/login", json={"username": who, "password": "x"})
    return {"Authorization": "Bearer " + r.json()["token"]}


def upload(c, h, iid, path, data):
    return c.post(f"/api/v1/imports/{iid}/files", headers=h, data={"path": path},
                  files={"file": (Path(path).name, data, "application/octet-stream")})


FOLDER = {
    "课程/大学物理教学大纲.docx": docx_bytes(["《大学物理A（上）》课程教学大纲", "课程目标：掌握力学基本规律"]),
    "课程/第1章/第1章教案.docx": docx_bytes(["教学目标", "教学重点", "教学过程"]),
    "课程/第1章/讲义.docx": docx_bytes(["第1章  质点运动学", "1.1  参考系与质点", "内容一", "1.2  速度和加速度", "内容二"]),
    "课程/第1章/习题1.docx": docx_bytes(["1. 求速度。", "2. 求加速度。"]),
    "课程/ch2/ch2 notes.docx": docx_bytes(["第2章  牛顿运动定律", "2.1  三定律", "2.2  常见的力"]),
    "课程/测验/期中参考答案.docx": docx_bytes(["1. B 2. C"]),
    "课程/图/cover.png": b"\x89PNG\r\n\x1a\n" + b"0" * 20,
    "课程/新建文本文档.txt": "监考安排：第9周".encode(),
}


def test_full_import_flow(client):
    h = login(client)
    iid = client.post("/api/v1/imports", headers=h).json()["import_id"]
    got = {}
    for path, data in FOLDER.items():
        r = upload(client, h, iid, path, data)
        assert r.status_code == 200, r.text
        got[path] = r.json()
    assert got["课程/大学物理教学大纲.docx"]["category"] == "syllabus"
    assert got["课程/第1章/第1章教案.docx"]["category"] == "lesson_plan" and got["课程/第1章/第1章教案.docx"]["teacher_only"]
    assert (got["课程/第1章/讲义.docx"]["category"], got["课程/第1章/讲义.docx"]["chapter"]) == ("notes", 1)
    assert got["课程/第1章/讲义.docx"]["headings"] == ["1.1 参考系与质点", "1.2 速度和加速度"]
    assert (got["课程/ch2/ch2 notes.docx"]["category"], got["课程/ch2/ch2 notes.docx"]["chapter"]) == ("notes", 2)
    assert got["课程/测验/期中参考答案.docx"]["category"] == "answer_key"
    assert got["课程/图/cover.png"]["category"] == "media"
    assert got["课程/新建文本文档.txt"]["category"] == "other"

    # teacher moves the picture to chapter 2
    pic = got["课程/图/cover.png"]["id"]
    r = client.put(f"/api/v1/imports/{iid}/files", headers=h, json=[{"id": pic, "category": "media", "chapter": 2}])
    assert next(f for f in r.json()["files"] if f["id"] == pic)["confidence"] == "teacher"

    o = client.post(f"/api/v1/imports/{iid}/outline", headers=h, json={"languages": "zh"}).json()
    titles = [s["title"]["zh"] for s in o["sections"]]
    assert titles[0] == "课程说明" and "第1章 质点运动学" in titles and "第2章 牛顿运动定律" in titles
    ch1 = o["sections"][titles.index("第1章 质点运动学")]
    assert [l["title"]["zh"] for l in ch1["lessons"]] == ["1.1 参考系与质点", "1.2 速度和加速度"]
    assert ch1["assignment"]["brief"]["zh"].startswith("1. 求速度")
    assert got["课程/第1章/讲义.docx"]["id"] in ch1["lessons"][0]["sources"]
    assert o["title"]["zh"] == "大学物理A（上）"

    # lesson written from sources, with a citation
    les = client.post("/api/v1/ai/lesson", headers=h, json={
        "import_id": iid, "sources": ch1["lessons"][0]["sources"], "course_title": "c", "section_title": "s",
        "lesson_title": "1.1 参考系与质点", "languages": "zh"}).json()
    assert "参考：讲义.docx" in les["content"]["zh"]

    # publish: files uploaded and attached; lesson plan hidden
    for s in o["sections"]:
        for l in s["lessons"]:
            l["content"] = {"zh": "<p>正文</p>"}
    r = client.post("/api/v1/courses", headers=h, json=o)
    assert r.status_code == 200, r.text
    acts = {k: v for k, v in SENT.items() if "[activities]" in k}
    names = {v: k for k, v in acts.items() if k.endswith("[name]")}
    plan_key = names["第1章教案"].replace("[name]", "")
    assert acts[plan_key + "[type]"] == "resource" and acts[plan_key + "[visible]"] == "0"
    notes_key = names["讲义"].replace("[name]", "")
    assert acts[notes_key + "[visible]"] == "1"
    assert "新建文本文档" not in names and len(UPLOADS) >= 5


def test_imports_are_private(client):
    h = login(client)
    iid = client.post("/api/v1/imports", headers=h).json()["import_id"]
    student = login(client, "s")
    assert client.post("/api/v1/imports", headers=student).status_code == 403
    assert client.get(f"/api/v1/imports/{iid}", headers=student).status_code == 403
    assert client.get("/api/v1/imports/" + "0" * 32, headers=h).status_code == 404
    assert client.get("/api/v1/imports/../../etc", headers=h).status_code == 404


def test_outline_needs_chapters(client):
    h = login(client)
    iid = client.post("/api/v1/imports", headers=h).json()["import_id"]
    upload(client, h, iid, "random.txt", b"hello")
    r = client.post(f"/api/v1/imports/{iid}/outline", headers=h, json={})
    assert r.status_code == 422 and r.json()["error"] == "no_chapters"


def test_unreadable_file_does_not_break_import(client):
    h = login(client)
    iid = client.post("/api/v1/imports", headers=h).json()["import_id"]
    r = upload(client, h, iid, "第1章/坏文件.pdf", b"not a pdf")
    assert r.status_code == 200 and r.json()["error"] == "unreadable" and r.json()["chapter"] == 1


def test_chapter_detection():
    assert mt.chapter_of("第三章 动量/作业.docx") == 3
    assert mt.chapter_of("Ch3 slides.pptx") == 3
    assert mt.chapter_of("x/ch2_教案.docx") == 2
    assert mt.chapter_of("1-质点运动学讲义.pdf") == 1
    assert mt.chapter_of("习题4.docx") == 4
    assert mt.chapter_of("素材/单摆.png") is None


def test_ai_classification_only_fills_gaps():
    a = mt.Material(id="a" * 32, name="x.txt", path="x.txt", size=1, ext=".txt", category="other", confidence="unsure")
    b = mt.Material(id="b" * 32, name="教案.docx", path="教案.docx", size=1, ext=".docx", category="lesson_plan", confidence="teacher")
    mt.apply_ai([a, b], {"files": [{"id": "a" * 32, "category": "notes", "chapter": 2},
                                   {"id": "b" * 32, "category": "notes", "chapter": 5}]})
    assert (a.category, a.chapter, a.confidence) == ("notes", 2, "ai")
    assert (b.category, b.chapter) == ("lesson_plan", None)  # teacher's choice is never overwritten


def test_source_ids_capped_for_crowded_chapters():
    from app import materials as mt
    items = [mt.Material(id=f"m{i}", name=f"实验{i} 实验指导书.docx", path=f"第1章/实验{i}.docx", size=1, ext="docx",
                         chars=100, category="lab", chapter=1) for i in range(12)]
    items.append(mt.Material(id="notes", name="讲义.pdf", path="第1章/讲义.pdf", size=1, ext="pdf", chars=100, category="notes", chapter=1))
    ids = mt.source_ids(items, 1)
    assert len(ids) == mt.MAX_SOURCES and ids[0] == "notes"
