"""Round 31: the course lead is the model itself (principles, tools), it edits the draft directly according to the
autonomy level, every change can be undone, batch work and deletions become proposals, replies stream."""
import json

import httpx

from app import main
from app.ai import ModelGateway
from tests.test_expert import SENT, claude_script, use
from tests.test_lead import say, to_outline
from tests.test_materials import login
from tests.test_studio import client, moodle  # noqa: F401 - the fixture


def as_claude(turns):
    http = httpx.AsyncClient(transport=httpx.MockTransport(claude_script(turns)))
    main.state.http = http
    main.state.moodle.http = http
    main.state.ai = ModelGateway("claude", http, anthropic_key="k", claude_model="claude-sonnet-5")


def lessons(p):
    return [les for c in p["outline"]["chapters"] for les in c["lessons"]]


def test_the_lead_edits_the_outline_at_once_and_the_teacher_can_undo(client):
    h = login(client)
    pid, p = to_outline(client, h)
    first, second = lessons(p)[0], lessons(p)[1]
    SENT.clear()
    as_claude([
        use("get_outline", {}, 1),
        use("edit_course", {"summary": "完善第 1 章", "ops": [
            {"type": "set_lesson", "lesson_id": first["id"], "title": {"zh": "操作系统的角色", "en": "Role of the OS"}, "week": 1},
            {"type": "add_lesson", "chapter_no": 1, "title": {"zh": "系统调用", "en": "System calls"}, "week": 2},
            {"type": "move_lesson", "lesson_id": second["id"], "chapter_no": 1, "position": 1},
            {"type": "remove_lesson", "lesson_id": "nope"}]}, 2),
        [{"type": "text", "text": "第 1 章改好了：第一课改名并排到第 1 周，新加了“系统调用”。不满意可以撤销。"}],
    ])
    p, m = say(client, h, pid, "能不能先把大纲完善", wait=15)
    assert "改好了" in m["text"]
    # the default lead is the AI lead, with the principles document and the new tools
    body = SENT[0]
    assert "课程负责人守则" in body["system"] and "Autonomy: small" in body["system"]
    assert {t["name"] for t in body["tools"]} >= {"edit_course", "start_work", "undo", "read_pages"}
    ch1 = p["outline"]["chapters"][0]["lessons"]
    assert ch1[0]["id"] == second["id"]                                             # moved to the top
    assert any(x["title"]["zh"] == "操作系统的角色" and x["week"] == 1 for x in ch1)
    assert any(x["title"]["zh"] == "系统调用" for x in ch1)
    card = next(x for x in p["messages"] if x.get("kind") == "change")
    assert card["text"] == "已改：完善第 1 章" and len(card["lines"]) == 3
    assert p["history"] and p["history"][-1]["by"] == "lead" and "history" not in json.dumps(p["history"][0].get("outline", ""))
    assert p["last_change"]["lessons"]
    # undo brings the outline back
    p = client.post(f"/api/v1/studio/projects/{pid}/undo", headers=h).json()
    assert [x["id"] for x in lessons(p)][:2] == [first["id"], second["id"]]
    assert lessons(p)[0]["title"] == first["title"] and not any(x["title"].get("zh") == "系统调用" for x in lessons(p))
    assert p["history"] == []
    assert client.post(f"/api/v1/studio/projects/{pid}/undo", headers=h).status_code == 409


def test_ask_mode_turns_edits_into_proposals_and_batches_always_ask(client):
    h = login(client)
    pid, p = to_outline(client, h)
    client.post(f"/api/v1/studio/projects/{pid}/approve-outline", headers=h)
    first = lessons(p)[0]
    p = client.put(f"/api/v1/studio/projects/{pid}/autonomy", headers=h, json={"level": "ask"}).json()
    assert p["autonomy"] == "ask"
    as_claude([
        use("edit_course", {"summary": "改名", "ops": [{"type": "set_lesson", "lesson_id": first["id"], "title": {"zh": "新名字", "en": "New"}}]}, 1),
        [{"type": "text", "text": "我提了一个改名的提议，等你确认。"}],
    ])
    p, m = say(client, h, pid, "第一课改个名", wait=15)
    assert m["kind"] == "proposal" and lessons(p)[0]["title"] == first["title"]       # nothing changed yet
    # small mode: writing two lessons at once is batch work → a proposal
    client.put(f"/api/v1/studio/projects/{pid}/autonomy", headers=h, json={"level": "small"})
    ids = [x["id"] for x in lessons(p)[:2]]
    as_claude([
        use("start_work", {"summary": "写前两课", "steps": [{"type": "write_lessons", "lesson_ids": ids}]}, 1),
        [{"type": "text", "text": "写两课是批量工作，提议在下面，确认后开始。"}],
    ])
    p, m = say(client, h, pid, "把前两课写了", wait=15)
    prop = next(x for x in p["proposals"] if x["id"] == m["proposal"])
    assert prop["steps"][0]["type"] == "write_lessons" and "依次写 2 课" in prop["lines"][0]
    assert not p["busy"]


def test_teacher_edits_are_undoable_too(client):
    h = login(client)
    pid, p = to_outline(client, h)
    o = p["outline"]
    body = {"title": o["title"], "summary": o.get("summary") or {"zh": "", "en": ""},
            "chapters": [{"id": c["id"], "no": c["no"], "title": c["title"], "summary": c.get("summary") or {"zh": "", "en": ""},
                          "lessons": [{"id": les["id"], "title": {**les["title"], "zh": "改过"}, "goal": les["goal"],
                                       "week": les.get("week") or 0, "sections": les.get("sections") or []} for les in c["lessons"]]}
                         for c in o["chapters"]]}
    p = client.put(f"/api/v1/studio/projects/{pid}/outline", headers=h, json=body).json()
    assert all(x["title"]["zh"] == "改过" for x in lessons(p)) and p["history"][-1]["by"] == "teacher"
    p = client.post(f"/api/v1/studio/projects/{pid}/undo", headers=h).json()
    assert not any(x["title"]["zh"] == "改过" for x in lessons(p))


def test_streaming_reply_is_parsed():
    """The streamed Messages API: text deltas reach on_text; tool input JSON is assembled."""
    import asyncio

    events = [
        {"type": "message_start", "message": {}},
        {"type": "content_block_start", "index": 0, "content_block": {"type": "thinking", "thinking": "", "signature": ""}},
        {"type": "content_block_delta", "index": 0, "delta": {"type": "signature_delta", "signature": "sig"}},
        {"type": "content_block_stop", "index": 0},
        {"type": "content_block_start", "index": 1, "content_block": {"type": "text", "text": ""}},
        {"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": "第 1 章"}},
        {"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": "改好了。"}},
        {"type": "content_block_stop", "index": 1},
        {"type": "content_block_start", "index": 2, "content_block": {"type": "tool_use", "id": "t1", "name": "undo", "input": {}}},
        {"type": "content_block_delta", "index": 2, "delta": {"type": "input_json_delta", "partial_json": "{\"a\": "}},
        {"type": "content_block_delta", "index": 2, "delta": {"type": "input_json_delta", "partial_json": "1}"}},
        {"type": "content_block_stop", "index": 2},
        {"type": "message_delta", "delta": {"stop_reason": "tool_use"}},
        {"type": "message_stop"},
    ]
    sse = "".join(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n" for e in events)

    def handler(request):
        assert json.loads(request.content)["stream"] is True
        return httpx.Response(200, text=sse, headers={"content-type": "text/event-stream"})
    seen = []

    async def go():
        gw = ModelGateway("claude", httpx.AsyncClient(transport=httpx.MockTransport(handler)), anthropic_key="k")
        return await gw._stream("https://api.anthropic.com/v1/messages", {"model": "m"}, {}, seen.append)
    data = asyncio.run(go())
    assert data["stop_reason"] == "tool_use"
    assert data["content"][0] == {"type": "thinking", "thinking": "", "signature": "sig"}
    assert data["content"][1]["text"] == "第 1 章改好了。" and seen[-1] == "第 1 章改好了。"
    assert data["content"][2]["input"] == {"a": 1}


def test_writing_from_the_outline_stage_settles_it_and_agreement_in_chat_carries_out_the_proposal(client):
    """Round 31, step 4 fix: the lead could not settle the outline, nor act on the teacher's 'yes' — it went in circles."""
    h = login(client)
    pid, p = to_outline(client, h)
    assert p["stage"] == "outline"
    ids = [x["id"] for x in lessons(p)[:2]]
    # asking to write two lessons while the outline is not settled: a proposal (batch work), not "impossible"
    as_claude([
        use("start_work", {"summary": "写前两课", "steps": [{"type": "write_lessons", "lesson_ids": ids}]}, 1),
        [{"type": "text", "text": "写两课是批量工作，提议在下面。"}],
    ])
    p, m = say(client, h, pid, "开始写吧", wait=15)
    prop = next(x for x in p["proposals"] if x["status"] == "open")
    assert prop["steps"][0]["type"] == "write_lessons"
    # the teacher agrees in the chat: the lead carries the proposal out (no new proposal)
    first = lessons(p)[0]
    client.put(f"/api/v1/studio/projects/{pid}/autonomy", headers=h, json={"level": "ask"})
    as_claude([
        use("edit_course", {"summary": "改名", "ops": [{"type": "set_lesson", "lesson_id": first["id"], "title": {"zh": "新名字", "en": "New"}}]}, 1),
        [{"type": "text", "text": "提议在下面。"}],
    ])
    p, m = say(client, h, pid, "第一课改个名", wait=15)
    rename = next(x for x in p["proposals"] if x["status"] == "open" and x["steps"][0]["type"] == "set_lesson")
    n_props = len(p["proposals"])
    as_claude([
        use("confirm_proposal", {"proposal_id": rename["id"]}, 1),
        [{"type": "text", "text": "改好了。"}],
    ])
    p, m = say(client, h, pid, "好，就这样", wait=15)
    assert len(p["proposals"]) == n_props
    assert next(x for x in p["proposals"] if x["id"] == rename["id"])["status"] == "done"
    assert lessons(p)[0]["title"]["zh"] == "新名字"
    assert any(x.get("kind") == "change" and x["text"].startswith("已按你的同意执行") for x in p["messages"])


def test_the_lead_can_settle_the_outline_and_undo_it(client):
    h = login(client)
    pid, p = to_outline(client, h)
    as_claude([
        use("edit_course", {"summary": "大纲定稿", "ops": [{"type": "approve_outline"}]}, 1),
        [{"type": "text", "text": "大纲定稿了，可以开写。"}],
    ])
    p, m = say(client, h, pid, "大纲可以了", wait=15)
    assert p["stage"] == "lessons" and not p["course"]["id"]      # the course is created at the first publish
    p = client.post(f"/api/v1/studio/projects/{pid}/undo", headers=h).json()
    assert p["stage"] == "outline"


def test_write_steps_are_possible_in_the_outline_stage_and_settle_it(client):
    import asyncio
    h = login(client)
    pid, p = to_outline(client, h)
    st = main._studio()
    proj = st.projects.load(pid)
    first = lessons(proj)[0]
    assert st.step_ok(proj, {"type": "write_next"}) and st.step_ok(proj, {"type": "write_lessons", "lesson_ids": [first["id"]]})
    called = []

    async def fake_write(pr, lid, note=""):
        called.append((pr["stage"], lid))
    st.write_lesson = fake_write
    asyncio.run(st.run_step(proj, {"type": "write_next"}))
    assert called == [("lessons", first["id"])]
    proj = st.projects.load(pid)
    assert proj["stage"] == "lessons" and proj["outline"]["chapters"][0]["confirmed"]
