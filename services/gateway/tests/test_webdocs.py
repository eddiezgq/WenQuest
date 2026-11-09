"""网页实验报告（第 122 轮）：存草稿、只收学生能改的部分、交进关联作业、退回后新版本、导出 Word / PDF、全班导出。"""
import base64
import io
import json
import zipfile

import docx
import httpx
import pytest
from fastapi.testclient import TestClient

from app import main, webdocs_api
from app.ai import ModelGateway
from app.moodle import MoodleClient
from app.production import webdoc
from tests import test_learn_api as L
from tests.test_materials import BASE, login

def _png() -> str:
    from PIL import Image
    b = io.BytesIO()
    Image.new("RGB", (40, 30), "white").save(b, "PNG")
    return base64.b64encode(b.getvalue()).decode()


PNG = _png()
TPL = {"v": 1, "kind": "labreport", "lab": "1.5", "title": ["长度测量", "Measuring length"], "where": ["《大学物理》1.5 节", ""],
       "gpu": False, "blocks": [
           {"t": "title", "zh": "实验报告  长度测量", "en": "Lab Report  Measuring length"},
           {"t": "fields", "id": "info", "items": [{"k": "name", "label": "姓名 Name", "v": ""}, {"k": "sid", "label": "学号 ID", "v": ""},
                                                   {"k": "date", "label": "日期 Date", "v": ""},
                                                   {"k": "score", "label": "成绩 Score", "v": "", "fixed": True}]},
           {"t": "h", "zh": "一、实验目的", "en": "1  Objectives"},
           {"t": "text", "id": "s1", "lines": 3, "v": ""},
           {"t": "h", "zh": "四、数据记录与处理", "en": "4  Data and processing"},
           {"t": "table", "id": "t1", "title": ["表 1  外径", "Table 1"], "head": ["位置", "1", "2"], "head_en": ["Place", "1", "2"],
            "rows": [["D / mm", "", "{{D1}}"]]},
           {"t": "table", "id": "records", "records": True, "grow": True, "title": ["实验记录", "Lab records"],
            "head": ["时间", "场景", "参数", "读数"], "head_en": ["Time", "Scene", "Parameters", "Readings"], "rows": []},
           {"t": "text", "id": "process", "lines": 4, "v": ""},
           {"t": "h", "zh": "九、AI 使用声明", "en": "9  AI use statement"},
           {"t": "check", "id": "ai", "v": [], "other": "", "options": [["未使用 AI", "No AI used"], ["用 AI 解释概念", "AI to explain"]]},
           {"t": "rubric", "head": ["项目", "分值", "要求"], "rows": [["原理", "20", "公式正确"]]}]}


def handler(request: httpx.Request) -> httpx.Response:
    u = str(request.url)
    if u.startswith("http://docs/converter"):
        body = json.loads(request.content)
        assert body["token"].count(".") == 2 and body["url"].startswith("http://gateway:8000/api/v1/webdocs-tmp/")
        HIT["converter"] = body
        return httpx.Response(200, json={"endConvert": True, "percent": 100, "fileUrl": "https://learn.example.com/docs/cache/x.pdf"})
    if u.startswith("http://docs/cache/x.pdf"):
        return httpx.Response(200, content=b"%PDF-1.7 report")
    if "mod_assign_list_participants" in u:
        return httpx.Response(200, json=[{"id": 6, "fullname": "学生甲"}, {"id": 9, "fullname": "学生乙"}])
    return L.moodle(request)


HIT: dict = {}


@pytest.fixture
def client(tmp_path):
    (tmp_path / "books" / "physics" / "lab").mkdir(parents=True)
    (tmp_path / "books" / "physics" / "web").mkdir(parents=True)
    (tmp_path / "books" / "physics" / "web" / "index.json").write_text('{"title": "大学物理", "chapters": []}', encoding="utf-8")
    (tmp_path / "books" / "physics" / "lab" / "lab1_5-report.json").write_text(json.dumps(TPL, ensure_ascii=False), encoding="utf-8")
    (tmp_path / "books" / "physics" / "lab" / "ch01.html").write_text("<html></html>", encoding="utf-8")
    with TestClient(main.app) as c:
        s = main.state.settings
        old = (s.textbook_dir, s.docs_url, s.docs_jwt_secret)
        s.textbook_dir, s.docs_url, s.docs_jwt_secret = str(tmp_path / "books"), "http://docs", "k"
        main.state.webdocs = webdocs_api.Store(str(tmp_path / "data"))
        main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        main.state.moodle = MoodleClient(BASE, "moodle_mobile_app", main.state.http)
        main.state.ai = ModelGateway("fake", main.state.http)
        L.CALLS.clear()
        L.STATE.update(status="new", drafts=1)
        HIT.clear()
        yield c
        s.textbook_dir, s.docs_url, s.docs_jwt_secret = old
        main.state.webdocs = None


def written(doc: dict) -> dict:
    for b in doc["blocks"]:
        if b.get("id") == "s1":
            b["v"] = "测量转接盘的外径和厚度，学会游标卡尺和螺旋测微器的读数方法。"
        if b.get("id") == "t1":
            b["rows"] = [["改掉表头", "50.02", "50.04"]]
        if b.get("id") == "records":
            b["rows"] = [["10:01", "游标卡尺", "", "50.02 mm"]]
        if b.get("t") == "rubric":
            b["rows"] = [["原理", "100", "改分值"]]
        if b.get("id") == "ai":
            b["v"] = [0, 7]
    doc["blocks"].append({"t": "figure", "id": "fig1", "png": PNG, "caption": "图 1  D 的测量值", "src": {"table": "t1"}})
    return doc


def test_merge_keeps_the_template_and_takes_only_answers():
    d = webdoc.merge(TPL, written(json.loads(json.dumps(TPL))))
    t1 = next(b for b in d["blocks"] if b.get("id") == "t1")
    assert t1["rows"] == [["D / mm", "50.02", "50.04"]]                 # the fixed cell stays, the two blanks are filled
    assert next(b for b in d["blocks"] if b["t"] == "rubric")["rows"][0][1] == "20"
    assert next(b for b in d["blocks"] if b.get("id") == "ai")["v"] == [0]
    figs = [b for b in d["blocks"] if b["t"] == "figure"]
    ids = [b.get("id") for b in d["blocks"]]
    assert len(figs) == 1 and ids.index("fig1") == ids.index("process") + 1
    with pytest.raises(webdoc.DocError):
        webdoc.merge(TPL, {"blocks": [{"t": "figure", "png": "bm90IGEgcG5n"}]})
    with pytest.raises(webdoc.DocError):
        webdoc.merge(TPL, {"blocks": [{"t": "figure", "png": base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\0" * 40).decode()}]})
    assert webdoc.placeholders(TPL) == {"D1": ("t1", 0, 2)}
    assert next(b for b in webdoc.blank(TPL)["blocks"] if b.get("id") == "t1")["rows"] == [["D / mm", "", ""]]


def test_write_save_submit_reopen_and_export(client):
    s = login(client, "s")
    r = client.get("/api/v1/reports/physics/1_5", headers=s).json()
    assert r["status"] == "new" and r["assignments"] == [] and r["slots"] == {"D1": ["t1", 0, 2]} and r["pdf"]
    assert "#lab-1-5-zh" in r["lab_url"]
    assert r["editable"]["t1"] == [[False, True, True]] and r["editable"]["records"] == []
    assert next(b for b in r["doc"]["blocks"] if b["t"] == "fields")["items"][0]["v"] == "T"      # name filled in
    # a teacher links assignment 50 to this lab; a student may not
    t = login(client, "t")
    assert client.put("/api/v1/assignments/50/lab-link", headers=s, json={"book": "physics", "lab": "1_5"}).status_code == 403
    assert client.put("/api/v1/assignments/50/lab-link", headers=t, json={"book": "physics", "lab": "9_9"}).status_code == 404
    assert client.put("/api/v1/assignments/50/lab-link", headers=t, json={"book": "physics", "lab": "1_5"}).json()["linked"]
    # nothing to hand in yet
    assert client.post("/api/v1/reports/physics/1_5/submit", headers=s, json={"cmid": 50}).json()["error"] == "report_empty"
    doc = written(r["doc"])
    saved = client.put("/api/v1/reports/physics/1_5", headers=s, json={"doc": doc, "base": 0}).json()
    assert saved["status"] == "draft"
    assert client.put("/api/v1/reports/physics/1_5", headers=s, json={"doc": doc, "base": 1}).json()["error"] == "report_changed"
    r = client.get("/api/v1/reports/physics/1_5", headers=s).json()
    assert r["status"] == "draft" and r["assignments"][0]["cmid"] == 50
    assert next(b for b in r["doc"]["blocks"] if b["t"] == "rubric")["rows"][0][1] == "20"
    # hand in: the Word file and the text go to Moodle, then "submit for grading"
    L.CALLS.clear()
    out = client.post("/api/v1/reports/physics/1_5/submit", headers=s, json={"cmid": 50}).json()
    assert out["status"] == "submitted" and out["version"] == 1
    sent = dict(L.CALLS)["mod_assign_save_submission"]
    assert sent["plugindata[files_filemanager]"] and "50.02" in sent["plugindata[onlinetext_editor][text]"]
    assert "mod_assign_submit_for_grading" in dict(L.CALLS)
    up = L.__dict__.get("UPLOADS") or __import__("tests.test_materials", fromlist=["UPLOADS"]).UPLOADS
    assert up and b"PK" in up[-1]                       # a .docx went into the draft area
    # handed in: read-only
    assert client.put("/api/v1/reports/physics/1_5", headers=s, json={"doc": doc}).json()["error"] == "report_submitted"
    # the teacher sees it, and can export the class
    tv = client.get("/api/v1/assignments/50/reports/6", headers=t).json()
    assert tv["ver"] == 1 and any(b.get("id") == "fig1" for b in tv["doc"]["blocks"])
    z = client.get("/api/v1/assignments/50/reports.zip", headers=t)
    assert z.status_code == 200 and zipfile.ZipFile(io.BytesIO(z.content)).namelist() == ["学生甲-实验1.5-长度测量-实验报告.docx"]
    zp = client.get("/api/v1/assignments/50/reports.zip?fmt=pdf", headers=t)
    assert zipfile.ZipFile(io.BytesIO(zp.content)).read("学生甲-实验1.5-长度测量-实验报告.pdf").startswith(b"%PDF")
    assert client.get("/api/v1/assignments/50/reports/6", headers=s).status_code == 403
    # the teacher reopens it: back to draft, a new version on the next hand-in, the old one kept
    L.STATE["status"] = "reopened"
    r = client.get("/api/v1/reports/physics/1_5", headers=s).json()
    assert r["status"] == "draft" and [v["ver"] for v in r["versions"]] == [1]
    client.put("/api/v1/reports/physics/1_5", headers=s, json={"doc": r["doc"], "base": r["updated"]})
    assert client.post("/api/v1/reports/physics/1_5/submit", headers=s, json={"cmid": 50}).json()["version"] == 2
    assert client.get("/api/v1/reports/physics/1_5/versions/1", headers=s).json()["ver"] == 1
    tv = client.get("/api/v1/assignments/50/reports/6", headers=t).json()
    assert tv["ver"] == 2 and [v["ver"] for v in tv["versions"]] == [1, 2]
    assert client.get("/api/v1/assignments/50/reports/6?ver=1", headers=t).json()["ver"] == 1
    # export: Word in the course layout, PDF through the online documents service
    w = client.get("/api/v1/reports/physics/1_5/export?fmt=docx", headers=s)
    text = "\n".join(p.text for p in docx.Document(io.BytesIO(w.content)).paragraphs)
    assert "测量转接盘的外径" in text and "☑ 未使用 AI" in text and len(docx.Document(io.BytesIO(w.content)).inline_shapes) == 1
    p = client.get("/api/v1/reports/physics/1_5/export?fmt=pdf", headers=s)
    assert p.content.startswith(b"%PDF") and HIT["converter"]["outputtype"] == "pdf"


def test_only_linked_assignments_take_the_report(client):
    s = login(client, "s")
    client.put("/api/v1/reports/physics/1_5", headers=s, json={"doc": written(json.loads(json.dumps(TPL)))})
    assert client.post("/api/v1/reports/physics/1_5/submit", headers=s, json={"cmid": 50}).json()["error"] == "not_linked"
    assert client.get("/api/v1/reports/physics/2_1", headers=s).status_code == 404
    labs = client.get("/api/v1/report-labs", headers=s).json()["books"]
    assert labs == [{"book": "physics", "title": "大学物理", "labs": [{"lab": "1_5", "no": "1.5", "title": ["长度测量", "Measuring length"]}]}]


def test_jwt_is_hs256():
    tok = webdocs_api.jwt_hs256({"a": 1}, "k")
    head, body, sig = tok.split(".")
    assert json.loads(base64.urlsafe_b64decode(head + "==")) == {"alg": "HS256", "typ": "JWT"}
    assert json.loads(base64.urlsafe_b64decode(body + "==")) == {"a": 1}
