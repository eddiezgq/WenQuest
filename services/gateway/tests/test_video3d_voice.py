"""第 99 轮：所有三维视频都能配旁白——有解说词念解说词（数只能是画面上有的），没有就念标题字幕；
新建默认配，工作页开关打开配、关掉退回没拉长的那一版；重配不往后挪；缝纫机讲解片照旧念字幕。"""
import asyncio

import httpx
import yaml

from app import main
from app import sewing_video as SVd
from app import sewing_voice as SVO
from app import video3d as v3
from app import video3d_voice as VV
from app.production import voice as VS
from tests.test_materials import login
from tests.test_sewing_voice import fake_tts
from tests.test_video3d import SCENE, blender, settle, v3c  # noqa: F401

SCRIPTED = SCENE.replace("labels:\n", """voice:
  - {t: 0, zh: 先看整台平缝机，主轴转一圈缝出一针。, en: First the whole machine; one turn of the main shaft makes one stitch.}
  - {t: 6, zh: 镜头推到针板下面：旋梭尖勾住线环，带着它绕过梭芯。, en: Now under the needle plate the hook point catches the loop.}
labels:
""")


def _spec(text):
    return yaml.safe_load(text)


def test_script_numbers_must_be_on_screen():
    s = _spec(SCRIPTED)
    assert VV.errors(s, 12) == []
    s["voice"][0]["zh"] = "主轴转速 4500 转每分，转 3 圈。"           # 4500 画面上没有；3 是小整数
    errs = VV.errors(s, 12)
    assert len(errs) == 1 and "4500" in errs[0] and "3" not in errs[0].split("4500")[1][:3]
    s["labels"].append({"t": [0, 12], "zh": "4500 r/min", "en": "4500 r/min"})
    assert VV.errors(s, 12) == []
    s["style"] = "cinematic"                                       # 电影风格：解说词就是屏上大字幕，不查数
    assert VV.errors(s, 12) == []
    del s["style"]
    s["voice"][1]["zh"] = "长" * 91
    assert any("太长" in e for e in VV.errors(s, 12))
    s["voice"] = [{"t": 13, "zh": "超出"}]
    assert any("超出视频长度" in e for e in VV.errors(s, 12))
    # check() 里一起查；只写了解说词（还没配）的片子仍按 120 秒
    _, errs = v3.check(SCRIPTED)
    assert errs == []
    long = _spec(SCRIPTED)
    long["duration"] = 130
    _, errs = v3.check(yaml.safe_dump(long, allow_unicode=True))
    assert errs and "duration" in errs[0]


def test_lines_prefer_script_then_labels_and_sewing_stays_on_labels():
    items, src = VV.lines(_spec(SCRIPTED), "zh")
    assert src == "script" and [x["t0"] for x in items] == [0, 6] and items[0]["t1"] == 6 and items[1]["t1"] == 12
    assert items[0]["text"].startswith("先看整台平缝机")
    sp = _spec(SCRIPTED)
    sp["voice"][0]["zh"] = "再来一次，快 2 倍，2.5 秒。"
    sp["labels"].append({"t": [0, 1], "zh": "2.5 s", "en": "2.5 s"})
    assert VV.lines(sp, "zh")[0][0]["text"] == "再来一次，快两倍，二点五 秒。"
    en, _ = VV.lines(_spec(SCRIPTED), "en")
    assert en[1]["text"].startswith("Now under the needle plate")
    items, src = VV.lines(_spec(SCENE), "zh")                       # 没有解说词：念标题
    assert src == "labels" and items[0]["text"].startswith("平缝机一针")
    items, src = VV.lines(_spec(SCRIPTED), "zh", locked=True)     # 缝纫机讲解片：一律念字幕
    assert src == "labels"


def _svc(tmp_path, monkeypatch, voice_url="http://voice.test"):
    monkeypatch.setattr(VS, "tts", fake_tts())
    return v3.Service(tmp_path, None, v3.Blender("http://blender.test", httpx.MockTransport(blender)), v3.Mock(), voice_url=voice_url)


def test_revoice_script_switch_off_restores_and_revoice_does_not_drift(tmp_path, monkeypatch):
    svc = _svc(tmp_path, monkeypatch)
    monkeypatch.setattr(VS, "tts", fake_tts(2.0))                 # 念得慢：两段都要拉长

    async def go():
        V = await svc.create(1, "x", "", "")
        assert svc.set_scene(V, SCRIPTED) == []
        V = svc.store.load(V["id"])
        V["voice"] = {"on": True}
        svc.store.save(V)
        await svc.revoice(V["id"], stills=False)
        return svc.store.load(V["id"])
    V = asyncio.run(go())
    spec = _spec(svc.store.scene(V["id"]))
    assert V["voice"]["state"] == "done" and V["voice"]["src"] == "script" and svc.audio_for(V)
    assert "AI 写的解说词" in V["chat"][-1]["text"]
    assert spec["duration"] > 12 and [x["seg"] for x in spec["voice"]][0] == 0
    assert all(x["zh"] and x["en"] and x["say"] and x["dur"] for x in spec["voice"])
    _, errs = v3.check(svc.store.scene(V["id"]))
    assert errs == []
    first = svc.store.scene(V["id"])

    # 关掉：退回配旁白前那一版（没拉长），不再有声音
    V = svc.set_voice(svc.store.load(V["id"]), False)
    assert V["voice"] == {"on": False} and svc.audio_for(V) is None
    assert _spec(svc.store.scene(V["id"]))["duration"] == 12 and "退回" in V["chat"][-1]["text"]

    # 在配好的场景上改过（人直接改场景，原样保存）再配：时刻不往后挪，片长不变；这时关掉不退回
    async def on_again():
        svc.set_voice(svc.store.load(V["id"]), True)
        await svc.revoice(V["id"], stills=False)
    asyncio.run(on_again())
    assert svc.store.scene(V["id"]) == first                       # 再打开：配出来和第一次一样
    V = svc.store.load(V["id"])
    assert svc.set_scene(V, first) == []
    asyncio.run(svc.revoice(V["id"], stills=False))
    again = _spec(svc.store.scene(V["id"]))
    assert abs(again["duration"] - spec["duration"]) < 0.05
    assert [x["t"] for x in again["voice"]] == [x["t"] for x in spec["voice"]]
    V = svc.set_voice(svc.store.load(V["id"]), False)
    assert abs(_spec(svc.store.scene(V["id"]))["duration"] - spec["duration"]) < 0.05 and "节奏保持" in V["chat"][-1]["text"]


def test_create_from_sample_voices_labels_and_needs_voice_service(tmp_path, monkeypatch):
    svc = _svc(tmp_path, monkeypatch)

    async def go():
        V = await svc.create(1, "x", "", "缝纫机一针", voice=True)
        assert V["busy"] == "voice"
        for _ in range(50):
            await asyncio.sleep(0.02)
            V = svc.store.load(V["id"])
            if not V["busy"]:
                break
        return V
    V = asyncio.run(go())
    assert V["voice"]["state"] == "done" and V["voice"]["src"] == "labels" and svc.audio_for(V)
    spec = _spec(svc.store.scene(V["id"]))
    assert all(x["src"] == "labels" for x in spec["voice"])
    # 没装语音服务：新建不打勾也不报错，开关打开说清楚
    svc2 = _svc(tmp_path / "b", monkeypatch, voice_url="")
    V2 = asyncio.run(svc2.create(1, "x", "", "缝纫机一针", voice=True))
    assert not V2.get("voice") and not V2["busy"]
    try:
        svc2.set_voice(V2, True)
        raise AssertionError
    except RuntimeError as e:
        assert "语音服务" in str(e)


def test_sewing_explainer_unchanged(tmp_path, monkeypatch):
    """缝纫机讲解片照第 90 轮念字幕，数一字不差"""
    svc = _svc(tmp_path, monkeypatch)
    text, meta = SVd.scene("lockstitch", {"n": 6000}, "zh")

    async def go():
        V = await svc.create(1, "x", "", "")
        V["lock"] = {"model": "d", "machine": "lockstitch", "params": meta["params"], "numbers": meta["numbers"]}
        svc.store.save(V)
        assert svc.set_scene(V, text) == []
        V = svc.store.load(V["id"])
        V["voice"] = {"on": True}
        svc.store.save(V)
        await svc.revoice(V["id"], stills=False)
        return svc.store.load(V["id"])
    V = asyncio.run(go())
    spec = _spec(svc.store.scene(V["id"]))
    assert V["voice"]["src"] == "labels" and all(x["src"] == "labels" for x in spec["voice"])
    want = [x["text"] for x in SVO.lines(_spec(text), "zh")]
    assert [x["say"] for x in spec["voice"]] == want
    assert "画面上的标题和字幕" in V["chat"][-1]["text"]


def test_endpoints_create_default_voice_and_switch(v3c, monkeypatch):  # noqa: F811
    monkeypatch.setattr(VS, "tts", fake_tts())
    st = main.state.settings
    old = st.voice_url
    st.voice_url = "http://voice.test"
    main.state.video3d = None
    try:
        t = login(v3c, "t")
        idx = v3c.get("/api/v1/video3d", headers=t).json()
        assert idx["voice_on"] is True
        r = v3c.post("/api/v1/video3d", json={"sample": "缝纫机一针"}, headers=t).json()      # 默认配
        d = settle(v3c, t, r["id"], lambda d: not d["busy"], n=200)
        assert d["voice"]["on"] and d["voice"]["state"] == "done" and d["voice_on"]
        tl = d["timeline"]["voice"]
        assert tl and tl[0]["labels"] and tl[0]["say"].startswith("平缝机一针")
        off = v3c.post(f"/api/v1/video3d/{r['id']}/voice", json={"on": False}, headers=t).json()
        assert off["voice"] == {"on": False} and off["timeline"]["duration"] == 12
        on = v3c.post(f"/api/v1/video3d/{r['id']}/voice", json={"on": True}, headers=t).json()
        assert on["busy"] == "voice"
        assert v3c.post(f"/api/v1/video3d/{r['id']}/voice", json={"on": False}, headers=t).status_code == 409   # 正在配：等配完
        d = settle(v3c, t, r["id"], lambda d: not d["busy"], n=200)
        assert d["voice"]["state"] == "done"
        r2 = v3c.post("/api/v1/video3d", json={"sample": "缝纫机一针", "voice": False}, headers=t).json()
        assert not r2["voice"] and not r2["busy"]
    finally:
        st.voice_url = old
        main.state.video3d = None


def test_review_fixes_number_values_length_estimate_and_voiced_limit(tmp_path, monkeypatch):
    s = _spec(SCRIPTED)
    s["labels"].append({"t": [0, 12], "zh": "转速 3,000 r/min · 针距 1.5 mm", "en": "3,000 r/min · 1.5 mm"})
    s["voice"][0]["zh"] = "主轴 3000 转每分，针距 1.50 毫米，快 2.0 倍。"      # 按数值比
    assert VV.errors(s, 12) == []
    s["voice"][1]["t"] = 0.2                                        # 两句挤在一起
    assert any("隔 0.5 秒" in e for e in VV.errors(s, 12))
    # 解说词太长：估计拉长后超过 150 秒，先让 AI 写短
    long = _spec(SCENE)
    long["duration"] = 40
    long["voice"] = [{"t": i * 4, "zh": "这" * 88, "en": "x"} for i in range(10)]
    assert any("解说词太长" in e for e in VV.errors(long, 40))
    # 配过旁白、拉长到 120 秒以上的片子：AI 改片时把 dur 删了也照 150 秒查
    big = _spec(SCENE)
    big["duration"] = 130
    big["camera"][-1]["t"] = 130
    big["motion"][0]["angle"] = [[0, 0], [130, 360]]
    big["effects"][0]["t"] = [2, 130]
    big["labels"][0]["t"] = [0, 130]
    txt = yaml.safe_dump(big, allow_unicode=True)
    assert v3.check(txt)[1] and v3.check(txt, voiced=True)[1] == []
