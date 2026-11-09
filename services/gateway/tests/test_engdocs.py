"""第 128 轮（阶段 C1）：缝纫机计算书、调机卡“存为网页文档”——数字和 Word 导出一致、计算的块改不了、自己加的块随便改、
设计改了提示重新生成（自己加的保留）、导出 Word / PDF、别的单位看不到；数字工厂工艺卡转 PDF 的内部接口只认钥匙。"""
import io

import docx
import httpx
import pytest

from app import coursedocs_api, engdocs_api, main
from app.moodle import MoodleClient
from tests.test_course_pack import client  # noqa: F401
from tests.test_materials import login
from tests.test_sewing_api import UID
from tests.test_sewing_api import moodle as sew_moodle


def handler(request: httpx.Request) -> httpx.Response:
    u = str(request.url)
    if u.startswith("http://docs/converter"):
        return httpx.Response(200, json={"endConvert": True, "fileUrl": "http://docs/cache/z.pdf"})
    if u.startswith("http://docs/cache/z.pdf"):
        return httpx.Response(200, content=b"%PDF-1.7 eng")
    return sew_moodle(request)


@pytest.fixture
def ec(client, tmp_path):  # noqa: F811
    s = main.state.settings
    old = (s.docs_url, s.docs_jwt_secret, s.factory_read_key)
    s.docs_url, s.docs_jwt_secret, s.factory_read_key = "http://docs", "k", "read-key"
    main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    main.state.moodle = MoodleClient("http://moodle.test", "moodle_mobile_app", main.state.http)
    main.state.engdocs = engdocs_api.EStore(str(tmp_path / "e"))
    main.state.coursedocs = coursedocs_api.Store(str(tmp_path / "e"))
    yield client
    s.docs_url, s.docs_jwt_secret, s.factory_read_key = old
    main.state.engdocs = main.state.coursedocs = None


def _licensed(c):
    admin, user = login(c), login(c, "s")
    UID["s"] = c.get("/api/v1/me", headers=user).json()["id"]
    assert c.post("/api/v1/admin/sewing/licenses", json={"username": "s", "org": "甲缝纫机厂"}, headers=admin).json()["ok"]
    return admin, user


def _words(data: bytes) -> str:
    d = docx.Document(io.BytesIO(data))
    return "\n".join([p.text for p in d.paragraphs] + [c.text for t in d.tables for r in t.rows for c in r.cells])


def test_calc_report_and_card_as_web_documents(ec):
    c = ec
    assert c.post("/api/v1/sewing/webdocs", json={"kind": "report"}, headers=login(c, "s")).status_code == 403   # not activated
    admin, user = _licensed(c)
    pid = c.post("/api/v1/sewing/projects", json={"name": "GC-6150", "params": {"n": 5000}}, headers=user).json()["id"]
    r = c.post("/api/v1/sewing/webdocs", json={"kind": "report", "params": {"n": 5000}, "pid": pid, "project": "GC-6150"}, headers=user).json()
    did, doc = r["id"], r["doc"]
    n_locked = len(doc["blocks"])
    assert not r["stale"] and all(b.get("lock") for b in doc["blocks"])
    kinds = {b["t"] for b in doc["blocks"]}
    assert {"h", "table"} <= kinds and "image" in kinds          # headings, the result tables and the curves
    # the same numbers as the Word export
    word = c.post("/api/v1/sewing/export/report", json={"params": {"n": 5000}, "project": "GC-6150"}, headers=user).content
    cells = [x for b in doc["blocks"] if b["t"] == "table" for row in [b["head"]] + b["rows"] for x in row if x]
    text = _words(word)
    assert cells and all(x in text for x in cells[:80])
    # the engineer edits a number (refused), adds a note and a picture-free table, moves a computed heading
    t0 = next(i for i, b in enumerate(doc["blocks"]) if b["t"] == "table")
    orig = doc["blocks"][t0]["rows"][0][:]
    doc["blocks"][t0]["rows"][0][-1] = "999999"
    doc["blocks"].insert(1, {"t": "para", "text": "现场说明：样机按 5000 r/min 试缝。", "en": ""})
    doc["blocks"].append({"t": "callout", "text": "下次改型前复核挑线弹簧。"})
    doc["blocks"].append({"t": "para", "text": "假装计算", "lock": True})       # cannot invent computed blocks
    up = c.put(f"/api/v1/engdocs/{did}", json={"doc": doc, "base": r["updated"]}, headers=user).json()
    cur = c.get(f"/api/v1/engdocs/{did}", headers=user).json()
    assert cur["updated"] == up["updated"]
    blocks = cur["doc"]["blocks"]
    assert blocks[1]["text"].startswith("现场说明") and blocks[-1]["t"] == "callout"
    assert next(b for b in blocks if b["t"] == "table")["rows"][0] == orig            # the number came back
    assert not any(b.get("text") == "假装计算" for b in blocks)
    assert sum(1 for b in blocks if b.get("lock")) == n_locked
    assert c.put(f"/api/v1/engdocs/{did}", json={"doc": doc, "base": 1}, headers=user).json()["error"] == "doc_changed"
    # a photo of the trial sewing
    from tests.test_coursedocs import _png
    img = c.post(f"/api/v1/engdocs/{did}/images", json={"data": _png()}, headers=user).json()["img"]
    assert c.get(f"/api/v1/webdoc-img/{img}").status_code == 200
    # export
    w = c.get(f"/api/v1/engdocs/{did}/export?fmt=docx", headers=user)
    assert w.status_code == 200 and "现场说明" in _words(w.content) and docx.Document(io.BytesIO(w.content)).inline_shapes
    assert c.get(f"/api/v1/engdocs/{did}/export?fmt=pdf", headers=user).content.startswith(b"%PDF")
    # the design changes: stale; regenerate keeps the engineer's blocks
    c.put(f"/api/v1/sewing/projects/{pid}", json={"name": "GC-6150", "params": {"n": 5500}}, headers=user)
    assert c.get(f"/api/v1/engdocs/{did}", headers=user).json()["stale"]
    g = c.post(f"/api/v1/engdocs/{did}/regenerate", headers=user).json()
    assert not g["stale"] and any(b.get("text", "").startswith("现场说明") for b in g["doc"]["blocks"])
    assert g["doc"]["blocks"][-1]["t"] == "callout"
    # the adjustment card; the list; other companies see nothing
    card = c.post("/api/v1/sewing/webdocs", json={"kind": "card", "params": {}}, headers=user).json()
    assert any(b["t"] == "table" and "确认" in "".join(b["head"]) for b in card["doc"]["blocks"])
    assert {d["kind"] for d in c.get("/api/v1/sewing/webdocs", headers=user).json()["docs"]} == {"report", "card"}
    assert c.get(f"/api/v1/engdocs/{did}", headers=admin).status_code == 404             # the admin's company is 问渠
    assert c.delete(f"/api/v1/engdocs/{card['id']}", headers=user).json()["ok"]


def test_internal_pdf_for_the_factory_hub(ec):
    c = ec
    d = docx.Document()
    d.add_paragraph("机械加工工艺过程卡片")
    b = io.BytesIO()
    d.save(b)
    assert c.post("/api/v1/internal/docx-to-pdf", content=b.getvalue()).status_code == 403
    assert c.post("/api/v1/internal/docx-to-pdf", content=b.getvalue(), headers={"Authorization": "Bearer nope"}).status_code == 403
    assert c.post("/api/v1/internal/docx-to-pdf", content=b"not a docx", headers={"Authorization": "Bearer read-key"}).status_code == 400
    r = c.post("/api/v1/internal/docx-to-pdf", content=b.getvalue(), headers={"Authorization": "Bearer read-key"})
    assert r.status_code == 200 and r.content.startswith(b"%PDF")
