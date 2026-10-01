"""Round 5 step 2: the expert course lead is Claude itself — thinks, uses tools (reads the textbook, writes notes, looks
at the outline), proposes; nothing changes until the teacher confirms. Claude's API is simulated turn by turn."""
import json
import time

import httpx

from app import main
from app.ai import ModelGateway
from tests.test_lead import say, to_outline
from tests.test_materials import login
from tests.test_studio import client, moodle  # noqa: F401 - the fixture

SENT: list[dict] = []


def claude_script(turns):
    """MockTransport: api.anthropic.com answers with the scripted turns in order; the rest goes to the fake Moodle."""
    it = iter(turns)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "api.anthropic.com":
            body = json.loads(request.content)
            SENT.append(body)
            turn = next(it)
            content = turn(body) if callable(turn) else turn
            stop = "tool_use" if any(b["type"] == "tool_use" for b in content) else "end_turn"
            return httpx.Response(200, json={"content": content, "stop_reason": stop})
        return moodle(request)
    return handler


def use(name, inp, i):
    return [{"type": "thinking", "thinking": "…", "signature": "x"}, {"type": "tool_use", "id": f"t{i}", "name": name, "input": inp}]


def test_the_expert_reads_thinks_and_proposes(client):
    h = login(client)
    pid, p = to_outline(client, h)
    client.post(f"/api/v1/studio/projects/{pid}/approve-outline", headers=h)
    first = p["outline"]["chapters"][0]["lessons"][0]["id"]

    def final(body):
        # the tool results came back to the model
        results = [b for m in body["messages"] if m["role"] == "user" and isinstance(m["content"], list) for b in m["content"]]
        assert any("Chapter 1" in r["content"] for r in results)                    # it saw the outline
        assert any("saved notes for chapter 1" in r["content"] for r in results)
        assert any(r["content"].startswith("proposal ") for r in results)
        return [{"type": "text", "text": "我看了教材第 1 章和现在的大纲：第 1 章应该先讲机器人概论，再讲空间描述。我的方案见提议。"}]

    SENT.clear()
    http = httpx.AsyncClient(transport=httpx.MockTransport(claude_script([
        use("get_outline", {}, 1),
        use("search_materials", {"query": "第1章"}, 2),
        use("save_notes", {"chapter": 1, "title": "导论", "notes": "1.1 背景（p.1）……", "seen_book": True}, 3),
        use("propose", {"summary": "第 1 章重排", "steps": [
            {"type": "set_chapter", "no": 1, "title": {"zh": "导论", "en": "Introduction"},
             "lessons": [{"id": first, "title": {"zh": "机器人概论", "en": "Robots"}}, {"title": {"zh": "空间描述", "en": "Spatial descriptions"}}]},
            {"type": "confirm_chapter", "no": 1}, {"type": "nonsense"}]}, 4),
        final,
    ])))
    main.state.http = http
    main.state.moodle.http = http
    main.state.ai = ModelGateway("claude", http, anthropic_key="k", claude_model="claude-sonnet-5")
    p = client.put(f"/api/v1/studio/projects/{pid}/lead-v2", headers=h, json={"on": True}).json()
    assert p["lead_v2"] and p["lead_v2_available"]
    p, m = say(client, h, pid, "第一章的安排不对，你先看看教材再说", wait=15)
    assert m["kind"] == "proposal" and "教材第 1 章" in m["text"]
    body = SENT[0]
    assert body["model"] == "claude-opus-5-5" and body["thinking"]["type"] == "enabled"
    assert {t["name"] for t in body["tools"]} >= {"read_pages", "save_notes", "propose", "get_outline"}
    assert "tool_choice" not in body                                           # it decides itself what to look at
    assert body["messages"][-1]["content"].endswith("你先看看教材再说")
    assert len(SENT) == 5 and SENT[1]["messages"][-2]["content"][0]["type"] == "thinking"   # thinking kept between tool calls
    assert p["textbook_notes"]["1"]["notes"].startswith("1.1 背景")
    prop = next(x for x in p["proposals"] if x["id"] == m["proposal"])
    assert len(prop["steps"]) == 2 and prop["status"] == "open"                # the impossible step was dropped
    assert p["outline"]["chapters"][0]["lessons"][0]["title"]["zh"] != "机器人概论"   # nothing changed yet
    p = client.post(f"/api/v1/studio/projects/{pid}/proposals/{prop['id']}/confirm", headers=h).json()
    ch = p["outline"]["chapters"][0]
    assert [x["title"]["zh"] for x in ch["lessons"]] == ["机器人概论", "空间描述"] and ch["ready"]
    assert not p["lead_status"]


def test_study_textbook_without_the_book(client):
    h = login(client)
    pid, p = to_outline(client, h)
    notes = {"chapters": [{"chapter": 1, "title": "导论", "notes": "背景、空间描述、操作臂运动学概览（未见原书）"},
                          {"chapter": 2, "title": "空间描述和变换", "notes": "位置、姿态、坐标系、齐次变换"}]}
    http = httpx.AsyncClient(transport=httpx.MockTransport(claude_script([
        lambda body: (body.get("thinking") and [{"type": "thinking", "thinking": "…", "signature": "x"},
                                                {"type": "text", "text": "研读结果：\n" + json.dumps(notes, ensure_ascii=False)}]),
    ])))
    main.state.http = http
    main.state.moodle.http = http
    main.state.ai = ModelGateway("claude", http, anthropic_key="k")
    st = main._studio()
    proj = st.projects.load(pid)
    proj["materials"]["textbook"] = ""
    proj["materials"]["book_title"] = "机器人学导论"
    st.projects.save(proj)
    async def go():
        st.run(proj, "研读", st.study_textbook)
    client.portal.call(go)
    end = time.time() + 10
    while st.is_busy(pid) and time.time() < end:
        time.sleep(0.05)
    p = client.get(f"/api/v1/studio/projects/{pid}", headers=h).json()
    assert set(p["textbook_notes"]) == {"1", "2"} and not p["textbook_notes"]["1"]["seen_book"]
    assert "未见原书" in p["messages"][-1]["text"]
    # the notes reach the lecturer: a lesson's context carries its chapter's notes
    proj = st.projects.load(pid)
    ch = proj["outline"]["chapters"][0]
    assert "背景、空间描述" in st.notes_for(proj, 1) and "位置、姿态" in st.notes_for(proj)
    assert st.notes_for(proj, 9) == "" and ch
