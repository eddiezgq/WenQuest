"""第 35 轮 白板讲课：AI 输出的检查修正、编译成播放数据、从 Excalidraw 画板再编译。"""
import asyncio

from app.ai import ModelGateway
from app.production.whiteboard import ai as wai
from app.production.whiteboard import core


def segs(n):
    return [{"t0": i * 4.0, "t1": i * 4.0 + 3.2, "zh": f"第{i}段讲稿"} for i in range(n)]


def test_fix_board_repairs_layout():
    els = [{"t": "box", "at": 0, "x": 500, "y": 400, "w": 300, "h": 100, "zh": "力矩", "en": "Torque"},
           {"t": "box", "at": 1, "x": 520, "y": 410, "w": 300, "h": 100, "zh": "力臂"},             # on top of the first
           {"t": "icon", "at": 2, "name": "unicorn", "x": 900, "y": 500, "zh": "独角兽"},            # unknown icon → box
           {"t": "icon", "at": 2, "name": "unicorn", "x": 900, "y": 500},                            # nothing to show → dropped
           {"t": "text", "at": 9, "x": -50, "y": 2000, "text": "这是一行非常非常长的字" * 6, "s": 60}, # out of the board, too long
           {"t": "arrow", "at": 1, "pts": [[10, 10]]}]                                               # one point → dropped
    out, notes = wai.fix_board(els, 4)
    kinds = [e["t"] for e in out]
    assert kinds == ["box", "box", "box", "text"]
    a, b = wai.bbox(out[0]), wai.bbox(out[1])
    assert not wai._overlap(a, b, 0)
    t = out[3]
    x0, y0, x1, y1 = wai.AREA
    tb = wai.bbox(t)
    assert t["at"] == 3 and tb[0] >= x0 - 1 and tb[2] <= x1 + 1 and t["y"] <= y1
    assert notes


def test_boards_follow_the_lecture():
    boards = [{"title": {"zh": "一"}, "elements": [{"t": "text", "at": 5, "x": 100, "y": 300, "text": "甲"}]},
              {"title": {"zh": "二"}, "elements": [{"t": "text", "at": 2, "x": 100, "y": 300, "text": "乙"}]}]
    out, _ = wai.fix_boards(boards, 8)
    assert out[1]["elements"][0]["at"] == 5


def test_fake_pipeline_compiles_to_player_data_and_back_through_excalidraw():
    ai = ModelGateway("fake", None)

    async def go():
        script = await wai.write_script(ai, "机器人关节的力矩")
        ss = [dict(s, t0=i * 4.0, t1=i * 4.0 + 3) for i, s in enumerate(script["segments"])]
        boards, notes = await wai.lay_out(ai, script["title"], ss)
        return script, ss, boards
    script, ss, boards = asyncio.run(go())
    lesson = wai.to_lesson(script["title"], ss, boards)
    data, ex = core.compile_lesson(lesson)
    assert data["items"] and all(it["dur"] > 0 for it in data["items"])
    assert [it["at"] for it in data["items"]] == sorted(it["at"] for it in data["items"])
    scene = core.excalidraw(lesson, ex)
    again = core.compile_scene(scene, lesson["segments"])
    assert len(again["items"]) == len(data["items"])
    html = core.page(data, "t", render=True)
    assert "WB.init" in html and "http" not in html.split("<script>")[0].lower().replace("http://www.w3.org", "")


def test_proofread_keeps_times_and_count():
    ai = ModelGateway("fake", None)
    out = asyncio.run(wai.proofread(ai, segs(5)))
    assert [s["t0"] for s in out["segments"]] == [s["t0"] for s in segs(5)]


def test_every_icon_has_help():
    assert set(wai.ICON_HELP) >= set(core.ICONS)


def test_moves_and_media_follow_the_drawing():
    lesson = {"title": "t", "audio": "", "segments": segs(3), "boards": [{"title": {"zh": "姿势"}, "elements": [
        {"t": "line", "at": 0, "id": "arm", "pts": [[200, 700], [800, 700]]},
        {"t": "arrow", "at": 0, "id": "load", "pts": [[800, 720], [800, 900]]},
        {"t": "move", "at": 0, "kind": "rotate", "targets": ["arm"], "pivot": [200, 700], "to": -60},
        {"t": "move", "at": 0, "kind": "shift", "targets": ["load"], "dx": -300, "dy": -520},
        {"t": "media", "at": 2, "src": "lab:physics/2.5", "x": 300, "y": 300, "w": 960, "h": 540}]}]}
    data, _ = core.compile_lesson(lesson, lambda src: {"kind": "page", "html": "<p>lab</p>"} if src.startswith("lab:") else None)
    drawn = max(it["start"] + it["dur"] for it in data["items"] if it.get("eid") in ("arm", "load"))
    rot, sh = data["moves"]
    assert rot["start"] == sh["start"] >= drawn            # moves start together, after the things are drawn
    assert all(it.get("eid") == "load" for it in data["items"] if it.get("eid") and it["shape"]["pts"][-1] == [800, 900])
    frame = data["items"][-1]
    assert data["media"][0]["start"] >= frame["start"] + frame["dur"]
    assert "<\\/p>" in core.page(data, "t", render=True)   # embedded pages cannot end the script early


def test_ai_keeps_only_listed_media_and_valid_moves():
    els = [{"t": "media", "at": 0, "src": "lab:physics/2.5", "x": 0, "y": 0, "w": 900},
           {"t": "media", "at": 0, "src": "https://example.com/x.mp4", "x": 0, "y": 0, "w": 900},
           {"t": "move", "at": 0, "kind": "teleport", "targets": ["a"]},
           {"t": "move", "at": 0, "kind": "spin", "targets": ["wheel"], "rpm": 999}]
    out, _ = wai.fix_board(els, 2, frozenset({"lab:physics/2.5"}))
    assert [e["t"] for e in out] == ["media", "move"] and out[1]["rpm"] == 120
    assert out[0]["x"] >= wai.AREA[0] and abs(out[0]["h"] - 900 * 9 / 16) < 1
