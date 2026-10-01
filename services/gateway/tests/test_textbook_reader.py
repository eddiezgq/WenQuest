"""问渠教材阅读（第 7 轮第 3 步）：signed-in users read the built sections; the chapter PDFs are for teachers."""
import json

from app import main
from tests.test_materials import login
from tests.test_studio import client  # noqa: F401 - the fixture


def student(client):
    r = client.post("/api/v1/auth/login", json={"username": "s", "password": "p"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


def built_book(tmp_path):
    web = tmp_path / "robotics" / "web"
    web.mkdir(parents=True)
    idx = {"book": "robotics", "title": "机器人学", "parts": [], "pdf": [4],
           "chapters": [{"no": 4, "title": "刚体的转动", "level": "基础", "part": "第一篇",
                         "sections": [{"id": "4.1", "title": "平面转动与旋转矩阵", "written": True},
                                      {"id": "4.2", "title": "空间转动", "written": True},
                                      {"id": "4.3", "title": "欧拉转动定理", "written": False}]}]}
    (web / "index.json").write_text(json.dumps(idx, ensure_ascii=False))
    (web / "4.1.html").write_text("<section><svg>式</svg>4.1 正文</section>")
    (web / "4.1.mp.html").write_text("<section><img src='data:image/svg+xml;base64,AA'/>4.1 正文</section>")
    (web / "4.2.html").write_text("<section>4.2 正文</section>")
    (tmp_path / "robotics" / "ch04.pdf").write_bytes(b"%PDF-1.4 test")
    main.state.settings.textbook_dir = str(tmp_path)


def test_reading_and_pdf_rules(client, tmp_path):
    built_book(tmp_path)
    assert client.get("/api/v1/textbooks").status_code == 401                      # signed in only
    h, hs = login(client), student(client)
    books = client.get("/api/v1/textbooks", headers=hs).json()["books"]
    assert books == [{"book": "robotics", "title": "机器人学", "chapters": 1, "sections": 3, "written": 2}]
    idx = client.get("/api/v1/textbooks/robotics", headers=hs).json()
    assert not idx["teacher"] and idx["pdf"] == []
    s = client.get("/api/v1/textbooks/robotics/sections/4.1", headers=hs).json()
    assert "<svg>" in s["html"] and s["prev"] is None and s["next"]["id"] == "4.2" and s["chapter"]["no"] == 4
    assert "<img" in client.get("/api/v1/textbooks/robotics/sections/4.1?mp=true", headers=hs).json()["html"]
    assert client.get("/api/v1/textbooks/robotics/sections/4.2?mp=true", headers=hs).json()["html"] == "<section>4.2 正文</section>"
    assert client.get("/api/v1/textbooks/robotics/sections/4.3", headers=hs).status_code == 404   # not written yet
    assert client.get("/api/v1/textbooks/robotics/sections/..%2Fx", headers=hs).status_code == 404
    assert client.get("/api/v1/textbooks/Nope", headers=hs).status_code == 404
    # the PDF: teachers only, through a short-lived link
    assert client.get("/api/v1/textbooks/robotics/pdf/4", headers=hs).status_code == 403
    assert client.get("/api/v1/textbooks/robotics", headers=h).json()["pdf"] == [4]
    url = client.get("/api/v1/textbooks/robotics/pdf/4", headers=h).json()["url"]
    r = client.get(url[url.index("/api/"):])
    assert r.status_code == 200 and r.content.startswith(b"%PDF") and "attachment" in r.headers["content-disposition"]
    assert client.get("/api/v1/textbook-pdf/garbage").status_code == 410
