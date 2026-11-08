"""体验课（第 117 轮）：每本已部署的教材在课程包页上自动多一个“体验课”，和现成课程包一起“全部发布”。"""
import json
from urllib.parse import parse_qs

from app import bookcourse
from tests.test_course_pack import (  # noqa: F401  (the fixture)
    CALLS,
    client,
    login,
    pack,
    wait,
)


def book(root, name="robotics", slides=("1",)):
    d = root / name
    (d / "web").mkdir(parents=True)
    (d / "slides").mkdir()
    for ch in slides:
        (d / "slides" / f"ch{int(ch):02d}.html").write_text("<html></html>")
    idx = {"book": name, "title": "机器人学", "title_en": "Robotics",
           "chapters": [
               {"no": 1, "title": "绪论", "title_en": "Introduction",
                "sections": [{"id": "1.1", "title": "引子", "written": True}, {"id": "1.2", "title": "历史", "written": False}]},
               {"no": 2, "title": "运动学", "title_en": "Kinematics",
                "sections": [{"id": "2.1", "title": "位姿", "written": False}]},
               {"no": 3, "title": "空章", "sections": []}],
           "resources": {"1": [{"kind": "lab", "num": "1.1", "title": "小车避障", "title_en": "Cart", "sec": "1.1"},
                               {"kind": "anim", "num": "1.1.1", "title": "动画", "sec": "1.1"}]}}
    (d / "web" / "index.json").write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")


def test_manifest_from_a_built_book(tmp_path):
    book(tmp_path)
    man = bookcourse.make(tmp_path, "robotics", "https://learn.example.cn")
    assert man["course"]["fullname"] == ["《机器人学》· 体验课", "Robotics · Trial course"]
    assert [x["no"] for x in man["lessons"]] == [1, 2] and [x["section"] for x in man["lessons"]] == [2, 3]  # 空章不建
    ch1, ch2 = man["lessons"]
    assert [a["type"] for a in ch1["activities"]] == ["page", "url", "url", "url"]       # 导读、教材、课件、一个实验
    assert ch1["activities"][1]["url"] == "https://learn.example.cn/pages/textbook/textbook?book=robotics&s=1.1"
    assert ch1["activities"][2]["url"].endswith("book=robotics&slides=1")
    assert "（编写中）" in ch1["activities"][0]["content"][0] and not ch1["placeholder"]
    assert ch2["placeholder"] and len(ch2["activities"]) == 2                              # 没写完的章：先当大纲
    assert man["exams"] == [] and man["batches"][0]["lessons"] == [1, 2]
    assert bookcourse.make(tmp_path, "nobook", "x") is None


def test_publish_all_packs_and_trial_courses(client, tmp_path):  # noqa: F811
    pack(tmp_path)                               # 现成课程包 sewing（两批）
    book(tmp_path / "textbook")                  # 教材 robotics
    h = login(client)
    names = [p["book"] for p in client.get("/api/v1/admin/course-packs", headers=h).json()["packs"]]
    assert names == ["sewing", "robotics"]
    assert client.post("/api/v1/admin/course-packs/publish-all", headers=login(client, "s")).status_code == 403
    r = client.post("/api/v1/admin/course-packs/publish-all", headers=h)
    assert r.json() == {"books": ["sewing", "robotics"]}
    import time
    end = time.time() + 10
    while time.time() < end:
        ps = client.get("/api/v1/admin/course-packs", headers=h).json()["packs"]
        if all(p["status"] == "done" for p in ps):
            break
        time.sleep(0.05)
    assert all(p["status"] == "done" for p in ps) and all(b["done"] for p in ps for b in p["batches"])
    made = [parse_qs(b) for f, b in CALLS if f == "local_wenquest_create_course"]
    assert len(made) == 2 and made[1]["shortname"] == ["WQT-ROBOTICS"]
    urls = [v[0] for f, b in CALLS if f == "local_wenquest_add_activities" for k, v in parse_qs(b).items() if k.endswith("[url]")]
    assert any("slides=1" in u for u in urls)
    # 再按一次：什么都不重复
    CALLS.clear()
    client.post("/api/v1/admin/course-packs/publish-all", headers=h)
    time.sleep(0.5)
    assert [f for f, _ in CALLS if f != "core_course_get_contents"] == []
