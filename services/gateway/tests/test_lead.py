"""Round 5: the course lead listens, says what it understood and thinks, proposes; nothing changes until the teacher
confirms; "stop" stops at once; a chapter is written only after the teacher confirms it. Scenario: 机器人学 第 1 章 导论."""
import asyncio
import time

from app import main
from app import studio as st
from app.lead import is_stop
from tests.test_materials import login
from tests.test_studio import client, confirm_chapters, make_project, settle  # noqa: F401 - the fixture


def to_outline(client, h):
    pid = make_project(client, h)
    client.post(f"/api/v1/studio/projects/{pid}/start", headers=h)
    settle(client, h, pid)
    client.post(f"/api/v1/studio/projects/{pid}/approve-materials", headers=h)
    return pid, settle(client, h, pid)


def say(client, h, pid, text, wait=10.0):
    n = len(client.get(f"/api/v1/studio/projects/{pid}", headers=h).json()["messages"])
    client.post(f"/api/v1/studio/projects/{pid}/messages", headers=h, json={"text": text})
    end = time.time() + wait
    while time.time() < end:
        p = client.get(f"/api/v1/studio/projects/{pid}", headers=h).json()
        new = p["messages"][n:]
        if any(m["role"] == "lead" for m in new) and not p.get("lead_thinking"):
            return p, [m for m in new if m["role"] == "lead"][-1]
        time.sleep(0.05)
    raise AssertionError("the course lead did not answer")


def test_stop_words():
    for t in ("停", "先停一下", "停下来，教材不对", "等一下，别写了", "stop", "Hold on"):
        assert is_stop(t), t
    for t in ("AGV 急停的例子要保留", "第1章改成：概论；空间描述"):
        assert not is_stop(t), t


def test_a_book_not_uploaded_becomes_the_textbook_only_after_confirming(client):
    h = login(client)
    pid, p = to_outline(client, h)
    before = p["materials"]["textbook"]
    p, m = say(client, h, pid, "主教材是《机器人学导论》，资料里没有这本书")
    assert m["kind"] == "proposal" and "机器人学导论" in m["text"]
    prop = next(x for x in p["proposals"] if x["id"] == m["proposal"])
    assert prop["status"] == "open" and "不再追问" in prop["lines"][0]
    assert p["materials"]["textbook"] == before                                 # nothing changed yet
    p = client.post(f"/api/v1/studio/projects/{pid}/proposals/{prop['id']}/confirm", headers=h).json()
    assert p["materials"]["book_title"] == "机器人学导论" and p["requirements"]["textbook"] == "机器人学导论"
    assert not [q for q in p["questions"] if q["status"] == "open" and "教材" in q["text"]]
    done = p["messages"][-1]
    assert done["kind"] == "done" and done["text"].startswith("已按你确认的做了") and "✓" in done["text"]
    assert "要不要按新教材重做" in done["text"]                                   # says what is NOT done yet
    assert not p["busy"]                                                         # and does not start anything by itself


def test_chapter_one_is_changed_then_confirmed_before_writing(client):
    h = login(client)
    pid, p = to_outline(client, h)
    client.post(f"/api/v1/studio/projects/{pid}/approve-outline", headers=h)
    # the outline is settled, but chapter 1 is not confirmed: no lesson is written
    r = client.post(f"/api/v1/studio/projects/{pid}/lessons/next", headers=h)
    assert r.status_code == 409 and r.json()["error"] == "chapter_unconfirmed"
    p, m = say(client, h, pid, "第1章改成：机器人概论；位置与姿态的描述；齐次变换")
    prop = m["proposal"]
    assert client.get(f"/api/v1/studio/projects/{pid}", headers=h).json()["outline"]["chapters"][0]["lessons"][0]["title"]["zh"] != "机器人概论"
    p = client.post(f"/api/v1/studio/projects/{pid}/proposals/{prop}/confirm", headers=h).json()
    ch = p["outline"]["chapters"][0]
    assert [x["title"]["zh"] for x in ch["lessons"]] == ["机器人概论", "位置与姿态的描述", "齐次变换"] and not ch["confirmed"]
    assert client.post(f"/api/v1/studio/projects/{pid}/lessons/next", headers=h).status_code == 409
    p, m = say(client, h, pid, "确认第1章")
    p = client.post(f"/api/v1/studio/projects/{pid}/proposals/{m['proposal']}/confirm", headers=h).json()
    assert p["outline"]["chapters"][0]["confirmed"]
    p = client.post(f"/api/v1/studio/projects/{pid}/lessons/next", headers=h).json()
    assert p["busy"] and "机器人概论" in p["busy"]["label"]
    settle(client, h, pid, 30)
    # editing a confirmed chapter's lessons by hand makes it wait for confirmation again
    p = client.get(f"/api/v1/studio/projects/{pid}", headers=h).json()
    o = p["outline"]
    o["chapters"][0]["lessons"][2]["title"]["zh"] = "齐次变换与坐标系"
    p = client.put(f"/api/v1/studio/projects/{pid}/outline", headers=h, json=o).json()
    assert not p["outline"]["chapters"][0]["confirmed"]


def test_stop_means_stop_even_mid_work_then_discuss(client, monkeypatch):
    h = login(client)
    pid, p = to_outline(client, h)
    client.post(f"/api/v1/studio/projects/{pid}/approve-outline", headers=h)
    confirm_chapters(client, h, pid)

    async def slow(self, proj, lid, note=""):
        await asyncio.sleep(30)
    monkeypatch.setattr(st.Studio, "write_lesson", slow)
    p = client.post(f"/api/v1/studio/projects/{pid}/lessons/next", headers=h).json()
    assert p["busy"]
    p, m = say(client, h, pid, "先停一下，教材不对")
    assert not p["busy"] and "停" in m["text"]
    assert any("已停止" in x["text"] for x in p["messages"])
    lesson = p["outline"]["chapters"][0]["lessons"][0]
    assert lesson["status"] == "planned"


def test_talking_while_the_team_works_gets_an_answer_and_does_not_disturb_it(client, monkeypatch):
    h = login(client)
    pid, p = to_outline(client, h)
    client.post(f"/api/v1/studio/projects/{pid}/approve-outline", headers=h)
    confirm_chapters(client, h, pid)

    async def slow(self, proj, lid, note=""):
        for _ in range(20):
            await asyncio.sleep(0.1)
            self.projects.save(proj)          # the job keeps saving its (older) copy of the project
    monkeypatch.setattr(st.Studio, "write_lesson", slow)
    client.post(f"/api/v1/studio/projects/{pid}/lessons/next", headers=h)
    p, m = say(client, h, pid, "你们现在在写哪一课？")
    assert p["busy"] and m["role"] == "lead"                                    # answered while busy, work goes on
    p = settle(client, h, pid, 10)
    assert any(x["text"] == "你们现在在写哪一课？" for x in p["messages"])          # nothing lost when the job saved
    assert any(x["id"] == m["id"] for x in p["messages"])


def test_ok_starts_nothing_and_a_cancelled_proposal_changes_nothing(client):
    h = login(client)
    pid, p = to_outline(client, h)
    client.post(f"/api/v1/studio/projects/{pid}/approve-outline", headers=h)
    p, m = say(client, h, pid, "好的")
    assert m["kind"] != "proposal" and not p["busy"] and "好的，记下了" not in m["text"]
    p, m = say(client, h, pid, "写下一课")
    assert m["kind"] == "proposal" and not p["busy"]                            # proposed, not started
    p = client.post(f"/api/v1/studio/projects/{pid}/proposals/{m['proposal']}/cancel", headers=h).json()
    assert not p["busy"] and next(x for x in p["proposals"] if x["id"] == m["proposal"])["status"] == "cancelled"
    # confirming a proposal that needs an unconfirmed chapter is refused with the reason
    p, m = say(client, h, pid, "写下一课")
    p = client.post(f"/api/v1/studio/projects/{pid}/proposals/{m['proposal']}/confirm", headers=h).json()
    p = settle(client, h, pid)
    assert "还没确认" in p["messages"][-1]["text"]


def test_when_the_model_fails_the_lead_says_so(client, monkeypatch):
    h = login(client)
    pid, p = to_outline(client, h)

    async def broken(**kw):
        raise RuntimeError("timeout")
    monkeypatch.setattr(main.state.ai, "json", broken)
    p, m = say(client, h, pid, "主教材是《机器人学导论》")
    assert "没能处理" in m["text"] and m["kind"] == "error"
