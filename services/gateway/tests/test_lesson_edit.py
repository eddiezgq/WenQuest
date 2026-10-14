"""Round 32 (D2 + D3): the course lead changes one part of a written lesson, or redoes one deliverable, and can undo it."""
import asyncio
import json

from app import main
from tests.test_lead import to_outline
from tests.test_materials import login
from tests.test_studio import client, moodle  # noqa: F401 - the fixture


def written_lesson(client):
    h = login(client)
    pid, p = to_outline(client, h)
    st = main._studio()
    proj = st.projects.load(pid)
    lid = proj["outline"]["chapters"][0]["lessons"][0]["id"]

    async def go():
        st.run(proj, "写", lambda pr: st.run_step(pr, {"type": "write_lesson", "lesson_id": lid}))
        await st.tasks[pid]
    asyncio.run(go())
    proj = st.projects.load(pid)
    assert st.find_lesson(proj, lid)[1]["status"] == "awaiting"
    return h, pid, lid, st


def spec_of(st, pid, lid):
    proj = st.projects.load(pid)
    _, les = st.find_lesson(proj, lid)
    return json.loads((st.lesson_dir(proj, les) / "spec.json").read_text())["lesson"], les


def test_one_part_of_a_lesson_is_changed_and_can_be_undone(client):
    h, pid, lid, st = written_lesson(client)
    before, les0 = spec_of(st, pid, lid)
    redone = []
    orig_video, orig_lab = st.make_video, st.make_lab

    async def video(*a, **k):
        redone.append("animation")
        return await orig_video(*a, **k)

    async def lab(*a, **k):
        redone.append("lab")
        return await orig_lab(*a, **k)
    st.make_video, st.make_lab = video, lab
    new_problem = {"title": ["移动机器人巡检", "Mobile robot patrol"], "text": ["差速移动机器人在车间巡检。", "A diff-drive robot patrols."],
                   "given": [["速度 0.5 m/s", "speed 0.5 m/s"], ["距离 30 m", "distance 30 m"]], "answer": ["60 s", "60 s"]}
    step = {"type": "rework_lesson", "lesson_id": lid, "summary": "换机器人问题", "set": {"problem": new_problem}}
    proj = st.projects.load(pid)
    assert st.step_ok(proj, step)

    async def go(s):
        st.run(st.projects.load(pid), "改", lambda pr: st.run_step(pr, s))
        await st.tasks[pid]
    asyncio.run(go(step))
    after, les = spec_of(st, pid, lid)
    assert after["problem"]["title"] == ["移动机器人巡检", "Mobile robot patrol"]
    assert after["notes"] == before["notes"] and after["animation"] == before["animation"]   # the rest stays
    assert redone == []                                                                      # nothing else made again
    assert les["status"] == "awaiting" and les["edits"] and "机器人问题" in les["edits"][-1]["what"]
    assert "移动机器人巡检" in json.dumps(les["content"], ensure_ascii=False)                    # the page shows it
    # a changed lab part redoes the lab, and only that
    step2 = {"type": "rework_lesson", "lesson_id": lid, "summary": "实验加一个任务",
             "set": {"lab": {**after["lab"], "tasks": after["lab"]["tasks"] + [["再测一次", "Measure again"]]}}}
    asyncio.run(go(step2))
    assert redone == ["lab"]
    # undo twice: back to the lesson as it was written
    p = client.post(f"/api/v1/studio/projects/{pid}/undo", headers=h).json()
    p = client.post(f"/api/v1/studio/projects/{pid}/undo", headers=h).json()
    back, les = spec_of(st, pid, lid)
    assert back["problem"] == before["problem"] and not les.get("edits")


def test_the_lead_can_call_edit_lesson_and_redo_a_deliverable(client):
    h, pid, lid, st = written_lesson(client)
    proj = st.projects.load(pid)
    made = []

    async def go():
        out = await st.agent_tool(proj, "edit_lesson", {"lesson_id": lid, "summary": "重出练习", "redo": ["exercises"],
                                                         "note": "加一道计算题"}, made)
        st.projects.save(proj)
        await st.tasks[pid]
        return out
    out = asyncio.run(go())
    assert out.startswith("started") and not made                   # one lesson, small mode: done at once
    _, les = spec_of(st, pid, lid)
    assert les.get("edits"), st.projects.load(pid)["messages"][-3:]
    assert "练习与答案" in les["edits"][-1]["what"]
    # a lesson that is not written cannot be reworked; a published one neither (round 32 step 3 brings new versions)
    other = proj["outline"]["chapters"][0]["lessons"][1]["id"]
    assert not st.step_ok(st.projects.load(pid), {"type": "rework_lesson", "lesson_id": other, "redo": ["lab"]})


def test_writing_several_lessons_keeps_every_lesson_written(client):
    """10-13: write_lessons worked on a second copy of the project, which the job runner's last save overwrote."""
    h = login(client)
    pid, p = to_outline(client, h)
    st = main._studio()
    proj = st.projects.load(pid)
    ids = [les["id"] for les in proj["outline"]["chapters"][0]["lessons"][:2]]

    async def go():
        st.run(proj, "写两课", lambda pr: st.run_step(pr, {"type": "write_lessons", "lesson_ids": ids}))
        await st.tasks[pid]
    asyncio.run(go())
    proj = st.projects.load(pid)
    assert [st.find_lesson(proj, i)[1]["status"] for i in ids] == ["awaiting", "awaiting"]
    assert proj["stage"] == "lessons"
