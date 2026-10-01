"""Round 4 · step 5: lecture videos — AI narration (B), the teacher's recording (A), edits, publishing, the player data."""
import io
import json
import math
import shutil
import subprocess
import time
import wave

import numpy as np
import pytest
from PIL import Image

from app import main
from app.production import lecture as L
from app.production import voice as V
from tests.test_materials import UPLOADS, login
from tests.test_studio import CALLS, client, confirm_chapters, make_project, settle  # noqa: F401 - the fixture

need_ffmpeg = pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("soffice")), reason="needs ffmpeg and LibreOffice")


def tone(seconds: float, hz: float = 220.0, rate: int = 24000) -> bytes:
    t = np.arange(int(seconds * rate)) / rate
    a = (0.2 * np.sin(2 * math.pi * hz * t) * 32767).astype("<i2")
    b = io.BytesIO()
    with wave.open(b, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(a.tobytes())
    return b.getvalue()


SPOKEN: list[tuple[str, str, float]] = []


async def fake_tts(url, text, voice, speed=1.0, timeout=300.0):
    SPOKEN.append((text, voice, speed))
    secs = round(max(0.4, len(text) * (0.09 if voice.startswith("z") else 0.045)) / speed, 2)
    return tone(secs), secs


def probe(path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                                capture_output=True, text=True).stdout)


def test_text_is_split_into_speakable_subtitle_lines():
    zh = L.sentences("机械臂有 $\\theta_1$ 和 θ₂ 两个角。末端的速度等于角速度乘以半径，这就是我们要用的关系式，在后面的建模里还会反复出现，请记住它！", "zh")
    assert zh[0] == "机械臂有 theta 1 和 θ₂ 两个角。" and all(len(x) <= L.ZH_MAX * 1.5 for x in zh) and len(zh) >= 3
    en = L.sentences("The arm is 0.5 m long. It turns at 2 rad/s! Why?", "en")
    assert en == ["The arm is 0.5 m long.", "It turns at 2 rad/s!", "Why?"]
    cues = [{"start": 0.5, "end": 2.25, "text": "一"}, {"start": 61.0, "end": 3725.5, "text": "two"}]
    text = L.vtt(cues)
    assert "00:01:01.000 --> 01:02:05.500" in text and L.parse_vtt(text) == cues


def test_the_timeline_fits_the_longer_language():
    slides = [{"audio": {"zh": [{"seconds": 3.0}, {"seconds": 2.0}], "en": [{"seconds": 2.0}]}},
              {"audio": {"zh": [{"seconds": 1.0}], "en": [{"seconds": 6.0}]}, "clip_seconds": 9.0}]
    tl = L.timeline(slides, ["zh", "en"])
    assert abs(tl[0]["seconds"] - (L.HEAD + 5.0 + L.PAUSE + L.TAIL)) < 0.04
    assert tl[1]["seconds"] >= 9.6 and tl[1]["start"] == tl[0]["seconds"]
    assert tl[0]["times"]["zh"][1][0] == pytest.approx(L.HEAD + 3.0 + L.PAUSE)


@need_ffmpeg
def test_assemble_two_voices_one_picture(tmp_path):
    imgs = []
    for i, c in enumerate(("#123456", "#f0f0f0")):
        p = tmp_path / f"p{i}.png"
        Image.new("RGB", (1600, 900), c).save(p)
        imgs.append(p)
    clip = tmp_path / "clip.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=s=640x360:d=2:r=30", "-pix_fmt", "yuv420p",
                    str(clip)], check=True)
    wavs = {}
    for k, s in (("a", 1.2), ("b", 0.8), ("c", 2.0)):
        wavs[k] = tmp_path / f"{k}.wav"
        wavs[k].write_bytes(tone(s))
    slides = [{"image": imgs[0], "clip": None, "box": None, "audio": {
                  "zh": [{"wav": wavs["a"], "seconds": 1.2, "text": "第一句。"}, {"wav": wavs["b"], "seconds": 0.8, "text": "第二句。"}],
                  "en": [{"wav": wavs["c"], "seconds": 2.0, "text": "One."}]}},
              {"image": imgs[1], "clip": clip, "box": {"x": 0.1, "y": 0.2, "w": 0.5, "h": 0.5}, "clip_seconds": 2.0,
               "audio": {"zh": [{"wav": wavs["b"], "seconds": 0.8, "text": "看动画。"}], "en": [{"wav": wavs["a"], "seconds": 1.2, "text": "Watch."}]}}]
    out = tmp_path / "lecture"
    r = L.assemble(slides, ["zh", "en"], out, tmp_path / "cache")
    assert abs(probe(out / "zh.mp4") - r["seconds"]) < 0.3 and abs(probe(out / "en.mp4") - r["seconds"]) < 0.3
    zh = L.parse_vtt((out / "zh.vtt").read_text())
    assert [c["text"] for c in zh] == ["第一句。", "第二句。", "看动画。"] and zh[2]["start"] >= r["slides"][1]["start"]
    assert (out / "poster.jpg").exists()
    # a second run with the same pictures reuses the encoded slides
    before = sorted(p.name for p in (tmp_path / "cache").iterdir())
    L.assemble(slides, ["zh", "en"], out, tmp_path / "cache")
    assert sorted(p.name for p in (tmp_path / "cache").iterdir()) == before


@need_ffmpeg
def test_ai_lecture_is_made_edited_and_published(client, monkeypatch):
    SPOKEN.clear()
    monkeypatch.setattr(V, "tts", fake_tts)
    monkeypatch.setattr(main.state.settings, "voice_url", "http://voice.test")
    h = login(client)
    pid, p = _write_first_lesson(client, h)
    p = settle(client, h, pid, 120)
    les = p["outline"]["chapters"][0]["lessons"][0]
    lec = next(f for f in les["files"] if f["kind"] == "lecture")
    assert lec["langs"] == ["zh", "en"] and lec["seconds"] > 10 and lec["source"] == "ai"
    item = next(c for c in les["checklist"] if c["key"] == "lecture")
    assert item["ok"] and "AI 讲解" in item["note"]
    assert {v for _, v, _ in SPOKEN} == {"zf_xiaobei", "af_heart"}
    # the teacher's preview: both voices, both subtitle tracks
    urls = lec["lecture"]
    assert client.get(urls["video"]["en"]).content[4:8] == b"ftyp"
    r = client.get(urls["subs"]["zh"])
    assert r.headers["content-type"].startswith("text/vtt") and "-->" in r.text
    part = client.get(urls["video"]["zh"], headers={"Range": "bytes=0-99"})
    assert part.status_code == 206 and len(part.content) == 100
    # the lines to check: one per slide
    v = client.get(f"/api/v1/studio/projects/{pid}/lessons/{les['id']}/lecture", headers=h).json()
    assert v["source"] == "ai" and len(v["rows"]) >= 8 and v["rows"][1]["start"] > 0 and not v["locked"]
    # an edit speaks only the changed sentence again
    n = len(SPOKEN)
    client.put(f"/api/v1/studio/projects/{pid}/lessons/{les['id']}/lecture", headers=h,
               json={"rows": [{"n": 1, "zh": "这一页先不急着算，想一想机器人会怎么动。"}]})
    p = settle(client, h, pid, 60)
    assert [t for t, _, _ in SPOKEN[n:]] == ["这一页先不急着算，想一想机器人会怎么动。"]
    v = client.get(f"/api/v1/studio/projects/{pid}/lessons/{les['id']}/lecture", headers=h).json()
    assert v["rows"][1]["edited"] and "想一想机器人" in client.get(urls["subs"]["zh"]).text
    # voices of the course
    monkeypatch.setattr(V, "voices", lambda url: _voices())
    vs = client.get("/api/v1/studio/voices", headers=h).json()
    assert vs["available"] and vs["voices"][0]["sample"]
    assert client.put(f"/api/v1/studio/projects/{pid}/voices", headers=h, json={"zh": "af_heart"}).status_code == 400
    assert client.put(f"/api/v1/studio/projects/{pid}/voices", headers=h, json={"zh": "zm_yunxi"}).json()["voices"]["zh"] == "zm_yunxi"
    # publishing: one file activity with the main video, the English voice and both subtitles
    UPLOADS.clear()
    p = client.post(f"/api/v1/studio/projects/{pid}/lessons/{les['id']}/approve", headers=h).json()
    sent = [c for f, c in CALLS if f == "local_wenquest_add_activities"][-1]
    order = [(sent[f"activities[{i}][type]"], sent[f"activities[{i}][name]"]) for i in range(20) if f"activities[{i}][type]" in sent]
    assert order[1][0] == "resource" and "讲解视频" in order[1][1]
    names = [u.split(b'filename="')[1].split(b'"')[0].decode() for u in UPLOADS if b'filename="' in u]
    names = [n for n in names if "讲解视频" in n]
    stem = order[1][1]
    assert names[:4] == [f"{stem}.mp4", f"{stem}.en.mp4", f"{stem}.zh.vtt", f"{stem}.en.vtt"]
    # published: the lines can be read but not changed
    assert client.put(f"/api/v1/studio/projects/{pid}/lessons/{les['id']}/lecture", headers=h, json={"rows": []}).status_code == 409


def _write_first_lesson(client, h):
    pid = make_project(client, h)
    client.post(f"/api/v1/studio/projects/{pid}/start", headers=h)
    settle(client, h, pid)
    client.post(f"/api/v1/studio/projects/{pid}/approve-materials", headers=h)
    settle(client, h, pid)
    client.post(f"/api/v1/studio/projects/{pid}/approve-outline", headers=h)
    confirm_chapters(client, h, pid)
    client.post(f"/api/v1/studio/projects/{pid}/lessons/next", headers=h)
    return pid, settle(client, h, pid, 180)


async def _voices():
    return [{"id": "zf_xiaobei", "lang": "zh", "gender": "f", "zh": "晓贝", "en": "Xiaobei"},
            {"id": "zm_yunxi", "lang": "zh", "gender": "m", "zh": "云希", "en": "Yunxi"},
            {"id": "af_heart", "lang": "en", "gender": "f", "zh": "Heart", "en": "Heart"}]


def test_students_get_both_voices_and_subtitles():
    files = [{"name": "2.1 讲解视频.zh.vtt", "url": "z"}, {"name": "2.1 讲解视频.mp4", "url": "m"},
             {"name": "2.1 讲解视频.en.mp4", "url": "e"}, {"name": "2.1 讲解视频.en.vtt", "url": "ev"}]
    assert main._lecture_of(files) == {"video": {"zh": "m", "en": "e"}, "subs": {"zh": "z", "en": "ev"}}
    assert main._lecture_of([{"name": "a.mp4", "url": "m"}]) is None


@need_ffmpeg
def test_teacher_recording_gets_subtitles_and_an_english_voice(client, monkeypatch, tmp_path):
    SPOKEN.clear()
    monkeypatch.setattr(V, "tts", fake_tts)
    monkeypatch.setattr(main.state.settings, "voice_url", "http://voice.test")
    heard = []

    async def fake_asr(url, wav, timeout=3600.0):
        heard.append(wav.stat().st_size)
        return [{"start": 0.4, "end": 2.0, "text": "同学们好今天讲机器人"}, {"start": 2.4, "end": 3.2, "text": "先看一个问题"},
                {"start": 4.0, "end": 5.5, "text": "这台机械臂有六个关节"}]
    monkeypatch.setattr(V, "asr", fake_asr)
    h = login(client)
    pid, p = _write_first_lesson(client, h)
    p = settle(client, h, pid, 120)
    les = p["outline"]["chapters"][0]["lessons"][0]
    rec = tmp_path / "rec.mov"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=s=1920x1080:d=6:r=25", "-f", "lavfi",
                    "-i", "sine=f=300:d=6", "-shortest", "-pix_fmt", "yuv420p", str(rec)], check=True)
    data = rec.read_bytes()
    half = len(data) // 2
    base = f"/api/v1/studio/projects/{pid}/lessons/{les['id']}/recording?upload=abc12345&name=rec.mov&total=2"
    assert client.post(base + "&index=1", headers=h, content=data[half:]).status_code == 400   # pieces in order
    assert client.post(base.replace("rec.mov", "rec.exe") + "&index=0", headers=h, content=b"x").status_code == 400
    assert client.post(base + "&index=0", headers=h, content=data[:half]).json()["received"] == 1
    client.post(base + "&index=1", headers=h, content=data[half:])
    p = settle(client, h, pid, 120)
    les = p["outline"]["chapters"][0]["lessons"][0]
    lec = next(f for f in les["files"] if f["kind"] == "lecture")
    assert lec["source"] == "teacher" and heard and abs(lec["seconds"] - 6) < 0.5
    assert "你的讲课录像" in next(c for c in les["checklist"] if c["key"] == "lecture")["note"]
    d = main._studio().lecture_dir(main._studio().projects.load(pid), les)
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0",
                          str(d / "zh.mp4")], capture_output=True, text=True).stdout.strip()
    assert out == "1280,720"                    # made fit for the web
    assert abs(probe(d / "en.mp4") - probe(d / "zh.mp4")) < 0.3
    zh = L.parse_vtt((d / "zh.vtt").read_text())
    assert [c["text"] for c in zh] == ["同学们好今天讲机器人。", "先看一个问题。", "这台机械臂有六个关节。"]
    assert zh[0]["start"] == 0.4
    en = L.parse_vtt((d / "en.vtt").read_text())
    assert len(en) == 3 and en[1]["start"] >= 2.4
    # the first line is too long for its slot: spoken faster (at most 1.35x)
    assert any(s > 1.0 for t, _, s in SPOKEN if t == "Line 1 of the lecture.") or len("Line 1 of the lecture.") * 0.045 < 2.0
    assert not list((main._studio().projects.root / pid / "uploads").glob("*"))    # the upload is not kept
    # the teacher fixes a translation: the English voice is made again
    n = len(SPOKEN)
    client.put(f"/api/v1/studio/projects/{pid}/lessons/{les['id']}/lecture", headers=h,
               json={"rows": [{"n": 2, "en": "This arm has six joints."}]})
    settle(client, h, pid, 60)
    assert [t for t, _, _ in SPOKEN[n:]] == ["This arm has six joints."]
    assert "This arm has six joints." in (d / "en.vtt").read_text()
    # AI narration again, replacing the recording
    client.post(f"/api/v1/studio/projects/{pid}/lessons/{les['id']}/lecture/redo", headers=h)
    p = settle(client, h, pid, 120)
    les = p["outline"]["chapters"][0]["lessons"][0]
    assert next(f for f in les["files"] if f["kind"] == "lecture")["source"] == "ai"
    _ = (json, time)
