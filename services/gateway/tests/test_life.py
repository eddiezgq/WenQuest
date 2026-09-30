"""A course's life after teaching: take down, delete into the recycle bin, restore, delete for good, download."""
import io
import time
import zipfile
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main
from app import materials as mt
from app import studio as st
from app.ai import ModelGateway
from app.moodle import MoodleClient
from tests.test_materials import BASE, fake_moodle, login

BIN: dict[int, dict] = {}
VISIBLE: dict[int, int] = {}
CALLS: list[tuple[str, dict]] = []


def moodle(request: httpx.Request) -> httpx.Response:
    url = urlparse(str(request.url))
    if url.path.startswith("/webservice/pluginfile.php/"):
        name = url.path.rsplit("/", 1)[-1]
        return httpx.Response(200, content=f"FILE:{name}".encode(), headers={"content-type": "application/octet-stream"})
    q = parse_qs(url.query)
    fn = (q.get("wsfunction") or [""])[0]
    tok = (q.get("wstoken") or [""])[0]
    body = {k: v[0] for k, v in parse_qs(request.content.decode()).items()} if request.content else {}
    teacher = tok == "teacher"
    if fn == "core_course_get_user_administration_options":
        cid = int(body["courseids[0]"])
        return httpx.Response(200, json={"courses": [{"id": cid, "options": [{"name": "update", "available": teacher}]}]})
    if fn == "local_wenquest_edit_course":
        CALLS.append((fn, body))
        VISIBLE[int(body["courseid"])] = int(body["visible"])
        return httpx.Response(200, json={"ok": True, "sectionid": 0, "cmid": 0})
    if fn == "local_wenquest_course_life":
        CALLS.append((fn, body))
        a = body["action"]
        base = {"ok": True, "courseid": 0, "oldcourseid": 0, "binid": 0, "fileurl": "", "filesize": 0, "items": []}
        if not teacher:
            return httpx.Response(200, json={"exception": "x", "errorcode": "nopermissions", "message": "no"})
        if a == "delete":
            cid = int(body["courseid"])
            if VISIBLE.get(cid, 1):
                return httpx.Response(200, json={"exception": "x", "errorcode": "coursevisible", "message": "take it down first"})
            bid = 100 + len(BIN)
            BIN[bid] = {"binid": bid, "oldcourseid": cid, "fullname": "<span lang=\"zh_cn\" class=\"multilang\">机器人学</span>",
                        "shortname": "R1", "deletedby": "T", "filesize": 1234, "timecreated": int(time.time())}
            return httpx.Response(200, json={**base, "binid": bid, "oldcourseid": cid})
        if a == "list":
            return httpx.Response(200, json={**base, "items": list(BIN.values())})
        if a == "restore":
            it = BIN.pop(int(body["binid"]))
            return httpx.Response(200, json={**base, "courseid": 90, "oldcourseid": it["oldcourseid"]})
        if a == "purge":
            it = BIN.pop(int(body["binid"]))
            return httpx.Response(200, json={**base, "oldcourseid": it["oldcourseid"]})
        if a in ("backup", "binfile"):
            return httpx.Response(200, json={**base, "fileurl": f"{BASE}/webservice/pluginfile.php/9/local_wenquest/backup/0/R1.mbz",
                                             "filesize": 10})
    if fn == "core_course_get_courses_by_field":
        return httpx.Response(200, json={"courses": [{"id": 7, "fullname": "机器人学", "visible": VISIBLE.get(7, 1)}]})
    if fn == "core_course_get_contents":
        return httpx.Response(200, json=[
            {"id": 1, "section": 1, "name": "第1章 空间描述", "modules": [
                {"id": 77, "modname": "resource", "name": "第1章 虚拟实验", "contents": []},
                {"id": 11, "modname": "resource", "name": "1.1 课件", "contents": [
                    {"type": "file", "filename": "1.1 课件.pptx", "fileurl": f"{BASE}/webservice/pluginfile.php/5/mod_resource/content/0/a.pptx"}]},
                {"id": 12, "modname": "page", "name": "1.1 讲义", "contents": [
                    {"type": "file", "filename": "index.html", "fileurl": f"{BASE}/webservice/pluginfile.php/6/mod_page/content/0/index.html"}]},
                {"id": 13, "modname": "url", "name": "参考网站", "contents": [{"type": "url", "fileurl": "https://example.org"}]},
                {"id": 14, "modname": "quiz", "name": "1.1 测验", "contents": []},
            ]}])
    return fake_moodle(request)


@pytest.fixture
def client(tmp_path, monkeypatch):
    BIN.clear(), VISIBLE.clear(), CALLS.clear()
    with TestClient(main.app) as c:
        main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(moodle))
        main.state.moodle = MoodleClient(BASE, "moodle_mobile_app", main.state.http)
        main.state.ai = ModelGateway("fake", main.state.http)
        main.state.store = mt.Store(str(tmp_path / "imports"))
        main.state.projects_dir = str(tmp_path / "projects")
        monkeypatch.setattr(main.state.settings, "data_dir", str(tmp_path / "data"))
        yield c


def project_for(course_id: int) -> dict:
    studio = main._studio()
    p = st.new_project(5, "T", "a" * 32, "机器人学")
    p["course"]["id"] = course_id
    p["course"]["sections"] = {"c1": 1}
    p["course"]["labs"] = {"c1": 55}
    p["outline"] = {"title": {"zh": "机器人学"}, "chapters": [{"id": "c1", "no": 1, "title": {"zh": "第1章"}, "lessons": [
        {"id": "l1", "status": "published", "cmids": [11, 12], "title": {"zh": "1.1"}}]}]}
    studio.projects.save(p)
    return p


def wait_export(c, h, eid, limit=10.0):
    end = time.time() + limit
    while time.time() < end:
        j = next(x for x in c.get("/api/v1/exports", headers=h).json()["exports"] if x["id"] == eid)
        if j["status"] != "running":
            return j
        time.sleep(0.1)
    raise AssertionError("export did not finish")


def test_take_down_then_delete_restore_and_the_project_follows(client):
    h = login(client)
    p = project_for(7)
    # a course that is still open cannot be deleted
    r = client.delete("/api/v1/courses/7", headers=h)
    assert r.status_code >= 400 and "take it down" in r.text
    assert client.post("/api/v1/courses/7/takedown", headers=h).json() == {"ok": True, "visible": False}
    r = client.delete("/api/v1/courses/7", headers=h)
    assert r.status_code == 200
    proj = main._studio().projects.load(p["id"])
    assert proj["course"]["deleted"]["binid"] == r.json()["binid"] and "回收站" in proj["messages"][-1]["text"]
    items = client.get("/api/v1/trash", headers=h).json()["items"]
    assert items[0]["name"] == "机器人学" and items[0]["projects"][0]["id"] == p["id"]
    r = client.post(f"/api/v1/trash/{items[0]['binid']}/restore", headers=h)
    assert r.json() == {"ok": True, "courseid": 90}
    proj = main._studio().projects.load(p["id"])
    assert proj["course"]["id"] == 90 and "deleted" not in proj["course"]
    assert proj["course"]["labs"] == {"c1": 77}   # the chapter lab page is found again in the restored course


def test_students_cannot(client):
    s = login(client, "s")
    assert client.post("/api/v1/courses/7/takedown", headers=s).status_code == 403
    assert client.post("/api/v1/courses/7/exports", headers=s, json={"kind": "files"}).status_code == 403


def test_purge_keeps_or_deletes_the_project(client):
    h = login(client)
    keep, gone = project_for(7), project_for(8)
    for cid in (7, 8):
        client.post(f"/api/v1/courses/{cid}/takedown", headers=h)
        client.delete(f"/api/v1/courses/{cid}", headers=h)
    items = {i["oldcourseid"]: i["binid"] for i in client.get("/api/v1/trash", headers=h).json()["items"]}
    assert client.delete(f"/api/v1/trash/{items[7]}", headers=h).json()["deleted_projects"] == []
    p = main._studio().projects.load(keep["id"])
    assert p["course"]["id"] == 0 and p["outline"]["chapters"][0]["lessons"][0]["status"] == "awaiting"
    assert client.delete(f"/api/v1/trash/{items[8]}?delete_project=true", headers=h).json()["deleted_projects"] == [gone["id"]]
    with pytest.raises(KeyError):
        main._studio().projects.load(gone["id"])


def test_downloads_backup_and_files_zip(client):
    h = login(client)
    j = client.post("/api/v1/courses/7/exports", headers=h, json={"kind": "backup"}).json()
    j = wait_export(client, h, j["id"])
    assert j["status"] == "done" and j["file"] == "机器人学-备份.mbz"
    r = client.get(j["url"])
    assert r.status_code == 200 and r.content == b"FILE:R1.mbz"
    j = client.post("/api/v1/courses/7/exports", headers=h, json={"kind": "files"}).json()
    j = wait_export(client, h, j["id"])
    z = zipfile.ZipFile(io.BytesIO(client.get(j["url"]).content))
    names = z.namelist()
    assert "01 第1章 空间描述/1.1 课件.pptx" in names and "01 第1章 空间描述/1.1 讲义.html" in names
    index = z.read("课程目录.html").decode()
    assert "参考网站" in index and "https://example.org" in index and "1.1 测验" in index
    # the link is personal and expires; a made-up one does not work
    assert client.get("/api/v1/exports/file/nonsense").status_code == 410


def test_download_from_the_recycle_bin(client):
    h = login(client)
    client.post("/api/v1/courses/7/takedown", headers=h)
    bid = client.delete("/api/v1/courses/7", headers=h).json()["binid"]
    j = client.post(f"/api/v1/trash/{bid}/exports", headers=h).json()
    j = wait_export(client, h, j["id"])
    assert j["status"] == "done" and client.get(j["url"]).content == b"FILE:R1.mbz"
    assert ("local_wenquest_course_life", {"action": "binfile", "binid": str(bid)}) in [(f, {k: v for k, v in b.items() if k in ("action", "binid")}) for f, b in CALLS]
