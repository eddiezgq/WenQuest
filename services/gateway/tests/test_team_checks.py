"""Team rebuild R2/R3: technique examples instead of physics samples, the course design book, the copy check,
the relevance check, honest 需要你处理 instead of 审稿通过, and the per-lesson checklist."""
from io import BytesIO

from PIL import Image

from app import main, team
from app.production import anim, demo_anim, labs, similar
from tests.test_materials import login
from tests.test_studio import _write_first_lesson, client, settle  # noqa: F401 - the fixture

OWN_SCENE = r'''
from wq_anim import *


class Lesson(Base):
    def construct(self):
        self.title("1.1", "位姿描述：旋转矩阵", "Describing pose: rotation matrices")
        a = frame3([-3, -1, 0], rot_z(0), 1.4, name=r"\{A\}")
        t = ValueTracker(0)
        b = always_redraw(lambda: frame3([2, -1, 0], rot_z(t.get_value()), 1.4, name=r"\{B\}"))
        m = always_redraw(lambda: matrix_tex(rot_z(t.get_value())[:2, :2]).to_corner(UR))
        self.play(FadeIn(a), FadeIn(b), FadeIn(m))
        self.caption("坐标系 B 绕 z 轴转过 θ", "Frame B turns by θ about z")
        self.play(t.animate.set_value(60), run_time=3)
        self.card([["旋转矩阵的列是新坐标轴在旧坐标系中的方向", "Columns are the new axes seen in the old frame"]])
'''


def png() -> bytes:
    b = BytesIO()
    Image.new("RGB", (64, 36), "#0f1419").save(b, "PNG")
    return b.getvalue()


def test_the_copy_check_tells_copies_from_own_work():
    edited = demo_anim.AGV_2_1.replace("2.1", "3.1").replace("惯性", "位姿")
    assert "physics sample" in similar.problem(edited, {"the physics sample lesson 2.1": demo_anim.AGV_2_1})
    assert "placeholder" in similar.problem(demo_anim.TECHNIQUE, {})
    refs = {"the technique example": demo_anim.TECHNIQUE, "the physics sample": demo_anim.AGV_2_1}
    assert similar.problem(OWN_SCENE, refs) == ""
    lab_refs = {"the physics sample lab 2.1": labs.physics_example()}
    assert "physics sample" in similar.problem(labs.physics_example(), lab_refs)
    assert similar.problem(labs.physics_example(), {"the technique example": labs.example_code()}) == ""


def test_prompts_carry_technique_and_the_course_not_the_physics_sample():
    p = team.animation_prompt("1.1", "{}", demo_anim.TECHNIQUE, course="Course: 机器人学")
    assert "Course: 机器人学" in p and "placeholder" in p and "AGV" not in p
    lp = team.lab_prompt("1.1", "{}", labs.example_code(), course="Course: 机器人学")
    assert "never copy" in lp and "AGV" not in lp.replace(team.LAB_API, "")
    assert "api.arm(" in team.LAB_API and "planar_arm(" in team.ANIM_API
    assert "大学物理" not in team.STANDARD


def _setup_animation(monkeypatch, relevance_ok=True):
    sent: list[str] = []
    prompts: list[str] = []

    async def render(url, code, timeout=600.0):
        sent.append(code)
        return b"\x00\x00\x00\x18ftypmp42video", png(), 30.0, [png()]

    monkeypatch.setattr(anim, "render", render)
    monkeypatch.setattr(main.state.settings, "animator_url", "http://animator.test")
    studio = main._studio()
    studio.copy_check = True
    ai = main.state.ai
    orig = ai.json
    answers = iter([demo_anim.AGV_2_1, OWN_SCENE, OWN_SCENE])

    async def spy(**kw):
        sysp = kw.get("system", "")
        if "动画师" in sysp:
            prompts.append(kw["prompt"])
            return {"code": next(answers)}
        if "relevance check" in sysp:
            prompts.append("RELEVANCE:" + kw["prompt"])
            assert kw.get("images")  # the key frames are shown to the reviewer
            return {"on_topic": relevance_ok, "reason": "ok" if relevance_ok else "画面是物理课的 AGV", "fix": "画机械臂"}
        return await orig(**kw)
    monkeypatch.setattr(ai, "json", spy)
    return sent, prompts


def test_a_copied_physics_animation_is_sent_back(client, monkeypatch):
    sent, prompts = _setup_animation(monkeypatch)
    h = login(client)
    _, p = _write_first_lesson(client, h)
    les = p["outline"]["chapters"][0]["lessons"][0]
    assert not any("agv(" in c for c in sent)          # the copy never reached the renderer
    anim_prompts = [x for x in prompts if not x.startswith("RELEVANCE:")]
    assert "the same as the physics sample" in anim_prompts[1]
    assert not les.get("attention")
    item = next(c for c in les["checklist"] if c["key"] == "animation")
    assert item["ok"] is True and item["image_url"]
    assert client.get(item["image_url"]).status_code == 200
    msg = p["messages"][-1]["text"]
    assert "做好了" in msg and "需要你处理" not in msg
    assert "清单里这几项没打勾：教材对应章节已参照" in msg     # this test course has no textbook: said, not hidden


def test_an_off_topic_animation_ends_as_needs_you_and_can_be_redone(client, monkeypatch):
    sent, prompts = _setup_animation(monkeypatch, relevance_ok=False)
    h = login(client)
    pid, p = _write_first_lesson(client, h)
    les = p["outline"]["chapters"][0]["lessons"][0]
    anim_prompts = [x for x in prompts if not x.startswith("RELEVANCE:")]
    assert "off topic" in anim_prompts[-1]
    assert [x["kind"] for x in les["attention"]] == ["animation"] and "不切题" in les["attention"][0]["text"]
    assert "需要你处理" in p["messages"][-1]["text"]
    assert "agv(" not in sent[-1]                        # the plain version draws no stock robot
    # 重做动画
    r = client.post(f"/api/v1/studio/projects/{pid}/lessons/{les['id']}/animation", headers=h)
    assert r.status_code == 200


def test_a_copied_lab_never_runs_and_needs_you(client, monkeypatch):
    runs = []

    async def trial_run(url, page_html, lab, timeout=150.0):
        runs.append(lab)
        return {"ok": True, "problems": [], "tasks": {}, "screenshot": png(), "seconds": 3.0}

    monkeypatch.setattr(labs, "trial_run", trial_run)
    monkeypatch.setattr(main.state.settings, "labcheck_url", "http://labcheck.test")
    main._studio().copy_check = True
    ai = main.state.ai
    orig = ai.json

    async def spy(**kw):
        if "实验师" in kw.get("system", ""):
            return {"code": labs.physics_example()}
        return await orig(**kw)
    monkeypatch.setattr(ai, "json", spy)
    h = login(client)
    _, p = _write_first_lesson(client, h)
    les = p["outline"]["chapters"][0]["lessons"][0]
    assert runs == [] and "lab" not in [f["kind"] for f in les["files"]]
    assert [x["kind"] for x in les["attention"]] == ["lab"]
    assert "the same as the physics sample lab 2.1" in les["attention"][0]["text"]
    assert next(c for c in les["checklist"] if c["key"] == "lab")["ok"] is False


def test_design_book_is_shown_and_the_teachers_edit_is_kept(client):
    h = login(client)
    pid, p = _write_first_lesson(client, h)
    book = p["design_book"]
    assert book["platform"] and len(book["chapters"]) == len(p["outline"]["chapters"])
    r = client.put(f"/api/v1/studio/projects/{pid}/design-book", headers=h,
                   json={"platform": "UR5 六轴机械臂 + TurtleBot 移动机器人", "avoid": ["不要物理课的 AGV"]})
    assert r.status_code == 200
    b = r.json()["design_book"]
    assert b["by"] == "teacher" and b["platform"].startswith("UR5") and b["avoid"] == ["不要物理课的 AGV"]
    studio = main._studio()
    proj = studio.projects.load(pid)
    assert "UR5" in studio.course_brief(proj) and "不要物理课的 AGV" in studio.course_brief(proj)


def test_every_lesson_has_a_checklist(client):
    h = login(client)
    _, p = _write_first_lesson(client, h)
    les = p["outline"]["chapters"][0]["lessons"][0]
    keys = [c["key"] for c in les["checklist"]]
    assert keys[:2] == ["textbook", "problem"] and keys[-2:] == ["numbers", "bilingual"]
    assert all(c["by"] in ("ai", "auto+ai") for c in les["checklist"])


def test_older_projects_can_get_a_design_book_and_reread_the_textbook(client):
    h = login(client)
    pid, p = _write_first_lesson(client, h)
    studio = main._studio()
    proj = studio.projects.load(pid)
    proj.pop("design_book")          # planned before the design book existed
    studio.projects.save(proj)
    r = client.post(f"/api/v1/studio/projects/{pid}/design-book", headers=h)
    assert r.status_code == 200
    p = settle(client, h, pid)
    assert p["design_book"]["platform"] and "设计书" in p["messages"][-1]["text"]
    r = client.post(f"/api/v1/studio/projects/{pid}/textbook/reread", headers=h)
    if p["materials"].get("textbook"):
        assert r.status_code == 200
        p = settle(client, h, pid)
        assert "目录" in p["messages"][-1]["text"]
    else:
        assert r.status_code == 409
