"""第 35 轮第 3 步：白板课接进平台——新建（题目 / 录音）、保存、编译（动作、素材）、重排一张、重新配音、权限、链接、出视频。"""
import shutil
import subprocess
import time

import pytest

from app import main
from app import whiteboards as WB
from app.production import voice as V
from app.production.whiteboard import speech
from tests.test_lecture import fake_tts, tone
from tests.test_materials import login
from tests.test_studio import client  # noqa: F401 - the fixture

need_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="needs ffmpeg")

LAB_PAGE = "<!doctype html><html><body><div id='lab-2-5'>叉积与力矩</div></body></html>"
CHAPTER = ("<p>…</p><div class='wq-media-box wq-labbox' data-lab='2-5'>【实验 2.5】叉积与力矩</div>"
           "<div class='wq-media-box' data-anim='a2_5_1' data-hash='47ab655321b6'>【动画 2.5.1】B 绕着 A 转一圈：力矩随 sin θ 变化</div>")


@pytest.fixture
def wb(client, tmp_path, monkeypatch):  # noqa: F811
    main.state.whiteboards_dir = str(tmp_path / "wb")
    books = tmp_path / "books"
    (books / "physics" / "lab").mkdir(parents=True)
    (books / "physics" / "ch02.html").write_text(CHAPTER, encoding="utf-8")
    (books / "physics" / "lab" / "ch02.html").write_text(LAB_PAGE, encoding="utf-8")
    monkeypatch.setattr(main.state.settings, "textbook_dir", str(books))
    monkeypatch.setattr(main.state.settings, "data_dir", str(tmp_path / "data"))
    monkeypatch.setattr(V, "tts", fake_tts)
    monkeypatch.setattr(main.state.settings, "voice_url", "http://voice.test")
    yield client
    main.state.whiteboards_dir = None


def settle(c, h, wid, timeout=20.0):
    end = time.time() + timeout
    while time.time() < end:
        L = c.get(f"/api/v1/whiteboards/{wid}", headers=h).json()
        if not L["job"]:
            return L
        time.sleep(0.05)
    raise AssertionError("still working")


@need_ffmpeg
def test_from_a_topic_to_a_web_page(wb):
    h = login(wb)
    r = wb.post("/api/v1/whiteboards", headers=h, json={"topic": "机器人关节的力矩", "minutes": 3, "voice": "zm_yunjian"})
    assert r.status_code == 200, r.text
    wid = r.json()["id"]
    L = settle(wb, h, wid)
    assert L["state"] == "ready", L["error"]
    assert L["segments"] and all(s["t1"] > s["t0"] for s in L["segments"]) and L["duration"] > L["segments"][-1]["t1"]
    assert [s["t0"] for s in L["segments"]] == sorted(s["t0"] for s in L["segments"])
    frames = [e for e in L["scene"]["elements"] if e["type"] == "frame"]
    assert frames and L["audio_kind"] == "ai" and L["play"]
    # the list
    lst = wb.get("/api/v1/whiteboards", headers=h).json()
    assert [x["id"] for x in lst["lessons"]] == [wid] and lst["voice_on"]
    # the page and its narration
    page = wb.get(L["play"].replace("http://testserver", ""))
    assert page.status_code == 200 and "WB.init" in page.text and "sandbox" in page.headers["content-security-policy"]
    audio = wb.get(L["audio"].replace("http://testserver", ""))
    assert audio.status_code == 200 and audio.headers["content-type"] == "audio/mpeg"
    # someone else sees nothing
    other = login(wb, "s")
    assert wb.get(f"/api/v1/whiteboards/{wid}", headers=other).status_code == 403
    assert wb.get("/api/v1/whiteboards", headers=other).json()["lessons"] == []


@need_ffmpeg
def test_save_compile_with_moves_and_media_then_revoice_only_changed(wb):
    h = login(wb)
    wid = wb.post("/api/v1/whiteboards", headers=h, json={"topic": "力矩", "minutes": 3}).json()["id"]
    L = settle(wb, h, wid)
    scene = L["scene"]
    frame = next(e for e in scene["elements"] if e["type"] == "frame")
    # the teacher adds a lab frame and an arm that turns
    scene["elements"] += [
        {"id": "m1", "type": "rectangle", "x": frame["x"] + 900, "y": frame["y"] + 300, "width": 800, "height": 450,
         "frameId": frame["id"], "customData": {"wq_at": 1, "wq_media": {"src": "lab:physics/2.5"}}},
        {"id": "arm", "type": "line", "x": frame["x"] + 200, "y": frame["y"] + 600, "width": 300, "height": 0,
         "points": [[0, 0], [300, 0]], "frameId": frame["id"], "customData": {"wq_at": 2, "wq_id": "arm"}},
    ]
    r = wb.put(f"/api/v1/whiteboards/{wid}", headers=h, json={"scene": scene, "title": "关节力矩"})
    assert r.status_code == 200 and r.json()["title"]["zh"] == "关节力矩"
    main.state.whiteboards.load(wid)
    L2 = main.state.whiteboards.load(wid)
    L2["moves"].append({"frame": frame["id"], "at": 2, "kind": "rotate", "targets": ["arm"], "pivot": [200, 600], "to": -60})
    main.state.whiteboards.save(L2)
    data = wb.post(f"/api/v1/whiteboards/{wid}/compile", headers=h, json={}).json()
    assert data["media"] and data["media"][0]["kind"] == "page" and data["media"][0]["url"].endswith("#lab-2-5")
    assert any(m["kind"] == "rotate" and m["targets"] == ["arm"] for m in data["moves"])
    lab = wb.get(data["media"][0]["url"].split("#")[0].replace("http://testserver", ""))
    assert lab.status_code == 200 and "叉积" in lab.text and "sandbox" in lab.headers["content-security-policy"]
    # the media list has the textbook lab
    media = wb.get(f"/api/v1/whiteboards/{wid}/media", headers=h).json()["media"]
    assert any(x["src"] == "lab:physics/2.5" for x in media)
    # change one segment's words: only that one is spoken again
    segs = [{"zh": s["zh"]} for s in L["segments"]]
    segs[1]["zh"] = "我们换一种说法：力矩等于力乘以力臂。"
    r = wb.put(f"/api/v1/whiteboards/{wid}", headers=h, json={"segments": segs}).json()
    assert r["voice_stale"]
    from tests import test_lecture
    test_lecture.SPOKEN.clear()
    wb.post(f"/api/v1/whiteboards/{wid}/revoice", headers=h)
    L3 = settle(wb, h, wid)
    assert not L3["voice_stale"] and len(test_lecture.SPOKEN) == 1 and "力臂" in test_lecture.SPOKEN[0][0]


@need_ffmpeg
def test_redo_one_board_keeps_the_others(wb):
    h = login(wb)
    wid = wb.post("/api/v1/whiteboards", headers=h, json={"topic": "力矩", "minutes": 3}).json()["id"]
    L = settle(wb, h, wid)
    frames = [e for e in L["scene"]["elements"] if e["type"] == "frame"]
    keep_other = {e["id"] for e in L["scene"]["elements"] if e.get("frameId") not in (None, frames[0]["id"]) and e["type"] != "frame"}
    wb.post(f"/api/v1/whiteboards/{wid}/redo", headers=h, json={"frame": frames[0]["id"], "note": "太挤了"})
    L2 = settle(wb, h, wid)
    assert L2["state"] == "ready" and not L2["error"]
    ids = {e["id"] for e in L2["scene"]["elements"]}
    assert keep_other <= ids and frames[0]["id"] not in ids
    new_frames = [e for e in L2["scene"]["elements"] if e["type"] == "frame"]
    assert new_frames[0]["x"] == frames[0]["x"]


@need_ffmpeg
def test_from_a_recording(wb, monkeypatch):
    h = login(wb)

    async def fake_asr(url, wav, timeout=3600.0):
        return [{"start": 0.5, "end": 2.0, "text": "大家好"}, {"start": 2.2, "end": 3.0, "text": "今天讲力矩"},
                {"start": 4.0, "end": 6.5, "text": "力矩等于力乘以力臂。"}, {"start": 7.0, "end": 9.0, "text": "我们来算一算。"}]
    monkeypatch.setattr(V, "asr", fake_asr)
    L = wb.post("/api/v1/whiteboards", headers=h, json={"source": "recording"}).json()
    assert L["state"] == "waiting"
    r = wb.post(f"/api/v1/whiteboards/{L['id']}/upload?kind=recording&upload=abcdefgh1&index=0&total=1&name=lesson.wav",
                headers=h, content=tone(10.0))
    assert r.status_code == 200, r.text
    L = settle(wb, h, L["id"])
    assert L["state"] == "ready" and L["audio_kind"] == "teacher", L["error"]
    assert [s["zh"] for s in L["segments"]][0] == "大家好，今天讲力矩" and len(L["segments"]) == 3
    assert wb.post(f"/api/v1/whiteboards/{L['id']}/revoice", headers=h).status_code == 409
    # a video for a frame
    r = wb.post(f"/api/v1/whiteboards/{L['id']}/upload?kind=video&upload=abcdefgh2&index=0&total=1&name=车间.mp4",
                headers=h, content=b"\0" * 2000)
    assert r.json()["src"] == "upload:车间.mp4"
    assert any(x["src"] == "upload:车间.mp4" for x in wb.get(f"/api/v1/whiteboards/{L['id']}/media", headers=h).json()["media"])


@need_ffmpeg
def test_mp4_in_pieces_joined_with_the_narration(wb, monkeypatch, tmp_path):
    h = login(wb)
    monkeypatch.setattr(main.state.settings, "labcheck_url", "http://labcheck.test")
    monkeypatch.setattr(WB, "CHUNK", 4.0)
    pages = []

    async def fake_record(url, html, seconds):
        pages.append(html)
        out = tmp_path / f"c{len(pages)}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=white:s=320x180:d={seconds}:r=30",
                        "-pix_fmt", "yuv420p", str(out)], check=True)
        return out.read_bytes()
    monkeypatch.setattr(WB, "record", fake_record)
    wid = wb.post("/api/v1/whiteboards", headers=h, json={"topic": "力矩", "minutes": 1}).json()["id"]
    L = settle(wb, h, wid)
    wb.post(f"/api/v1/whiteboards/{wid}/mp4", headers=h)
    L = settle(wb, h, wid, 60)
    assert L["mp4_state"] == "done" and L["video"], L["error"]
    assert len(pages) == int((L["duration"] + 3.999) // 4) and "window.SEEK" in pages[1] and "WB.seek(4.0+t)" in pages[1]
    v = wb.get(L["video"].replace("http://testserver", ""))
    assert v.status_code == 200 and v.headers["content-type"] == "video/mp4"
    p = tmp_path / "out.mp4"
    p.write_bytes(v.content)
    streams = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(p)],
                             capture_output=True, text=True).stdout.split()
    assert streams == ["video", "audio"]


@need_ffmpeg
def test_a_lesson_of_the_course_builder_gets_a_whiteboard_lecture(wb):
    from tests.test_studio import make_project
    h = login(wb)
    pid = make_project(wb, h)
    st = main._studio()
    proj = st.projects.load(pid)
    proj["outline"] = {"title": {"zh": "大学物理"}, "chapters": [{"no": 1, "title": {"zh": "力"}, "lessons": [
        {"id": "l1", "title": {"zh": "力矩"}, "status": "awaiting", "content": {"zh": "<p>力矩等于力乘以力臂。</p>"}, "files": []}]}]}
    st.projects.save(proj)
    r = wb.post(f"/api/v1/studio/projects/{pid}/lessons/l1/whiteboard", headers=h, json={})
    assert r.status_code == 200, r.text
    wid = r.json()["id"]
    L = settle(wb, h, wid)
    assert L["state"] == "ready" and L["course"]["pid"] == pid
    assert st.projects.load(pid)["outline"]["chapters"][0]["lessons"][0]["whiteboard"] == wid


def test_symbols_are_read_out():
    assert speech.speakable("τ = F × r = 20 N × 0.3 m = 6 N·m") == "tau 等于 F 乘以 r 等于 20 N 乘以 0.3 m 等于 6牛米"
    assert "度" in speech.speakable("抬到 60°") and "约等于" in speech.speakable("≈ 3")
    assert speech.merge_asr([{"start": 0, "end": 1, "text": "一"}, {"start": 1.2, "end": 2, "text": "二。"},
                             {"start": 2.1, "end": 3, "text": "三"}]) == [{"t0": 0, "t1": 2, "zh": "一，二。"}, {"t0": 2.1, "t1": 3, "zh": "三"}]
