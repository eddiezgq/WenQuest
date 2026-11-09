"""老师用的网页文档（第 126 轮）：新建（课程里多一个隐藏页面）、保存、发布给学生（页面正文 + 显示）、版本与恢复、
图片、导出 Word / PDF、批量导出、AI 初稿与改一块、只有本课程老师能用；模板栏目与 Word 教案 / 指导书一致。"""
import base64
import io
import json
import zipfile
from urllib.parse import parse_qs, urlparse

import docx
import httpx
import pytest
from fastapi.testclient import TestClient

from app import coursedocs_api, main
from app.ai import ModelGateway
from app.moodle import MoodleClient
from app.production import coursedoc, docs
from tests import test_learn_api as L
from tests.test_materials import BASE, login

PAGES: dict[int, dict] = {}
CALLS: list[tuple[str, dict]] = []


def _docx_bytes() -> bytes:
    d = docx.Document()
    d.add_paragraph("第三章 刚体转动 教学大纲：转动惯量、角动量守恒")
    b = io.BytesIO()
    d.save(b)
    return b.getvalue()


def handler(request: httpx.Request) -> httpx.Response:
    u = str(request.url)
    q = parse_qs(urlparse(u).query)
    fn = (q.get("wsfunction") or [""])[0]
    tok = (q.get("wstoken") or [""])[0]
    body = {k: v[0] for k, v in parse_qs(request.content.decode(errors="ignore")).items()} if fn else {}
    if u.startswith("http://docs/converter"):
        return httpx.Response(200, json={"endConvert": True, "fileUrl": "http://docs/cache/y.pdf"})
    if u.startswith("http://docs/cache/y.pdf"):
        return httpx.Response(200, content=b"%PDF-1.7 doc")
    if fn:
        CALLS.append((fn, body))
    if fn == "core_course_get_user_administration_options":
        return httpx.Response(200, json={"courses": [{"id": 7, "options": [{"name": "update", "available": tok == "teacher"}]}]})
    if fn == "core_course_get_courses_by_field":
        return httpx.Response(200, json={"courses": [{"id": 7, "fullname": "大学物理"}]})
    if fn == "local_wenquest_add_activities":
        cmid = 100 + len(PAGES)
        PAGES[cmid] = {"name": body.get("activities[0][name]"), "content": body.get("activities[0][content]"),
                       "visible": body.get("activities[0][visible]"), "section": int(body.get("section", 0))}
        return httpx.Response(200, json={"cmids": [cmid]})
    if fn == "local_wenquest_edit_course":
        cm = int(body.get("cmid", 0))
        if cm not in PAGES:
            return httpx.Response(200, json={"exception": "x", "errorcode": "invalidrecord", "message": "gone"})
        for k in ("name", "content", "visible"):
            if k in body:
                PAGES[cm][k] = body[k]
        return httpx.Response(200, json={"ok": True})
    if fn == "core_course_get_contents":
        mods = [{"id": c, "modname": "page", "name": p["name"]} for c, p in PAGES.items()]
        return httpx.Response(200, json=[
            {"id": 1, "section": 3, "name": "第三章", "modules": mods + [
                {"id": 90, "modname": "resource", "name": "教学大纲",
                 "contents": [{"type": "file", "filename": "大纲.docx", "fileurl": BASE + "/webservice/pluginfile.php/1/x/大纲.docx"}]}]}])
    if "/webservice/pluginfile.php/" in u:
        return httpx.Response(200, content=_docx_bytes())
    if fn == "core_webservice_get_site_info":
        return httpx.Response(200, json={"fullname": "张老师", "userid": 2})
    return L.moodle(request)


def _png() -> str:
    from PIL import Image
    b = io.BytesIO()
    Image.new("RGB", (2400, 300), "white").save(b, "PNG")
    return base64.b64encode(b.getvalue()).decode()


@pytest.fixture
def client(tmp_path):
    with TestClient(main.app) as c:
        s = main.state.settings
        old = (s.docs_url, s.docs_jwt_secret)
        s.docs_url, s.docs_jwt_secret = "http://docs", "k"
        main.state.coursedocs = coursedocs_api.Store(str(tmp_path / "data"))
        main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        main.state.moodle = MoodleClient(BASE, "moodle_mobile_app", main.state.http)
        main.state.ai = ModelGateway("fake", main.state.http)
        PAGES.clear()
        CALLS.clear()
        yield c
        s.docs_url, s.docs_jwt_secret = old
        main.state.coursedocs = None


def test_create_edit_publish_versions_and_export(client):
    t, s = login(client, "t"), login(client, "s")
    assert client.post("/api/v1/courses/7/webdocs", headers=s, json={"section": 3, "template": "plan", "title": "3.1 刚体"}).status_code == 403
    r = client.post("/api/v1/courses/7/webdocs", headers=t, json={"section": 3, "template": "plan", "title": "3.1 刚体定轴转动"}).json()
    did, cmid = r["id"], r["cmid"]
    assert PAGES[cmid]["visible"] == "0" and PAGES[cmid]["section"] == 3          # a hidden page in chapter 3
    assert PAGES[cmid]["name"] == "3.1 刚体定轴转动 教案"                           # named by its 课题, not “大学物理教案”
    assert r["doc"]["title"][0] == "大学物理教案" and "张老师" in r["doc"]["sub"]
    assert coursedoc.headings(r["doc"]) == coursedoc.PLAN_HEADINGS
    # students cannot read or change the source
    assert client.get(f"/api/v1/webdocs/{did}", headers=s).status_code == 403
    assert client.get(f"/api/v1/webdocs/by-cmid/{cmid}", headers=t).json()["id"] == did
    assert client.get("/api/v1/courses/7/structure", headers=t).json()["sections"][0]["modules"][0]["webdoc"] == did
    # edit: a formula, a picture (made smaller), an unknown block is dropped
    img = client.post(f"/api/v1/webdocs/{did}/images", headers=t, json={"data": "data:image/png;base64," + _png()}).json()
    assert client.get(f"/api/v1/webdoc-img/{img['img']}").status_code == 200
    from PIL import Image
    assert Image.open(io.BytesIO(client.get(f"/api/v1/webdoc-img/{img['img']}").content)).width == 1600
    assert client.post(f"/api/v1/webdocs/{did}/images", headers=t, json={"data": base64.b64encode(b"not a picture").decode()}).status_code == 400
    doc = r["doc"]
    doc["blocks"] += [{"t": "para", "text": "转动定律 $M = J\\alpha$"}, {"t": "image", "img": img["img"], "caption": "图 1"},
                      {"t": "script", "text": "x"}]
    up = client.put(f"/api/v1/webdocs/{did}", headers=t, json={"doc": doc, "base": r["updated"]}).json()
    assert client.put(f"/api/v1/webdocs/{did}", headers=t, json={"doc": doc, "base": 1}).json()["error"] == "doc_changed"
    cur = client.get(f"/api/v1/webdocs/{did}", headers=t).json()
    assert cur["updated"] == up["updated"] and not any(b["t"] == "script" for b in cur["doc"]["blocks"])
    assert cur["published"] == 0
    # publish to students: page content and shown
    p = client.post(f"/api/v1/webdocs/{did}/publish", headers=t, json={"audience": "students"}).json()
    assert p["published"] == 1 and p["audience"] == "students"
    assert PAGES[cmid]["visible"] == "1" and "\\(M = J\\alpha\\)" in PAGES[cmid]["content"]
    assert f"/api/v1/webdoc-img/{img['img']}" in PAGES[cmid]["content"]
    # a new draft does not change the page until published again
    doc = cur["doc"]
    doc["blocks"].append({"t": "callout", "text": "第二版"})
    client.put(f"/api/v1/webdocs/{did}", headers=t, json={"doc": doc})
    assert "第二版" not in PAGES[cmid]["content"]
    p = client.post(f"/api/v1/webdocs/{did}/publish", headers=t, json={"audience": "teachers"}).json()
    assert p["published"] == 2 and PAGES[cmid]["visible"] == "0" and "第二版" in PAGES[cmid]["content"]
    assert [v["ver"] for v in p["versions"]] == [1, 2]
    v1 = client.get(f"/api/v1/webdocs/{did}/versions/1", headers=t).json()["doc"]
    assert not any(b.get("text") == "第二版" for b in v1["blocks"])
    back = client.post(f"/api/v1/webdocs/{did}/restore", headers=t, json={"ver": 1}).json()
    assert not any(b.get("text") == "第二版" for b in back["doc"]["blocks"]) and back["published"] == 2
    # export: Word with the picture, PDF through the online documents service
    w = client.get(f"/api/v1/webdocs/{did}/export?fmt=docx", headers=t)
    assert w.status_code == 200 and "filename*=UTF-8''" in w.headers["content-disposition"]
    wd = docx.Document(io.BytesIO(w.content))
    assert len(wd.inline_shapes) == 1 and any("转动定律" in x.text for x in wd.paragraphs)
    assert client.get(f"/api/v1/webdocs/{did}/export?fmt=pdf", headers=t).content.startswith(b"%PDF")
    # a second plan in chapter 3, then the chapter's plans in one zip
    client.post("/api/v1/courses/7/webdocs", headers=t, json={"section": 3, "template": "plan", "title": "3.2 角动量"})
    client.post("/api/v1/courses/7/webdocs", headers=t, json={"section": 3, "template": "notice", "title": "实验课调课通知"})
    listed = client.get("/api/v1/courses/7/webdocs?section=3&template=plan", headers=t).json()["docs"]
    assert len(listed) == 2
    z = zipfile.ZipFile(io.BytesIO(client.get("/api/v1/courses/7/webdocs.zip?section=3&template=plan", headers=t).content))
    assert sorted(z.namelist()) == ["3.1刚体定轴转动教案.docx", "3.2角动量教案.docx"]
    # the page was deleted in Moodle: publishing says so
    PAGES.pop(cmid)
    assert client.post(f"/api/v1/webdocs/{did}/publish", headers=t, json={"audience": "students"}).json()["error"] == "page_gone"


def test_ai_draft_and_rewrite_a_block(client):
    t = login(client, "t")
    r = client.post("/api/v1/courses/7/webdocs", headers=t, json={"section": 3, "template": "plan", "title": "3.1 刚体"}).json()
    src = client.get("/api/v1/courses/7/ai-sources", headers=t).json()["sources"]
    assert any(x["cmid"] == 90 for x in src)
    d = client.post(f"/api/v1/webdocs/{r['id']}/ai-draft", headers=t,
                    json={"prompt": "2 学时教案，机器人关节举例", "sources": [90]}).json()["doc"]
    assert coursedoc.headings(d) == coursedoc.PLAN_HEADINGS and "AI 初稿" in json.dumps(d, ensure_ascii=False)
    # nothing saved until the teacher takes it
    assert "AI 初稿" not in json.dumps(client.get(f"/api/v1/webdocs/{r['id']}", headers=t).json()["doc"], ensure_ascii=False)
    b = client.post(f"/api/v1/webdocs/{r['id']}/ai-block", headers=t,
                    json={"index": 3, "action": "bilingual", "block": {"t": "para", "text": "重点：转动惯量"}}).json()["block"]
    assert b["t"] == "para" and b["en"]
    assert client.post(f"/api/v1/webdocs/{r['id']}/ai-block", headers=t,
                       json={"index": 0, "action": "poem", "block": {"t": "para", "text": "x"}}).status_code == 400
    assert client.post(f"/api/v1/webdocs/{r['id']}/ai-block", headers=t,
                       json={"index": 0, "action": "rewrite", "block": {"t": "hr"}}).status_code == 400


GP = {"plan": {"audience": "机械类本科", "hours": "", "method": "", "objectives": {"knowledge": "", "ability": "", "literacy": ""},
               "key": "", "difficult": "", "process": [], "board": "", "homework": "", "reflection": ""},
      "guide": {"goal": [["测量转动惯量", "Measure the moment of inertia"]], "theory": [["$J = \\sum m r^2$", "$J = \\sum m r^2$"]],
                "env": [{"item": ["转盘", "Disc"], "range": ["0–1 kg", "0–1 kg"]}], "steps": [["放上转盘", "Put the disc on"]],
                "tables": [{"caption": ["表 1", "Table 1"], "headers": ["m / kg", "J"], "rows": [["", ""]]}],
                "cautions": [["轻放", "Gently"]], "questions": [["为什么？", "Why?"]], "problem_question": ["", ""]}}
SPEC = {"title": ["刚体定轴转动", "Rotation"], "goal": ["理解转动定律", "Understand"],
        "problem": {"title": ["机械臂关节", "Robot joint"], "text": ["关节要多大力矩？", "What torque?"]},
        "concept": {"points": [["转动惯量", "J"], ["转动定律", "M=Ja"]]}, "animation": {"question": ["为什么？", "Why?"]},
        "lab": {"title": ["转动惯量的测量", "Moment of inertia"], "tasks": [["测 J", "Measure J"]],
                "robot_scene": ["机械臂", "Arm"], "life_scene": ["门", "Door"]},
        "model": {"solve": ["M = J α", "M = J a"]}, "summary": [["转动定律", "law"]], "everyday": {"text": ["开门", "Opening a door"]}}


def _heads(path) -> list[str]:
    return [p.text.split("  ")[0] for p in docx.Document(str(path)).paragraphs if p.style.name.startswith("Heading")]


def test_templates_match_the_word_lesson_plan_and_lab_guide(tmp_path):
    """The web documents of the AI course workshop have the same sections and tables as the Word files it writes."""
    docs.plan(SPEC, GP, tmp_path / "p.docx", "3.1", "大学物理", "第三章", "张老师")
    plan = coursedoc.from_plan(SPEC, GP, "3.1", "大学物理", "第三章", "张老师")
    assert coursedoc.headings(plan) == _heads(tmp_path / "p.docx") == coursedoc.PLAN_HEADINGS
    assert [b["head"] for b in plan["blocks"] if b["t"] == "table"] == [t.rows[0].cells and [c.text for c in t.rows[0].cells]
                                                                          for t in docx.Document(str(tmp_path / "p.docx")).tables]
    docs.guide(SPEC, GP, tmp_path / "g.docx", "3.1")
    guide = coursedoc.from_guide(SPEC, GP, "3.1")
    assert coursedoc.headings(guide) == _heads(tmp_path / "g.docx") == [h[0] for h in coursedoc.GUIDE_HEADINGS]
    assert [b["head"] for b in guide["blocks"] if b["t"] == "table"] == [[c.text for c in t.rows[0].cells]
                                                                           for t in docx.Document(str(tmp_path / "g.docx")).tables]
    assert coursedoc.headings(coursedoc.template("guide")) == [h[0] for h in coursedoc.GUIDE_HEADINGS]
    # and they round-trip through Word and the page
    for d in (plan, guide, coursedoc.template("notice", "调课"), coursedoc.template("blank")):
        assert docx.Document(io.BytesIO(coursedoc.to_docx(d))).paragraphs
        assert coursedoc.to_html(d)
