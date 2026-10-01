"""问渠教材阅读（第 7 轮第 3 步）：signed-in users read the built sections; the chapter PDFs are for teachers."""
import json

from app import main
from tests.test_materials import login
from tests.test_studio import client  # noqa: F401 - the fixture


def student(client):
    r = client.post("/api/v1/auth/login", json={"username": "s", "password": "p"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


import pytest


@pytest.fixture(autouse=True)
def _restore_settings(client):  # noqa: F811 - after the app has started
    """These tests point the gateway at temporary folders and a fake animation service; put everything back after."""
    st = getattr(main.state, "settings", None)
    saved = {k: getattr(st, k) for k in ("textbook_dir", "data_dir", "animator_url")} if st else {}
    yield
    if st:
        for k, v in saved.items():
            setattr(st, k, v)


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


def test_animations_are_rendered_once_and_shown(client, tmp_path):
    """Textbook animations: the gateway renders each scene once with the animation service; the page shows the video."""
    import asyncio
    from app import textbook_api
    from app.production import anim

    built_book(tmp_path)
    web = tmp_path / "robotics" / "web"
    idx = json.loads((web / "index.json").read_text())
    idx["anims"] = {"a4_1_1": "abc123", "a4_1_2": "def456"}
    (web / "index.json").write_text(json.dumps(idx, ensure_ascii=False))
    (tmp_path / "robotics" / "anim").mkdir()
    for n in ("a4_1_1", "a4_1_2"):
        (tmp_path / "robotics" / "anim" / f"{n}.py").write_text("class Lesson(Base): pass")
    box = "<figure class='wq-anim'><div class='wq-media-box' data-anim='{}' data-hash='{}'>【动画 4.1.{}】说明</div></figure>"
    (web / "4.1.html").write_text("<section>" + box.format("a4_1_1", "abc123", 1) + box.format("a4_1_2", "def456", 2) + "</section>")
    (web / "4.1.mp.html").write_text((web / "4.1.html").read_text())
    main.state.settings.data_dir = str(tmp_path / "data")
    main.state.settings.animator_url = "http://animator.test"
    calls = []

    async def fake_render(url, code, timeout=600):
        calls.append(code)
        if len(calls) == 2:
            raise anim.RenderError("boom", "render")
        return b"MP4DATA", b"PNGDATA", 21.0, []

    real = anim.render
    anim.render = fake_render
    try:
        assert len(textbook_api.pending(main)) == 2
        made = asyncio.run(textbook_api.render_pending(main))
        assert made == 1 and len(calls) == 2
        assert textbook_api.pending(main) == []                  # the failure is not retried within a day
        for f in (tmp_path / "data" / "textbook-media" / "robotics").glob("*.err"):
            f.unlink()

        async def unreachable(url, code, timeout=600):
            raise anim.RenderError("renderer unreachable: ConnectError", "service")
        anim.render = unreachable
        assert asyncio.run(textbook_api.render_pending(main)) == 0
        assert len(textbook_api.pending(main)) == 1              # a service hiccup is retried on the next round
        anim.render = fake_render
        calls.clear()
        assert asyncio.run(textbook_api.render_pending(main)) == 1 and textbook_api.pending(main) == []
        for f in (tmp_path / "data" / "textbook-media" / "robotics").glob("a4_1_2-*"):
            f.unlink()                                           # back to: one ready, one not yet
    finally:
        anim.render = real
    hs = student(client)
    html = client.get("/api/v1/textbooks/robotics/sections/4.1", headers=hs).json()["html"]
    assert "<video" in html and "动画制作中" in html                # one ready, one still a box
    url = html.split("src='")[1].split("'")[0]
    r = client.get(url[url.index("/api/"):])
    assert r.status_code == 200 and r.content == b"MP4DATA" and r.headers["content-type"] == "video/mp4"
    mp = client.get("/api/v1/textbooks/robotics/sections/4.1?mp=true", headers=hs).json()["html"]
    assert "<video" not in mp and "请在网页端观看动画" in mp
    idx = client.get("/api/v1/textbooks/robotics", headers=hs).json()
    assert idx["anims_ready"] == 1 and idx["anims_total"] == 2 and "anims" not in idx


def test_virtual_labs_open_from_the_page(client, tmp_path):
    built_book(tmp_path)
    web = tmp_path / "robotics" / "web"
    box = "<figure class='wq-lab'><div class='wq-media-box wq-labbox' data-lab='4-1'>【实验 4.1】转动零件</div></figure>"
    (web / "4.1.html").write_text("<section>" + box + "</section>")
    (web / "4.1.mp.html").write_text("<section>" + box + "</section>")
    hs = student(client)
    assert "wq-labbox" in client.get("/api/v1/textbooks/robotics/sections/4.1", headers=hs).json()["html"]   # no lab page yet
    (tmp_path / "robotics" / "lab").mkdir()
    (tmp_path / "robotics" / "lab" / "ch04.html").write_text("<!doctype html><title>第4章 虚拟实验</title>")
    html = client.get("/api/v1/textbooks/robotics/sections/4.1", headers=hs).json()["html"]
    assert "wq-labbtn" in html and "#lab-4-1" in html and "打开【实验 4.1】" in html
    url = html.split("href='")[1].split("#")[0]
    r = client.get(url[url.index("/api/"):])
    assert r.status_code == 200 and "虚拟实验" in r.text and "default-src 'none'" in r.headers["content-security-policy"]
    mp = client.get("/api/v1/textbooks/robotics/sections/4.1?mp=true", headers=hs).json()["html"]
    assert "请在网页端打开虚拟实验" in mp
