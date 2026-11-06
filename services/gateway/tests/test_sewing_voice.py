"""第 90 轮：讲解片旁白——念画面上的字（口语读法，数不变）；旁白长的段放慢拉长，后面顺延，关键画面仍停在原来那一刻；
配好的 audio.m4a 跟着出片传到机器上；语音服务不在时照无声出。"""
import asyncio
import io
import math
import re
import wave

import httpx
import yaml

from app import main
from app import sewing_video as SVd
from app import sewing_voice as SVO
from app import video3d as v3
from app.production import voice as VS
from tests.test_materials import login
import httpx

from tests.test_video3d import blender, settle, v3c  # noqa: F401


def _wav(secs: float, sr: int = 24000) -> bytes:
    b = io.BytesIO()
    with wave.open(b, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        n = int(secs * sr)
        w.writeframes(bytes(2 * n))
    return b.getvalue()


def fake_tts(rate=6.0):
    """假语音：一秒念 rate 个字"""
    async def tts(url, text, voice, speed=1.0, timeout=300.0):
        secs = max(0.8, len(text) / rate)
        return _wav(secs), secs
    return tts


def test_spoken_reads_numbers_and_units_without_changing_them():
    s = SVO.spoken("① 刺布机构（曲柄滑块）")
    assert s.startswith("第一段，")
    assert SVO.spoken("下止点惯性力 941 N · 连杆比 0.282 · 曲柄 15.5 mm") == "下止点惯性力 九百四十一牛，连杆比 零点二八二，曲柄 十五点五毫米"
    assert SVO.spoken("6000 r/min · 判据 ≤ 800 N") == "六千 转每分，判据 不超过 八百牛"
    assert SVO.spoken("弯针定时 −6° · 判据 ≥ 1.5°") == "弯针定时 负六度，判据 不小于 一点五度"
    assert SVO.spoken("这台绷缝机：406 线迹") == "这台绷缝机：四零六 线迹"
    assert SVO.spoken("⚠ 不合格：针杆下止点惯性力") == "不合格：针杆下止点惯性力"
    assert SVO._int_zh(10329) == "一万零三百二十九" and SVO._int_zh(2000) == "两千" and SVO._int_zh(15) == "十五"
    e = SVO.spoken("Looper timing −6°, window −3.5°–+4.0° · 6500 r/min", "en")
    assert e == "Looper timing minus 6 degrees, window minus 3.5 degrees to plus 4.0 degrees, 6500 R P M"
    for txt in ("① Needle", "⚠ Lambda fails"):
        assert "⚠" not in SVO.spoken(txt, "en") and "①" not in SVO.spoken(txt, "en")


def _all_scenes():
    for m, p in (("lockstitch", {"n": 6000}), ("overlock", {}), ("cover", {"dphi": -6}), ("pattern", {"n": 2000}),
                 ("embroid", {"s": 12, "n": 1200}), ("flatknit", {"rack": 4, "dwell": 0.01})):
        for lang in ("zh", "en"):
            text, meta = SVd.scene(m, p, lang)
            yield m, lang, yaml.safe_load(text), meta


def _angle(spec, t):
    ks = spec["motion"][0]["angle"]
    for (t0, a0), (t1, a1) in zip(ks, ks[1:]):
        if t <= t1:
            return a0 + (a1 - a0) * (t - t0) / max(1e-9, t1 - t0)
    return ks[-1][1]


def test_fit_stretches_segments_and_keeps_the_stills_on_the_same_frame():
    for m, lang, spec, meta in _all_scenes():
        items = SVO.lines(spec, lang)
        assert items and all(x["text"] for x in items)
        assert len({x["text"] for x in items}) == len(items)                  # 同一句不念两遍
        for x in items:
            x["dur"] = max(1.0, len(x["text"]) / (5.0 if lang == "zh" else 14.0))
        out = SVO.fit(spec, items)
        _, errs = v3.check(yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=200))
        assert errs == [], (m, lang, errs)
        assert v3.lock_errors(out, {"model": "d", "machine": m, "params": meta["params"], "numbers": meta["numbers"]}) == []
        assert out["duration"] >= spec["duration"]
        f, _ = SVO.warp_map([(x["t0"], x["t1"], SVO.LEAD + x["dur"] + SVO.TAIL) for x in items])
        for a, b in zip(spec["stills"], out["stills"]):                       # 关键画面：同一个转角（同一针 / 趟）
            assert math.isclose(_angle(spec, a), _angle(out, b), abs_tol=0.2)
            assert math.isclose(f(a), b, abs_tol=0.02)
        for x, v in zip(items, out["voice"]):                                 # 每句在自己那一段里读完
            assert f(x["t0"]) <= v["t"] and v["t"] + v["dur"] <= f(x["t1"]) + 1e-6
        ks = [k[0] for k in out["motion"][0]["angle"]]
        assert ks == sorted(ks)
        # 再配一遍（改片后）：已经够长的段不再拉
        again = SVO.fit(out, [dict(x, t0=f(x["t0"]), t1=f(x["t1"])) for x in items])
        assert math.isclose(again["duration"], out["duration"], abs_tol=0.05)


def test_mix_places_each_sentence():
    a = SVO.mix([(0.5, _wav(1.0)), (3.0, _wav(0.5))], 5.0)
    assert len(a) > 200 and a[4:8] == b"ftyp"


def test_revoice_service_audio_and_render_upload(tmp_path, monkeypatch):
    monkeypatch.setattr(VS, "tts", fake_tts())
    svc = v3.Service(tmp_path, None, v3.Blender("http://blender.test", httpx.MockTransport(blender)), v3.Mock(), voice_url="http://voice.test")
    text, meta = SVd.scene("pattern", {"n": 2000}, "zh")

    async def go():
        V = await svc.create(1, "x", "", "")
        V["lock"] = {"model": "d", "machine": "pattern", "params": meta["params"], "numbers": meta["numbers"]}
        svc.store.save(V)
        assert svc.set_scene(V, text) == []
        V = svc.store.load(V["id"])
        V["voice"] = {"on": True}
        svc.store.save(V)
        await svc.revoice(V["id"], stills=False)
        return svc.store.load(V["id"])
    V = asyncio.run(go())
    spec = yaml.safe_load(svc.store.scene(V["id"]))
    assert V["voice"]["state"] == "done" and V["voice"]["version"] == V["version"] and not V["busy"]
    assert spec["duration"] > meta["duration"] and spec["voice"] and svc.audio_for(V)
    assert "旁白配好了" in V["chat"][-1]["text"]
    # 出小样：旁白跟着这一次出片
    rid = svc.request_render(V, "draft", 1)
    assert (svc.store.vdir(V["id"]) / f"run_{rid}.m4a").exists()
    for _ in range(4):
        asyncio.run(svc.tick())
    files = svc.provider.box.get("files") or {}
    assert "wq3d/job/audio.m4a" in files and isinstance(files["wq3d/job/audio.m4a"], bytes)          # 传到租的机器上
    # 场景再改（版本变了）：旧旁白不再用
    V = svc.store.load(V["id"])
    svc.store.set_scene(V, svc.store.scene(V["id"]))
    svc.store.save(V)
    assert svc.audio_for(svc.store.load(V["id"])) is None


def test_revoice_without_voice_service_falls_back(tmp_path):
    svc = v3.Service(tmp_path, None, v3.Blender(""), None, voice_url="")
    text, meta = SVd.scene("lockstitch", {}, "zh")

    async def go():
        V = await svc.create(1, "x", "", "")
        assert svc.set_scene(V, text) == []
        V = svc.store.load(V["id"])
        V["voice"] = {"on": True}
        svc.store.save(V)
        await svc.revoice(V["id"], stills=False)
        return svc.store.load(V["id"])
    V = asyncio.run(go())
    assert V["voice"]["state"] == "failed" and "语音服务" in V["voice"]["error"] and not V["busy"]
    assert svc.store.scene(V["id"]) == text and svc.audio_for(V) is None
    assert "旁白没配成" in V["chat"][-1]["text"]


def test_endpoint_voice_switch(v3c, monkeypatch):  # noqa: F811
    monkeypatch.setattr(VS, "tts", fake_tts())
    st = main.state.settings
    old = st.voice_url
    st.voice_url = "http://voice.test"
    main.state.video3d = None
    try:
        t = login(v3c, "t")
        assert v3c.post("/api/v1/admin/sewing/licenses", json={"username": "t", "org": "乙缝纫机厂"}, headers=t).status_code == 200
        r = v3c.post("/api/v1/sewing/video", json={"machine": "lockstitch", "params": {"n": 6000}, "lang": "zh"}, headers=t).json()
        assert r["voice"] is True
        d = settle(v3c, t, r["id"], lambda d: not d["busy"] and d["stills"].get("state") in ("done", "failed"), n=400)
        assert d["timeline"]["duration"] > r["duration"]                      # 拉长了
        assert any("旁白配好了" in c["text"] for c in d["chat"])
        r2 = v3c.post("/api/v1/sewing/video", json={"machine": "lockstitch", "params": {}, "lang": "zh", "voice": False}, headers=t).json()
        d2 = settle(v3c, t, r2["id"], lambda d: not d["busy"] and d["stills"].get("state") in ("done", "failed"), n=400)
        assert math.isclose(d2["timeline"]["duration"], r2["duration"]) and not any("旁白" in c["text"] for c in d2["chat"][1:])
        # 直接改场景：旁白重配
        sc = d["scene"].replace("第一", "第一")
        sc = re.sub(r"(zh: )① 刺布机构", r"\1① 刺布机构（改）", sc, count=1)
        assert v3c.put(f"/api/v1/video3d/{r['id']}/scene", json={"scene": sc}, headers=t).status_code == 200
        d3 = settle(v3c, t, r["id"], lambda d: not d["busy"], n=400)
        assert d3["chat"][-1]["text"].startswith("旁白配好了")
    finally:
        st.voice_url = old
        main.state.video3d = None
