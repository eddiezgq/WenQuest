"""第 102 轮：三维视频旁白选声音、调语速——视频页、网页版缝纫机设计软件、FreeCAD（钥匙）都能选；新视频一律从平台默认开始"""
import asyncio

import httpx
import pytest

from app import main
from app import sewing_voice as SVO
from app import video3d as v3
from app import video3d_api
from app import video3d_voice as VV
from app.production import voice as VS
from tests.test_materials import login
from tests.test_sewing_voice import fake_tts
from tests.test_video3d import SCENE, blender, settle, v3c  # noqa: F401

VOICES = [{"id": "zf_xiaobei", "lang": "zh", "gender": "f", "zh": "晓贝（女）", "en": "Xiaobei (female)"},
          {"id": "zm_yunjian", "lang": "zh", "gender": "m", "zh": "云健（男）", "en": "Yunjian (male)"},
          {"id": "af_heart", "lang": "en", "gender": "f", "zh": "Heart（美式女声）", "en": "Heart (US female)"},
          {"id": "am_michael", "lang": "en", "gender": "m", "zh": "Michael（美式男声）", "en": "Michael (US male)"}]


def recording_tts(log):
    base = fake_tts()

    async def tts(url, text, voice, speed=1.0, timeout=300.0):
        log.append((voice, speed))
        return await base(url, text, voice, speed, timeout)
    return tts


async def fake_voices(url):
    return VOICES


@pytest.fixture(autouse=True)
def _voices(monkeypatch):
    monkeypatch.setattr(VS, "voices", fake_voices)
    video3d_api.VOICE_LIST.update(at=0.0, voices=[])


def test_pick_defaults_and_fallbacks():
    assert VV.pick({}, "zh") == ("zf_xiaobei", 1.1, "")
    assert VV.pick({}, "en") == ("af_heart", 1.1, "")
    assert VV.pick({"name": "zm_yunjian", "speed": 1.25}, "zh") == ("zm_yunjian", 1.25, "")
    v, s, note = VV.pick({"name": "am_michael", "speed": 1.3}, "zh")      # 语言不对、语速不在三档：退回默认并说明
    assert (v, s) == ("zf_xiaobei", 1.1) and "中文声音" in note and "三档" in note
    assert VV.describe({"name": "zm_yunjian", "label": "云健（男）"}, "zm_yunjian", 1.25) == "声音 云健（男），快语速"
    assert VV.describe({}, "zf_xiaobei", 1.1) == "声音 晓贝（女），标准语速"


def test_revoice_uses_the_videos_voice_and_speed_and_keeps_them(tmp_path, monkeypatch):
    log = []
    monkeypatch.setattr(VS, "tts", recording_tts(log))
    svc = v3.Service(tmp_path, None, v3.Blender("http://blender.test", httpx.MockTransport(blender)), v3.Mock(), voice_url="http://voice.test")

    async def go():
        V = await svc.create(1, "x", "", "缝纫机一针", voice=True)
        for _ in range(50):
            await asyncio.sleep(0.02)
            if not svc.store.load(V["id"])["busy"]:
                break
        first = svc.store.load(V["id"])
        n0 = len(log)
        assert {x for x in log} == {("zf_xiaobei", 1.1)}                 # 新视频：平台默认
        svc.set_voice(first, True, "zm_yunjian", 1.25, "云健（男）")
        for _ in range(50):
            await asyncio.sleep(0.02)
            if not svc.store.load(V["id"])["busy"]:
                break
        return first, svc.store.load(V["id"]), n0
    first, V, n0 = asyncio.run(go())
    assert {x for x in log[n0:]} == {("zm_yunjian", 1.25)}
    assert V["voice"]["plain"] is True                             # 换声音前退回了没拉长的那一版，重新拉长
    assert V["voice"]["name"] == "zm_yunjian" and V["voice"]["speed"] == 1.25
    assert "声音 云健（男），快语速" in V["chat"][-1]["text"]
    # 关掉再打开（不带选择）：还是这段视频选的声音
    V = svc.set_voice(V, False)
    assert V["voice"]["name"] == "zm_yunjian"

    async def again():
        W = svc.set_voice(svc.store.load(V["id"]), True)
        await asyncio.sleep(0.3)
        return W
    W = asyncio.run(again())
    assert W["voice"]["name"] == "zm_yunjian" and W["voice"]["speed"] == 1.25


def test_endpoints_voices_and_switch_with_choice(v3c, monkeypatch):  # noqa: F811
    log = []
    monkeypatch.setattr(VS, "tts", recording_tts(log))
    st = main.state.settings
    old = st.voice_url
    st.voice_url = "http://voice.test"
    main.state.video3d = None
    try:
        t = login(v3c, "t")
        vs = v3c.get("/api/v1/video3d/voices", headers=t).json()
        assert vs["available"] and len(vs["voices"]) == 4 and vs["default"] == {"zh": "zf_xiaobei", "en": "af_heart", "speed": 1.1}
        assert [x["v"] for x in vs["speeds"]] == [1.0, 1.1, 1.25] and vs["voices"][1]["sample"].endswith("/voice-sample/zm_yunjian")
        smp = v3c.get("/api/v1/video3d/voice-sample/zm_yunjian")
        assert smp.status_code == 200 and smp.headers["content-type"] == "audio/wav"
        assert v3c.get("/api/v1/video3d/voice-sample/xx_none").status_code == 404
        r = v3c.post("/api/v1/video3d", json={"sample": "缝纫机一针"}, headers=t).json()
        settle(v3c, t, r["id"], lambda d: not d["busy"], n=200)
        assert v3c.post(f"/api/v1/video3d/{r['id']}/voice", json={"on": True, "voice": "zz_no"}, headers=t).status_code == 400
        assert v3c.post(f"/api/v1/video3d/{r['id']}/voice", json={"on": True, "speed": 1.3}, headers=t).status_code == 400
        bad = v3c.post(f"/api/v1/video3d/{r['id']}/voice", json={"on": True, "voice": "am_michael"}, headers=t)
        assert bad.status_code == 400 and "中文声音" in bad.text                  # 中文视频选英文声音
        n0 = len(log)
        assert v3c.post(f"/api/v1/video3d/{r['id']}/voice", json={"on": True, "voice": "zm_yunjian", "speed": 1.0}, headers=t).status_code == 200
        d = settle(v3c, t, r["id"], lambda d: not d["busy"], n=200)
        assert d["voice"]["name"] == "zm_yunjian" and d["voice"]["speed"] == 1.0 and {x for x in log[n0:]} == {("zm_yunjian", 1.0)}
        assert "云健（男），慢语速" in d["chat"][-1]["text"]
    finally:
        st.voice_url = old
        main.state.video3d = None


def test_sewing_video_carries_the_choice(v3c, monkeypatch):  # noqa: F811
    log = []
    monkeypatch.setattr(VS, "tts", recording_tts(log))
    st = main.state.settings
    old = st.voice_url
    st.voice_url = "http://voice.test"
    main.state.video3d = None
    try:
        t = login(v3c, "t")
        assert v3c.post("/api/v1/admin/sewing/licenses", json={"username": "t", "org": "乙缝纫机厂"}, headers=t).status_code == 200
        vs = v3c.get("/api/v1/sewing/video/voices", headers=t).json()
        assert vs["available"] and {v["id"] for v in vs["voices"]} >= {"am_michael"} and vs["voices"][0]["sample"].endswith("/voice-sample/zf_xiaobei")
        body = {"machine": "lockstitch", "params": {"n": 6000}, "lang": "en", "voice_name": "zm_yunjian"}
        assert v3c.post("/api/v1/sewing/video", json=body, headers=t).status_code == 400        # 英文字幕配中文声音
        body["voice_name"], body["speed"] = "am_michael", 1.25
        r = v3c.post("/api/v1/sewing/video", json=body, headers=t).json()
        d = settle(v3c, t, r["id"], lambda d: not d["busy"] and d["stills"].get("state") in ("done", "failed"), n=400)
        assert d["voice"]["name"] == "am_michael" and {x for x in log} == {("am_michael", 1.25)}
        # 不选：和以前一样，平台默认
        log.clear()
        r2 = v3c.post("/api/v1/sewing/video", json={"machine": "lockstitch", "params": {}, "lang": "zh"}, headers=t).json()
        settle(v3c, t, r2["id"], lambda d: not d["busy"] and d["stills"].get("state") in ("done", "failed"), n=400)
        assert {x for x in log} == {("zf_xiaobei", 1.1)}
    finally:
        st.voice_url = old
        main.state.video3d = None


def test_voice_service_down_keeps_the_cached_list(monkeypatch):
    class S:
        voice_url = "http://voice.test"

    async def down(url):
        raise VS.VoiceError("down", "service")
    asyncio.run(video3d_api.voice_list(S()))                     # 取到列表
    video3d_api.VOICE_LIST["at"] = 0.0                           # 过期
    monkeypatch.setattr(VS, "voices", down)
    assert len(asyncio.run(video3d_api.voice_list(S()))) == 4    # 连不上：用旧的
    video3d_api.VOICE_LIST.update(at=0.0, voices=[])             # 没有旧列表：认得出语言的先记下
    assert asyncio.run(video3d_api.check_voice(S(), "zm_yunjian", None))[0] == "zm_yunjian"
    with pytest.raises(Exception):
        asyncio.run(video3d_api.check_voice(S(), "xx_none", None))
